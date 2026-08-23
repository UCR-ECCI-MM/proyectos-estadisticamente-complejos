import ply.lex as lex

tokens = (
    'RECORDID',
    'TIMESTAMP',
    'STATE',
    'IP',
    'AS',
    'LINE',
    'NEWLINE',
    'ASPATH',
    'SPACE'
)

t_STATE    = r'[A|B|W]{1}'
t_LINE   = r'\|'
t_SPACE = r'\s'
t_ASPATH = r'\d{1,10}(\s+\d{1,10})*'
t_ignore  = ' \t'

def t_AS(t):
    r'\d{1,10}'
    t.value = int(t.value)

    if t.value < 1 or t.value >= 2**32:
        print(f"Error: ASN fuera de rango: {t.value}")
        return None

    return t
 
def t_error(t):
     print("Illegal character '%s'" % t.value[0])
     t.lexer.skip(1)
 
lexer = lex.lex()

with open("Proyecto_1/datos/chunk_aa_muestra.txt", "r", encoding="utf-8") as archivo:
    data = archivo.read()

lexer.input(data)
 
# Tokenize
while True:
     tok = lexer.token()
     if not tok: 
         break
     print(tok)