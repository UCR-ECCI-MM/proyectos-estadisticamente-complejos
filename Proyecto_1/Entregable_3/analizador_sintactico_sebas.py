# LIBRERIAS

import os
import glob
from collections import Counter
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
    'PIPE',
    'NEWLINE'
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

def valida_bits(t):
    if t.value > 4294967295:
        mensaje = (
                f"Error de lexer en linea {t.lineno}: "
                f"Fuera de rango (max 4294967295): {t.value}"
        )
        errores_lexicos.append(mensaje)
        return False

    return True

# TOKEN TIMESTAMP

def t_TIMESTAMP(t):
    r'\d{10}'
    t.value = int(t.value)

    valida_bits(t)

    return t

# TOKEN AS_NUMBER

def t_AS_NUMBER(t):
    r'\d{1,10}'
    t.value = int(t.value)

    valida_bits(t)

    return t

# SALTOS DE LINEA
def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    return t

# ERRORES LEXICOS

errores_lexicos = []

def t_error(t):
    mensaje = (
        f"Error léxico en línea {t.lineno}, "
        f"posición {t.lexpos}: "
        f"carácter inesperado '{t.value[0]}'"
    )

    errores_lexicos.append(mensaje)

    t.lexer.skip(1)


lexer = lex.lex()

# REGLAS PARSER

errores_sintacticos = []

def p_archivo(t):
    'archivo : lista_lineas'
    pass


def p_lista_lineas_multiple(t):
    'lista_lineas : linea NEWLINE lista_lineas'
    pass


def p_lista_lineas_una(t):
    'lista_lineas : linea'
    pass


def p_linea(t):
    'linea : TABLE_DUMP2 PIPE TIMESTAMP PIPE STATE PIPE IP PIPE AS_NUMBER PIPE PREFIX PIPE as_path'
    pass


def p_as_path_number(t):
    'as_path : AS_NUMBER lista_as'
    pass


def p_as_path_timestamp(t):
    'as_path : TIMESTAMP lista_as'
    pass


def p_lista_as_number(t):
    'lista_as : AS_NUMBER lista_as'
    pass


def p_lista_as_timestamp(t):
    'lista_as : TIMESTAMP lista_as'
    pass


def p_lista_as_vacia(t):
    'lista_as :'
    pass


def p_error(t):

    if t:
        mensaje = (
            f"Error sintáctico en línea {t.lineno}: "
            f"token inesperado '{t.value}' "
            f"({t.type})"
        )

        errores_sintacticos.append(mensaje)

        # Intentamos continuar para encontrar más errores
        parser.errok()

    else:
        mensaje = "Error sintáctico: fin de archivo inesperado"
        errores_sintacticos.append(mensaje)


parser = yacc.yacc()

# ANALIZAR UN ARCHIVO

def analizar_archivo(ruta):

    global errores_lexicos
    global errores_sintacticos

    errores_lexicos = []
    errores_sintacticos = []

    print("\n" + "=" * 70)
    print(f"Analizando: {os.path.basename(ruta)}")
    print("=" * 70)

    # Reiniciar número de línea
    lexer.lineno = 1

    # Leer archivo
    with open(ruta, 'r', encoding='utf-8') as archivo:
        contenido = archivo.read()

    # 1. ANÁLISIS LÉXICO

    lexer.input(contenido)

    tokens_encontrados = []

    while True:

        tok = lexer.token()

        if not tok:
            break

        tokens_encontrados.append(tok)

    if errores_lexicos:

        print("\nERRORES LÉXICOS:")

        for error in errores_lexicos:
            print("  -", error)

    else:
        print("\nAnálisis léxico correcto")

    # 2. ANÁLISIS SINTÁCTICO

    if not errores_lexicos:

        lexer.lineno = 1

        parser.parse(
            contenido,
            lexer=lexer
        )

        if errores_sintacticos:

            print("\nERRORES SINTÁCTICOS:")

            for error in errores_sintacticos:
                print("  -", error)

        else:
            print("Análisis sintáctico correcto")

    else:

        print(
            "\nNo se ejecutó el análisis sintáctico "
            "porque existen errores léxicos."
        )

    # RESULTADO

    if not errores_lexicos and not errores_sintacticos:

        print("\nRESULTADO: ARCHIVO VÁLIDO")

    else:

        print("\nRESULTADO: ARCHIVO CON ERRORES")


# PROCESAR LOS CHUNKS

def main():

    carpeta = '''Proyecto_1\Datos\Chunks'''

    archivos = [
        os.path.join(carpeta, "chunk_aa.txt"),
        os.path.join(carpeta, "chunk_ab.txt"),
        os.path.join(carpeta, "chunk_ac.txt"),
        os.path.join(carpeta, "chunk_ad.txt"),
        os.path.join(carpeta, "chunk_ae.txt")
    ]

    for archivo in archivos:

        if os.path.exists(archivo):

            analizar_archivo(archivo)

        else:

            print(
                f"\nNo se encontró el archivo: {archivo}"
            )


# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":
    main()
