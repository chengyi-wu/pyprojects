###### Lexer ########
class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return "Token({type}, {value})".format(type=self.type, value=self.value)

RESERVED_KEYWORDS = {
    'BEGIN' : Token('BEGIN', 'BEGIN'),
    'END' : Token('END', 'END'),
    'DIV' : Token('DIV', 'DIV')
}

class Lexer(object):
    def __init__(self, text):
        self.pos = 0
        self.text = text
        self.current_char = self.text[self.pos]
        self.token_types = {
            '.' : 'DOT',
            ';' : 'SEMI',
            '+' : 'PLUS',
            '-' : 'MINUS',
            '*' : 'MUL',
            #'/' : 'DIV',
            '(' : 'LPAREN',
            ')' : 'RPAREN'
        }

    def advance(self):
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        return self.text[peek_pos]

    def skip_whitespace(self):
        text = self.text
        while self.pos < len(text) and self.current_char.isspace():
            self.advance()

    def getNumber(self):
        result = ''
        text = self.text
        while self.pos < len(text) and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return Token('INTEGER', int(result))

    def getWord(self):
        word = ''
        text = self.text
        while self.current_char is not None\
             and (self.current_char.isalnum() or self.current_char == '_'):
            word += self.current_char
            self.advance()
        # Set the word to upper case, making keyword case insensitve
        token = RESERVED_KEYWORDS.get(word.upper(), Token('ID', word))
        return token

    def error(self):
        raise Exception("Invalid input: {pos}".format(pos=self.pos))

    def get_next_token(self):
        text = self.text
        while self.pos < len(text):
            if self.current_char.isspace():
                self.advance()
            elif self.current_char in self.token_types:
                token = Token(self.token_types[self.current_char], self.current_char)
                self.advance()
                return token
            elif self.current_char.isdigit():
                return self.getNumber()
            elif self.current_char.isalpha() or self.current_char == '_':
                return self.getWord()
            elif self.current_char == ':' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token('ASSIGN', ':=')
            else:
                self.error()

        return Token('EOF', 'EOF')