from spi_lexer import Lexer

s = '\
BEGIN\
    BEGIN\
        number := 2;\
        a := number;\
        b := 10 * a + 10 * number DIV 4;\
        c := a - - b\
    END;\
    x := 11;\
END.'
l = Lexer(s)
t = l.get_next_token()
print t
while t.type != 'EOF':
    t = l.get_next_token()
    print t
