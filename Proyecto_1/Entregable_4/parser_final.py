# IMPORTAR BIBLOTECAS

import os
import glob
import ply.lex as lex
import ply.yacc as yacc

#====================================================== CARGAR DATOS ======================================================

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

#====================================================== ANALIZADOR LEXICO ======================================================

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
t_ignore = ' \t\n(),{}'

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
    r'\d{10}'
    t.value = int(t.value)

    valida_bits(t.value)

    return t

# TOKEN AS_NUMBER

def t_AS_NUMBER(t):
    r'\d{1,10}'
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

#====================================================== PARSER ======================================================

# GRAMATICA DEL PARSER

def p_ruta_bgp(p):
    'linea : TABLE_DUMP2 PIPE TIMESTAMP PIPE STATE PIPE IP PIPE AS_NUMBER PIPE PREFIX PIPE as_path'
    p[0]= {        
        'peer_ip': p[7],
        'peer_as': p[9],
        'prefijo': p[11], 
        'as_path': p[13]}

def p_as_path(p):
    '''as_path : as_path AS_NUMBER
               | as_path TIMESTAMP
               | AS_NUMBER
               | TIMESTAMP'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

errores_sintacticos = []

def p_error(p):
    contenido = linea_actual.rstrip(chr(10))

    if p:
        errores_sintacticos.append(
            f"Linea {p.lineno} | {contenido}"
        )
    else:
        errores_sintacticos.append(
            f"Linea {lexer.lineno}: la entrada termino antes de tiempo "
            f"| Contenido: {contenido}"
        )

# CREAR PARSER
parser = yacc.yacc()

#================================================ ESTRUCTURAS DE DATOS ================================================

# FUNCIONALIDAD 1

funcionalidad_1_datos = {}

def funcionalidad_1(prefijo, as_path):

    if prefijo not in funcionalidad_1_datos:
        funcionalidad_1_datos[prefijo] = [as_path[-1]]
    else:
        if as_path[-1] not in funcionalidad_1_datos[prefijo]:
          funcionalidad_1_datos[prefijo].append(as_path[-1])


#================================================ FUNCIONALIDAD 2 ====================================================

datos_por_as = {}

def funcionalidad_2(peer_as, peer_ip, prefijo, as_path):

    # Si el AS no existe, se crea.
    if peer_as not in datos_por_as:
        datos_por_as[peer_as] = {}

    # Si la arista (Peer IP) no existe para ese AS,
    # se crea con una lista vacia.
    if peer_ip not in datos_por_as[peer_as]:
        datos_por_as[peer_as][peer_ip] = []

    # Se almacena el prefijo junto con su AS Path.
    datos_por_as[peer_as][peer_ip].append(
        {
            "prefijo": prefijo,
            "as_path": as_path
        }
    )

#================================================ FUNCIONALIDAD 3 ====================================================

datos_funcionalidad_3 = {}

def funcionalidad_3(prefijo, peer_as, as_path):

    # Si el prefijo no existe, se crea.

    if prefijo not in datos_funcionalidad_3:

        datos_funcionalidad_3[prefijo] = {}

    # Si el Peer AS no existe para ese prefijo, se crea.

    if peer_as not in datos_funcionalidad_3[prefijo]:

        datos_funcionalidad_3[prefijo][peer_as] = []

    # Se almacena el AS Path asociado.

    datos_funcionalidad_3[prefijo][peer_as].append(as_path)

#==================================== PROCESAR LINEAS: LEXER + PARSER SOBRE CADA LINEA ====================================

total_lineas = 0
lineas_ok = 0

try:

    for ruta in archivos:

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

                lexer.lineno = numero_linea

                linea_actual = linea

                resultado = parser.parse(linea, lexer=lexer)

                if resultado:
                    lineas_ok += 1

                    prefijo = resultado.get('prefijo')
                    as_path = resultado.get('as_path')
                    peer_as = resultado.get('peer_as')
                    peer_ip = resultado.get('peer_ip')

                    # FUNCIONALIDAD 1
                    funcionalidad_1(prefijo, as_path)

                    # FUNCIONALIDAD 2
                    funcionalidad_2(peer_as, peer_ip, prefijo, as_path)

                    # FUNCIONALIDAD 3
                    funcionalidad_3(prefijo, peer_as, as_path)
     
except Exception as e:

    print(f"Error leyendo archivos de entrada: {e}")

    raise SystemExit

print(f"Archivos leidos con exito: {len(archivos)}")
print(f"Lineas parseadas correctamente: {lineas_ok}/{total_lineas}")

if errores:

    print(f"\nErrores lexicos ({len(errores)}):")

    for error in errores:

        print("  ", error)

if errores_sintacticos:

    print(f"\nErrores sintacticos ({len(errores_sintacticos)}):")

    for error in errores_sintacticos:

        print("  ", error)

#======================================= MOSTRAR OUTPUTS ===========================

#=========== FUNCIONALIDAD 1
 
print(f"Prefijos distintos: {len(funcionalidad_1_datos)}")

moas = {p: o for p, o in funcionalidad_1_datos.items() if len(o) > 1}
unicos = {p: o for p, o in funcionalidad_1_datos.items() if len(o) == 1}
print(f"Prefijos con mas de un origen: {len(moas)}\n")

muestras = sorted(moas.items())[:7] + sorted(unicos.items())[:7]
ancho = max(len(p) for p, _ in muestras)

print(f"{'PREFIJO':<{ancho}}  {'#':>2}  ORIGENES")
print("-" * (ancho + 30))

for prefijo, origenes in muestras:
    lista = ", ".join(str(o) for o in sorted(origenes))
    print(f"{prefijo:<{ancho}}  {len(origenes):>2}  {lista}")


#=========== FUNCIONALIDAD 2

print(
    f"\nPeer AS distintos: "
    f"{len(datos_por_as)}"
)

print(
    f"Peer AS encontrados: "
    f"{list(datos_por_as.keys())}"
)

# TOP 5 AS con mayor cantidad de rutas
top_as = sorted(
    datos_por_as.items(),
    key=lambda item: sum(
        len(rutas)
        for rutas in item[1].values()
    ),
    reverse=True
)[:5]

print("\nTOP 5 Peer AS con mas rutas:")

for peer_as, peer_ips in top_as:

    cantidad_aristas = len(peer_ips)

    cantidad_rutas = sum(
        len(rutas)
        for rutas in peer_ips.values()
    )

    print(
        f"AS {peer_as}: "
        f"{cantidad_aristas} aristas, "
        f"{cantidad_rutas} rutas"
    )

#=========== FUNCIONALIDAD 3

print(

    f"\nPrefijos distintos en funcionalidad 3: "

    f"{len(datos_funcionalidad_3)}"

)

print("\nEjemplo de estructuras creadas:")

for prefijo, datos in list(datos_funcionalidad_3.items())[:2]:

    print(f"\nPrefijo: {prefijo}")
    print(datos)