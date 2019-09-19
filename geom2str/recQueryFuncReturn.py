import requests
import json
import sys
import multiprocessing as mp
import random
import os
import datetime

LC_ADDR_fuseki_app = os.environ["LC_ADDR_fuseki_app"]

proxies = {"http": None, "https": None}

myCharset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def give_me_new_IDs(RangeIDs):
    IDList = []
    for IDs in range(RangeIDs):
        IDList.append('_%s' % ''.join(random.choice(myCharset)
                                      for _ in range(8)))
    return IDList


def sparqlSelect(PrefixList, SelectStr, FindStr):

    str1 = ""
    for i1 in PrefixList:
        str1 += "PREFIX " + i1

    headers = {"content-type": "application/json", "encoding": "UTF-8"}
    url = LC_ADDR_fuseki_app + "/fuseki/sparql"
    # url = "http://localhost:22631/fuseki/sparql"

    payload = {
        "SparqlString": "%s SELECT ?g %s WHERE { GRAPH ?g { %s } }"
        % (str1, SelectStr, FindStr)
    }
    print("T 2  _", datetime.datetime.now())
    testdata = json.dumps(payload)
    print("T 8  _", datetime.datetime.now())

    r = requests.post(url, data=testdata, headers=headers, proxies=proxies)
    print("T 3  _", datetime.datetime.now())

    jsonResp = r.json()

    return jsonResp


def sparqlInsert(InsStr):
    headers = {"content-type": "application/json", "encoding": "UTF-8"}
    url = LC_ADDR_fuseki_app + "/fuseki/insert"
    payload = {
        "SparqlString": """%s""" % InsStr
    }
    r = requests.post(url, data=json.dumps(payload),
                      headers=headers, proxies=proxies)
    return r


def findObjects():
    PrefixList = ["omg: <https://w3id.org/omg#>"]
    SelectStr = "?GeomEnt"
    FindStr = "?x omg:hasGeometry ?GeomEnt . "
    qresStart = sparqlSelect(PrefixList, SelectStr, FindStr)
    return [i1["GeomEnt"]["value"] for i1 in qresStart["results"]["bindings"]]


def extendStr(res, paramstrlist):
    for k, paramstr in enumerate(paramstrlist):
        if " = " in paramstr:
            res = paramstr + res
            tmp = paramstr.split("\\n")[-2]
            id1 = tmp.replace(".", " = ").split(" = ")[0]
            res += "%s" % (id1)
            if k != len(paramstrlist) - 1:
                res += ", "
        else:
            res += "%s" % (paramstr)
            if k != len(paramstrlist) - 1:
                res += ", "
    # res += ")\n"
    return res + ")\\n"


def geomQuery(position):
    print("T 1  _", datetime.datetime.now())

    retString = ""
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
    print(position)
    print("4", datetime.datetime.now())

    if len(qresResBin) != 0:
        # find OCC class and className
        occName = qresResBin[0]["CompGeomDesc"]["value"]
        ResOCC_className = qresResBin[0]["CompGeomDescType"]["value"]
        OCC_classname = ResOCC_className.split("#")[-1]
        OCC_module = OCC_classname.split("_")[0]
        objID = occName.split("#")[-1]
        retString += "%s = OCC.Core.%s.%s(" % (objID,
                                               OCC_module, OCC_classname)

        cparamstrlist = paramQuery(occName)
        retString = extendStr(retString, cparamstrlist)

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
                mString = ""
                PrefixList = [
                    "rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>"]
                SelectStr = "?o "
                FindStr = "<%s> rdf:type ?o . " % methodname
                qres = sparqlSelect(PrefixList, SelectStr, FindStr)
                qresResBin4 = qres["results"]["bindings"]

                for row_qMN in qresResBin4:
                    methodtypestr = row_qMN["o"]["value"].split("#")[-1]

                    if methodtypestr in ["Shape", "Edge", "Curve", "Wire", "Face"]:
                        mString += "%s = %s.%s(" % (objID,
                                                    objID, str(methodtypestr))

                    else:
                        mString += "%s.%s(" % (objID, str(methodtypestr))

                mparamstrlist = paramQuery(methodname)
                mString = extendStr(mString, mparamstrlist)
                retString += mString

    return retString


def paramQuery(position):
    # find all parameters (doesn't matter if list or single)

    PrefixList = ["oop: <https://projekt-scope.de/ontologies/oop#> "]
    SelectStr = "?o1 ?o2"
    FindStr = "<%s> oop:hasParameter ?o1 . OPTIONAL { ?o1 a ?o2 }" % position
    qres = sparqlSelect(PrefixList, SelectStr, FindStr)
    qresResBin = qres["results"]["bindings"]

    paramstr = ""
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
                            paramstrlist.append(str(row_qPL["item"]["value"]))
                else:
                    paramname = row_qP["o1"]["value"]
                    paramstrlist.append(geomQuery(paramname))

            elif row_qP["o"]["type"] == "str":
                paramstrlist.append(col_qP)

            else:
                return ValueError("further coding required for this case")

    return paramstrlist


def upload_handler(oneObjInObjList, graphID):
    res = geomQuery(oneObjInObjList)

    insStr = "PREFIX omg: <https://w3id.org/omg#> INSERT DATA { GRAPH <http://%s> { <%s> omg:hasOccString '%s' . } }" % (
        graphID, oneObjInObjList, res)
    # print(insStr, file=sys.stderr)
    sparqlInsert(insStr)


def pool_handler(ResObjList):

    graphID = give_me_new_IDs(1)[0]
    for elem in ResObjList:
        upload_handler(elem, graphID)

###################

    # if len(ResObjList) == 0:
    #     return ValueError("Number of processes must be at least 1")
    # elif len(ResObjList) < 31:
    #     pool = mp.Pool(processes=len(ResObjList))
    # else:
    #     pool = mp.Pool(processes=30)

    # res = [pool.apply_async(upload_handler, args=(x,)) for x in ResObjList]

#################

    # res = [p.get() for p in results]

    # return(res)

    # if len(ResObjList) < 8:
    #     p = Pool(processes=len(ResObjList))
    # if len(ResObjList) >= 8:
    #     p = Pool(processes=8)

    # res = p.map(geomQuery, ResObjList)

################


if __name__ == "__main__":
    objres = findObjects()
    res = pool_handler(objres)
