#!/usr/bin/python
# -*- coding: utf-8 -*-

import psycopg2
import sys
import urllib
import zipfile
import os
from config import config
#sudo apt-get install python-psycopg2
#sudo service postgres start
#sudo -u postgres createuser postgres
#sudo -u postgres createdb geoip -O postgres
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


    #Nos conectamos a la BDD
    try:
        params = config()
        con = psycopg2.connect(**params)
        #con = psycopg2.connect("dbname=geoip user=geoip password=postgrespassword")
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
                "     OWNER TO geoip;")

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
                "  OWNER TO geoip;")

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
                "  OWNER TO geoip;")

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
ficheroPath="/tmp/"+carpetaCity+"/GeoLite2-City-Locations-es.csv"
#eliminamos la cabecera del csv
with open(ficheroPath, 'r') as fin:
    data = fin.read().splitlines(True)
with open(ficheroPath, 'w') as fout:
    fout.writelines(data[1:])
#Insertamos los datos
cur.execute("COPY public.citylocations FROM '"+ficheroPath+"' CSV ENCODING 'utf-8';")
con.commit()



#sudo apt-get install python-psycopg2
