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
from pathlib import Path

from algoritmo_genetico import PARAMETROS, correr_algoritmo_genetico, tabla_genetico
from datos_r2 import nombres_variables
from fuerza_bruta import mejor_resultado_guardado, tabla_corridas
from stepwise import Stepwise

# DATOS FINALES
resultados = {}

carpeta_output = Path(__file__).resolve().parent / "output"


def bloque(titulo, datos):
    # un dict pasado a lineas "clave: valor"
    lineas = [f"\n--- {titulo} ---"]
    for clave, valor in datos.items():
        if clave == "variables":
            lineas.append(f"num variables: {len(valor)}")
            lineas.append(f"variables: {', '.join(valor)}")
        elif isinstance(valor, float):
            lineas.append(f"{clave}: {valor:.5f}")
        else:
            lineas.append(f"{clave}: {valor}")
    return lineas


def guardar(nombre, lineas):
    carpeta_output.mkdir(exist_ok=True)
    texto = "\n".join(lineas)
    (carpeta_output / nombre).write_text(texto, encoding="utf-8")
    return texto


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

    texto_genetico = tabla_genetico(resultados_genetico)

    ganador = max(resultados_genetico, key=lambda p: resultados_genetico[p][4])
    resultados["Algoritmo Genetico"] = resultados_genetico[ganador][:6]

    # HEURISTICA: STEPWISE

    sw = Stepwise()
    resultados_stepwise = {
        "forward": sw.forward(),
        "backward": sw.backward(),
        "ambos": sw.ambos(),
    }

    # cada uno es (vector, r2, tiempo, modelos), gana el de mayor r2
    ganador_sw = max(resultados_stepwise, key=lambda m: resultados_stepwise[m][1])
    resultados["Stepwise"] = resultados_stepwise[ganador_sw]

    # FUERZA BRUTA

    # Se lee el mejor resultado de los experimentos ya guardados en
    # resultados_fuerza_bruta/corridas_fuerza_bruta.csv (para generarlos
    # de nuevo: python fuerza_bruta.py). Es el optimo exacto sobre las
    # primeras k variables, con el mayor k que se completo.
    resultados["fuerza_bruta"] = mejor_resultado_guardado()

    # RESULTADOS FINALES

    # cada metodo guarda distinto, aqui se pasa todo al mismo formato
    ag = resultados["Algoritmo Genetico"]
    vector_sw, r2_sw, tiempo_sw, modelos_sw = resultados["Stepwise"]
    fb = resultados["fuerza_bruta"]

    finales = {
        "Algoritmo Genetico": {
            "r2 ajustado": ag[4],
            "modelos evaluados": ag[0],
            "tiempo (s)": ag[2],
            "generaciones": ag[1],
            "generacion del mejor": ag[3],
            "variables": ag[5],
        },
        f"Stepwise ({ganador_sw})": {
            "r2 ajustado": r2_sw,
            "modelos evaluados": modelos_sw,
            "tiempo (s)": tiempo_sw,
            "variables": nombres_variables[vector_sw.astype(bool)].tolist(),
        },
        "Fuerza bruta": {
            "r2 ajustado": fb["r2_ajustado"],
            "modelos evaluados": fb["modelos_evaluados"],
            "tiempo (s)": fb["tiempo_seg"],
            "variables": fb["variables"],
        },
    }

    # output/algoritmo_genetico.txt
    lineas = ["ALGORITMO GENETICO", "", texto_genetico]
    lineas += bloque("mejor configuracion", {**dict(zip(PARAMETROS, ganador)), **finales["Algoritmo Genetico"]})
    guardar("algoritmo_genetico.txt", lineas)

    # output/stepwise.txt
    lineas = ["STEPWISE"]
    for direccion, (vector, r2, tiempo, modelos) in resultados_stepwise.items():
        titulo = f"{direccion} (ganador)" if direccion == ganador_sw else direccion
        lineas += bloque(titulo, {
            "r2 ajustado": r2,
            "modelos evaluados": modelos,
            "tiempo (s)": tiempo,
            "variables": nombres_variables[vector.astype(bool)].tolist(),
        })
    guardar("stepwise.txt", lineas)

    # output/fuerza_bruta.txt
    lineas = ["FUERZA BRUTA (solo las primeras k variables del csv)", "", "Corridas:", tabla_corridas()]
    lineas += bloque("mejor corrida completa", finales["Fuerza bruta"])
    guardar("fuerza_bruta.txt", lineas)

    # output/output_final.txt
    lineas = ["COMPARACION FINAL"]
    for metodo, datos in finales.items():
        lineas += bloque(metodo, datos)

    mejor = max(finales, key=lambda m: finales[m]["r2 ajustado"])
    lineas.append(f"\nmejor: {mejor}  r2 ajustado = {finales[mejor]['r2 ajustado']:.5f}")

    print(guardar("output_final.txt", lineas))
    print(f"\nguardado en {carpeta_output}")

