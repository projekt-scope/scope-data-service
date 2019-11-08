import requests
from flask import Flask, request, jsonify
import recQueryFuncReturn
import os.path
from flask_restplus import Api, Resource, fields
import json
import os, time

LC_ADDR_fuseki_app = os.environ["LC_ADDR_fuseki_app"]
# LC_ADDR_fuseki_app ="http://localhost:22631"

proxies = {"http": None, "https": None}


app = Flask(__name__)
api = Api(
    app=app,
    version="0.1",
    title="geom2pickle-app: API documentation",
    description="with this microservice you can generate the pythonOCC geomPickle",
)

namespace_geomPickle = api.namespace("geomPickle", description="geomPickle_API")

model_create_geompickle = api.model(
    "create_geompickle_model",
    {
        "ResObjList": fields.String(
            required=True,
            description="give this endpoint an ResObjList and it will create the geom Pickle",
        )
    },
)

model_read_geompickle = api.model(
    "read_geompickle_model",
    {
        "fileName": fields.String(
            required=True, description="fetch a geom pickle from the server"
        )
    },
)


@namespace_geomPickle.route("/create_geomPickle")
class createGeomStr(Resource):
    @api.doc(responses={200: "OK", 400: "Invalid Argument", 500: "Mapping Key Error"})
    @api.expect(model_create_geompickle)
    def post(self):
        """
        create the geomPickle from a given identifier(ResObj)
        """

        body = request.json
        s = time.time()
        result = recQueryFuncReturn.pool_handler(body["ResObjList"])
        print("geom2pickle_time: " + str(time.time()-s))
        return result


@namespace_geomPickle.route("/read_geompickle")
class readGeomStr(Resource):
    @api.doc(responses={200: "OK", 400: "Invalid Argument", 500: "Mapping Key Error"})
    @api.expect(model_read_geompickle)
    def post(self):
        
        body = request.json
        headers = {"content-type": "application/json", "encoding": "UTF-8"}
        url = LC_ADDR_fuseki_app + "sparql"
        obj_list = json.loads(body["jsonList"])
        
        dic = {}
        
        for i in obj_list:
            payload = {
                "SparqlString": "PREFIX omg: <https://w3id.org/omg#> SELECT ?g ?s ?p ?o WHERE { GRAPH ?g { <%s> omg:hasOccPickle ?o } }"
                % i
            }
            r = requests.post( url, data=json.dumps(payload), headers=headers, proxies=proxies)
            dic[i] = r.json()  
    
        return json.dumps(dic)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=22635)
