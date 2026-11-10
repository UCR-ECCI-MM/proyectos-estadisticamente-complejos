from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

# 1. CARGA DE DATOS

# Busca datos.csv en la misma carpeta de este script
ruta_datos = Path(__file__).resolve().parent / "datos.csv"
datos = pd.read_csv(ruta_datos)

# X: variables predictoras, y: variable objetivo
X = datos.drop(columns="critical_temp").to_numpy()
y = datos["critical_temp"].to_numpy()
n, total_variables = X.shape

# 2. Guarda la mejor solucion de cada tecnica
resultados = {}


# 3. ESTADISTICAS DEL DATASET

if __name__ == "__main__":
    print(f"Observaciones: {n} | Variables predictoras: {total_variables}")
    print(f"Valores nulos: {datos.isna().sum().sum()}")
    print(datos["critical_temp"].describe().round(2))


# 4. FUNCION OBJETIVO

def r2_ajustado(vector):
    """
    Retorna el R2 ajustado del modelo que representa un vector.

    Fuerza bruta, stepwise y el algoritmo genetico la usan para evaluar
    los modelos que generan.

    vector: lista de 81 valores, uno por variable predictora,
    en el orden de las columnas del CSV.
    
        1 = la variable entra al modelo
        0 = la variable no entra al modelo

    Ejemplo: [1, 0, 1, 0, ..., 0] usa solo la primera y la tercera variable.
    """
    seleccion = np.array(vector, dtype=bool)

    # Ajusta el modelo con intercepto y las columnas seleccionadas
    X_modelo = sm.add_constant(X[:, seleccion])
    return sm.OLS(y, X_modelo).fit().rsquared_adj
