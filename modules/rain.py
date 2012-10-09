#!/usr/bin/python
# -*- coding:utf-8 -*-
#
# Orage : weather forecast in your shell
# Copyright 2012 Nicolas Wyss
#
# This file is part of Orage.
#
# Orage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Orage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Orage.  If not, see <http://www.gnu.org/licenses/>.

import json
import sys
import httplib
import os
import gzip
from   StringIO          import StringIO
import xml.dom.minidom
from   xml.dom.minidom   import Node
import datetime

traduction = {
    '0' : 'Pas de données disponibles',
    '1' : 'Pas de pluie',
    '2' : 'Pluie faible',
    '3' : 'Pluie modérée',
    '4' : 'Pluie forte',
    '5' : '5',
    '6' : '6',
    '7' : '7',
    '8' : '8',
    '9' : '9'
}

def __fetch_weather_xml_data(host, selector, params, headers, city_id):
    try:
        
        # Reading zipped data from web-server
        conn = httplib.HTTPConnection(host)
        conn.request("POST", selector, params % city_id, headers)
        response = conn.getresponse()
        raw_data = response.read()
        conn.close() 

        # Descompress raw data
        gzip_reader = gzip.GzipFile(fileobj=StringIO(raw_data))
        xml_data = gzip_reader.read()
        gzip_reader.close()
        
        return xml_data

    except:
        print "orage: error: web service unreachable."
        sys.exit(0)

def __getElementValueByTagName(node, tagName):
    
    value = ''

    if node and tagName and len(tagName) > 0:
        children = node.getElementsByTagName(tagName)
        for child in children:
            for grandchild in child.childNodes:
                if grandchild.nodeType == Node.TEXT_NODE:
                    value += grandchild.data

    return value
    

def __get_forecasts_from_xml_data(xml_data):
    
    try:
        
        doc = xml.dom.minidom.parseString(xml_data)
        raw_data = doc.getElementsByTagName("data")[0].childNodes[0].data
        data = ''.join(raw_data.split())

        return data

    except:
        print "orage: error: xml data unparsable"
        sys.exit(0)

def __print_forecasts(forecasts):

    now = datetime.datetime.now()

    # Start
    print ("[xx:xx - {0}]  {1}").format(now.strftime("%H:%M"), traduction[forecasts[0]])

    # First Half an hour
    for i in range(1, 7):
        start = now.strftime("%H:%M")
        end = (now + datetime.timedelta(minutes=5)).strftime("%H:%M")
        print ("[{0} - {1}]  {2}").format(start, end, traduction[forecasts[i]])
        now += datetime.timedelta(minutes=5)

    # Next Half an hour
    for i in range(7, 10):
        start = now.strftime("%H:%M")
        end = (now + datetime.timedelta(minutes=10)).strftime("%H:%M")
        print ("[{0} - {1}]  {2}").format(start, end, traduction[forecasts[i]]) 
        now += datetime.timedelta(minutes=10)
        
def search(parameters_path, city_id):

    # Test : parameters.json
    if not os.path.exists(parameters_path):
        print "orage: error: parameters.json doesn't exist. Grab it from anywhere."
        sys.exit(1)
    
    # Get webservice request configuration
    data = open(parameters_path, 'r')
    json_data_parametres = json.loads(data.read())
    data.close()
      
    # Get informations for this station 
    host = json_data_parametres["weather"]["host"] 
    selector = json_data_parametres["weather"]["selector"] 
    params = json_data_parametres["weather"]["params"]
    headers = json_data_parametres["weather"]["headers"]
    xml_data = __fetch_weather_xml_data(host, selector, params, headers, city_id)

    # Parse and print informations
    forecasts = __get_forecasts_from_xml_data(xml_data)
    __print_forecasts(forecasts)

