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

from app.OCC_helper import generate_objlist

# rdf
from rdflib import Graph, Namespace
from SPARQLWrapper import SPARQLWrapper, N3

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
    create_geomstr,
    read_geomstr,
    check_for_geomStrings,
    get_geom_graph,
    getPart,
    getGraph,
    generate_objlist_TS,
    run_sparql
)


@bp.route("/", methods=["POST"])
def api():

    jsonlist = []
    objlist = []
    prefixlist = []
    ttlstring = ""
    if not request.json:
        abort(400)

    data = request.json
    if "file" in data:
        filename = data["file"]
        print(f"filename: {filename}")
        try:
            g = Graph()
            g.load("src/app/render/ttlExamples/" + filename + ".ttl", format="turtle")

            # ToDo generate prefixlist out of ttl
            ttlstring = g.serialize(format="turtle").decode("utf-8")

        except Exception as e:
            print(e)
            return "File not found!"

    if "ttl" in data:
        ttlstring = data["ttl"]
        prefixlist = generate_prefixlist_fromString(ttlstring)

        try:
            g = Graph()
            g.parse(format="ttl", data=ttlstring)

        except Exception as e:
            print(e)
            return "no valid ttl"
        ttlstring = ""

    objlist = generate_objlist(g)

    # at the moment the query needs to be a construct query so the response is a graph and can be used as a graph
    qres = g.query(
        """PREFIX omg:	<https://w3id.org/omg#>
                construct {}
            WHERE
                {
            ?s omg:hasGeometry ?o ;
                }"""
    )

    subPredObjList = generate_subPredObjList(qres, prefixlist)

    for obj in objlist:
        try:
            # print(obj[1].split("#")[-1])
            json = generate_json_from_shape(obj[0], obj[1], export_edges=False)
            jsonlist.append(json)
        except Exception as e:
            print(e)
            pass
    data = {"jsonIDs": jsonlist, "subPredObjs": subPredObjList, "ttlstring": ttlstring}

    return jsonify(data)


@bp.route("/TS", methods=["POST"])
def api_TS():

    jsonlist = []
    objlist = []
    prefixlist = []
    ttlstring = ""
    if not request.json:
        abort(400)

    data = request.json
    nGraph = data["nGraph"]
    graph = getGraph(nGraph)
    objlist = generate_objlist_TS(nGraph)
    
    geom_graph = get_geom_graph(nGraph)
    prefixlist = generate_prefixlist_from_graph(geom_graph)
    subPredObjList = generate_subPredObjList_from_TS(geom_graph, prefixlist)

    # prefixStrings = """@prefix occ: <https://projekt-scope.de/ontologies/occ#> .
    #                     @prefix omg: <https://w3id.org/omg#> .
    #                     @prefix oop: <https://projekt-scope.de/ontologies/oop#> .
    #                     @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    #                     @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    #                     @prefix xml: <http://www.w3.org/XML/1998/namespace> .
    #                     @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
    #                     """
    # prefixlist = generate_prefixlist_fromString(prefixStrings)
    # geom_graph = get_geom_graph(nGraph)
    # subPredObjList = generate_subPredObjList_from_TS(geom_graph, prefixlist)

    for obj in objlist:
        try:
            # print(obj[1].split("#")[-1])
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

    return jsonify(data)


@bp.route("/graph/", methods=["POST"])
def api_graph():
    data = request.json
    prefixlist = []
    ttlstring = ""
    simplifylist = data["simplifylist"]
    if "ttl" in data:
        ttlstring = data["ttl"]
        prefixlist = generate_prefixlist_fromString(ttlstring)

        try:
            g = Graph()
            g.parse(format="ttl", data=ttlstring)

        except Exception as e:
            print(e)
            return "no valid ttl"
        ttlstring = ""

    qres = queryAllFromNode(data["uri"], g)
    subPredObjList = []
    if simplifylist:
        #  get all liste geordnet und subPredObjList hinzufügen
        response = getOrderedLists(qres)
        subPredObjList = generate_subPredObjList_forLists(response, prefixlist)

        # alle blank nodes raus löschen
        qres = filterBlanknodes(qres)
    # liste appenden nicht überschreiben
    subPredObjList.extend(generate_subPredObjList(qres, prefixlist))

    data = {"subPredObjs": subPredObjList}

    return jsonify(data)


@bp.route("/graph/TS", methods=["POST"])
def api_graph_TS():
    data = request.json
    prefixlist = []
    ttlstring = ""
    simplifylist = data["simplifylist"]
    jsonResp = getPart(data["uri"])
    # TODO generate from graph (TS)
    prefixStrings = """@prefix occ: <https://projekt-scope.de/ontologies/occ#> .
                        @prefix omg: <https://w3id.org/omg#> .
                        @prefix oop: <https://projekt-scope.de/ontologies/oop#> .
                        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
                        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
                        @prefix xml: <http://www.w3.org/XML/1998/namespace> .
                        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
                        """

    prefixlist = generate_prefixlist_fromString(prefixStrings)
    subPredObjList = generate_subPredObjList_from_TS(jsonResp, prefixlist)
    ttlstring = jsonResp
    # -------------------------------- old --------------------------------------------#
    # qres = queryAllFromNode(data["uri"], g)

    # subPredObjList = []
    # if simplifylist:
    #     #  get all liste geordnet und subPredObjList hinzufügen
    #     response = getOrderedLists(qres)
    #     subPredObjList = generate_subPredObjList_forLists(response, prefixlist)

    #     # alle blank nodes raus löschen
    #     qres = filterBlanknodes(qres)
    # # liste appenden nicht überschreiben
    # subPredObjList.extend(generate_subPredObjList(qres, prefixlist))

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

@bp.route("/TS/test", methods=["POST"])
def api_new_test():
    
    data = request.json

    data = {"Bauteil": data["TS"]}
    return jsonify(data)

