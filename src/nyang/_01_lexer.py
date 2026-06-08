# 한 줄을 토큰 리스트로 바꾸는 코드

# import ========================================
from __future__ import annotations
from typing import List

from nyang._00_types import TokenType, Token
# import ========================================


def _strip_comments(line: str) -> str:
    """
    #### input: 1개 라인의 명령어
    - "냥", "냐", ".", ",", "~", "!", "?" 외 문자는 주석 취급
    #### output: 주석을 제외한 명령어
    """
    idx = line.find("#")
    if idx != -1: 
        return line[:idx]
    return line


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
    line = _strip_comments(line)
    tokens: List[Token] = []
    current_type: TokenType | None = None
    count: int = 0
    n = len(line)

    if not line.strip(): return []

    i = 0
    while i < n:
        ch = line[i]
        if ch.isspace():
            if current_type is not None:
                tokens.append(Token(current_type, count))
                current_type, count = None, 0
            i += 1
            continue

        if ch == '야' and i+1 < n and line[i+1] == '옹':
            if current_type is not None:
                tokens.append(Token(current_type, count))
                current_type, count = None, 0
            tokens.append(Token(TokenType.YAONG))
            i += 2
            continue

        ttype = classify_char(ch)
        if ttype is None:
            # 토큰에 쓰이는 문자(냥/냐/./,/~/!/?/야옹) 외의 모든 문자는 주석으로 간주하고 무시
            if current_type is not None:
                tokens.append(Token(current_type, count))
                current_type, count = None, 0
            i += 1
            continue

        # 1. 타입이 바뀌면 지금까지 쌓인 토큰을 저장(Flush)
        if current_type != ttype:
            if current_type is not None:
                tokens.append(Token(current_type, count))

            # 새 토큰 시작
            current_type = ttype
            if ttype == TokenType.INT:
                count = 1 if ch == '.' else -1
            else:
                count = 1

        # 2. 같은 타입이면 계속 개수만 세기 (제한 없이!)
        else:
            if ttype == TokenType.INT:
                count += 1 if ch == "." else -1
            else:
                count += 1

        i += 1

    # 마지막 남은 토큰 처리
    if current_type is not None:
        tokens.append(Token(current_type, count))

    return tokens


def print_lex_line(line: List[Token]) -> None:
    for token in line:
        print(f"({token.type.name},{token.value})", end=' ')