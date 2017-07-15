from spi_lexer import *
from spi_parser import *
from spi_interpreter import *

s = '\
BEGIN\
    begin\
        number := 2;\
        _num := 5;\
        a := number;\
        b := 10 * a + 10 * number DIV 4;\
        c := a - - b\
    END;\
    x := 11;\
END.'
l = Lexer(s)
p = Parser(l)
interpreter = Interpreter(p)
interpreter.interpret()
print(interpreter.GLOBAL_SCOPE)