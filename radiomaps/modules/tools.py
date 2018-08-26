#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *
import xml.etree.ElementTree as ET
import urllib2
import os
from geoip import open_database
import random

def ipv4_generator():
    return str(random.randint(0, 255))+"."+str(random.randint(0, 255))+"."+str(random.randint(0, 255))+"."+str(random.randint(0, 255))

def get_wms_extent(layername='tiger-ny'):
    extent="[[40.679648,-74.047185],[40.882078,-73.907005]]"

    geoserver_getcapabilities = "http://localhost:8080/geoserver/ows?service=wms&version=1.3.0&request=GetCapabilities"
    root = ET.fromstring(urllib2.urlopen(geoserver_getcapabilities).read())

    for capability in root.findall('{http://www.opengis.net/wms}Capability'):
        for masterlayer in capability.findall('{http://www.opengis.net/wms}Layer'):
             for layer in masterlayer.findall('{http://www.opengis.net/wms}Layer'):
                    if (layer.find('{http://www.opengis.net/wms}Name').text==layername):
                        bbox = layer.find('{http://www.opengis.net/wms}BoundingBox').attrib
                        extent = '[[' + bbox['miny'] + ',' + bbox['minx'] +  '],[' + bbox['maxy'] + ',' + bbox['maxx']+']]'
    return extent


#  {ip: 191.189.19.105, subdivisions: frozenset([AM]), location: (-3.1133, -60.0253), country: BR,timezone: America/Manaus, continent:SA}
def get_pos(request_client):
    bd = open_database(os.getcwd()+ "/GeoLite2-City.mmdb")
    if bd.lookup(request_client)!=None:
        resposta_geoip = bd.lookup(request_client).to_dict()
        location = resposta_geoip['location'] # (lat,lng)
        #lat, lng =  [location[0], location[1]]
        pos = str(resposta_geoip).replace("'","")
    else:
        pos = str(request_client) + " não consta no Banco GeoLite2-City"
        location = ('0','0')
    return pos, float(location[0]), float(location[1])



def get_rd_point():
    lat =  random.randint(-90, 89)+random.random()
    lng =  random.randint(-180, 179)+random.random()
    # print str(lat)+", "+str(lng)
    return lat,lng

def pgis():
    import psycopg2
    import pandas
    try:
        conn = psycopg2.connect("dbname='geoserver' user='geoserver' host='localhost' password='geoserver'")
        print "deu certo..."
    except:
        print "N deu pra conectar com a database"
    cur = conn.cursor()
    # cur.execute("SELECT datname from pg_database") # mostra todas as databases
    # cur.execute("SELECT * FROM INFORMATION_SCHEMA.Tables") # mostra as tabelas do db conectado
    # cur.execute("SELECT * FROM INFORMATION_SCHEMA.columns where TABLE_NAME='area';") # mostra as colunas da tabela 'area'
#     cur.execute("INSERT INTO ippos (ip, descricao, pos)  VALUES ('191.189.19.102', '101', ST_geomfromtext('POINT(-44.1 -22)',4326));")
#     cur.execute("INSERT INTO ippos (ip, descricao, pos)  VALUES ('191.189.19.103', '101', ST_geomfromtext('POINT(-44 -22)',4326));")
#     cur.execute("INSERT INTO ippos (ip, descricao, pos)  VALUES ('191.189.19.104', '101', ST_geomfromtext('POINT(-44.1 -22.1)',4326));")
#     cur.execute("INSERT INTO ippos (ip, descricao, pos)  VALUES ('191.189.19.105', '101', ST_geomfromtext('POINT(-44 -22.1)',4326));")
#     cur.execute("INSERT INTO ippos (ip, descricao, pos)  VALUES ('191.189.19.106', '101', ST_geomfromtext('POINT(-44.2 -22.1)',4326));")

# [longitude, latitude]-order: OpenLayers, MapboxGL, KML, GeoJSON, PostGIS, MongoDB, MySQL, GeoServer
# [latitude, longitude]-order: Leaflet, Google Maps API, ArangoDB, GeoIP

    # cur.execute("SELECT i.id,i.ip,i.descricao,ST_AsText(i.pos) FROM ippos AS i;")

#     rows = cur.fetchall()

#     print pandas.DataFrame(rows)

    # Make the changes to the database persistent
    conn.commit()
    # Close communication with the database
    cur.close()
    conn.close()
    return 0
