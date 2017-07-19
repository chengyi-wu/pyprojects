from html_lexer import *

f = open('baidu.html', 'r')
text = f.read()

f.close()

lexer = Lexer(text)

t = lexer.get_next_token()
print t
while t.value != 'EOF':
    t = lexer.get_next_token()
    print t