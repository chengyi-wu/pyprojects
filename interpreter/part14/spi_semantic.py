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

class ProcedureSymbol(Symbol):
    def __init__(self, name, params=None):
        super(ProcedureSymbol, self).__init__(name)
        self.params = params if params is not None else []

    def __str__(self):
        return '<{class_name}(name={name}, parameters={params})>'.format(
            class_name=self.__class__.__name__,
            name=self.name,
            params=self.params
            )
    
    __repr__ = __str__

class ScopedSymbolTable(object):
    def __init__(self, scope_name, scope_level, enclosing_scope=None):
        self.scope_name = scope_name
        self.scope_level = scope_level
        self._symbols = OrderedDict()
        # parent pointer to the higher scope
        self.enclosing_scope = enclosing_scope
        #self.init_builtins()
    
    # def init_builtins(self):
    #     self.define(BuiltinTypeSymbol('INTEGER'))
    #     self.define(BuiltinTypeSymbol('REAL'))

    def __str__(self):
        h1 = 'SCOPE (SCOPED SYMBOL TABLE)'
        lines = ['\n', h1, '=' * len(h1)]
        for header_name, header_value in (
            ('Scope name', self.scope_name),
            ('Scope level', self.scope_level),
            ('Enclosing scope', self.enclosing_scope),
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

    def lookup(self, name, current_scope_only=False):
        '''
        Most closely nested scope.
        '''
        print("lookup: %s (Scope name=%s)" % (name,self.scope_name))
        symbol = self._symbols.get(name)
        
        if symbol is not None:
            return symbol
        
        if not current_scope_only and self.enclosing_scope is not None:
            return self.enclosing_scope.lookup(name)
        return symbol

class SemanticAnalyzer(NodeVisitor):
    def __init__(self, root):
        #self.symtab = SymbolTable()
        #self.scope = ScopedSymbolTable(scope_name='global', scope_level=1)
        self.current_scope = None
        self.root = root
        # adding scope for built-in types
        self.init_BuiltinTypes()

    def init_BuiltinTypes(self):
        self.current_scope = ScopedSymbolTable(
            scope_name='builtin',
            scope_level=0
        )
        self.current_scope.define(BuiltinTypeSymbol('INTEGER'))
        self.current_scope.define(BuiltinTypeSymbol('REAL'))

    def analyze(self):
        self.visit(self.root)

    def visit_Block(self, node):
        for decl in node.declarations:
            self.visit(decl)
        self.visit(node.compound_statement)

    def visit_Program(self, node):
        '''
        Program creates a scope of symbols
        '''
        print('ENTER scope:global')
        global_scope = ScopedSymbolTable(
            scope_name=node.name,
            scope_level=1,
            enclosing_scope=self.current_scope, #self.current_scope = None
        )
        self.current_scope = global_scope
        self.visit(node.block)
        print(global_scope)
        print('LEAVE scope:global')

    def visit_ProcedureDecl(self, node):
        '''
        Procedure creates another scope.
        1. Create a ProcedureSymbol, define it in the current_scope
        2. Create a new symbol scope
        3. Define all the formal parameters in the procedure scope
        '''
        proc_name = node.name.value
        proc_symbol = ProcedureSymbol(proc_name)
        self.current_scope.define(proc_symbol)

        print('ENTER scope: %s' % proc_name)
        # Scope for parameters and local vaiables
        procedure_scope = ScopedSymbolTable(
            scope_name=proc_name,
            scope_level=self.current_scope.scope_level + 1,
            enclosing_scope=self.current_scope
        )
        self.current_scope = procedure_scope

        for param in node.params:
            param_type = self.current_scope.lookup(param.param_type.value)
            param_name = param.param_name.value
            var_symbol = VarSymbol(param_name, param_type)
            self.current_scope.define(var_symbol)
            proc_symbol.params.append(var_symbol) # Why?? Appears not needed

        self.visit(node.block)

        print(procedure_scope)
        print('LEAVE scope: %s' % proc_name)

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
        type_symbol = self.current_scope.lookup(type_name)
        var_name = node.var_node.value
        
        if self.current_scope.lookup(var_name, current_scope_only=True) is not None:
            raise Exception(
                "Error: Duplicate identifier '%s' found" % var_name
            )
        var_symbol = VarSymbol(var_name, type_symbol)
        self.current_scope.define(var_symbol)

    def visit_Assign(self, node):
        var_name = node.left.value
        var_symbol = self.current_scope.lookup(var_name)
        if var_symbol is None:
            raise NameError(repr(var_name))

        self.visit(node.right)

    def visit_Var(self, node):
        var_name = node.value

        if self.current_scope.lookup(var_name) is None:
            raise NameError(repr(var_name))