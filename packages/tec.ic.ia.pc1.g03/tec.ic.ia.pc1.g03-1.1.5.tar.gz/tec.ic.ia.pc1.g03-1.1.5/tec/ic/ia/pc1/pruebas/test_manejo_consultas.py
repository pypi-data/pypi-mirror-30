# -----------------------------------------------------------------------------

from g03 import *
from modelo.manejo_consultas import *

# -----------------------------------------------------------------------------

"""
Módulo para probar las consultas a datos obtenidos de los archivos respectivos.
La duración de la prueba es corta.
"""

# -----------------------------------------------------------------------------


def test_obtener_datos_canton():

    ruta_i = os.path.join("..", RUTA_INDICADORES)
    indicadores = obtener_dataframe(ruta_i).values.tolist()

    atenas = obtener_datos_canton(indicadores, 'ATENAS')
    assert atenas == ['ATENAS', 'ALAJUELA', 25460, 127.2, 200, 7472, 3.41,
                      22.9, 8.5, 56.2, 100.1, 44.9, 74.4, 2.3, 99.3, 97.4,
                      9.4, 7.3, 50.4, 6.7, 70.3, 31.6, 12.7, 8.2, 9.4, 10.8]

    flores = obtener_datos_canton(indicadores, 'FLORES')
    assert flores == ['FLORES', 'HEREDIA', 20037, 7.0, 2879, 5751, 3.48, 28.5,
                      11.2, 100.0, 95.9, 41.3, 83.0, 2.4, 99.3, 99.0, 11.5,
                      9.0, 50.9, 9.4, 74.3, 44.5, 9.3, 7.8, 9.4, 9.0]

    turrialba = obtener_datos_canton(indicadores, 'TURRIALBA')
    assert turrialba == ['TURRIALBA', 'CARTAGO', 69616, 1642.7, 42, 20453, 3.4,
                         26.5, 8.3, 57.4, 97.8, 49.1, 64.9, 3.4, 98.8, 94.8,
                         8.3, 6.0, 49.1, 8.2, 67.7, 28.1, 14.9, 2.2, 11.7,
                         12.6]

# -----------------------------------------------------------------------------


def test_obtener_juntas():

    ruta_a = os.path.join("..", RUTA_ACTAS)
    actas = obtener_dataframe(ruta_a, encabezado=True)

    # Se comprueba que se extraen los 6541 números de junta definidos en el
    # archivo csv y que es un listado con números de junta
    juntas = obtener_juntas(actas)
    assert len(juntas) == 6541
    assert juntas[1] == 2
    assert juntas[1500] == 1501
    assert juntas[4532] == 4533

# -----------------------------------------------------------------------------


def test_obtener_datos_junta():

    ruta_a = os.path.join("..", RUTA_ACTAS)
    actas = obtener_dataframe(ruta_a, encabezado=True)

    # Se comprueba que se extrajeron correctamente los datos para algunas
    # juntas de ejemplo
    junta3015 = obtener_datos_junta(actas, 3015)
    assert junta3015 == [3015, 'ALAJUELA', 'SAN CARLOS', 0,
                         108, 0, 0, 5, 30, 70, 0, 4, 2, 14, 102, 74, 2, 1, 412]

    junta6120 = obtener_datos_junta(actas, 6120)
    assert junta6120 == [6120, 'LIMON', 'LIMON', 4, 17,
                         0, 0, 2, 45, 43, 0, 0, 3, 8, 123, 51, 5, 2, 303]

    junta520 = obtener_datos_junta(actas, 520)
    assert junta520 == [520, 'SAN JOSE', 'DESAMPARADOS', 1,
                        93, 1, 3, 4, 44, 59, 4, 1, 4, 28, 101, 55, 0, 0, 398]

# -----------------------------------------------------------------------------


def test_obtener_juntas_provincia():

    ruta_a = os.path.join("..", RUTA_ACTAS)
    actas = obtener_dataframe(ruta_a, encabezado=True)

    # Se comprueba que se extrajeron 1266 juntas, que son las que pertenecen
    # a la provincia de Alajuela
    juntas_alajuela = obtener_datos_juntas_provincia(actas, 'ALAJUELA')
    assert len(juntas_alajuela) == 1266

    # Se comprueba que se extrajeron 565 juntas, que son las que pertenecen
    # a la provincia de Guanacaste
    juntas_guanacaste = obtener_datos_juntas_provincia(actas, 'GUANACASTE')
    assert len(juntas_guanacaste) == 565

# -----------------------------------------------------------------------------


def test_obtener_opciones_voto():

    ruta_a = os.path.join("..", RUTA_ACTAS)
    actas = obtener_dataframe(ruta_a, encabezado=True)

    # Se comprueba que las opciones son las conocidas
    opciones = obtener_opciones_voto(actas)
    assert opciones == ['ACCESIBILIDAD SIN EXCLUSION', 'ACCION CIUDADANA',
                        'ALIANZA DEMOCRATA CRISTIANA', 'DE LOS TRABAJADORES',
                        'FRENTE AMPLIO', 'INTEGRACION NACIONAL',
                        'LIBERACION NACIONAL', 'MOVIMIENTO LIBERTARIO',
                        'NUEVA GENERACION', 'RENOVACION COSTARRICENSE',
                        'REPUBLICANO SOCIAL CRISTIANO',
                        'RESTAURACION NACIONAL', 'UNIDAD SOCIAL CRISTIANA',
                        'NULO', 'BLANCO']

# -----------------------------------------------------------------------------


def test_obtener_total_votos():

    ruta_a = os.path.join("..", RUTA_ACTAS)
    actas = obtener_dataframe(ruta_a, encabezado=True)

    # Se comprueba que se obtuvieron los totales de 6541 juntas disponibles
    # y que dichos totales suman 2 178 326 votos
    totales = obtener_total_votos(actas)
    assert len(totales) == 6541
    assert sum(totales) == 2178326

# -----------------------------------------------------------------------------
