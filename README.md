# visa-scraping

Este proyecto se centra en la recolección automatizada de información a través de técnicas de web scraping. Su mayor importancia radica en la generación de alertas automáticas cuando se scrapea una página web, lo que permite a los usuarios ser más eficientes en el uso del tiempo y optimizar el proceso de monitoreo de datos.


[[_TOC_]]


## Instalación

1. Se recomienda utilizar Python 3.11. Puedes descargarlo desde el siguiente enlace: https://www.python.org/downloads/

2. Se recomienda realizar la instalación en un [**entorno virtual**]. Dentro del proyecto, encontrarás el ejecutable ```PyEnv.bat```, que crea un entorno virtual en el directorio del proyecto e instala todo lo necesario para ejecutar el flujo especificado en el archivo ```setup.cfg```.


## Ejecución

Antes de ejecutar el proyecto, asegúrate de activar el entorno virtual si estás utilizando uno.

Para ejecutar el archivo principal **ejecution.py** o utiliza el siguiente comando:

```
python -m visa_scraping.ejecution
```

Nota: El proyecto incluye el ejecutable ```PyRun.bat```, que activa el entorno virtual y ejecuta automáticamente el flujo.


## Prerrequisitos

El proyecto ha sido generado para la versión de Python
	```
    3.10
    ```
. Las librerías o paquetes necesarios para la ejecución son:
- `versioneer>=0.10`
- `setuptools>=75.3.0`
- `openpyxl>=3.1.2`
- `pandas>=2.2.3`
- `beautifulsoup4>=4.12.3`
- `selenium>=4.25.0`


## Insumos y resultados

Los insumos utilizados en el proceso son:

| Insumo | Descripción|
| - | - |
| driver_path | Ubicación del web driver dentro del proyecto, definida en el parámetro global driver_path del archivo ```config.json```. |
| user | Nombre de usuario para acceder a la página, definido en el parámetro global user del archivo ```config.json```. |
| password | Contraseña de acceso, definida en el parámetro global password del archivo ```config.json```. |


Los resultados obtenidos son:

| Resultado| Descripción|
| - | - |
| execution_log.csv | Resultado almacenado en la carpeta ```outputs``` de la ejecución en caso de que se encuentre una fecha inferior a la fecha del evento |
