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

archivo_prueba = os.path.join(
    carpeta_chunks,
    "chunk_aa.txt"
)

if not os.path.exists(archivo_prueba):
    print(
        f"No se encontró el archivo: {archivo_prueba}"
    )
    raise SystemExit

archivos = [archivo_prueba]

 
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
# Cada octeto va de 0 a 255 y son 4 octetos los que llevan una IP 
# Una IP esta conformada por 4 octetos separados por puntos

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
# IP + / + longitud de mascara = PREFIX 

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

    
    peer_ip = p[7]
    peer_as = p[9]
    prefijo = p[11]
    as_path = p[13]

    # Resultado funcionalidades 1 y 2

    p[0] = {
        'peer_ip': peer_ip,
        'peer_as': peer_as,
        'prefijo': prefijo,
        'as_path': as_path
    }

    # FUNCIONALIDAD 3

    # 1. Relación PREFIJO -> AS

    if prefijo not in prefijo_as:
        prefijo_as[prefijo] = set()

    prefijo_as[prefijo].add(peer_as)

    # 2. Construcción del grafo AS -> AS

    for i in range(len(as_path) - 1):

        as_actual = as_path[i]
        as_siguiente = as_path[i + 1]

        if as_actual not in grafo_as:
            grafo_as[as_actual] = set()

        grafo_as[as_actual].add(as_siguiente)

    # Aseguramos que el último AS también exista como nodo
    if as_path:
        ultimo_as = as_path[-1]

        if ultimo_as not in grafo_as:
            grafo_as[ultimo_as] = set()
 
 
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
 
#================================================ FUNCIONALIDAD 1 ====================================================
 
funcionalidad_1_datos = {} 
 
 
def funcionalidad_1(prefijo, as_path): 
 
    if prefijo not in funcionalidad_1_datos: 
        funcionalidad_1_datos[prefijo] = [as_path[-1]] 
    else: 
        if as_path[-1] not in funcionalidad_1_datos[prefijo]: 
            funcionalidad_1_datos[prefijo].append(as_path[-1]) 


#================================================ FUNCIONALIDAD 2 ====================================================

# Estructura:
#
# datos_por_as = {
#     peer_as: {
#         peer_ip: [
#             {
#                 "prefijo": prefijo,
#                 "as_path": [AS1, AS2, AS3, ...]
#             }
#         ]
#     }
# }

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

# Estructura que relaciona cada prefijo con los Peer AS asociados
prefijo_as = {}

# Estructura que representa el grafo dirigido entre AS
grafo_as = {}

def dfs_rutas(as_actual, as_destino, ruta_actual, visitados, rutas):
    # Si llegamos al AS destino, guardamos la ruta encontrada
    if as_actual == as_destino:
        rutas.append(ruta_actual.copy())
        return

    # Obtener los AS conectados al AS actual
    siguientes = grafo_as.get(as_actual, set())

    for as_siguiente in siguientes:

        # Evitar ciclos dentro de la ruta actual
        if as_siguiente in visitados:
            continue

        visitados.add(as_siguiente)
        ruta_actual.append(as_siguiente)

        dfs_rutas(
            as_siguiente,
            as_destino,
            ruta_actual,
            visitados,
            rutas
        )

        # Regresar para poder buscar otra ruta
        ruta_actual.pop()
        visitados.remove(as_siguiente)


def buscar_rutas(prefijo_A, prefijo_B):

    # Verificar que ambos prefijos existan
    if prefijo_A not in prefijo_as:
        return []

    if prefijo_B not in prefijo_as:
        return []

    # Obtener los AS asociados a cada prefijo
    ases_origen = prefijo_as[prefijo_A]
    ases_destino = prefijo_as[prefijo_B]

    todas_las_rutas = []

    # Buscar rutas desde cada AS de A hacia cada AS de B
    for as_origen in ases_origen:
        for as_destino in ases_destino:

            ruta_actual = [as_origen]
            visitados = {as_origen}

            dfs_rutas(
                as_origen,
                as_destino,
                ruta_actual,
                visitados,
                todas_las_rutas
            )

    return todas_las_rutas

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
 
                resultado = parser.parse(
                    linea,
                    lexer=lexer
                ) 
 
                if resultado: 

                    lineas_ok += 1 
 
                    # FUNCIONALIDAD 1 

                    funcionalidad_1(
                        resultado.get('prefijo'),
                        resultado.get('as_path')
                    )

                    # FUNCIONALIDAD 2

                    funcionalidad_2(
                        resultado.get('peer_as'),
                        resultado.get('peer_ip'),
                        resultado.get('prefijo'),
                        resultado.get('as_path')
                    )
 
 
except Exception as e: 
 
    print(f"Error leyendo archivos de entrada: {e}") 
 
    raise SystemExit 
 
 
print(f"Archivos leidos con exito: {len(archivos)}") 

print(
    f"Lineas parseadas correctamente: "
    f"{lineas_ok}/{total_lineas}"
) 
 
 
if errores: 
 
    print(f"\nErrores lexicos ({len(errores)}):") 
 
    for error in errores: 
 
        print("  ", error) 
 
 
if errores_sintacticos: 
 
    print(
        f"\nErrores sintacticos "
        f"({len(errores_sintacticos)}):"
    ) 
 
    for error in errores_sintacticos: 
 
        print("  ", error) 
 
 
#======================================= MOSTRAR OUTPUTS =========================== 
 
#=========== FUNCIONALIDAD 1 
 
print(
    f"Prefijos distintos: "
    f"{len(funcionalidad_1_datos)}"
)


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

prefijo_A = "11.0.0.0/8"
prefijo_B = "40.138.0.0/17"

rutas = buscar_rutas(prefijo_A, prefijo_B)

print(
    f"\nRutas entre {prefijo_A} y {prefijo_B}: "
    f"{len(rutas)}"
)

for numero, ruta in enumerate(rutas, start=1):
    print(
        f"Ruta {numero}: "
        + " -> ".join(map(str, ruta))
    )