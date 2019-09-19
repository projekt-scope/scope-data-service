# -*- coding: cp852 -*-
try:
    import sys
    sys.path.append("C:\Program Files (x86)\IronPython 2.7\Lib\site-packages")
    import clr
    import os
    import rdflib
    from rdflib import Graph, Namespace, RDF, XSD, BNode, Literal
    from Autodesk.Revit.DB import *
    import math
    import Autodesk
    import System
    from System.Collections.Generic import *
    import random
except:
    print("some imports didn't work")

clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")

clr.AddReference("RevitAPI")


app = __revit__.Application
doc = __revit__.ActiveUIDocument.Document

umlaute_dict = {
    "\xc3\xa4": "ae",
    "\xc3\xb6": "oe",
    "\xc3\xbc": "ue",
    "\xc3\x84": "Ae",
    "\xc3\x96": "Oe",
    "\xc3\x9c": "Ue",
    "\xc3\x9f": "ss",
    "\xc3\xB8": "D",
    "\xe2\x82\xAC": "Euro",
    "\xe2\x80\xA6": "x",
    "\xc2\xb0": "Degree",
    "'": "HochKomma"
}  # UTF-8 (hex)    - from:    http://www.fileformat.info/info/unicode/char/search.htm

myCharset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def give_me_new_IDs(RangeIDs):
    IDList = []
    for IDs in range(RangeIDs):
        IDList.append("_%s" % "".join(random.choice(myCharset)
                                      for _ in range(8)))
    return IDList


def toUTF8(unicode_string):
    utf8_string = unicode_string.encode("utf-8")
    for k in umlaute_dict.keys():
        utf8_string = utf8_string.replace(k, umlaute_dict[k])
    return utf8_string.decode()


def getParamValue(entry, paramNameUn):

    paramValueUnStorageType = entry.Element.GetParameters(paramNameUn)[
        0].StorageType
    paramValue = None
    if str(paramValueUnStorageType) == "String":
        paramValueUn = entry.Element.GetParameters(paramNameUn)[0].AsString()
        if paramValueUn != None:
            paramValue = toUTF8(paramValueUn)
            paramValue = """%s""" % paramValue
        else:
            paramValue = "None"
    elif str(paramValueUnStorageType) == "Double":
        paramValue = entry.Element.GetParameters(paramNameUn)[0].AsDouble()
    elif str(paramValueUnStorageType) == "Integer":
        paramValue = entry.Element.GetParameters(paramNameUn)[0].AsInteger()
    elif str(paramValueUnStorageType) == "ElementId":
        paramValue = entry.Element.GetParameters(paramNameUn)[0].AsElementId()
        tmp = doc.GetElement(paramValue)
    elif str(paramValueUnStorageType) == "None":
        paramValue = None
    else:
        print("Error, noch nicht abgedeckt")
        paramValue = []
    return paramValue


def createList(graph, ListItems):
    """
    this function converts a "python" list to an ordered rdf-list
    """

    if not isinstance(ListItems, list) or ListItems == []:
        raise TypeError(
            "ListItems must be of type list with at least one element")

    ListNode = oop[give_me_new_IDs(1)[0]]
    graph.add((ListNode, RDF.type, oop.List))
    ItemName = BNode()
    graph.add((ListNode, oop.hasListContent, ItemName))
    for i1 in range(len(ListItems) - 1):
        Item = ListItems[i1]
        NextItem = BNode()
        if type(Item) == rdflib.term.URIRef:
            graph.add((ItemName, RDF.first, Item))
        else:
            graph.add((ItemName, RDF.first, Literal(Item)))
        graph.add((ItemName, RDF.rest, NextItem))
        ItemName = NextItem

    if type(ListItems[-1]) == rdflib.term.URIRef:
        graph.add((NextItem, RDF.first, ListItems[-1]))
    else:
        graph.add((NextItem, RDF.first, Literal(ListItems[-1])))

    graph.add((NextItem, RDF.rest, RDF.nil))

    return ListNode


g = Graph()
BIM = Namespace("https://projekt-scope.de/ontologies/BIM#")
Revit = Namespace("https://projekt-scope.de/software/Revit#")
RevitAPI = Namespace("https://projekt-scope.de/software/RevitAPI#")
oop = Namespace("https://projekt-scope.de/ontologies/oop#")
bot = Namespace("https://w3id.org/bot#")

builtInCats = [
    "OST_Windows",
    "OST_Doors",
    "OST_Walls",
    "OST_Floors",
    "OST_StructuralColumns",
    "OST_StructuralFoundation",
]
IdConnector = {}

ProjectName = doc.ProjectInformation.Name
ProjID = BIM[give_me_new_IDs(1)[0]]

g.add((ProjID, RevitAPI.hasName, Literal(ProjectName)))
g.add((ProjID, RDF.type, bot.Building))


def addTypeToGraph(builtInCat, fNode, famID, allTypes):
    getFamID = allTypes.get(famID)
    FamUriRefNode = getFamID.get("UriRef")
    g.add((FamUriRefNode, RevitAPI.fromBuiltInCategory, Revit[builtInCat]))
    g.add((fNode, RevitAPI.hasRevitType, FamUriRefNode))
    g.add((FamUriRefNode, RDF.type, Revit.Type))
    g.add((FamUriRefNode, RevitAPI.hasName, Literal(getFamID.get("famName"))))
    for entry in getFamID.get("paramList"):
        anode = BNode()
        g.add((FamUriRefNode, RevitAPI.hasParameter, anode))
        g.add((anode, RevitAPI.hasName, Literal(toUTF8(entry[0]))))
        g.add((anode, RevitAPI.hasValue, Literal(entry[1])))


for builtInCat in builtInCats:
    InstID = give_me_new_IDs(1)[0]

    inst_collector = (
        FilteredElementCollector(doc)
        .OfCategory(getattr(BuiltInCategory, builtInCat))
        .WhereElementIsNotElementType()
        .ToElements()
    )
    type_collector = (
        FilteredElementCollector(doc)
        .OfCategory(getattr(BuiltInCategory, builtInCat))
        .WhereElementIsElementType()
        .ToElements()
    )

    allTypes = {}

    # loop through all types of a given BuiltInCategory
    for elemType in type_collector:
        famNameCol = toUTF8(str(elemType.FamilyName))
        TNode = BIM[give_me_new_IDs(1)[0]]
        collTypes = {}
        allTypes[elemType.Id.IntegerValue] = collTypes
        collTypes["UriRef"] = TNode
        collTypes["InstID"] = InstID
        collTypes["famName"] = famNameCol

        paramList = []
        for entry in elemType.GetOrderedParameters():
            parName = entry.Definition.Name
            paramValue = getParamValue(entry, parName)
            sepParam = [toUTF8(parName), paramValue]
            paramList.append(sepParam)

        collTypes["paramList"] = paramList

    # loop through all instances of a given BuiltInCategory
    for inst in inst_collector:
        if inst.GetType().Name == "Wall":
            famID = inst.WallType.Id.IntegerValue
        elif inst.GetType().Name == "Floor":
            famID = inst.FloorType.Id.IntegerValue
        else:
            famID = inst.Symbol.Id.IntegerValue
        fNode = BIM[give_me_new_IDs(1)[0]]
        g.add((fNode, RevitAPI.hasName, Literal(toUTF8(inst.Name))))
        g.add((fNode, RevitAPI.hasRevitID, Literal(inst.Id.IntegerValue)))

        addTypeToGraph(builtInCat, fNode, famID, allTypes)

        g.add((fNode, RDF.type, bot.Element))
        # g.add((fNode, RevitAPI.isPartOfProject, Literal(ProjectName)))
        g.add((ProjID, bot.hasElement, fNode))
        IdConnector[inst.Id.IntegerValue] = fNode
        for entry in inst.GetOrderedParameters():
            parName1 = entry.Definition.Name
            paramValue = getParamValue(entry, parName1)
            anode = BNode()
            g.add((fNode, RevitAPI.hasParameter, anode))
            g.add((anode, RevitAPI.hasName, Literal(toUTF8(parName1))))
            g.add((anode, RevitAPI.hasValue, Literal(paramValue)))

        ############      OST_Walls      ############

        if builtInCat == "OST_Walls":
            isType = inst.Location.Curve.GetType().Name
            geomPar = give_me_new_IDs(1)[0]
            g.add((fNode, RevitAPI.hasFurtherGeomParams, BIM[geomPar]))
            # Type of Line
            g.add((BIM[geomPar], RevitAPI.isBasedOn, Literal(isType)))
            # if type == Line, then get direction
            if str(isType) == "Line":
                normDir = inst.Location.Curve.Direction.Normalize()
                direct = [normDir.X, normDir.Y, normDir.Z]
                dirNode = createList(g, direct)
                g.add((BIM[geomPar], RevitAPI.hasDirection, dirNode))

                # startPoint
                startP = [
                    inst.Location.Curve.GetEndPoint(0).X,
                    inst.Location.Curve.GetEndPoint(0).Y,
                    inst.Location.Curve.GetEndPoint(0).Z,
                ]
                startLocNode = createList(g, startP)
                g.add((BIM[geomPar], RevitAPI.hasExactStartLoc, startLocNode))

                # endPoint
                endP = [
                    inst.Location.Curve.GetEndPoint(1).X,
                    inst.Location.Curve.GetEndPoint(1).Y,
                    inst.Location.Curve.GetEndPoint(1).Z,
                ]
                endLocNode = createList(g, endP)
                g.add((BIM[geomPar], RevitAPI.hasExactEndLoc, endLocNode))

                #  get all the openings in a specific wall element an handle them
                inserts = inst.FindInserts(True, False, False, False)
                if len(inserts) == 0:
                    pass
                else:
                    for openingsInst in inserts:
                        cutOutNode = give_me_new_IDs(1)
                        g.add(
                            (BIM[geomPar], RevitAPI.hasCutOuts, BIM[cutOutNode[0]]))
                        elem1 = doc.GetElement(openingsInst)
                        g.add(
                            (
                                BIM[cutOutNode[0]],
                                RevitAPI.CutInst,
                                Literal(int(elem1.Id.IntegerValue)),
                            )
                        )
                        instLocPoint = [
                            elem1.Location.Point.X,
                            elem1.Location.Point.Y,
                            elem1.Location.Point.Z,
                        ]
                        ListNode1 = createList(g, instLocPoint)
                        g.add(
                            (BIM[cutOutNode[0]], RevitAPI.hasExactLoc, ListNode1))

                        instHandOr = [
                            elem1.HandOrientation.X,
                            elem1.HandOrientation.Y,
                            elem1.HandOrientation.Z,
                        ]
                        ListNode2 = createList(g, instHandOr)
                        g.add(
                            (BIM[cutOutNode[0]], RevitAPI.hasHandOr, ListNode2))

                        instFacingOr = [
                            elem1.FacingOrientation.X,
                            elem1.FacingOrientation.Y,
                            elem1.FacingOrientation.Z,
                        ]
                        ListNode3 = createList(g, instFacingOr)
                        g.add(
                            (BIM[cutOutNode[0]], RevitAPI.hasFacingOr, ListNode3))

                        instToFind = IdConnector.get(
                            int(elem1.Id.IntegerValue))
                        if instToFind != None:
                            g.add(
                                (BIM[cutOutNode[0]], BIM.isFamInst, instToFind))
        ############      OST_StructuralColumns      ############

        if builtInCat == "OST_StructuralColumns":
            geomPar = give_me_new_IDs(1)[0]
            g.add((fNode, RevitAPI.hasFurtherGeomParams, BIM[geomPar]))
            try:
                in1 = inst.GetSweptProfile()
                in2 = in1.GetSweptProfile()
                drivingCurve = in1.GetDrivingCurve()
                dCStartP = drivingCurve.GetEndPoint(0)
                dCEndP = drivingCurve.GetEndPoint(1)
                nG = BNode()
                for i, curve in enumerate(in2.Curves):
                    startP = [
                        curve.GetEndPoint(0).X,
                        curve.GetEndPoint(0).Y,
                        curve.GetEndPoint(0).Z,
                    ]
                    curveNode = give_me_new_IDs(1)[0]
                    g.add((BIM[geomPar], RevitAPI.hasCurve, BIM[curveNode]))
                    g.add((BIM[curveNode], BIM.hasCurveNr, Literal(i)))
                    startLocNode = createList(g, startP)
                    g.add(
                        (BIM[curveNode], RevitAPI.hasExactStartLoc, startLocNode))
                    CuType = curve.GetType().Name
                    g.add((BIM[curveNode], RevitAPI.isOfType, Literal(CuType)))
                    if CuType == "Arc":
                        centerP = [curve.Center.X,
                                   curve.Center.Y, curve.Center.Z]
                        centerNode = createList(g, centerP)
                        g.add((BIM[curveNode], RevitAPI.hasCenter, centerNode))
                        g.add(
                            (BIM[curveNode], RevitAPI.hasRadius,
                             Literal(curve.Radius))
                        )

                    g.add(
                        (
                            BIM[geomPar],
                            RevitAPI.hasLength,
                            Literal(in1.GetDrivingCurve().Length),
                        )
                    )
                # First attempt was to take the location Point of a column. But the loc. point just has an x and y coord. Z is always = 0
                # LocPoint = []
                # LocPoint.append(inst.Location.Point.X)
                # LocPoint.append(inst.Location.Point.Y)
                # LocPoint.append(inst.Location.Point.Z)
                # Second attempt is to take the coords of the driving Curve. But its not clear if the driving Curve is in the center of the column.
                # So i take the x and y coord of the location Point and the z coord of the driving Curve.
                LocPoint = [inst.Location.Point.X,
                            inst.Location.Point.Y, dCStartP.Z]
                LocPointNode = createList(g, LocPoint)
                g.add((BIM[geomPar], RevitAPI.hasLocation, LocPointNode))
            except:
                print("This instance does not have a swept profile")
        ############      OST_Floors      ############

        if builtInCat == "OST_Floors" or builtInCat == "OST_StructuralFoundation":

            if inst.GetType().Name != "FamilyInstance":
                # the inst obj is a "Autodesk.Revit.DB.Floor object"  DB object. To get the Element one
                # has to do the following
                botface = HostObjectUtils.GetBottomFaces(inst)
                element = doc.GetElement(botface[0])
                elementface = element.GetGeometryObjectFromReference(
                    botface[0])
                AllCurves = []

                # doing the following two times (collecting Curves and Extracting afterwards)
                # just because i want to provide the array for (perhaps) later use
                for EdgeArray in elementface.EdgeLoops:
                    CurveArr = []
                    for Edge in EdgeArray:
                        CurveArr.append(Edge.AsCurve())
                    AllCurves.append(CurveArr)
                # second time: splitting what was created just above
                AllPoints = []
                for CurveArray in AllCurves:
                    innerPoints = []
                    for oneCurve in CurveArray:
                        onePoint = [
                            oneCurve.GetEndPoint(0).X,
                            oneCurve.GetEndPoint(0).Y,
                            oneCurve.GetEndPoint(0).Z,
                        ]
                        innerPoints.append(onePoint)
                    AllPoints.append(innerPoints)

                ListOfListNodeArr = []

                for listArray in AllPoints:
                    collectList = []
                    for oneList in listArray:
                        ListNode = createList(g, oneList)
                        collectList.append(ListNode)
                    ListOfListNode = createList(g, collectList)
                    ListOfListNodeArr.append(ListOfListNode)

                if len(ListOfListNodeArr) == 1:
                    furParNode = BIM[give_me_new_IDs(1)[0]]
                    g.add((fNode, RevitAPI.hasFurtherGeomParams, furParNode))
                    g.add((furParNode, RevitAPI.hasPolyline,
                           ListOfListNodeArr[0]))

                else:
                    listOfArrays = createList(g, ListOfListNodeArr)
                    furParNode = BIM[give_me_new_IDs(1)[0]]
                    g.add((fNode, RevitAPI.hasFurtherGeomParams, furParNode))
                    g.add((furParNode, RevitAPI.hasPolyline, listOfArrays))
            else:
                pass
                # this is to do, if inst is a FamInstance !!!


g.bind("Revit", Revit)
g.bind("RevitAPI", RevitAPI)
g.bind("BIM", BIM)
g.bind("oop", oop)
g.bind("bot", bot)


filename = "REVIT_%s.ttl" % ProjectName
fileLocation = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
output = os.path.join(fileLocation, filename)

g.serialize(output, format="turtle")

print("File %s ready inside folder %s" % (filename, fileLocation))
