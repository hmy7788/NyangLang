# 토큰을 명령 객체로 바꾸는 부분
# 01_core/parser.py

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, List

from .lexer import Token, TokenType



class CommandKind(Enum):
    NOOP = auto()               
    VAR_DECL = auto()           # 변수 선언 + 초기화 (냥..)
    VALUE_PUSH = auto()         # 상수 push (..)
    VAR_ACCESS = auto()         # 변수 push or 대입 (런타임 결정)
    OPERATION = auto()          # 연산 (냐냐, 냐냐냐...)
    INPUT = auto()              # 입력 (냥?)
    OUTPUT_NUM_LITERAL = auto() # 상수 출력 (...!)
    OUTPUT_NUM_VAR = auto()     # 변수 숫자 출력 (냥!)
    OUTPUT_ASCII_VAR = auto()   # 변수 ASCII 출력 (냥!!)



@dataclass
class Command:
    kind: CommandKind
    nyang_id: Optional[int] = None
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

    

    # 1) 입력: <냥 N개>?
    if last.type == TokenType.QUESTION:
        if first.type == TokenType.NYANG:
            return Command(
                kind=CommandKind.INPUT,
                nyang_id=first.value
            )
        else:
            raise SyntaxError("입력 문법 오류")
        


    # 2) 연산: <냐 N개>~
    if last.type == TokenType.TILDE:
        if first.type == TokenType.NYA:
            return Command(
                kind=CommandKind.OPERATION,
                op_arity=first.value
            )
        else:
            raise SyntaxError("연산 문법 오류")
    


    # 3) 값 push: <. 또는 , N개>~
    if last.type == TokenType.TILDE:
        if first.type == TokenType.INT:
            return Command(
                kind=CommandKind.VALUE_PUSH,
                int_value=first.value
            )
        else:
            raise SyntaxError("스택 push 문법 오류")
        

    
    # 4) 변수 접근/대입: <냥 N개>~ -> 우선 분기로 안함
    if last.type == TokenType.TILDE:
        if first.type == TokenType.NYANG:
            return Command(
                kind=CommandKind.VAR_ACCESS,
                nyang_id=first.value
            )
        else:
            raise SyntaxError("")
    


    # 5) 출력: <숫자형>!
    if last.type == TokenType.BANG:
        if first.type == TokenType.INT:
            return Command(
                kind=CommandKind.OUTPUT_NUM_LITERAL,
                int_value=first.value,
                bang_count=last.value
            )
        else:
            raise SyntaxError("숫자형 출력 문법 오류")



    # 6) 출력: <냥 N개>! or <냥 N개>!!
    if last.type == TokenType.BANG:
        if first.type == TokenType.NYANG:
            if last.value == 1:
                return Command(
                    kind=CommandKind.OUTPUT_NUM_VAR,
                    nyang_id=first.value,
                    bang_count=1
                )
            elif last.value == 2:
                return Command(
                    kind=CommandKind.OUTPUT_ASCII_VAR,
                    nyang_id=first.value,
                    bang_count=2
                )
        else:
            raise SyntaxError("변수 출력을 지원하지 않는 형식입니다.")
        


    # 7) 변수 선언 + 초기화: <냥 N개><. 또는 ,>
    if first.type == TokenType.NYANG:
        if last.type == TokenType.INT:
            return Command(
                kind=CommandKind.VAR_DECL,
                nyang_id=first.value,
                int_value=last.value
            )
    
    raise SyntaxError(f"파싱할 수 없는 문장 패턴입니다. : {tokens}")        