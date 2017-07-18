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

    interpreter = Interpreter(tree)
    interpreter.interpret()
    print('\nGLOBAL MEMORY')
    for k, v in interpreter.GLOBAL_MEMORY.items():
        print('%7s = %s' % (k,v))

if __name__ == '__main__':
    main()