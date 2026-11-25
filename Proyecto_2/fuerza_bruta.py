"""
Fuerza bruta: seleccion de variables en RLM probando TODAS las combinaciones.

Idea:
    Con k variables hay 2^k - 1 modelos posibles (todas las combinaciones
    no vacias). La fuerza bruta los evalua todos con r2_ajustado y se queda
    con el de mayor R2 ajustado. Siempre encuentra el optimo exacto, pero
    el numero de modelos se duplica con cada variable nueva.

Como con las 81 variables del dataset es imposible (2^81 - 1 modelos),
se trabaja con las primeras k variables y se mide como crece el tiempo.
"""
import csv
import time
from pathlib import Path

import numpy as np

from datos_r2 import nombres_variables, r2_ajustado, total_variables


def fuerza_bruta(k, limite_seg=None):
    """
    Evalua todos los modelos no vacios que se pueden formar con las
    primeras k variables del dataset y retorna el mejor.

    k: cantidad de variables a considerar (de 1 a total_variables).
    limite_seg: tiempo maximo en segundos. Si se pasa, la busqueda se
        detiene y se retorna el mejor modelo encontrado hasta ese momento.
        None = sin limite.

    Retorna un diccionario con el formato acordado por el grupo, mas el
    campo "completada" (True si se evaluaron todas las combinaciones).
    """
    if not 1 <= k <= total_variables:
        raise ValueError(f"k debe estar entre 1 y {total_variables}")

    inicio = time.perf_counter()

    mejor_r2 = -np.inf      # R2 ajustado del mejor modelo encontrado
    mejor_vector = None     # vector de 0/1 del mejor modelo
    modelos_evaluados = 0
    completada = True

    # Cada numero entero m entre 1 y 2^k - 1 representa una combinacion:
    # su representacion binaria dice que variables entran al modelo.
    # Ejemplo con k = 3:
    #   m = 1 -> 001 -> solo la variable 0
    #   m = 5 -> 101 -> variables 0 y 2
    #   m = 7 -> 111 -> las tres variables
    # Empezar en 1 deja por fuera el modelo vacio (m = 0 -> 000).
    for m in range(1, 2 ** k):

        # r2_ajustado siempre espera 81 posiciones: las que estan fuera
        # de las primeras k quedan en 0.
        vector = np.zeros(total_variables, dtype=int)
        for i in range(k):
            vector[i] = (m >> i) & 1    # bit i de m: 1 = la variable i entra

        r2 = r2_ajustado(vector)
        modelos_evaluados += 1

        # Se reemplaza solo si es estrictamente mejor (en empate queda el primero)
        if r2 > mejor_r2:
            mejor_r2 = r2
            mejor_vector = vector

        # Limite de tiempo: se corta la busqueda si ya se paso
        if limite_seg is not None and time.perf_counter() - inicio > limite_seg:
            completada = m == 2 ** k - 1    # True solo si era la ultima
            break

    tiempo = time.perf_counter() - inicio

    # Traduce el vector a los nombres reales de las variables
    variables = nombres_variables[mejor_vector.astype(bool)].tolist()

    return {
        "r2_ajustado": float(mejor_r2),
        "variables": variables,
        "num_variables": len(variables),
        "tiempo_seg": tiempo,
        "modelos_evaluados": modelos_evaluados,
        "completada": completada,
    }


def correr_experimentos(plan, ruta_csv, limite_seg=None):
    """
    Corre la fuerza bruta para varios tamanos de k y guarda cada corrida
    como una fila del CSV.

    plan: lista de pares (k, repeticiones). Ejemplo: [(5, 3), (10, 2)]
        corre k = 5 tres veces y k = 10 dos veces.
    ruta_csv: archivo donde se guardan las corridas. Se crea de nuevo
        cada vez que se llama a esta funcion.
    limite_seg: limite de tiempo por corrida (ver fuerza_bruta).

    Cada fila se escribe apenas termina su corrida, asi que si el
    experimento se interrumpe no se pierde lo que ya se corrio.
    """
    columnas = ["k", "repeticion", "modelos_evaluados", "tiempo_seg",
                "mejor_r2_ajustado", "num_variables", "variables", "completada"]

    ruta_csv = Path(ruta_csv)
    ruta_csv.parent.mkdir(parents=True, exist_ok=True)

    with open(ruta_csv, "w", newline="") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(columnas)

        for k, repeticiones in plan:
            for repeticion in range(1, repeticiones + 1):
                r = fuerza_bruta(k, limite_seg)

                escritor.writerow([
                    k,
                    repeticion,
                    r["modelos_evaluados"],
                    r["tiempo_seg"],
                    r["r2_ajustado"],
                    r["num_variables"],
                    ";".join(r["variables"]),   # nombres separados por ;
                    r["completada"],
                ])
                archivo.flush()     # guarda la fila en disco de inmediato

                print(f"k={k:2d}  rep={repeticion}  "
                      f"modelos={r['modelos_evaluados']:>7}  "
                      f"tiempo={r['tiempo_seg']:9.2f} s  "
                      f"R2aj={r['r2_ajustado']:.5f}  "
                      f"vars={r['num_variables']}", flush=True)


if __name__ == "__main__":
    # Plan de experimentos:
    #   - k de 1 a 12: corridas cortas, 5 repeticiones cada una
    #   - k de 13 a 16: corridas mas largas, 3 repeticiones cada una
    #   - k = 18: una sola corrida, para comprobar despues si la
    #     extrapolacion hecha con k <= 16 predice bien su tiempo
    plan = ([(k, 5) for k in range(1, 13)]
            + [(k, 3) for k in range(13, 17)]
            + [(18, 1)])

    ruta = Path(__file__).resolve().parent / "resultados_fuerza_bruta" / "corridas_fuerza_bruta.csv"

    # Limite de 30 minutos por corrida para que ninguna se quede colgada
    correr_experimentos(plan, ruta, limite_seg=30 * 60)
