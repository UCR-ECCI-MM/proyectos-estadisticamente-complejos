# Proyecto: Analizador de datos BGP

## Entregable 5

### Integrantes

- Brandon Arias Sandoval
- Alison Lobo Salas
- Sebastian Varela Vargas

---

## 1. Descripción

Este proyecto implementa un analizador para archivos de datos BGP (Border Gateway Protocol).

A partir de la información procesada por el analizador léxico y sintáctico, se construyen diferentes estructuras de datos que permiten consultar información relacionada con:

- Prefijos de red.
- Sistemas Autónomos (AS).
- Peer AS.
- Peer IP.
- AS Paths.
- Rutas disponibles entre prefijos.

Para facilitar la interacción con el usuario, se implementó una aplicación mediante un menú en consola que permite acceder a las tres funcionalidades principales del proyecto.

---

## 2. Estructura general de la aplicación

La aplicación se divide principalmente en dos componentes:

### `parser.py`

Se encarga de leer y procesar los archivos de entrada utilizando el analizador léxico y sintáctico.

Durante el procesamiento se construyen las estructuras de datos necesarias para las tres funcionalidades.

La función:

`cargar_datos()`

retorna las estructuras:

- `datos_func_1`
- `datos_func_2`
- `datos_func_3`

Estas estructuras son utilizadas posteriormente por la aplicación para realizar las consultas.

### `app.py`

Contiene la interfaz de consola de la aplicación.

Desde este archivo el usuario puede seleccionar cualquiera de las tres funcionalidades mediante el menú principal:

1. Funcionalidad 1
2. Funcionalidad 2
3. Funcionalidad 3
0. Salir

---

# 3. Funcionalidad 1: Consulta de prefijos y AS de origen

La funcionalidad 1 permite analizar los Sistemas Autónomos de origen asociados a los prefijos encontrados durante el procesamiento de los datos.

Para esta funcionalidad se utiliza una estructura que relaciona cada prefijo con los AS de origen que lo reportaron.

Conceptualmente:

Prefijo → AS de origen

Ejemplo:

192.0.2.0/24 → {AS100, AS200}

La funcionalidad cuenta con un submenú con dos opciones.

## 3.1 Consultar el AS de origen de un prefijo

El usuario ingresa un prefijo y la aplicación muestra los AS de origen asociados.

Ejemplo:

Prefijo:

192.0.2.0/24

Salida:

AS de origen:
1. AS 100
2. AS 200

## 3.2 Mostrar prefijos con múltiples AS de origen

La segunda opción permite identificar todos los prefijos que presentan dos o más AS de origen distintos.

Para esto se filtra la estructura de datos seleccionando únicamente aquellos prefijos cuya cantidad de AS de origen sea mayor o igual a dos.

---

# 4. Funcionalidad 2: Consulta de un Sistema Autónomo (AS)

La funcionalidad 2 permite consultar un Peer AS y obtener información sobre sus aristas, los prefijos conocidos a través de ellas y sus respectivos AS Paths.

La estructura utilizada sigue la siguiente organización:

Peer AS
└── Peer IP (arista)
    └── Rutas
        ├── Prefijo
        └── AS Path

Cada `Peer IP` representa una arista asociada al Peer AS.

Para cada arista se almacena una lista de rutas, donde cada ruta contiene:

- El prefijo.
- El AS Path asociado.

Conceptualmente:

Peer AS → Peer IP → Prefijo + AS Path

## Funcionamiento

El usuario ingresa el número de un AS.

La aplicación:

1. Valida que el valor ingresado sea numérico.
2. Busca el AS en la estructura de datos.
3. Obtiene todos los Peer IP asociados.
4. Muestra la cantidad total de aristas.
5. Muestra los Peer IP correspondientes a dichas aristas.
6. Para cada arista, muestra los prefijos conocidos y sus AS Paths.
7. Muestra la cantidad total de rutas asociadas a cada arista.

Ejemplo de salida:

AS consultado: 6057

Total de aristas: 1

Aristas encontradas:
1. 192.XXX.XXX.XXX

Al continuar con la consulta:

PREFIJO                 AS PATH
158.146.32.0/22         6057 -> 15830 -> 63255
158.162.120.0/22        6057 -> 6461 -> 8657 -> 15525

Total de rutas por esta arista: 229204

Debido a que algunos AS contienen una gran cantidad de rutas, la aplicación realiza una pausa antes de desplegar todos los prefijos y AS Paths.

---

# 5. Funcionalidad 3: Rutas disponibles entre dos prefijos

La funcionalidad 3 permite consultar las rutas disponibles entre dos prefijos utilizando los AS Paths almacenados durante el procesamiento.

El usuario proporciona:

- Prefijo A
- Prefijo B

Primero se obtienen los AS de origen asociados a ambos prefijos utilizando la información generada para la funcionalidad 1.

Posteriormente, se consultan los AS Paths conocidos hacia el prefijo B.

Para considerar un AS Path como una ruta válida entre ambos prefijos se comprueba que:

1. Alguno de los AS de origen del prefijo A aparezca dentro del AS Path.
2. El AS Path termine en alguno de los AS de origen correspondientes al prefijo B.

Las rutas que cumplen ambas condiciones se almacenan evitando duplicados.

Finalmente, la aplicación muestra todas las rutas encontradas.

Ejemplo conceptual:

Prefijo A
   ↓
AS de origen A
   ↓
AS intermedios
   ↓
AS de origen B
   ↓
Prefijo B

La salida se presenta de la siguiente forma:

Prefijo A -> AS1 -> AS2 -> AS3 -> Prefijo B

Además, se muestra el número total de rutas encontradas.

---

# 6. Funciones auxiliares

## `formatear_as_path()`

Convierte una lista de números de AS en una representación más legible.

Por ejemplo:

[6057, 15830, 63255]

se muestra como:

6057 -> 15830 -> 63255

## `pausar()`

Detiene temporalmente la ejecución hasta que el usuario presiona ENTER.

Esto permite que el usuario pueda revisar los resultados antes de regresar al menú.

---

# 7. Ejecución

Para ejecutar la aplicación se utiliza:

python app.py

Al iniciar, la aplicación carga y procesa los datos:

Cargando y procesando los chunks, esto puede tardar...

Una vez finalizado el procesamiento se muestra:

Datos cargados con exito.

Posteriormente se presenta el menú principal:

==================== MENU ====================

1. Funcionalidad 1
2. Funcionalidad 2
3. Funcionalidad 3
0. Salir

==============================================

El usuario puede seleccionar la funcionalidad que desea consultar.

---

# 8. Validaciones

La aplicación contempla diferentes casos durante las consultas:

- Validación de que el número de AS ingresado sea numérico.
- Verificación de la existencia del AS solicitado.
- Verificación de la existencia de los prefijos ingresados.
- Manejo de prefijos sin información disponible.
- Manejo de consultas donde no existen rutas conocidas.
- Eliminación de rutas duplicadas en la funcionalidad 3.

---

# 9. Distribución del trabajo

## Brandon Arias Sandoval

- Desarrollo de la funcionalidad 1.
- Implementación de las consultas relacionadas con prefijos y AS de origen.
- Creación de la interfaz principal de la aplicación.
- Integración de la funcionalidad 1 con el menú de la aplicación.

## Alison Lobo Salas

- Desarrollo de la funcionalidad 2.
- Organización de los datos por Peer AS y Peer IP.
- Implementación de la consulta de aristas de un AS.
- Visualización de los prefijos y AS Paths asociados a cada arista.
- Integración de la funcionalidad 2 con la aplicación.

## Sebastian Varela Vargas

- Desarrollo de la funcionalidad 3.
- Implementación de la consulta de rutas entre dos prefijos.
- Uso de los AS de origen y AS Paths para determinar las rutas disponibles.
- Integración de la funcionalidad 3 con la aplicación.

## Trabajo grupal

- Discusión y definición de las estructuras de datos utilizadas.
- Revisión de las funcionalidades propuestas.
- Integración de las tres funcionalidades.
- Pruebas de la aplicación.
- Revisión de resultados y preparación del entregable.

---

# 10. Resumen de las estructuras utilizadas

Las tres funcionalidades pueden resumirse de la siguiente manera:

Funcionalidad 1:

Prefijo → AS de origen

Funcionalidad 2:

Peer AS → Peer IP (arista) → Prefijo + AS Path

Funcionalidad 3:

Prefijo → Peer AS → AS Paths

Estas estructuras permiten almacenar la información obtenida durante el parseo una sola vez y posteriormente realizar las consultas desde la aplicación.
