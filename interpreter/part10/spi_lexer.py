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
    'DIV' : Token('INTEGER_DIV', 'DIV'),
    'PROGRAM' : Token('PROGRAM', 'PROGRAM'),
    'VAR' : Token('VAR', 'VAR'),
    'INTEGER' : Token('INTEGER', 'INTEGER'),
    'REAL' : Token('REAL', 'REAL'),
}

class Lexer(object):
    def __init__(self, text):
        self.pos = 0
        self.text = text
        self.current_token = None
        self.current_char = self.text[self.pos]
        self.token_types = {
            '.' : 'DOT',
            ';' : 'SEMI',
            '+' : 'PLUS',
            '-' : 'MINUS',
            '*' : 'MUL',
            '/' : 'FLOAT_DIV',
            '(' : 'LPAREN',
            ')' : 'RPAREN',
            ',' : 'COMMA',
            ':' : 'COLON',
            #'{' : 'LBRACE',
            #'}' : 'RBRACE',
            #"'" : 'SINGLEQUOTE',
            #'"' : 'DOUBLEQUOTE',
            #'=' : 'EQUAL'
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
        
    def skip_comment(self):
        while self.current_char != '}':
            self.advance()
        self.advance() # the closing curly brace

    def number(self):
        '''
        Use decimal point to determine integer or float
        '''
        result = ''
        isfloat = False
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
            if self.current_char == '.':
                isfloat = True
                result += self.current_char
                self.advance()
                while self.current_char is not None and self.current_char.isdigit():
                    result += self.current_char
                    self.advance()
        if isfloat:
            return Token('REAL_CONST', float(result))
        return Token('INTEGER_CONST', int(result))

    def identifier(self):
        ident = ''
        text = self.text
        while self.current_char is not None\
             and (self.current_char.isalnum() or self.current_char == '_'):
            ident += self.current_char
            self.advance()
        # Set the word to upper case, making keyword case insensitve
        ident = ident.upper()
        token = RESERVED_KEYWORDS.get(ident, Token('ID', ident))
        return token

    def error(self):
        raise Exception("Invalid input: '{ch}', pos: {pos}".format(pos=self.pos,ch=self.text[self.pos]))

    def get_next_token(self):
        text = self.text
        while self.pos < len(text):
            if self.current_char.isspace():
                self.advance()
            elif self.current_char == ':' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token('ASSIGN', ':=')
            elif self.current_char in self.token_types:
                token = Token(self.token_types[self.current_char], self.current_char)
                self.advance()
                return token
            elif self.current_char.isdigit():
                # either it's float or integer
                return self.number()
            elif self.current_char.isalpha() or self.current_char == '_':
                return self.identifier()
            elif self.current_char == '{':
                self.advance()
                self.skip_comment()
            else:
                self.error()

        return Token('EOF', 'EOF')