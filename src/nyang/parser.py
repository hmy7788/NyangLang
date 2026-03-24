# 토큰을 명령 객체로 바꾸는 부분
# 01_core/parser.py

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, List
from .lexer import Token, TokenType, lex_line
from .parser_utils import TokenStream, parse_nyang_command, parse_nya_command, parse_int_command
from dataclasses import asdict

class CommandKind(Enum):
    NOOP = auto()               
    VAR_DECL = auto()                       # 변수 선언 + 초기화 (냥..)
    VALUE_PUSH = auto()                     # 상수 push (..)
    VAR_PUSH_OR_ACCESS = auto()             # 변수 push or 대입 (런타임 결정)
    OPERATION = auto()                      # 연산 (냐냐, 냐냐냐...)
    INPUT = auto()                          # 입력 (냥?)
    OUTPUT = auto()                         # 상수/변수값 -> 10진수/ASCII 출력
    DISPLAY_STACK = auto()                  # 스택 상태 출력 (!)
    DISPLAY_VARIABLES_TABLE = auto()        # 변수 테이블 출력 (!!)
    JUMP = auto()                           # 점프문: <숫자형/변수형>?<숫자형/변수형>
    ARRAY_DECL = auto()                     # 배열 선언
    ARRAY_WRITE = auto()                    # 배열 쓰기     
    ARRAY_READ = auto()   


@dataclass
class Command:
    kind: CommandKind
    nyang_id: Optional[int] = None
    nya_id: Optional[int] = None
    int_value: Optional[int] = None
    op_arity: Optional[int] = None
    bang_count: Optional[int] = None
    output_kind: Optional[str] = None
    output_form: Optional[str] = None
    output_mode: Optional[str] = None
    jump_kind: Optional[int] = None
    condition: Optional[int] = None
    line: Optional[int] = None
    array_decl_mode: Optional[int] = None
    array_write_mode: Optional[int] = None
    array_read_mode: Optional[int] = None
    array_id: Optional[int] = None
    array_length: Optional[int] = None
    array_idx: Optional[int] = None







def parse_command(token_stream: TokenStream) -> Command:
    """
    """
    token = token_stream.peek()
    if not token:
        return None
    elif token.type == TokenType.NYANG:
        return parse_nyang_command(token_stream)
    elif token.type == TokenType.NYA:
        return parse_nya_command(token_stream)
    elif token.type == TokenType.INT:
        return parse_int_command(token_stream)
    

def parse_line(tokens: List[Token]) -> List[Command]:
    """
    input: 토큰 리스트
    output: 명령어 리스트
    """
    token_stream = TokenStream(tokens)
    commands: List[Command] = []

    while token_stream.peek() is not None:
        # print(token_stream.peek())
        command = parse_command(token_stream)
        commands.append(command)
    return commands



def print_parse_line(commands: List[Command]) -> None:
    for cmd in commands:
        data = asdict(cmd)
        filtered = {k: v for k, v in data.items() if v is not None}
        # kind는 Enum이라 이름만 보이게
        filtered["kind"] = cmd.kind.name
        print(filtered)

if __name__ == "__main__":
    print_parse_line(parse_line(lex_line("..!?..,,!!??")))