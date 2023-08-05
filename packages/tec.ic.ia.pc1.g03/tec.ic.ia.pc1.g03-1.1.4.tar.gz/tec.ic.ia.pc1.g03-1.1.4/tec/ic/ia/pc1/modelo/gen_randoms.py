# -----------------------------------------------------------------------------

from random import randint
from modelo.manejo_consultas import *

# -----------------------------------------------------------------------------


def random_con_pesos(atributos, pesos):
    """
    Genera un aleatorio según los porcentajes de cada elemento
    :param atributos: lista de elementos candidatos a escogerse
    :param pesos: lista de porcentajes correspondientes a cada elemento
    :return: el atributo en la posición aleatoria generada
    """

    numero_random = randint(0, sum(pesos) * 100 - 1)
    porcent_acumulado = 0

    for i in range(0, len(atributos)):
        porcent_acumulado += pesos[i] * 100
        if numero_random < porcent_acumulado:
            return atributos[i]

# -----------------------------------------------------------------------------


def random_de_juntas(tipos_repetidos):
    """
    Genera un random para las posiciones en una lista de elementos repetidos
    :param tipos_repetidos: lista de elementos repetidos ordenados
    :return: el elemento en la posición resultado del random
    """

    numero_random = randint(0, len(tipos_repetidos) - 1)
    return tipos_repetidos[numero_random]

# -----------------------------------------------------------------------------


def generar_buckets(tipos, cantidades):
    """
    Genera de elementos repetidos según la lista de nombres de los elementos y
    la lista con las cantidades para cada uno
    :param tipos: lista con nombres de los elementos
    :param cantidades: lista de cantidad para cada nombre
    :return: lista de elementos repetidos
    """

    contador = 0
    acumulador = []
    for cantidad in cantidades:
        acumulador += [tipos[contador]] * cantidad
        contador += 1

    return acumulador


# -----------------------------------------------------------------------------

def random_cero_cien(valor_comparacion):
    """
    Función encargada de generar un random de cero a 100 para saber si un
    indicador es positivo o negativo para un determinado individuo
    :param valor_comparacion: es el porcentaje que posee el indicador
    para saber si es positivo o negativo
    :return: valor booleano, que indica si el número generado se encuentra
    en el rango del valor de comparación o no.
    """

    numero_random = randint(1, 10000)
    return numero_random <= valor_comparacion*100

# -----------------------------------------------------------------------------


def random_sexo(razon_masculinidad):
    """
    Función encargada de generar un random para saber si un individuo
    es hombre o mujer
    :param razon_masculinidad: es el índice de hombres por cada 100 mujeres
    :return: valor booleano indicando el sexo, el hombre es True
    """

    porc_hombre = razon_masculinidad/(razon_masculinidad+100)*100
    return random_cero_cien(porc_hombre)

# -----------------------------------------------------------------------------


def random_edad():
    """
    Función encargada de generar una edad para un individuo según los datos
    tomados de los indicadores demográficos cantonales del anho 2013. Donde
    un 69p de personas están entre 18 y 64 anhos, y un 7p de 65 a más anhos.
    El otro grupo (menores de edad) no se toma en cuenta.
    :return: Edad que va ser asignada a un individuo
    """

    numero_random = randint(1, 76)
    return randint(18, 64) if numero_random else randint(64, 100)


# -----------------------------------------------------------------------------


def indicador(columna, positivo, negativo,
              funcion_random=random_cero_cien):
    """
    Esta función se utiliza únicamente en random_indicadores, con el fin
    de acortar el tamaño de cada una de las líneas
    :param funcion_random: ej. random_cero_cien
    :param columna: donde se encuentra el valor por analizar. ej indicadores.M
    :param positivo: ej. El votante SI tiene vivienda propia
    :param negativo: ej. E; votante NO tiene vivienda propia
    :return: retornar el positivo o negativo según función_random
    """

    return positivo if funcion_random(columna) else negativo

# -----------------------------------------------------------------------------


def random_indicadores(indicadores, canton):
    """
    Función encargada de obtener los indicadores de un cierto cantón, tomar
    los campos a los que se les debe aplicar un random y llamar a las
    respectivas funciones. Al final se obtiene una lista con todos los
    indicadores que devuelvan dichas funciones secundarias.
    :param indicadores: lista de lista que contiene los indicadores de los
    cantones
    :param canton: es sobre el cuál se tomarán los indicadores
    :return: una lista con los K atributos/indicadores que tendrá el individuo
    """

    # -------------------------------------------------------------------------
    # pandas.Series con los indicadores de un cantón

    columnas = obtener_datos_canton(indicadores, canton)

    # -------------------------------------------------------------------------
    # Generación de una edad para el individuo

    edad = random_edad()

    # -------------------------------------------------------------------------
    # Porcentaje de la población urbana

    es_urbano = indicador(columnas[9], 'URBANO', 'NO URBANO')

    # -------------------------------------------------------------------------
    # Porcentaje de hombres por cada cien mujeres

    sexo = indicador(columnas[10], 'M', 'F', random_sexo)

    # -------------------------------------------------------------------------
    # Porcentaje de dependencia demográfica

    def f(porcent): return edad >= 65 and random_cero_cien(porcent)
    es_dependiente = indicador(
        columnas[11], 'DEPENDIENTE', 'NO DEPENDIENTE', f)

    # -------------------------------------------------------------------------
    # Porcentaje de viviendas en buen estado

    vivienda_buena = indicador(columnas[12], 'V. BUEN ESTADO', 'V. MAL ESTADO')

    # -------------------------------------------------------------------------
    # Porcentaje de viviendas hacinadas

    vivienda_hacinada = indicador(
        columnas[13], 'V. HACINADA', 'V. NO HACINADA')

    # -------------------------------------------------------------------------
    # Porcentaje de Alfabetismo

    columna = columnas[14] if edad <= 24 else columnas[15]
    alfabetismo = indicador(columna, 'ALFABETIZADO', 'NO ALFABETIZADO')

    # -------------------------------------------------------------------------
    # Porcentaje de escolaridad
    # Se aplica Desviación estandar de -2 a 2

    escolaridad = columnas[16] if edad <= 49 else columnas[17]
    escolaridad = round(randint(-2, 2) + escolaridad, 2)

    # -------------------------------------------------------------------------
    # Porcentaje de asistencia a la educación regular

    columna = columnas[18] if edad <= 24 else columnas[19]
    educacion_regular = indicador(
        columna, 'EN EDUCACION REGULAR', 'EDUCACION REGULAR INACTIVA')

    # -------------------------------------------------------------------------
    # Tasa neta de participación

    columna = columnas[20] if sexo == 'M' else columnas[21]
    es_empleado = indicador(columna, 'EMPLEADO', 'DESEMPLEADO')

    # -------------------------------------------------------------------------
    # Porcentaje de ser no asegurado

    columna = columnas[22] if es_empleado == 'EMPLEADO' else columnas[25]
    es_asegurado = indicador(columna, 'ASEGURADO', 'NO ASEGURADO')

    # -------------------------------------------------------------------------
    # Porcentaje de ser extranjero

    es_extranjero = indicador(columnas[23], 'EXTRANJERO', 'NO EXTRANJERO')

    # -------------------------------------------------------------------------
    # Porcentaje de ser discapacitado

    es_discapacitado = indicador(
        columnas[24], 'DISCAPACITADO', 'NO DISCAPACITADO')

    # -------------------------------------------------------------------------

    return [
        canton, edad, es_urbano, sexo, es_dependiente, vivienda_buena,
        vivienda_hacinada, alfabetismo, escolaridad, educacion_regular,
        es_empleado, es_asegurado, es_extranjero, es_discapacitado
    ] + columnas[2:9]

# -----------------------------------------------------------------------------
