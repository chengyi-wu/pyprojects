from spi_lexer import *
from spi_parser import *
from spi_symbol import *
from NodeVisitor import *
from collections import OrderedDict

class Interpreter(NodeVisitor):
    def __init__(self, tree):
        # changed the parser to AST tree root
        self.tree = tree
        self.GLOBAL_MEMORY = OrderedDict()

    def visit_BinOp(self, node):
        if node.op.type == 'PLUS':
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == 'MINUS':
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == 'MUL':
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == 'INTEGER_DIV':
            return self.visit(node.left) // self.visit(node.right)
        elif node.op.type == 'FLOAT_DIV':
            return float(self.visit(node.left)) / float(self.visit(node.right))

    def visit_UnaryOp(self, node):
        if node.op.type == 'PLUS':
            return +self.visit(node.expr)
        elif node.op.type == 'MINUS':
            return -self.visit(node.expr)

    def visit_Num(self, node):
        return node.value

    def visit_Compound(self, node):
        for child in node.children:
            self.visit(child)

    def visit_NoOp(self, node):
        pass

    def visit_Assign(self, node):
        var_name = node.left.value
        self.GLOBAL_MEMORY[var_name] = self.visit(node.right)

    def visit_Var(self, node):
        var_name = node.value
        val = self.GLOBAL_MEMORY.get(var_name)
        return val

    def visit_Program(self, node):
        # Register the program name?
        self.visit(node.block)
    
    def visit_Block(self, node):
        for decl in node.declarations:
            self.visit(decl)
        
        self.visit(node.compound_statement)

    def visit_VarDecl(self, node):
        # Register in Symbol table for the variable
        node.var_node
        self.visit(node.type_node)

    def visit_Type(self, node):
        return node.value

    def interpret(self):
        self.visit(self.tree)