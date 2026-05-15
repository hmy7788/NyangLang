# 토큰, 커맨드 타입 정의

# import ========================
from enum import Enum, auto
from typing import Optional
from dataclasses import dataclass
# import ========================

class TokenType(Enum):
    NYANG = auto()      # "냥" 연속 개수
    NYA = auto()        # "냐" 연속 개수 (연산)
    YAONG = auto()      # "야옹"
    INT = auto()        # . , 조합 -> 정수 리터럴 값
    TILDE = auto()      # "~"
    BANG = auto()       # "!", "!!"
    QUESTION = auto()   # "?"


@dataclass
class Token:
    type: TokenType
    value: Optional[int] = None


class CommandKind(Enum):
    NOOP = auto()               
    VAR_DECL = auto()                       # 변수 선언 + 초기화 (냥..)
    VALUE_PUSH = auto()                     # 상수 push (..)
    VAR_PUSH = auto()                       # 변수 push
    VAR_ASSIGN = auto()                     # 변수 대입
    OPERATION = auto()                      # 연산 (냐냐, 냐냐냐...)
    INPUT = auto()                          # 입력 (냥?)
    OUTPUT = auto()                         # 상수/변수값 -> 10진수/ASCII 출력
    DISPLAY_STACK = auto()                  # 스택 상태 출력 (!)
    DISPLAY_VARIABLES_TABLE = auto()        # 변수 테이블 출력 (!!)
    JUMP = auto()                           # 점프문: <숫자형/변수형>?<숫자형/변수형>
    ARRAY_DECL = auto()                     # 배열 선언
    ARRAY_WRITE = auto()                    # 배열 쓰기
    ARRAY_READ = auto()                     # 배열 읽기
    ARRAY_INPUT = auto()                    # 배열 직접 입력 (냥N!<idx>??야옹)


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
    jump_kind: Optional[str] = None
    condition: Optional[int] = None
    jump_line: Optional[int] = None
    array_decl_mode: Optional[int] = None
    array_write_mode: Optional[int] = None
    array_read_mode: Optional[int] = None
    array_id: Optional[int] = None
    array_length: Optional[int] = None
    array_idx: Optional[int] = None