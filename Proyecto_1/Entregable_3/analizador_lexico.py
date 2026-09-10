
# LIBRERIAS


import os
import glob
import ply.lex as lex
import ply.yacc as yacc


# TOKENS

tokens = (
    'TABLE_DUMP2',
    'STATE',
    'TIMESTAMP',
    'IP',
    'PREFIX',
    'AS_NUMBER',
    'PIPE'
)

# EXPRESIONES REGULARES

t_TABLE_DUMP2 = r'TABLE_DUMP2'
t_PIPE = r'\|'
t_STATE = r'[BAW]{1}'
t_ignore = ' \t(),{}'

# IP Y PREFIX
#Cada octeto va de 0 225 y son 4 octetos los que llevan una IP
# Una ip esta conformada por 4 octetos separados por puntos, esto se hace aca
OCTET = r'(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])(?![0-9])'
IP_REGEX = (
    OCTET + r'\.' +
    OCTET + r'\.' +
    OCTET + r'\.' +
    OCTET
)

# La mascara puede ir de 0 a 32 y se separa con / del IP
MASK = r'(?:3[0-2]|[12][0-9]|[0-9])(?![0-9])'
PREFIX_REGEX = IP_REGEX + r'/' + MASK

# PREFIJO
#  IP + / + longitud de mascara = PREFIX
@lex.TOKEN(PREFIX_REGEX)
def t_PREFIX(t):
    return t

# PEER IP
@lex.TOKEN(IP_REGEX)
def t_IP(t):
    return t

# Funcion que valida rango de tokens NUMBER y TIMESTAMP

def valida_bits(num):
    if num > 4294967295:
        print(
                f"Error de lexer en linea {num.lineno}: "
                f"Fuera de rango (max 4294967295): {num.value}"
        )
        return None

# TOKEN TIMESTAMP

def t_TIMESTAMP(t):
    r'\d{10}(?![0-9])'
    t.value = int(t.value)

    valida_bits(t.value)

    return t

# TOKEN AS_NUMBER

def t_AS_NUMBER(t):
    r'\d{1,10}(?![0-9])'
    t.value = int(t.value)

    valida_bits(t.value)

    return t

# ERRORES LEXICOS

errores = []
linea_actual = ""

def t_error(t):
    errores.append(
        f"Linea {t.lexer.lineno}: "
        f"caracter no reconocido '{t.value[0]}' "
        f"| Contenido: {linea_actual.rstrip(chr(10))}"
    )
    t.lexer.skip(1)


# CREAR LEXER
lexer = lex.lex()

# CARPETAS

# Ruta relativa a la ubicacion de este script, no al usuario/PC actual,
# para que funcione igual en la maquina de cualquier integrante del equipo.
carpeta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
carpeta_chunks = os.path.join(carpeta_proyecto, "Datos", "Chunks")

# BUSCAR TODOS LOS CHUNKS

archivos = sorted(
    glob.glob(
        os.path.join(
            carpeta_chunks,
            "chunk_*.txt"
        )
    )
)

if not archivos:

    print("No se encontraron archivos chunk_*.txt")

    raise SystemExit

# PROCESAR TODOS LOS CHUNKS

todos_los_tokens = []

try:

    for ruta in archivos:

        errores.clear()

        lexer.lineno = 1

        with open(
            ruta,
            "r",
            encoding="utf-8"
        ) as archivo:

            for numero_linea, linea in enumerate(
                archivo,
                start=1
            ):

                lexer.lineno = numero_linea

                linea_actual = linea

                lexer.input(linea)

                while True:

                    token = lexer.token()

                    if token is None:
                        break

                    todos_los_tokens.append(token)

except Exception as e:

    print(f"Error leyendo archivos de entrada: {e}")

    raise SystemExit

print(f"Archivos leidos con exito: {len(archivos)}")


# PARSER

def p_ruta_bgp(p):
    'linea : TABLE_DUMP2 PIPE TIMESTAMP PIPE STATE PIPE IP PIPE AS_NUMBER PIPE PREFIX PIPE as_path'
    print("OK: linea reconocida")
def p_as_path(p):
    '''as_path : AS_NUMBER lista_as 
                | TIMESTAMP lista_as'''

def p_listas_as(p):
    '''lista_as : AS_NUMBER lista_as 
                | TIMESTAMP lista_as 
                | '''

def p_error(p):
    if p:
        print("Error sintactico, linea %d: no esperaba %r" % (p.lineno, p.value))
    else:
        print("Error sintactico: la entrada termino antes de tiempo")

import ply.yacc as yacc

def procesar_archivos():

    carpeta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    carpeta_chunks = os.path.join(carpeta_proyecto, "Datos", "Chunks")

    archivos = sorted(glob.glob(os.path.join(carpeta_chunks, "chunk_*.txt")))

    if not archivos:
        print("No se encontraron archivos chunk_*.txt")
        return

    # ... el resto del bloque, ya indentado ...

    print(f"Archivos leidos con exito: {len(archivos)}")
parser = yacc.yacc()
parser = yacc.yacc()

pruebas = [
    "TABLE_DUMP2|1785888000|B|200.40.162.202|6057|0.0.0.0/0|6057 12956",
    "TABLE_DUMP2|1785888000|B|177.221.140.2|270014|0.0.0.0/0|270014",
    "TABLE_DUMP2|1785888000|B|200.40.162.202|6057|0.0.0.0/0",
    "TABLE_DUMP2|1785888000|X|200.40.162.202|6057|0.0.0.0/0|6057",
    "TABLE_DUMP2|1785888000|B|200.40.162.202|0.0.0.0/0|6057|6057",
]

for texto in pruebas:
    print("\n>>>", texto)
    lexer.lineno = 1
    parser.parse(texto, lexer=lexer)

linea = "TABLE_DUMP2|1785888000|B|200.40.162.202|6057|0.0.0.0/0|6057 12956"
parser.parse(linea, lexer=lexer)