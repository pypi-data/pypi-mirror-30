# -----------------------------------------------------------------------------

from g03 import *
from random import seed
from time import time

# -----------------------------------------------------------------------------

"""
Módulo para probar los resultados de las funciones principales del proyecto.
La duración de la prueba es corta, se utilizan muestras pequeñas.
"""

# -----------------------------------------------------------------------------


def test_generar_muestra_pais():

    ruta_a = os.path.join("..", RUTA_ACTAS)
    ruta_i = os.path.join("..", RUTA_INDICADORES)

    # Definir una semilla de random fija para obtener resultados consistentes
    seed(2018)

    # Se usa la función auxiliar para reemplazar la ruta de los archivos
    # de prueba
    muestra = generar_muestra_pais_aux(2, ruta_a, ruta_i)

    assert muestra == [['ACOSTA', 58, 'NO URBANO', 'M', 'NO DEPENDIENTE',
                        'V. BUEN ESTADO', 'V. NO HACINADA', 'ALFABETIZADO',
                        7.0, 'EDUCACION REGULAR INACTIVA', 'EMPLEADO',
                        'ASEGURADO', 'NO EXTRANJERO', 'NO DISCAPACITADO',
                        20209, 342.2, 59, 5871, 3.44, 26.5, 4.9,
                        'ACCION CIUDADANA'],
                       ['ABANGARES', 20, 'NO URBANO', 'F', 'NO DEPENDIENTE',
                        'V. BUEN ESTADO', 'V. NO HACINADA', 'ALFABETIZADO',
                        6.7, 'EN EDUCACION REGULAR', 'DESEMPLEADO',
                        'NO ASEGURADO', 'NO EXTRANJERO', 'NO DISCAPACITADO',
                        18039, 675.8, 27, 5311, 3.39, 26.7, 6.6,
                        'UNIDAD SOCIAL CRISTIANA']]

    # Aleatorizar la semilla en caso que la prueba se corra individualmente
    seed(time())

# -----------------------------------------------------------------------------


def test_generar_muestra_provincia():

    ruta_a = os.path.join("..", RUTA_ACTAS)
    ruta_i = os.path.join("..", RUTA_INDICADORES)

    # Definir una semilla de random fija para obtener resultados consistentes
    seed(2503)

    # Se usa la función auxiliar para reemplazar la ruta de los archivos
    # de prueba
    muestra = generar_muestra_provincia_aux(2, 'CARTAGO', ruta_a, ruta_i)

    assert muestra == [['LA UNION', 29, 'URBANO', 'M', 'NO DEPENDIENTE',
                        'V. MAL ESTADO', 'V. HACINADA', 'ALFABETIZADO', 8.2,
                        'EDUCACION REGULAR INACTIVA', 'DESEMPLEADO',
                        'ASEGURADO', 'EXTRANJERO', 'NO DISCAPACITADO', 99399,
                        44.8, 2217, 26979, 3.67, 31.5, 8.4,
                        'UNIDAD SOCIAL CRISTIANA'],
                       ['CARTAGO', 50, 'URBANO', 'M', 'NO DEPENDIENTE',
                        'V. MAL ESTADO', 'V. NO HACINADA', 'ALFABETIZADO', 5.6,
                        'EDUCACION REGULAR INACTIVA', 'DESEMPLEADO',
                        'NO ASEGURADO', 'NO EXTRANJERO', 'DISCAPACITADO',
                        147898, 287.8, 514, 38618, 3.8, 28.7, 6.4, 'NULO']]

    muestra = generar_muestra_provincia_aux(2, 'HEREDIA', ruta_a, ruta_i)

    assert muestra == [['HEREDIA', 32, 'URBANO', 'M', 'NO DEPENDIENTE',
                        'V. MAL ESTADO', 'V. NO HACINADA', 'ALFABETIZADO',
                        11.2, 'EDUCACION REGULAR INACTIVA', 'DESEMPLEADO',
                        'NO ASEGURADO', 'NO EXTRANJERO', 'NO DISCAPACITADO',
                        123616, 282.6, 437, 35216, 3.5, 34.9, 9.2,
                        'ACCION CIUDADANA'],
                       ['SANTA BARBARA', 20, 'URBANO', 'M', 'NO DEPENDIENTE',
                        'V. BUEN ESTADO', 'V. NO HACINADA', 'ALFABETIZADO',
                        11.6, 'EDUCACION REGULAR INACTIVA', 'DESEMPLEADO',
                        'NO ASEGURADO', 'NO EXTRANJERO', 'DISCAPACITADO',
                        36243, 53.2, 681, 10107, 3.58, 24.6, 8.0,
                        'ACCION CIUDADANA']]

    # Aleatorizar la semilla en caso que la prueba se corra individualmente
    seed(time())
