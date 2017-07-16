from spi_lexer import Lexer
from spi_parser import Parser

source_code = ''
with open('part10.pas', 'r') as f:
    for ln in f:
        source_code += ln

print source_code
    
l = Lexer(source_code)
p = Parser(l)
program = p.parse()

print program.name

block = program.block

for d in block.declarations:
    print d

for n in block.compound_statement.children:
    print n