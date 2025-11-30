from fastapi import FastAPI
from nyang.interpreter import Interpreter

app = FastAPI()

@app.post("/run")
def run(code: str):
    interp = Interpreter()
    logs = []
    for line in code.splitlines():
        interp.exec_line(line, output=lambda m: logs.append(str(m)))
    return {"stdout": logs}