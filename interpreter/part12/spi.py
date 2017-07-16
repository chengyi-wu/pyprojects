from spi_lexer import *
from spi_parser import *
from spi_symbol import *
from spi_interpreter import *

def main():
    import sys
    text = open(sys.argv[1], 'r').read()
    lexer = Lexer(text)
    parser = Parser(lexer)
    tree = parser.parse()
    symtab_builder = SymbolTableBuilder()
    symtab_builder.visit(tree)

    print(symtab_builder.symtab)

    interpreter = Interpreter(tree)
    interpreter.interpret()
    print(interpreter.GLOBAL_MEMORY)

if __name__ == '__main__':
    main()