# IPloc

## Introducción

IPloc es un programa en python que utiliza la base de datos publica de GeoLite2 (maxmind.com) y nos da información sobre las IPs que le pasemos por parámetro o en un fichero.

Se ha utilizado PostgreSQL ya que dispone de un tipo de datos para IPs y redes (inet).

## Funcionalidades
* Geo localización de IPs en modo resumido y verbose.

* Traducción de hostname a IP

* Lectura de IPs desde uno o varios ficheros

* Elegir idioma de la BDD en la instalación

* Incluye la base de datos proxy de iblocklist.com, con proxies y nodos TOR

## Instalación
### Requisitos
* Linux
* Python

Instalar requisitos ejecutando installRequisites.sh como administrador:

`sudo bash installRequisites.sh`

Nos preguntara una contraseña para el usuario geoip de postgresl que debemos introducir dos veces, el idioma para las ciudades de la base de datos y si queremos que se instale solo para root. De esta forma solo un usuario con permisos de administrador podrá ejecutar el programa, pero el fichero con la contraseña de postgres solo podrá leerla un administrador.

### Requisitos sin el script de instalación
* Python
* python-psycopg2
* postgresql
* Python ConfigParser
* Python requests

## Uso

Para actualizara la base de datos (se recomienda mensualmente):
```python
   python IPloc.py -u;
```

Para obtener la información de una IP o más:
```python
   python IPloc.py <IP>;
   python IPloc.py <IP1> <IP2> <IP3>
```

Para obtener la información de nuestra IP publica:
```python
   python IPloc.py
```

Para obtener la información de una lista de IPs desde un fichero :
```python
   python IPloc.py -f <fichero>;
   python IPloc.py -f <fichero1> -f <fichero2> -f <fichero3>
```

Para obtener la información de un hostname se pueden utilizar los mismos comandos comentados anteriormente pero sustituyendo las IPs por hostnames

## TODO
* Instalación en windows
* Instalación en MAC OS
* Descarga premium MaxMind
* Mover la creacion de las tablas al instalador

## Autores

### Raúl Calvo Laorden

Mail: raulcalvolaorden@gmail.com

Linkedin: https://www.linkedin.com/in/raulcalvolaorden/

### Miguel Romeral

Mail: miguelangel.garciar@edu.uah.es

LinkedIn: (https://www.linkedin.com/in/miguelromeral/)

## License

GNU General Public License v3.0

This product includes GeoLite2 data created by MaxMind, available from <a href="http://www.maxmind.com">http://www.maxmind.com</a> and proxy list by Bluetack, available from <a href="https://www.iblocklist.com">https://www.iblocklist.com</a>
