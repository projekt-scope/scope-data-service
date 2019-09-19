import os
import glob
import time
import uuid
import sys
from app import app
from flask import render_template, request, abort, jsonify, url_for
from app.helper.spaqrlQueries import filterBlanknodes, queryAllFromNode, getOrderedLists

# import json

# occ

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
)

from app.api.scope_service_api_calls import getNamedGraphs

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/ttl", methods=["GET"])
def ttl():

    examples = generate_example_links()
    delet_old_json()

    return render_template("render_file_based.html", examples=examples)


@app.route("/TS", methods=["GET"])
@app.route("/ts", methods=["GET"])
@app.route("/Ts", methods=["GET"])
def homeTS():

    examples = getNamedGraphs()
    delet_old_json()

    return render_template("render_TS_based.html", examples=examples)


def generate_example_links():
    # generates a list for existing ttl files in folder
    examples = []
    dirpath = os.getcwd()
    path = os.path.join(dirpath, "src/app/render/ttlExamples")
    for file in glob.glob(path + "/*.ttl"):
        # print(file)
        examples.append(os.path.basename(file).split(".")[0])
    return examples


def delet_old_json():
    # files = []
    dirpath = os.getcwd()
    path = os.path.join(dirpath, "src/app/render/static/shapes")
    minutes = 1
    time_in_secs = time.time() - (minutes * 60)
    for file in glob.glob(path + "/*.json"):
        stat = os.stat(file)
        if stat.st_mtime <= time_in_secs:
            # print(f'delete {file}')
            os.remove(file)
