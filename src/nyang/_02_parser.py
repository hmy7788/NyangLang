# 토큰을 커맨드로 바꾸는 코드

# import =============================================================
from __future__ import annotations
from typing import Optional, List
from dataclasses import asdict

from nyang._00_types import TokenType, Token, Command, CommandKind
# import =============================================================

# TokenStream ==============================================================
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
    
    def peek_offset(self, offset: int) -> Optional[Token] | None:
        """
        """
        idx = self.pos + offset
        return self.tokens[idx] if idx < len(self.tokens) else None


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
# TokenStream ==============================================================


# parse_*_command ===================================================================================
def parse_nyang_command(token_stream: TokenStream) -> Command:
    nyang_token = token_stream.consume()    # <NYANG> 소비
    next_token = token_stream.peek()        # 다음 토큰 확인

    if next_token is None: return None

    # <NYANG><INT>: VAR_DECL
    if next_token.type == TokenType.INT:
        int_token = next_token
        token_stream.consume()  # <INT> 소비
        # <NYANG><INT>: VAR_DECL
        return Command(CommandKind.VAR_DECL, 
                       nyang_id=nyang_token.value, 
                       int_value=int_token.value)
    
    # <NYANG><~>
    elif next_token.type == TokenType.TILDE:
        
        if next_token.value == 1:
            tilde_token = next_token
            token_stream.consume()  # <~> 소비
            # <NYANG>~: VAR_PUSH
            return Command(CommandKind.VAR_PUSH, 
                           nyang_id=nyang_token.value)
        
        elif next_token.value == 2:
            tilde_token = next_token
            token_stream.consume()  # <~> 소비
            # <NYANG>~~: VAR_ASSIGN
            return Command(CommandKind.VAR_ASSIGN, 
                           nyang_id=nyang_token.value)

    # <NYANG><?>
    elif next_token.type == TokenType.QUESTION:
        question_token = next_token
        token_stream.consume()  # <?> 소비

        # <NYANG>?
        if question_token.value == 1:
            question_token = next_token
            next_token = token_stream.peek()

            if next_token is None:
                raise SyntaxError()

            if next_token.type == TokenType.INT:
                int_token = next_token
                token_stream.consume()  # <INT> 소비
                # <NYANG>?<INT>: JUMP, kind=nyang?int
                return Command(CommandKind.JUMP,
                               jump_kind='nyang?int',
                               condition=nyang_token.value,
                               jump_line=int_token.value)

            elif next_token.type == TokenType.NYANG:
                nyang_token2 = next_token
                token_stream.consume()  # <NYANG> 소비
                # <NYANG>?<NYANG>: JUMP, kind=nyang?nyang
                return Command(CommandKind.JUMP,
                               jump_kind='nyang?nyang',
                               condition=nyang_token.value,
                               jump_line=nyang_token2.value)

        elif question_token.value == 2:
            # <NYANG>??: INPUT
            return Command(CommandKind.INPUT,
                           nyang_id=nyang_token.value)
        
        else:
            raise SyntaxError(f'물음표 개수때문에 ~ 물음표 개수: {question_token.value}')
        
    elif next_token.type == TokenType.BANG:
        # BANG(1)만 배열 ops 후보; BANG(2)는 항상 ascii OUTPUT
        if next_token.value == 1:
            after_bang = token_stream.peek_offset(1)  # BANG 다음 토큰

            # <NYANG>!<INT/NYANG> → ARRAY_DECL 또는 ARRAY_WRITE
            if after_bang is not None and after_bang.type in (TokenType.INT, TokenType.NYANG):
                token_stream.consume()                       # BANG 소비
                idx_or_len_token = token_stream.consume()   # INT 또는 NYANG 소비
                nxt = token_stream.peek()

                if nxt is not None and nxt.type == TokenType.BANG:
                    # <NYANG>!<INT/NYANG>!<INT/NYANG> → ARRAY_WRITE
                    token_stream.consume_value(TokenType.BANG, 1)
                    val_token = token_stream.consume()
                    mode = (0 if idx_or_len_token.type == TokenType.INT else 2) + \
                           (0 if val_token.type == TokenType.INT else 1)
                    return Command(CommandKind.ARRAY_WRITE,
                                   array_id=nyang_token.value,
                                   array_idx=idx_or_len_token.value,
                                   int_value=val_token.value,
                                   array_write_mode=mode)
                elif nxt is not None and nxt.type == TokenType.QUESTION and nxt.value == 2:
                    # <NYANG>!<INT/NYANG>?? → ARRAY_INPUT
                    token_stream.consume()  # ?? 소비
                    mode = 0 if idx_or_len_token.type == TokenType.INT else 1
                    return Command(CommandKind.ARRAY_INPUT,
                                   array_id=nyang_token.value,
                                   array_idx=idx_or_len_token.value,
                                   array_write_mode=mode)
                else:
                    # <NYANG>!<INT/NYANG> → ARRAY_DECL
                    mode = 0 if idx_or_len_token.type == TokenType.INT else 1
                    return Command(CommandKind.ARRAY_DECL,
                                   array_id=nyang_token.value,
                                   array_length=idx_or_len_token.value,
                                   array_decl_mode=mode)

            # <NYANG>!?<INT/NYANG>... → ARRAY_READ
            elif (after_bang is not None and
                  after_bang.type == TokenType.QUESTION and after_bang.value == 1 and
                  token_stream.peek_offset(2) is not None and
                  token_stream.peek_offset(2).type in (TokenType.INT, TokenType.NYANG)):
                token_stream.consume()                              # BANG 소비
                token_stream.consume_value(TokenType.QUESTION, 1)  # ? 소비
                idx_token = token_stream.consume()                  # INT 또는 NYANG 소비
                token_stream.consume_value(TokenType.BANG, 1)      # ! 소비
                token_stream.consume_value(TokenType.QUESTION, 1)  # ? 소비
                dest = token_stream.peek()
                if dest is not None and dest.type == TokenType.TILDE:
                    token_stream.consume_value(TokenType.TILDE, 1)
                    mode = 0 if idx_token.type == TokenType.INT else 2
                    return Command(CommandKind.ARRAY_READ,
                                   array_id=nyang_token.value,
                                   array_idx=idx_token.value,
                                   array_read_mode=mode)
                elif dest is not None and dest.type == TokenType.NYANG:
                    dest_token = token_stream.consume()
                    mode = 1 if idx_token.type == TokenType.INT else 3
                    return Command(CommandKind.ARRAY_READ,
                                   array_id=nyang_token.value,
                                   array_idx=idx_token.value,
                                   nyang_id=dest_token.value,
                                   array_read_mode=mode)
                else:
                    raise SyntaxError("ARRAY_READ: !?<인덱스>!? 뒤에 ~ 또는 변수가 와야 합니다.")

        # 기존 OUTPUT 처리 (BANG(1) decimal 또는 BANG(2) ascii)
        bang_token = next_token
        output_form = None

        # <NYANG>!
        if bang_token.value == 1: output_form = 'decimal'
        # <NYANG>!!
        elif bang_token.value == 2: output_form = 'ascii'
        # 느낌표 개수 오류
        else: raise SyntaxError(f'느낌표 개수때문에 ~ 느낌표 개수: {bang_token.value}')

        token_stream.consume()
        next_token = token_stream.peek()

        if next_token is None:
            raise SyntaxError()

        output_mode = None
        if next_token.type == TokenType.QUESTION:
            question_token = next_token

            # <NYANG><!>?
            if question_token.value == 1: output_mode = 'newline'
            # <NYANG><!>??
            elif question_token.value == 2: output_mode = 'inline'
            # <NYANG><!>???
            elif question_token.value == 3: output_mode = 'space'
            # 물음표 개수 오류
            else: raise SyntaxError(f'물음표 개수때문에 ~ 물음표 개수: {question_token.value}')

            token_stream.consume()

        return Command(CommandKind.OUTPUT,
                       output_kind='nyang',
                       output_form=output_form,
                       output_mode=output_mode,
                       nyang_id=nyang_token.value)

    return None

def parse_int_command(token_stream: TokenStream) -> Command:
    int_token = token_stream.consume()  # <INT> 소비
    next_token = token_stream.peek()    # 다음 토큰 확인

    # <INT><~>
    if next_token.type == TokenType.TILDE:
        tilde_token = next_token
        token_stream.consume()  # <~> 소비
        
        # <INT>~
        if tilde_token.value == 1:
            return Command(CommandKind.VALUE_PUSH,
                           int_value=int_token.value)
        else:
            raise SyntaxError()

    # <INT><!>
    if next_token.type == TokenType.BANG:
        bang_token = next_token
        token_stream.consume()  # <!> 소비

        output_form = None

        # <INT>!
        if bang_token.value == 1: output_form = 'decimal'
        # <INT>!!
        elif bang_token.value == 2: output_form = 'ascii'
        # 느낌표 개수 오류
        else: raise SyntaxError(f'느낌표 개수때문에 ~ 느낌표 개수: {bang_token.value}')

        next_token = token_stream.peek() # 다음 토큰 확인

        if next_token is None:
            raise SyntaxError()

        # <INT><!><?>
        if next_token.type == TokenType.QUESTION:
            question_token = next_token
            token_stream.consume() # <?> 소비
            output_mode = None

            # <INT><!>?
            if question_token.value == 1: output_mode = 'newline'
            # <INT><!>??
            elif question_token.value == 2: output_mode = 'inline'
            # <INT><!>???
            elif question_token.value == 3: output_mode = 'space'
            # 물음표 개수 오류
            else: raise SyntaxError(f'물음표 개수때문에 ~ 물음표 개수: {question_token.value}')

        return Command(CommandKind.OUTPUT,
                       output_kind='int',
                       output_form=output_form,
                       output_mode=output_mode,
                       int_value=int_token.value)

    # <INT><?>
    if next_token.type == TokenType.QUESTION:
        question_token = next_token

        # <INT>?
        if question_token.value == 1:
            token_stream.consume()
            next_token = token_stream.peek()

            # <INT>?<INT>
            if next_token.type == TokenType.INT:
                int_token2 = next_token
                token_stream.consume()

                return Command(CommandKind.JUMP,
                               jump_kind='int?int',
                               condition=int_token.value,
                               jump_line=int_token2.value)

            elif next_token.type == TokenType.NYANG:
                nyang_token2 = next_token
                token_stream.consume()

                return Command(CommandKind.JUMP,
                               jump_kind='int?nyang',
                               condition=int_token.value,
                               jump_line=nyang_token2.value)

        else:
            raise SyntaxError()


def parse_nya_command(token_stream: TokenStream) -> Command:
    nya_token = token_stream.consume()  # <NYA> 소비
    next_token = token_stream.peek()    # 다음 토큰 확인

    if next_token is None:
        raise SyntaxError()
    
    # 
    if next_token.type == TokenType.BANG:
        bang_token = next_token
        token_stream.consume() # <BANG> 소비

        if bang_token.value == 1:
            return Command(CommandKind.DISPLAY_STACK)
        if bang_token.value == 2:
            return Command(CommandKind.DISPLAY_VARIABLES_TABLE)
        else:
            raise SyntaxError(f'느낌표 개수때문에 ~ 느낌표 개수: {bang_token.value}')
        

    elif next_token.type == TokenType.TILDE:
        tilde_token = next_token
        token_stream.consume() # <~> 소비

        if tilde_token.value == 1:
            # <NYA>~: OPERATION
            return Command(CommandKind.OPERATION,
                           op_arity=nya_token.value)
        else:
            raise SyntaxError()
# parse_*_command ===================================================================================


def parse_command(token_stream: TokenStream) -> Optional[Command]:
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
    return None
    

def parse_line(tokens: List[Token]) -> List[Command]:
    """
    input: 토큰 리스트
    output: 명령어 리스트
    """
    token_stream = TokenStream(tokens)
    commands: List[Command] = []

    while token_stream.peek() is not None:
        before_pos = token_stream.pos
        command = parse_command(token_stream)

        # 토큰 소비가 되었는데 문법 매칭에 실패한 경우는 명시적으로 에러 처리
        if command is None:
            if token_stream.pos == before_pos:
                tok = token_stream.peek()
                raise SyntaxError(f"파싱이 진행되지 않았습니다: {tok}")
            raise SyntaxError(f"문장 파싱 실패 (근처 pos={before_pos})")

        # 커맨드 뒤에 반드시 야옹이 있어야 함
        yaong = token_stream.peek()
        if yaong is None or yaong.type != TokenType.YAONG:
            raise SyntaxError(f"'{command.kind.name}' 커맨드 뒤에 '야옹'이 없습니다")
        token_stream.consume()

        commands.append(command)
    return commands


# Testing =========================================================
def print_parse_line(commands: List[Command]) -> None:
    for cmd in commands:
        data = asdict(cmd)
        filtered = {k: v for k, v in data.items() if v is not None}
        # kind는 Enum이라 이름만 보이게
        filtered["kind"] = cmd.kind.name
        print(filtered)
# Testing =========================================================