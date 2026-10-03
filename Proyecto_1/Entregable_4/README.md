# Proyecto 1 – Rutas en Internet (Entregable 4)

Computabilidad y Complejidad – CI0124, II-2026
Prof. Maureen Murillo R.

Equipo: Brandon Arias Sandoval, Alison Lobo Salas y Sebastián Varela Vargas

## Descripción

Este entregable agrega, sobre el analizador léxico y sintáctico de las entregas anteriores, la **creación dinámica de las estructuras de datos** de la aplicación. Mientras el programa lee el dump de MRT línea por línea, cada línea válida se usa para llenar tres estructuras, una por cada funcionalidad:

1. **Funcionalidad 1:** prefijos y los AS que los originan, para detectar posibles casos de *prefix hijacking*.
2. **Funcionalidad 2:** consulta por Sistema Autónomo (AS), con sus aristas (Peer IP) y los prefijos y AS Path conocidos por cada arista.
3. **Funcionalidad 3:** rutas por prefijo, agrupadas por Peer AS, para poder encontrar las rutas entre dos prefijos sin recorrer todo el dump.

Al terminar, el programa imprime un resumen de lo leído, los errores encontrados y una muestra de cada estructura. Las consultas interactivas de la aplicación completa se implementan en la entrega final.

## Requisitos

- Python 3.8 o superior
- Paquete **PLY** (Python Lex-Yacc)

```
pip install ply
```

No se necesitan más paquetes; el resto (`os`, `glob`) es de la biblioteca estándar.

## Estructura de carpetas esperada

El programa busca los datos con una ruta relativa a la ubicación del script (no depende del usuario ni de la computadora), por lo que la carpeta del proyecto debe verse así:

```
Proyecto_1/
├── Datos/
│   └── Chunks/
│       ├── chunk_aa.txt
│       ├── chunk_ab.txt
│       └── ...            (archivos chunk_*.txt con el dump de MRT)
└── Entregable_4/
    ├── parser_final.py    <- programa a ejecutar
    └── README.md
```

Se leen **todos** los archivos que coincidan con `Datos/Chunks/chunk_*.txt`, en orden alfabético. Si no se encuentra ninguno, el programa muestra `No se encontraron archivos chunk_*.txt` y termina.

## Cómo ejecutarlo

Desde la carpeta `Entregable_4`:

```
python parser_final.py
```

Al correrlo por primera vez, PLY genera automáticamente los archivos `parser.out` y `parsetab.py` en esa misma carpeta; no hay que crearlos ni editarlos.

## Formato de entrada

Cada línea del dump tiene siete campos separados por `|`:

```
TABLE_DUMP2|1785888000|B|177.101.16.80|53046|7.0.0.0/8|53046 61626 14840 3356 749
```

## Qué hace el programa

1. **Lee** todos los archivos `chunk_*.txt`.
2. **Analizador léxico:** convierte cada línea en tokens (`TABLE_DUMP2`, `PIPE`, `TIMESTAMP`, `STATE`, `IP`, `PREFIX`, `AS_NUMBER`). Si aparece un carácter no reconocido, lo registra en la lista de errores léxicos y sigue.
3. **Analizador sintáctico (PLY):** verifica que los campos estén completos y en el orden correcto, y que el AS Path tenga al menos un AS. Si una línea es incorrecta, la registra en la lista de errores sintácticos y continúa con la siguiente.
4. **Estructuras de datos:** por cada línea válida llama a `funcionalidad_1`, `funcionalidad_2` y `funcionalidad_3`.
5. **Imprime** el resumen final.

## Estructuras de datos

**Funcionalidad 1 – `funcionalidad_1_datos`**

```python
{ prefijo: [AS_origen, ...] }
# "8.8.8.0/24": [15169, 64512]
```

El AS de origen es el último AS del AS Path. No se repiten orígenes. Un prefijo con más de un origen es una anomalía a reportar.

**Funcionalidad 2 – `datos_por_as`**

```python
{ peer_as: { peer_ip: [ {"prefijo": ..., "as_path": [...]}, ... ] } }
# 53046: {"177.101.16.80": [{"prefijo": "7.0.0.0/8", "as_path": [53046, 61626, 14840, 3356, 749]}]}
```

Permite ir de un AS a sus aristas (Peer IP) y de cada arista a los prefijos con su AS Path, sin recorrer todos los registros.

**Funcionalidad 3 – `datos_funcionalidad_3`**

```python
{ prefijo: { peer_as: [as_path, ...] } }
# "7.0.0.0/8": {53046: [[53046, 61626, 14840, 3356, 749]]}
```

Agrupa las rutas por prefijo y por Peer AS, de modo que las rutas de un prefijo hacia un AS dado se obtienen con dos accesos a diccionario.

## Salida del programa

- Cantidad de archivos leídos y líneas parseadas correctamente (`lineas_ok/total_lineas`).
- Errores léxicos y sintácticos, cada uno con el número de línea y su contenido.
- **Funcionalidad 1:** cantidad de prefijos distintos, cantidad de prefijos con más de un origen y una tabla de muestra (7 con múltiples orígenes y 7 con un único origen).
- **Funcionalidad 2:** cantidad de Peer AS distintos, la lista de Peer AS encontrados y el top 5 de AS con más rutas (número de aristas y de rutas).
- **Funcionalidad 3:** cantidad de prefijos distintos y un ejemplo de las estructuras creadas para los dos primeros prefijos.

## Otros archivos de la carpeta

| Archivo | Descripción |
|---------|-------------|
| `parser_final.py` | Versión final del entregable (léxico, sintáctico y estructuras). |
| `estructura_datos_brandon.py` | Borrador de trabajo de la funcionalidad 1. |
| `estructura_datos_alison.py` | Borrador de trabajo de las funcionalidades 1 y 2. |
| `estructura_datos_sebas.py` | Borrador de trabajo de la funcionalidad 3. |
| `parser.out`, `parsetab.py` | Generados automáticamente por PLY. |

Los archivos `estructura_datos_*.py` son borradores individuales previos a la integración y no forman parte de la ejecución.
