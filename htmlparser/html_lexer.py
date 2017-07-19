class Token(object):
    def __init__(self, name, value, pos):
        self.name = name
        self.value = value
        self.pos = pos
    
    def __str__(self):
        return "<Token:({name}, {value}, {pos})>".format(name=self.name,value=self.value,pos=self.pos)

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
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def tag(self):
        result = ''
        isEndTag = False
        if self.current_char == '/':
            isEndTag = True
            self.advance()
        pos = self.pos
        while self.current_char is not None\
            and self.current_char != '>':
            result += self.current_char
            self.advance()
        self.advance()
        if isEndTag:
            return Token('ENDTAG', result, pos)
        return Token('STARTTAG', result, pos)

    def literal(self):
        result = ''
        pos = self.pos
        while self.current_char is not None and self.current_char != '<':
            result += self.current_char
            self.advance()
        return Token('LITERAL', result, pos)

    def get_next_token(self):

        self.skip_whitespace()
        
        if self.current_char == '<':
            self.advance()
            return self.tag()
        elif self.current_char is not None:
            return self.literal()
        
        print(self.current_char)
        return Token('EOF', 'EOF', self.pos)