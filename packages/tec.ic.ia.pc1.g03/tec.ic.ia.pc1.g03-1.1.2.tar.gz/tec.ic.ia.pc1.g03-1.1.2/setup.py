# setup.py es un archivo necesario para publicar el proyecto
# y después usarlo con pip.
# Referencia: https://packaging.python.org/tutorials/distributing-packages/#setup-args

from setuptools import setup, find_packages

setup(
    name="tec.ic.ia.pc1.g03",
    packages=find_packages(),
    description="Inteligencia Artificial: Proyecto Corto I",
    long_description="Generador de datos según el Estado de la Nación",
    version="1.1.2",
    author="Julian Salinas, Brandon Dinarte, Armando López",
    license="GNU General Public License v3.0",
    keywords=['tec', 'ic', 'ia', "g03"],
    url='https://github.com/bdinarte/SimuladorVotantes',
    download_url="https://github.com/bdinarte/SimuladorVotantes/archive/v1.1.1.tar.gz",
    install_requires=['pandas', 'matplotlib', 'pytest'],
    python_requires='>=3',
    include_package_data=True,
    package_data={"": ["*.txt", "*.csv", ".xlsx"]},
    classifiers=[],
    entry_points={
        'console_scripts':[
            'generar_muestra_pais = tec.ic.ia.pc1.g03:generar_muestra_pais',
            'generar_muestra_provincia = tec.ic.ia.pc1.g03:generar_muestra_provincia'
        ]},
)
