import asyncio
import concurrent.futures
import os
import threading
import time
from typing import Optional

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from nyang._03_interpreter import Interpreter

app = FastAPI()

app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")


class CodeRequest(BaseModel):
    code: str
    inputs: list[str] = []


class _ComputeTimer:
    """입력 대기 시간을 제외한 순수 계산 시간만 측정"""
    def __init__(self):
        self._lock = threading.Lock()
        self._acc = 0.0
        self._t0 = time.monotonic()
        self._paused = False

    def pause(self):
        with self._lock:
            if not self._paused:
                self._acc += time.monotonic() - self._t0
                self._paused = True

    def resume(self):
        with self._lock:
            if self._paused:
                self._t0 = time.monotonic()
                self._paused = False

    def elapsed(self) -> float:
        with self._lock:
            extra = 0.0 if self._paused else (time.monotonic() - self._t0)
            return self._acc + extra


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    messages = "; ".join(error["msg"] for error in exc.errors())
    return JSONResponse(
        status_code=422,
        content={"status": "error", "result": "", "error_msg": messages},
    )


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# examples/ 폴더의 .nyang 예제를 그대로 읽어 제공 (하드코딩 복사본 없이 단일 출처)
EXAMPLES_DIR = "examples"
EXAMPLES_SKIP = {"bench.nyang"}  # 벤치마크(출력 없음·장시간)는 플레이그라운드에서 제외


@app.get("/api/examples")
async def list_examples():
    items = []
    if os.path.isdir(EXAMPLES_DIR):
        for fn in sorted(os.listdir(EXAMPLES_DIR)):
            if fn.endswith(".nyang") and fn not in EXAMPLES_SKIP:
                try:
                    with open(os.path.join(EXAMPLES_DIR, fn), encoding="utf-8") as f:
                        items.append({"name": fn, "code": f.read()})
                except OSError:
                    pass
    return {"examples": items}


@app.websocket("/ws/run")
async def ws_run(websocket: WebSocket):
    await websocket.accept()

    try:
        data = await asyncio.wait_for(websocket.receive_json(), timeout=10.0)
    except Exception:
        return

    code = data.get("code", "")
    lines = code.splitlines()
    loop = asyncio.get_event_loop()

    input_event = threading.Event()
    input_holder: list = [None]
    timer = _ComputeTimer()

    async def send_safe(msg: dict):
        try:
            await websocket.send_json(msg)
        except Exception:
            pass

    def collect(msg="", end=None):
        text = str(msg) + ("" if end is None else end)
        asyncio.run_coroutine_threadsafe(
            send_safe({"type": "output", "data": text}), loop
        ).result(timeout=5)

    def web_input(prompt: str = "") -> str:
        timer.pause()
        asyncio.run_coroutine_threadsafe(
            send_safe({"type": "input_request", "prompt": prompt}), loop
        ).result(timeout=5)
        if not input_event.wait(timeout=60):
            raise RuntimeError("입력 대기 시간이 초과되었습니다. (60초)")
        input_event.clear()
        val = input_holder[0]
        timer.resume()
        return val

    # 협조적 정지: 매 라인 실행 전 호출되어, 중단/타임아웃/연결종료 시 워커 스레드를 빠져나오게 함
    stopped = [False]
    def stop_hook(pc: int):
        if stopped[0]:
            raise RuntimeError("실행이 중단되었습니다.")

    interp = Interpreter(output_func=collect, input_func=web_input, debug_hook=stop_hook)
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    exec_future = loop.run_in_executor(executor, lambda: interp.run_program(lines))

    timed_out = False
    try:
        while not exec_future.done():
            if timer.elapsed() > 5.0:
                timed_out = True
                stopped[0] = True       # 워커 스레드도 다음 라인에서 중단
                break
            try:
                msg = await asyncio.wait_for(websocket.receive_json(), timeout=0.1)
                if msg.get("type") == "input":
                    input_holder[0] = msg.get("value", "")
                    input_event.set()
            except asyncio.TimeoutError:
                pass
            except WebSocketDisconnect:
                stopped[0] = True
                input_event.set()       # 입력 대기 중이면 해제
                executor.shutdown(wait=False)
                return

        if timed_out:
            await send_safe({
                "type": "done", "status": "error",
                "error_msg": "⏱ 실행 시간이 5초를 초과했습니다. 무한 루프가 의심됩니다.",
                "error_line": interp.current_line
            })
            return

        exc = exec_future.exception()
        if exc:
            await send_safe({
                "type": "done", "status": "error",
                "error_msg": str(exc),
                "error_line": interp.current_line
            })
        else:
            await send_safe({
                "type": "done",
                "status": "success",
                "variables": {str(k): v for k, v in sorted(interp.variables_table.items())},
            })

    except WebSocketDisconnect:
        pass
    finally:
        stopped[0] = True               # 어떤 경로로 종료되든 워커 스레드 정지 신호
        input_event.set()
        executor.shutdown(wait=False)


@app.websocket("/ws/debug")
async def ws_debug(websocket: WebSocket):
    await websocket.accept()

    try:
        data = await asyncio.wait_for(websocket.receive_json(), timeout=10.0)
    except Exception:
        return

    code = data.get("code", "")
    lines = code.splitlines()
    loop = asyncio.get_event_loop()

    # 디버그 제어 상태 (list로 감싸서 클로저에서 수정 가능하게)
    breakpoints: set = set(data.get("breakpoints", []))
    step_mode = [True]      # True면 매 라인마다 멈춤
    cmd_step_mode = [False] # True면 매 명령어마다 멈춤
    stopped = [False]

    resume_event = threading.Event()  # debug_hook / cmd_hook이 여기서 대기
    input_event = threading.Event()
    input_holder: list = [None]

    async def send_safe(msg: dict):
        try:
            await websocket.send_json(msg)
        except Exception:
            pass

    def collect(msg="", end=None):
        text = str(msg) + ("" if end is None else end)
        asyncio.run_coroutine_threadsafe(
            send_safe({"type": "output", "data": text}), loop
        ).result(timeout=5)

    def web_input(prompt: str = "") -> str:
        asyncio.run_coroutine_threadsafe(
            send_safe({"type": "input_request", "prompt": prompt}), loop
        ).result(timeout=5)
        if not input_event.wait(timeout=120):
            raise RuntimeError("입력 대기 시간이 초과되었습니다. (120초)")
        input_event.clear()
        return input_holder[0]

    def debug_hook(pc: int):
        if stopped[0]:
            raise RuntimeError("디버깅이 중단되었습니다.")
        if cmd_step_mode[0]:
            return  # 명령어 단위 모드일 때는 cmd_hook이 처리
        line_no = pc + 1
        if line_no in breakpoints or step_mode[0]:
            asyncio.run_coroutine_threadsafe(
                send_safe({
                    "type": "debug_paused",
                    "line": line_no,
                    "stack": list(interp.stack),
                    "variables": {str(k): v for k, v in sorted(interp.variables_table.items())},
                    "arrays": {str(k): list(v) for k, v in sorted(interp.array_table.items())},
                }),
                loop
            ).result(timeout=5)
            resume_event.wait()
            resume_event.clear()
            if stopped[0]:
                raise RuntimeError("디버깅이 중단되었습니다.")

    def cmd_hook(pc: int, cmd_idx: int):
        if stopped[0]:
            raise RuntimeError("디버깅이 중단되었습니다.")
        if not cmd_step_mode[0]:
            return
        line_no = pc + 1
        asyncio.run_coroutine_threadsafe(
            send_safe({
                "type": "debug_cmd_paused",
                "line": line_no,
                "cmd_index": cmd_idx,
                "stack": list(interp.stack),
                "variables": {str(k): v for k, v in sorted(interp.variables_table.items())},
                "arrays": {str(k): list(v) for k, v in sorted(interp.array_table.items())},
            }),
            loop
        ).result(timeout=5)
        resume_event.wait()
        resume_event.clear()
        if stopped[0]:
            raise RuntimeError("디버깅이 중단되었습니다.")

    interp = Interpreter(output_func=collect, input_func=web_input, debug_hook=debug_hook, cmd_hook=cmd_hook)
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    exec_future = loop.run_in_executor(executor, lambda: interp.run_program(lines))

    try:
        while not exec_future.done():
            try:
                msg = await asyncio.wait_for(websocket.receive_json(), timeout=0.1)
                mtype = msg.get("type", "")

                if mtype == "debug_step":
                    cmd_step_mode[0] = False
                    step_mode[0] = True
                    resume_event.set()

                elif mtype == "debug_cmd_step":
                    cmd_step_mode[0] = True
                    step_mode[0] = False
                    resume_event.set()

                elif mtype == "debug_continue":
                    cmd_step_mode[0] = False
                    step_mode[0] = False
                    resume_event.set()

                elif mtype == "debug_stop":
                    stopped[0] = True
                    resume_event.set()
                    input_event.set()  # 입력 대기 중이면 해제

                elif mtype == "debug_set_breakpoints":
                    breakpoints.clear()
                    breakpoints.update(msg.get("lines", []))

                elif mtype == "input":
                    input_holder[0] = msg.get("value", "")
                    input_event.set()

            except asyncio.TimeoutError:
                pass
            except WebSocketDisconnect:
                stopped[0] = True
                resume_event.set()
                executor.shutdown(wait=False)
                return

        exc = exec_future.exception()
        if exc and not stopped[0]:
            await send_safe({
                "type": "debug_done", "status": "error",
                "error_msg": str(exc),
                "error_line": interp.current_line,
            })
        elif not stopped[0]:
            await send_safe({
                "type": "debug_done", "status": "success",
                "variables": {str(k): v for k, v in sorted(interp.variables_table.items())},
                "arrays": {str(k): list(v) for k, v in sorted(interp.array_table.items())},
            })

    except WebSocketDisconnect:
        pass
    finally:
        stopped[0] = True
        resume_event.set()
        executor.shutdown(wait=False)


# 웹 구동시 -> uvicorn web.app:app --reload 써서 들어가기
