# 01_core/lexer.py
# 한 줄을 토큰 리스트로 바꾸는 코드

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional



class TokenType(Enum):
    NYANG = auto()      # "냥" 연속 개수
    NYA = auto()        # "냐" 연속 개수 (연산)
    INT = auto()        # . , 조합 -> 정수 리터럴 값
    TILDE = auto()      # "~"
    BANG = auto()       # "!", "!!"
    QUESTION = auto()   # "?" 



@dataclass
class Token:
    type: TokenType
    value: Optional[int] = None


ALLOWED_CHARS = {"냥", "냐", ".", ",", "~", "!", "?"}


def _strip_comments(line: str) -> str:
    """
    #### input: 1개 라인의 명령어
    - "냥", "냐", ".", ",", "~", "!", "?" 외 문자는 주석 취급
    #### output: 주석을 제외한 명령어
    """
    idx = line.find("#")
    if idx != -1: line = line[:idx]
    return "".join(ch for ch in line if ch in ALLOWED_CHARS)


def classify_char(ch: str) -> TokenType | None:
    if ch == "냥":
        return TokenType.NYANG
    if ch == "냐":
        return TokenType.NYA
    if ch == "." or ch == ",":
        return TokenType.INT
    if ch == "~":
        return TokenType.TILDE
    if ch == "!":
        return TokenType.BANG
    if ch == "?":
        return TokenType.QUESTION
    return None



def lex_line(line: str) -> List[Token]:
    """
    input: 명령어 라인
    - 한 줄을 토큰 리스트로 변환
    output: 명령어에 대한 토큰 리스트
    """
    line = _strip_comments(line)
    tokens: List[Token] = []
    current_type: TokenType | None = None
    count: int = 0

    if not line:
        return []

    for ch in line:
        ttype = classify_char(ch)

        if ttype is None:
            if (current_type is not None) and (count):
                tokens.append(Token(current_type, count))
                current_type = None
                count = 0
            continue

        if (current_type is None) or (current_type != ttype):
            if current_type is not None:
                tokens.append(Token(current_type, count))

            current_type = ttype

            if ttype == TokenType.INT:
                count = 1 if ch == '.' else -1
            else:
                count = 1
        else:
            if ttype == TokenType.INT:
                count += 1 if ch == '.' else -1
            else:
                count += 1

    # 마지막 토큰 flush
    if current_type is not None and count:
        tokens.append(Token(current_type, count))

    return tokens


# 테스트
if __name__ == "__main__":
    print(lex_line("냥!?....!?~"))