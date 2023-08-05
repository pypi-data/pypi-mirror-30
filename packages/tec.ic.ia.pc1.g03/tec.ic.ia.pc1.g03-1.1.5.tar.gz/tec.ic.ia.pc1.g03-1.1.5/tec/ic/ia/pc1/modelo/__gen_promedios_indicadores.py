
from g03 import *

# -----------------------------------------------------------------------------


def obtener_promedio_indicadores_muestra(muestra):

    suma_urbano = 0
    suma_hombres = 0
    suma_alfabetizado = 0
    suma_discapacidad = 0
    suma_empleado = 0
    suma_escolaridad = 0

    for atributos in muestra:

        suma_urbano += 1 if atributos[2] == 'URBANO' else 0
        suma_hombres += 1 if atributos[3] == 'M' else 0
        suma_alfabetizado += 1 if atributos[7] == 'ALFABETIZADO' else 0
        suma_escolaridad += atributos[8]
        suma_empleado += 1 if atributos[10] == 'EMPLEADO' else 0
        suma_discapacidad += 1 if atributos[13] == 'DISCAPACITADO' else 0

    promedios = []
    tamano_muestra = len(muestra)
    promedios.append(100*suma_urbano/tamano_muestra)
    promedios.append(100*suma_hombres/tamano_muestra)
    promedios.append(100*suma_alfabetizado/tamano_muestra)
    promedios.append(100*suma_empleado/tamano_muestra)
    promedios.append(round(suma_escolaridad / tamano_muestra, 2))
    promedios.append(100*suma_discapacidad/tamano_muestra)

    return promedios

# -----------------------------------------------------------------------------


if __name__ == "__main__":

    ruta_actas = os.path.join("..", "archivos", "actas.csv")
    ruta_indicadores = os.path.join("..", "archivos", "indicadores.csv")

    tamano_muestra = 500

    muestra = generar_muestra_pais_aux(tamano_muestra, ruta_actas,
                                       ruta_indicadores)
    promedios = obtener_promedio_indicadores_muestra(muestra)
    print('Promedios de muestra para Costa Rica con n = '
          + str(tamano_muestra) + ': ' + str(promedios))

    muestra = generar_muestra_provincia_aux(tamano_muestra, 'SAN JOSE',
                                            ruta_actas, ruta_indicadores)
    promedios = obtener_promedio_indicadores_muestra(muestra)
    print('Promedios de muestra para San José con n = '
          + str(tamano_muestra) + ': ' + str(promedios))

    muestra = generar_muestra_provincia_aux(tamano_muestra, 'CARTAGO',
                                            ruta_actas, ruta_indicadores)
    promedios = obtener_promedio_indicadores_muestra(muestra)
    print('Promedios de muestra para Cartago con n = '
          + str(tamano_muestra) + ': ' + str(promedios))

    muestra = generar_muestra_provincia_aux(tamano_muestra, 'PUNTARENAS',
                                            ruta_actas, ruta_indicadores)
    promedios = obtener_promedio_indicadores_muestra(muestra)
    print('Promedios de muestra para Puntarenas con n = '
          + str(tamano_muestra) + ': ' + str(promedios))

# -----------------------------------------------------------------------------
