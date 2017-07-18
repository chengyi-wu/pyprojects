from NodeVisitor import *
from spi_semantic import *
class S2SCompiler(NodeVisitor):
    def __init__(self, tree):
        self.tree = tree
        self.current_scope = None
        self.current_inden = 0 # indentation level, 4 spaces
        self.init_biltinSymbolTable()

    def init_biltinSymbolTable(self):
        self.current_scope = ScopedSymbolTable(
            scope_name='builtin',
            scope_level=0
        )
        self.current_scope.define(BuiltinTypeSymbol('INTEGER'))
        self.current_scope.define(BuiltinTypeSymbol('REAL'))

    def lookup(self, scope, symbol):
        '''
        Return the symbol and it's scope
        '''
        if scope is None:
            return None

        if scope._symbols.get(symbol) is None:
            return self.lookup(scope.enclosing_scope, symbol)
        return scope.scope_level, scope._symbols.get(symbol)

    def visit_Program(self, node):
        s = "PROGRAM {name};".format(name=node.name.value,)
        self.current_scope = ScopedSymbolTable(
            scope_name=node.name.value,
            scope_level=self.current_scope.scope_level + 1,
            enclosing_scope=self.current_scope
        )
        s += self.visit(node.block)
        s += "."
        return s

    def visit_ProcedureDecl(self, node):
        self.current_inden += 4
        s = "\n{inden}PROCEDURE {name}{scope_level}".format(
            inden=' ' * self.current_inden,
            name=node.name.value,
            scope_level=self.current_scope.scope_level
        )

        self.current_scope.define(ProcedureSymbol(node.name))

        self.current_scope = ScopedSymbolTable(
            scope_name=node.name,
            scope_level=self.current_scope.scope_level + 1,
            enclosing_scope=self.current_scope
        )
        
        if node.params is not None:
            s += '('
            for p in node.params:
                s += self.visit(p)
            s += ');'
        
        s += self.visit(node.block)
        self.current_inden -= 4
        return s

    def visit_Param(self, node):
        self.current_scope.define(VarSymbol(node.var_node.value, node.type_node.value))
        return '{name}{scope_level} : {type}'.format(
            name=node.param_name.value, 
            scope_level=self.current_scope.scope_level,
            type=node.param_type.value
        )

    def visit_Block(self, node):
        s = ''
        for decl in node.declarations:
            s += self.visit(decl)

        s += self.visit(node.compound_statement)
        return s


    def visit_VarDecl(self, node):
        
        var_name = node.var_node.value

        level, type_sym = self.lookup(self.current_scope, node.type_node.value)

        if type_sym is None:
            raise NameError(node.type_node.value)
            
        self.current_scope.define(VarSymbol(var_name, type_sym))

        return "\n{inden}VAR {var}{scope_level} : {type};".format(
            inden=' ' * self.current_inden,
            var=node.var_node.value,
            type=self.visit(node.type_node),
            scope_level=self.current_scope.scope_level
        )

    def visit_Compound(self, node):
        s = '\n{inden}BEGIN'.format(inden=' ' * self.current_inden)
        self.current_inden += 4
        for n in node.children:
            s += self.visit(n) + ';'
        s = s[:-1]
        self.current_inden -= 4
        s += '\n{inden}END {{ END OF {scope_name}}}'.format(
            inden=' ' * self.current_inden,
            scope_name=self.current_scope.scope_name
        )
        return s


    def visit_Assign(self, node):
        if self.current_scope.lookup(node.left.value) is None:
            raise NameError(node.left.value)
        return "\n{inden}{left} {op} {right}".format(
            inden=' ' * self.current_inden,
            left=self.visit(node.left),
            op=node.op.value,
            right=self.visit(node.right))

    def visit_Var(self, node):
        '''
        <var_name_with_subscript:type>
        '''
        level, var_type = self.lookup(self.current_scope, node.value)
        
        if var_type is None:
            raise Exception(node.value)
        return "<{name}{scope_level}:{type}>".format(
            name=node.value,
            scope_level=level,
            type=var_type.type.name
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
        