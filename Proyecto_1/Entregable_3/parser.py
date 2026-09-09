
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
    'PIPE',
    'NEWLINE'
)



# VARIABLES GLOBALES


errores_lexicos = []
errores_sintacticos = []

linea_actual = ""
campo_actual = 1

MAX_32_BITS = 4294967295


 
# TOKENS SIMPLES
 

t_TABLE_DUMP2 = r'TABLE_DUMP2'
t_STATE = r'[BAW]'
t_ignore = ' \t(),{}'


 
# PIPE
 

def t_PIPE(t):
    r'\|'

    global campo_actual

    campo_actual += 1

    return t


 
# IP Y PREFIX
 

OCTET = (
    r'(?:'
    r'25[0-5]'
    r'|2[0-4][0-9]'
    r'|1[0-9]{2}'
    r'|[1-9]?[0-9]'
    r')'
    r'(?![0-9])'
)

IP_REGEX = (
    OCTET + r'\.' +
    OCTET + r'\.' +
    OCTET + r'\.' +
    OCTET
)

MASK = r'(?:3[0-2]|[12][0-9]|[0-9])(?![0-9])'

PREFIX_REGEX = IP_REGEX + r'/' + MASK


@lex.TOKEN(PREFIX_REGEX)
def t_PREFIX(t):
    return t


@lex.TOKEN(IP_REGEX)
def t_IP(t):
    return t


 
# TIMESTAMP Y AS_NUMBER
 

def t_AS_NUMBER(t):
    r'\d+'

    global campo_actual

    valor = int(t.value)

    # Campo 2 = TIMESTAMP
    if campo_actual == 2:

        t.type = 'TIMESTAMP'
        t.value = valor

        if valor > MAX_32_BITS:

            mensaje = (
                f"Error lexico en linea {t.lexer.lineno}: "
                f"TIMESTAMP fuera de rango "
                f"(max {MAX_32_BITS}): {valor} "
                f"| Contenido: {linea_actual.rstrip()}"
            )

            errores_lexicos.append(mensaje)
            print(mensaje)

        return t

    # Campo 5 o 7 = AS_NUMBER
    if campo_actual == 5 or campo_actual == 7:

        t.type = 'AS_NUMBER'
        t.value = valor

        if valor > MAX_32_BITS:

            mensaje = (
                f"Error lexico en linea {t.lexer.lineno}: "
                f"AS_NUMBER fuera de rango "
                f"(max {MAX_32_BITS}): {valor} "
                f"| Contenido: {linea_actual.rstrip()}"
            )

            errores_lexicos.append(mensaje)
            print(mensaje)

        return t

    # Si aparece un numero en otro campo,
    # lo devolvemos como AS_NUMBER para que
    # el parser detecte que esta en una posicion incorrecta.
    t.type = 'AS_NUMBER'
    t.value = valor

    return t


 
# NEWLINE
 

def t_NEWLINE(t):
    r'\n+'

    global campo_actual

    t.lexer.lineno += len(t.value)

    campo_actual = 1

    return t


 
# ERROR LEXICO
 

def t_error(t):

    mensaje = (
        f"Error lexico en linea {t.lexer.lineno}: "
        f"caracter no reconocido '{t.value[0]}' "
        f"| Contenido: {linea_actual.rstrip()}"
    )

    errores_lexicos.append(mensaje)

    print(mensaje)

    t.lexer.skip(1)


 
# CREAR LEXER
 

lexer = lex.lex()


 
# PARSER
 

start = 'archivo'


def p_archivo(p):
    '''
    archivo : lineas
    '''
    pass


def p_lineas(p):
    '''
    lineas : lineas linea
           | linea
    '''
    pass


def p_linea(p):
    '''
    linea : TABLE_DUMP2 PIPE TIMESTAMP PIPE STATE PIPE IP PIPE AS_NUMBER PIPE PREFIX PIPE as_path NEWLINE
    '''

    peer_as = p[9]
    primer_as_path = p[13]

    numero_linea = p.lineno(1)

    if peer_as != primer_as_path:

        mensaje = (
            f"Error sintactico/estructural en linea "
            f"{numero_linea}: "
            f"Peer AS {peer_as} no coincide con "
            f"el primer AS del AS Path {primer_as_path} "
            f"| Contenido: {linea_actual.rstrip()}"
        )

        errores_sintacticos.append(mensaje)

        print(mensaje)


def p_as_path(p):
    '''
    as_path : AS_NUMBER as_path_resto
    '''

    # Se retorna solamente el primer AS para compararlo
    # con el Peer AS. No se crea una lista.
    p[0] = p[1]


def p_as_path_resto_numero(p):
    '''
    as_path_resto : AS_NUMBER as_path_resto
    '''
    pass


def p_as_path_resto_vacio(p):
    '''
    as_path_resto : empty
    '''
    pass


def p_empty(p):
    '''
    empty :
    '''
    pass


 
# ERROR SINTACTICO
 

def p_error(p):

    if p is None:

        mensaje = (
            "Error sintactico: "
            "fin inesperado de la entrada. "
            "La linea puede estar incompleta."
        )

    else:

        mensaje = (
            f"Error sintactico en linea {p.lineno}: "
            f"token inesperado {p.type} "
            f"con valor {p.value!r} "
            f"| Contenido: {linea_actual.rstrip()}"
        )

    errores_sintacticos.append(mensaje)

    print(mensaje)


 
# CREAR PARSER
 

parser = yacc.yacc()


 
# ANALIZAR UNA LINEA
 

def analizar_linea(linea, numero_linea):

    global linea_actual
    global campo_actual

    linea_actual = linea

    campo_actual = 1

    lexer.lineno = numero_linea

    if not linea.endswith('\n'):
        linea += '\n'

    parser.parse(
        linea,
        lexer=lexer,
        tracking=True
    )


 
# ANALIZAR ARCHIVO
 

def analizar_archivo(ruta):

    errores_lexicos.clear()
    errores_sintacticos.clear()

    total_lineas = 0

    nombre_archivo = os.path.basename(ruta)

    print()
    print("=" * 60)
    print(f"Archivo: {nombre_archivo}")
    print("=" * 60)

    with open(
        ruta,
        "r",
        encoding="utf-8"
    ) as archivo:

        for numero_linea, linea in enumerate(
            archivo,
            start=1
        ):

            total_lineas += 1

            analizar_linea(
                linea,
                numero_linea
            )

    print()
    print(f"Lineas analizadas: {total_lineas}")
    print(f"Errores lexicos: {len(errores_lexicos)}")
    print(
        f"Errores sintacticos/estructurales: "
        f"{len(errores_sintacticos)}"
    )

    return (
        list(errores_lexicos),
        list(errores_sintacticos)
    )


 
# GUARDAR ERRORES
 

def guardar_errores(
    carpeta_salida,
    nombre_archivo,
    errores_lex,
    errores_sint
):

    if errores_lex:

        ruta_errores_lexicos = os.path.join(
            carpeta_salida,
            f"errores_lexicos_{nombre_archivo}"
        )

        with open(
            ruta_errores_lexicos,
            "w",
            encoding="utf-8"
        ) as salida:

            for error in errores_lex:
                salida.write(error + "\n")

        print(
            f"Archivo de errores lexicos: "
            f"{ruta_errores_lexicos}"
        )

    if errores_sint:

        ruta_errores_sintacticos = os.path.join(
            carpeta_salida,
            f"errores_sintacticos_{nombre_archivo}"
        )

        with open(
            ruta_errores_sintacticos,
            "w",
            encoding="utf-8"
        ) as salida:

            for error in errores_sint:
                salida.write(error + "\n")

        print(
            f"Archivo de errores sintacticos: "
            f"{ruta_errores_sintacticos}"
        )


 
# PROGRAMA PRINCIPAL
 

if __name__ == "__main__":


    carpeta_entregable = os.path.dirname(
        os.path.abspath(__file__)
    )

    carpeta_proyecto = os.path.dirname(
        carpeta_entregable
    )

    carpeta_datos = os.path.join(
        carpeta_proyecto,
        "Datos"
    )

    carpeta_chunks = os.path.join(
        carpeta_datos,
        "Chunks"
    )

    carpeta_salida = os.path.join(
        carpeta_chunks,
        "resultados_parser"
    )

    os.makedirs(
        carpeta_salida,
        exist_ok=True
    )

    print("Rutas utilizadas:")
    print(f"  Proyecto: {carpeta_proyecto}")
    print(f"  Datos: {carpeta_datos}")
    print(f"  Chunks: {carpeta_chunks}")
    print(f"  Salida: {carpeta_salida}")
    print()

    archivos = sorted(
        glob.glob(
            os.path.join(
                carpeta_chunks,
                "chunk_*.txt"
            )
        )
    )

    if not archivos:

        print(
            "No se encontraron archivos "
            "chunk_*.txt en:"
        )

        print(carpeta_chunks)

        raise SystemExit

    print("=" * 60)
    print("ANALISIS SINTACTICO INICIADO")
    print("=" * 60)

    print()
    print(f"Chunks encontrados: {len(archivos)}")
    print()

    total_errores_lexicos = 0
    total_errores_sintacticos = 0

    for ruta in archivos:

        nombre_archivo = os.path.basename(
            ruta
        )

        errores_lex, errores_sint = analizar_archivo(
            ruta
        )

        total_errores_lexicos += len(
            errores_lex
        )

        total_errores_sintacticos += len(
            errores_sint
        )

        guardar_errores(
            carpeta_salida,
            nombre_archivo,
            errores_lex,
            errores_sint
        )

    print()
    print("=" * 60)
    print("ANALISIS SINTACTICO FINALIZADO")
    print("=" * 60)

    print()
    print(
        f"Total errores lexicos: "
        f"{total_errores_lexicos}"
    )

    print(
        f"Total errores sintacticos/estructurales: "
        f"{total_errores_sintacticos}"
    )

    print()
    print("Resultados guardados en:")
    print(carpeta_salida)


