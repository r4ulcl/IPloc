#!/bin/bash

RED=`tput setaf 1`
GREEN=`tput setaf 2`
NC=`tput sgr0`

# only root can run the script
if [[ $EUID -ne 0 ]]; then
   echo "${RED}This script must be run as an user${NC}" 1>&2
   exit 1
fi

echo "instalamos python-psycopg2" #para postgres en python
sudo apt update
sudo apt-get install python-psycopg2 -y

echo "Instalamos las librerias de python"
sudo apt install python-pip -y 
pip install ConfigParser
pip install requests

echo "Instalamos e iniciamos postgresql"
sudo apt install postgresql -y

echo "Start and Enable PostgreSQL Server"
sudo systemctl start postgresql.service
sudo systemctl enable postgresql.service 


sudo -u postgres dropuser iploc

echo "Creamos el usuario iploc"
if ! sudo -u postgres createuser iploc 2>/dev/null ; then
	echo "No se ha podido crear el usuario iploc. Puede que ya exista."
fi	
echo
echo
# Bucle para comprobar la clave que el usuario introduce
CLAVE_1=""
CLAVE_2=""
typeset -i REPETIR_PWD=1
while [ $REPETIR_PWD -eq 1 ]
do
	echo "Escriba la nueva password para el usuario iploc"
	read -s -p "Password: " CLAVE_1
	echo ""
	read -s -p "Repita el password: " CLAVE_2
	echo ""
	# Verificamos que la clave sea la misma
	if [ $CLAVE_1 = $CLAVE_2 ] ; then
		REPETIR_PWD=0
	else
		echo "Los password no coinciden. Por favor, intentelo de nuevo."
	fi	
done

sudo -u postgres psql -U postgres -d postgres -c "alter user iploc with password '$CLAVE_1';"

echo "[postgresql]
host=localhost
database=iploc
user=iploc
password=$CLAVE_1" > database.ini

#Descomentar para solo ejecutar el programa con root
#chmod 600 database.ini

# Borramos las claves de las variables
unset CLAVE_1
unset CLAVE_2

echo "Creamos la base de datos 'iploc'"
if ! sudo -u postgres createdb iploc -O iploc 2>/dev/null ; then
	echo "No se ha podido crear la base de datos iploc. Puede que ya exista."
fi

function dosql()
{
	sudo -u postgres psql -U postgres -d postgres -c "$1"
}

dosql "GRANT ALL PRIVILEGES ON DATABASE \"iploc\" TO iploc;"
dosql "ALTER USER iploc WITH SUPERUSER "

# Creamos la tabla de tipos de IP
dosql "CREATE TABLE types ( id integer PRIMARY KEY, tipo varchar(10) NOT NULL, inicio cidr NOT NULL, final cidr NOT NULL );"

echo "Instalando curl y gawk"
sudo apt-get install curl -y
sudo apt-get install gawk -y
echo "Descargando el fichero de tipos de IP."
curl -L "http://list.iblocklist.com/?list=xoebmbyexwuiogmbyprb&fileformat=p2p&archiveformat=gz" -o tipos.gz
echo "Insertando las IP en la base de datos."
gunzip "tipos.gz"
tr ':' '-' < tipos > tipos_aux
rm tipos
sed 1,2d tipos_aux | awk -F '-' '{ print "insert into types (id, tipo, inicio, final) values (" NR ",'\''"$1"'\'','\''"$2"'\'','\''"$3"'\'');"} ;' > inserts.sql
rm tipos_aux

sudo -u postgres psql -U postgres -d postgres -f inserts.sql
rm inserts.sql



sudo /etc/init.d/postgresql reload
sudo service postgresql restart



PS3='Seleccione el idioma de la base de datos: '
options=("DE" "EN" "ES" "FR" "JA" "PT-BR" "RU" )
select opt in "${options[@]}"
do
    case $opt in
        "DE")
			IDIOMA="de"
			break
            ;;
        "EN")
			IDIOMA="en"
			break
            ;;
        "ES")
			IDIOMA="es"  
			break          
			;;
        "FR")
            IDIOMA="fr"
			break
			;;
        "JA")
            IDIOMA="ja"
			break
			;;
        "PT-BR")
            IDIOMA="pt-BR"
			break
			;;
        "RU")
            IDIOMA="ru"
			break
			;;
        *) IDIOMA="es" ;;
    esac
done

echo "[idioma]
idioma=$IDIOMA" >> database.ini


#Preguntamos si el usuario quiere que solo pueda el root
#si si ejecutamos aqui inserpostgres
read -p "Instalar para solo root (y/N)?" -n 1 -r
echo    
if [[ $REPLY =~ ^[Yy]$ ]]
then
		chmod 600 database.ini
		python insertPostgres.py
		echo
		echo "Ahora ya puede ejecutar: sudo python IPloc.py <IP>"
fi

python IPloc.py -u

#borramos los ficheros descargador
rm GeoLite2-ASN-CSV.zip
rm GeoLite2-City-CSV.zip
rm -r /tmp/GeoLite2-*

echo 
echo "Ahora ya puede ejecutar: python IPloc.py <IP>"


exit 0
