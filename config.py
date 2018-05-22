#!/usr/bin/python
from configparser import ConfigParser
import sys
 
def config(filename='database.ini', section='postgresql'):
    try:
        parser = ConfigParser()
        # read config file
        parser.read(filename)
     
        # get section, default to postgresql
        db = {}
        #if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
        #else:
        #    raise Exception('Section {0} not found in the {1} file'.format(section, filename))
     
        return db
    except:
        print "Error al cargar datos desde database.ini"
        sys.exit(0)