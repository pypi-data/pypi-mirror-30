# -----------------------------------------------------------------------------

import os
import sys
import random
from time import time

from modelo.gen_randoms import *
from modelo.manejo_archivos import *
from modelo.manejo_consultas import *
from multiprocessing import Pool, cpu_count

# -----------------------------------------------------------------------------


def generar_muestra_pais_aux(n, ruta_actas, ruta_indicadores):
    """
    Función auxiliar para la generación de una muestra del país, el objetivo
    principal es recibir rutas de los archivos con datos
    @param n: cantidad de votantes de muestra
    @param ruta_actas: ruta del archivo con las juntas y votos
    @param ruta_indicadores: ruta del archivo con indicadores cantonales
    @return: lista de listas con las muestras de votantes
    """

    juntas_pais = obtener_dataframe(ruta_actas, encabezado=True)
    df_indicadores = obtener_dataframe(ruta_indicadores)
    return generar_muestra_threads(n, juntas_pais, df_indicadores)

# -----------------------------------------------------------------------------


def generar_muestra_provincia_aux(n, provincia, ruta_actas, ruta_indicadores):
    """
    Función auxiliar para la generación de una muestra de una provincia,
    el objetivo
    principal es recibir rutas de los archivos con datos
    @param n: cantidad de votantes de muestra
    @param provincia: provincia en mayúscula y sin tildes
    @param ruta_actas: ruta del archivo con las juntas y votos
    @param ruta_indicadores: ruta del archivo con indicadores cantonales
    @return: lista de listas con las muestras de votantes
    """

    juntas_pais = obtener_dataframe(ruta_actas, encabezado=True)
    juntas_prov = obtener_datos_juntas_provincia(juntas_pais, provincia)
    df_indicadores = obtener_dataframe(ruta_indicadores)
    return generar_muestra_threads(n, juntas_prov, df_indicadores)

# -----------------------------------------------------------------------------


def generar_muestra_threads(n_muestras, df_juntas, df_indicadores):
    """
    Generar un conjunto de "votantes" mediante la función
    generar_muestra(n,_muestras, df_juntas) pero usando 4 procesos
    simultaneos, al final se unen los resultados obtenidos de cada uno.
    @param n_muestras: Cantidad de "votantes" que se deben generar
    @param df_juntas: Dataframe que contiene la información de las juntas
    @param df_indicadores: Dataframe con los indicadores de cada cantón
    @return: Lista con sublistas, donde cada sublista es un votante
    """

    # Se genera un proceso por cada núcleo del procesador
    # Se resta 1 para que el porcentaje de uso del procesador no llegue al 100%
    n_procesos = cpu_count() - 1

    # Variables compartidas por los diferentes procesos
    partidos = obtener_opciones_voto(df_juntas)
    lista_juntas = obtener_juntas(df_juntas)
    total_votos = obtener_total_votos(df_juntas)
    juntas_con_pesos = generar_buckets(lista_juntas, total_votos)
    indicadores = df_indicadores.values.tolist()

    # Si cada proceso tuviese que hacer menos de 2000 muestras, resulta
    # mejor usar solo un proceso, esto varía entre equipos
    if n_muestras < n_procesos * 2000:
        return generar_muestra(n_muestras, df_juntas, indicadores, partidos,
                               juntas_con_pesos)

    pool = Pool(processes=n_procesos)

    # 1 parte de las muestras serán generadas por cada proceso
    muestras_x_proceso = n_muestras // n_procesos

    # Se especifica que función debe correr cada proceso
    # Los primeros tres corren la misma cantidad

    procesos = [
        pool.apply_async(generar_muestra,
                         (muestras_x_proceso, df_juntas, indicadores,
                          partidos, juntas_con_pesos,))
        for _ in range(n_procesos-1)
    ]

    # El último genera la cantidad que le corresponde más lo que hace falta
    muestras_restantes = n_muestras - (muestras_x_proceso * n_procesos)

    procesos.append(
        pool.apply_async(generar_muestra,
                         (muestras_x_proceso + muestras_restantes,
                          df_juntas, indicadores, partidos, juntas_con_pesos,))
    )

    # La función sum une las listas de listas obtenidas de cada proceso
    return sum([res.get() for res in procesos], [])

# -----------------------------------------------------------------------------


def generar_muestra(n, df_juntas, indicadores, partidos, juntas_con_pesos):
    """
    Función que ejecuta el ciclo para las n muestras definidas, en el cual
    se obtienen datos que varían según la junta aleatoria
    :param n: cantidad de votantes de la muestra
    :param df_juntas: dataframe con las juntas y sus votos
    :param indicadores: lista de listas con los indicadores de cada cantón
    :param partidos: lista de partidos políticos disponibles
    :param juntas_con_pesos: lista de números de junta repetidos según la
    cantidad total de votos emitidos en dicha junta
    :return: lista con las muestras de votantes
    """
    muestra = []

    for num_muestra in range(0, n):

        junta_random = random_de_juntas(juntas_con_pesos)
        datos_junta = obtener_datos_junta(df_juntas, junta_random)
        votos_junta = datos_junta[3:18]
        voto_muestra = random_con_pesos(partidos, votos_junta)

        canton = datos_junta[2]
        indic_muestra = random_indicadores(indicadores, canton)
        indic_muestra.append(voto_muestra)
        muestra.append(indic_muestra)

    return muestra

# -----------------------------------------------------------------------------
