from html_lexer import *

class HtmlElement(object):
    def __init__(self, name, children=None, attributes=None):
        self.name = name
        self.children = children
        self.attributes = attributes

class HtmlDocument(HtmlElement):
    def __init__(self, name):
        super(HtmlDocument,self).__init__(name)

class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = lexer.get_next_token()

    def match(self, tag):
        if self.current_token.name == tag:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def error(self):
        raise Exception("Invalid Syntax")

    def document(self):
        doc = None
        while self.current_token.name == 'STARTTAG'\
            and self.current_token.value.lower() == 'html':
            doc = HtmlDocument(self.current_token.value)
            
        return doc

    def parse(self):
        return self.document()

    