# Proyecto 2 – Selección de variables en RLM

Computabilidad y Complejidad – CI0124, II-2026
Prof. Maureen Murillo R.

Equipo: Brandon Arias Sandoval y Paula Sofia Grell

## Descripción

El programa busca qué variables de `datos.csv` conviene usar en una regresión lineal múltiple
para predecir `critical_temp`. Un modelo es mejor si su **R² ajustado** es más alto.

Se comparan tres métodos: **fuerza bruta**, **stepwise** y **algoritmo genético**.
Cómo funciona cada uno se explica en el documento del proyecto.

## Requisitos

- Python 3.11 o superior
- Los paquetes de `requirements.txt` (en la raíz del repositorio):

```
pip install -r ../requirements.txt
```

## Estructura de carpetas

```
Proyecto_2/
├── datos.csv                      <- datos (81 variables + critical_temp)
├── datos_r2.py                    <- carga los datos y calcula el R² ajustado
├── fuerza_bruta.py
├── stepwise.py
├── algoritmo_genetico.py
├── graficos_fuerza_bruta.py       <- gráficos de la fuerza bruta
├── optimizacion_variables_rlm.py  <- programa principal
├── output/                        <- resultados finales
└── resultados_fuerza_bruta/       <- corridas y gráficos de la fuerza bruta
```

## Cómo se conectan los scripts

```
                ┌──> stepwise.py ────────────┐
datos_r2.py ────┼──> algoritmo_genetico.py ──┼──> optimizacion_variables_rlm.py ──> output/
                └──> fuerza_bruta.py ────────┘
```

- **`datos_r2.py`** es la base: carga los datos y tiene la función `r2_ajustado(vector)`.
  El vector es de 0 y 1 e indica qué variables entran al modelo.
- **Los tres métodos** importan esa función y sólo se encargan de buscar el mejor vector.
- **`optimizacion_variables_rlm.py`** llama a los tres métodos, pone sus resultados en un mismo
  formato y escribe los archivos de `output/`.

## Cómo ejecutarlo

Desde la carpeta `Proyecto_2`:

```
python optimizacion_variables_rlm.py
```

La fuerza bruta **no se vuelve a correr** aquí porque tarda horas. Se usa el resultado que
ya está guardado en `resultados_fuerza_bruta/`. Si se quiere repetir:

```
python fuerza_bruta.py
python graficos_fuerza_bruta.py
```

## Qué hace el programa

1. Carga los datos desde `datos_r2.py`.
2. Corre el algoritmo genético con 5 configuraciones y se queda con la mejor.
3. Corre stepwise en sus tres versiones (forward, backward y ambos) y se queda con la mejor.
4. Lee el mejor resultado guardado de la fuerza bruta.
5. Compara los tres métodos y guarda los resultados en `output/`.

## Salida del programa

| Archivo | Contenido |
|---------|-----------|
| `output/output_final.txt` | Comparación de los tres métodos y el ganador |
| `output/algoritmo_genetico.txt` | Resultados de las 5 configuraciones |
| `output/stepwise.txt` | Resultados de forward, backward y ambos |
| `output/fuerza_bruta.txt` | Resultados de cada corrida |
| `resultados_fuerza_bruta/` | CSV de corridas, gráficos y la estimación para las 81 variables |


