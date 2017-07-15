# Token types
#
# EOF token is used to indicate that there's no more 
# input for lexical analysis

INTEGER, PLUS, MINUS, MUL, DIV, LPARENT, RPARENT, EOF \
= 'INTEGER', 'PLUS', 'MINUS','MUL', 'DIV', 'LPARENT', 'RPARENT', 'EOF'

class Token(object):
    def __init__(self, type, value):
        # token type: INTEGER, MUL, DIV, or EOF
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

class Lexer(object):
    '''
    Lexical analysis: the process of breaking the input string into tokens.
    '''
    def __init__(self, text):
        # client string input, e.g. "3 * 5", "12 / 3 * 4", etc
        self.text = text
        # self.pos is an index into self.ttext
        self.pos = 0
        # current token instance
        self.current_token = None
        self.current_char = self.text[self.pos]

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
        # terminals
        operators = { '+':PLUS, '-':MINUS, '*':MUL, '/':DIV, '(':LPARENT, ')':RPARENT }

        while self.current_char is not None:
            
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return Token(INTEGER, self.integer())

            if self.current_char in operators:
                op = self.current_char
                self.advance()
                return Token(operators[op], op)
            
            self.error()

        return Token(EOF, None)

##########################################################################
#                                                                        #
#   Parser                                                               #
#                                                                        #
##########################################################################

# base class
class AST(object):
    pass

class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        # set current token to the first token taken from the input
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception("Invalid syntax")

    def eat(self, token_type):
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else: # Invalid syntax
            self.error()

    def factor(self):
        '''
        factor : INTEGER | LPARENT expr RPARENT
        '''
        token = self.current_token
        if token.type == INTEGER:
            self.eat(INTEGER)
            return Num(token)
        elif token.type == LPARENT:
            self.eat(LPARENT)
            node = self.expr()
            self.eat(RPARENT)
            return node

    def term(self):
        '''
        term : factor ((MUL|DIV) factor)*
        '''
        node = self.factor()
        while self.current_token.type in (MUL, DIV):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
            elif token.type == DIV:
                self.eat(DIV)
            node = BinOp(node, token, self.factor())
        return node

    def expr(self):
        '''
        Parser / Interpreter

        expr : term ((PLUS|MINUS) term)*
        '''
        node = self.term()

        while self.current_token.type in (PLUS, MINUS):
            # we expect the current token to be a '+' token
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
            elif token.type == MINUS:
                self.eat(MINUS)
            node = BinOp(node, token, self.term())
        
        return node
    
    def parse(self):
        return self.expr()

##########################################################################
#                                                                        #
#   Interpreter                                                          #
#                                                                        #
##########################################################################

# Visitor pattern
class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))

class Interpreter(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser
    
    def visit_BinOp(self, node):
        if node.op.type == PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == DIV:
            return self.visit(node.left) / self.visit(node.right)

    def visit_Num(self, node):
        return node.value

    def interpret(self):
        tree = self.parser.parse()
        return self.visit(tree)
    

def main():
    while True:
        try:
            text = raw_input('calc> ')
        except EOFError:
            break
        if not text:
            continue
        lexer = Lexer(text)
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        print(interpreter.interpret())

if __name__ == '__main__':
    main()
