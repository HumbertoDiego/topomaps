#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *
import xml.etree.ElementTree as ET
import urllib2
import os
from geoip import open_database
import random

def get_extent(layername='tiger-ny'):
    extent="[[40.679648,-74.047185],[40.882078,-73.907005]]"

    geoserver_getcapabilities = "http://localhost:8080/geoserver/ows?service=wms&version=1.3.0&request=GetCapabilities"
    root = ET.fromstring(urllib2.urlopen(geoserver_getcapabilities).read())

    for capability in root.findall('{http://www.opengis.net/wms}Capability'):
        for masterlayer in capability.findall('{http://www.opengis.net/wms}Layer'):
             for layer in masterlayer.findall('{http://www.opengis.net/wms}Layer'):
                    if (layer.find('{http://www.opengis.net/wms}Name').text==layername):
                        bbox = layer.find('{http://www.opengis.net/wms}BoundingBox').attrib
                        extent = '[[' + bbox['minx'] + ',' + bbox['miny'] +  '],[' + bbox['maxx'] + ',' + bbox['maxy']+']]'
    return extent

def get_pos(request_client):
    bd = open_database(os.getcwd()+ "/GeoLite2-City.mmdb")
    if bd.lookup(request_client)!=None:
        pos = str(bd.lookup(request_client).to_dict()).replace("'","")
    else:
        pos = str(request_client) + " não consta no Banco GeoLite2-City"
    return pos

def get_rd_point():
    lat =  random.randint(-90, 89)+random.random()
    lng =  random.randint(-180, 179)+random.random()
    # print str(lat)+", "+str(lng)
    return lat,lng
