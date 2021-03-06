from spi_lexer import *
from spi_parser import *
from spi_symbol import *

source_code = ''
with open('part11.pas', 'r') as f:
    for ln in f:
        source_code += ln

#print source_code

l = Lexer(source_code)
p = Parser(l)
tree = p.parse()

symtab_builder = SymbolTableBuilder()

symtab_builder.visit(tree)