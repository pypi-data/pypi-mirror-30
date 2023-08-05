# -----------------------------------------------------------------------------

from g03 import *
from modelo.manejo_archivos import obtener_dataframe

# -----------------------------------------------------------------------------

"""
Módulo para probar lectura de archivos csv con datos mediante el uso de la 
biblioteca "pandas".
"""

# -----------------------------------------------------------------------------


def test_obtener_dataframe():

    ruta_a = os.path.join("..", RUTA_ACTAS)
    ruta_i = os.path.join("..", RUTA_INDICADORES)

    # Se comprueba que se leyeron las 6541 filas con las juntas
    actas = obtener_dataframe(ruta_a, encabezado=True)
    assert len(actas) == 6541

    # Se comprueba que se leyeron los 81 cantones disponibles con indicadores
    indicadores = obtener_dataframe(ruta_i)
    assert len(indicadores) == 81
