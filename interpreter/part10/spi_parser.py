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
    def __str__(self):
        return "{left} {op} {right}".format(left=self.left,op=self.op,right=self.right)

class Num(AST):
    def __init__(self, token, value):
        self.token = token
        self.value = value
    def __str__(self):
        return repr(self.value)

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

class Program(AST):
    def __init__(self, name, block):
        self.name = name
        self.block = block

class Block(AST):
    def __init__(self, declarations, compound_statement):
        self.declarations = declarations
        self.compound_statement = compound_statement

class VarDecl(AST):
    '''
    Holds a variable node + type node
    '''
    def __init__(self, var_node, var_type):
        self.var_node = var_node
        self.var_type = var_type
    def __str__(self):
        return "{type} {node}".format(type=self.var_type, node=self.var_node) 

class Type(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value
    def __str__(self):
        return repr(self.value)

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
            print("Expected token={expected}, feeding token={feed}".format(expected=token_type,feed=self.current_token))
            self.error()

    def factor(self):
        '''
        factor : PLUS factor | MINUS factor | INTEGER_CONST | REAL_CONST | LPAREN expr RPAREN | variable
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
        elif token.type == 'INTEGER_CONST':
            node = Num(token, token.value)
            self.eat('INTEGER_CONST')
            return node
        elif token.type == 'REAL_CONST':
            node = Num(token, token.value)
            self.eat('REAL_CONST')
            return node
        else:
            return self.variable()

    def term(self):
        '''
        term : factor((MUL | INTEGER_DIV | FLOAT_DIV) factor)*
        '''
        node = self.factor()
        while self.current_token.type in ('MUL', 'INTEGER_DIV', 'FLOAT_DIV'):
            token = self.current_token
            if token.type == 'MUL':
                self.eat('MUL')
            elif token.type == 'INTEGER_DIV':
                self.eat('INTEGER_DIV')
            elif token.type == 'FLOAT_DIV':
                self.eat('FLOAT_DIV')
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
            node = self.compound_statement()
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

    def compound_statement(self):
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
        program : PROGRAM variable SEMI block DOT
        '''
        self.eat('PROGRAM')
        var = self.variable()
        self.eat("SEMI")
        block = self.block()
        self.eat('DOT')
        return Program(var, block)

    def block(self):
        declarations = self.declarations()
        compound_statement = self.compound_statement()
        return Block(declarations, compound_statement)

    def declarations(self):
        if self.current_token.type == 'VAR':
            self.eat('VAR')
            var_nodes = []
            while self.current_token.type != 'BEGIN':
                var_nodes.extend(self.variable_declaration())
                self.eat('SEMI')
            return var_nodes

    def variable_declaration(self):
        if self.current_token.type == 'ID':
            token = self.current_token
            self.eat('ID')
            var_nodes = [token]
            while self.current_token.type == 'COMMA':
                self.eat('COMMA')
                token = self.current_token
                self.eat('ID')
                var_nodes.append(token)
            self.eat('COLON')
            var_type = self.type_spec()
            vars = []
            for n in var_nodes:
                vars.append(VarDecl(n, var_type))
            return vars
        

    def type_spec(self):
        token = self.current_token
        if token.type == 'INTEGER':
            self.eat('INTEGER')
        elif token.type == 'REAL':
            self.eat('REAL')
        else:
            self.error()
        return Type(token)
 
    def parse(self):
        node = self.program()
        if self.current_token.type != 'EOF':
            self.error()
        return node