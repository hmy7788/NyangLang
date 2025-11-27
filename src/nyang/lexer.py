# 01_core/lexer.py
# 한 줄을 토큰 리스트로 바꾸는 코드

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional



class TokenType(Enum):
    NYANG = auto()      # "냥" 연속 개수
    NYA = auto()        # "냐" 연속 개수 (연산용)
    INT = auto()        # . , 조합 -> 정수 리터럴 값
    TILDE = auto()      # "~"
    BANG = auto()       # "!", "!!"
    QUESTION = auto()   # "?" 
    EOL = auto()        # 줄 끝



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
    return "".join(ch for ch in line if ch in ALLOWED_CHARS)



def lex_line(line: str) -> List[Token]:
    """
    #### input: 명령어 라인
    - 한 줄을 토큰 리스트로 변환
    #### output: 명령어에 대한 토큰 리스트
    """
    line = _strip_comments(line)
    tokens: List[Token] = []

    if not line:
        return tokens
    
    
    bodys = {"냥", "냐"}
    symbols = {"~", "!", "?"}
    numbers = {".", ","}

    # 줄 끝 기호 파악
    end_char = line[-1] if line[-1] in {"~", "!", "?"} else None # ; print(f'end_char = {end_char}')
    body = line[:-1] if end_char else line # ; print(f'body = {body}')

    # 1) 앞부분: NYANG / NYA / INT 처리
    nyang_count = body.count("냥") # ; print(f'nyang_count = {nyang_count}')
    nya_count = body.count("냐") # ; print(f'nya_count = {nya_count}')
    dot_count = body.count(".") # ; print(f'dot_count = {dot_count}')
    comma_count = body.count(",") # ; print(f'comma_count = {comma_count}')

    # 
    if nyang_count > 0:
        tokens.append(Token(TokenType.NYANG, nyang_count))
    if nya_count > 0:
        tokens.append(Token(TokenType.NYA, nya_count))
    if dot_count + comma_count > 0:
        value = dot_count - comma_count
        tokens.append(Token(TokenType.INT, value))

    # 2) 끝 기호 처리
    if end_char == "~":
        tokens.append(Token(TokenType.TILDE))
    elif end_char == "?":
        tokens.append(Token(TokenType.QUESTION))
    elif end_char == "!":
        bang_count = line.count("!")
        tokens.append(Token(TokenType.BANG, bang_count))
    # elif end_char == "\n":
    #     tokens.append(Token(TokenType.EOL))

    return tokens

# 테스트
if __name__ == "__main__":
    print(lex_line("....!")) 