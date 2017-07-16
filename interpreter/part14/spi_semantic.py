from collections import OrderedDict
from NodeVisitor import *

class Symbol(object):
    def __init__(self, name, type=None):
        self.name = name
        self.type = type
    
class BuiltinTypeSymbol(Symbol):
    def __init__(self, name):
        super(BuiltinTypeSymbol, self).__init__(name)

    def __str__(self):
        return '<{class_name}(name={name})>'.format(
            class_name=self.__class__.__name__,
            name=self.name
        )

    __repr__ = __str__

class VarSymbol(Symbol):
    def __init__(self, name, type):
        super(VarSymbol, self).__init__(name, type)

    def __str__(self):
        return '<{class_name}(name={name}, type={type})>'.format(
            class_name=self.__class__.__name__,
            name=self.name, 
            type=self.type.name
        )

    __repr__ = __str__

class ScopedSymbolTable(object):
    def __init__(self, scope_name, scope_level):
        self.scope_name = scope_name
        self.scope_level = scope_level
        self._symbols = OrderedDict()
        self.init_builtins()
    
    def init_builtins(self):
        self.define(BuiltinTypeSymbol('INTEGER'))
        self.define(BuiltinTypeSymbol('REAL'))

    def __str__(self):
        h1 = 'SCOPE (SCOPED SYMBOL TABLE)'
        lines = ['\n', h1, '=' * len(h1)]
        for header_name, header_value in (
            ('Scope name', self.scope_name),
            ('Scope level', self.scope_level)
        ):lines.append("%-15s: %s" % (header_name, header_value))
        h2 = 'Scope (scoped symbol table) contents'
        lines.extend([h2, '-' * len(h2)])
        lines.extend(
            ('%7s: %r') % (key, value) for key, value in self._symbols.items()
        )
        lines.append('\n')
        #s = 'Symbols: {symbols}'.format(symbols=self._symbols.values())
        s = '\n'.join(lines)
        return s

    __repr__ = __str__

    def define(self, symbol):
        print("define: %s" % symbol)
        self._symbols[symbol.name] = symbol

    def lookup(self, name):
        print("lookup: %s" % name)
        symbol = self._symbols.get(name)
        # symbol is either a symbol or None
        return symbol

class SemanticAnalyzer(NodeVisitor):
    def __init__(self, root):
        #self.symtab = SymbolTable()
        self.scope = ScopedSymbolTable(scope_name='global', scope_level=1)
        self.root = root

    def analyze(self):
        self.visit(self.root)

    def visit_Block(self, node):
        for decl in node.declarations:
            self.visit(decl)
        self.visit(node.compound_statement)

    def visit_Program(self, node):
        self.visit(node.block)

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visit_Num(self, node):
        pass
    
    def visit_UnaryOp(self, node):
        self.visit(node.expr)

    def visit_Compound(self, node):
        for stmt in node.children:
            self.visit(stmt)

    def visit_NoOp(self, node):
        pass

    def visit_VarDecl(self, node):
        type_name = node.type_node.value
        type_symbol = self.scope.lookup(type_name)
        var_name = node.var_node.value
        # throw an error if symtab has already the same 
        # varible defined
        # if self.symtab.lookup(var_name) is not None:
        #     raise Exception(
        #         "Error: Duplicate identifier '%s' found" % var_name
        #     )
        var_symbol = VarSymbol(var_name, type_symbol)
        self.scope.define(var_symbol)

    def visit_Assign(self, node):
        var_name = node.left.value
        var_symbol = self.scope.lookup(var_name)
        if var_symbol is None:
            raise NameError(repr(var_name))

        self.visit(node.right)

    def visit_Var(self, node):
        var_name = node.value

        if self.scope.lookup(var_name) is None:
            raise NameError(repr(var_name))

    def visit_ProcedureDecl(self, node):
        pass