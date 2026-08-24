
# LIBRERIAS


import os
import glob
from collections import Counter
import ply.lex as lex


# TOKENS

tokens = (
    'TABLE_DUMP2',
    'STATE',
    'IP',
    'PREFIX',
    'NUMBER',
    'PIPE',
    'NEWLINE'
)

# EXPRESIONES REGULARES

t_TABLE_DUMP2 = r'TABLE_DUMP2'
t_PIPE = r'\|'
t_STATE = r'[BAW]{1}'
t_ignore = ' \t'
#t_ASPATH = r'\d{1,10}(\s+\d{1,10})*'

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

# La mascara puede ir de 1 a 31 y se separa con / del IP
MASK = r'(?:3[0-1]|[12][0-9]|[1-9])(?![0-9])'
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

# TOKEN NUMBER

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)

    if t.value > 4294967295:
        print(
            f"Error de lexer en linea {t.lineno}: "
            f"Fuera de rango (max 4294967295): {t.value}"
        )
        return None

    return t

# SALTOS DE LINEA
def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    return t

# ERRORES LEXICOS

errores = []
def t_error(t):
    errores.append(
        f"Linea {t.lexer.lineno}: "
        f"caracter no reconocido '{t.value[0]}'"
    )
    t.lexer.skip(1)


# CREAR LEXER
lexer = lex.lex()

# CARPETAS

# Ruta relativa a la ubicacion de este script, no al usuario/PC actual,
# para que funcione igual en la maquina de cualquier integrante del equipo.
carpeta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
carpeta_chunks = os.path.join(carpeta_proyecto, "Datos", "Chunks")

carpeta_salida = os.path.join(
    carpeta_chunks,
    "resultados_lexer"
)
os.makedirs(carpeta_salida, exist_ok=True)

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

print("=" * 60)
print("ANALISIS LEXICO INICIADO")
print("=" * 60)
print()

print(f"Chunks encontrados: {len(archivos)}")
print()

resumen_global = Counter()

for ruta in archivos:

    errores.clear()

    lexer.lineno = 1

    total_tokens = 0
    total_lineas = 0

    resumen_chunk = Counter()


    # ========================================================
    # NOMBRES DE ARCHIVOS
    # ========================================================

    nombre_archivo = os.path.basename(ruta)

    nombre_salida = f"tokens_{nombre_archivo}"

    ruta_salida = os.path.join(
        carpeta_salida,
        nombre_salida
    )

    nombre_errores = f"errores_{nombre_archivo}"

    ruta_errores = os.path.join(
        carpeta_salida,
        nombre_errores
    )

    # ========================================================
    # LEER ARCHIVO
    # ========================================================

    with open(
        ruta,
        "r",
        encoding="utf-8"
    ) as archivo, open(
        ruta_salida,
        "w",
        encoding="utf-8"
    ) as salida:


        for numero_linea, linea in enumerate(
            archivo,
            start=1
        ):

            total_lineas += 1

            lexer.lineno = numero_linea

            lexer.input(linea)


            # =================================================
            # OBTENER TOKENS
            # =================================================

            while True:

                token = lexer.token()

                if token is None:
                    break

                total_tokens += 1

                resumen_chunk[token.type] += 1


                # =============================================
                # GUARDAR SOLO EL VALOR DEL TOKEN
                # =============================================

                salida.write(
                    f"{token.value}\n"
                )

    resumen_global.update(resumen_chunk)

    # ========================================================
    # GUARDAR ERRORES EN ARCHIVO
    # ========================================================

    if errores:

        with open(
            ruta_errores,
            "w",
            encoding="utf-8"
        ) as archivo_errores:

            for error in errores:

                archivo_errores.write(f"{error}\n")

    # ========================================================
    # RESULTADOS EN CONSOLA
    # ========================================================

    print("=" * 60)

    print(f"Archivo: {nombre_archivo}")

    print(f"Lineas analizadas: {total_lineas}")

    print(f"Tokens reconocidos: {total_tokens}")

    print(f"Errores lexicos: {len(errores)}")

    # ========================================================
    # MOSTRAR ERRORES
    # ========================================================

    if errores:

        print("Errores encontrados:")

        for error in errores[:4]:

            print("  ", error)


        if len(errores) > 4:

            print(
                f"  ... y "
                f"{len(errores) - 4} "
                f"errores adicionales."
            )

    else:

        print("No se encontraron errores lexicos.")


    print(
        f"\nArchivo generado: "
        f"{ruta_salida}"
    )

    if errores:

        print(
            f"Archivo de errores: "
            f"{ruta_errores}"
        )

    print()

# MENSAJE FINAL

print("=" * 60)

print("ANALISIS LEXICO FINALIZADO")

print("=" * 60)

print(
    f"Resultados guardados en:\n"
    f"{carpeta_salida}"
)

print()
print("Resumen global de tokens:")

for tipo, cantidad in sorted(resumen_global.items()):

    print(f"  {tipo}: {cantidad}")
