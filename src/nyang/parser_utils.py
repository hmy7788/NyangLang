class TokenStream:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None
    
    def consume(self):
        if self.pos < len(self.tokens):
            t = self.tokens[self.pos]
            self.pos += 1
            return t
        return None
    
    def consume_value(self, target_type, needed_amount):
        """
        """
        token = self.peek()

        if not token or token.type != target_type:
            return None
        
        if token.value == needed_amount:
            self.pos += 1
            return token
        
        elif token.value > needed_amount:
            token.value -= needed_amount