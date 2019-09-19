
import ast
import numpy as np
import os.path
import rdflib
from rdflib import Graph, BNode, RDF
from ttl_helpers_copy import *
from DrawAndExtrude import *
from scipy import linalg


from argparse import ArgumentParser


def qryList(g, inst, parDesc):
    qInstList = """
        SELECT ?items WHERE
        {
        <%s> RevitAPI:hasFurtherGeomParams ?parBN . 
        ?parBN <%s> ?furPars . 
        ?furPars oop:hasListContent ?ListItems . 
        ?ListItems rdf:rest*/rdf:first ?items . 
        }
        """ % (
        inst,
        parDesc,
    )
    qInstL = g.query(qInstList)
    ItemList = []
    for i, bind in enumerate(qInstL.bindings):
        items = bind._d[rdflib.term.Variable("items")]
        ItemList.append(str(items).split("#")[-1])
    return ItemList


def qInst(g, inst):
    qString = (
        """
        SELECT ?parDesc ?furPars ?isList WHERE
        {
        <%s> RevitAPI:hasFurtherGeomParams ?parBN . 
        ?parBN ?parDesc ?furPars . 
        OPTIONAL {?furPars a ?isList}
        }
        """
        % inst
    )
    qryInst = g.query(qString)

    paramDict = {}

    inDi = {}
    for bind in qryInst.bindings:
        furPars = bind._d[rdflib.term.Variable("furPars")]
        parDesc = bind._d[rdflib.term.Variable("parDesc")]
        if rdflib.term.Variable("isList") in bind._d:
            params = qryList(g, inst, parDesc)
        else:
            params = str(furPars)
        paramDict[str(parDesc).split("#")[-1]] = params
    return paramDict


def cart2pol(x, y):
    rho = np.sqrt(x ** 2 + y ** 2)
    phi = np.arctan2(y, x)
    return (rho, phi)

def PolyArea(x,y):
    return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))

def instBelongsToProject(g, inst):
    qry = """
    SELECT ?projName WHERE
    {
        ?proj bot:hasElement <%s> . 
        ?proj RevitAPI:hasName ?projName .
    }
    """% inst

    qryProjName = g.query(qry)
    for element in qryProjName.bindings:
        ProjectName = element._d[rdflib.term.Variable("projName")]
    return ProjectName


def importGeomData(g):
    newGraph = Graph()

    BIM = Namespace("https://projekt-scope.de/ontologies/BIM#")
    bot = Namespace("https://w3id.org/bot#")

    qSt = """
        SELECT ?inst ?BuiltInCategory WHERE
        {
            ?inst a bot:Element . 
            ?inst RevitAPI:hasRevitType ?type . 
            ?type RevitAPI:fromBuiltInCategory ?BuiltInCategory .
        }
        """

    qry = g.query(qSt)

    IDListMain = give_me_new_IDs(len(qry.bindings))

    for i, bind in enumerate(qry.bindings):
        inst = bind._d[rdflib.term.Variable("inst")]
        builtInCat = bind._d[rdflib.term.Variable("BuiltInCategory")]
        bStr = str(builtInCat).split("#")[-1]
        ProjectName = instBelongsToProject(g, inst)
        if bStr == "OST_StructuralColumns":
            qS = (
                """
                SELECT ?Curve ?curveType WHERE
                {
                <%s> RevitAPI:hasFurtherGeomParams ?parBN . 
                ?parBN RevitAPI:hasCurve ?Curve . 
                ?Curve BIM:hasCurveNr "0" .
                ?Curve RevitAPI:isOfType ?curveType .
                }
                """
                % inst
            )
            qInst1 = g.query(qS)
            print(inst)

            for bind in qInst1.bindings:
                curveType = bind._d[rdflib.term.Variable("curveType")]
                Curve = bind._d[rdflib.term.Variable("Curve")]

                if curveType == rdflib.term.Literal("Arc"):
                    qS2 = """
                        SELECT ?rad ?leng WHERE
                        {
                        <%s> RevitAPI:hasRadius ?rad .
                        ?inst RevitAPI:hasCurve <%s> .
                        ?inst RevitAPI:hasLocation ?loc .
                        ?inst RevitAPI:hasLength ?leng . 
                        }
                        """ % (
                        Curve,
                        Curve,
                    )
                    qInst2 = g.query(qS2)
                    length = ""
                    radius = ""
                    for newbind in qInst2.bindings:
                        length = newbind._d[rdflib.term.Variable("leng")]
                        radius = newbind._d[rdflib.term.Variable("rad")]

                    qS3 = (
                        """
                        SELECT ?items WHERE
                        {
                        ?inst RevitAPI:hasCurve <%s> .
                        ?inst RevitAPI:hasLocation ?loc . 
                        ?loc oop:hasListContent ?content . 
                        ?content rdf:rest*/rdf:first ?items . 
                        }
                        """
                        % Curve
                    )
                    qInst3 = g.query(qS3)
                    loc = []
                    for newbind3 in qInst3.bindings:
                        loc.append(float(newbind3._d[rdflib.term.Variable("items")]))

                    createTTLofClass(
                        newGraph,
                        BIM,
                        BIM[IDListMain[i]],
                        "BRepPrimAPI_MakeCylinder",
                        [
                            Literal(radius, datatype=XSD.double),
                            Literal(length, datatype=XSD.double),
                        ],
                        "Shape",
                    )
                    P0 = float(loc[0])
                    P1 = float(loc[1])
                    P2 = float(loc[2])

                    movedShape = move_a_Shape(
                        newGraph, BIM, BIM[IDListMain[i]], P0, P1, P2
                    )

                    newGraph.add(
                        (inst, omg.hasGeometry, movedShape)
                    )
                    newGraph.add(
                        (inst, BIM.isPartOfProject, ProjectName)
                    )
                Points = []

                if curveType == rdflib.term.Literal("Line"):
                    Points = 4
                    x2DDrawing = []
                    leng = ""

                    for i in range(Points):
                        qS = """
                            SELECT ?leng ?Points WHERE
                            {
                            ?proj RevitAPI:hasCurve <%s> .
                            ?proj RevitAPI:hasCurve ?curve .
                            ?proj RevitAPI:hasLength ?leng .
                            ?curve BIM:hasCurveNr %s . 
                            ?curve RevitAPI:hasExactStartLoc ?PointNode .
                            ?PointNode oop:hasListContent ?Point .
                            ?Point rdf:rest*/rdf:first ?Points .
                            }
                            """ % (
                            Curve,
                            i,
                        )
                        qIn = g.query(qS)
                        PList = []
                        for k, bind4 in enumerate(qIn.bindings):
                            PList.append(float(bind4._d[rdflib.term.Variable("Points")]))
                            # leng is at every Point, just need it one time. Take it at k = 0 or somewhere else
                            if k == 0:
                                leng = float(bind4._d[rdflib.term.Variable("leng")])
                        x2DDrawing.append(PList)

                    extrusion = x2DDrawAndExtrude(newGraph, BIM, x2DDrawing, leng)

                    qS2 = (
                        """
                        SELECT ?LocPoints WHERE
                        {
                        ?proj RevitAPI:hasCurve <%s> .
                        ?proj RevitAPI:hasLocation ?locationNode . 
                        ?locationNode oop:hasListContent ?location . 
                        ?location rdf:rest*/rdf:first ?LocPoints .
                        }
                        """
                        % Curve
                    )
                    q2 = g.query(qS2)

                    LocPoints = []
                    for bind5 in q2.bindings:
                        LocPoints.append(
                            float(bind5._d[rdflib.term.Variable("LocPoints")])
                        )

                    Poi0 = float(LocPoints[0])
                    Poi1 = float(LocPoints[1])
                    Poi2 = float(LocPoints[2])

                    movedShape = move_a_Shape(
                        newGraph, BIM, extrusion[1], Poi0, Poi1, Poi2
                    )

                    newGraph.add(
                        (inst, omg.hasGeometry, movedShape)
                    )
                    newGraph.add(
                        (inst, BIM.isPartOfProject, ProjectName)
                    )
        # ##############################################
        if bStr == "OST_Walls":
            allParams = qInst(g, inst)
            if allParams["isBasedOn"] == "Line":
                hoehe = float
                length = float
                breite = float

                qStHoehe = """
                SELECT ?Name ?Value WHERE
                {
                    <%s> a bot:Element . 
                    <%s> RevitAPI:hasParameter ?paraBN . 
                    ?paraBN RevitAPI:hasName ?Name . 
                    ?paraBN RevitAPI:hasValue ?Value .
                    FILTER(?Name = 'Nicht verknuepfte Hoehe') .
                }
                """ % (
                    inst,
                    inst,
                )

                qryPara = g.query(qStHoehe)

                for praramElem in qryPara.bindings:
                    hoehe = praramElem._d[rdflib.term.Variable("Value")]

                qStBreite = """
                SELECT ?Name ?Value WHERE
                {
                    <%s> a bot:Element . 
                    <%s> RevitAPI:hasRevitType ?type . 
                    ?type RevitAPI:hasParameter ?paraBN .
                    ?paraBN RevitAPI:hasName ?Name . 
                    ?paraBN RevitAPI:hasValue ?Value .
                    FILTER(?Name = 'Breite') . 
                }
                """ % (
                    inst,
                    inst,
                )

                qryBreite = g.query(qStBreite)

                for praramElem in qryBreite.bindings:
                    breite = float(praramElem._d[rdflib.term.Variable("Value")])

                ### test ###
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

                P0Vec = KernA0Vec + (
                    ((np.cross(Vec10, c)) / (linalg.norm(np.cross(Vec10, c))))
                    * (breite / 2)
                )
                P1Vec = KernA1Vec + (
                    ((np.cross(Vec01, c)) / (linalg.norm(np.cross(Vec01, c))))
                    * (-breite / 2)
                )

                P2Vec = KernA1Vec + (
                    ((np.cross(Vec01, c)) / (linalg.norm(np.cross(Vec01, c))))
                    * (breite / 2)
                )
                P3Vec = KernA0Vec + (
                    ((np.cross(Vec10, c)) / (linalg.norm(np.cross(Vec10, c))))
                    * (-breite / 2)
                )
                PointArr = [P0Vec, P1Vec, P2Vec, P3Vec]
                extrus = x2DDrawAndExtrude(newGraph, BIM, PointArr, hoehe)
                extr = extrus[1]


                # get exactLoc Cutout _____________________________________________________________________________________________________
                qStCutOut = """
                SELECT ?CutInst ?cutOutLoc WHERE
                {
                    <%s> a bot:Element . 
                    <%s> RevitAPI:hasFurtherGeomParams ?pars . 
                    ?pars RevitAPI:hasCutOuts ?cutOut .
                    ?cutOut BIM:isFamInst ?CutInst .
                    ?cutOut RevitAPI:hasExactLoc ?loc . 
                    ?loc oop:hasListContent ?cutOutNode .
                    ?cutOutNode rdf:rest*/rdf:first ?cutOutLoc .
                }
                """ % (
                    inst,
                    inst,
                )

                qryCutOut = g.query(qStCutOut)
                allCutLocs = {}
                CutLoc = []
                testStr = ""

                for CutOut in qryCutOut.bindings:
                    newStr = CutOut._d[rdflib.term.Variable("CutInst")]
                    if newStr == testStr or testStr == "":
                        CutLoc.append(float(CutOut._d[rdflib.term.Variable("cutOutLoc")]))
                        testStr = CutOut._d[rdflib.term.Variable("CutInst")]
                    else:
                        allCutLocs[str(testStr)] = CutLoc
                        testStr = CutOut._d[rdflib.term.Variable("CutInst")]
                        CutLoc = [float(CutOut._d[rdflib.term.Variable("cutOutLoc")])]
                    if CutOut == qryCutOut.bindings[-1]:
                        allCutLocs[str(testStr)] = CutLoc
                # get Cutout Family _____________________________________________________________________________________________________
                qStCutOutFamily = """
                    SELECT ?CutInst ?builtInCat WHERE
                    {
                        <%s> a bot:Element . 
                        <%s> RevitAPI:hasFurtherGeomParams ?pars . 
                        ?pars RevitAPI:hasCutOuts ?cutOut .
                        ?cutOut BIM:isFamInst ?CutInst .
                        ?CutInst RevitAPI:hasRevitType ?type . 
                        ?type RevitAPI:fromBuiltInCategory ?builtInCat .
                    }
                    """ % (
                    inst,
                    inst,
                )

                qryCutOutFam = g.query(qStCutOutFamily)

                builtInCatCutOutFam = ""
                cutOutInstance= {}
                for element in qryCutOutFam.bindings:
                    builtInCatCutOutFam = element._d[
                        rdflib.term.Variable("builtInCat")
                    ]
                    builtInCatCutOutFam = builtInCatCutOutFam.split("#")[-1]
                    cutOutInstance[str(element._d[rdflib.term.Variable("CutInst")])] = builtInCatCutOutFam
                
                for key, value in allCutLocs.items():
                    getFam = cutOutInstance.get(key)
                    if getFam == "OST_Windows":
                        PointArray = []
                        qCutStr = """
                        SELECT ?Name ?Value WHERE
                        {
                            <%s> a bot:Element . 
                            <%s> RevitAPI:hasRevitType ?type . 
                            ?type RevitAPI:hasParameter ?paraBN . 
                            ?paraBN RevitAPI:hasName ?Name . 
                            ?paraBN RevitAPI:hasValue ?Value .
                            FILTER(?Name = 'Rohbauhoehe' || ?Name = 'Rohbaubreite') .
                        }
                        """ % (
                            key,
                            key,
                        )
                        qCut = g.query(qCutStr)
                        for CutPar in qCut.bindings:
                            if CutPar[rdflib.term.Variable("Name")] == rdflib.term.Literal(
                                "Rohbauhoehe"
                            ):
                                Rohbauhoehe = float(CutPar[rdflib.term.Variable("Value")])
                            elif CutPar[
                                rdflib.term.Variable("Name")
                            ] == rdflib.term.Literal("Rohbaubreite"):
                                Rohbaubreite = float(CutPar[rdflib.term.Variable("Value")])
                            else:
                                pass

                        NullVec = np.array([0, 0, 0])
                        aVec = (P1Vec - P0Vec) / linalg.norm(P1Vec - P0Vec)
                        bVec = (P2Vec - P1Vec) / linalg.norm(P2Vec - P1Vec)

                        x = np.array(value)
                        # "breite" here i took the "breite" (depth) of the wall.

                        P0SnVec = (
                            x + aVec * (Rohbaubreite / 2) + bVec * ((breite + 0.001) / 2)
                        )
                        P1SnVec = (
                            x - aVec * (Rohbaubreite / 2) + bVec * ((breite + 0.001) / 2)
                        )
                        P2SnVec = (
                            x - aVec * (Rohbaubreite / 2) - bVec * ((breite + 0.001) / 2)
                        )
                        P3SnVec = (
                            x + aVec * (Rohbaubreite / 2) - bVec * ((breite + 0.001) / 2)
                        )

                        PointArray = [P0SnVec, P1SnVec, P2SnVec, P3SnVec]

                        subBody = x2DDrawAndExtrude(
                            newGraph, BIM, PointArray, Rohbauhoehe + 0.001
                        )
                        extr = cutA_fromB(newGraph, BIM, extr, subBody[1])

                    if getFam == "OST_Doors":
                        PointArray = []
                        qCutStr = """
                        SELECT ?Name ?Value WHERE
                        {
                            <%s> a bot:Element . 
                            <%s> RevitAPI:hasRevitType ?type . 
                            ?type RevitAPI:hasParameter ?paraBN . 
                            ?paraBN RevitAPI:hasName ?Name . 
                            ?paraBN RevitAPI:hasValue ?Value .
                            FILTER(?Name = 'Rohbauhoehe' || ?Name = 'Rohbaubreite') .
                        }
                        """ % (
                            key,
                            key,
                        )
                        qCut = g.query(qCutStr)
                        for CutPar in qCut.bindings:
                            if CutPar[rdflib.term.Variable("Name")] == rdflib.term.Literal(
                                "Rohbauhoehe"
                            ):
                                Rohbauhoehe = float(CutPar[rdflib.term.Variable("Value")])
                            elif CutPar[
                                rdflib.term.Variable("Name")
                            ] == rdflib.term.Literal("Rohbaubreite"):
                                Rohbaubreite = float(CutPar[rdflib.term.Variable("Value")])
                            else:
                                pass

                        qStDoorsFacing = """
                        SELECT ?CutInst ?FacingDir WHERE
                        {
                            <%s> a bot:Element . 
                            <%s> RevitAPI:hasFurtherGeomParams ?pars . 
                            ?pars RevitAPI:hasCutOuts ?cutOut .
                            ?cutOut BIM:isFamInst ?CutInst .
                            ?cutOut RevitAPI:hasFacingOr ?FacingOr . 
                            ?FacingOr oop:hasListContent ?FacingOrList .
                            ?FacingOrList rdf:rest*/rdf:first ?FacingDir .
                        }
                        """ % (
                            inst,
                            inst,
                        )

                        qDoorsFacing = g.query(qStDoorsFacing)

                        allCutLocsFacing = {}
                        CutLoc = []
                        testStr = ""

                        for CutOut in qDoorsFacing.bindings:
                            newStr = CutOut._d[rdflib.term.Variable("CutInst")]
                            if newStr == testStr or testStr == "":
                                CutLoc.append(
                                    float(CutOut._d[rdflib.term.Variable("FacingDir")])
                                )
                                testStr = CutOut._d[rdflib.term.Variable("CutInst")]
                            else:
                                allCutLocsFacing[str(testStr)] = CutLoc
                                testStr = CutOut._d[rdflib.term.Variable("CutInst")]
                                CutLoc = [
                                    float(CutOut._d[rdflib.term.Variable("FacingDir")])
                                ]
                            if CutOut == qDoorsFacing.bindings[-1]:
                                allCutLocsFacing[str(testStr)] = CutLoc

                        qStDoorsHandOr = """
                        SELECT ?CutInst ?HandDir WHERE
                        {
                            <%s> a bot:Element . 
                            <%s> RevitAPI:hasFurtherGeomParams ?pars . 
                            ?pars RevitAPI:hasCutOuts ?cutOut .
                            ?cutOut BIM:isFamInst ?CutInst .
                            ?cutOut RevitAPI:hasHandOr ?HandOr . 
                            ?HandOr oop:hasListContent ?HandOrList .
                            ?HandOrList rdf:rest*/rdf:first ?HandDir .
                        }
                        """ % (
                            inst,
                            inst,
                        )

                        qDoorsHandOr = g.query(qStDoorsHandOr)

                        allCutLocsqDoorsHandOr = {}
                        CutLoc = []
                        testStr = ""

                        for CutOut in qDoorsHandOr.bindings:
                            newStr = CutOut._d[rdflib.term.Variable("CutInst")]
                            if newStr == testStr or testStr == "":
                                CutLoc.append(
                                    float(CutOut._d[rdflib.term.Variable("HandDir")])
                                )
                                testStr = CutOut._d[rdflib.term.Variable("CutInst")]
                            else:
                                allCutLocsqDoorsHandOr[str(testStr)] = CutLoc
                                testStr = CutOut._d[rdflib.term.Variable("CutInst")]
                                CutLoc = [float(CutOut._d[rdflib.term.Variable("HandDir")])]
                            if CutOut == qDoorsHandOr.bindings[-1]:
                                allCutLocsqDoorsHandOr[str(testStr)] = CutLoc

                        handOr = allCutLocsqDoorsHandOr.get(key)
                        handOr = np.array(handOr)
                        facingOr = allCutLocsFacing.get(key)
                        facingOr = np.array(facingOr)

                        x = np.array(value)

                        P0SnVec = x + facingOr * ((breite + 0.001) / 2)
                        P1SnVec = (
                            x - handOr * (Rohbaubreite) + facingOr * ((breite + 0.001) / 2)
                        )
                        P2SnVec = (
                            x - handOr * (Rohbaubreite) - facingOr * ((breite + 0.001) / 2)
                        )
                        P3SnVec = x - facingOr * ((breite + 0.001) / 2)

                        PointArray = [P0SnVec, P1SnVec, P2SnVec, P3SnVec]
                        try:
                            subBody = x2DDrawAndExtrude(
                                newGraph, BIM, PointArray, Rohbauhoehe + 0.001
                            )
                            extr = cutA_fromB(newGraph, BIM, extr, subBody[1])
                        except:
                            pass
                newGraph.add((inst, omg.hasGeometry, extr))
                newGraph.add(
                        (inst, BIM.isPartOfProject, ProjectName)
                    )

        if bStr == "OST_Floors" or bStr == "OST_StructuralFoundation":
            qS = (
                """
                SELECT ?listArr ?ListList ?oneList WHERE
                {
                <%s> RevitAPI:hasFurtherGeomParams ?parBN . 
                ?parBN RevitAPI:hasPolyline ?Polyline . 
                ?Polyline oop:hasListContent ?list .
                ?list rdf:rest*/rdf:first ?listArr . 
                ?listArr oop:hasListContent ?anotherList . 
                ?anotherList rdf:rest*/rdf:first ?ListList . 
                OPTIONAL {
                ?ListList oop:hasListContent ?lastLevelList . 
                ?lastLevelList rdf:rest*/rdf:first ?oneList
                }
                }
                """
                % inst
            )
            qInst1 = g.query(qS)
            
            firstLevel = []
            secondLevel = []
            thirdLevel = []
            SLI = ""
            getLen = len(qInst1.bindings)
            hasCutOuts = False
            #  if oneList is not in response ==> the floor has no cutOuts. 
            if len(qInst1.bindings)!= 0:
                if rdflib.term.Variable("oneList") not in qInst1.bindings[0]:
                    
                    hasCutOuts = False
                    for k, bind in enumerate(qInst1.bindings):
                        if k == 0:
                            FLI = bind._d[rdflib.term.Variable("listArr")]
                            secondLevel.append(float(bind._d[rdflib.term.Variable("ListList")]))
                        else:
                            newFLI = bind._d[rdflib.term.Variable("listArr")]
                            if FLI == newFLI:
                                secondLevel.append(float(bind._d[rdflib.term.Variable("ListList")]))
                                FLI = newFLI
                            else:
                                firstLevel.append(secondLevel)
                                secondLevel = [float(bind._d[rdflib.term.Variable("ListList")])]
                                FLI = newFLI
                            if k ==getLen -1:
                                firstLevel.append(secondLevel)        
                    # todo: this is very bad written but works as if there is only one list later which is the "create" List.
                    # better would be handling instances without cutOuts different.
                    firstLevel = [firstLevel]
            
                # else: the floor has cutOuts and therefore one list more
                else:
                    hasCutOuts = True
                    for k, bind in enumerate(qInst1.bindings):
                        if k == 0:
                            FLI = bind._d[rdflib.term.Variable("listArr")]
                            SLI = bind._d[rdflib.term.Variable("ListList")]
                            thirdLevel.append(float(bind._d[rdflib.term.Variable("oneList")]))
                        else:
                            newFLI = bind._d[rdflib.term.Variable("listArr")]
                            newSLI = bind._d[rdflib.term.Variable("ListList")]
                            if SLI == newSLI:
                                thirdLevel.append(float(bind._d[rdflib.term.Variable("oneList")]))
                                SLI = newSLI
                            else:
                                secondLevel.append(thirdLevel)
                                thirdLevel = []
                                thirdLevel.append(float(bind._d[rdflib.term.Variable("oneList")]))
                                SLI = newSLI

                            if FLI != newFLI:
                                firstLevel.append(secondLevel)
                                secondLevel = []
                                FLI = newFLI

                            if k == getLen - 1:
                                secondLevel.append(thirdLevel)
                                firstLevel.append(secondLevel)        
                
                qH = """
                    SELECT ?Name ?Value WHERE
                    {
                    <%s> a bot:Element . 
                    <%s> RevitAPI:hasRevitType ?type . 
                    ?type RevitAPI:hasParameter ?paraBN .
                    ?paraBN RevitAPI:hasName ?Name . 
                    ?paraBN RevitAPI:hasValue ?Value .
                    FILTER(?Name = 'Standarddicke') . 
                    }
                    """ % (
                    inst,
                    inst,
                )
                qHoehe = g.query(qH)
                
                if len(qHoehe.bindings) != 0:
                    hight = qHoehe.bindings[0]._d[rdflib.term.Variable("Value")]
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
                            x=np.array(elemX)
                            y=np.array(elemY)
                            AreaCompare.append(PolyArea(x,y))
                        utterBound = np.argmax(AreaCompare)
                        # extrude the utter Bound of the floor
                        extrusion = x2DDrawAndExtrude(newGraph, BIM, firstLevel[utterBound], hight)
                        ext = extrusion[1]
                        del firstLevel[utterBound]

                        for elem in firstLevel:
                            subBody = x2DDrawAndExtrude(newGraph, BIM, elem, float(hight)+0.001)
                            ext = cutA_fromB(newGraph, BIM, ext, subBody[1])

                newGraph.add((inst, omg.hasGeometry, ext))
                newGraph.add((inst, BIM.isPartOfProject, ProjectName))



    newGraph.bind("BIM", BIM)
    newGraph.bind("omg", omg)
    newGraph.bind("occ", occ)
    newGraph.bind("oop", oop)
    newGraph.bind("bot", bot)


    return newGraph



def addBotTriples(g):
    
    graphWithBot = Graph()
    bot = Namespace("https://w3id.org/bot#")
    
    
    qString1 = """SELECT ?s WHERE {?s rdf:type bot:Building }"""
    qry1 = g.query(qString1)
    
    for element1 in qry1.bindings:
        graphWithBot.add((element1["s"], RDF.type, bot.Building))
    
    qString2 = """SELECT ?s ?o WHERE {?s bot:hasElement ?o }"""
    qry2 = g.query(qString2)
    
    for element2 in qry2.bindings:
        graphWithBot.add((element2["s"], bot.hasElement, element2["o"]))

    qString3 = """SELECT ?s WHERE {?s rdf:type bot:Element }"""
    qry3 = g.query(qString3)
    
    for element3 in qry3.bindings:
        graphWithBot.add((element3["s"], RDF.type, bot.Element))

    graphWithBot.bind("bot", bot)

    return graphWithBot

#if __name__ == "__main__":
    # parser = ArgumentParser(
    # description="revit export to opencascade geometric description")
    # parser.add_argument("-file", dest="filename", required=True, help="input a valid ttl file", metavar="TurtleFile")
    # args = parser.parse_args()
    
    # getAbsPath = os.path.join(os.getcwd(), args.filename)
    # g = Graph()
    # newGraph = Graph()
    # ttlName = args.filename[6:]
    # ProjName = ttlName.split(".")[0]
    
    # g.load(getAbsPath, format="turtle")
    
    # importGeomData(g, newGraph)
    
    # filename = "GeomGraph_%s.ttl"%ProjName
    # fileLocation = "./"
    # output = os.path.join(fileLocation, filename)

    # newGraph.serialize(output, format="turtle")
    # print("File %s ready inside folder %s" % (filename, fileLocation))
