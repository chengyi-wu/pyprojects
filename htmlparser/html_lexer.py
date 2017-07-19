token_types = {
    '<' : 'LTAG',
    '>' : 'RTAG',
    # '/' : 'SLAH',
    # '-' : 'DASH',
    # '"' : 'DQUOTE',
    # "'" : 'SQUOTE',
    # '!' : 'EXC',
    # '=' : 'EQUAL',
    # ';' : 'SEMI',
    # '#' : "#",
    # '.' : 'DOT',
    # '+' : "PLUS",
    # '-' : "MINUS",
    # ':' : 'COLON'
}

class Token(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value
    
    def __str__(self):
        return "<Token:{name}-{value}>".format(name=self.name,value=self.value)

class Lexer(object):
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]
        #print(self.current_char)

    def advance(self):
        text = self.text
        if self.pos < len(text) - 1:
            self.pos += 1
            self.current_char = text[self.pos]
            #print self.current_char,
        else:
            self.current_char = None

    def skip_whitespace(self):
        if self.current_char is not None and self.current_char.isspace():
            self.advance()

    def identifier(self):
        result = ''
        while self.current_char is not None \
            and not self.current_char.isspace()\
            and self.current_char not in token_types:
            result += self.current_char
            self.advance()
        return Token('ID', result)


    def get_next_token(self):
        
        while self.current_char is not None and self.current_char.isspace():
            self.skip_whitespace()

        #print(self.current_char,self.pos, ord(self.current_char))

        if self.current_char in token_types:
            token = Token(self.current_char, token_types[self.current_char])
            self.advance()
            return token
        elif self.current_char is not None:
            return self.identifier()
        
        return Token('EOF', 'EOF')