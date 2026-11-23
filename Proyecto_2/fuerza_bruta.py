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
import time

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


if __name__ == "__main__":
    # Prueba rapida con k pequeno
    for k in (1, 2, 3, 8):
        print(f"k = {k}:", fuerza_bruta(k))
