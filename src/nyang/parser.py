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

    UNCONDITION_JUMP = auto()                        # 무조건 점프 (냐..! or )
    CONDITION_JUMP = auto()



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
    
    if len(tokens) == 2:
        # 1) 변수 선언 & 초기화: <냥 N개><. , M개>
        if tokens[0].type == TokenType.NYANG:
            if tokens[1].type == TokenType.INT:
                return Command(
                    kind=CommandKind.VAR_DECL,
                    nyang_id=tokens[0].value,
                    int_value=tokens[1].value
                )
            elif len(tokens) == 1:
                return Command(
                    kind=CommandKind.VAR_DECL,
                    nyang_id=tokens[0].value,
                    int_value=0
                )
        
        # 2) 정수형 push: <. ,>~
        if tokens[0].type == TokenType.INT:
            if tokens[1].type == TokenType.TILDE:
                return Command(
                    kind=CommandKind.VALUE_PUSH,
                    int_value=tokens[0].value
                )
            
        # 3) 변수형 push: <냥 N개>~
        if tokens[0].type == TokenType.NYANG:
            if tokens[1].type == TokenType.TILDE:
                return Command(
                    kind=CommandKind.VAR_PUSH_OR_ACCESS,
                    nyang_id=tokens[0].value
                )
            
        # 4) 연산자: <냐 N개>~
        if tokens[0].type == TokenType.NYA:
            if tokens[1].type == TokenType.TILDE:
                return Command(
                    kind=CommandKind.OPERATION,
                    op_arity= tokens[0].value
                )
            
        # 5) 입력: <냥 N개>?
        if tokens[0].type == TokenType.NYANG:
            if tokens[1].type == TokenType.QUESTION:
                return Command(
                    kind=CommandKind.INPUT,
                    nyang_id=tokens[0].value
                )
            
        # 6) 출력: <정수형>! or <정수형>!! or <냥 N개>! or <냥 N개>!! or ! or !!
        # 6-1) 출력: <정수형>! or <정수형>!!
        if tokens[0].type == TokenType.INT:
            # <정수형>!
            if tokens[1].type == TokenType.BANG and tokens[1].value == 1:
                return Command(
                    kind=CommandKind.OUTPUT_NUM_TO_LITERAL,
                    int_value=tokens[0].value
                )
            # <정수형>!!
            elif tokens[1].type == TokenType.BANG and tokens[1].value == 2:
                return Command(
                    kind=CommandKind.OUTPUT_NUM_TO_ASCII,
                    int_value=tokens[0].value
                )
            
        
        # 6-2) 출력: <냥 N개>! or <냥 N개>!!
        if tokens[0].type == TokenType.NYANG:
            # <냥 N개>!
            if tokens[1].type == TokenType.BANG and tokens[1].value == 1:
                return Command(
                        kind=CommandKind.OUTPUT_VAR_TO_NUM,
                        nyang_id=tokens[0].value
                )
            # <냥 N개>!!
            elif tokens[1].type == TokenType.BANG and tokens[1].value == 2:
                return Command(
                    kind=CommandKind.OUTPUT_VAR_TO_ASCII,
                    nyang_id=tokens[0].value
                )

        # 6-3) 출력: 냐! or 냐!!
        if tokens[0].type == TokenType.NYA and tokens[1].type == TokenType.BANG:
            # 냐!
            if tokens[1].value == 1:
                return Command(
                    kind=CommandKind.DISPLAY_STACK
                )
            # 냐!!
            elif tokens[1].value == 2:
                return Command(
                    kind=CommandKind.DISPLAY_VARIABLES_TABLE
                )

    if len(tokens) == 3:
        if tokens[0].type == TokenType.NYA:
            if tokens[2].type == TokenType.BANG and tokens[2].value == 1:
                if tokens[1].type == TokenType.INT:
                    # 냐<숫자형>!
                    return Command(
                        kind=CommandKind.UNCONDITION_JUMP,
                        int_value=tokens[1].value
                    )
                elif tokens[1].type == TokenType.NYANG:
                    # 냐<변수형>!
                    return Command(
                        kind=CommandKind.UNCONDITION_JUMP,
                        nyang_id=tokens[1].value
                    )
            if tokens[2].type == TokenType.BANG and tokens[2].value == 2:
                if tokens[1].type == TokenType.INT:
                    # 냐<숫자형>!!
                    return Command(
                        kind=CommandKind.CONDITION_JUMP,
                        int_value=tokens[1].value
                    )
                elif tokens[1].type == TokenType.NYANG:
                    # 냐<변수형>!!
                    return Command(
                        kind=CommandKind.CONDITION_JUMP,
                        nyang_id=tokens[1].value
                    )
    
    raise SyntaxError(f"파싱할 수 없는 문장 패턴입니다. : {tokens}")