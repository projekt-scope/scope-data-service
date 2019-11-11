import requests
from flask import Flask, request, jsonify
from flask_restplus import Api, Resource, fields
import json
import os
import revit2occ
import createTTLString
from threading import Thread
import sys
import TDB_Helpers

LC_ADDR_fuseki_app = os.environ["LC_ADDR_fuseki_app"]
LC_ADDR_geom2pickle_app = os.environ["LC_ADDR_geom2pickle_app"]

#####
# following is not in the env vars: add it if you need it
# LC_ADDR_revit_app = os.environ["LC_ADDR_revit_app"]
#####

# LC_ADDR_fuseki_app = "http://10.200.29.203:22631"
# LC_ADDR_geom2str_app = "http://10.200.29.203:22632"
LC_ADDR_revit_app = "http://127.0.0.1:22633"

proxies = {"http": None, "https": None}

app = Flask(__name__)
api = Api(
    app=app,
    version="0.2",
    title="revit-app: API documentation",
    description="with this microservice you can generate the pythonOCC-Graph from a revit .ttl output",
)

namespace_revitAPI = api.namespace(
    "revitAPI", description="this is the revit-app Endpoint")

model_create_OCCGraph = api.model(
    "create_OCCGRAPH_model",
    {
        "quadID":
        fields.String(
            required=True,
            description="give this endpoint an quadID from a fuseki quad and it will create the pythonOCC Graph for you"
        )
    },
)

model_fetchRevitData = api.model(
    "fetch_Revit_Data_model",
    {
        "RevitJsonData":
        fields.String(required=True,
                      description="send Data from Revit to this Endpoint")
    },
)


def makeRevitToOCC(quadID):
    sparqlAppUrl = LC_ADDR_fuseki_app
    # selectedquadID = "http://quadID%s" % TDB_Helpers.give_me_new_IDs(1)[0]
    pickleQuadID = revit2occ.revit2occ(quadID, sparqlAppUrl)

    process = Thread(target=makeGeom2pickle, args=[pickleQuadID])
    process.start()


def findquadID(projectName):
    headers = {"content-type": "application/json", "encoding": "UTF-8"}
    url = LC_ADDR_fuseki_app + "/fuseki/sparql"
    payload = {
        "SparqlString":
        "SELECT ?g WHERE { GRAPH ?g { ?s ?p '%s' } }" % projectName
    }
    try:
        r = requests.post(url,
                          data=json.dumps(payload),
                          headers=headers,
                          proxies=proxies)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        sys.exit()

    jsonResp = r.json()

    return jsonResp["results"]["bindings"][0]["g"]["value"]


def makeGeom2pickle(selectedquadID):

    headers = {"content-type": "application/json", "encoding": "UTF-8"}
    url = LC_ADDR_fuseki_app + "/fuseki/sparql"
    payload = {
        "SparqlString":
        "PREFIX omg: <https://w3id.org/omg#> SELECT ?o WHERE { GRAPH <%s> { ?s omg:hasGeometry ?o } } "
        % selectedquadID
    }
    try:
        r = requests.post(url,
                          data=json.dumps(payload),
                          headers=headers,
                          proxies=proxies)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        sys.exit()

    jsonResp = r.json()

    ResObjList = []
    for elem in jsonResp["results"]["bindings"]:
        ResObjList.append(elem["o"]["value"])

    json_data = json.dumps({"ResObjList": ResObjList})

    # Note: changed from geom2str to geom2pickle
    url = LC_ADDR_geom2pickle_app + "/geomPickle/create_geomPickle"

    try:
        r = requests.post(url,
                          data=json_data,
                          headers={'content-type': 'application/json'},
                          proxies=proxies)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        sys.exit()

    jsonResp = r.json()


@namespace_revitAPI.route("/createOccGraph")
class createOccGraph(Resource):
    @api.doc(responses={
        200: "OK",
        400: "Invalid Argument",
        500: "Mapping Key Error"
    })
    @api.expect(model_create_OCCGraph)
    def post(self):
        """
        description:
        Invoke-WebRequest -Uri http://localhost:22633/revitAPI/createOccGraph  -Body ((@{"data" = Get-Content -Raw ./Box1CutTransformedBox2.ttl}) | ConvertTo-Json) -Method POST -ContentType "application/json"

        """
        # maybe put selected graph id inside body??
        # body = request.json
        sparqlAppUrl = LC_ADDR_fuseki_app
        selectedquadID = "http://%s" % TDB_Helpers.give_me_new_IDs(1)[0]
        newQuadID = revit2occ.revit2occ(selectedquadID, sparqlAppUrl)

        process = Thread(target=makeGeom2pickle, args=[newQuadID])
        process.start()


@namespace_revitAPI.route("/fetchRevitData")
class fetchRevitData(Resource):
    @api.doc(responses={
        200: "OK",
        400: "Invalid Argument",
        500: "Mapping Key Error"
    })
    @api.expect(model_fetchRevitData)
    def post(self):
        """
        description:
        Comming Soon
        """
        projectID = TDB_Helpers.give_me_new_IDs(1)[0]
        res = request.get_json()
        TTLString = createTTLString.createTTLString(res, projectID)
        data = {}
        data["SparqlString"] = TTLString
        json_data = json.dumps(data)
        url = LC_ADDR_fuseki_app + "/fuseki/insert"

        try:
            r = requests.post(url,
                              data=json_data,
                              headers={'content-type': 'application/json'},
                              proxies=proxies)
            r.raise_for_status()

        except requests.exceptions.HTTPError as err:
            print(err)
            sys.exit()

        quadID = findquadID(res["data"]["ProjectID"])
        makeRevitToOCC(quadID)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=22633)
