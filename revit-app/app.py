import requests
from flask import Flask, request, jsonify
import os.path
from flask_restplus import Api, Resource, fields
import json
import os
import importGeomData
import rdflib
import sys

LC_ADDR_fuseki_app = os.environ["LC_ADDR_fuseki_app"]
# LC_ADDR_fuseki_app = "http://10.200.29.203:22631"


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
        "GraphID": fields.String(
            required=True,
            description="give this endpoint an GraphId from a fuseki quad and it will create the pythonOCC Graph for you"
        )
    },
)

model_fetchRevitData = api.model(
    "fetch_Revit_Data_model",
    {
        "RevitJsonData": fields.String(
            required=True,
            description="send Data from Revit to this Endpoint"
        )
    },
)


@namespace_revitAPI.route("/createOccGraph")
class createOccGraph(Resource):
    @api.doc(responses={200: "OK", 400: "Invalid Argument", 500: "Mapping Key Error"})
    @api.expect(model_create_OCCGraph)
    def post(self):
        """
        description:
        Invoke-WebRequest -Uri http://localhost:22633/revitAPI/createOccGraph  -Body ((@{"data" = Get-Content -Raw ./Box1CutTransformedBox2.ttl}) | ConvertTo-Json) -Method POST -ContentType "application/json"

        """

        res = request.get_json()
        if not isinstance(res, dict):
            return "Error, wrong datatype provided to createOCCGraph Endpoint"
        if "data" not in res:
            return "Error, wrong JSON provided to createOCCGraph Endpoint, needs key 'data'"
        if "value" not in res["data"]:
            return "Error, wrong JSON provided to createOCCGraph Endpoint, needs key 'value'"

        resString = res["data"]["value"]

        g = rdflib.Graph()
        g.parse(data=resString, format="turtle")

        newGraph = importGeomData.importGeomData(g)

        mergeGraphs = g + newGraph
        # graphWithBot = importGeomData.addBotTriples(g)

        serializedTTL = mergeGraphs.serialize(
            format="turtle")
        TTLString = serializedTTL.decode('utf-8')
        data = {}
        data["data"] = TTLString
        json_data = json.dumps(data)
        url = LC_ADDR_fuseki_app + "/fuseki/upload"
        r = requests.post(url, data=json_data, headers={
                          'content-type': 'application/json'}, proxies=proxies)

        # serializedBotTTL = graphWithBot.serialize(format="turtle")
        # TTLBotString = serializedBotTTL.decode('utf-8')
        # data2 = {}
        # data2["data"] = TTLBotString
        # jsonBOT_data = json.dumps(data2)
        # url = LC_ADDR_fuseki_app + "/fuseki/upload"
        # r = requests.post(url, data=jsonBOT_data, headers={
        #                   'content-type': 'application/json'}, proxies=proxies)

        return "done"


@namespace_revitAPI.route("/fetchRevitData")
class fetchRevitData(Resource):
    @api.doc(responses={200: "OK", 400: "Invalid Argument", 500: "Mapping Key Error"})
    @api.expect(model_fetchRevitData)
    def post(self):
        """
        description:
        Comming Soon
        """
        g = rdflib.Graph()
        res = request.get_json()
        BNdict = {}
        for BN in res["data"]["BlankNodes"]:
            BNdict[BN] = rdflib.BNode()

        for triple in res["data"]["Triples"]:

            if triple[0][:4] == "http" or triple[0][:5] == "https":
                s = rdflib.term.URIRef(triple[0])
            elif triple[0] in BNdict:
                s = BNdict[triple[0]]
            else:
                s = rdflib.Literal(triple[0])

            if triple[1][:4] == "http" or triple[1][:5] == "https":
                p = rdflib.term.URIRef(triple[1])
            elif triple[1] in BNdict:
                p = BNdict[triple[1]]
            else:
                p = rdflib.Literal(triple[1])

            if triple[2][:4] == "http" or triple[2][:5] == "https":
                o = rdflib.term.URIRef(triple[2])
            elif triple[2] in BNdict:
                o = BNdict[triple[2]]
            else:
                o = rdflib.Literal(triple[2])

            g.add((s, p, o))

        for elem in res["data"]["Namespaces"]:
            NameSpaceElem = rdflib.Namespace(res["data"]["Namespaces"][elem])
            g.bind("%s" % elem, NameSpaceElem)

        newGraph = importGeomData.importGeomData(g)
        mergeGraphs = g + newGraph
        # graphWithBot = importGeomData.addBotTriples(g)

        serializedTTL = mergeGraphs.serialize(
            format="turtle")
        TTLString = serializedTTL.decode('utf-8')
        data = {}
        data["data"] = TTLString
        json_data = json.dumps(data)
        url = LC_ADDR_fuseki_app + "/fuseki/upload"
        r = requests.post(url, data=json_data, headers={
                          'content-type': 'application/json'}, proxies=proxies)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=22633)
