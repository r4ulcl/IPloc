#!/usr/bin/python
# -*- coding: UTF-8 -*-


#author         : Raul Calvo Laorden (raulcalvolaorden@gmail.com)
#description    :
#date           : 2018-05-24
#usage          : python IPloc.py <IP>
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


            return dict(zip(colnames,country)) #unimos columnas y valores y lo pasamos a json

        cur.close()

    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
        sys.exit(1)


    finally:

        if con:
            con.close()


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

def getGeo(addr):
    if(not validIP(addr)):
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

def printHelp():
    print "author         : Raul Calvo Laorden (raulcalvolaorden@gmail.com)"
    print "description    : "
    print "date           : 2018-05-24"
    print "usage          : python IPloc.py OPTIONS"
    print "--------------------------------------------------------------------------------------\n"
    print "OPTIONS: "
    print "  {}:                        Print this message.".format(COM_HELP)
    print "  {}:                        Increase verbosity level".format(COM_VERB)
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
        # Si no tiene argumentos, cogemos nuestra propia IP
	getGeo(requests.get('https://ipinfo.io/ip').text.rstrip()) #si no le pasamos ningun parametro devuelve la ip de la maquina que la ejecuta
    else:
        # Para cada IP, lo consultamos.
        for direc in direcciones:
            getGeo(direc)
