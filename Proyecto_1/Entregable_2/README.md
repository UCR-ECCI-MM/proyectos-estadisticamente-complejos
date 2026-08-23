# Proyecto 1 — Entregable 2

## Analizador Léxico de datos MRT utilizando PLY

Este entregable corresponde a la implementación de un **analizador léxico (lexer)** para archivos MRT. El objetivo es leer los archivos de datos previamente divididos en *chunks*, identificar los diferentes componentes presentes en cada línea y transformarlos en una secuencia de **tokens**.

La implementación fue realizada en **Python** utilizando la biblioteca **PLY (Python Lex-Yacc)**, específicamente el módulo `ply.lex`.

---

## 1. Objetivo del entregable

El objetivo principal del Entregable 2 es realizar el **análisis léxico de los archivos MRT**, definiendo expresiones regulares capaces de reconocer los elementos que componen cada registro.

El lexer procesa cada archivo `chunk_*.txt`, identifica los tokens definidos, detecta posibles errores léxicos y genera archivos con los resultados del procesamiento.

De esta manera, los datos originales quedan convertidos en una secuencia de tokens que podrá ser utilizada posteriormente en las siguientes etapas del proyecto.

---

## 2. Reunión de coordinación — 20/08/2026

Durante la reunión del **20 de agosto de 2026** se revisaron los requerimientos correspondientes al Entregable 2.

Como parte de la reunión, se analizó la estructura del archivo MRT para determinar cuáles elementos debían ser reconocidos por el analizador léxico.

Posteriormente, se distribuyó entre los integrantes del equipo la implementación de las funciones y expresiones regulares necesarias para reconocer cada componente.

La distribución realizada fue la siguiente:

| Elemento             | Integrante |       |
| -------------------- | ---------- | ----- |
| `TABLE_DUMP2`        | Alison     |       |
| Timestamp            | Brandon    |       |
| State                | Sebas      |       |
| Fragmento de IP      | Alison     |       |
| Dígito               | Brandon    |       |
| Línea vertical (`    | `)         | Sebas |
| Salto de línea       | Alison     |       |
| Longitud del prefijo | Sebas      |       |

Después de integrar las diferentes partes desarrolladas por el equipo, se construyó el lexer utilizado para procesar los archivos completos.

---

## 3. Tecnologías utilizadas

El proyecto utiliza las siguientes bibliotecas de Python:

```python
import os
import glob
from collections import Counter
import ply.lex as lex
```

### `os`

Se utiliza para trabajar con rutas y carpetas del sistema operativo. Permite construir rutas relativas al proyecto, evitando depender de una ruta específica de una computadora.

### `glob`

Permite buscar automáticamente todos los archivos que cumplan con un determinado patrón. En este proyecto se utiliza para localizar los archivos:

```text
chunk_*.txt
```

### `Counter`

Se utiliza para contar la cantidad de tokens encontrados de cada tipo durante el análisis.

### `ply.lex`

Corresponde al módulo de PLY utilizado para construir el analizador léxico a partir de las expresiones regulares y funciones definidas.

---

## 4. Tokens definidos

El lexer utiliza los siguientes tokens:

```python
tokens = (
    'TABLE_DUMP2',
    'STATE',
    'IP',
    'PREFIX',
    'NUMBER',
    'PIPE',
    'NEWLINE'
)
```

Cada token representa un elemento diferente presente en los registros MRT.

| Token         | Descripción                                      | Ejemplo          |   |
| ------------- | ------------------------------------------------ | ---------------- | - |
| `TABLE_DUMP2` | Identificador del tipo de registro               | `TABLE_DUMP2`    |   |
| `STATE`       | Estado del registro BGP                          | `B`, `A` o `W`   |   |
| `IP`          | Dirección IPv4                                   | `186.211.128.34` |   |
| `PREFIX`      | Dirección IPv4 acompañada de longitud de prefijo | `82.255.64.0/19` |   |
| `NUMBER`      | Valor numérico presente en el registro           | `14840`          |   |
| `PIPE`        | Separador de campos                              | `                | ` |
| `NEWLINE`     | Salto de línea                                   | `\n`             |   |

---

## 5. Reconocimiento de `TABLE_DUMP2`

La siguiente expresión regular identifica directamente la palabra `TABLE_DUMP2`:

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

## 6. Reconocimiento del separador `PIPE`

Los campos de los registros MRT se encuentran separados mediante el carácter:

```text
|
```

Este carácter es reconocido utilizando:

```python
t_PIPE = r'\|'
```

La barra invertida permite indicar que `|` debe interpretarse como un carácter literal dentro de la expresión regular.

---

## 7. Reconocimiento del estado

Los estados permitidos se reconocen mediante:

```python
t_STATE = r'[BAW]{1}'
```

Esto permite reconocer uno de los siguientes caracteres:

```text
B
A
W
```

Estos valores corresponden a los estados utilizados en los registros procesados.

---

## 8. Espacios y tabulaciones

El lexer ignora espacios y tabulaciones mediante:

```python
t_ignore = ' \t'
```

Esto es importante porque algunos campos, como los AS presentes en un AS Path, pueden estar separados por espacios.

Los espacios no generan tokens y únicamente se utilizan como separación entre los diferentes números.

---

## 9. Reconocimiento de direcciones IPv4

Una dirección IPv4 está formada por **cuatro octetos separados por puntos**.

Por ejemplo:

```text
186.211.128.34
```

Cada octeto puede contener un valor entre:

```text
0 y 255
```

Para validar este rango se utiliza:

```python
OCTET = r'(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])(?![0-9])'
```

La expresión se divide de la siguiente manera:

| Expresión     | Valores reconocidos |
| ------------- | ------------------- |
| `25[0-5]`     | 250–255             |
| `2[0-4][0-9]` | 200–249             |
| `1[0-9]{2}`   | 100–199             |
| `[1-9]?[0-9]` | 0–99                |

Posteriormente se combinan cuatro octetos separados por puntos:

```python
IP_REGEX = (
    OCTET + r'\.' +
    OCTET + r'\.' +
    OCTET + r'\.' +
    OCTET
)
```

Por ejemplo:

```text
186.211.128.34
```

es reconocido como:

```text
IP
```

La función utilizada por PLY es:

```python
@lex.TOKEN(IP_REGEX)
def t_IP(t):
    return t
```

---

## 10. Reconocimiento de prefijos

Un prefijo está compuesto por una dirección IPv4 seguida por `/` y la longitud de la máscara.

Por ejemplo:

```text
82.255.64.0/19
```

La longitud de máscara se reconoce mediante:

```python
MASK = r'(?:3[0-2]|[12][0-9]|[1-9])(?![1-9])'
```

Posteriormente se combina la dirección IP con la máscara:

```python
PREFIX_REGEX = IP_REGEX + r'/' + MASK
```

Por lo tanto:

```text
82.255.64.0/19
```

se reconoce como un token:

```text
PREFIX
```

La regla utilizada por PLY es:

```python
@lex.TOKEN(PREFIX_REGEX)
def t_PREFIX(t):
    return t
```

La regla de `PREFIX` se define antes que la regla de `IP`, ya que un prefijo comienza precisamente con una dirección IP. Esto permite que el lexer reconozca correctamente la expresión completa como un `PREFIX`.

---

## 11. Reconocimiento de números

Los valores numéricos son reconocidos mediante:

```python
def t_NUMBER(t):
    r'\d+'
```

Una vez reconocido el número, su valor se convierte de texto a entero:

```python
t.value = int(t.value)
```

También se realiza una validación para evitar valores superiores a:

```text
4294967295
```

La validación implementada es:

```python
if t.value > 4294967295:
    print(
        f"Error de lexer en linea {t.lineno}: "
        f"Fuera de rango (max 4294967295): {t.value}"
    )
    return None
```

Si el número supera este límite, no se devuelve como un token válido.

---

## 12. Reconocimiento de saltos de línea

Los saltos de línea se reconocen mediante:

```python
def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    return t
```

La expresión:

```text
\n+
```

significa que se reconoce **uno o más saltos de línea consecutivos**.

Además, se actualiza:

```python
t.lexer.lineno
```

para mantener el número de línea que está procesando el lexer.

---

## 13. Manejo de errores léxicos

Los caracteres que no corresponden con ninguno de los tokens definidos son procesados mediante:

```python
errores = []

def t_error(t):
    errores.append(
        f"Linea {t.lexer.lineno}: "
        f"caracter no reconocido '{t.value[0]}'"
    )
    t.lexer.skip(1)
```

Cuando se encuentra un carácter no reconocido:

1. Se registra el número de línea.
2. Se guarda el carácter que produjo el error.
3. El lexer avanza una posición mediante `skip(1)`.
4. El análisis continúa con el resto del archivo.

Esto permite que un error no detenga completamente el procesamiento del chunk.

---

## 14. Creación del lexer

Una vez definidas todas las reglas, el lexer se construye mediante:

```python
lexer = lex.lex()
```

PLY utiliza las reglas y expresiones regulares previamente definidas para generar el analizador léxico.

---

## 15. Manejo de rutas

El programa utiliza rutas relativas a la ubicación del proyecto:

```python
carpeta_proyecto = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
```

Esto evita utilizar rutas absolutas asociadas a una computadora específica.

Los archivos de entrada se buscan dentro de:

```text
Datos/Chunks/
```

y los resultados se almacenan en:

```text
Datos/Chunks/resultados_lexer/
```

Si la carpeta de resultados no existe, el programa la crea automáticamente mediante:

```python
os.makedirs(carpeta_salida, exist_ok=True)
```

---

## 16. Búsqueda automática de chunks

El programa busca todos los archivos cuyo nombre cumpla el patrón:

```text
chunk_*.txt
```

mediante:

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

Esto permite procesar automáticamente múltiples chunks sin tener que especificar manualmente cada archivo.

Si no se encuentran archivos, el programa muestra:

```text
No se encontraron archivos chunk_*.txt
```

y finaliza la ejecución.

---

## 17. Procesamiento de los archivos

Cada chunk se procesa individualmente.

Para cada archivo se reinician:

* Los errores encontrados.
* El número de línea.
* El contador total de tokens.
* El contador total de líneas.
* El resumen de tokens del chunk.

Cada línea del archivo se envía al lexer mediante:

```python
lexer.input(linea)
```

Posteriormente se obtienen los tokens utilizando:

```python
token = lexer.token()
```

El proceso continúa hasta que:

```python
token is None
```

lo que indica que ya no existen más tokens en la línea actual.

---

## 18. Archivos generados

Para cada chunk procesado se genera un archivo de tokens.

Por ejemplo, si el archivo original es:

```text
chunk_aa.txt
```

el resultado será:

```text
tokens_chunk_aa.txt
```

El archivo contiene el valor de cada token reconocido:

```python
salida.write(
    f"{token.value}\n"
)
```

Por ejemplo, una línea original similar a:

```text
TABLE_DUMP2|1785888000|B|186.211.128.34|14840|82.255.64.0/19|14840 3356 12322
```

genera valores de tokens como:

```text
TABLE_DUMP2
|
1785888000
|
B
|
186.211.128.34
|
14840
|
82.255.64.0/19
|
14840
3356
12322
```

---

## 19. Archivos de errores

Cuando un chunk contiene errores léxicos, también se genera un archivo independiente.

Por ejemplo:

```text
errores_chunk_aa.txt
```

Este archivo contiene los errores encontrados junto con el número de línea correspondiente.

Si el archivo no contiene errores léxicos, no es necesario generar el archivo de errores.

---

## 20. Resumen de resultados

Después de procesar cada chunk, el programa muestra información como:

```text
============================================================
Archivo: chunk_aa.txt
Lineas analizadas: 500000
Tokens reconocidos: XXXXXXX
Errores lexicos: 0
No se encontraron errores lexicos.

Archivo generado: .../tokens_chunk_aa.txt
```

Esto permite verificar rápidamente si el procesamiento fue exitoso.

---

## 21. Resumen global de tokens

Además del conteo individual de cada chunk, se utiliza:

```python
resumen_global = Counter()
```

para acumular los resultados de todos los archivos procesados.

Al finalizar el programa se muestra un resumen como:

```text
Resumen global de tokens:

  IP: ...
  NEWLINE: ...
  NUMBER: ...
  PIPE: ...
  PREFIX: ...
  STATE: ...
  TABLE_DUMP2: ...
```

Esto permite conocer la cantidad total de tokens identificados durante el procesamiento completo de los datos.

---

## 22. Estructura esperada del proyecto

La estructura general utilizada por el programa es similar a:

```text
Proyecto_1/
│
├── Datos/
│   └── Chunks/
│       ├── chunk_aa.txt
│       ├── chunk_ab.txt
│       ├── chunk_ac.txt
│       │
│       └── resultados_lexer/
│           ├── tokens_chunk_aa.txt
│           ├── tokens_chunk_ab.txt
│           ├── tokens_chunk_ac.txt
│           └── errores_chunk_XX.txt
│
└── Entregable_2/
    └── [archivos Python del lexer]
```

La carpeta `resultados_lexer` se crea automáticamente durante la ejecución en caso de que todavía no exista.

---

## 23. Requisitos

Para ejecutar el proyecto es necesario tener instalado:

* Python 3
* PLY

PLY puede instalarse mediante:

```bash
pip install ply
```

---

## 24. Ejecución

Desde la terminal se debe ubicar el proyecto y ejecutar el archivo Python correspondiente al lexer.

Por ejemplo:

```bash
python Proyecto_1/Entregable_2/all_tokens.py
```

El nombre exacto del archivo puede variar según el archivo utilizado para integrar el lexer.

Al iniciar correctamente se mostrará:

```text
============================================================
ANALISIS LEXICO INICIADO
============================================================
```

Posteriormente se indicará la cantidad de chunks encontrados y se procesará cada uno de ellos.

Al finalizar aparecerá:

```text
============================================================
ANALISIS LEXICO FINALIZADO
============================================================
```

junto con la ubicación donde fueron almacenados los resultados.

---

## 25. Resultado del Entregable 2

Con esta implementación se obtiene un analizador léxico capaz de:

* Reconocer los principales componentes de los registros MRT.
* Validar direcciones IPv4.
* Reconocer prefijos IPv4.
* Identificar estados.
* Identificar valores numéricos.
* Reconocer separadores entre campos.
* Reconocer saltos de línea.
* Detectar caracteres no reconocidos.
* Registrar errores léxicos sin detener completamente el procesamiento.
* Procesar automáticamente múltiples archivos `chunk_*.txt`.
* Generar un archivo de tokens para cada chunk.
* Generar archivos con los errores encontrados.
* Contabilizar los tokens identificados tanto por chunk como globalmente.

El resultado de este entregable constituye la etapa de **análisis léxico** del proyecto y prepara la información para las etapas posteriores de procesamiento y análisis sintáctico.

