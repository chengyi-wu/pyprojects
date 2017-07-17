from NodeVisitor import *
from spi_semantic import *
class S2SCompiler(NodeVisitor):
    def __init__(self, tree):
        self.tree = tree
        self.current_level = 0
        self.current_inden = 0

    def visit_Program(self, node):
        self.current_level += 1
        self.current_inden += 4
        print("PROGRAM {name}{level}".format(name=node.name.value,level=self.current_level))
        print("BEGIN")
        self.visit(node.block)
        print("END")

    def visit_ProcedureDecl(self, node):
        s = "{inden}PROCEDURE {name}{level}".format(
            inden=self.current_inden,
            name=node.name,
            level=self.current_level
        )
        
        self.current_level += 1
        if node.params is not None:
            for p in node.params:
                s += self.visit(p)
        s += '\nBEGIN'
        print(s)
        self.current_inden += 4

        self.visit(node.block)

        self.current_inden -= 4

        self.current_level -= 1

    def visit_Block(self, node):
        for decl in node.declarations:
            self.visit(decl)
        print('{inden}BEGIN'.format(inden=' ' * self.current_inden))
        self.current_inden += 4
        self.visit(node.compound_statement)
        self.current_inden -= 4
        print('{inden}END'.format(inden=' ' * self.current_inden))

    def visit_VarDecl(self, node):
        print("{inden}VAR {var}{level} : {type}".format(
            inden=' ' * self.current_inden,
            var=node.var_node.value,
            type=node.type_node.value,
            level=self.current_level)
        )

    def visit_Compound(self, node):
        for n in node.children:
            self.visit(n)

    def visit_Assign(self, node):
        print("{inden}{left} {op} {right}".format(
            inden=' ' * self.current_inden,
            left=self.visit(node.left),
            op=node.op.value,
            right=self.visit(node.right)))

    def visit_Var(self, node):
        return "{name}{level}".format(name=node.value,level=self.current_level)

    def visit_Num(self, node):
        return node.value

    def visit_BinOp(self, node):
        return("{left} {op} {right}".format(
            left=self.visit(node.left),
            op=node.op.value,
            right=self.visit(node.right)))

    def visit_UnaryOp(self, node):
        return "{op} {right}".format(
            op=node.op.value,
            right=self.visit(node.expr))

    def visit_NoOp(self, node):
        pass

    def rewrite(self):
        self.visit(self.tree)