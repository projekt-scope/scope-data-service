from flask import Flask, request
from flask_restplus import Api, Resource, fields
import requests
import sys
import rdflib
import random
import os
import datetime

LC_ADDR_fuseki_db = os.environ["LC_ADDR_fuseki_db"]

app = Flask(__name__)

api = Api(
    app=app,
    version="0.1_B",
    title="fuseki-app: API documentation",
    description="with this microservice you can upload, sparql, delete and insert data")

namespace_fuseki = api.namespace('fuseki', description='fuseki_API')

proxies = {
    "http": None,
    "https": None,
}

model_sparql = api.model(
    "sparql_model", {
        "SparqlString":
        fields.String(
            required=True,
            description='make a sparql query',
            example="SELECT ?g ?s ?p ?o WHERE { { ?s ?p ?o }UNION{ GRAPH ?g { ?s ?p ?o } } }"
        )
    })

model_upload = api.model(
    "upload_model", {
        "data":
        fields.String(required=True,
                      description='upload a file',
                      example="enter triples here!"),
    })

model_insert = api.model(
    "insert_model", {
        "SparqlString":
        fields.String(
            required=True,
            description='make a sparql insert query',
            example="INSERT DATA { GRAPH <http://test/test> { <http://test/testtest> <http://test.de/hatEintrag> 'Das ist mein Testeintrag' . } }"
        )
    })

model_delete = api.model(
    "delete_model", {
        "SparqlString":
        fields.String(required=True,
                      description='make a sparql delete query',
                      example="DELETE WHERE {GRAPH ?g {?s ?p ?o }}")
    })

myCharset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def give_me_new_IDs(RangeIDs):
    IDList = []
    for IDs in range(RangeIDs):
        IDList.append('_%s' %
                      ''.join(random.choice(myCharset) for _ in range(8)))
    return IDList


@namespace_fuseki.route("/sparql")
class sparql(Resource):
    @api.doc(responses={
        200: 'OK',
        400: 'Invalid Argument',
        500: 'Mapping Key Error'
    })
    @api.expect(model_sparql)
    def post(self):
        """
        run a SPARQL query 
        powershell Invoke-WebRequest example:
        (Invoke-WebRequest -Uri http://localhost:22631/fuseki/sparql  -Body ((@{SparqlString="SELECT ?g ?s ?p ?o WHERE {{ ?s ?p ?o } UNION { GRAPH ?g { ?s ?p ?o } } }"}) | ConvertTo-Json) -ContentType "application/json" -Method POST).Content
        """
        body = request.json
        url = LC_ADDR_fuseki_db + "/data/sparql"
        payload = body["SparqlString"]

        try:
            r = requests.post(
                url,
                data=payload,
                headers={'content-type': 'application/sparql-query'},
                proxies=proxies)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
            sys.exit()

        return r.json()


@namespace_fuseki.route("/upload")
class uploadData(Resource):
    @api.expect(model_upload)
    def post(self):
        """
        upload a ttl file to the jena fuseki tdb
        powershell Invoke-WebRequest example:
        Invoke-WebRequest -Uri http://localhost:22631/fuseki/upload  -Body ((@{"data" = Get-Content -Raw ./Box1CutTransformedBox2.ttl}) | ConvertTo-Json) -Method POST -ContentType "application/json"
        """
        res = request.json
        resString = res["data"]
        g = rdflib.Graph()
        g.parse(data=resString, format="turtle")
        qres = g.query("""SELECT ?x ?y ?z
        WHERE {
            ?x ?y ?z .
        }""")
        GraphID = give_me_new_IDs(1)[0]
        insertString = "INSERT DATA { GRAPH <http://%s> { " % GraphID
        for row in qres:
            for col in row:
                if isinstance(col, rdflib.term.Literal):
                    insertString += " '%s'" % str(col)
                elif isinstance(col, rdflib.term.BNode):
                    insertString += " _:%s" % str(col)
                elif isinstance(col, rdflib.term.URIRef):
                    insertString += " <%s>" % str(col)
                else:
                    pass

            insertString += " ."
        insertString += " } }"
        url = LC_ADDR_fuseki_db + "/data/update"

        try:
            r = requests.post(
                url,
                data=insertString,
                headers={'content-type': 'application/sparql-update'},
                auth=("admin", "julian_rocks"),
                proxies=proxies)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
            sys.exit()

        return GraphID


@namespace_fuseki.route("/delete")
class deleteData(Resource):
    @api.expect(model_delete)
    def post(self):
        """
        delete data from fuseki
        powershell Invoke-WebRequest example:
        (Invoke-WebRequest -Uri http://localhost:22631/fuseki/delete  -Body ((@{SparqlString="DELETE WHERE {GRAPH ?g {?s ?p ?o }}"}) | ConvertTo-Json) -ContentType "application/json" -Method POST).Content

        """
        body = request.json
        url = LC_ADDR_fuseki_db + "/data/update"
        payload = body["SparqlString"]

        try:
            r = requests.post(
                url,
                data=payload,
                headers={'content-type': 'application/sparql-update'},
                auth=("admin", "julian_rocks"),
                proxies=proxies)
            r.raise_for_status()

        except requests.exceptions.HTTPError as err:
            print(err)
            sys.exit()

        return r.text


@namespace_fuseki.route("/insert")
class insData(Resource):
    @api.expect(model_insert)
    def post(self):
        """
        inserts data into fuseki
        powershell Invoke-WebRequest example:
        (Invoke-WebRequest -Uri http://localhost:22631/fuseki/insert  -Body ((@{SparqlString="INSERT DATA { GRAPH <http://test/test> { <http://test/testtest> <http://test.de/hatEintrag> 'Das ist mein Testeintrag' . } }"}) | ConvertTo-Json) -ContentType "application/json" -Method POST).Content
        """
        body = request.json
        url = LC_ADDR_fuseki_db + "/data/update"
        payload = body["SparqlString"]

        try:
            r = requests.post(
                url,
                data=payload,
                headers={'content-type': 'application/sparql-update'},
                proxies=proxies,
                auth=("admin", "julian_rocks"))
            r.raise_for_status()

        except requests.exceptions.HTTPError as err:
            print(err)
            sys.exit()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=22631)

# print on server ... add file = sys.stderr ...
# print(r["File1"]["value"], file = sys.stderr)
