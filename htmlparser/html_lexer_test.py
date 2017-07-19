from html_lexer import *

f = open('google.html', 'r')
text = f.read()

f.close()

lexer = Lexer(text)

t = lexer.get_next_token()
print t
while t.value != 'EOF':
    t = lexer.get_next_token()
    print t