# 01_core/interpreter.py
# 실제 실행 엔진

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable

from .lexer import lex_line
from .parser import parse_line
from .parser_utils import Command, CommandKind
from .cmd import CommandExecMixin



@dataclass
class Interpreter(CommandExecMixin):
    variables_table: Dict[int, int] = field(default_factory=dict)
    array_table: Dict[int, List] = field(default_factory=dict)
    stack: List[int] = field(default_factory=list)
    last_result: Optional[int] = None
    last_was_operation: bool = False
    output_func: Callable[[str], None] = print


    def write(self, msg="", end=None) -> None:
        self.output_func(msg, end=end)


    def reset(self) -> None:
        self.variables_table.clear()
        self.stack.clear()
        self.last_result = None
        self.last_was_operation = False


    # ───────────────── 파일 실행용: pc 기반 루프 ─────────────────
    def run_program(self, lines: List[str]) -> None:
        clean_lines = [ln.rstrip("\n") for ln in lines]
        pc = 0
        n = len(clean_lines)

        while 0 <= pc < n:
            line = clean_lines[pc]
            tokens = lex_line(line)
            if not tokens:
                pc += 1
                continue
            cmds = parse_line(tokens)

            jumped = False
            for cmd in cmds:
                if cmd.kind == CommandKind.JUMP:
                    pc = self.execute_with_pc(cmd, pc, advance_pc=False)
                    jumped = True
                    break
                else:
                    self.execute_with_pc(cmd, pc, advance_pc=False)

            if not jumped:
                pc += 1

    
    def execute_with_pc(self, cmd: Command, pc: int, *, advance_pc: bool = True) -> int:
        """파일 실행용: pc 기반 실행.

        advance_pc=True 는 “한 줄=명령 1개” 가정일 때 pc를 다음 줄로 넘긴다.
        여러 명령을 한 줄에서 순차 실행할 때는 advance_pc=False 로 호출해 pc 변경을 막는다.
        """
        kind = cmd.kind

        if kind == CommandKind.NOOP:
            return pc + 1 if advance_pc else pc
        
        if kind == CommandKind.VAR_DECL:
            self._exec_var_decl(cmd)
            return pc + 1 if advance_pc else pc

        elif kind == CommandKind.VALUE_PUSH:
            self._exec_value_push(cmd)
            return pc + 1 if advance_pc else pc

        elif kind == CommandKind.VAR_PUSH_OR_ACCESS:
            self._exec_var_push_or_access(cmd)
            return pc + 1 if advance_pc else pc

        elif kind == CommandKind.OPERATION:
            self._exec_operation(cmd)
            return pc + 1 if advance_pc else pc

        elif kind == CommandKind.INPUT:
            self._exec_input(cmd)
            return pc + 1 if advance_pc else pc

        elif kind == CommandKind.OUTPUT:
            self._exec_output(cmd)
            return pc + 1 if advance_pc else pc

        elif kind == CommandKind.DISPLAY_STACK:
            self._exec_display_stack()
            return pc + 1 if advance_pc else pc

        elif kind == CommandKind.DISPLAY_VARIABLES_TABLE:
            self._exec_display_variable_table()
            return pc + 1 if advance_pc else pc

        elif kind == CommandKind.JUMP:
            return self._exec_jump(cmd, pc)
        
        elif kind == CommandKind.ARRAY_DECL:
            self._exec_array_decl(cmd)
            return pc + 1 if advance_pc else pc
        
        elif kind == CommandKind.ARRAY_WRITE:
            self._exec_array_write(cmd)
            return pc + 1 if advance_pc else pc
        
        elif kind == CommandKind.ARRAY_READ:
            self._exec_array_read(cmd)
            return pc + 1 if advance_pc else pc

        else:
            raise ValueError(f"알 수 없는 CommandKind: {kind}")