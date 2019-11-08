# -*- coding: cp852 -*-
try:
    import sys
    sys.path.append("C:\Program Files (x86)\IronPython 2.7\Lib\site-packages")
    import clr
    from Autodesk.Revit.DB import *
    import Autodesk
    import System
    from System.Collections.Generic import *
    import random
    import httplib
    import urllib
    import json
    from threading import Thread
except:
    print("some imports didn't work")

clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")

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
        IDList.append("_%s" %
                      "".join(random.choice(myCharset) for _ in range(8)))
    return IDList


def toUTF8(unicode_string):
    utf8_string = unicode_string.encode("utf-8")
    for k in umlaute_dict.keys():
        utf8_string = utf8_string.replace(k, umlaute_dict[k])
    return utf8_string.decode()


def getParamValue(entry, paramNameUn):

    paramValueUnStorageType = entry.Element.GetParameters(
        paramNameUn)[0].StorageType
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


def OST_Walls_GeomParams(inst):
    paramDict = {}
    # Type of Line
    isType = inst.Location.Curve.GetType().Name
    paramDict["isType"] = isType
    if str(isType) == "Line":
        normDir = inst.Location.Curve.Direction.Normalize()
        direct = [normDir.X, normDir.Y, normDir.Z]
        paramDict["hasDirection"] = direct
        # startPoint
        startP = [
            inst.Location.Curve.GetEndPoint(0).X,
            inst.Location.Curve.GetEndPoint(0).Y,
            inst.Location.Curve.GetEndPoint(0).Z,
        ]
        paramDict["hasExactStartLoc"] = startP
        # endPoint
        endP = [
            inst.Location.Curve.GetEndPoint(1).X,
            inst.Location.Curve.GetEndPoint(1).Y,
            inst.Location.Curve.GetEndPoint(1).Z,
        ]
        paramDict["hasExactEndLoc"] = endP
        #  get all the openings in a specific wall element an handle them
        inserts = inst.FindInserts(True, False, False, False)
        if len(inserts) == 0:
            pass
        else:
            cutOutList = []
            for openingsInst in inserts:
                elem1 = doc.GetElement(openingsInst)
                hasCutOuts = {}
                hasCutOuts["CutInst"] = int(elem1.Id.IntegerValue)
                instLocPoint = [
                    elem1.Location.Point.X,
                    elem1.Location.Point.Y,
                    elem1.Location.Point.Z,
                ]
                hasCutOuts["hasExactLoc"] = instLocPoint
                instHandOr = [
                    elem1.HandOrientation.X,
                    elem1.HandOrientation.Y,
                    elem1.HandOrientation.Z,
                ]
                hasCutOuts["hasHandOr"] = instHandOr
                instFacingOr = [
                    elem1.FacingOrientation.X,
                    elem1.FacingOrientation.Y,
                    elem1.FacingOrientation.Z,
                ]
                hasCutOuts["hasFacingOr"] = instFacingOr

                instToFind = None
                for BIC in allBuiltInCats:
                    for group in BIC:
                        for instances in group["hasInstances"]:
                            if instances[
                                    "hasRevitID"] == elem1.Id.IntegerValue:
                                instToFind = instances["fromRevitFamID"]
                                hasCutOuts["hasRevitType"] = instToFind
                if instToFind != None:
                    hasCutOuts["isFamInst"] = instToFind
                cutOutList.append(hasCutOuts)

            paramDict["hasCutOuts"] = cutOutList
    else:
        print("This does not get handeled until now")
    return paramDict


def OST_Columns_GeomParams(inst):
    paramDict = {}
    try:
        in1 = inst.GetSweptProfile()
        in2 = in1.GetSweptProfile()
        drivingCurve = in1.GetDrivingCurve()
        dCStartP = drivingCurve.GetEndPoint(0)
        dCEndP = drivingCurve.GetEndPoint(1)
        curveArr = []
        for i, curve in enumerate(in2.Curves):
            curveDict = {}
            startP = [
                curve.GetEndPoint(0).X,
                curve.GetEndPoint(0).Y,
                curve.GetEndPoint(0).Z,
            ]
            curveDict["hasCurveNr"] = i
            curveDict["hasExactStartLoc"] = startP
            curveDict["hasLength"] = drivingCurve.Length

            CuType = curve.GetType().Name
            curveDict["isOfType"] = CuType
            if CuType == "Arc":
                centerP = [curve.Center.X, curve.Center.Y, curve.Center.Z]
                curveDict["hasCenter"] = centerP
                curveDict["hasRadius"] = curve.Radius
            curveArr.append(curveDict)
        paramDict["hasCurve"] = curveArr
        LocPoint = [inst.Location.Point.X, inst.Location.Point.Y, dCStartP.Z]
        paramDict["hasLocation"] = LocPoint
    except:
        print("This instance does not have a swept profile")
    return paramDict


def OST_FloorOrStructuralFoundation_GeomParams(inst):
    paramDict = {}
    if inst.GetType().Name != "FamilyInstance":
        # the inst obj is a "Autodesk.Revit.DB.Floor object"  DB object. To get the Element one
        # has to do the following
        botface = HostObjectUtils.GetBottomFaces(inst)
        element = doc.GetElement(botface[0])
        elementface = element.GetGeometryObjectFromReference(botface[0])
        AllCurves = []
        for EdgeArray in elementface.EdgeLoops:
            AllPoints = []
            for Edge in EdgeArray:
                NewEdgeArray = []
                NewEdgeArray.append(Edge.AsCurve().GetEndPoint(0).X)
                NewEdgeArray.append(Edge.AsCurve().GetEndPoint(0).Y)
                NewEdgeArray.append(Edge.AsCurve().GetEndPoint(0).Z)
                AllPoints.append(NewEdgeArray)
            AllCurves.append(AllPoints)
        paramDict["hasPolyline"] = AllCurves
    else:
        pass
        # this is to do, if inst is a FamInstance !!!
    return paramDict


def sendRequest(conn, typeOfReq, route, json_data, headers):
    conn.request(typeOfReq, route, json_data, headers)


dataDict = {}

dataDict["ProjectID"] = give_me_new_IDs(1)[0]
dataDict["ProjectType"] = "bot.Building"

builtInCats = [
    "OST_Windows",
    "OST_Doors",
    "OST_Walls",
    "OST_Floors",
    "OST_StructuralColumns",
    "OST_StructuralFoundation",
]

allBuiltInCats = []
for builtInCat in builtInCats:
    builtInCatDict = {}

    # first : Instances

    inst_collector = ""
    inst_collector = (FilteredElementCollector(doc).OfCategory(
        getattr(BuiltInCategory,
                builtInCat)).WhereElementIsNotElementType().ToElements())

    inst_To_Fam_ID_collection = []
    if inst_collector != "":
        instances = []
        for inst in inst_collector:
            instanceDict = {}
            actualInstance = give_me_new_IDs(1)[0]
            if inst.GetType().Name == "Wall":
                famID = inst.WallType.Id.IntegerValue
            elif inst.GetType().Name == "Floor":
                famID = inst.FloorType.Id.IntegerValue
            else:
                famID = inst.Symbol.Id.IntegerValue
            inst_To_Fam_ID_collection.append(famID)
            instanceDict["fromRevitFamID"] = famID
            instanceDict["hasName"] = toUTF8(inst.Name)
            instanceDict["hasRevitID"] = inst.Id.IntegerValue
            instanceDict["fromBuiltInCategory"] = builtInCat

            paramDict = {}
            for entry in inst.GetOrderedParameters():
                parName = entry.Definition.Name
                paramValue = getParamValue(entry, parName)
                # TODO ... grab all Element IDs and look recursive for there type where they are used (by there ID)
                if isinstance(paramValue, ElementId):
                    paramDict[toUTF8(parName)] = str(paramValue)
                else:
                    paramDict[toUTF8(parName)] = paramValue
            instanceDict["hasParameterSet"] = paramDict
            if builtInCat == "OST_Walls":
                instanceDict["hasFurtherGeomParams"] = OST_Walls_GeomParams(
                    inst)
            elif builtInCat == "OST_StructuralColumns":
                instanceDict["hasFurtherGeomParams"] = OST_Columns_GeomParams(
                    inst)
            elif builtInCat == "OST_Floors" or builtInCat == "OST_StructuralFoundation":
                instanceDict[
                    "hasFurtherGeomParams"] = OST_FloorOrStructuralFoundation_GeomParams(
                        inst)
            instances.append(instanceDict)
        builtInCatDict["Instances"] = instances

    # second : Types

    type_collector = ""
    type_collector = (FilteredElementCollector(doc).OfCategory(
        getattr(BuiltInCategory,
                builtInCat)).WhereElementIsElementType().ToElements())

    if type_collector != "":
        families = []
        for elemType in type_collector:
            # here just add types to the dataset if an instance of that type is used in the project
            if elemType.Id.IntegerValue in inst_To_Fam_ID_collection:
                typeDict = {}
                typeDict["hasRevitID"] = elemType.Id.IntegerValue
                famNameCol = toUTF8(str(elemType.FamilyName))
                typeDict["hasFamName"] = famNameCol
                typeDict["fromBuiltInCategory"] = builtInCat
                paramDict = {}
                for entry in elemType.GetOrderedParameters():
                    parName = entry.Definition.Name
                    paramValue = getParamValue(entry, parName)
                    # TODO ... grab all Element IDs and look recursive for there type where they are used (by there ID)
                    if isinstance(paramValue, ElementId):
                        paramDict[toUTF8(parName)] = str(paramValue)
                    else:
                        paramDict[toUTF8(parName)] = paramValue
                typeDict["hasParameterSet"] = paramDict
                families.append(typeDict)
            else:
                pass
        builtInCatDict["Families"] = families

    if builtInCatDict["Families"] and builtInCatDict["Instances"]:
        for revitFam in builtInCatDict["Families"]:
            famID = revitFam["hasRevitID"]
            hasInstances = []
            for inst in builtInCatDict["Instances"]:
                if inst["fromRevitFamID"] == famID:
                    hasInstances.append(inst)
            revitFam["hasInstances"] = hasInstances
        allBuiltInCats.append(builtInCatDict["Families"])
dataDict["BuiltInCategories"] = allBuiltInCats

jsonContent = {"data": dataDict}

json_data = json.dumps(jsonContent)
#print(json_data)
# # TODO change Endpoint
# conn = httplib.HTTPConnection(host="10.200.29.203", port="22633")

conn = httplib.HTTPConnection(host="localhost", port="22633")

headers = {"Content-type": "application/json"}

typeOfReq = "POST"
route = "/revitAPI/fetchRevitData"

process = Thread(target=sendRequest,
                 args=[conn, typeOfReq, route, json_data, headers])
process.start()

# # response = conn.getresponse()
# print(response.status, response.reason)
