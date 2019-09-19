import requests
import json
import urllib.request

from rdflib import Graph
import os

import OCC

proxies = {"http": None, "https": None}

ADDR_fuseki_app = os.environ["LC_ADDR_fuseki_app"] + "/fuseki/"
ADDR_geom2str_app = os.environ["LC_ADDR_geom2str_app"] + "/geomStr/"



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


def create_geomstr(resObjList):
    """create_geomstr 
    
    Args:
        resObjList (list): objectlist
    """
    headers = {"content-type": "application/json"}
    url = ADDR_geom2str_app + "create_geomstr"
    payload = {"ResObjList": resObjList}
    print(payload)

    r = requests.post(url, data=json.dumps(payload), headers=headers, proxies=proxies)
    print(r.text)


def read_geomstr(resObjList):
    """read_geomstr 
    
    Args:
        resObjList (liste): objectlist
    
    Returns:
        list: liste with occstrings 
    """

    headers = {"content-type": "application/json", "encoding": "UTF-8"}
    url = ADDR_fuseki_app + "sparql"
    OCCStringList = []
    for obj in resObjList:
        payload = {
            "SparqlString": "PREFIX omg: <https://w3id.org/omg#> SELECT ?g ?s ?p ?o WHERE { GRAPH ?g { <%s> omg:hasOccString ?o } }"
            % obj
        }

        r = requests.post(
            url, data=json.dumps(payload), headers=headers, proxies=proxies
        )

        jsonResp = r.json()

        for elem in jsonResp["results"]["bindings"]:
            OCCStringList.append([obj, elem["o"]["value"]])

    return OCCStringList


def check_for_geomStrings(resObjList):
    """check_for_geomStrings 
    
    Args:
        resObjList (list): objectlist
    
    Returns:
        boolean: returns true if a connection with OccString has been found. Otherwise it returns false.
    """
    headers = {"content-type": "application/json", "encoding": "UTF-8"}
    url = ADDR_fuseki_app + "sparql"
    OCCStringList = []
    for obj in resObjList:
        payload = {
            "SparqlString": "PREFIX omg: <https://w3id.org/omg#> SELECT ?g ?s ?p ?o WHERE { GRAPH ?g { <%s> omg:hasOccString ?o } }"
            % obj
        }
        r = requests.post(
            url, data=json.dumps(payload), headers=headers, proxies=proxies
        )

        jsonResp = r.json()

        for elem in jsonResp["results"]["bindings"]:
            OCCStringList.append([obj, elem["o"]["value"]])
    # print(f"occ string {OCCStringList}")
    if not OCCStringList:
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


def getNamedGraphs():
    """getNamedGraphs This function returns all named graphs which have a hasGeometry connection in it.
    
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


def generate_objlist_TS(nGraph):
    """generate_objlist_TS objectlist from TS
    the function checks if the named graph has geomStrings, if so these will be used otherwise the geomStrings will be created first
    
    Args:
        nGraph (str): named graph
    
    Returns:
        list: objectlist with objects (pythonocc) and uri (Startobject)
    """
    resObjList = createObjList(nGraph)
    # print(f"resObjList {resObjList}")

    # check if geomstr already exist
    if not check_for_geomStrings(resObjList):
        create_geomstr(resObjList)
        print("Geomstring created")
    else:
        print("Geomstrings found")

    # Reads the GeoString from with the objectlist
    OCCList = read_geomstr(resObjList)
    temp_geo_var = []
    objnames = []
    for o in OCCList:
        objnames.append(o[0])
        occString = o[1]
        for line in occString.splitlines():
            exec(line)
        # finde last line with shape object
        last_line = [l2 for l2 in (l1.strip() for l1 in occString.splitlines()) if l2][
            -1
        ]

        temp_geo_var.append(last_line.split("=")[0])

    geo_var = []
    # Creating variables from String and adding it to a list
    for i in temp_geo_var:
        exec("geo_var.append(" + i + ")")

    objlist = list(zip(geo_var, objnames))
    return objlist


def run_sparql(sparql_string):

    headers = {"content-type": "application/json", "encoding": "UTF-8"}
    url = ADDR_fuseki_app + "sparql"
    payload = {
        "SparqlString": sparql_string
    }

    r = requests.post(url, data=json.dumps(payload), headers=headers, proxies=proxies)

    resp = r.json()

    return resp
