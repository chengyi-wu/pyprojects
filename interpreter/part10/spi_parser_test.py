from spi_lexer import Lexer
from spi_parser import Parser

s = '\
BEGIN\
    BEGIN\
        number := 2;\
        a := number;\
        b := 10 * a + 10 * number / 4;\
        c := a - - b\
    END;\
    x := 11;\
END.'
l = Lexer(s)
p = Parser(l)
root = p.parse()

for n in root.children:
    print n