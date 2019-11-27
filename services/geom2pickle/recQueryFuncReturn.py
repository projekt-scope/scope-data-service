# generell imports
import os
import time
import requests
import urllib.request
import json
import string
import random


# pythonOCC imports
import OCC

#FIXME OCC imports are neccessary fix this !

from OCC import VERSION as OCC_VERSION
from OCC.Core.Standard import Standard_Transient, Handle_Standard_Transient
from OCC.Core import gp
from OCC.Core.gp import gp_Vec, gp_Trsf, gp_Dir, gp_Pnt, gp_Ax2
from OCC.Core.Visualization import Tesselator
from OCC.Extend.TopologyUtils import is_edge, is_wire, discretize_edge, discretize_wire
from multiprocessing import Process, Value
from OCC.Core.BRepPrimAPI import (
    BRepPrimAPI_MakeBox,
    BRepPrimAPI_MakeTorus,
    BRepPrimAPI_MakeCylinder,
)
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut


import jsonpickle
# from app import LC_ADDR_fuseki_app


LC_ADDR_fuseki_app = os.environ["LC_ADDR_fuseki_app"]
# LC_ADDR_fuseki_app ="http://localhost:22631"
proxies = {"http": None, "https": None}


def give_me_new_ID():
    return "_%s" % "".join(random.choice(string.ascii_letters) for _ in range(8))


def dict_generator(indict, pre=None):
    pre = pre[:] if pre else []
    if isinstance(indict, dict):
        for key, value in indict.items():
            if isinstance(value, dict):
                for d in dict_generator(value, [key] + pre):
                    yield d
            elif isinstance(value, list) or isinstance(value, tuple):
                for v in value:
                    for d in dict_generator(v, [key] + pre):
                        yield d
            else:
                yield pre + [key, value]
    else:
        yield indict


def sparqlSelect(PrefixList, SelectStr, FindStr):
    s = time.time()
    str1 = ""
    for i1 in PrefixList:
        str1 += "PREFIX " + i1
    qer_string = """ %s """ % str1 + """ SELECT %s WHERE {  GRAPH ?g { %s }} """ % (
        SelectStr,
        FindStr,
    )
    # print(f"qer_string: {qer_string}")
    headers = {"content-type": "application/json", "encoding": "UTF-8"}
    url = LC_ADDR_fuseki_app + "/fuseki/sparql"
    payload = {"SparqlString": qer_string}

    r = requests.post(url, data=json.dumps(payload), headers=headers, proxies=proxies)
    jsonResp = r.json()

    return jsonResp


def geomQuery(position):
    # print(f"position: {position}")
    PrefixList = [
        "omg: <https://w3id.org/omg#> ",
        "rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> ",
    ]
    SelectStr = "?CompGeomDesc ?CompGeomDescType "
    FindStr = (
        """<%s> omg:hasComplexGeometryDescription ?CompGeomDesc . 
                ?CompGeomDesc rdf:type ?CompGeomDescType . """
        % position
    )

    qres = sparqlSelect(PrefixList, SelectStr, FindStr)
    qresResBin = qres["results"]["bindings"]
    if len(qresResBin) != 0:
        # find OCC class and className
        occName = qresResBin[0]["CompGeomDesc"]["value"]
        ResOCC_className = qresResBin[0]["CompGeomDescType"]["value"]
        OCC_classname = ResOCC_className.split("#")[-1]
        OCC_module = OCC_classname.split("_")[0]
        # print(OCC_classname, OCC_module)
        occClass = getattr(getattr(OCC.Core, OCC_module), OCC_classname)
        # print(occClass)
        cparamstrlist = paramQuery(occName)
        # print(cparamstrlist)
        #TODO find better way to convert numbers into floats and keep Classes
        for i in range(len(cparamstrlist)):
            try:
                cparamstrlist[i] = float(cparamstrlist[i])
            except:
                pass

        objres = occClass(*cparamstrlist)

        PrefixList = [
            "oop: <https://projekt-scope.de/ontologies/oop#> ",
            "rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>",
        ]
        SelectStr = "?Method ?oneMethod "
        FindStr = (
            """<%s> oop:hasMethod ?Method . 
                OPTIONAL { ?Method oop:hasListContent ?o .
                ?o rdf:rest*/rdf:first ?oneMethod . }"""
            % occName
        )
        qresResBin3 = []

        qres = sparqlSelect(PrefixList, SelectStr, FindStr)
        qresResBin3 = qres["results"]["bindings"]

        methods = []
        if len(qresResBin3) != 0:
            if len(qresResBin3) > 1:
                for entry in qresResBin3:
                    if entry["oneMethod"]["type"] == "uri":
                        methods.append(entry["oneMethod"]["value"])
                    else:
                        pass
            else:
                methods.append(qresResBin3[0]["Method"]["value"])

            for methodname in methods:

                PrefixList = ["rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>"]
                SelectStr = "?o "
                FindStr = "<%s> rdf:type ?o . " % methodname
                qres = sparqlSelect(PrefixList, SelectStr, FindStr)
                qresResBin4 = qres["results"]["bindings"]

                for row_qMN in qresResBin4:
                    methodtypestr = row_qMN["o"]["value"].split("#")[-1]
                mparams = []
                mparams = paramQuery(methodname)
                if methodtypestr in ["Shape", "Edge", "Curve", "Wire", "Face"]:
                    objres = getattr(objres, methodtypestr)(*mparams)
                else:
                    # print(objres, methodtypestr,*mparams)
                    getattr(objres, methodtypestr)(*mparams)
    return objres


def paramQuery(position):
    # find all parameters (doesn't matter if list or single)

    PrefixList = ["oop: <https://projekt-scope.de/ontologies/oop#> "]
    SelectStr = "?o1 ?o2"
    FindStr = "<%s> oop:hasParameter ?o1 . OPTIONAL { ?o1 a ?o2 }" % position
    qres = sparqlSelect(PrefixList, SelectStr, FindStr)
    qresResBin = qres["results"]["bindings"]

    paramstrlist = []

    if len(qresResBin) != 0:
        for row_qP in qresResBin:

            if row_qP["o1"]["type"] == "uri":
                if "o2" in row_qP and (row_qP["o2"]["value"].split("#")[-1] == "List"):

                    PrefixList = [
                        "oop: <https://projekt-scope.de/ontologies/oop#> ",
                        "rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>",
                    ]
                    SelectStr = "?item ?type "

                    FindStr = (
                        """<%s> oop:hasParameter ?o1 .
                                ?o1 oop:hasListContent ?o2 .
                                ?o2 rdf:rest*/rdf:first ?item .
                                BIND(DATATYPE(?item) AS ?type)"""
                        % position
                    )

                    qres = sparqlSelect(PrefixList, SelectStr, FindStr)
                    qresResBin1 = qres["results"]["bindings"]

                    for k, row_qPL in enumerate(qresResBin1):

                        if row_qPL["item"]["type"] == "uri":
                            paramname = row_qPL["item"]["value"]
                            paramstrlist.append(geomQuery(paramname))
                        else:
                            if (row_qPL["item"]["type"].split("#"))[-1] == "double":
                                paramstrlist.append(float(row_qPL["item"]["value"]))
                            elif (row_qPL["item"]["type"].split("#"))[
                                -1
                            ] == "integer":
                                paramstrlist.append(int(row_qPL["item"]["value"]))
                            else:
                                paramstrlist.append(row_qPL["item"]["value"])
                else:
                    paramname = row_qP["o1"]["value"]
                    paramstrlist.append(geomQuery(paramname))

            elif row_qP["o"]["type"] == "str":
                paramstrlist.append(col_qP)  # FIXME undefinde varibale

            else:
                return ValueError("further coding required for this case")

    return paramstrlist


def sparqlInsertList(insertList):
    headers = {"content-type": "application/json", "encoding": "UTF-8"}
    url = LC_ADDR_fuseki_app + "/fuseki/insert"
    insStr = "INSERT DATA {"
    for i in insertList:
        insStr += (
            "GRAPH <%s> { <%s>   <https://w3id.org/omg#hasOccPickle>  '%s' . } ."
            % (i[0], i[1], i[2])
        )
    insStr += "}"

    payload = {"SparqlString": """%s""" % insStr}
    requests.post(url, data=json.dumps(payload), headers=headers, proxies=proxies)


def sparqlInsert(InsStr):
    headers = {"content-type": "application/json", "encoding": "UTF-8"}
    url = LC_ADDR_fuseki_app + "/fuseki/insert"
    payload = {"SparqlString": """%s""" % InsStr}
    r = requests.post(url, data=json.dumps(payload), headers=headers, proxies=proxies)
    return r


def upload_handler(elem,ur):
    objectOcc = geomQuery(elem)
    res = jsonpickle.encode(objectOcc)
    
    return ur, elem, str(res)


def pool_handler(ResObjList):
    l_insert = []
    ur = "http://" + give_me_new_ID()
    for elem in ResObjList:
        l_insert.append(upload_handler(elem,ur))

    sparqlInsertList(l_insert)

