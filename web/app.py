import asyncio
import concurrent.futures
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

    interp = Interpreter(output_func=collect, input_func=web_input)
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    exec_future = loop.run_in_executor(executor, lambda: interp.run_program(lines))

    timed_out = False
    try:
        while not exec_future.done():
            if timer.elapsed() > 5.0:
                timed_out = True
                break
            try:
                msg = await asyncio.wait_for(websocket.receive_json(), timeout=0.1)
                if msg.get("type") == "input":
                    input_holder[0] = msg.get("value", "")
                    input_event.set()
            except asyncio.TimeoutError:
                pass
            except WebSocketDisconnect:
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
            await send_safe({"type": "done", "status": "success"})

    except WebSocketDisconnect:
        pass
    finally:
        executor.shutdown(wait=False)


# 웹 구동시 -> uvicorn web.app:app --reload 써서 들어가기
