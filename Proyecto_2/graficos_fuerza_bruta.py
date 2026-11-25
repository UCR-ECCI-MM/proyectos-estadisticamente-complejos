"""
Graficos y extrapolacion de la fuerza bruta.

Lee el CSV generado por fuerza_bruta.py y:
    1. Grafica tiempo contra k (escala lineal y logaritmica).
    2. Grafica el mejor R2 ajustado contra k.
    3. Estima cuanto tardaria la fuerza bruta con las 81 variables,
       usando dos metodos independientes.

Correr desde la carpeta Proyecto_2:
    python graficos_fuerza_bruta.py
"""
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")   # guarda los graficos en archivos sin abrir ventanas
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from datos_r2 import r2_ajustado, total_variables

CARPETA = Path(__file__).resolve().parent / "resultados_fuerza_bruta"
RUTA_CSV = CARPETA / "corridas_fuerza_bruta.csv"

# Rango de k que se usa para ajustar la curva exponencial.
# Los k pequenos se dejan fuera: duran milesimas de segundo y su tiempo
# depende mas del "costo fijo" de Python que del numero de modelos.
K_MIN_AJUSTE = 8

SEG_POR_ANIO = 365.25 * 24 * 3600
EDAD_UNIVERSO_ANIOS = 13.8e9

# Colores y estilo (paleta de referencia: azul = medido, naranja = modelo)
AZUL, NARANJA = "#2a78d6", "#eb6834"
TINTA, TINTA_SUAVE, REJILLA = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({
    "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
    "axes.edgecolor": TINTA_SUAVE, "axes.labelcolor": TINTA,
    "xtick.color": TINTA_SUAVE, "ytick.color": TINTA_SUAVE,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": REJILLA, "grid.linewidth": 0.8,
    "font.size": 11, "axes.titlesize": 13, "axes.titleweight": "bold",
})


def formato_tiempo(seg):
    """Convierte segundos a un texto facil de leer."""
    if seg < 60:
        return f"{seg:.1f} s"
    if seg < 3600:
        return f"{seg / 60:.1f} min"
    if seg < 86400:
        return f"{seg / 3600:.1f} h"
    if seg < SEG_POR_ANIO:
        return f"{seg / 86400:.1f} dias"
    return f"{seg / SEG_POR_ANIO:.2e} anios"


def cargar_resumen():
    """Lee el CSV y calcula el promedio y la desviacion del tiempo por k."""
    corridas = pd.read_csv(RUTA_CSV)
    completas = corridas[corridas["completada"]]

    resumen = completas.groupby("k").agg(
        repeticiones=("tiempo_seg", "size"),
        tiempo_prom=("tiempo_seg", "mean"),
        tiempo_desv=("tiempo_seg", "std"),
        modelos=("modelos_evaluados", "first"),
        mejor_r2=("mejor_r2_ajustado", "first"),
        num_variables=("num_variables", "first"),
    ).reset_index()

    return corridas, completas, resumen


def ajustar_exponencial(resumen):
    """
    Ajusta log2(tiempo) = a + b*k con minimos cuadrados.

    Si la fuerza bruta es exponencial, en escala logaritmica los puntos
    forman una recta. La pendiente b dice cuanto crece el tiempo por
    cada variable extra: el tiempo se multiplica por 2^b.
    """
    datos = resumen[resumen["k"] >= K_MIN_AJUSTE]
    b, a = np.polyfit(datos["k"], np.log2(datos["tiempo_prom"]), 1)
    return a, b


def predecir(a, b, k):
    """Tiempo estimado (segundos) para k variables segun el ajuste."""
    return 2 ** (a + b * k)


def costo_por_modelo_81(muestras=100, semilla=42):
    """
    Mide el tiempo promedio de r2_ajustado con modelos tipicos de las
    81 variables. Al elegir cada variable al azar con probabilidad 1/2,
    los modelos tienen ~40 variables, que es el tamano promedio entre
    las 2^81 - 1 combinaciones.
    """
    rng = np.random.default_rng(semilla)
    vectores = rng.integers(0, 2, size=(muestras, total_variables))
    vectores[vectores.sum(axis=1) == 0, 0] = 1   # evita el modelo vacio

    inicio = time.perf_counter()
    for v in vectores:
        r2_ajustado(v)
    return (time.perf_counter() - inicio) / muestras


def grafico_tiempo(completas, resumen, a, b, logaritmico, punto_k18=None):
    """
    Tiempo contra k: cada repeticion, el promedio y el ajuste.
    punto_k18: tiempo completo estimado para k = 18 (corrida cortada),
        se dibuja solo en el grafico logaritmico para validar el ajuste.
    """
    fig, ax = plt.subplots(figsize=(8, 5))

    # Puntos sueltos: cada repeticion (muestra cuanto varia el tiempo)
    ax.scatter(completas["k"], completas["tiempo_seg"], s=18, color=AZUL,
               alpha=0.35, linewidths=0, label="Cada repeticion")

    # Linea con el promedio por k
    ax.plot(resumen["k"], resumen["tiempo_prom"], color=AZUL, linewidth=2,
            marker="o", markersize=6, label="Promedio medido")

    if logaritmico:
        # Recta del ajuste, extendida hasta k = 18 para ver la prediccion
        k_linea = np.linspace(K_MIN_AJUSTE, 18, 100)
        ax.plot(k_linea, predecir(a, b, k_linea), color=NARANJA, linewidth=2,
                linestyle="--",
                label=f"Ajuste: tiempo x {2 ** b:.2f} por variable")
        if punto_k18 is not None:
            # Punto hueco: no se midio completo, se estimo por el ritmo
            ax.plot(18, punto_k18, marker="D", markersize=8, linestyle="none",
                    markerfacecolor="none", markeredgecolor=AZUL,
                    markeredgewidth=2, label="k = 18 estimado por ritmo (87% medido)")
        ax.set_yscale("log")
        ax.set_title("Fuerza bruta: tiempo contra k (escala logaritmica)")
        ax.set_xticks(range(1, 19))
    else:
        ax.set_title("Fuerza bruta: tiempo contra k")
        ax.set_xticks(resumen["k"])

    ax.set_xlabel("k (numero de variables consideradas)")
    ax.set_ylabel("Tiempo por corrida (segundos)")
    ax.legend(frameon=False)
    fig.tight_layout()

    nombre = "tiempo_vs_k_log.png" if logaritmico else "tiempo_vs_k.png"
    fig.savefig(CARPETA / nombre, dpi=150)
    plt.close(fig)
    return nombre


def grafico_r2(resumen):
    """Mejor R2 ajustado encontrado para cada k."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(resumen["k"], resumen["mejor_r2"], color=AZUL, linewidth=2,
            marker="o", markersize=6)

    # Nota con el optimo exacto mas grande, en la esquina inferior derecha
    ultimo = resumen.iloc[-1]
    ax.text(0.98, 0.04,
            f"Optimo exacto con k = {int(ultimo['k'])}:\n"
            f"R2 aj. = {ultimo['mejor_r2']:.4f} ({int(ultimo['num_variables'])} variables)",
            transform=ax.transAxes, ha="right", va="bottom", color=TINTA)

    ax.set_title("Fuerza bruta: mejor R2 ajustado contra k")
    ax.set_xlabel("k (numero de variables consideradas)")
    ax.set_ylabel("Mejor R2 ajustado")
    ax.set_xticks(resumen["k"])
    fig.tight_layout()
    fig.savefig(CARPETA / "r2_vs_k.png", dpi=150)
    plt.close(fig)
    return "r2_vs_k.png"


if __name__ == "__main__":
    corridas, completas, resumen = cargar_resumen()

    a, b = ajustar_exponencial(resumen)

    # --- Validacion con k = 18 (corrida cortada por el limite de tiempo) ---
    # Si se cumplio el 87% de los modelos en 1800 s, la corrida completa
    # habria tardado aproximadamente 1800 / 0.87 segundos.
    lineas = []
    tiempo_k18 = None
    k18 = corridas[corridas["k"] == 18]
    if not k18.empty:
        fila = k18.iloc[0]
        fraccion = fila["modelos_evaluados"] / (2 ** 18 - 1)
        tiempo_k18 = fila["tiempo_seg"] / fraccion
        pred_k18 = predecir(a, b, 18)
        error = (pred_k18 - tiempo_k18) / tiempo_k18 * 100
        lineas += [
            "VALIDACION CON k = 18",
            f"  Modelos evaluados antes del limite: {fila['modelos_evaluados']} "
            f"de {2 ** 18 - 1} ({fraccion:.1%})",
            f"  Tiempo completo estimado por ritmo: {formato_tiempo(tiempo_k18)}",
            f"  Tiempo que predice el ajuste:       {formato_tiempo(pred_k18)}",
            f"  Diferencia: {error:+.1f}%",
            "",
        ]

    # --- Graficos ---
    archivos = [grafico_tiempo(completas, resumen, a, b, logaritmico=False),
                grafico_tiempo(completas, resumen, a, b, logaritmico=True,
                               punto_k18=tiempo_k18),
                grafico_r2(resumen)]

    # --- Extrapolacion a las 81 variables ---
    total_modelos = 2 ** total_variables - 1

    # Metodo 1: extender la recta del grafico logaritmico hasta k = 81
    t1 = predecir(a, b, total_variables)

    # Metodo 2: numero de modelos x costo medido de un modelo tipico
    costo = costo_por_modelo_81()
    t2 = total_modelos * costo

    lineas += [
        "AJUSTE EXPONENCIAL",
        f"  log2(tiempo) = {a:.3f} + {b:.3f} * k   (con k = {K_MIN_AJUSTE} a "
        f"{resumen['k'].max()})",
        f"  Cada variable extra multiplica el tiempo por {2 ** b:.2f}",
        "",
        f"EXTRAPOLACION A LAS {total_variables} VARIABLES "
        f"({total_modelos:.3e} modelos)",
        f"  Metodo 1 (recta del ajuste):          {t1:.3e} s = {formato_tiempo(t1)}",
        f"  Metodo 2 (modelos x {costo * 1000:.1f} ms/modelo): "
        f"{t2:.3e} s = {formato_tiempo(t2)}",
        f"  Comparacion: {t2 / SEG_POR_ANIO / EDAD_UNIVERSO_ANIOS:.2e} veces "
        f"la edad del universo (metodo 2)",
    ]

    texto = "\n".join(lineas)
    print(resumen.round(4).to_string(index=False))
    print()
    print(texto)
    (CARPETA / "extrapolacion.txt").write_text(texto + "\n")
    print("\nArchivos guardados en resultados_fuerza_bruta/:",
          ", ".join(archivos + ["extrapolacion.txt"]))
