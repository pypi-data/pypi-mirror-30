# -----------------------------------------------------------------------------

from random import seed
from g03 import *
from modelo.gen_randoms import *
from modelo.manejo_archivos import obtener_dataframe

"""
Módulo para probar las funciones de generación de datos aleatorios. 
Para obtener resultados consistentes, se altera la semilla de generación de 
números aleatorios y posteriormente se aleatoriza nuevamente.
"""

# -----------------------------------------------------------------------------


def test_random_con_pesos():

    opciones_posibles = ['Opcion 1', 'Opcion 2', 'Opcion 3', 'Opcion 4']
    pesos_por_opcion = [10, 20, 150, 10]

    # Se altera la semilla de random
    seed(2018)

    resultado1 = random_con_pesos(opciones_posibles, pesos_por_opcion)
    assert resultado1 == 'Opcion 3'

    resultado2 = random_con_pesos(opciones_posibles, pesos_por_opcion)
    assert resultado2 == 'Opcion 3'

    resultado3 = random_con_pesos(opciones_posibles, pesos_por_opcion)
    assert resultado3 == 'Opcion 1'

    resultado4 = random_con_pesos(opciones_posibles, pesos_por_opcion)
    assert resultado4 == 'Opcion 3'

    # Aleatorizar la semilla de random
    seed(time())

# -----------------------------------------------------------------------------


def test_random_de_juntas():

    juntas_por_cada_voto = [1, 1, 1, 1, 2, 2, 4, 3, 3, 3]

    seed(2018)

    num_junta = random_de_juntas(juntas_por_cada_voto)
    assert num_junta == 3

    num_junta = random_de_juntas(juntas_por_cada_voto)
    assert num_junta == 1

    num_junta = random_de_juntas(juntas_por_cada_voto)
    assert num_junta == 1

    # aleatorizar la semilla de random
    seed(time())

# -----------------------------------------------------------------------------


def test_generar_buckets():

    posibilidades = ['Junta1990', 'Junta2002', 'Junta2006', 'Junta2014',
                     'Junta2018']
    cantidades = [2, 1, 1, 3, 1]

    resultado_esperado = ['Junta1990', 'Junta1990', 'Junta2002', 'Junta2006',
                          'Junta2014', 'Junta2014', 'Junta2014', 'Junta2018']

    # Se comprueba que se generan repeticiones de la primer lista, según
    # las cantidades de la segunda lista, lo cual sirve para el random
    # de juntas por ejemplo
    assert generar_buckets(posibilidades, cantidades) == resultado_esperado

# -----------------------------------------------------------------------------


def test_random_indicadores():

    ruta_i = os.path.join("..", RUTA_INDICADORES)
    indicadores = obtener_dataframe(ruta_i).values.tolist()

    seed(2018)

    indicadores_atenas = random_indicadores(indicadores, 'ATENAS')
    assert indicadores_atenas == ['ATENAS', 26, 'URBANO', 'F',
                                  'NO DEPENDIENTE', 'V. MAL ESTADO',
                                  'V. NO HACINADA', 'ALFABETIZADO', 10.4,
                                  'EDUCACION REGULAR INACTIVA', 'DESEMPLEADO',
                                  'NO ASEGURADO', 'NO EXTRANJERO',
                                  'DISCAPACITADO', 25460, 127.2, 200, 7472,
                                  3.41, 22.9, 8.5]

    indicadores_pococi = random_indicadores(indicadores, 'POCOCI')
    assert indicadores_pococi == ['POCOCI', 22, 'NO URBANO', 'F',
                                  'NO DEPENDIENTE', 'V. BUEN ESTADO',
                                  'V. NO HACINADA', 'ALFABETIZADO', 5.6,
                                  'EN EDUCACION REGULAR', 'EMPLEADO',
                                  'NO ASEGURADO', 'NO EXTRANJERO',
                                  'NO DISCAPACITADO', 125962, 2403.5, 52,
                                  36238, 3.46, 26.5, 6.3]

    seed(time())
