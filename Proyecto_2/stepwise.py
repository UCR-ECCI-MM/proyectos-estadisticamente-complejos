"""
stepwise para seleccion de variables (forward, backward y ambos)
"""
import time

import numpy as np

from datos_r2 import r2_ajustado, total_variables


class Stepwise:
    def __init__(self):
        self.cache = {}

    def evaluar(self, vector):
        # para no correr la misma regresion dos veces
        clave = tuple(vector)
        if clave not in self.cache:
            self.cache[clave] = r2_ajustado(vector)
        return self.cache[clave]

    def forward(self):
        # arranca vacio y va metiendo la mejor variable hasta que ya no sube el r2
        inicio = time.perf_counter()
        self.cache = {}

        vector = np.zeros(total_variables, dtype=int)
        r2_actual = -1

        while True:
            fuera = np.flatnonzero(vector == 0)
            if len(fuera) == 0:
                break

            # 0100 -> 1100, 0110, 0101
            candidatos = np.tile(vector, (len(fuera), 1))
            candidatos[np.arange(len(fuera)), fuera] = 1

            r2s = [self.evaluar(c) for c in candidatos]
            k = np.argmax(r2s)

            if r2s[k] <= r2_actual:
                break

            vector = candidatos[k]
            r2_actual = r2s[k]

        tiempo = time.perf_counter() - inicio
        modelos_evaluados = len(self.cache)

        return vector, r2_actual, tiempo, modelos_evaluados

    def backward(self):
        # al reves: arranca con todas y va sacando
        inicio = time.perf_counter()
        self.cache = {}

        vector = np.ones(total_variables, dtype=int)
        r2_actual = self.evaluar(vector)  # aca si hay que calcularlo, con -1 siempre sacaria una

        while True:
            dentro = np.flatnonzero(vector == 1)
            if len(dentro) <= 1:
                break

            # 1111 -> 0111, 1011, 1101, 1110
            candidatos = np.tile(vector, (len(dentro), 1))
            candidatos[np.arange(len(dentro)), dentro] = 0

            r2s = [self.evaluar(c) for c in candidatos]
            k = np.argmax(r2s)

            if r2s[k] <= r2_actual:
                break

            vector = candidatos[k]
            r2_actual = r2s[k]

        tiempo = time.perf_counter() - inicio
        modelos_evaluados = len(self.cache)

        return vector, r2_actual, tiempo, modelos_evaluados

    def ambos(self):
        # mete una, revisa si sobra alguna, y repite. para cuando no cambia nada
        inicio = time.perf_counter()
        self.cache = {}

        vector = np.zeros(total_variables, dtype=int)
        r2_actual = -1

        while True:
            agrego = False
            quito = False

            # meter
            fuera = np.flatnonzero(vector == 0)
            if len(fuera) > 0:
                candidatos = np.tile(vector, (len(fuera), 1))
                candidatos[np.arange(len(fuera)), fuera] = 1

                r2s = [self.evaluar(c) for c in candidatos]
                k = np.argmax(r2s)

                if r2s[k] > r2_actual:
                    vector = candidatos[k]
                    r2_actual = r2s[k]
                    agrego = True

            # sacar (ojo, con el vector que ya tiene la nueva)
            dentro = np.flatnonzero(vector == 1)
            if len(dentro) > 1:
                candidatos = np.tile(vector, (len(dentro), 1))
                candidatos[np.arange(len(dentro)), dentro] = 0

                r2s = [self.evaluar(c) for c in candidatos]
                k = np.argmax(r2s)

                if r2s[k] > r2_actual:
                    vector = candidatos[k]
                    r2_actual = r2s[k]
                    quito = True

            if not agrego and not quito:
                break

        tiempo = time.perf_counter() - inicio
        modelos_evaluados = len(self.cache)

        return vector, r2_actual, tiempo, modelos_evaluados

