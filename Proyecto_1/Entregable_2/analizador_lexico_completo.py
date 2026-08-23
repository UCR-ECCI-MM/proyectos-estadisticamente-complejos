
# LIBRERIAS


import os
import glob
import ply.lex as lex


# TOKENS


tokens = (
    'TABLE_DUMP2',
    'STATE',
    'IP',
    'PREFIX',
    'NUMBER',
    'PIPE',
    'LBRACE',
    'RBRACE',
    'COMMA'
)



# TOKENS SIMPLES


t_TABLE_DUMP2 = r'TABLE_DUMP2'
t_PIPE = r'\|'
t_STATE = r'[BAW]{1}'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COMMA = r','
t_ASPATH = r'\d{1,10}(\s+\d{1,10})*'


# IP Y PREFIX
#Cada octeto va de 0 225 y son 4 octetos los que llevan una IP


OCTET = r'(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])'
# Una ip esta conformada por 4 octetos separados por puntos, esto se hace aca

IP_REGEX = (
    OCTET + r'\.' +
    OCTET + r'\.' +
    OCTET + r'\.' +
    OCTET
)

# La mascara puede ir de 0 a 32 y se separa con / del IP
MASK = r'(?:3[0-2]|[12][0-9]|[0-9])'

PREFIX_REGEX = IP_REGEX + r'/' + MASK



# TOKEN PREFIX

#  IP + / + longitud de máscara = PREFIX
@lex.TOKEN(PREFIX_REGEX)
def t_PREFIX(t):
    return t



# TOKEN IP


@lex.TOKEN(IP_REGEX)
def t_IP(t):
    return t



# TOKEN NUMBER


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t



# ESPACIOS


t_ignore = ' \t'



# SALTOS DE LINEA


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)



# ERRORES LEXICOS


errores = []


def t_error(t):

    errores.append(
        f"Línea {t.lexer.lineno}: "
        f"carácter no reconocido '{t.value[0]}'"
    )

    t.lexer.skip(1)



# CREAR LEXER


lexer = lex.lex()



# CARPETAS


carpeta_chunks = (
    r"C:\Users\loboa\OneDrive\Desktop\Maestria"
    r"\Computabilidad_Complejidad\dumps_correctos\Chunks"
)

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


print(f"Chunks encontrados: {len(archivos)}")
print()


for ruta in archivos:

    errores.clear()

    lexer.lineno = 1

    total_tokens = 0
    total_lineas = 0


    # ========================================================
    # NOMBRES DE ARCHIVOS
    # ========================================================

    nombre_archivo = os.path.basename(ruta)

    nombre_salida = f"tokens_{nombre_archivo}"

    ruta_salida = os.path.join(
        carpeta_salida,
        nombre_salida
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


                # =============================================
                # GUARDAR SOLO EL VALOR DEL TOKEN
                # =============================================

                salida.write(
                    f"{token.value}\n"
                )


    # ========================================================
    # RESULTADOS EN CONSOLA
    # ========================================================

    print("=" * 60)

    print(f"Archivo: {nombre_archivo}")

    print(f"Líneas analizadas: {total_lineas}")

    print(f"Tokens reconocidos: {total_tokens}")

    print(f"Errores léxicos: {len(errores)}")


    # ========================================================
    # MOSTRAR ERRORES
    # ========================================================

    if errores:

        print("Errores encontrados:")

        for error in errores[:10]:

            print("  ", error)


        if len(errores) > 10:

            print(
                f"  ... y "
                f"{len(errores) - 10} "
                f"errores adicionales."
            )

    else:

        print("No se encontraron errores léxicos.")


    print(
        f"\nArchivo generado: "
        f"{ruta_salida}"
    )

    print()



# MENSAJE FINAL


print("=" * 60)

print("ANÁLISIS LÉXICO FINALIZADO")

print("=" * 60)

print(
    f"Resultados guardados en:\n"
    f"{carpeta_salida}"
)
