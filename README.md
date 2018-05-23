# IPloc 

IPloc es un programa en python que descarga la base de datos publica de GeoLite2 (maxmind.com), la inserta en una base de datos PosgreSQL y nos da informacion sobre las IPs que le pasame por parametro. 

Se ha utilizado PostgreSQL ya que dispone de un tipo de datos para IPs y redes (inet).

* Traduccion de hostname a IP
	Solo obtiene una ip

## Instalación
### Requisitos
* Linux
* Python

Instalar requisitos ejecutando installRequisites.sh como administrador y seguir los pasos..:

`sudo bash installRequisites.sh`

Ejecutamos insertPostgres.py para actualizar la base de datos postgresql con la base de datos de MaxMind

`python insertPostgres.py`

### Requisitos sin el script de instalacion
* Python
* python-psycopg2
* postgresql
* Python ConfigParser
* Python requests


## Uso
```python
    python IPloc.py <IP> #returns <IP> info
    
    python IPloc.py # returns your public ip info
```


## Agradecimientos
Agradecer a Miguel Romeral ([enlace github](https://github.com/miguelromeral)) por su ayuda en las pruebas y en el código de instalación. 

## TODO
* Instalacion en windows
* Instalacion en MAC OS
* Descarga premium MaxMind
* Elegir idioma de la BDD en la instalacion

## Contacto

mail: raulcalvolaorden@gmail.com

linkedin: https://www.linkedin.com/in/raulcalvolaorden/

## License

GNU General Public License v3.0


This product includes GeoLite2 data created by MaxMind, available from
<a href="http://www.maxmind.com">http://www.maxmind.com</a>.

