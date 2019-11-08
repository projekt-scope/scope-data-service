import os
import glob
import time
import uuid
import sys
from app import app
from app.api import api_bp as bp


from flask import render_template, request, abort, jsonify, url_for
from app.helper.spaqrlQueries import filterBlanknodes, queryAllFromNode, getOrderedLists

# occ
import OCC
from OCC.Core.gp import gp_Vec
from OCC.Core.Visualization import Tesselator
from OCC import VERSION as OCC_VERSION

from OCC.Extend.TopologyUtils import is_edge, is_wire, discretize_edge, discretize_wire

# import Display from own folder
from app.helper.threejs_rendere_small import generate_json_from_shape

from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeTorus
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Core.gp import gp_Trsf

# rdf
from rdflib import Graph, Namespace
from SPARQLWrapper import SPARQLWrapper, N3
import pickle

# graph visualizer
from app.helper.graph_visualizer_helper import (
    generate_subPredObjList,
    checkPrefixes,
    generate_prefixlist_fromString,
    generate_subPredObjList_forLists,
    generate_subPredObjList_from_TS,
    generate_prefixlist_from_graph,
)

from app.api.scope_service_api_calls import (
    createObjList,
    get_geom_graph,
    getPart,
    getGraph,
    run_sparql,
    generate_objlist_TS_with_pickleServices,
    insert_sparql_bpo
)

prefixStrings = """@prefix occ: <https://projekt-scope.de/ontologies/occ#> .
                        @prefix omg: <https://w3id.org/omg#> .
                        @prefix oop: <https://projekt-scope.de/ontologies/oop#> .
                        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
                        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
                        @prefix xml: <http://www.w3.org/XML/1998/namespace> .
                        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
                        @prefix BIM: <https://projekt-scope.de/ontologies/BIM#> .
                        """
prefixlist = generate_prefixlist_fromString(prefixStrings)


@bp.route("/TS", methods=["POST"])
def api_TS():

    jsonlist = []
    objlist = []
    ttlstring = ""
    if not request.json:
        abort(400)

    data = request.json
    nGraph = data["nGraph"]
    s = time.time()
    objlistPickle = generate_objlist_TS_with_pickleServices(nGraph)
    geom2pickletime = str(time.time() - s)
    geom_graph = get_geom_graph(nGraph)
    subPredObjList = generate_subPredObjList_from_TS(geom_graph, prefixlist)

    # for obj in objlist:
    for obj in objlistPickle:
        try:
            json = generate_json_from_shape(obj[0], obj[1], export_edges=False)
            jsonlist.append(json)
        except Exception as e:
            print(e)
            pass

    data = {
        "jsonIDs": jsonlist,
        "subPredObjs": subPredObjList,
        "ttlstring": str(jsonlist),
    }

    print("[geom2Pickle]  Time: " + geom2pickletime)
    return jsonify(data)


@bp.route("/graph/TS", methods=["POST"])
def api_graph_TS():
    data = request.json
    ttlstring = ""
    simplifylist = data["simplifylist"]
    jsonResp = getPart(data["uri"])
    trimnumber = int(data["trimnumber"])
    # TODO generate from graph (TS)

    subPredObjList = generate_subPredObjList_from_TS(jsonResp, prefixlist)
    subPredObjList = subPredObjList[:trimnumber]
    ttlstring = jsonResp
    data = {"subPredObjs": subPredObjList}

    return jsonify(data)


@bp.route("/sparql/TS", methods=["POST"])
def api_sparql_TS():
    data = request.json
    output = run_sparql(data["sparql"])
    header = output["head"]["vars"]
    results = output["results"]["bindings"]

    list_with_rows = []
    for i in results:
        temp = []
        for a in header:
            if a in i:
                temp.append(i[a]["value"])
            else:
                temp.append("")
        list_with_rows.append(temp)
    d = {"header": header, "rows": list_with_rows}
    return jsonify(d)


@bp.route("/insert/TS", methods=["POST"])
def api_insert_TS():
    data = request.json
    insert_sparql_bpo(data)

    return jsonify(data)
