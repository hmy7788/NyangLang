# 

# import ============================================
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable

from nyang._00_types import Command, CommandKind
from nyang._01_lexer import lex_line
from nyang._02_parser import parse_line
# import ============================================

class CommandExecMixin:
    """
    - Interpreter에서 사용하는 개별 명령 실행 로직을 모은 믹스인 클래스
    - Interpreter가 이 클래스를 상속받아 self._exec_*를 그대로 사용
    """

    # 1. <NYNAG><INT><YAONG>: VAR_DECL: 변수 선언
    def _exec_var_decl(self: "Interpreter", cmd: Command) -> None:
        var_id = cmd.nyang_id
        value = cmd.int_value
        self.variables_table[var_id] = value


    # 2. <NYNAG><TILDE_1><YAONG>: VAR_PUSH: 스택에 변수값 PUSH
    def _exec_var_push(self: "Interpreter", cmd: Command) -> None:
        var_id = cmd.nyang_id
        if var_id not in self.variables_table:
            raise KeyError(f"변수{var_id}가 정의되지 않았습니다.")
        int_value = self.variables_table[var_id]
        self.stack.append(int_value)
        self.stack_top = int_value


    # 3. <NYANG><TILDE_2>야옹: VAR_ASSIGN: 변수 = 스택의 TOP 값 
    def _exec_var_assign(self: "Interpreter", cmd: Command) -> None:
        var_id = cmd.nyang_id
        if not self.stack:
            raise RuntimeError("스택이 비어있습니다.")
        self.variables_table[var_id] = self.stack.pop()

    
    # 4. <INT><TILDE_1><YAONG>: VALUE_PUSH: 스택에 정수값 PUSH
    def _exec_value_push(self: "Interpreter", cmd: Command) -> None:
        value = cmd.int_value
        self.stack.append(value)
        self.stack_top = value


    # 5. <NYA><QUESTION_1,2><YAONG>: OPERATION: 연산 수행
    def _exec_operation(self: "Interpreter", cmd: Command) -> None:
        if len(self.stack) < 2:
            raise RuntimeError("연산을 수행하기 위한 스택 값이 부족합니다.")
        b = self.stack.pop()
        a = self.stack.pop()
        op = cmd.op_arity

        if op == 2: result = a + b
        elif op == 3: result = a - b
        elif op == 4: result = a * b
        elif op == 5:
            if b == 0: raise ZeroDivisionError("0으로 나눌 수 없습니다.")
            result = a // b
        else: raise RuntimeError("지원하지 않는 연산입니다.")
        
        self.stack.append(result)
        self.stack_top = result


    # 6. <NYANG><QUESTION_2><YAONG>: INPUT: 입력
    def _exec_input(self: "Interpreter", cmd: Command) -> None:
        var_id = cmd.nyang_id
        try:
            raw = self.input_func(f"변수{var_id} 입력 > ")
            value = int(str(raw).rstrip())
        except ValueError:
            raise ValueError("정수만 입력할 수 있습니다.")
        self.variables_table[var_id] = value

    
    # 7. <NYANG, INT><BANG_1,2><QUESTION_1,2,3><YAONG>: OUTPUT: 출력
    def _exec_output(self: "Interpreter", cmd: Command) -> None:
        # 출력 종류
        if cmd.output_kind == "int":
            value = cmd.int_value
        elif cmd.output_kind == "nyang":
            try:
                var_id = cmd.nyang_id
                value = self.variables_table[var_id]
            except KeyError:
                raise KeyError(f"변수{var_id}가 정의되지 않았습니다.")
        else:
            raise RuntimeError("알 수 없는 output_kind")
        
        # 출력 형식
        if cmd.output_form == "decimal":
            out = value
        elif cmd.output_form == "ascii":
            try:
                out = chr(value)
            except ValueError:
                raise ValueError("ASCII 범위를 벗어난 값입니다.")
        else:
            raise RuntimeError("알 수 없는 output_form")
        
        # 출력 모드
        if cmd.output_mode == "newline": end = "\n"
        elif cmd.output_mode == "inline": end = ""
        elif cmd.output_mode == "space": end = " "
        else: raise RuntimeError("알 수 없는 output_mode")
        
        # 
        self.write(out, end=end)


    # 8. <NYANG, INT><QUESTION_1><NYANG, INT>: JUMP: (조건)?(점프라인)
    def _exec_jump(self: "Interpreter", cmd: Command, pc: int):
        jump_kind = cmd.jump_kind

        # 점프문1: <숫자형>?<숫자형>
        if jump_kind == 'int?int':
            condition = cmd.condition
            line = cmd.jump_line

        # 점프문2: <숫자형>?<변수형>
        elif jump_kind == 'int?nyang':
            condition = cmd.condition
            try:
                line = self.variables_table[cmd.jump_line]
            except KeyError:
                raise KeyError(f"변수{cmd.jump_line}은 정의되지 않았습니다.")

        # 점프문3: <변수형>?<숫자형>
        elif jump_kind == 'nyang?int':
            try:
                condition = self.variables_table[cmd.condition]
            except KeyError:
                raise KeyError(f"변수{cmd.condition}은 정의되지 않았습니다.")
            line = cmd.jump_line
        
        # 점프문4: <변수형>?<변수형>
        elif jump_kind == 'nyang?nyang':
            try:
                condition = self.variables_table[cmd.condition]
                line = self.variables_table[cmd.jump_line]
            except KeyError:
                raise KeyError(f"변수{cmd.condition} 또는 변수{cmd.jump_line}은 정의되지 않았습니다.")
        
        if condition != 0:
            if line <= 0:
                raise RuntimeError(f"잘못된 점프 라인 {line}")
            return line-1
        else:
            return pc+1
        

    # 9. <NYA><TILDE_1>: DISPLAY_STACK: 스택 디버깅
    def _exec_display_stack(self: "Interpreter") -> None:
        self.write()
        if self.stack:
            self.write("===============")
            for i in range(len(self.stack)-1, -1, -1):
                if i == len(self.stack)-1:
                    self.write(f'=      {self.stack[i]}      = <- Top')
                else:
                    self.write(f'=      {self.stack[i]}      =')
            self.write("==[현재 스택]==")
        else:
            self.write("====================")
            self.write("스택이 비어있습니다.")
            self.write("====================")



    # 10. <NYA><TILDE_2>: DISPLAY_VARIABLES_TABLE: 변수 테이블 디버깅
    def _exec_display_variable_table(self: "Interpreter") -> None:
        vt = self.variables_table
        self.write()
        if vt:
            self.write("--[변수 테이블]--")
            for k, v in vt.items():
                self.write(f'- 변수{k} = {v}    -')
            self.write("-----------------")
        else:
            self.write("===========================")
            self.write("변수 테이블이 비어있습니다.")
            self.write("===========================")
        

    # 11.
    def _exec_array_decl(self: "Interpreter", cmd: Command):
        array_id = cmd.array_id

        if cmd.array_decl_mode == 0:
            array_length = cmd.array_length
        elif cmd.array_decl_mode == 1:
            if cmd.array_length not in self.variables_table:
                raise KeyError(f"변수{cmd.array_length}가 정의되지 않았습니다.")
            array_length = self.variables_table[cmd.array_length]
        else:
            raise RuntimeError("알 수 없는 array_decl_mode")

        self.array_table[array_id] = [0] * array_length


    # 12.
    def _exec_array_write(self: "Interpreter", cmd: Command):
        array = self.array_table.get(cmd.array_id)
        if array is None:
            raise KeyError(f"배열{cmd.array_id}가 정의되지 않았습니다.")

        # 인덱스 결정
        if cmd.array_write_mode in (0, 1):  # int idx
            idx = cmd.array_idx
        else:                                # nyang idx (mode 2, 3)
            if cmd.array_idx not in self.variables_table:
                raise KeyError(f"변수{cmd.array_idx}가 정의되지 않았습니다.")
            idx = self.variables_table[cmd.array_idx]

        # 값 결정
        if cmd.array_write_mode in (0, 2):  # int val
            val = cmd.int_value
        else:                                # nyang val (mode 1, 3)
            if cmd.int_value not in self.variables_table:
                raise KeyError(f"변수{cmd.int_value}가 정의되지 않았습니다.")
            val = self.variables_table[cmd.int_value]

        if not (0 <= idx < len(array)):
            raise IndexError(f"배열{cmd.array_id}의 인덱스 {idx}가 범위를 벗어났습니다.")
        array[idx] = val


    # 13.
    def _exec_array_read(self: "Interpreter", cmd: Command):
        array = self.array_table.get(cmd.array_id)
        if array is None:
            raise KeyError(f"배열{cmd.array_id}가 정의되지 않았습니다.")

        # 인덱스 결정
        if cmd.array_read_mode in (0, 1):  # int idx
            idx = cmd.array_idx
        else:                               # nyang idx (mode 2, 3)
            if cmd.array_idx not in self.variables_table:
                raise KeyError(f"변수{cmd.array_idx}가 정의되지 않았습니다.")
            idx = self.variables_table[cmd.array_idx]

        if not (0 <= idx < len(array)):
            raise IndexError(f"배열{cmd.array_id}의 인덱스 {idx}가 범위를 벗어났습니다.")

        val = array[idx]

        # 목적지 결정
        if cmd.array_read_mode in (0, 2):  # 스택에 push
            self.stack.append(val)
            self.stack_top = val
        else:                               # 변수에 대입 (mode 1, 3)
            self.variables_table[cmd.nyang_id] = val


    # 14.
    def _exec_array_input(self: "Interpreter", cmd: Command):
        array = self.array_table.get(cmd.array_id)
        if array is None:
            raise KeyError(f"배열{cmd.array_id}가 정의되지 않았습니다.")

        # 인덱스 결정
        if cmd.array_write_mode == 0:  # int idx
            idx = cmd.array_idx
        else:                           # nyang idx (mode 1)
            if cmd.array_idx not in self.variables_table:
                raise KeyError(f"변수{cmd.array_idx}가 정의되지 않았습니다.")
            idx = self.variables_table[cmd.array_idx]

        if not (0 <= idx < len(array)):
            raise IndexError(f"배열{cmd.array_id}의 인덱스 {idx}가 범위를 벗어났습니다.")

        try:
            raw = self.input_func(f"배열{cmd.array_id} {idx}번 인덱스 입력 > ")
            array[idx] = int(str(raw).rstrip())
        except ValueError:
            raise ValueError("정수만 입력할 수 있습니다.")


@dataclass
class Interpreter(CommandExecMixin):
    variables_table: Dict[int, int] = field(default_factory=dict)
    array_table: Dict[int, List] = field(default_factory=dict)
    stack: List[int] = field(default_factory=list)
    stack_top: Optional[int] = None
    last_was_operation: bool = False
    output_func: Callable[[str], None] = print
    input_func: Callable[[int], None] = input
    current_line: int = 0
    debug_hook: Optional[Callable[[int], None]] = None  # debug: called before each line with pc
    cmd_hook: Optional[Callable[[int, int], None]] = None  # debug: called before each command with (pc, cmd_idx)


    def write(self, msg="", end=None) -> None:
        self.output_func(msg, end=end)

    
    def inputs(self, msg=""):
        self.input_func()


    def reset(self) -> None:
        self.variables_table.clear()
        self.stack.clear()
        self.stack_top = None


    # ───────────────── 파일 실행용: pc 기반 루프 ─────────────────
    def run_program(self, lines: List[str]) -> None:
        clean_lines = [ln.rstrip("\n") for ln in lines]
        pc = 0
        n = len(clean_lines)

        while 0 <= pc < n:
            if self.debug_hook:
                self.debug_hook(pc)
            self.current_line = pc + 1
            line = clean_lines[pc]
            tokens = lex_line(line)
            if not tokens:
                pc += 1
                continue
            cmds = parse_line(tokens)

            jumped = False
            for cmd_idx, cmd in enumerate(cmds):
                if self.cmd_hook:
                    self.cmd_hook(pc, cmd_idx)
                if cmd.kind == CommandKind.JUMP:
                    pc = self.execute_with_pc(cmd, pc)
                    jumped = True
                    break
                else:
                    self.execute_with_pc(cmd, pc)

            if not jumped:
                pc += 1

    
    def execute_with_pc(self, cmd: Command, pc: int) -> int:
        """
        - 파일 실행용: pc 기반 실행.
        """
        kind = cmd.kind

        if kind == CommandKind.NOOP:
            return pc + 1
        
        if kind == CommandKind.VAR_DECL:
            self._exec_var_decl(cmd)
            return pc + 1

        elif kind == CommandKind.VALUE_PUSH:
            self._exec_value_push(cmd)
            return pc + 1

        elif kind == CommandKind.VAR_PUSH:
            self._exec_var_push(cmd)
            return pc + 1
        
        elif kind == CommandKind.VAR_ASSIGN:
            self._exec_var_assign(cmd)
            return pc + 1

        elif kind == CommandKind.OPERATION:
            self._exec_operation(cmd)
            return pc + 1

        elif kind == CommandKind.INPUT:
            self._exec_input(cmd)
            return pc + 1

        elif kind == CommandKind.OUTPUT:
            self._exec_output(cmd)
            return pc + 1

        elif kind == CommandKind.DISPLAY_STACK:
            self._exec_display_stack()
            return pc + 1

        elif kind == CommandKind.DISPLAY_VARIABLES_TABLE:
            self._exec_display_variable_table()
            return pc + 1

        elif kind == CommandKind.JUMP:
            return self._exec_jump(cmd, pc)
        
        # 일단 여기까지

        elif kind == CommandKind.ARRAY_DECL:
            self._exec_array_decl(cmd)
            return pc + 1
        
        elif kind == CommandKind.ARRAY_WRITE:
            self._exec_array_write(cmd)
            return pc + 1
        
        elif kind == CommandKind.ARRAY_READ:
            self._exec_array_read(cmd)
            return pc + 1

        elif kind == CommandKind.ARRAY_INPUT:
            self._exec_array_input(cmd)
            return pc + 1

        else:
            raise ValueError(f"알 수 없는 CommandKind: {kind}")