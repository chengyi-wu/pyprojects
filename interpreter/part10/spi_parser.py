from spi_lexer import Lexer, Token

################### PARSER #######################
#            Produce a syntax tree               #
################### PARSER #######################

class AST(object):
    pass

class UnaryOp(AST):
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr

class BinOp(AST):
    def __init__(self, left, op, right):
        self. token = self.op = op
        self.left = left
        self.right = right

class Num(AST):
    def __init__(self, token, value):
        self.token = token
        self.value = value

class Var(Num):
    pass
    
class Assign(BinOp):
    pass

class Compound(AST):
    '''
    Compound statement is a container
    '''
    def __init__(self):
        self.children = []

class NoOp(AST):
    pass

class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = lexer.get_next_token()

    def error(self):
        raise Exception("Invalid Syntax")

    def eat(self, token_type):
        '''
        Consume the current token and get the next token
        '''
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            print("Expected token={expected}, feeding token={feed}".format(expected=self.current_token,feed=token_type))
            self.error()

    def factor(self):
        '''
        factor : PLUS factor | MINUS factor | INTEGER | LPAREN expr RPAREN | variable
        '''
        token = self.current_token

        if token.type == 'PLUS':
            self.eat('PLUS')
            return UnaryOp(token, self.factor())
        elif token.type == 'MINUS':
            self.eat('MINUS')
            return UnaryOp(token, self.factor())
        elif token.type == 'LPAREN':
            self.eat('LPAREN')
            node = self.expr()
            self.eat('RPAREN')
            return node
        elif token.type == 'INTEGER':
            node = Num(token, token.value)
            self.eat('INTEGER')
            return node
        else:
            return self.variable()

    def term(self):
        '''
        term : factor((MUL|DIV)factor)*
        '''
        node = self.factor()
        while self.current_token.type in ('MUL', 'DIV'):
            token = self.current_token
            if token.type == 'MUL':
                self.eat('MUL')
            else:
                self.eat('DIV')
            node = BinOp(node, token, self.factor())
        
        return node

    def expr(self):
        '''
        expr : term((PLUS|MINUS)term)*
        '''
        node = self.term()
        while self.current_token.type in ('PLUS', 'MINUS'):
            token = self.current_token
            if token.type == 'PLUS':
                self.eat('PLUS')
            else:
                self.eat('MINUS')
            node = BinOp(node, token, self.term())
        return node
                
    def variable(self):
        '''
        variable: ID
        '''
        token = self.current_token
        if token.type == 'ID':
            self.eat('ID')
            return Var(token, token.value)
        self.error()

    def empty(self):
        return NoOp()

    def assignment_statement(self):
        '''
        assignment_statement : variable ASSIGN expr
        '''
        node = self.variable()
        token = self.current_token
        if token.type == 'ASSIGN':
            self.eat('ASSIGN')
            return Assign(node, token, self.expr())
        self.error()

    def statement(self):
        """
        statement : compound_statement | assignment_statement | empty???
        """
        token = self.current_token
        if token.type == 'BEGIN':
            node = self.compund_statment()
        elif token.type == 'ID':
            node = self.assignment_statement()
        else:
            node = self.empty()
        return node

    def statement_list(self):
        '''
        statement_list : statement | statement SEMI statement_list
        '''
        node = self.statement()
        results = [node]
        if self.current_token.type == 'SEMI':
            self.eat('SEMI')
            # Should be a statement_list, which is a list
            results.extend(self.statement_list()) 
        
        # Why ??
        if self.current_token.type == 'ID':
            self.error()
        
        return results

    def compund_statment(self):
        '''
        compund_statment : BEGIN statement_list END
        '''
        if self.current_token.type == 'BEGIN':
            self.eat('BEGIN')
            nodes = self.statement_list()
            self.eat('END')
            
            root = Compound()
            for node in nodes:
                root.children.append(node)
            return root

        self.error()

    def program(self):
        '''
        program : compound_staement DOT
        '''
        node = self.compund_statment()
        if self.current_token.type == "DOT":
            self.eat('DOT')
            return node
        self.error()
            
    def parse(self):
        node = self.program()
        if self.current_token.type != 'EOF':
            self.error()
        return node