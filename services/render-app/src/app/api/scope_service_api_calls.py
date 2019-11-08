import requests
import json
import urllib.request

from rdflib import Graph
import os

import OCC
import pickle
import jsonpickle
import time
import random
import string

proxies = {"http": None, "https": None}

ADDR_fuseki_app = os.environ["LC_ADDR_fuseki_app"] + "/fuseki/"
ADDR_geom2pickle_app = os.environ["LC_ADDR_geom2pickle_app"] + "/geomPickle/"


def createObjList(nGraph):
    """createObjList 
    This function generates a list for with all nodes from a named graph which have a omg:hasGeometry connection.
    
    Args:
        nGraph (str): named graph
    
    Returns:
        list: objectlist
    """
    headers = {"content-type": "application/json", "encoding": "UTF-8"}
    url = ADDR_fuseki_app + "sparql"
    payload = {
        "SparqlString": "PREFIX omg: <https://w3id.org/omg#> SELECT ?g ?s ?p ?o WHERE { GRAPH <%s> { ?s omg:hasGeometry ?o } }"
        % nGraph
    }

    r = requests.post(url, data=json.dumps(payload), headers=headers, proxies=proxies)

    jsonResp = r.json()

    ResObjList = []
    for elem in jsonResp["results"]["bindings"]:
        ResObjList.append(elem["o"]["value"])

    return ResObjList


# -----------------Pickle Services--------------------#


def create_geompickle(resObjList):
    """create_geompickle
    
    Args:
        resObjList (list): objectlist
    """
    headers = {"content-type": "application/json"}
    url = ADDR_geom2pickle_app + "create_geomPickle"
    payload = {"ResObjList": resObjList}
    print(payload)
    r = requests.post(url, data=json.dumps(payload), headers=headers, proxies=proxies)
    print(r.text)


def read_geompickle(resObjList):
    """read_geompickle
    
    Args:
        resObjList (liste): objectlist
    
    Returns:
        list: liste with occpickles 
    """
    headers = {"content-type": "application/json", "encoding": "UTF-8"}
    url = ADDR_fuseki_app + "sparql"
    OCCPickleList = []
    for obj in resObjList:
        payload = {
            "SparqlString": "PREFIX omg: <https://w3id.org/omg#> SELECT ?g ?s ?p ?o WHERE { GRAPH ?g { <%s> omg:hasOccPickle ?o } }"
            % obj
        }

        r = requests.post(
            url, data=json.dumps(payload), headers=headers, proxies=proxies
        )

        jsonResp = r.json()

        for elem in jsonResp["results"]["bindings"]:
            o = jsonpickle.decode(
                str(json.loads(elem["o"]["value"], strict=False)).replace("'", '"')
            )
            OCCPickleList.append([obj, o])

    return OCCPickleList


def check_for_geomPickles(resObjList):
    """check_for_geomPickles 
    
    Args:
        resObjList (list): objectlist
    
    Returns:
        boolean: returns true if a connection with OccPickle has been found. Otherwise it returns false.
    """
    headers = {"content-type": "application/json", "encoding": "UTF-8"}
    url = ADDR_fuseki_app + "sparql"
    OCCPickleList = []
    for obj in resObjList:
        payload = {
            "SparqlString": "PREFIX omg: <https://w3id.org/omg#> SELECT ?g ?s ?p ?o WHERE { GRAPH ?g { <%s> omg:hasOccPickle ?o } }"
            % obj
        }
        r = requests.post(
            url, data=json.dumps(payload), headers=headers, proxies=proxies
        )

        jsonResp = r.json()

        for elem in jsonResp["results"]["bindings"]:
            OCCPickleList.append([obj, elem["o"]["value"]])

    if not OCCPickleList:
        return False
    return True


def getGraph(nGraph):
    """getGraph 
    This function returns the whole named graph. 
    TODO return for whole graph
    Args:
        nGraph (str): named graph
    
    Returns:
        list: list of object from the graph.
    """
    headers = {"content-type": "application/json", "encoding": "UTF-8"}
    url = ADDR_fuseki_app + "sparql"
    payload = {
        "SparqlString": """PREFIX omg: <https://w3id.org/omg#>
                            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                            PREFIX owl: <http://www.w3.org/2002/07/owl#>
                            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                            PREFIX oop: <https://projekt-scope.de/ontologies/oop#>
                            PREFIX occ: <https://projekt-scope.de/ontologies/occ#> 
                            SELECT ?g ?s ?p ?o WHERE { GRAPH <%s> { ?s ?p ?o } }"""
        % nGraph
    }
    r = requests.post(url, data=json.dumps(payload), headers=headers, proxies=proxies)

    jsonResp = r.json()

    ResObjList = []
    for elem in jsonResp["results"]["bindings"]:
        ResObjList.append(elem["o"]["value"])

    return ResObjList


def getPart(uri):
    """getPart searches parts of a graph

    Args:
        uri (str): the uri of the item
    
    Returns:
        json: Sparql Result of the query which return every subject, predicate and object down from the uri
    """

    headers = {"content-type": "application/json", "encoding": "UTF-8"}
    url = ADDR_fuseki_app + "sparql"

    payload = {
        "SparqlString": "prefix x: <urn:ex:> Select ?g ?s ?p ?o  where { GRAPH ?g { <%s> (x:|!x:)* ?s . ?s ?p ?o . }}"
        % uri
    }

    r = requests.post(url, data=json.dumps(payload), headers=headers, proxies=proxies)

    jsonResp = r.json()

    return jsonResp


def get_named_graphs():
    """get_named_graphs This function returns all named graphs which have a hasGeometry connection in it.
    
    Returns:
        list: unique names of the graphs 
    """

    headers = {"content-type": "application/json", "encoding": "UTF-8"}
    url = ADDR_fuseki_app + "sparql"
    payload = {
        "SparqlString": "PREFIX omg: <https://w3id.org/omg#> SELECT ?g WHERE { GRAPH ?g  {?s omg:hasGeometry ?o } }"
    }

    r = requests.post(url, data=json.dumps(payload), headers=headers, proxies=proxies)

    jsonResp = r.json()

    nGraphList = []
    for elem in jsonResp["results"]["bindings"]:
        nGraphList.append(elem["g"]["value"])
    # unique named graphs
    uniList = set(nGraphList)
    return uniList


def get_geom_graph(nGraph):
    """get_geom_graph searches for hasGeometry connections
    
    Args:
        nGraph (str): named graph
    
    Returns:
        json: subject predicate object list from the sparql result
    """

    headers = {"content-type": "application/json", "encoding": "UTF-8"}
    url = ADDR_fuseki_app + "sparql"
    payload = {
        "SparqlString": "PREFIX omg: <https://w3id.org/omg#> SELECT ?g ?s ?p ?o WHERE { GRAPH <%s> { ?s omg:hasGeometry ?o . ?s ?p ?o. } }"
        % nGraph
    }

    r = requests.post(url, data=json.dumps(payload), headers=headers, proxies=proxies)
    jsonResp = r.json()

    return jsonResp


def generate_objlist_TS_with_pickleServices(nGraph):
    """generate_objlist_TS objectlist from TS
    the function checks if the named graph has geomStrings, if so these will be used otherwise the geomStrings will be created first
    
    Args:
        nGraph (str): named graph
    
    Returns:
        list: objectlist with objects (pythonocc) and uri (Startobject)
    """
    resObjList = createObjList(nGraph)

    # check if geomstr already exist
    if not check_for_geomPickles(resObjList):
        create_geompickle(resObjList)
        # print("Geompickle created")
    # else:
        # print("Geompickle found")

    # Reads the GeoPickle from with the objectlist
    OCCList = read_geompickle(resObjList)

    geo_obj = []
    objnames = []
    for o in OCCList:
        objnames.append(o[0])
        geo_obj.append(o[1])

    objlist = list(zip(geo_obj, objnames))
    return objlist


def run_sparql(sparql_string):

    headers = {"content-type": "application/json", "encoding": "UTF-8"}
    url = ADDR_fuseki_app + "sparql"
    payload = {"SparqlString": sparql_string}

    r = requests.post(url, data=json.dumps(payload), headers=headers, proxies=proxies)

    resp = r.json()

    return resp

def insert_sparql_bpo(data):

    graph = data["graph"]
    element = data["elem"]
    attr = data["attr"]
    value = data["value"]
    headers = {"content-type": "application/json", "encoding": "UTF-8"}

    # Create the node
    ur = "http://projekt-scope.de/attribute#_" + "".join(
        random.choice(string.ascii_uppercase) for _ in range(8)
    )
    url = ADDR_fuseki_app + "insert"
    payload = {
        "SparqlString": """INSERT DATA { GRAPH <%s>  { <%s> <https://www.w3id.org/bpo#hasAttribute> <%s> . } } """
        % (graph, element, ur)
    }

    r = requests.post(url, data=json.dumps(payload), headers=headers, proxies=proxies)

    # ToDO add real GUID from BSSD API
    # Insert the value
    url = ADDR_fuseki_app + "insert"
    payload = {
        "SparqlString": """INSERT DATA { GRAPH <%s> 
        { <%s>
        <https://schema.org#value> "%s"^^<http://www.w3.org/2001/XMLSchema#string> . 
         <%s> <https://www.w3id.org/bpo#hasBSDDGUID> "%s" .
        } }"""
        % (graph, ur, value,ur,attr)
    }

    r = requests.post(url, data=json.dumps(payload), headers=headers, proxies=proxies)

    # Insert the rdf types
    url = ADDR_fuseki_app + "insert"
    payload = {
        "SparqlString": """INSERT DATA { GRAPH <%s> 
        {
        <%s>
       <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <https://www.w3id.org/bpo#Attribute> .
        } }"""
        % (graph, ur)
    }

    r = requests.post(url, data=json.dumps(payload), headers=headers, proxies=proxies)

    return payload

