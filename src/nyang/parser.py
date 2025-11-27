# 토큰을 명령 객체로 바꾸는 부분
# 01_core/parser.py

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, List

from .lexer import Token, TokenType



class CommandKind(Enum):
    NOOP = auto()               
    VAR_DECL = auto()                       # 변수 선언 + 초기화 (냥..)
    VALUE_PUSH = auto()                     # 상수 push (..)
    VAR_PUSH_OR_ACCESS = auto()             # 변수 push or 대입 (런타임 결정)
    OPERATION = auto()                      # 연산 (냐냐, 냐냐냐...)
    INPUT = auto()                          # 입력 (냥?)

    OUTPUT_NUM_TO_LITERAL = auto()          # 상수 10진수 출력 (...!)
    OUTPUT_NUM_TO_ASCII = auto()            # 상수 ASCII 출력 (...!!)
    OUTPUT_VAR_TO_NUM = auto()              # 변수 10진수 출력 (냥!)
    OUTPUT_VAR_TO_ASCII = auto()            # 변수 ASCII 출력 (냥!!)
    
    DISPLAY_STACK = auto()                  # 스택 상태 출력 (!)
    DISPLAY_VARIABLES_TABLE = auto()        # 변수 테이블 출력 (!!)



@dataclass
class Command:
    kind: CommandKind
    nyang_id: Optional[int] = None
    nya_id: Optional[int] = None
    int_value: Optional[int] = None
    op_arity: Optional[int] = None
    bang_count: Optional[int] = None



def parse_line(tokens: List[Token]) -> Command:
    """
    """
    if not tokens:
        return Command(kind=CommandKind.NOOP)

    first = tokens[0]
    last = tokens[-1]

    # 1) 변수 선언 & 초기화: <냥 N개><. , M개>
    if first.type == TokenType.NYANG:
        if last.type == TokenType.INT:
            return Command(
                kind=CommandKind.VAR_DECL,
                nyang_id=first.value,
                int_value=last.value
            )
        elif len(tokens) == 1:
            return Command(
                kind=CommandKind.VAR_DECL,
                nyang_id=first.value,
                int_value=0
            )
    
    # 2) 정수형 push: <. ,>~
    if first.type == TokenType.INT:
        if last.type == TokenType.TILDE:
            return Command(
                kind=CommandKind.VALUE_PUSH,
                int_value=first.value
            )
        
    # 3) 변수형 push: <냥 N개>~
    if first.type == TokenType.NYANG:
        if last.type == TokenType.TILDE:
            return Command(
                kind=CommandKind.VAR_PUSH_OR_ACCESS,
                nyang_id=first.value
            )
        
    # 4) 연산자: <냐 N개>~
    if first.type == TokenType.NYA:
        if last.type == TokenType.TILDE:
            return Command(
                kind=CommandKind.OPERATION,
                op_arity= first.value
            )
        
    # 5) 입력: <냥 N개>?
    if first.type == TokenType.NYANG:
        if last.type == TokenType.QUESTION:
            return Command(
                kind=CommandKind.INPUT,
                nyang_id=first.value
            )
        
    # 6) 출력: <정수형>! or <정수형>!! or <냥 N개>! or <냥 N개>!! or ! or !!
    # 6-1) 출력: <정수형>! or <정수형>!!
    if first.type == TokenType.INT:
        # <정수형>!
        if last.type == TokenType.BANG and last.value == 1:
            return Command(
                kind=CommandKind.OUTPUT_NUM_TO_LITERAL,
                int_value=first.value
            )
        # <정수형>!!
        elif last.type == TokenType.BANG and last.value == 2:
            return Command(
                kind=CommandKind.OUTPUT_NUM_TO_ASCII,
                int_value=first.value
            )
        
    
    # 6-2) 출력: <냥 N개>! or <냥 N개>!!
    if first.type == TokenType.NYANG:
        # <냥 N개>!
        if last.type == TokenType.BANG and last.value == 1:
            return Command(
                    kind=CommandKind.OUTPUT_VAR_TO_NUM,
                    nyang_id=first.value
            )
        # <냥 N개>!!
        elif last.type == TokenType.BANG and last.value == 2:
            return Command(
                kind=CommandKind.OUTPUT_VAR_TO_ASCII,
                nyang_id=first.value
            )
            
    # 6-3) 출력: ! or !!
    if first.type == TokenType.BANG:
        # !
        if first.value == 1:
            return Command(
                kind=CommandKind.DISPLAY_STACK
            )
        # !!
        elif first.value == 2:
            return Command(
                kind=CommandKind.DISPLAY_VARIABLES_TABLE
            )
    
    raise SyntaxError(f"파싱할 수 없는 문장 패턴입니다. : {tokens}")