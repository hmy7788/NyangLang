# 01_core/interpreter.py
# 실제 실행 엔진

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .lexer import lex_line
from .parser import parse_line, Command, CommandKind



@dataclass
class Interpreter:
    variables: Dict[int, int] = field(default_factory=dict)
    stack: List[int] = field(default_factory=list)
    last_result: Optional[int] = None
    last_was_operation: bool = False

    def reset(self) -> None:
        self.variables.clear()
        self.stack.clear()
        self.last_result = None
        self.last_was_operation = False

    def exec_line(self, line: str) -> None:
        """
        NyangLang 코드 한줄을 실행
        """
        tokens = lex_line(line)
        cmd = parse_line(tokens)
        self.execute(cmd)

    def execute(self, cmd: Command) -> None:
        kind = cmd.kind

        if kind == CommandKind.NOOP:
            return
        
        if kind == CommandKind.VAR_DECL:
            self._exec_var_decl(cmd)
        elif kind == CommandKind.VALUE_PUSH:
            self._exec_value_push(cmd)
        elif kind == CommandKind.VAR_ACCESS:
            self._exec_var_access(cmd)
        elif kind == CommandKind.OPERATION:
            self._exec_operation(cmd)
        elif kind == CommandKind.INPUT:
            self._exec_input(cmd)
        elif kind == CommandKind.OUTPUT_NUM_LITERAL:
            self._exec_output_num_literal(cmd)
        elif kind == CommandKind.OUTPUT_NUM_VAR:
            self._exec_output_num_var(cmd)
        elif kind == CommandKind.OUTPUT_ASCII_VAR:
            self._exec_output_ascii_var(cmd)
        else:
            raise ValueError(f"알 수 없는 CommandKind: {kind}")


    # --- 개별 명령 처리 메소드 ---


    def _exec_var_decl(self, cmd: Command) -> None:
        var_id = cmd.nyang_id
        value = cmd.int_value or 0
        self.variables[var_id] = value
        self.last_result = value
        self.last_was_operation = False

    def _exec_value_push(self, cmd: Command) -> None:
        value = cmd.int_value or 0
        self.stack.append(value)
        self.last_result = value
        self.last_was_operation = False

    def _exec_var_access(self, cmd: Command) -> None:
        var_id = cmd.nyang_id
        current_value = self.variables.get(var_id, 0)

        # 연산 직후 -> 대입 처리
        if self.last_was_operation:
            if not self.stack:
                raise RuntimeError("스택이 비어있는데 대입을 시도했습니다.")
            value = self.stack.pop()
            self.variables[var_id] = value
            self.last_result = value
            self.last_was_operation = False
        # 일반 모드 -> 변수 값을 push
        else:
            self.stack.append(current_value)
            self.last_result = current_value

    def _exec_operation(self, cmd: Command) -> None:
        if len(self.stack) < 2:
            raise RuntimeError("연산을 수행하기 위한 스택 값이 부족합니다.")
        
        b = self.stack.pop()
        a = self.stack.pop()
        op_n = cmd.op_arity

        if op_n == 2:       # 덧셈 연산
            result = a + b
        elif op_n == 3:     # 뺄셈 연산
            result = a - b
        elif op_n == 4:     # 곱셈 연산
            result = a * b
        elif op_n == 5:     # 나눗셈 연산
            if b == 0:
                raise ZeroDivisionError("0으로 나눌 수 없습니다.")
            result = a // b
        else:
            raise RuntimeError("지원하지 않는 연산입니다.")
         
        self.stack.append(result)
        self.last_result = result
        self.last_was_operation = True

    def _exec_input(self, cmd: Command) -> None:
        var_id = cmd.nyang_id
        try:
            raw = input(f'변수{var_id} 입력 >')
            value = int(raw.strip())
        except ValueError:
            raise ValueError("정수만 입력할 수 있습니다")
        self.variables[var_id] = value
        self.last_result = value
        self.last_was_operation = False

    def _exec_output_num_literal(self, cmd: Command) -> None:
        value = cmd.int_value or 0
        print(value)
        self.last_result = value    # ?
        self.last_was_operation = False

    def _exec_output_num_var(self, cmd: Command) -> None:
        var_id = cmd.nyang_id
        value = self.variables.get(var_id, 0)
        print(value)
        self.last_result = value
        self.last_was_operation = False

    def _exec_output_ascii_var(self, cmd: Command) -> None:
        var_id = cmd.nyang_id
        value = self.variables.get(var_id, 0)
        try:
            ch = chr(value)
        except ValueError:
            raise ValueError(f"ASCII 범위를 벗어난 값입니다. {value}")
        print(ch)
        self.last_result = value
        self.last_was_operation = False