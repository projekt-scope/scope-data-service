import ast
import numpy as np
import rdflib
from rdflib import Graph, BNode, RDF
import DrawAndExtrude
from scipy import linalg
import json
import requests
import TDB_Helpers
#
proxies = {"http": None, "https": None}

BIM = "https://projekt-scope.de/ontologies/BIM#"
RevitAPI = "https://projekt-scope.de/software/RevitAPI#"
rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
bot = "https://w3id.org/bot#"
oop = "https://projekt-scope.de/ontologies/oop#"
omg = "https://w3id.org/omg#"


class SparqlConn:
    def __init__(self, url, SparqlQueryString):
        self.url = url
        self.SparqlQueryString = SparqlQueryString

    def sendSparqlRequest(self):
        SparqlQueryString = "PREFIX bot: <https://w3id.org/bot#> PREFIX RevitAPI: <https://projekt-scope.de/software/RevitAPI#> PREFIX oop: <https://projekt-scope.de/ontologies/oop#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX BIM: <https://projekt-scope.de/ontologies/BIM#> %s" % self.SparqlQueryString
        dataDict = {"SparqlString": SparqlQueryString}
        json_data = json.dumps(dataDict)
        qUrl = self.url
        r = requests.post(qUrl,
                          data=json_data,
                          headers={'content-type': 'application/json'},
                          proxies=proxies)
        r = r.json()
        return r["results"]["bindings"]


def qryList(url, inst, parDesc):

    SparqlQueryString = ("SELECT ?items WHERE {GRAPH ?g {"
                         "<%s> RevitAPI:hasFurtherGeomParams ?parBN . "
                         "?parBN <%s> ?furPars . "
                         "?furPars oop:hasListContent ?ListItems . "
                         "?ListItems rdf:rest*/rdf:first ?items . } }") % (
                             inst["value"], parDesc)
    qUrl = url + "/fuseki/sparql"
    questObj = SparqlConn(qUrl, SparqlQueryString)
    res = questObj.sendSparqlRequest()

    ItemList = []
    for bind in res:
        items = bind["items"]["value"]
        ItemList.append(str(items).split("#")[-1])
    return ItemList


def qInst(url, inst):
    SparqlQueryString = ("SELECT ?parDesc ?furPars ?isList WHERE {GRAPH ?g {"
                         "<%s> RevitAPI:hasFurtherGeomParams ?parBN . "
                         "?parBN ?parDesc ?furPars . "
                         "OPTIONAL {?furPars a ?isList} . } }") % inst["value"]

    qUrl = url + "/fuseki/sparql"
    questObj = SparqlConn(qUrl, SparqlQueryString)
    res = questObj.sendSparqlRequest()

    paramDict = {}
    for bind in res:
        furPars = bind["furPars"]["value"]
        parDesc = bind["parDesc"]["value"]
        if "isList" in bind:
            params = qryList(url, inst, parDesc)
        else:
            params = str(furPars)
        paramDict[str(parDesc).split("#")[-1]] = params
    return paramDict


def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    return (rho, phi)


def PolyArea(x, y):
    return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def sendSparqlString(SparqlString, url):
    data = {}
    data["SparqlString"] = SparqlString
    json_data = json.dumps(data)
    insUrl = url + "/fuseki/insert"
    r = requests.post(insUrl,
                      data=json_data,
                      headers={'content-type': 'application/json'},
                      proxies=proxies)


def handle_OST_StructuralColumns(url, newquadID, inst, BIM, IDListMain,
                                 ProjectName, i):

    SparqlString = "INSERT DATA { GRAPH <%s> {" % newquadID

    SparqlQueryString_3 = (
        "SELECT ?Curve ?curveType WHERE {GRAPH ?g"
        "{ <%s> RevitAPI:hasFurtherGeomParams ?parBN . "
        "?parBN RevitAPI:hasCurve ?Curve . "
        "?Curve RevitAPI:hasCurveNr '0' . "
        "?Curve RevitAPI:isOfType ?curveType . } }") % inst["value"]
    qUrl = url + "/fuseki/sparql"
    questObj_3 = SparqlConn(qUrl, SparqlQueryString_3)
    res3 = questObj_3.sendSparqlRequest()

    for elem in res3:
        curveType = elem["curveType"]
        Curve = elem["Curve"]

        if curveType["value"] == "Arc":
            SparqlQueryString_4 = ("SELECT ?rad ?leng WHERE  {GRAPH ?g {"
                                   "<%s> RevitAPI:hasRadius ?rad . "
                                   "?inst RevitAPI:hasCurve <%s> . "
                                   "?inst RevitAPI:hasLength ?leng . } }") % (
                                       Curve["value"],
                                       Curve["value"],
            )

            questObj_4 = SparqlConn(qUrl, SparqlQueryString_4)
            res4 = questObj_4.sendSparqlRequest()

            length = res4[0]["leng"]["value"]
            radius = res4[0]["rad"]["value"]

            SparqlQueryString_5 = (
                "SELECT ?items WHERE {GRAPH ?g {"
                "?inst RevitAPI:hasCurve <%s> . "
                "?inst RevitAPI:hasLocation ?loc . "
                "?loc oop:hasListContent ?content . "
                "?content rdf:rest*/rdf:first ?items . } }") % Curve["value"]
            questObj_5 = SparqlConn(qUrl, SparqlQueryString_5)
            res5 = questObj_5.sendSparqlRequest()

            loc = []
            for element in res5:
                loc.append(float(element["items"]["value"]))

            SparqlString = TDB_Helpers.sparqlInsertClass(
                SparqlString,
                BIM,
                BIM + IDListMain[i],
                "BRepPrimAPI_MakeCylinder",
                [
                    radius,
                    length,
                ],
                "Shape",
            )

            P0 = float(loc[0])
            P1 = float(loc[1])
            P2 = float(loc[2])

            movedShape = TDB_Helpers.move_a_Shape(SparqlString, inst, BIM,
                                                  BIM + IDListMain[i], P0, P1, P2)
            SparqlString = movedShape[0]

            SparqlString += "<%s> <%s> '%s' . " % (
                inst["value"], BIM + "isPartOfProject", ProjectName)
            SparqlString += "<%s> <%s> <%s> . " % (
                inst["value"], omg + "hasGeometry", movedShape[1])
        Points = []

        if curveType["value"] == "Line":
            Points = 4
            x2DDrawing = []
            leng = ""

            for i in range(Points):

                SparqlQueryString_6 = (
                    "SELECT ?leng ?Points WHERE {GRAPH ?g {"
                    "?proj RevitAPI:hasCurve <%s> . "
                    "?proj RevitAPI:hasCurve ?curve . "
                    "?proj RevitAPI:hasLength ?leng . "
                    "?curve RevitAPI:hasCurveNr '%s' . "
                    "?curve RevitAPI:hasExactStartLoc ?PointNode . "
                    "?PointNode oop:hasListContent ?Point . "
                    "?Point rdf:rest*/rdf:first ?Points . } }") % (
                        Curve["value"], i)

                questObj_6 = SparqlConn(qUrl, SparqlQueryString_6)
                res6 = questObj_6.sendSparqlRequest()

                PList = []
                for k, element in enumerate(res6):
                    PList.append(float(element["Points"]["value"]))
                    # leng is at every Point, just need it one time. Take it at k = 0 or somewhere else
                    if k == 0:
                        leng = float(element["leng"]["value"])
                x2DDrawing.append(PList)
            extrusion = DrawAndExtrude.x2DDrawAndExtrude(
                SparqlString, BIM, x2DDrawing, leng)
            SparqlString = extrusion[0]

            SparqlQueryString_7 = (
                "SELECT ?LocPoints WHERE {GRAPH ?g {"
                "?proj RevitAPI:hasCurve <%s> . "
                "?proj RevitAPI:hasLocation ?locationNode . "
                "?locationNode oop:hasListContent ?location . "
                "?location rdf:rest*/rdf:first ?LocPoints . } }" %
                Curve["value"])

            questObj_7 = SparqlConn(qUrl, SparqlQueryString_7)
            res7 = questObj_7.sendSparqlRequest()

            LocPoints = []

            for point in res7:
                LocPoints.append(point["LocPoints"]["value"])

            Poi0 = float(LocPoints[0])
            Poi1 = float(LocPoints[1])
            Poi2 = float(LocPoints[2])

            movedShape = TDB_Helpers.move_a_Shape(SparqlString, inst, BIM, extrusion[1],
                                                  Poi0, Poi1, Poi2)
            SparqlString = movedShape[0]
            SparqlString += "<%s> <%s> '%s' . " % (
                inst["value"], BIM + "isPartOfProject", ProjectName)
            SparqlString += "<%s> <%s> <%s> . " % (
                inst["value"], omg + "hasGeometry", movedShape[1])

    SparqlString += "} }"
    sendSparqlString(SparqlString, url)


def handle_OST_Floors_OST_StructuralFoundation(url, newquadID, inst, BIM,
                                               IDListMain, ProjectName, i):
    qUrl = url + "/fuseki/sparql"
    SparqlString = "INSERT DATA { GRAPH <%s> {" % newquadID

    SparqlQueryString_1 = (
        "SELECT ?listArr ?ListList ?oneList WHERE {GRAPH ?g {"
        "<%s> RevitAPI:hasFurtherGeomParams ?parBN . "
        "?parBN RevitAPI:hasPolyline ?Polyline . "
        "?Polyline oop:hasListContent ?list . "
        "?list rdf:rest*/rdf:first ?listArr . "
        "?listArr oop:hasListContent ?anotherList . "
        "?anotherList rdf:rest*/rdf:first ?ListList . "
        "OPTIONAL {"
        "?ListList oop:hasListContent ?lastLevelList . "
        "?lastLevelList rdf:rest*/rdf:first ?oneList . } } }") % inst["value"]

    questObj_1 = SparqlConn(qUrl, SparqlQueryString_1)
    res_1 = questObj_1.sendSparqlRequest()

    firstLevel = []
    secondLevel = []
    thirdLevel = []
    SLI = ""
    getLen = len(res_1)
    #  if oneList is not in response ==> the floor has no cutOuts.
    if len(res_1) != 0:
        if "oneList" not in res_1[0]:
            for k, bind in enumerate(res_1):
                if k == 0:
                    FLI = bind["listArr"]["value"]
                    secondLevel.append(float(bind["ListList"]["value"]))
                else:
                    newFLI = bind["listArr"]["value"]
                    if FLI == newFLI:
                        secondLevel.append(float(bind["ListList"]["value"]))
                        FLI = newFLI
                    else:
                        firstLevel.append(secondLevel)
                        secondLevel = [float(bind["ListList"]["value"])]
                        FLI = newFLI
                    if k == getLen - 1:
                        firstLevel.append(secondLevel)
            # todo: this is very bad written but works as if there is only one list later which is the "create" List.
            # better would be handling instances without cutOuts different.
            firstLevel = [firstLevel]
        # else: the floor has cutOuts and therefore one list more
        else:
            for k, bind in enumerate(res_1):
                if k == 0:
                    FLI = bind["listArr"]["value"]
                    SLI = bind["ListList"]["value"]
                    thirdLevel.append(float(bind["oneList"]["value"]))
                else:
                    newFLI = bind["listArr"]["value"]
                    newSLI = bind["ListList"]["value"]
                    if SLI == newSLI:
                        thirdLevel.append(float(bind["oneList"]["value"]))
                        SLI = newSLI
                    else:
                        secondLevel.append(thirdLevel)
                        thirdLevel = []
                        thirdLevel.append(float(bind["oneList"]["value"]))
                        SLI = newSLI

                    if FLI != newFLI:
                        firstLevel.append(secondLevel)
                        secondLevel = []
                        FLI = newFLI

                    if k == getLen - 1:
                        secondLevel.append(thirdLevel)
                        firstLevel.append(secondLevel)

        SparqlQueryString_2 = ("SELECT ?Name ?Value WHERE {GRAPH ?g {"
                               "<%s> a bot:Element . "
                               "<%s> RevitAPI:hasRevitType ?type . "
                               "?type RevitAPI:hasParameter ?paraBN . "
                               "?paraBN RevitAPI:hasName ?Name . "
                               "?paraBN RevitAPI:hasValue ?Value . "
                               "FILTER(?Name = 'Standarddicke') . } }") % (
                                   inst["value"], inst["value"])

        questObj_2 = SparqlConn(qUrl, SparqlQueryString_2)
        res_2 = questObj_2.sendSparqlRequest()

        if len(res_2) != 0:
            hight = res_2[0]["Value"]["value"]
            if len(firstLevel) != 0:
                # it is not clear which array is the utter boundary of a floor and which one is the one which has to be cut out
                # because of that i'm going to get the array with the biggest area and cut all the others out
                AreaCompare = []
                for el in firstLevel:
                    elemX = []
                    elemY = []
                    for tmp in el:
                        elemX.append(tmp[0])
                        elemY.append(tmp[1])
                    x = np.array(elemX)
                    y = np.array(elemY)
                    AreaCompare.append(PolyArea(x, y))
                utterBound = np.argmax(AreaCompare)
                # extrude the utter Bound of the floor

                extrusion = DrawAndExtrude.x2DDrawAndExtrude(SparqlString, BIM,
                                                             firstLevel[utterBound], hight)
                SparqlString = extrusion[0]

                del firstLevel[utterBound]

                for elem in firstLevel:
                    subBody = DrawAndExtrude.x2DDrawAndExtrude(SparqlString, BIM, elem,
                                                               float(hight) + 0.001)
                    SparqlString = subBody[0]
                    extrusion = TDB_Helpers.cutA_fromB(SparqlString, BIM, extrusion[1],
                                                       subBody[1])
                    SparqlString = extrusion[0]

        SparqlString += "<%s> <%s> '%s' . " % (inst["value"], BIM +
                                               "isPartOfProject", ProjectName)
        SparqlString += "<%s> <%s> <%s> . " % (inst["value"], omg +
                                               "hasGeometry", extrusion[1])
    SparqlString += "} }"
    sendSparqlString(SparqlString, url)


def handle_OST_Walls(url, newquadID, inst, BIM, IDListMain, ProjectName,
                     i):
    qUrl = url + "/fuseki/sparql"
    SparqlString = "INSERT DATA { GRAPH <%s> {" % newquadID

    allParams = qInst(url, inst)
    if allParams["isBasedOn"] == "Line":
        hoehe = float
        length = float
        breite = float

        SparqlQueryString_1 = (
            "SELECT ?Name ?Value WHERE {GRAPH ?g {"
            "<%s> a bot:Element .  "
            "<%s> RevitAPI:hasParameter ?paraBN . "
            "?paraBN RevitAPI:hasName ?Name . "
            "?paraBN RevitAPI:hasValue ?Value . "
            "FILTER(?Name = 'Nicht verknuepfte Hoehe') . } }") % (
                inst["value"], inst["value"])

        questObj_1 = SparqlConn(qUrl, SparqlQueryString_1)
        res_1 = questObj_1.sendSparqlRequest()

        for paramElem in res_1:
            hoehe = paramElem["Value"]["value"]

        SparqlQueryString_2 = ("SELECT ?Name ?Value WHERE {GRAPH ?g {"
                               "<%s> a bot:Element .  "
                               "<%s> RevitAPI:hasRevitType ?type . "
                               "?type RevitAPI:hasParameter ?paraBN . "
                               "?paraBN RevitAPI:hasName ?Name . "
                               "?paraBN RevitAPI:hasValue ?Value . "
                               "FILTER(?Name = 'Breite') . } }") % (
                                   inst["value"], inst["value"])

        questObj_2 = SparqlConn(qUrl, SparqlQueryString_2)
        res_2 = questObj_2.sendSparqlRequest()

        for paramElem in res_2:
            breite = float(paramElem["Value"]["value"])

        P0x = float(allParams["hasExactStartLoc"][0])
        P0y = float(allParams["hasExactStartLoc"][1])
        P0z = float(allParams["hasExactStartLoc"][2])

        P1x = float(allParams["hasExactEndLoc"][0])
        P1y = float(allParams["hasExactEndLoc"][1])
        P1z = float(allParams["hasExactEndLoc"][2])

        KernA0Vec = np.array([P0x, P0y, P0z])
        KernA1Vec = np.array([P1x, P1y, P1z])
        Vec01 = KernA1Vec - KernA0Vec
        Vec10 = KernA0Vec - KernA1Vec
        c = np.array([0.0, 0.0, 1.0])

        P0Vec = KernA0Vec + (((np.cross(Vec10, c)) /
                              (linalg.norm(np.cross(Vec10, c)))) *
                             (breite / 2))
        P1Vec = KernA1Vec + (((np.cross(Vec01, c)) /
                              (linalg.norm(np.cross(Vec01, c)))) *
                             (-breite / 2))

        P2Vec = KernA1Vec + (((np.cross(Vec01, c)) /
                              (linalg.norm(np.cross(Vec01, c)))) *
                             (breite / 2))
        P3Vec = KernA0Vec + (((np.cross(Vec10, c)) /
                              (linalg.norm(np.cross(Vec10, c)))) *
                             (-breite / 2))
        PointArr = [P0Vec, P1Vec, P2Vec, P3Vec]

        extrusion = DrawAndExtrude.x2DDrawAndExtrude(
            SparqlString, BIM, PointArr, hoehe)
        SparqlString = extrusion[0]

        # get exactLoc Cutout _____________________________________________________________________________________________________

        SparqlQueryString_3 = (
            "SELECT ?cutOut ?cutOutLoc WHERE { GRAPH ?g {"
            "<%s> a bot:Element .  "
            "<%s> RevitAPI:hasFurtherGeomParams ?pars . "
            "?pars RevitAPI:hasCutOuts ?cutOut . "
            "?cutOut BIM:isFamInst ?CutInst . "
            "?cutOut RevitAPI:hasExactLoc ?loc . "
            "?loc oop:hasListContent ?cutOutNode . "
            "?cutOutNode rdf:rest*/rdf:first ?cutOutLoc . } }") % (
                inst["value"], inst["value"])

        questObj_3 = SparqlConn(qUrl, SparqlQueryString_3)
        res_3 = questObj_3.sendSparqlRequest()

        allCutLocs = {}
        CutLoc = []
        testStr = ""

        for CutOut in res_3:
            newStr = CutOut["cutOut"]["value"]
            if newStr == testStr or testStr == "":
                CutLoc.append(float(CutOut["cutOutLoc"]["value"]))
                testStr = CutOut["cutOut"]["value"]
            else:
                allCutLocs[str(testStr)] = CutLoc
                testStr = CutOut["cutOut"]["value"]
                CutLoc = [float(CutOut["cutOutLoc"]["value"])]
            if CutOut == res_3[-1]:
                allCutLocs[str(testStr)] = CutLoc

        # get Cutout Family _____________________________________________________________________________________________________
        if res_3:

            SparqlQueryString_4 = (
                "SELECT ?cutOut ?CutInst ?builtInCat WHERE { GRAPH ?g {"
                "<%s> a bot:Element . "
                "<%s> RevitAPI:hasFurtherGeomParams ?pars . "
                "?pars RevitAPI:hasCutOuts ?cutOut . "
                "?cutOut BIM:isFamInst ?CutInst . "
                "?CutInst RevitAPI:fromBuiltInCategory ?builtInCat . } }") % (
                    inst["value"], inst["value"])

            questObj_4 = SparqlConn(qUrl, SparqlQueryString_4)
            res_4 = questObj_4.sendSparqlRequest()

            builtInCatCutOutFam = ""
            cutOutInstance = {}
            for element in res_4:
                builtInCatCutOutFam = element["builtInCat"]["value"]

                cutOutInstance[str(
                    element["cutOut"]["value"])] = builtInCatCutOutFam

            for key, value in allCutLocs.items():
                getFam = str(cutOutInstance.get(key))
                if getFam == "OST_Windows":
                    PointArray = []

                    SparqlQueryString_5 = (
                        "SELECT ?Name ?Value WHERE { GRAPH ?g {"
                        "<%s> RevitAPI:hasRevitType ?type . "
                        "?type RevitAPI:hasParameter ?paraBN . "
                        "?paraBN RevitAPI:hasName ?Name . "
                        "?paraBN RevitAPI:hasValue ?Value . "
                        "FILTER(?Name = 'Rohbauhoehe' || ?Name = 'Rohbaubreite') . } }"
                    ) % key

                    questObj_5 = SparqlConn(qUrl, SparqlQueryString_5)
                    res_5 = questObj_5.sendSparqlRequest()

                    for CutPar in res_5:
                        if CutPar["Name"]["value"] == "Rohbauhoehe":
                            Rohbauhoehe = float(CutPar["Value"]["value"])
                        elif CutPar["Name"]["value"] == "Rohbaubreite":
                            Rohbaubreite = float(CutPar["Value"]["value"])
                        else:
                            pass

                    aVec = (P1Vec - P0Vec) / linalg.norm(P1Vec - P0Vec)
                    bVec = (P2Vec - P1Vec) / linalg.norm(P2Vec - P1Vec)

                    x = np.array(value)
                    # "breite" here i took the "breite" (depth) of the wall.

                    P0SnVec = (x + aVec * (Rohbaubreite / 2) + bVec *
                               ((breite + 0.001) / 2))
                    P1SnVec = (x - aVec * (Rohbaubreite / 2) + bVec *
                               ((breite + 0.001) / 2))
                    P2SnVec = (x - aVec * (Rohbaubreite / 2) - bVec *
                               ((breite + 0.001) / 2))
                    P3SnVec = (x + aVec * (Rohbaubreite / 2) - bVec *
                               ((breite + 0.001) / 2))

                    PointArray = [P0SnVec, P1SnVec, P2SnVec, P3SnVec]

                    subBody = DrawAndExtrude.x2DDrawAndExtrude(SparqlString, BIM, PointArray,
                                                               Rohbauhoehe + 0.001)

                    SparqlString = subBody[0]

                    extrusion = TDB_Helpers.cutA_fromB(SparqlString, BIM, extrusion[1],
                                                       subBody[1])
                    SparqlString = extrusion[0]

                if getFam == "OST_Doors":
                    PointArray = []

                    SparqlQueryString_6 = (
                        "SELECT ?Name ?Value WHERE { GRAPH ?g {"
                        "<%s> RevitAPI:hasRevitType ?type . "
                        "?type RevitAPI:hasParameter ?paraBN . "
                        "?paraBN RevitAPI:hasName ?Name . "
                        "?paraBN RevitAPI:hasValue ?Value . "
                        "FILTER(?Name = 'Rohbauhoehe' || ?Name = 'Rohbaubreite') . } }"
                    ) % key

                    questObj_6 = SparqlConn(qUrl, SparqlQueryString_6)
                    res_6 = questObj_6.sendSparqlRequest()

                    for CutPar in res_6:
                        if CutPar["Name"]["value"] == "Rohbauhoehe":
                            Rohbauhoehe = float(CutPar["Value"]["value"])
                        elif CutPar["Name"]["value"] == "Rohbaubreite":
                            Rohbaubreite = float(CutPar["Value"]["value"])
                        else:
                            pass

                    SparqlQueryString_7 = (
                        "SELECT ?CutInst ?FacingDir { GRAPH ?g {"
                        "<%s> BIM:isFamInst ?CutInst . "
                        "<%s> RevitAPI:hasFacingOr ?FacingOr . "
                        "?FacingOr oop:hasListContent ?FacingOrList . "
                        "?FacingOrList rdf:rest*/rdf:first ?FacingDir . } }"
                    ) % (key, key)

                    questObj_7 = SparqlConn(qUrl, SparqlQueryString_7)
                    res_7 = questObj_7.sendSparqlRequest()

                    allCutLocsFacing = {}
                    CutLoc = []
                    testStr = ""
                    for CutOut in res_7:
                        newStr = CutOut["CutInst"]["value"]
                        if newStr == testStr or testStr == "":
                            CutLoc.append(float(CutOut["FacingDir"]["value"]))
                            testStr = CutOut["CutInst"]["value"]
                        else:
                            allCutLocsFacing[str(testStr)] = CutLoc
                            testStr = CutOut["CutInst"]["value"]
                            CutLoc = [float(CutOut["FacingDir"]["value"])]
                        if CutOut == res_7[-1]:
                            allCutLocsFacing[str(testStr)] = CutLoc
                    instanceString = testStr

                    SparqlQueryString_8 = (
                        "SELECT ?CutInst ?HandDir { GRAPH ?g {"
                        "<%s> BIM:isFamInst ?CutInst . "
                        "<%s> RevitAPI:hasHandOr ?HandOr . "
                        "?HandOr oop:hasListContent ?HandOrList . "
                        "?HandOrList rdf:rest*/rdf:first ?HandDir . } }") % (
                            key, key)

                    questObj_8 = SparqlConn(qUrl, SparqlQueryString_8)
                    res_8 = questObj_8.sendSparqlRequest()

                    allCutLocsqDoorsHandOr = {}
                    CutLoc = []
                    testStr = ""

                    for CutOut in res_8:
                        newStr = CutOut["CutInst"]["value"]
                        if newStr == testStr or testStr == "":
                            CutLoc.append(float(CutOut["HandDir"]["value"]))
                            testStr = CutOut["CutInst"]["value"]
                        else:
                            allCutLocsqDoorsHandOr[str(testStr)] = CutLoc
                            testStr = CutOut["CutInst"]["value"]
                            CutLoc = [float(CutOut["HandDir"]["value"])]
                        if CutOut == res_8[-1]:
                            allCutLocsqDoorsHandOr[str(testStr)] = CutLoc

                    CutInstString = testStr

                    handOr = allCutLocsqDoorsHandOr.get(str(CutInstString))
                    handOr = np.array(handOr)

                    facingOr = allCutLocsFacing.get(str(instanceString))
                    facingOr = np.array(facingOr)

                    x = np.array(value)

                    P0SnVec = x + facingOr * ((breite + 0.001) / 2)
                    P1SnVec = (x - handOr * (Rohbaubreite) + facingOr *
                               ((breite + 0.001) / 2))
                    P2SnVec = (x - handOr * (Rohbaubreite) - facingOr *
                               ((breite + 0.001) / 2))
                    P3SnVec = x - facingOr * ((breite + 0.001) / 2)

                    PointArray = [P0SnVec, P1SnVec, P2SnVec, P3SnVec]

                    subBody = DrawAndExtrude.x2DDrawAndExtrude(SparqlString, BIM, PointArray,
                                                               Rohbauhoehe + 0.001)

                    SparqlString = subBody[0]

                    extrusion = TDB_Helpers.cutA_fromB(SparqlString, BIM, extrusion[1],
                                                       subBody[1])
                    SparqlString = extrusion[0]

        SparqlString += "<%s> <%s> '%s' . " % (inst["value"], BIM +
                                               "isPartOfProject", ProjectName)
        SparqlString += "<%s> <%s> <%s> . " % (inst["value"], omg +
                                               "hasGeometry", extrusion[1])
    SparqlString += "} }"
    sendSparqlString(SparqlString, url)


def revit2occ(selectedGraphID, url):

    newquadID = "http://%s" % TDB_Helpers.give_me_new_IDs(1)[0]

    SparqlQueryString_1 = (
        "SELECT ?inst ?BuiltInCategory WHERE {GRAPH <%s>"
        "{ ?inst a bot:Element . "
        "?inst RevitAPI:hasRevitType ?type . "
        "?type RevitAPI:fromBuiltInCategory ?BuiltInCategory . } }" % selectedGraphID)
    qUrl = url + "/fuseki/sparql"
    questObj_1 = SparqlConn(qUrl, SparqlQueryString_1)
    res1 = questObj_1.sendSparqlRequest()

    IDListMain = TDB_Helpers.give_me_new_IDs(len(res1))
    for i, bind in enumerate(res1):
        inst = bind["inst"]
        builtInCat = bind["BuiltInCategory"]

        SparqlQueryString_2 = (
            "SELECT ?projName WHERE {GRAPH ?g"
            "{ ?proj bot:hasElement <%s> . "
            "?proj RevitAPI:hasName ?projName . } }") % inst["value"]

        questObj_2 = SparqlConn(qUrl, SparqlQueryString_2)
        res2 = questObj_2.sendSparqlRequest()

        ProjectName = res2[0]["projName"]["value"]

        ##############################################

        if str(builtInCat["value"]) == "OST_StructuralColumns":
            handle_OST_StructuralColumns(url, newquadID, inst, BIM,
                                         IDListMain, ProjectName, i)

        if str(builtInCat["value"]) == "OST_Walls":
            handle_OST_Walls(url, newquadID, inst, BIM, IDListMain,
                             ProjectName, i)

        if str(builtInCat["value"]) == "OST_Floors" or str(
                builtInCat["value"]) == "OST_StructuralFoundation":
            handle_OST_Floors_OST_StructuralFoundation(url, newquadID,
                                                       inst, BIM, IDListMain,
                                                       ProjectName, i)

    return newquadID
