# -----------------------------------------------------------------------------

import os
import pytest
import pandas as pd

from g03 import *
from modelo.manejo_archivos import *
import matplotlib.pyplot as plt

"""
Módulo para generar muestras y escribirlas en un csv para luego realizar el
análisis correspondiente. 
"""

# -----------------------------------------------------------------------------

encabezado = [
    "CANTON", "EDAD", "ES URBANO", "SEXO", "ES DEPENDIENTE",
    "ESTADO VIVIENDA", "E.HACINAMIENTO", "ALFABETIZACIÓN",
    "ESCOLARIDAD PROMEDIO", "ASISTENCIA EDUCACION", "FUERZA DE TRABAJO",
    "SEGURO", "N.EXTRANJERO", "C.DISCAPACIDAD", "POBLACION TOTAL",
    "SUPERFICIE", "DENSIDAD POBLACION", "VIVIENDAS INDIVIDUALES OCUPADAS",
    "PROMEDIO DE OCUPANTES", "P.JEFAT.FEMENINA", "P.JEFAT.COMPARTIDA",
    "PARTIDO"
]

# -----------------------------------------------------------------------------


def contar_votos_partidos(df_muestra):

    return df_muestra.groupby('PARTIDO').size().sort_values()

# -----------------------------------------------------------------------------


def ejecutar_analisis_muestra_pais(lista_muestra):

    ruta_base = os.path.join("..", "archivos")
    ruta_votantes = os.path.join(ruta_base, "ejemplo_de_salida.csv")
    ruta_conteo_votos = os.path.join(ruta_base, "conteo_votos.csv")

    # Se crear un Dataframe para poder nombrar las columnas y sea
    # fácil de visualizar
    df_muestra = pd.DataFrame(lista_muestra, columns=encabezado)

    # Se hace el conteo de votos para cada partido
    df_conteo_votos = contar_votos_partidos(df_muestra)

    df_conteo_votos.plot.barh()
    plt.show()

    # # Guardar cada uno de los archivos generados
    # guardar_como_csv(df_muestra, ruta_votantes)
    # guardar_como_csv(df_conteo_votos, ruta_conteo_votos)
    #
    # # Se trata de abrir la carpeta donde están los archivos
    # try:
    #     os.startfile(ruta_base)
    # except Exception:
    #     print("No se pudo abrir el directorio donde están los archivos")


# -----------------------------------------------------------------------------


if __name__ == "__main__":

    ruta_actas = os.path.join("..", "archivos", "actas.csv")
    ruta_indicadores = os.path.join("..", "archivos", "indicadores.csv")

    # Con 100 votantes se considera suficiente para ser revisado manualmente
    # e incluso notar una distribución en los datos
    muestra = generar_muestra_pais_aux(100, ruta_actas, ruta_indicadores)
    ejecutar_analisis_muestra_pais(muestra)

# -----------------------------------------------------------------------------
