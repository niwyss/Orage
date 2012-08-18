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

def __fetch_city_xml_data(host, selector, params, headers, city_name):
    try:
        
        # Reading zipped data from web-server
        conn = httplib.HTTPConnection(host)
        conn.request("POST", selector, params % city_name, headers)
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
    

def __parse_xml_data(xml_data):
    
    try:
        
        doc = xml.dom.minidom.parseString(xml_data)
 
        data = []
        for node in doc.getElementsByTagName("ns2:Lieu"):
        
            lieu = {}
        
            codePostal = __getElementValueByTagName(node, "codePostal")
            libelle = __getElementValueByTagName(node, "libelle")
            lieuId = __getElementValueByTagName(node, "lieuId")
            
            lieu['codePostal'] = codePostal.encode('utf-8', "replace")
            lieu['libelle'] = libelle.encode('utf-8', "replace")
            lieu['id'] = lieuId.encode('utf-8', "replace")

            data.append(lieu)
 
        return data

    except:
        print "orage: error: xml data unparsable"
        sys.exit(0)

def __print_lieus(lieus):
    
    for lieu in lieus:
        print ("{0:25}  {1:10}  {2:10}").format(lieu['libelle'], lieu['codePostal'], lieu['id'])

def search(parameters_path, city_name):

    # Test : parameters.json
    if not os.path.exists(parameters_path):
        print "orage: error: parameters.json doesn't exist. Grab it from anywhere."
        sys.exit(1)
    
    # Get webservice request configuration
    data = open(parameters_path, 'r')
    json_data_parametres = json.loads(data.read())
    data.close()
      
    # Get informations for this station 
    host = json_data_parametres["city"]["host"] 
    selector = json_data_parametres["city"]["selector"] 
    params = json_data_parametres["city"]["params"]
    headers = json_data_parametres["city"]["headers"]
    xml_data = __fetch_city_xml_data(host, selector, params, headers, city_name)
    
    # Parse and print informations
    lieus = __parse_xml_data(xml_data)
    __print_lieus(lieus)
