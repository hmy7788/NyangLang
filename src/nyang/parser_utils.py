from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from tkinter import N
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


class TokenStream:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Optional[Token] | None:
        """
        input: 토큰 리스트
        output: 현재 pos 위치의 토큰 (없으면 None)
        - 현재 pos 위치의 토큰을 반환하는 함수
        - pos의 위치는 변화 x
        """
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self) -> Optional[Token] | None:
        """
        input: 토큰 리스트
        output: 현재 pos 위치의 토큰 (없으면 None)  
        - 현재 pos 위치의 토큰을 소비하고 pos의 위치는 다음 토큰으로 넘어감
        """
        if self.pos < len(self.tokens):
            t = self.tokens[self.pos]
            self.pos += 1
            return t
        return None

    def consume_value(self, target_type: TokenType, needed_amount: int):
        """
        ★ 핵심 기능: 토큰 쪼개기 (Token Splitting)
        예: (BANG, 3)이 있을 때 needed_amount=1을 요청하면
            -> 현재 토큰을 (BANG, 2)로 줄이고,
            -> (BANG, 1)에 해당하는 가상의 토큰을 리턴
        """
        token = self.peek()
        
        # 토큰이 없거나 타입이 다르면 실패
        if not token or token.type != target_type:
            return None
        
        # 1. 딱 맞는 경우 (그냥 소비)
        if token.value == needed_amount:
            self.pos += 1
            return token
        
        # 2. 토큰 값이 더 큰 경우 (쪼개기!) -> 님이 원하던 기능
        elif token.value > needed_amount:
            # 원본 토큰의 값을 줄임 (3 -> 2)
            token.value -= needed_amount
            # 1짜리 새 토큰을 리턴 (마치 1짜리가 있었던 것처럼)
            return Token(target_type, needed_amount)
            
        # 3. 값이 부족한 경우
        else:
            return None # 에러 처리


def parse_nyang_command(token_stream: TokenStream) -> Command:
    nyang_token = token_stream.consume()
    next_token = token_stream.peek()
    
    if next_token is None:
        return None

    if next_token.type == TokenType.INT:
        int_token = next_token
        token_stream.consume()
        return Command(CommandKind.VAR_DECL, nyang_id=nyang_token.value, int_value=int_token.value)

    if next_token.type == TokenType.TILDE:
        tilde_token = next_token
        token_stream.consume()
        return Command(CommandKind.VAR_PUSH_OR_ACCESS, nyang_id=nyang_token.value)

    if next_token.type == TokenType.QUESTION:
        question_token = next_token
        token_stream.consume()
        return Command(CommandKind.INPUT, nyang_id=nyang_token.value)

    if next_token.type == TokenType.BANG:
        bang_token = next_token
        token_stream.consume()
        next_token = token_stream.peek()

        if next_token is None: return None

        if next_token.type == TokenType.QUESTION:
            question_token = next_token
            token_stream.consume()
            
            if bang_token.value == 1: output_form = 'decimal'
            elif bang_token.value == 2: output_form = 'ascii'
            else: return None

            if question_token.value == 1: output_mode = 'newline'
            elif question_token.value == 2: output_mode = 'inline'
            elif question_token.value == 3: output_mode = 'space'
            else: return None

            return Command(CommandKind.OUTPUT, 
                           output_kind='nyang',
                           output_form=output_form,
                           output_mode=output_mode,
                           nyang_id=nyang_token.value)

        else:
            return None

    return None



def parse_nya_command(token_stream: TokenStream) -> Command:
    nya_token = token_stream.consume()
    next_token = token_stream.peek()

    if next_token is None: return None

    if next_token.type == TokenType.TILDE:
        tilde_token = next_token
        token_stream.consume()
        return Command(CommandKind.OPERATION, op_arity=tilde_token.value)

    return None


def parse_int_command(token_stream: TokenStream) -> Command:
    int_token = token_stream.consume()
    next_token = token_stream.peek()

    if next_token is None:
        return None

    if next_token.type == TokenType.TILDE:
        tilde_token = next_token
        token_stream.consume()
        return Command(CommandKind.VALUE_PUSH, int_value=int_token.value)

    if next_token.type == TokenType.BANG:
        bang_token = next_token
        token_stream.consume()
        next_token = token_stream.peek()

        if next_token is None: return None

        if next_token.type == TokenType.QUESTION:
            question_token = next_token
            token_stream.consume()

            if bang_token.value == 1: output_form = 'decimal'
            elif bang_token.value == 2: output_form = 'ascii'
            else: return None

            if question_token.value == 1: output_mode = 'newline'
            elif question_token.value == 2: output_mode = 'inline'
            elif question_token.value == 3: output_mode = 'space'
            else: return None

            return Command(CommandKind.OUTPUT,
                           output_kind='int',
                           output_form=output_form,
                           output_mode=output_mode,
                           int_value=int_token.value)

        else: return None

    return None