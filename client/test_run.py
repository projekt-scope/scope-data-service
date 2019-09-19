import requests
import json
import argparse
import os

proxies = {
    "http": None,
    "https": None,
}

parser = argparse.ArgumentParser()
parser.add_argument('project_name')
args = parser.parse_args()


dockerIP = "localhost"


LC_ADDR_fuseki_app = "http://" + dockerIP + ":22631"
LC_ADDR_geom2str_app = "http://" + dockerIP + ":22632"
LC_ADDR_revit_app = "http://" + dockerIP + ":22633"
LC_ADDR_render_app = "http://" + dockerIP + ":22634"
LC_ADDR_fuseki_db = "http://" + dockerIP + ":22630"


def add_revit():
    url = LC_ADDR_revit_app + "/revitAPI/createOccGraph"

    filename = "REVIT_" + args.project_name + ".ttl"

    with open(filename) as f:
        json_data = json.dumps({"data": {"value": f.read()}})

    requests.post(url, data=json_data, headers={
                  'content-type': 'application/json'}, proxies=proxies)


def findProjectID(projectName):
    headers = {"content-type": "application/json", "encoding": "UTF-8"}
    url = LC_ADDR_fuseki_app + "/fuseki/sparql"
    payload = {
        "SparqlString": "PREFIX omg: <https://w3id.org/omg#> SELECT ?g WHERE { GRAPH ?g { ?s ?p '%s' } }" % projectName
    }
    r = requests.post(url, data=json.dumps(payload),
                      headers=headers, proxies=proxies)
    jsonResp = r.json()

    return jsonResp["results"]["bindings"][0]["g"]["value"]


def findoccstrID(projectID):
    headers = {"content-type": "application/json", "encoding": "UTF-8"}
    url = LC_ADDR_fuseki_app + "/fuseki/sparql"
    payload = {
        "SparqlString": "PREFIX omg: <https://w3id.org/omg#> SELECT ?o WHERE { GRAPH <%s> { ?s omg:hasGeometry ?o } }" % projectID
    }
    r = requests.post(url, data=json.dumps(payload),
                      headers=headers, proxies=proxies)

    jsonResp = r.json()
    objID = jsonResp["results"]["bindings"][0]["o"]["value"]
    payload = {
        "SparqlString": "PREFIX omg: <https://w3id.org/omg#> SELECT ?g WHERE { GRAPH ?g { ?s ?p <%s> } }" % objID
    }
    r = requests.post(url, data=json.dumps(payload),
                      headers=headers, proxies=proxies)
    jsonResp = r.json()
    return jsonResp["results"]["bindings"][0]["g"]["value"]


def createObjList(projectID):
    headers = {"content-type": "application/json", "encoding": "UTF-8"}
    url = LC_ADDR_fuseki_app + "/fuseki/sparql"
    payload = {
        "SparqlString": "PREFIX omg: <https://w3id.org/omg#> SELECT ?o WHERE { GRAPH <%s> { ?s omg:hasGeometry ?o } }" % projectID
    }
    res = requests.post(url, data=json.dumps(payload),
                        headers=headers, proxies=proxies)
    jsonResp = res.json()
    ResObjList = []
    for elem in jsonResp["results"]["bindings"]:
        ResObjList.append(elem["o"]["value"])
    return ResObjList


def create_geomstr(resObjList):
    headers = {"content-type": "application/json"}
    url = LC_ADDR_geom2str_app + "/geomStr/create_geomstr"
    payload = {"ResObjList": resObjList}
    r = requests.post(url, data=json.dumps(payload),
                      headers=headers, proxies=proxies)
    return(r.text)


def add_occstr(projectID):
    resObjList = createObjList(projectID)
    create_geomstr(resObjList)


if __name__ == "__main__":

    add_revit()
    projectID = findProjectID(args.project_name)
    print(projectID)
    add_occstr(projectID)
    occstrID = findoccstrID(projectID)
    print(occstrID)
