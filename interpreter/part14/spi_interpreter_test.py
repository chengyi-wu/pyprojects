from spi_lexer import *
from spi_parser import *
from spi_semantic import *
from spi_interpreter import *

source_code = ''
with open('pascal.pas', 'r') as f:
    for ln in f:
        source_code += ln

print source_code

l = Lexer(source_code)
p = Parser(l)
tree = p.parse()
analyzer = SemanticAnalyzer(tree)
analyzer.analyze()

interpreter = Interpreter(tree)
interpreter.interpret()
print(interpreter.GLOBAL_MEMORY)