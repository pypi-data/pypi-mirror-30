# -----------------------------------------------------------------------------

import os
import sys

ruta = os.path.abspath(__file__)
ruta_base = os.path.split(ruta)[0]
sys.path.append(ruta_base)

from util.timeit import timeit
from modelo.manejo_muestras import *

# -----------------------------------------------------------------------------

# Constantes para arch
RUTA_ACTAS = os.path.join(ruta_base, "archivos", "actas.csv")
RUTA_INDICADORES = os.path.join(ruta_base, "archivos", "indicadores.csv")

# -----------------------------------------------------------------------------


@timeit
def generar_muestra_pais(n):
    """
    Genera una muestra simulada de votantes con sus características y
    un voto por un partido específico
    :param n: cantidad de votantes de la muestra
    :return: lista de listas (cada sublista contiene los atributos de un
    votante)
    """

    return generar_muestra_pais_aux(n, RUTA_ACTAS, RUTA_INDICADORES)

# -----------------------------------------------------------------------------


@timeit
def generar_muestra_provincia(n, nombre_provincia):
    """
    Genera una muestra simulada para una provincia específica.
    :param n: cantidad de votantes en la muestra
    :param nombre_provincia: nombre en mayuscula y sin tildes
    :return:
    """

    return generar_muestra_provincia_aux(n, nombre_provincia,
                                         RUTA_ACTAS, RUTA_INDICADORES)

# -----------------------------------------------------------------------------
