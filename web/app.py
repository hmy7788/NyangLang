from typing import List

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from nyang.interpreter import Interpreter

app = FastAPI()

# static / templates 설정 (app.py 기준으로 상대 경로)
app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")


# 기본 화면: index.html 렌더링
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# 코드 실행 API
@app.post("/run")
async def run(code: str = Form(...)):
    logs: List[str] = []
    output_buffer = ""

    # Interpreter에서 self.output_func(msg, end=end) 이런 식으로 호출하니까
    # end 인자도 같이 받도록 정의
    def collect(msg: str, end: str = "") -> None:
        nonlocal output_buffer
        # end는 여기선 무시하고 msg만 로그에 쌓기
        # logs.append(str(msg))
        output_buffer += str(msg) + end

    # 인터프리터 생성 + 출력 콜백 연결
    interp = Interpreter(output_func=collect)

    # 코드 여러 줄 → 리스트로 만들어서 실행
    lines = code.splitlines()
    interp.run_program(lines)

    # 프론트에서 data.stdout 기준으로 출력하니까 키 이름을 stdout으로 반환
    # return {"stdout": logs}
    return {"stdout": output_buffer}