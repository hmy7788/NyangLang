from typing import Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from nyang._03_interpreter import Interpreter

app = FastAPI()

# static / templates 설정 (app.py 기준으로 상대 경로)
app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")

class CodeRequest(BaseModel):
    code: str
    inputs: list[str] = []


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    # 요청 JSON 검증 실패도 동일한 응답 스키마로 통일
    messages = "; ".join(error["msg"] for error in exc.errors())
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "result": "",
            "error_msg": messages,
        },
    )


# 기본 화면: index.html 렌더링
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# 코드 실행 API
@app.post("/run")
async def run(req: CodeRequest):
    result = ""

    def collect(msg: str = "", end: Optional[str] = None) -> None:
        nonlocal result
        safe_end = "" if end is None else end
        result += str(msg) + safe_end

    try:
        input_queue = list(req.inputs)
        input_idx = 0

        def web_input(prompt: str = "") -> str:
            nonlocal input_idx
            if input_idx >= len(input_queue):
                raise RuntimeError("입력값이 부족합니다. 입력창에 값을 추가해주세요.")
            val = input_queue[input_idx]
            input_idx += 1
            return val

        interp = Interpreter(output_func=collect, input_func=web_input)
        lines = req.code.splitlines()
        interp.run_program(lines)

        # 성공
        return {
            "status": "success",
            "result": result,
            "error_msg": None
        }

    except Exception as e:
        print(f'예외 발생: {e}')
        return {
            "status": "error",
            "result": result,
            "error_msg": str(e),
            "error_line": interp.current_line
        }


# 웹 구동시 -> uvicorn web.app:app --reload 써서 들어가기

# 브랜치 생성
