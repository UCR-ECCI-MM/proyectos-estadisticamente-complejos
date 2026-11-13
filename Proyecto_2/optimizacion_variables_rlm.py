"""
Script principal: corre los metodos de seleccion de variables y
compara sus mejores soluciones:
    - algoritmo genetico (metaheuristica)
    - stepwise (heuristica)
    - fuerza bruta

Estructura:

                    ┌──> stepwise.py ────────────┐
    datos_r2.py ────┼──> algoritmo_genetico.py ──┼──> optimizacion_variables_rlm.py
                    └──> fuerza_bruta.py ────────┘
"""
import pandas as pd

from algoritmo_genetico import correr_algoritmo_genetico

# DATOS FINALES
resultados = {}


if __name__ == "__main__":

    # METAHEURISTICA: ALGORITMO GENETICO

    # (no_poblacion, porc_progenitores, no_generaciones, prob_mutacion,
    #  prob_cruce, paciencia, tolerancia, elitismo, tam_torneo)
    parametros_1 = (50, 0.5, 50, 0.012, 0.9, 5, 1e-3, 0.05, 3)
    parametros_2 = (100, 0.5, 50, 0.012, 0.9, 5, 1e-3, 0.05, 3)
    parametros_3 = (50, 0.5, 50, 0.03, 0.9, 5, 1e-3, 0.05, 3)
    parametros_4 = (50, 0.3, 50, 0.012, 0.8, 5, 1e-3, 0.10, 5)
    parametros_5 = (50, 0.7, 50, 0.012, 0.9, 10, 1e-4, 0.02, 2)

    matriz_parametros = [parametros_1, parametros_2, parametros_3, parametros_4, parametros_5]

    resultados_genetico = correr_algoritmo_genetico(matriz_parametros, semilla=42)

    tabla_genetico = pd.DataFrame.from_dict(
        resultados_genetico,
        orient="index",
        columns=["modelos_evaluados", "generaciones", "tiempo_s",
                 "generacion_mejor", "r2_ajustado", "variables", "ganador"],
    )
    print(tabla_genetico.drop(columns="variables").to_string())

    ganador = max(resultados_genetico, key=lambda p: resultados_genetico[p][4])
    resultados["Algoritmo Genetico"] = resultados_genetico[ganador][:6]

    # HEURISTICA: STEPWISE

    # FUERZA BRUTA

    # RESULTADOS FINALES
