from NodeVisitor import *
from spi_semantic import *
class S2SCompiler(NodeVisitor):
    def __init__(self, tree):
        self.tree = tree
        self.current_level = 0 # scope level
        self.current_inden = 0 # indentation level, 4 spaces

    def visit_Program(self, node):
        s = "PROGRAM {name};".format(name=node.name.value,)
        self.current_level += 1
        s += self.visit(node.block)
        s += "."
        return s

    def visit_ProcedureDecl(self, node):
        self.current_inden += 4
        s = "\n{inden}PROCEDURE {name}".format(
            inden=' ' * self.current_inden,
            name=node.name.value,
            #level=self.current_level
        )
        
        self.current_level += 1
        if node.params is not None:
            s += '('
            for p in node.params:
                s += self.visit(p)
            s += ');'
        
        s += self.visit(node.block)
        self.current_inden -= 4
        self.current_level -= 1
        return s

    def visit_Param(self, node):
        return '{name} : {type}'.format(
            name=node.param_name.value, 
            #level=self.current_level, 
            type=node.param_type.value
        )

    def visit_Block(self, node):
        s = ''
        for decl in node.declarations:
            s += self.visit(decl)

        s += self.visit(node.compound_statement)
        return s


    def visit_VarDecl(self, node):
        return "\n{inden}VAR {var} : {type};".format(
            inden=' ' * self.current_inden,
            var=node.var_node.value,
            type=self.visit(node.type_node),
            #level=self.current_level
        )

    def visit_Compound(self, node):
        s = '\n{inden}BEGIN'.format(inden=' ' * self.current_inden)
        self.current_inden += 4
        for n in node.children:
            s += self.visit(n) + ';'
        s = s[:-1]
        self.current_inden -= 4
        s += '\n{inden}END'.format(inden=' ' * self.current_inden)
        return s


    def visit_Assign(self, node):
        return "\n{inden}{left} {op} {right}".format(
            inden=' ' * self.current_inden,
            left=self.visit(node.left),
            op=node.op.value,
            right=self.visit(node.right))

    def visit_Var(self, node):
        return "{name}".format(
            name=node.value,
            #level=self.current_level
        )

    def visit_Num(self, node):
        return node.value

    def visit_Type(self, node):
        return node.value

    def visit_BinOp(self, node):
        return "{left} {op} {right}".format(
            left=self.visit(node.left),
            op=node.op.value,
            right=self.visit(node.right))

    def visit_UnaryOp(self, node):
        return "{op} {right}".format(
            op=node.op.value,
            right=self.visit(node.expr))

    def visit_NoOp(self, node):
        return ''

    def rewrite(self):
        return self.visit(self.tree)
        