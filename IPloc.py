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
from config import config

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
    if(validIP(addr)):
	socket.inet_aton(addr) #si es ip valida sigue. se usa?
	if full:
	    jsonAux = geo(addr)
	else:
	    jsonAux = geoShort(addr)
	print "IP: " + addr
	print json.dumps(jsonAux, indent=4, sort_keys=True, ensure_ascii=False).encode('utf8')
    else:
	print addr + ": Ip invalida"

def printHelp():
    print "author         : Raul Calvo Laorden (raulcalvolaorden@gmail.com)"
    print "description    : "
    print "date           : 2018-05-24"
    print "usage          : python IPloc.py <IP>"
    print "--------------------------------------------------------------------------------------\n"
    print "Opciones: "
    print "  -h:                        Print this message."
    print "  -v                         Increase verbosity level"

if __name__ == "__main__":

    if len(sys.argv) > 1 and str(sys.argv[1]) =="-h":
        printHelp()
    else:
	contador=0
	full=False
	for ip in sys.argv:
	    if contador == 0:
		if len(sys.argv) == 1:
		    addr=requests.get('https://ipinfo.io/ip').text.rstrip() #si no le pasamos ningun parametro devuelve la ip de la maquina que la ejecuta
		    getGeo(addr)
	    elif contador==1 and str(sys.argv[contador]) =="-v":
		full=True
		if len(sys.argv) == 2:
		    addr=requests.get('https://ipinfo.io/ip').text.rstrip()   #si no le pasamos ningun parametro devuelve la ip de la maquina que la ejecuta
		    getGeo(addr)
	    else:
		addr = ip
		getGeo(addr)
	    contador+=1

