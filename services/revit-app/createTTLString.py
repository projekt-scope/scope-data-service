import random

BIM = "https://projekt-scope.de/ontologies/BIM#"
RevitAPI = "https://projekt-scope.de/software/RevitAPI#"
rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
bot = "https://w3id.org/bot#"
oop = "https://projekt-scope.de/ontologies/oop#"

myCharset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def give_me_new_IDs(RangeIDs):
    IDList = []
    for IDs in range(RangeIDs):
        IDList.append("_%s" % "".join(random.choice(myCharset)
                                      for _ in range(8)))
    return IDList


class RevitFamily(object):
    instances = []

    def __init__(self, builtInCategory, revitID, parameterSet):
        self.builtInCategory = builtInCategory
        self.revitID = revitID
        self.parameterSet = parameterSet
        self.FamilyNode = "%s%s" % (BIM, give_me_new_IDs(1)[0])
        RevitFamily.instances.append(self)

    def addFamTTLString(self, TTLString):
        for key in self.parameterSet:
            blNode = "_:%s" % give_me_new_IDs(1)[0]
            TTLString += "<%s> <%s> %s . " % (self.FamilyNode,
                                              RevitAPI + "hasParameter", blNode)
            TTLString += "%s <%s> '%s' . " % (blNode,
                                              RevitAPI + "hasName", key)
            TTLString += "%s <%s> '%s' . " % (blNode, RevitAPI +
                                              "hasValue", self.parameterSet[key])
            # print(self.parameterSet)
            # TTLString += "<%s> <%s> '%s' . " % (
            #     self.FamilyNode, RevitAPI + "fromBuiltInCategory", self.parameterSet["fromBuiltInCategory"])
        return TTLString

    # class method to access the get method without any instance
    @classmethod
    def get(cls, revitID):
        return [inst for inst in cls.instances if inst.revitID == revitID]


def addRevitColInst(TTLString, revitInst, oneRevitFam, ProjectNode):
    InstanceNode = "%s%s" % (BIM, give_me_new_IDs(1)[0])
    FamilyNode = oneRevitFam.FamilyNode
    TTLString += "<%s> <%s> <%s> . " % (ProjectNode, bot +
                                        "hasElement", InstanceNode)
    TTLString += "<%s> <%s> <%s> . " % (
        InstanceNode, rdf + "type", bot + "Element")
    TTLString += "<%s> <%s> <%s> . " % (InstanceNode,
                                        RevitAPI + "hasRevitType", FamilyNode)
    TTLString += "<%s> <%s> '%s' . " % (FamilyNode,
                                        RevitAPI + "fromBuiltInCategory", revitInst["fromBuiltInCategory"])
    geomParamNode = "%s%s" % (BIM, give_me_new_IDs(1)[0])
    TTLString += "<%s> <%s> <%s> . " % (InstanceNode,
                                        RevitAPI + "hasFurtherGeomParams", geomParamNode)

    ListNode6 = "%s%s" % (oop, give_me_new_IDs(1)[0])
    TTLString += "<%s> <%s> <%s> . " % (geomParamNode,
                                        RevitAPI + "hasLocation", ListNode6)
    TTLString += "<%s> <%s> <%s> . " % (
        ListNode6, rdf + "type", oop + "List")
    TTLString += "<%s> <%s> (%s %s %s) . " % (ListNode6, oop + "hasListContent",
                                              revitInst["hasFurtherGeomParams"]["hasLocation"][0], revitInst["hasFurtherGeomParams"]["hasLocation"][1], revitInst["hasFurtherGeomParams"]["hasLocation"][2])
    TTLString += "<%s> <%s> '%s' . " % (geomParamNode,
                                        RevitAPI + "hasLength", revitInst["hasFurtherGeomParams"]["hasCurve"][0]["hasLength"])
    for curve in revitInst["hasFurtherGeomParams"]["hasCurve"]:
        curveNode = "%s%s" % (BIM, give_me_new_IDs(1)[0])
        TTLString += "<%s> <%s> <%s> . " % (geomParamNode, RevitAPI +
                                            "hasCurve", curveNode)
        TTLString += "<%s> <%s> '%s' . " % (curveNode, RevitAPI +
                                            "hasCurveNr", curve["hasCurveNr"])
        TTLString += "<%s> <%s> '%s' . " % (curveNode, RevitAPI +
                                            "isOfType", curve["isOfType"])

        ListNode7 = "%s%s" % (oop, give_me_new_IDs(1)[0])
        TTLString += "<%s> <%s> <%s> . " % (curveNode,
                                            RevitAPI + "hasExactStartLoc", ListNode7)

        TTLString += "<%s> <%s> <%s> . " % (
            ListNode7, rdf + "type", oop + "List")
        TTLString += "<%s> <%s> (%s %s %s) . " % (ListNode7, oop + "hasListContent",
                                                  curve["hasExactStartLoc"][0], curve["hasExactStartLoc"][1], curve["hasExactStartLoc"][2])

        if "hasRadius" in curve:
            TTLString += "<%s> <%s> '%s' . " % (curveNode, RevitAPI +
                                                "hasRadius", curve["hasRadius"])
    return TTLString


def addRevitWindowInst(TTLString, revitInst, oneRevitFam, ProjectNode):
    InstanceNode = "%s%s" % (BIM, give_me_new_IDs(1)[0])
    FamilyNode = oneRevitFam.FamilyNode

    TTLString += "<%s> <%s> <%s> . " % (ProjectNode, bot +
                                        "hasElement", InstanceNode)
    TTLString += "<%s> <%s> <%s> . " % (InstanceNode,
                                        RevitAPI + "hasRevitType", FamilyNode)
    TTLString += "<%s> <%s> <%s> . " % (
        InstanceNode, rdf + "type", bot + "Element")
    return TTLString


def addRevitDoorInst(TTLString, revitInst, oneRevitFam, ProjectNode):
    InstanceNode = "%s%s" % (BIM, give_me_new_IDs(1)[0])
    FamilyNode = oneRevitFam.FamilyNode

    TTLString += "<%s> <%s> <%s> . " % (ProjectNode, bot +
                                        "hasElement", InstanceNode)
    TTLString += "<%s> <%s> <%s> . " % (InstanceNode,
                                        RevitAPI + "hasRevitType", FamilyNode)
    TTLString += "<%s> <%s> <%s> . " % (
        InstanceNode, rdf + "type", bot + "Element")
    return TTLString


def addRevitStructFoundationInst(TTLString, revitInst, oneRevitFam, ProjectNode):
    InstanceNode = "%s%s" % (BIM, give_me_new_IDs(1)[0])
    FamilyNode = oneRevitFam.FamilyNode

    TTLString += "<%s> <%s> <%s> . " % (ProjectNode, bot +
                                        "hasElement", InstanceNode)
    TTLString += "<%s> <%s> <%s> . " % (InstanceNode,
                                        RevitAPI + "hasRevitType", FamilyNode)
    TTLString += "<%s> <%s> <%s> . " % (InstanceNode,
                                        rdf + "type", bot + "Element")
    TTLString += "<%s> <%s> '%s' . " % (FamilyNode,
                                        RevitAPI + "fromBuiltInCategory", revitInst["fromBuiltInCategory"])

    geomParamNode = "%s%s" % (BIM, give_me_new_IDs(1)[0])
    TTLString += "<%s> <%s> <%s> . " % (InstanceNode,
                                        RevitAPI + "hasFurtherGeomParams", geomParamNode)

    if len(revitInst["hasFurtherGeomParams"]["hasPolyline"]) == 1:
        for pointList in revitInst["hasFurtherGeomParams"]["hasPolyline"][0][0]:
            ListNode8 = "%s%s" % (oop, give_me_new_IDs(1)[0])
            TTLString += "<%s> <%s> <%s> . " % (geomParamNode,
                                                RevitAPI + "hasPolyline", ListNode8)
            TTLString += "<%s> <%s> <%s> . " % (
                ListNode8, rdf + "type", oop + "List")
            TTLString += "<%s> <%s> (%s %s %s) . " % (ListNode8, oop + "hasListContent",
                                                      pointList[0], pointList[1], pointList[2])

    return TTLString


def addRevitFloorInst(TTLString, revitInst, oneRevitFam, ProjectNode):
    InstanceNode = "%s%s" % (BIM, give_me_new_IDs(1)[0])
    FamilyNode = oneRevitFam.FamilyNode

    TTLString += "<%s> <%s> <%s> . " % (ProjectNode, bot +
                                        "hasElement", InstanceNode)
    TTLString += "<%s> <%s> <%s> . " % (InstanceNode,
                                        RevitAPI + "hasRevitType", FamilyNode)
    TTLString += "<%s> <%s> <%s> . " % (InstanceNode,
                                        rdf + "type", bot + "Element")
    TTLString += "<%s> <%s> '%s' . " % (FamilyNode,
                                        RevitAPI + "fromBuiltInCategory", revitInst["fromBuiltInCategory"])

    geomParamNode = "%s%s" % (BIM, give_me_new_IDs(1)[0])

    TTLString += "<%s> <%s> <%s> . " % (InstanceNode,
                                        RevitAPI + "hasFurtherGeomParams", geomParamNode)

    if len(revitInst["hasFurtherGeomParams"]["hasPolyline"]) == 1:
        ListNode10 = "<%s%s>" % (oop, give_me_new_IDs(1)[0])
        TTLString += "<%s> <%s> %s . " % (geomParamNode,
                                          RevitAPI + "hasPolyline", ListNode10)
        TTLString += "%s <%s> <%s> . " % (
            ListNode10, rdf + "type", oop + "List")

        ListString = "("
        for onePoint in revitInst["hasFurtherGeomParams"]["hasPolyline"][0]:
            ListNode2 = "<%s%s>" % (oop, give_me_new_IDs(1)[0])
            TTLString += "%s <%s> <%s> . " % (
                ListNode2, rdf + "type", oop + "List")
            TTLString += "%s <%s> (%s %s %s) . " % (ListNode2, oop + "hasListContent",
                                                    onePoint[0], onePoint[1], onePoint[2])
            ListString += ListNode2
            ListString += " "

        ListString = ListString[:-1]
        ListString += ")"
        TTLString += "%s <%s> %s . " % (
            ListNode10, oop + "hasListContent", ListString)

    elif len(revitInst["hasFurtherGeomParams"]["hasPolyline"]) > 1:

        ListNode10 = "<%s%s>" % (oop, give_me_new_IDs(1)[0])
        TTLString += "<%s> <%s> %s . " % (geomParamNode,
                                          RevitAPI + "hasPolyline", ListNode10)
        TTLString += "%s <%s> <%s> . " % (
            ListNode10, rdf + "type", oop + "List")
        firstListString = "("
        for onePolyLine in revitInst["hasFurtherGeomParams"]["hasPolyline"]:
            ListNode1 = "<%s%s>" % (oop, give_me_new_IDs(1)[0])
            TTLString += "%s <%s> <%s> . " % (
                ListNode1, rdf + "type", oop + "List")
            firstListString += ListNode1
            firstListString += " "

            ListString = "("
            for onePoint in onePolyLine:
                ListNode2 = "<%s%s>" % (oop, give_me_new_IDs(1)[0])
                TTLString += "%s <%s> <%s> . " % (
                    ListNode2, rdf + "type", oop + "List")
                TTLString += "%s <%s> (%s %s %s) . " % (ListNode2, oop + "hasListContent",
                                                        onePoint[0], onePoint[1], onePoint[2])
                ListString += ListNode2
                ListString += " "

            ListString = ListString[:-1]
            ListString += ")"
            TTLString += "%s <%s> %s . " % (
                ListNode1, oop + "hasListContent", ListString)

        firstListString = firstListString[:-1]
        firstListString += ")"
        TTLString += "%s <%s> %s . " % (ListNode10,
                                        oop + "hasListContent", firstListString)
    return TTLString


def addRevitWallInst(TTLString, revitInst, oneRevitFam, ProjectNode):
    InstanceNode = "%s%s" % (BIM, give_me_new_IDs(1)[0])
    FamilyNode = oneRevitFam.FamilyNode

    TTLString += "<%s> <%s> <%s> . " % (ProjectNode, bot +
                                        "hasElement", InstanceNode)

    TTLString += "<%s> <%s> <%s> . " % (InstanceNode,
                                        RevitAPI + "hasRevitType", FamilyNode)
    TTLString += "<%s> <%s> <%s> . " % (InstanceNode,
                                        rdf + "type", bot + "Element")
    TTLString += "<%s> <%s> '%s' . " % (FamilyNode,
                                        RevitAPI + "fromBuiltInCategory", revitInst["fromBuiltInCategory"])

    geomParamNode = "%s%s" % (BIM, give_me_new_IDs(1)[0])

    TTLString += "<%s> <%s> <%s> . " % (InstanceNode,
                                        RevitAPI + "hasFurtherGeomParams", geomParamNode)

    TTLString += "<%s> <%s> '%s' . " % (geomParamNode,
                                        RevitAPI + "isBasedOn", revitInst["hasFurtherGeomParams"]["isType"])

    ListNode1 = "%s%s" % (oop, give_me_new_IDs(1)[0])

    TTLString += "<%s> <%s> <%s> . " % (geomParamNode,
                                        RevitAPI + "hasExactStartLoc", ListNode1)
    TTLString += "<%s> <%s> <%s> . " % (ListNode1,
                                        rdf + "type", oop + "List")
    TTLString += "<%s> <%s> (%s %s %s) . " % (ListNode1,
                                              oop + "hasListContent", revitInst["hasFurtherGeomParams"]["hasExactStartLoc"][0], revitInst["hasFurtherGeomParams"]["hasExactStartLoc"][1], revitInst["hasFurtherGeomParams"]["hasExactStartLoc"][2])

    ListNode2 = "%s%s" % (oop, give_me_new_IDs(1)[0])

    TTLString += "<%s> <%s> <%s> . " % (geomParamNode,
                                        RevitAPI + "hasExactEndLoc", ListNode2)
    TTLString += "<%s> <%s> <%s> . " % (ListNode2,
                                        rdf + "type", oop + "List")
    TTLString += "<%s> <%s> (%s %s %s) . " % (ListNode2,
                                              oop + "hasListContent", revitInst["hasFurtherGeomParams"]["hasExactEndLoc"][0], revitInst["hasFurtherGeomParams"]["hasExactEndLoc"][1], revitInst["hasFurtherGeomParams"]["hasExactEndLoc"][2])
    if "hasCutOuts" in revitInst["hasFurtherGeomParams"]:
        if revitInst["hasFurtherGeomParams"]["hasCutOuts"]:
            for CutInst in revitInst["hasFurtherGeomParams"]["hasCutOuts"]:
                instance = RevitFamily.get(CutInst["isFamInst"])
                if len(instance) == 1:
                    CutFamNode = instance[0].FamilyNode
                    cutOutNode = "%s%s" % (BIM, give_me_new_IDs(1)[0])
                    TTLString += "<%s> <%s> <%s> . " % (geomParamNode,
                                                        RevitAPI + "hasCutOuts", cutOutNode)
                    TTLString += "<%s> <%s> <%s> . " % (cutOutNode,
                                                        BIM + "isFamInst", CutFamNode)
                    TTLString += "<%s> <%s> '%s' . " % (CutFamNode,
                                                        RevitAPI + "fromBuiltInCategory", instance[0].builtInCategory)
                    ListNode3 = "%s%s" % (oop, give_me_new_IDs(1)[0])
                    TTLString += "<%s> <%s> <%s> . " % (cutOutNode,
                                                        RevitAPI + "hasExactLoc", ListNode3)
                    TTLString += "<%s> <%s> <%s> . " % (ListNode3,
                                                        rdf + "type", oop + "List")
                    TTLString += "<%s> <%s> (%s %s %s) . " % (ListNode3,
                                                              oop + "hasListContent", CutInst["hasExactLoc"][0], CutInst["hasExactLoc"][1], CutInst["hasExactLoc"][2])
                    TTLString += "<%s> <%s> <%s> . " % (
                        cutOutNode, RevitAPI + "hasRevitType", instance[0].FamilyNode)

                    ListNode4 = "%s%s" % (oop, give_me_new_IDs(1)[0])
                    TTLString += "<%s> <%s> <%s> . " % (cutOutNode,
                                                        RevitAPI + "hasFacingOr", ListNode4)
                    TTLString += "<%s> <%s> <%s> . " % (ListNode4,
                                                        rdf + "type", oop + "List")
                    TTLString += "<%s> <%s> (%s %s %s) . " % (ListNode4,
                                                              oop + "hasListContent", CutInst["hasFacingOr"][0], CutInst["hasFacingOr"][1], CutInst["hasFacingOr"][2])

                    ListNode5 = "%s%s" % (oop, give_me_new_IDs(1)[0])
                    TTLString += "<%s> <%s> <%s> . " % (cutOutNode,
                                                        RevitAPI + "hasHandOr", ListNode5)
                    TTLString += "<%s> <%s> <%s> . " % (ListNode5,
                                                        rdf + "type", oop + "List")
                    TTLString += "<%s> <%s> (%s %s %s) . " % (ListNode5,
                                                              oop + "hasListContent", CutInst["hasHandOr"][0], CutInst["hasHandOr"][1], CutInst["hasHandOr"][2])

                else:
                    print("Something went wrong while Family-mapping")

    for key in revitInst["hasParameterSet"]:
        blNode = "_:%s" % give_me_new_IDs(1)[0]
        TTLString += "<%s> <%s> %s . " % (InstanceNode,
                                          RevitAPI + "hasParameter", blNode)
        TTLString += "%s <%s> '%s' . " % (blNode,
                                          RevitAPI + "hasName", key)
        TTLString += "%s <%s> '%s' . " % (
            blNode, RevitAPI + "hasValue", revitInst["hasParameterSet"][key])

    return TTLString


def createTTLString(res, projectID):

    TTLString = "INSERT DATA { GRAPH <http://%s> {" % projectID

    ProjectNode = "%s%s" % (BIM, give_me_new_IDs(1)[0])
    ProjectID = res["data"]["ProjectID"]

    TTLString += "<%s> <%s> '%s' . " % (ProjectNode,
                                        RevitAPI+"hasName", ProjectID)
    TTLString += "<%s> <%s> <%s> . " % (ProjectNode,
                                        RevitAPI+"ProjectType", bot+"Building")

    for revitFam in res["data"]["BuiltInCategories"]:
        for revitTypes in revitFam:
            oneRevitFam = RevitFamily(
                revitTypes["fromBuiltInCategory"], revitTypes["hasRevitID"], revitTypes["hasParameterSet"])
            TTLString = oneRevitFam.addFamTTLString(TTLString)

        for revitTypes in revitFam:
            for revitInst in revitTypes["hasInstances"]:
                if revitInst["fromBuiltInCategory"] == "OST_Walls":
                    TTLString = addRevitWallInst(
                        TTLString, revitInst, oneRevitFam, ProjectNode)

                if revitInst["fromBuiltInCategory"] == "OST_StructuralColumns":
                    TTLString = addRevitColInst(
                        TTLString, revitInst, oneRevitFam, ProjectNode)

                if revitInst["fromBuiltInCategory"] == "OST_Floors":
                    TTLString = addRevitFloorInst(
                        TTLString, revitInst, oneRevitFam, ProjectNode)

                if revitInst["fromBuiltInCategory"] == "OST_Windows":
                    TTLString = addRevitWindowInst(
                        TTLString, revitInst, oneRevitFam, ProjectNode)

                if revitInst["fromBuiltInCategory"] == "OST_Doors":
                    TTLString = addRevitDoorInst(
                        TTLString, revitInst, oneRevitFam, ProjectNode)

                if revitInst["fromBuiltInCategory"] == "OST_StructuralFoundation":
                    TTLString = addRevitStructFoundationInst(
                        TTLString, revitInst, oneRevitFam, ProjectNode)

    TTLString += "} }"
    RevitFamily.instances = []
    return TTLString
