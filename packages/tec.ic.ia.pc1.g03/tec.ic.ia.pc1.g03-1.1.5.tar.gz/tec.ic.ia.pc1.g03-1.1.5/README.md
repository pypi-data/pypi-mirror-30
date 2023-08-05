# SimuladorVotantes

Módulo de Python que contiene funciones para crear muestras de ejemplo, basados en los resultados electorales presidenciales de la primera ronda en Costa Rica.

### Instalación 

Se debe instalar usando desde la terminal usando `pip` de la siguiente manera: 

> pip install tec.ic.ia.pc1.g03 

Luego, para utilizarlo poder utilizarlo se debe importar al proyecto de la siguiente forma: 

> from tec.ic.ia.pc1.g03 import generar_muestra_pais, generar_muestra_provincia

### Incluir proyecto en PyPI

El primer paso es registrarse en la página de [PYPI](https://pypi.org/). Luego se procede a crear un archivo llamando [setup.py](setup.py) Dentro de ese módulo se debe agregar la función con el msmo nombre. Esta función debe contener los argumentos presentados [aquí](https://packaging.python.org/tutorials/distributing-packages/#setup-args). A continuación, se debe instalar los siguiente paquetes: 

> pip install wheel && pip install twine

Seguidamente, se debe crear una distribución o carpeta `dist`. Luego de crear esta carpeta se prosigue a subir el proyecto al repositorio con `twine`. Al hacer este paso nos solicitará el nombre de usuario y contraseña de nuestra cuenta de [PYPI](https://pypi.org/). Para hacer lo mecionado anteriormente, se ejecuta el siguiente comando: 

> python setup.py sdist && twine upload dist/*

Si el comando `twine upload dist/*` no funciona utilizar el siguiente :

> python setup.py sdist upload -r pypi

**Nota**: Se debe abrir la consola desde la carpeta [raíz](https://github.com/bdinarte/SimuladorVotantes), es decir, al mismo nivel que el archivo `setup.py`.
