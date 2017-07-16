from spi_lexer import *
from spi_parser import *
from spi_semantic import *
from spi_interpreter import *

def main():
    import sys
    text = open(sys.argv[1], 'r').read()
    lexer = Lexer(text)
    parser = Parser(lexer)
    tree = parser.parse()
    analyzer = SemanticAnalyzer(tree)
    analyzer.analyze()

    print(analyzer.symtab)

    interpreter = Interpreter(tree)
    interpreter.interpret()
    print(interpreter.GLOBAL_MEMORY)

if __name__ == '__main__':
    main()