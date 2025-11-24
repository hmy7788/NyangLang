from core.interpreter import Interpreter

interpreter = Interpreter()
interpreter.reset()

with open('./examples/simple.nyang', encoding='utf-8') as f:
    for line in f:
        interpreter.exec_line(line)