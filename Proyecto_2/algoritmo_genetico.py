"""
Metaheuristica: algoritmo genetico para seleccion de variables en RLM.
"""
import time

import numpy as np

from datos_r2 import nombres_variables, r2_ajustado, total_variables


class AlgoritmoGenetico:
    def __init__(self, no_poblacion, porc_progenitores, no_generaciones, prob_mutacion, prob_cruce, paciencia, tolerancia, elitismo, tam_torneo=3):
        if not 1 <= paciencia < no_generaciones:
            raise ValueError("paciencia debe ser menor a no_generaciones")
        if not 0 < porc_progenitores <= 1:
            raise ValueError("porc_progenitores debe estar entre 0 y 1")
        if not 0 <= elitismo <= 1:
            raise ValueError("elitismo debe estar entre 0 y 1")
        if not 2 <= tam_torneo <= no_poblacion:
            raise ValueError("tam_torneo debe estar entre 2 y no_poblacion")

        self.no_poblacion = no_poblacion
        self.no_progenitores = int(round(porc_progenitores * no_poblacion))
        self.no_generaciones = no_generaciones
        self.prob_mutacion = prob_mutacion
        self.prob_cruce = prob_cruce
        self.paciencia = paciencia
        self.tolerancia = tolerancia
        self.no_elite = int(round(elitismo * no_poblacion))
        self.tam_torneo = tam_torneo

        if self.no_progenitores < 2:
            raise ValueError("se necesitan al menos 2 progenitores")

        self.cache = {}  # r2 de los individuos ya evaluados

    def poblacion_inicial(self):
        # vectores aleatorios, sin repetidos y sin filas en cero
        poblacion = np.empty((0, total_variables), dtype=int)

        while len(poblacion) < self.no_poblacion:
            faltan = self.no_poblacion - len(poblacion)
            nuevos = np.random.randint(0, 2, size=(faltan, total_variables))

            poblacion = np.vstack([poblacion, nuevos])
            poblacion = poblacion[poblacion.sum(axis=1) > 0]
            poblacion = np.unique(poblacion, axis=0)

        np.random.shuffle(poblacion)
        self.poblacion = poblacion
        return poblacion

    def evaluar_poblacion(self):
        fitness = []
        for individuo in self.poblacion:
            clave = tuple(individuo)
            if clave not in self.cache:
                self.cache[clave] = r2_ajustado(individuo)
            fitness.append(self.cache[clave])

        self.fitness = np.array(fitness)
        return self.fitness

    def seleccion(self):
        # torneo: gana el de mejor r2 entre tam_torneo individuos al azar
        ganadores = []

        while len(ganadores) < self.no_progenitores:
            competidores = np.random.choice(len(self.poblacion), size=self.tam_torneo, replace=False)
            mejor = competidores[np.argmax(self.fitness[competidores])]
            ganadores.append(self.poblacion[mejor])

        self.padres = np.array(ganadores)
        return self.padres

    def seleccion_elite(self):
        orden = np.argsort(self.fitness)[::-1]
        self.elite = self.poblacion[orden[:self.no_elite]].copy()
        return self.elite

    def cruce(self):
        # cruce uniforme: cada gen del hijo viene de uno de los dos padres al azar
        hijos = []
        no_hijos = self.no_poblacion - self.no_elite

        while len(hijos) < no_hijos:
            i, j = np.random.choice(len(self.padres), size=2, replace=False)
            padre1, padre2 = self.padres[i], self.padres[j]

            if np.random.rand() < self.prob_cruce:
                mascara = np.random.rand(total_variables) < 0.5
                hijo = np.where(mascara, padre1, padre2)
            else:
                hijo = (padre1 if np.random.rand() < 0.5 else padre2).copy()

            if hijo.sum() == 0:
                continue

            hijos.append(hijo)

        self.hijos = np.array(hijos, dtype=int).reshape(-1, total_variables)
        return self.hijos

    def mutacion(self):
        # cada gen tiene prob_mutacion de cambiar
        originales = self.hijos.copy()

        mascara = np.random.rand(*self.hijos.shape) < self.prob_mutacion
        self.hijos[mascara] = 1 - self.hijos[mascara]

        # si un hijo queda sin variables se deja como estaba
        en_cero = self.hijos.sum(axis=1) == 0
        self.hijos[en_cero] = originales[en_cero]

        return self.hijos

    def nueva_generacion(self):
        self.seleccion_elite()
        self.seleccion()
        self.cruce()
        self.mutacion()
        self.poblacion = np.vstack([self.elite, self.hijos])
        return self.poblacion

    def ejecutar(self):
        """
        Retorna [modelos evaluados, generaciones, tiempo, generacion del mejor,
                 r2 ajustado del mejor, variables del mejor]
        """
        inicio = time.perf_counter()

        self.cache = {}
        self.historial = []  # mejor r2 de cada generacion
        self.mejor_individuo = None
        self.mejor_r2 = -np.inf
        self.generacion_mejor = None
        sin_mejora = 0
        referencia = -np.inf  # r2 de la ultima mejora mayor a la tolerancia

        self.poblacion_inicial()

        for generacion in range(1, self.no_generaciones + 1):
            if generacion > 1:
                self.nueva_generacion()

            self.evaluar_poblacion()

            i = np.argmax(self.fitness)
            mejor_gen = self.fitness[i]
            self.historial.append(mejor_gen)

            # early stopping
            if mejor_gen - referencia > self.tolerancia:
                referencia = mejor_gen
                sin_mejora = 0
            else:
                sin_mejora += 1

            if mejor_gen > self.mejor_r2:
                self.mejor_r2 = mejor_gen
                self.mejor_individuo = self.poblacion[i].copy()
                self.generacion_mejor = generacion

            if sin_mejora >= self.paciencia:
                break

        tiempo = time.perf_counter() - inicio
        variables_mejor = nombres_variables[self.mejor_individuo.astype(bool)].tolist()

        return [
            len(self.cache),
            generacion,
            tiempo,
            self.generacion_mejor,
            float(self.mejor_r2),
            variables_mejor,
        ]


def correr_algoritmo_genetico(matriz_parametros, semilla=42):
    # corre el algoritmo con cada fila de parametros y marca al ganador
    resultados_genetico = {}

    for parametros in matriz_parametros:
        np.random.seed(semilla)
        ag = AlgoritmoGenetico(*parametros)
        resultados_genetico[parametros] = ag.ejecutar()

    ganador = max(resultados_genetico, key=lambda p: resultados_genetico[p][4])
    for parametros, salida in resultados_genetico.items():
        salida.append("Ganador!" if parametros == ganador else "")

    return resultados_genetico
