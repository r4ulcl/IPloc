#!/usr/bin/python
# -*- coding: UTF-8 -*-


#authors        : Raul Calvo Laorden y Miguel Romeral
#description    : IPloc es un programa en python que utiliza la base de datos publica de GeoLite2 (maxmind.com) y nos da información sobre las IPs que le pasemos por parámetro o en un fichero.
#date           : 2018-05-24
#usage          : python IPloc.py <OPTIONS>
#-----------------------------------------------------------------------------------------------------------

import time

import requests

from datetime import datetime


import json
import csv
import psycopg2
import sys
import pprint
import socket
import psycopg2.extensions
import urllib
import zipfile
import os
import gzip
from configparser import ConfigParser

#Funcion para obtener los datos de la conexion a la base de datos
def config(filename='database.ini', section='postgresql'):
    try:
	parser = ConfigParser()
	parser.read(filename) #leemos el fichero

	db = {}
	params = parser.items(section) #cogemos la seccion postgresql
	for param in params:
	    db[param[0]] = param[1]

	return db
    except:
	print "Error al cargar datos desde database.ini"
	sys.exit(0)
	
def idioma(filename='database.ini', section='idioma'):
    try:
	parser = ConfigParser()
	parser.read(filename) #leemos el fichero

	db = {}
	params = parser.items(section) #cogemos la seccion postgresql
	idioma = "es"
	for param in params:
	    idioma =  param[1]
	    db[param[0]] = param[1]

	return idioma
    except:
	print "Error al cargar datos desde database.ini"
	sys.exit(0)

#Funcion que crea la base de datos e introduce los datos
def insertPostgres():
    con = None
    try:
	#Descargamos y descomprimimos los ficheros de la BDD
	url = 'http://geolite.maxmind.com/download/geoip/database/GeoLite2-City-CSV.zip'
    
	print "downloading GeoLite2-City-CSV.zip"
	urllib.urlretrieve(url, "GeoLite2-City-CSV.zip")
    
	print "Unzipping GeoLite2-City-CSV.zip"
	zip_ref = zipfile.ZipFile("GeoLite2-City-CSV.zip", 'r')
	zip_ref.extractall("/tmp/")
	ficheroCity = zip_ref.namelist()
	carpetaCity=ficheroCity[0].split("/")[0]
	zip_ref.close()
    
    
	url = 'http://geolite.maxmind.com/download/geoip/database/GeoLite2-ASN-CSV.zip'
    
	print "downloading GeoLite2-ASN-CSV.zip"
	urllib.urlretrieve(url, "GeoLite2-ASN-CSV.zip")
    
	print "Unzipping GeoLite2-ASN-CSV.zip"
	zip_ref = zipfile.ZipFile("GeoLite2-ASN-CSV.zip", 'r')
	zip_ref.extractall("/tmp/")
	ficheroASN = zip_ref.namelist()
	carpetaASN=ficheroASN[0].split("/")[0]
	zip_ref.close()


	url = 'http://list.iblocklist.com/?list=xoebmbyexwuiogmbyprb&fileformat=p2p&archiveformat=gz'    
	print "downloading xoebmbyexwuiogmbyprb.gz"
	urllib.urlretrieve(url, "xoebmbyexwuiogmbyprb.gz")
	print "Unzipping xoebmbyexwuiogmbyprb.gz"
	
	inF = gzip.GzipFile("xoebmbyexwuiogmbyprb.gz", 'rb')
	s = inF.read()
	inF.close()

	outF = file("xoebmbyexwuiogmbyprb.txt", 'wb')
	outF.write(s)
	outF.close()
    
    
	#Nos conectamos a la BDD
	try:
	    params = config()
	    con = psycopg2.connect(**params)
	    con.set_client_encoding("utf8")
	except:
	    print "I am unable to connect to the database."
    
	cur = con.cursor()
    
    
	#Creamos las tablas
    
	cur.execute("DROP TABLE IF EXISTS public.asn;")
	cur.execute("CREATE TABLE public.asn(" +
	            "     network inet NOT NULL,"+
	            "     autonomous_system_number integer,"+
	            "     autonomous_system_organization character varying(150),"+
	            "     CONSTRAINT thirdkey PRIMARY KEY (network)"+
	            ")"+
	            "WITH ("+
	            "     OIDS=FALSE"+
	            ");"+
	            "ALTER TABLE public.asn"+
	            "     OWNER TO iploc;")
    
	cur.execute("DROP TABLE IF EXISTS public.cityblocks;")
	cur.execute("CREATE TABLE public.cityblocks ( "+
	            "  network inet NOT NULL,"+
	            "  geoname_id integer,"+
	            "  registered_country_geoname_id integer,"+
	            "  represented_country_geoname_id character varying(10),"+
	            "  is_anonymous_proxy boolean,"+
	            "  is_satellite_provider boolean,"+
	            "  postal_code character varying(100),"+
	            "  latitude real,"+
	            "  longitude real,"+
	            "  accuracy_radius integer,"+
	            "  CONSTRAINT firstkey PRIMARY KEY (network)"+
	            ")"+
	            "WITH ("+
	            "  OIDS=FALSE"+
	            ");"+
	            "ALTER TABLE public.cityblocks"+
	            "  OWNER TO iploc;")
    
	cur.execute("DROP TABLE IF EXISTS public.citylocations;")
	cur.execute("CREATE TABLE public.citylocations("+
	            "  geoname_id integer NOT NULL,"+
	            "  locale_code character varying(10),"+
	            "  continent_code character varying(10),"+
	            "  continent_name character varying(100),"+
	            "  country_iso_code character varying(10),"+
	            "  country_name character varying(100),"+
	            "  subdivision_1_iso_code character varying(10),"+
	            "  subdivision_1_name character varying(100),"+
	            "  subdivision_2_iso_code character varying(10),"+
	            "  subdivision_2_name character varying(100),"+
	            "  city_name character varying(100),"+
	            "  metro_code character varying(10),"+
	            "  time_zone character varying(50),"+
	            "  is_in_european_union boolean,"+
	            "  CONSTRAINT secondkey PRIMARY KEY (geoname_id)"+
	            ")"+
	            "WITH ("+
	            "  OIDS=FALSE"+
	            ");"+
	            "ALTER TABLE public.citylocations"+
	            "  OWNER TO iploc;")
	cur.execute("DROP TABLE IF EXISTS public.tipos;")
	cur.execute("CREATE TABLE tipos ( tipo varchar(10) NOT NULL, inicio inet PRIMARY KEY, final inet NOT NULL )"+
	            "WITH ("+
	            "  OIDS=FALSE"+
	            ");"+
	            "ALTER TABLE public.tipos"+
	            "  OWNER TO iploc;")
    
	con.commit()
    
    except psycopg2.DatabaseError, e:
	print 'Error %s' % e
	print 'Ejecuta ./installRequisites.sh y comprueba que la base de datos esta funcionando.'
	sys.exit(1)
    
    #Insertamos los datos
    
    #obtenemos la ruta del fichero
    ficheroPath="/tmp/"+carpetaASN+"/GeoLite2-ASN-Blocks-IPv4.csv"
    #eliminamos la cabecera del csv
    with open(ficheroPath, 'r') as fin:
	data = fin.read().splitlines(True)
    with open(ficheroPath, 'w') as fout:
	fout.writelines(data[1:])
    #Insertamos los datos
    cur.execute("COPY public.asn FROM '"+ficheroPath+"' CSV ENCODING 'utf-8';")
    
    #obtenemos la ruta del fichero
    ficheroPath="/tmp/"+carpetaCity+"/GeoLite2-City-Blocks-IPv4.csv"
    #eliminamos la cabecera del csv
    with open(ficheroPath, 'r') as fin:
	data = fin.read().splitlines(True)
    with open(ficheroPath, 'w') as fout:
	fout.writelines(data[1:])
    #Insertamos los datos
    cur.execute("COPY public.cityblocks FROM '"+ficheroPath+"' CSV ENCODING 'utf-8';")
    
    #obtenemos la ruta del fichero
    aux=idioma()
    ficheroPath="/tmp/"+carpetaCity+"/GeoLite2-City-Locations-"+str(aux)+".csv"
    #eliminamos la cabecera del csv
    with open(ficheroPath, 'r') as fin:
	data = fin.read().splitlines(True)
    with open(ficheroPath, 'w') as fout:
	fout.writelines(data[1:])
    #Insertamos los datos
    cur.execute("COPY public.citylocations FROM '"+ficheroPath+"' CSV ENCODING 'utf-8';")


    with open('xoebmbyexwuiogmbyprb.txt') as f:
	for line in f.readlines()[2:]:
		reg = line.rstrip().replace(':','-').split('-')
		query = "insert into tipos (tipo, inicio, final) values (\'" + reg[0] + "\',\'" + reg[1] + "\',\'" + reg[2] + "\');"
    		cur.execute(query)

    con.commit()


    
#funcion que obtiene la informacion de una ip y la devuelve en formato resumido
def geoShort(ip):
    con = None
    try:
        params = config()
        con = psycopg2.connect(**params)
	con.set_client_encoding('LATIN1')

	psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

        cur = con.cursor()
        #network, city_name, country_iso_code, postal_code, latitude, longitude
        cur.execute("SELECT network, city_name, country_iso_code, postal_code, latitude, longitude FROM public.cityblocks NATURAL JOIN cityLocations WHERE '"+str(ip)+"' <<  network;")
        colnames = [desc[0] for desc in cur.description]

        rows = cur.fetchall()
        if cur.rowcount == 1: #si hay solo un resultado
            country = rows[0]

            cur.execute("SELECT autonomous_system_organization FROM asn WHERE '"+str(ip)+"' <<  network;")
            colnames2 = [desc[0] for desc in cur.description]
            rows2 = cur.fetchall()

            #unimos las dos salidas
	    if cur.rowcount == 1: #si hay solo un resultado
		colnames = colnames + colnames2
		country = country + rows2[0]


            return dict(zip(colnames,country)) #unimos columnas y valores y lo pasamos a json

        cur.close()

    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
        sys.exit(1)


    finally:
        if con:
            con.close()

#funcion que obtiene la informacion de una ip y la devuelve en formato completo
def geo(ip):
    con = None
    try:
        params = config()
        con = psycopg2.connect(**params)
	con.set_client_encoding('LATIN1')

	psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

        cur = con.cursor()
	cur.execute("SELECT tipo FROM public.tipos WHERE inicio <= \'" + str(ip) + "\' AND final >= \'" + str(ip) + "\';")
	colnames = [desc[0] for desc in cur.description]
	rows = cur.fetchall()
	tipo = None 
	if cur.rowcount == 1:
	    tipo = rows[0]


	cur = con.cursor()

        cur.execute("SELECT  * FROM public.cityblocks NATURAL JOIN cityLocations WHERE '"+str(ip)+"' <<  network;")
        colnames = [desc[0] for desc in cur.description]
	

        rows = cur.fetchall()
        if cur.rowcount == 1: #si hay solo un resultado
            country = rows[0]

            cur.execute("SELECT  * FROM asn WHERE '"+str(ip)+"' <<  network;")
            colnames2 = [desc[0] for desc in cur.description]
            rows2 = cur.fetchall()

            l = ["google_maps"]
	    l2 = ('www.google.com/maps/@'+str(country[7])+','+str(country[8])+',15z',[])
            #unimos las dos salidas
	    if cur.rowcount == 1: #si hay solo un resultado
		colnames = colnames + colnames2 + l
		country = country + rows2[0]+l2
	
	    json = dict(zip(colnames,country)) #unimos columnas y valores y lo pasamos a json

	    if tipo:
		json['type'] = tipo[0]

            return json

        cur.close()

    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
        sys.exit(1)


    finally:

        if con:
            con.close()

#Funcion que comprueba si una IP es valida
def validIP(address):
    try:
        parts = address.split(".")
        if len(parts) != 4:
            return False
        for item in parts:
            if not 0 <= int(item) <= 255:
                return False
        return True
    except ValueError:
        return False

#Funcion para obtener la informacion de una ip  
def getGeo(addr):
    if(not validIP(addr)): #comprobamos si es una ip valida
	try:
	    addr=str(socket.gethostbyname(addr)) #si no es una IP comprobamos hostname
	except:
	    addr=""
    
    if(validIP(addr)):
	socket.inet_aton(addr) 
	if full:
	    jsonAux = geo(addr)
	else:
	    jsonAux = geoShort(addr)
	print "IP: " + addr
	print json.dumps(jsonAux, indent=4, sort_keys=True, ensure_ascii=False).encode('utf8')
    else:
	print addr + " Ip invalida"

COM_HELP = '-h'
COM_VERB = '-v'
COM_FILE = '-f'
COM_INSERT = '-u'

def printHelp():
    print "#authors        : Raul Calvo Laorden y Miguel Romeral"
    print "#description    : IPloc es un programa en python que utiliza la base de datos publica de GeoLite2 (maxmind.com) y nos da información sobre las IPs que le pasemos por parámetro o en un fichero."
    print "#date           : 2018-05-24"
    print "#usage          : python IPloc.py <OPTIONS>"
    print "--------------------------------------------------------------------------------------\n"
    print "OPTIONS: "
    print "  {}:                        Print this message.".format(COM_HELP)
    print "  {}:                        Increase verbosity level".format(COM_VERB)
    print "  {}:                        Update database".format(COM_INSERT)
    print "  {} <FILE>:                 Read IPs from file".format(COM_FILE)

if __name__ == "__main__":

    argu = None         # Indica que estamos usando un argumento
    archivo = []        # Almacena los archivos de las ip.
    full = False        # Modo verbose
    direcciones = []    # Conjunto de direcciones a analizar
    del sys.argv[0]     # Elimino la llamada al programa
    for el in sys.argv:
        # Argumentos unarios (que no necesitan de otro argumento):
        if argu == None:
            # Si coincide con uno de los que necesitan otro argumento, lo guardamos para la siguiente iteracion
            if el in (COM_FILE):
                argu = el
            # A partir de aqui, cada argumento cumple con una funcion
            elif el == COM_VERB:
                full = True
            elif el == COM_HELP:
                printHelp()
                sys.exit()
	    elif el == COM_INSERT:
		insertPostgres()
		sys.exit()		
            else:
                # Si no se trata de ningun argumento, lo tratamos como IP (aunque puede que no lo sea)
                direcciones.append(el)
        else:
            # Aqui realizamos operaciones con los argumentos
            if argu in (COM_FILE):
                archivo.append(el)
            # Limpiamos el argumento guardado
            argu = None

    # Si le hemos pasado archivos:
    if archivo:
        for arc in archivo:
            try:
                # Abrimos el archivo y cogemos la linea (cada linea es una IP)
                with open(arc, 'r') as fp:
                    for line in fp.readlines():
                        direcciones.append(line.replace("\n", ""))
            except IOError:
                print("The file doesn't exist or is not readable.", archivo)
            finally:
                fp.close()

    if not direcciones:
        # Si no tiene argumentos, cogemos la ip de la maquina que la ejecuta
	getGeo(requests.get('https://ipinfo.io/ip').text.rstrip())
    else:
        # Para cada IP, lo consultamos.
        for direc in direcciones:
            getGeo(direc)
