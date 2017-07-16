from spi_lexer import *

source_code = ''
with open('part12_6.pas', 'r') as f:
    for ln in f:
        source_code += ln

print source_code
    
l = Lexer(source_code)
t = l.get_next_token()
print t
while t.type != 'EOF':
    t = l.get_next_token()
    print t