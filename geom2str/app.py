import requests
from flask import Flask, request, jsonify
import recQueryFuncReturn
import os.path
from flask_restplus import Api, Resource, fields
import json
import os

LC_ADDR_fuseki_app = os.environ["LC_ADDR_fuseki_app"]

proxies = {"http": None, "https": None}


app = Flask(__name__)
api = Api(
    app=app,
    version="0.2",
    title="geom2str-app: API documentation",
    description="with this microservice you can generate the pythonOCC geomString",
)

namespace_geomStr = api.namespace("geomStr", description="geomStr_API")

model_create_geomstr = api.model(
    "create_geomstr_model",
    {
        "ResObjList": fields.String(
            required=True,
            description="give this endpoint an ResObjList and it will create the geom String",
        )
    },
)

model_read_geomstr = api.model(
    "read_geomstr_model",
    {
        "fileName": fields.String(
            required=True, description="fetch a geomstring from the server"
        )
    },
)


@namespace_geomStr.route("/create_geomstr")
class createGeomStr(Resource):
    @api.doc(responses={200: "OK", 400: "Invalid Argument", 500: "Mapping Key Error"})
    @api.expect(model_create_geomstr)
    def post(self):
        """
        create the geomString from a given identifier(ResObj)
        """

        body = request.json

        result = recQueryFuncReturn.pool_handler(body["ResObjList"])
        return result


@namespace_geomStr.route("/read_geomstr")
class readGeomStr(Resource):
    @api.doc(responses={200: "OK", 400: "Invalid Argument", 500: "Mapping Key Error"})
    @api.expect(model_read_geomstr)
    def post(self):
        """
        fetch a geomString from the server
        """
        headers = {"content-type": "application/json", "encoding": "UTF-8"}
        url = LC_ADDR_fuseki_app + "/fuseki/sparql"
        body = request.json
        payload = {
            "SparqlString": "SELECT ?s ?p ?o FROM %s WHERE { ?s ?p ?o } " % body["GrahpID"]}
        r = requests.post(url, data=json.dumps(payload),
                          headers=headers, proxies=proxies)
        jsonResp = r.json()
        resString = ""
        for elem in jsonResp["results"]["bindings"]:
            resString += elem["o"]["value"]
            resString += "\n"
        print(resString)

        return resString


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=22632)
