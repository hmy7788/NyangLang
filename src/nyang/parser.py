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



def parse_line(tokens: List[Token]) -> Command:
    """
    """
    if not tokens:
        return Command(kind=CommandKind.NOOP)
    

    if len(tokens) == 1:
        if tokens[0].type == TokenType.NYANG:
            return Command(
                kind=CommandKind.VAR_DECL,
                nyang_id=tokens[0].value,
                int_value=0
            )
    

    if len(tokens) == 2:
        # 1) 변수 선언 & 초기화: <냥 N개><. , M개>
        if tokens[0].type == TokenType.NYANG:
            if tokens[1].type == TokenType.INT:
                return Command(
                    kind=CommandKind.VAR_DECL,
                    nyang_id=tokens[0].value,
                    int_value=tokens[1].value
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
                    kind=CommandKind.OUTPUT,
                    int_value=tokens[0].value,
                    output_form=1
                )
            # <정수형>!!
            elif tokens[1].type == TokenType.BANG and tokens[1].value == 2:
                return Command(
                    kind=CommandKind.OUTPUT,
                    int_value=tokens[0].value,
                    output_form=2
                )
            
        
        # 6-2) 출력: <냥 N개>! or <냥 N개>!!
        if tokens[0].type == TokenType.NYANG:
            # <냥 N개>!
            if tokens[1].type == TokenType.BANG and tokens[1].value == 1:
                return Command(
                        kind=CommandKind.OUTPUT,
                        nyang_id=tokens[0].value,
                        output_form=3
                )
            # <냥 N개>!!
            elif tokens[1].type == TokenType.BANG and tokens[1].value == 2:
                return Command(
                    kind=CommandKind.OUTPUT,
                    nyang_id=tokens[0].value,
                    output_form=4
                )

        # 6-3) 출력(내장함수): 냐! or 냐!!
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
        # 출력: 정수형<!/!!><?/??/???>
        if tokens[0].type == TokenType.INT and tokens[1].type == TokenType.BANG and tokens[2].type == TokenType.QUESTION:
            # 정수형!<?/??/???>
            if tokens[1].value == 1:
                # 정수형!?
                if tokens[2].value == 1:
                    return Command(
                        kind=CommandKind.OUTPUT,
                        output_kind="integer",
                        output_form="decimal",
                        output_mode="newline",
                        int_value=tokens[0].value
                    )
                # 정수형!??
                if  tokens[2].value == 2:
                    return Command(
                        kind=CommandKind.OUTPUT,
                        output_kind="integer",
                        output_form="decimal",
                        output_mode="inline",
                        int_value=tokens[0].value
                    )
                # 정수형!???
                if tokens[2].value == 3:
                    return Command(
                        kind=CommandKind.OUTPUT,
                        output_kind="integer",
                        output_form="decimal",
                        output_mode="space",
                        int_value=tokens[0].value
                    )
                
            # # 정수형!!<?/??/???>
            if tokens[1].value == 2:
                # 정수형!!?
                if tokens[2].value == 1:
                    return Command(
                        kind=CommandKind.OUTPUT,
                        output_kind="integer",
                        output_form="ascii",
                        output_mode="newline",
                        int_value=tokens[0].value
                    )
                # 정수형!!??
                if tokens[2].value == 2:
                    return Command(
                        kind=CommandKind.OUTPUT,
                        output_kind="integer",
                        output_form="ascii",
                        output_mode="inline",
                        int_value=tokens[0].value
                    )
                # 정수형!!???
                if tokens[2].value == 3:
                    return Command(
                        kind=CommandKind.OUTPUT,
                        output_kind="integer",
                        output_form="ascii",
                        output_mode="space",
                        int_value=tokens[0].value
                    )

        # 출력: 변수형<!/!!><?/??/???>
        if tokens[0].type == TokenType.NYANG and tokens[1].type == TokenType.BANG and tokens[2].type == TokenType.QUESTION:
            # 출력: 변수형!<?/??/???>
            if tokens[1].value == 1:
                # 출력: 변수형!?
                if tokens[2].value == 1:
                    return Command(
                        kind=CommandKind.OUTPUT,
                        output_kind="variable",
                        output_form="decimal",
                        output_mode="newline",
                        nyang_id=tokens[0].value
                    )
                # 출력: 변수형!?
                if tokens[2].value == 2:
                    return Command(
                        kind=CommandKind.OUTPUT,
                        output_kind="variable",
                        output_form="decimal",
                        output_mode="inline",
                        nyang_id=tokens[0].value
                    )
                # 출력: 변수형!?
                if tokens[2].value == 3:
                    return Command(
                        kind=CommandKind.OUTPUT,
                        output_kind="variable",
                        output_form="decimal",
                        output_mode="space",
                        nyang_id=tokens[0].value
                    )

            # 출력: 변수형!!<?/??/???>
            if tokens[1].value == 2:
                # 출력: 변수형!!?
                if tokens[2].value == 1:
                    return Command(
                        kind=CommandKind.OUTPUT,
                        output_kind="variable",
                        output_form="ascii",
                        output_mode="newline",
                        nyang_id=tokens[0].value
                    )
                # 출력: 변수형!!??
                if tokens[2].value == 2:
                    return Command(
                        kind=CommandKind.OUTPUT,
                        output_kind="variable",
                        output_form="ascii",
                        output_mode="inline",
                        nyang_id=tokens[0].value
                    )
                # 출력: 변수형!!???
                if tokens[2].value == 3:
                    return Command(
                        kind=CommandKind.OUTPUT,
                        output_kind="variable",
                        output_form="ascii",
                        output_mode="space",
                        nyang_id=tokens[0].value
                    )


        # 점프문
        if tokens[0].type == TokenType.INT and tokens[1].type == TokenType.QUESTION:
            # 점프문1: <숫자형>?<숫자형>
            if tokens[2].type == TokenType.INT:
                return Command(
                    kind=CommandKind.JUMP,
                    condition=tokens[0].value,
                    line=tokens[2].value,
                    jump_kind=1
                )
            # 점프문2: <숫자형>?<변수형>
            if tokens[2].type == TokenType.NYANG:
                return Command(
                    kind=CommandKind.JUMP,
                    condition=tokens[0].value,
                    line=tokens[2].value,
                    jump_kind=2
                )
        if tokens[0].type == TokenType.NYANG and tokens[1].type == TokenType.QUESTION:
            # 점프문3: <변수형>?<숫자형>
            if tokens[2].type == TokenType.INT:
                return Command(
                    kind=CommandKind.JUMP,
                    condition=tokens[0].value,
                    line=tokens[2].value,
                    jump_kind=3
                )
            # 점프문4: <변수형>?<변수형>
            if tokens[2].type == TokenType.NYANG:
                return Command(
                    kind=CommandKind.JUMP,
                    condition=tokens[0].value,
                    line=tokens[2].value,
                    jump_kind=4
                )
    
        # 배열 선언문: <배열명>!<정수형/변수형>
        if tokens[0].type == TokenType.NYANG and tokens[1].type == TokenType.BANG:
            # 배열명!<정수형>
            if tokens[2].type == TokenType.INT:
                return Command(
                    kind=CommandKind.ARRAY_DECL,
                    array_decl_mode=0,
                    array_id=tokens[0].value,
                    array_length=tokens[2].value
                )

            # 배열명!<변수형>
            if tokens[2].type == TokenType.NYANG:
                return Command(
                    kind=CommandKind.ARRAY_DECL,
                    array_decl_mode=1,
                    array_id=tokens[0].value,
                    array_length=tokens[2].value
                )

    
    if len(tokens) == 4:
        pass

    if len(tokens) == 5:
        # 배열 쓰기: <배열명>!<정수형/변수형>!<정수형/변수형>
        if tokens[0].type == TokenType.NYANG and tokens[1].type == TokenType.BANG and tokens[3].type == TokenType.BANG:
            # 배열명!정수형!정수형
            if tokens[2].type == TokenType.INT and tokens[4].type == TokenType.INT:
                return Command(
                    kind=CommandKind.ARRAY_WRITE,
                    array_write_mode=0,
                    array_id=tokens[0].value,
                    array_idx=tokens[2].value,
                    int_value=tokens[4].value
                )
            
            # 배열명!정수형!변수형
            if tokens[2].type == TokenType.INT and tokens[4].type == TokenType.NYANG:
                return Command(
                    kind=CommandKind.ARRAY_WRITE,
                    array_write_mode=1,
                    array_id=tokens[0].value,
                    array_idx=tokens[2].value,
                    int_value=tokens[4].value
                )

            # 배열명!변수형!정수형
            if tokens[2].type == TokenType.NYANG and tokens[4].type == TokenType.INT:
                return Command(
                    kind=CommandKind.ARRAY_WRITE,
                    array_write_mode=2,
                    array_id=tokens[0].value,
                    array_idx=tokens[2].value,
                    int_value=tokens[4].value
                )

            # 배열명!변수형!변수형
            if tokens[2].type == TokenType.NYANG and tokens[4].type == TokenType.NYANG:
                return Command(
                    kind=CommandKind.ARRAY_WRITE,
                    array_write_mode=3,
                    array_id=tokens[0].value,
                    array_idx=tokens[2].value,
                    int_value=tokens[4].value
                )


    if len(tokens) == 7:
        if tokens[0].type == TokenType.NYANG and tokens[1].type == TokenType.BANG and tokens[2].type == TokenType.QUESTION:
            if tokens[4].type == TokenType.BANG and tokens[5].type == TokenType.QUESTION:
                if tokens[3].type == TokenType.INT and tokens[6].type == TokenType.TILDE:
                    return Command(
                        kind=CommandKind.ARRAY_READ,
                        array_id=tokens[0].value,
                        array_read_mode=0,
                        array_idx=tokens[3].value
                    )

                if tokens[3].type == TokenType.INT and tokens[6].type == TokenType.NYANG:
                    return Command(
                        kind=CommandKind.ARRAY_READ,
                        array_id=tokens[0].value,
                        array_read_mode=1,
                        array_idx=tokens[3].value,
                        nyang_id=tokens[6].value
                    )

                if tokens[3].type == TokenType.NYANG and tokens[6].type == TokenType.TILDE:
                    return Command(
                        kind=CommandKind.ARRAY_READ,
                        array_id=tokens[0].value,
                        array_read_mode=2,
                        array_idx=tokens[3].value,
                    )

                if tokens[3].type == TokenType.INT and tokens[6].type == TokenType.NYANG:
                    return Command(
                        kind=CommandKind.ARRAY_READ,
                        array_id=tokens[0].value,
                        array_read_mode=3,
                        array_idx=tokens[3].value,
                        nyang_id=tokens[6].value
                    )
            

    raise SyntaxError(f"파싱할 수 없는 문장 패턴입니다. : {tokens}")