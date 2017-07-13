# Token types
#
# EOF token is used to indicate that there's no more 
# input for lexical analysis

INTEGER, PLUS, MINUS, EOF = 'INTEGER', 'PLUS', 'MINUS', 'EOF'

class Token(object):
    def __init__(self, type, value):
        # token type: INTEGER, PLUS, or EOF
        self.type = type
        self.value = value

    def __str__(self):
        '''
        String representaion of the class instance.
        '''
        return 'Token({type}, {value})'.format(
            type=self.type,
            value=repr(self.value)
        )

    def __repr__(self):
        return self.__str__()

class Interpreter(object):
    def __init__(self, text):
        # client string input, e.g. "3+5", "12-5", etc
        self.text = text
        # self.pos is an index into self.ttext
        self.pos = 0
        # current token instance
        self.current_token = None
        self.current_char = self.text[self.pos]
        #self.advance() # this line cannot be correctly executed

    def error(self):
        raise Exception("Error parsing input")

    def advance(self):
        '''
        Advance the pos pointer and set the current_char varibale
        '''
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None # Indicates end of input
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def integer(self):
        '''
        Return a (multidigit) integer consumd from the input
        '''
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def get_next_token(self):
        '''
        Lexical analyzer (also know as scanner or tokenizer)

        This method is reponsible for breaking a sentence apart
        into tokens. One token at a time.
        '''

        while self.current_char is not None:
            
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return Token(INTEGER, self.integer())

            if self.current_char == '+':
                self.advance()
                return Token(PLUS, '+')

            if self.current_char == '-':
                self.advance()
                return Token(MINUS, '-')
            
            self.error()

        return Token(EOF, None)

    def eat(self, token_type):
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        #print(self.current_token, token_type)
        if self.current_token.type == token_type:
            self.current_token = self.get_next_token()
        else:
            self.error()

    def expr(self):
        '''
        Parser / Interpreter

        expr -> INTEGER PLUS INTEGER
        expr -> INTEGER MINUS INTEGER
        '''
        # set the current token into the first token from the input
        self.current_token = self.get_next_token()

        # we expect the current token to be a single-digit integer
        left = self.current_token
        self.eat(INTEGER)

        while self.current_token.type != EOF:
            # we expect the current token to be a '+' token
            op = self.current_token
            if op.type == PLUS:
                self.eat(PLUS)
            elif op.type == MINUS:
                self.eat(MINUS)
            else: # op.type == None
                continue
            # we expect the current token to be a single-digit integer
            right = self.current_token
            self.eat(INTEGER)

            # after the above call the self.current_token is set to EOF token

            # at this point either INTEGER PLUS INTEGER or 
            # INTEGER MINUS INTEGER sequence of tokens
            # has been successfully found and the method can just
            # return the result of adding tow integers, thus
            # effectively interpreting client input
            if op.type == PLUS:
                left.value += right.value
            else:
                left.value -= right.value
            #left.value = result
        return left.value

def main():
    while True:
        try:
            text = raw_input('calc> ')
        except EOFError:
            break
        if not text:
            continue
        interpreter = Interpreter(text)
        result = interpreter.expr()
        print(result)

if __name__ == '__main__':
    main()
