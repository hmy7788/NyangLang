from typing import List

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from nyang.interpreter import Interpreter

app = FastAPI()

# static / templates 설정 (app.py 기준으로 상대 경로)
app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")

class CodeRequest(BaseModel):
    code: str


# 기본 화면: index.html 렌더링
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# 코드 실행 API
@app.post("/run")
async def run(req: CodeRequest):
    status = "success"
    result = ""
    error_msg = None

    def collect(msg: str, end: str = "") -> None:
        nonlocal result
        result += str(msg) + end

    interp = Interpreter(output_func=collect)

    # ★ req.code 로 꺼내서 씁니다.
    lines = req.code.splitlines()

    try:
        interp.run_program(lines)

        # 성공
        return {
            "status": "success",
            "result": result,
            "error_msg": None
        }

    except Exception as e:
        # 에러
        print(f'예외 발생: {e}')
        return {
            "status": "error",
            "result": result,
            "error_msg": str(e)
        }


    