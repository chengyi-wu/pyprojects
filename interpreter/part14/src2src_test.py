from spi_lexer import *
from spi_parser import *
from spi_semantic import *
from src2src import *

source_code = ''
with open('translated.pas', 'r') as f:
    for ln in f:
        source_code += ln

print source_code

l = Lexer(source_code)
p = Parser(l)
tree = p.parse()

analyzer = SemanticAnalyzer(tree)

analyzer.analyze()

#print(analyzer)
rewriter = S2SCompiler(tree)

print rewriter.rewrite()
