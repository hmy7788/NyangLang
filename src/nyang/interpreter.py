# 01_core/interpreter.py
# 실제 실행 엔진

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .lexer import lex_line
from .parser import parse_line, Command, CommandKind



@dataclass
class Interpreter:
    variables_table: Dict[int, int] = field(default_factory=dict)
    stack: List[int] = field(default_factory=list)
    last_result: Optional[int] = None
    last_was_operation: bool = False

    def reset(self) -> None:
        self.variables_table.clear()
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
        print(cmd)

        kind = cmd.kind

        if kind == CommandKind.NOOP:
            return
        
        # 변수 선언 & 초기화
        if kind == CommandKind.VAR_DECL:
            self._exec_var_decl(cmd)

        # 값 push
        elif kind == CommandKind.VALUE_PUSH: 
            self._exec_value_push(cmd)

        # 변수 push or 대입
        elif kind == CommandKind.VAR_PUSH_OR_ACCESS:
            self._exec_var_push_or_access(cmd)

        # 연산
        elif kind == CommandKind.OPERATION:
            self._exec_operation(cmd)

        # 입력
        elif kind == CommandKind.INPUT:
            self._exec_input(cmd)

        # 출력1
        elif kind == CommandKind.OUTPUT_NUM_TO_LITERAL:
            self._exec_output_num_to_literal(cmd)

        # 출력2
        elif kind == CommandKind.OUTPUT_NUM_TO_ASCII:
            self._exec_output_num_to_ascii(cmd)

        # 출력3
        elif kind == CommandKind.OUTPUT_VAR_TO_NUM:
            self._exec_output_var_to_num(cmd)

        # 출력4
        elif kind == CommandKind.OUTPUT_VAR_TO_ASCII:
            self._exec_output_var_to_ascii(cmd)

        # 스택 display 내장함수
        elif kind == CommandKind.DISPLAY_STACK:
            self._exec_display_stack()

        # 변수 테이블 display 내장함수
        elif kind == CommandKind.DISPLAY_VARIABLES_TABLE:
            self._exec_display_variable_table()

        # 무조건 점프
        elif kind == CommandKind.UNCONDITION_JUMP:
            self._exec_uncondtion_jump(cmd)

        # 조건 점프
        elif kind == CommandKind.CONDITION_JUMP:
            self._exec_condtion_jump(cmd)
        
        # 해석 실패
        else:
            raise ValueError(f"알 수 없는 CommandKind: {kind}")


    # --- 개별 명령 처리 메소드 ---
    # 변수 선언 & 초기화: <냥 N개><. , M개>
    def _exec_var_decl(self, cmd: Command) -> None:
        var_id = cmd.nyang_id   # N
        value = cmd.int_value   # . , 계산값
        self.variables_table[var_id] = value


    # 정수형 push: <. , M개>~
    def _exec_value_push(self, cmd: Command) -> None:
        value = cmd.int_value       # . , 계산값
        self.stack.append(value)    # 스택에 push
        self.last_result = value


    # 변수형 push / 대입: <냥 N개>~
    def _exec_var_push_or_access(self, cmd: Command) -> None:
        var_id = cmd.nyang_id   # N

        # 연산 직후 -> 대입 처리
        if self.last_was_operation:
            if len(self.stack) == 0:
                raise RuntimeError("스택이 비어있는데 대입을 시도했습니다.")
            value = self.last_result
            self.variables_table[var_id] = value
            self.last_result = value
            self.last_was_operation = False
        # 일반 모드 -> 변수 값을 push
        else:
            int_value =  self.variables_table[var_id]
            self.stack.append(int_value)
            self.last_result = int_value


    # 연산자: <냐 N개>~
    def _exec_operation(self, cmd: Command) -> None:
        if len(self.stack) < 2:
            raise RuntimeError("연산을 수행하기 위한 스택 값이 부족합니다.")

        b = self.stack.pop()
        a = self.stack.pop()
        op_n = cmd.op_arity # 연산 종류

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


    # 입력: <냥 N개>?
    def _exec_input(self, cmd: Command) -> None:
        var_id = cmd.nyang_id
        try:
            raw = input(f'변수{var_id} 입력 > ')
            value = int(raw.strip())
        except ValueError:
            raise ValueError("정수만 입력할 수 있습니다")
        self.variables_table[var_id] = value


    # 출력: <정수형>! -> 정수값 10진수 출력
    def _exec_output_num_to_literal(self, cmd: Command) -> None:
        value = cmd.int_value
        print(value)


    # 출력: <정수형>!! -> 정수값 ASCII 출력
    def _exec_output_num_to_ascii(self, cmd: Command) -> None:
        value = cmd.int_value
        try:
            print(chr(value))
        except ValueError:
            raise ValueError(f"ASCII 범위를 벗어난 값입니다. {value}")


    # 출력: <냥 N개>! -> 변수값 10진수 출력
    def _exec_output_var_to_num(self, cmd: Command) -> None:
        var_id = cmd.nyang_id
        try:
            value = self.variables_table[var_id]
            print(value)
        except KeyError:
            raise KeyError(f"변수{var_id}가 정의되지 않았습니다.")


    # 출력: <냥 N개>!! -> ascii 값 출력
    def _exec_output_var_to_ascii(self, cmd: Command) -> None:
        var_id = cmd.nyang_id
        try:
            value = self.variables_table[var_id]
            ch = chr(value)
        except KeyError:
            raise KeyError(f"변수{var_id}가 정의되지 않았습니다.")
        except ValueError:
            raise ValueError(f"ASCII 범위를 벗어난 값입니다. {value}")
        print(ch)

    
    # 출력: ! -> 현재 스택 출력
    def _exec_display_stack(self) -> None:
        if self.stack:
            print("===============")
            for i in range(len(self.stack)-1, -1, -1):
                if i == len(self.stack)-1:
                    print(f'=      {self.stack[i]}      = <- Top')
                else:
                    print(f'=      {self.stack[i]}      =')
            print("==[현재 스택]==")
        else:
            print("====================")
            print("스택이 비어있습니다.")
            print("====================")


    # 출력: !! -> 현재 변수 테이블 출력
    def _exec_display_variable_table(self) -> None:
        vt = self.variables_table
        if vt:
            print("--[변수 테이블]--")
            for k, v in vt.items():
                print(f'- 변수{k} = {v}    -')
            print("-----------------")
        else:
            print("===========================")
            print("변수 테이블이 비어있습니다.")
            print("===========================")


    def _exec_uncondtion_jump(self, cmd: Command):
        # 숫자형 무조건 점프
        if cmd.nyang_id is None:
            jump_line = cmd.int_value

        # 변수형 무조건 점프
        elif cmd.int_value is None:
            jump_line = self.variables_table[cmd.nyang_id]


    def _exec_condtion_jump(self, cmd: Command):
        # 숫자형 조건 점프
        if cmd.nyang_id is None:
            pass

        # 변수형 조건 점프
        elif cmd.int_value is None:
            pass