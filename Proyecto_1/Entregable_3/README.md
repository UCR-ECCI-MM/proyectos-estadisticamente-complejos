# Proyecto 1 — Entregable 3

## Analizador sintáctico de datos MRT utilizando PLY

Este entregable corresponde a la implementación de un **analizador sintáctico (parser)** para archivos MRT.

El programa utiliza como base el análisis léxico desarrollado en el Entregable 2 y añade una gramática que permite verificar que cada registro presente en los archivos de entrada siga la estructura esperada.

La implementación fue realizada en **Python** utilizando la biblioteca **PLY (Python Lex-Yacc)**, específicamente los módulos:

- `ply.lex`, para el análisis léxico.
- `ply.yacc`, para el análisis sintáctico.

En esta etapa todavía **no se crean estructuras de datos dinámicamente**. El objetivo del Entregable 3 es verificar la correctitud sintáctica de los registros MRT y reportar los errores encontrados.

> **Importante:** dentro de la carpeta del Entregable 3 existen archivos con los nombres de los integrantes del equipo. Estos archivos corresponden a **prototipos individuales realizados durante el proceso de desarrollo**.  
> La versión integrada y final del Entregable 3 se encuentra en el archivo **`analizador_sintactico_final.py`**, el cual es el archivo que debe utilizarse para ejecutar y evaluar el programa.

---

## 1. Objetivo del entregable

El objetivo principal del Entregable 3 es construir un **analizador sintáctico** capaz de validar la estructura de las líneas contenidas en los archivos MRT.

Cada línea debe respetar el siguiente formato general:

```text
TABLE_DUMP2|TIMESTAMP|STATE|IP|AS_NUMBER|PREFIX|AS_PATH
```

Por ejemplo:

```text
TABLE_DUMP2|1785888000|B|177.101.16.80|53046|7.0.0.0/8|53046 61626 14840 3356 749
```

El programa realiza las siguientes tareas:

1. Busca automáticamente todos los archivos `chunk_*.txt`.
2. Lee cada archivo línea por línea.
3. Ejecuta el lexer sobre cada línea.
4. Obtiene los tokens correspondientes.
5. Envía los tokens al parser.
6. Verifica que los campos aparezcan en el orden definido por la gramática.
7. Detecta y registra errores léxicos.
8. Detecta y registra errores sintácticos.
9. Cuenta cuántas líneas fueron parseadas correctamente.
10. Muestra un resumen general al finalizar.

---

## 2. Relación con el Entregable 2

En el Entregable 2 se desarrolló el **analizador léxico (lexer)**.

Su función era reconocer los diferentes componentes de cada registro MRT y convertirlos en tokens.

En el Entregable 3 se incorpora el **analizador sintáctico (parser)**.

Su función es comprobar que los tokens reconocidos por el lexer aparezcan en la estructura y en el orden esperado.

La diferencia principal entre ambas etapas es:

| Etapa | Función |
|---|---|
| Lexer | Verifica que cada elemento individual tenga un formato reconocido. |
| Parser | Verifica que los elementos aparezcan en la estructura y orden definidos por la gramática. |

Por lo tanto, el parser utiliza como entrada los tokens producidos por el lexer.

---

## 3. Archivo final del Entregable 3

Durante el desarrollo del proyecto cada integrante realizó diferentes pruebas y prototipos del parser.

Por esta razón, dentro de la carpeta `Entregable_3` pueden encontrarse archivos identificados con nombres como:

- analizador_sintactico_alison.py
- analizador_sintactico_brandon.py
- analizador_sintactico_sebas.py

Estos archivos representan **prototipos desarrollados individualmente** y se conservaron como evidencia del proceso de trabajo e integración realizado por el equipo.

Sin embargo, estos archivos **no corresponden a la versión final que debe ejecutarse**.

La implementación final, integrada y utilizada para este entregable se encuentra en:

```text
analizador_sintactico_final.py
```

Por lo tanto, todas las instrucciones de ejecución presentadas en este README hacen referencia a este archivo.

---

## 4. Tecnologías y bibliotecas utilizadas

El programa utiliza las siguientes bibliotecas de Python:

```python
import os
import glob
import ply.lex as lex
import ply.yacc as yacc
```

### `os`

Se utiliza para trabajar con rutas y carpetas del sistema operativo.

Permite construir rutas relativas al proyecto para evitar depender de una ruta específica de la computadora de algún integrante.

---

### `glob`

Permite buscar automáticamente archivos que cumplan con un determinado patrón.

En este proyecto se utiliza para localizar los archivos:

```text
chunk_*.txt
```

---

### `ply.lex`

Corresponde al módulo de PLY utilizado para construir el **analizador léxico**.

---

### `ply.yacc`

Corresponde al módulo de PLY utilizado para construir el **analizador sintáctico** a partir de las producciones gramaticales definidas.

---

## 5. Tokens definidos

El lexer utiliza los siguientes tokens:

```python
tokens = (
    'TABLE_DUMP2',
    'STATE',
    'TIMESTAMP',
    'IP',
    'PREFIX',
    'AS_NUMBER',
    'PIPE'
)
```

Cada token representa un elemento presente en los registros MRT.

| Token | Descripción | Ejemplo |
|---|---|---|
| `TABLE_DUMP2` | Identificador del tipo de registro | `TABLE_DUMP2` |
| `TIMESTAMP` | Marca temporal | `1785888000` |
| `STATE` | Estado del registro BGP | `B`, `A` o `W` |
| `IP` | Dirección IPv4 | `177.101.16.80` |
| `AS_NUMBER` | Número de sistema autónomo | `53046` |
| `PREFIX` | Dirección IPv4 acompañada de una máscara | `7.0.0.0/8` |
| `PIPE` | Separador entre los campos | `|` |

---

## 6. Reconocimiento de `TABLE_DUMP2`

El tipo de registro es reconocido mediante:

```python
t_TABLE_DUMP2 = r'TABLE_DUMP2'
```

Por ejemplo:

```text
TABLE_DUMP2
```

produce un token:

```text
TABLE_DUMP2
```

---

## 7. Reconocimiento del separador `PIPE`

Los campos de los registros MRT se encuentran separados mediante:

```text
|
```

Este carácter es reconocido mediante:

```python
t_PIPE = r'\|'
```

La barra invertida permite indicar que `|` debe interpretarse como un carácter literal dentro de la expresión regular.

---

## 8. Reconocimiento del estado

Los estados permitidos se reconocen mediante:

```python
t_STATE = r'[BAW]{1}'
```

Esto permite reconocer los valores:

```text
B
A
W
```

---

## 9. Caracteres ignorados

El lexer utiliza:

```python
t_ignore = ' \t\n(),{}'
```

Por lo tanto, los siguientes caracteres son ignorados:

- Espacios.
- Tabulaciones.
- Saltos de línea.
- Paréntesis.
- Llaves.
- Comas.

Los espacios son necesarios para separar los diferentes valores presentes dentro del `AS_PATH`.

---

## 10. Reconocimiento de direcciones IPv4

Una dirección IPv4 está formada por **cuatro octetos separados por puntos**.

Por ejemplo:

```text
177.101.16.80
```

Cada octeto puede contener valores entre:

```text
0 y 255
```

La expresión regular utilizada es:

```python
OCTET = r'(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])(?![0-9])'
```

La expresión puede dividirse de la siguiente manera:

| Expresión | Valores reconocidos |
|---|---|
| `25[0-5]` | 250–255 |
| `2[0-4][0-9]` | 200–249 |
| `1[0-9]{2}` | 100–199 |
| `[1-9]?[0-9]` | 0–99 |

Posteriormente se combinan cuatro octetos separados por puntos:

```python
IP_REGEX = (
    OCTET + r'\.' +
    OCTET + r'\.' +
    OCTET + r'\.' +
    OCTET
)
```

La regla utilizada por PLY es:

```python
@lex.TOKEN(IP_REGEX)
def t_IP(t):
    return t
```

Por ejemplo:

```text
177.101.16.80
```

es reconocido como:

```text
IP
```

---

## 11. Reconocimiento de prefijos

Un prefijo está formado por:

```text
Dirección IP + / + longitud de máscara
```

Por ejemplo:

```text
7.0.0.0/8
```

La máscara se reconoce mediante:

```python
MASK = r'(?:3[0-2]|[12][0-9]|[0-9])(?![0-9])'
```

La expresión utilizada para construir un prefijo es:

```python
PREFIX_REGEX = IP_REGEX + r'/' + MASK
```

La regla correspondiente es:

```python
@lex.TOKEN(PREFIX_REGEX)
def t_PREFIX(t):
    return t
```

La regla `PREFIX` se define antes que la regla `IP` porque un prefijo comienza precisamente con una dirección IPv4.

De esta manera, el lexer intenta reconocer primero la expresión completa.

---

## 12. Validación de valores numéricos

El programa utiliza una función para comprobar el rango máximo permitido para los valores numéricos procesados:

```python
def valida_bits(num):
    if num > 4294967295:
        print(
            f"Error de lexer en linea {num.lineno}: "
            f"Fuera de rango (max 4294967295): {num.value}"
        )
        return None
```

El límite considerado por la implementación es:

```text
4294967295
```

---

## 13. Reconocimiento de `TIMESTAMP`

El timestamp se reconoce mediante:

```python
def t_TIMESTAMP(t):
    r'\d{10}'
    t.value = int(t.value)

    valida_bits(t.value)

    return t
```

La expresión:

```text
\d{10}
```

indica que el token está compuesto por exactamente **10 dígitos**.

Por ejemplo:

```text
1785888000
```

se reconoce como:

```text
TIMESTAMP
```

Después de reconocer el valor se convierte a entero mediante:

```python
t.value = int(t.value)
```

---

## 14. Reconocimiento de `AS_NUMBER`

Los números correspondientes a sistemas autónomos se reconocen mediante:

```python
def t_AS_NUMBER(t):
    r'\d{1,10}'
    t.value = int(t.value)

    valida_bits(t.value)

    return t
```

La expresión:

```text
\d{1,10}
```

permite reconocer números formados por entre **1 y 10 dígitos**.

Por ejemplo:

```text
53046
```

se reconoce como:

```text
AS_NUMBER
```

---

## 15. Manejo de errores léxicos

Los errores léxicos se almacenan en:

```python
errores = []
```

También se utiliza:

```python
linea_actual = ""
```

para conservar el contenido de la línea que está siendo procesada.

La función encargada del manejo de errores es:

```python
def t_error(t):
    errores.append(
        f"Linea {t.lexer.lineno}: "
        f"caracter no reconocido '{t.value[0]}' "
        f"| Contenido: {linea_actual.rstrip(chr(10))}"
    )
    t.lexer.skip(1)
```

Cuando se encuentra un carácter no reconocido:

1. Se registra el número de línea.
2. Se registra el carácter que produjo el error.
3. Se almacena el contenido completo de la línea.
4. El lexer avanza una posición mediante `skip(1)`.
5. El análisis continúa.

Esto permite que un error individual no detenga completamente el procesamiento.

---

## 16. Creación del lexer

Una vez definidas todas las reglas léxicas, el lexer se construye mediante:

```python
lexer = lex.lex()
```

PLY utiliza las expresiones regulares y funciones definidas anteriormente para generar el analizador léxico.

---

# Analizador sintáctico

A partir de esta sección se describe específicamente el componente principal desarrollado para el **Entregable 3: el parser**.

---

## 17. Gramática principal del parser

La producción principal utilizada para validar cada línea es:

```python
def p_ruta_bgp(p):
    'linea : TABLE_DUMP2 PIPE TIMESTAMP PIPE STATE PIPE IP PIPE AS_NUMBER PIPE PREFIX PIPE as_path'
    p[0] = True
```

Esta regla establece que los campos deben aparecer en el siguiente orden:

```text
TABLE_DUMP2
|
TIMESTAMP
|
STATE
|
IP
|
AS_NUMBER
|
PREFIX
|
AS_PATH
```

De manera simplificada:

```text
linea →
TABLE_DUMP2 PIPE TIMESTAMP PIPE STATE PIPE IP PIPE AS_NUMBER PIPE PREFIX PIPE as_path
```

Una línea válida puede ser:

```text
TABLE_DUMP2|1785888000|B|177.101.16.80|53046|7.0.0.0/8|53046 61626 14840 3356 749
```

Si la línea cumple con la gramática se ejecuta:

```python
p[0] = True
```

Posteriormente este resultado permite contar la línea como correctamente parseada.

---

## 18. Regla del `AS_PATH`

El último campo corresponde a la secuencia de sistemas autónomos que forman la ruta.

La producción utilizada es:

```python
def p_as_path(p):
    '''as_path : AS_NUMBER lista_as
               | TIMESTAMP lista_as'''
```

Esta regla establece que un `AS_PATH` comienza con al menos un valor numérico.

El parser acepta como primer elemento:

```text
AS_NUMBER
```

o:

```text
TIMESTAMP
```

Esto permite manejar los valores numéricos reconocidos por las reglas definidas en el lexer.

---

## 19. Procesamiento de la lista de AS

Los elementos adicionales del `AS_PATH` se procesan mediante una producción recursiva:

```python
def p_listas_as(p):
    '''lista_as : AS_NUMBER lista_as
                | TIMESTAMP lista_as
                | '''
```

Esta producción contempla tres posibilidades:

1. Encontrar un `AS_NUMBER` y continuar procesando la lista.
2. Encontrar un `TIMESTAMP` y continuar procesando la lista.
3. Encontrar una producción vacía, lo que indica que terminó la lista.

Conceptualmente:

```text
lista_as → AS_NUMBER lista_as
         | TIMESTAMP lista_as
         | ε
```

El símbolo:

```text
ε
```

representa la cadena vacía.

Esta producción recursiva permite procesar rutas con diferente cantidad de sistemas autónomos.

Por ejemplo:

```text
53046
```

```text
53046 61626
```

```text
53046 61626 14840 3356 749
```

---

## 20. Gramática utilizada

La gramática del parser puede resumirse de la siguiente manera:

```text
linea →
    TABLE_DUMP2 PIPE
    TIMESTAMP PIPE
    STATE PIPE
    IP PIPE
    AS_NUMBER PIPE
    PREFIX PIPE
    as_path

as_path →
    AS_NUMBER lista_as
    | TIMESTAMP lista_as

lista_as →
    AS_NUMBER lista_as
    | TIMESTAMP lista_as
    | ε
```

Esta gramática permite comprobar la estructura general de los registros MRT procesados.

---

## 21. Manejo de errores sintácticos

Los errores detectados por el parser se almacenan en:

```python
errores_sintacticos = []
```

La función encargada de manejar estos errores es:

```python
def p_error(p):
    contenido = linea_actual.rstrip(chr(10))

    if p:
        errores_sintacticos.append(
            f"Linea {p.lineno}: no esperaba '{p.value}' "
            f"| Contenido: {contenido}"
        )
    else:
        errores_sintacticos.append(
            f"Linea {lexer.lineno}: la entrada termino antes de tiempo "
            f"| Contenido: {contenido}"
        )
```

La función contempla dos situaciones principales.

### Token inesperado

Cuando `p` contiene información, significa que el parser encontró un token que no esperaba según la gramática.

El programa registra:

- El número de línea.
- El valor inesperado.
- El contenido completo de la línea.

Por ejemplo:

```text
Linea 25: no esperaba 'B' | Contenido: ...
```

### Entrada incompleta

Cuando `p` es `None`, significa que la entrada terminó antes de completar una producción válida.

En este caso se registra:

```text
Linea X: la entrada termino antes de tiempo | Contenido: ...
```

---

## 22. Creación del parser

Una vez definidas las producciones gramaticales, el parser se construye mediante:

```python
parser = yacc.yacc()
```

PLY utiliza las funciones definidas con el prefijo `p_` para construir automáticamente el analizador sintáctico.

---

## 23. Manejo de rutas

Para evitar utilizar rutas absolutas asociadas a una computadora específica, se utiliza:

```python
carpeta_proyecto = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
```

Posteriormente se define la carpeta donde se encuentran los chunks:

```python
carpeta_chunks = os.path.join(
    carpeta_proyecto,
    "Datos",
    "Chunks"
)
```

De esta manera, el programa puede funcionar en las computadoras de los diferentes integrantes del equipo sin tener que modificar manualmente las rutas.

---

## 24. Búsqueda automática de archivos

Los archivos MRT divididos en chunks se buscan utilizando:

```python
archivos = sorted(
    glob.glob(
        os.path.join(
            carpeta_chunks,
            "chunk_*.txt"
        )
    )
)
```

El patrón utilizado es:

```text
chunk_*.txt
```

Por ejemplo:

```text
chunk_aa.txt
chunk_ab.txt
chunk_ac.txt
```

Si no se encuentran archivos, el programa muestra:

```text
No se encontraron archivos chunk_*.txt
```

y finaliza mediante:

```python
raise SystemExit
```

---

## 25. Procesamiento de los chunks

El programa recorre todos los archivos encontrados.

Cada archivo se abre mediante:

```python
with open(
    ruta,
    "r",
    encoding="utf-8"
) as archivo:
```

Posteriormente se procesa línea por línea:

```python
for numero_linea, linea in enumerate(
    archivo,
    start=1
):
```

Para cada registro se realizan los siguientes pasos:

1. Se aumenta el contador total de líneas.
2. Se actualiza el número de línea del lexer.
3. Se guarda el contenido en `linea_actual`.
4. Se envía la línea al parser.

La ejecución del parser se realiza mediante:

```python
resultado = parser.parse(linea, lexer=lexer)
```

Si el resultado es verdadero:

```python
if resultado:
    lineas_ok += 1
```

la línea se contabiliza como correctamente parseada.

---

## 26. Contadores utilizados

El programa mantiene dos contadores principales:

```python
total_lineas = 0
lineas_ok = 0
```

### `total_lineas`

Contiene la cantidad total de líneas procesadas.

### `lineas_ok`

Contiene la cantidad de líneas aceptadas correctamente por la gramática.

Al finalizar se muestra:

```python
print(f"Archivos leidos con exito: {len(archivos)}")
print(f"Lineas parseadas correctamente: {lineas_ok}/{total_lineas}")
```

Por ejemplo:

```text
Archivos leidos con exito: 3
Lineas parseadas correctamente: 1500000/1500000
```

---

## 27. Reporte de errores

Si existen errores léxicos:

```python
if errores:

    print(f"\nErrores lexicos ({len(errores)}):")

    for error in errores:

        print("  ", error)
```

El programa puede mostrar:

```text
Errores lexicos (2):
   Linea 15: caracter no reconocido ...
   Linea 80: caracter no reconocido ...
```

Si existen errores sintácticos:

```python
if errores_sintacticos:

    print(f"\nErrores sintacticos ({len(errores_sintacticos)}):")

    for error in errores_sintacticos:

        print("  ", error)
```

Por ejemplo:

```text
Errores sintacticos (2):
   Linea 20: no esperaba '...' | Contenido: ...
   Linea 50: la entrada termino antes de tiempo | Contenido: ...
```

---

## 28. Manejo de excepciones

La lectura y procesamiento de los archivos se encuentra dentro de un bloque:

```python
try:

    # procesamiento de archivos

except Exception as e:

    print(f"Error leyendo archivos de entrada: {e}")

    raise SystemExit
```

Si ocurre un problema durante la lectura o procesamiento de los archivos, se muestra la información correspondiente y el programa finaliza.

---

## 29. Ejemplo de registro válido

Un ejemplo de un registro válido es:

```text
TABLE_DUMP2|1785888000|B|177.101.16.80|53046|7.0.0.0/8|53046 61626 14840 3356 749
```

Conceptualmente, el lexer genera una secuencia de tokens similar a:

```text
TABLE_DUMP2
PIPE
TIMESTAMP
PIPE
STATE
PIPE
IP
PIPE
AS_NUMBER
PIPE
PREFIX
PIPE
AS_NUMBER
AS_NUMBER
AS_NUMBER
AS_NUMBER
AS_NUMBER
```

Posteriormente el parser comprueba esta secuencia contra las producciones definidas.

Si coincide con la gramática, la línea es aceptada.

---

## 30. Ejemplos de errores sintácticos

### Campo faltante

Por ejemplo:

```text
TABLE_DUMP2|1785888000|B|177.101.16.80|53046|53046 61626
```

En este registro falta el campo correspondiente al:

```text
PREFIX
```

por lo tanto, la estructura no coincide con la producción principal.

---

### Orden incorrecto

Por ejemplo:

```text
TABLE_DUMP2|B|1785888000|177.101.16.80|53046|7.0.0.0/8|53046
```

En este caso el `STATE` aparece antes del `TIMESTAMP`.

La gramática espera:

```text
TABLE_DUMP2 PIPE TIMESTAMP PIPE STATE
```

por lo que el registro no cumple el orden definido.

---

### `AS_PATH` faltante

Por ejemplo:

```text
TABLE_DUMP2|1785888000|B|177.101.16.80|53046|7.0.0.0/8|
```

La gramática espera que `as_path` comience con al menos un valor numérico.

Al no encontrarlo, la entrada termina antes de completar la producción.

---

## 31. Alcance actual del Entregable 3

En esta etapa se implementa la validación de la **estructura sintáctica general de cada registro MRT**.

El programa permite:

- Reconocer los tokens definidos.
- Validar direcciones IPv4.
- Validar el formato de los prefijos.
- Reconocer los estados BGP.
- Reconocer los valores numéricos.
- Reconocer los separadores `PIPE`.
- Validar la estructura general de una línea.
- Verificar el orden de los campos.
- Comprobar la presencia del `AS_PATH`.
- Exigir al menos un valor en el `AS_PATH`.
- Procesar un `AS_PATH` con diferente cantidad de elementos.
- Detectar errores léxicos.
- Detectar errores sintácticos.
- Detectar registros incompletos.
- Procesar múltiples archivos `chunk_*.txt`.
- Contabilizar las líneas correctamente parseadas.

En esta versión todavía **no se crean dinámicamente las estructuras de datos utilizadas por la aplicación final**, debido a que esa funcionalidad corresponde a la siguiente etapa del proyecto.

---

## 32. Estructura del Entregable 3

La estructura general del proyecto es similar a:

```text
Proyecto_1/
│
├── Datos/
│   └── Chunks/
│       ├── chunk_aa.txt
│       ├── chunk_ab.txt
│       ├── chunk_ac.txt
│       └── ...
│
└── Entregable_3/
    │
    ├── analizador_sintactico_final.py
    ├── README.md
    │
    ├── [prototipo de Alison]
    ├── [prototipo de Brandon]
    └── [prototipo de Sebas]
```

Los archivos correspondientes a Alison, Brandon y Sebas representan **prototipos individuales desarrollados durante el proceso de construcción del parser**.

Estos archivos permiten conservar evidencia de las diferentes propuestas realizadas antes de integrar la solución.

El archivo:

```text
analizador_sintactico_final.py
```

corresponde a la **implementación final unificada del equipo** y es el archivo que debe utilizarse para ejecutar el Entregable 3.

---

## 33. Requisitos

Para ejecutar el proyecto es necesario tener instalado:

- **Python 3**
- **PLY**

PLY puede instalarse utilizando:

```bash
pip install ply
```

Para comprobar la instalación de Python:

```bash
python --version
```

En algunos sistemas puede utilizarse:

```bash
python3 --version
```

---

## 34. Ejecución del programa

El archivo que debe ejecutarse es:

```text
analizador_sintactico_final.py
```

### Opción 1: desde la raíz del repositorio

Ejecutar:

```bash
python Proyecto_1/Entregable_3/analizador_sintactico_final.py
```

En sistemas que utilizan `python3`:

```bash
python3 Proyecto_1/Entregable_3/analizador_sintactico_final.py
```

---

### Opción 2: desde la carpeta `Entregable_3`

Primero ubicarse en:

```text
Proyecto_1/Entregable_3/
```

Luego ejecutar:

```bash
python analizador_sintactico_final.py
```

o:

```bash
python3 analizador_sintactico_final.py
```

El programa buscará automáticamente los archivos:

```text
Proyecto_1/Datos/Chunks/chunk_*.txt
```

por lo que no es necesario indicar manualmente cada archivo de entrada.

> Los archivos individuales correspondientes a Alison, Brandon y Sebas son prototipos de desarrollo y **no deben utilizarse para realizar la ejecución final del entregable**.

---

## 35. Salida esperada

Después de procesar los chunks, el programa muestra un resumen similar a:

```text
Archivos leidos con exito: 5
Lineas parseadas correctamente: 2500000/2500000
```

La cantidad exacta dependerá de los archivos presentes en la carpeta `Datos/Chunks`.

Si existen errores léxicos se mostrará:

```text
Errores lexicos (N):

   Linea X: caracter no reconocido ...
```

Si existen errores sintácticos se mostrará:

```text
Errores sintacticos (N):

   Linea X: no esperaba '...' | Contenido: ...
```

También pueden reportarse registros que terminan antes de completar la estructura esperada:

```text
Linea X: la entrada termino antes de tiempo | Contenido: ...
```

---

## 36. Flujo general del programa

El procesamiento puede representarse de la siguiente manera:

```text
Archivos chunk_*.txt
        |
        v
Lectura línea por línea
        |
        v
      Lexer
        |
        v
Secuencia de tokens
        |
        v
      Parser
        |
        +-----------------------+
        |                       |
        v                       v
  Línea válida           Error sintáctico
        |                       |
        v                       v
 lineas_ok++          errores_sintacticos[]
```

Los errores léxicos son detectados y registrados durante la etapa correspondiente al lexer.

---

## 37. Organización del trabajo del Entregable 3

Durante el desarrollo del Entregable 3 se realizaron actividades de análisis, propuesta de solución, comprensión del parser, preparación de la presentación, documentación y unificación del código final.

Entre los aportes registrados durante esta etapa se encuentran:

| Fecha | Integrante | Aporte |
|---|---|---|
| 07/09/2026 | Sebastian Varela Vargas | Entendimiento del entregable y propuesta de solución completa para el Entregable 3. |
| 07/09/2026 | Alison Lobo Salas | Entendimiento del entregable y propuesta de solución completa para el Entregable 3. |
| 07/09/2026 | Brandon Arias Sandoval | Participación en la propuesta de solución del Entregable 3. |
| 09/09/2026 | Todo el equipo | Revisión y entendimiento del código del parser. |
| 10/09/2026 | Sebastian Varela Vargas | Creación de la presentación para el Entregable 3. |
| 12/09/2026 | Alison Lobo Salas | Creación y documentación del archivo README. |
| 12/09/2026 | Brandon Arias Sandoval | Unificación del código final del Entregable 3. |

Los prototipos individuales fueron utilizados como parte del proceso de análisis y posteriormente se realizó la integración de la solución final.

---

## 38. Resultado del Entregable 3

Con la implementación final se obtiene un analizador capaz de:

- Reconocer los principales componentes de los registros MRT.
- Validar direcciones IPv4.
- Reconocer prefijos IPv4.
- Identificar estados BGP.
- Reconocer valores numéricos.
- Reconocer los separadores entre campos.
- Procesar los tokens mediante un analizador sintáctico.
- Validar la estructura general de cada registro.
- Verificar el orden de los campos.
- Procesar un `AS_PATH` de longitud variable.
- Requerir al menos un elemento en el `AS_PATH`.
- Detectar caracteres no reconocidos.
- Registrar errores léxicos.
- Detectar tokens inesperados.
- Detectar registros incompletos.
- Registrar errores sintácticos.
- Procesar automáticamente múltiples archivos `chunk_*.txt`.
- Contabilizar las líneas aceptadas por el parser.
- Mostrar un resumen del procesamiento realizado.

Los archivos individuales desarrollados por los integrantes representan el proceso de construcción y prueba de la solución.

La implementación integrada utilizada para la entrega se encuentra en:

```text
analizador_sintactico_final.py
```

El resultado de este entregable constituye la etapa de **análisis sintáctico** del proyecto y prepara el programa para las siguientes fases, en las cuales se incorporará la creación dinámica de las estructuras de datos requeridas por la aplicación.
