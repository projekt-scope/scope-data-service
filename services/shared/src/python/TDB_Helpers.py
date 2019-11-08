import random

myCharset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

BIM = "https://projekt-scope.de/ontologies/BIM#"
RevitAPI = "https://projekt-scope.de/software/RevitAPI#"
rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
bot = "https://w3id.org/bot#"
oop = "https://projekt-scope.de/ontologies/oop#"
occ = "https://projekt-scope.de/ontologies/occ#"
omg = "https://w3id.org/omg#"


def give_me_new_IDs(RangeIDs):
    IDList = []
    for _ in range(RangeIDs):
        IDList.append("_%s" %
                      "".join(random.choice(myCharset) for _ in range(8)))
    return IDList


def sparqlInsertClass(SparqlString, NSUriref, ITEMuriref, classname, cparams,
                      methodsMparams):
    funcID = give_me_new_IDs(1)
    SparqlString += "<%s> <%s> <%s> . " % (ITEMuriref, omg +
                                           "hasComplexGeometryDescription",
                                           NSUriref + funcID[0])

    SparqlString += "<%s> <%s> <%s> . " % (NSUriref + funcID[0], rdf + "type",
                                           occ + classname)
    if len(cparams) == 1:
        SparqlString += "<%s> <%s> <%s> . " % (NSUriref + funcID[0], oop +
                                               "hasParameter", cparams[0])

    elif len(cparams) > 1:
        ListNode = "%s%s" % (BIM, give_me_new_IDs(1)[0])
        SparqlString += "<%s> <%s> <%s> . " % (NSUriref + funcID[0],
                                               oop + "hasParameter", ListNode)

        SparqlString += "<%s> <%s> <%s> . " % (ListNode, rdf + "type",
                                               oop + "List")

        ListString = ""
        for elem in cparams:
            if not isinstance(elem, float):
                if not isinstance(elem, int):
                    if elem[0:4] == "http":
                        elem = "<" + elem + ">"
            ListString += str(elem)
            ListString += " "
        ListString = ListString[:-1]
        SparqlString += "<%s> <%s> (%s) . " % (ListNode, oop +
                                               "hasListContent", ListString)
    if isinstance(methodsMparams, str):
        methodsID = give_me_new_IDs(1)
        SparqlString += "<%s> <%s> <%s> . " % (
            NSUriref + funcID[0], oop + "hasMethod", NSUriref + methodsID[0])
        SparqlString += "<%s> <%s> <%s> . " % (NSUriref + methodsID[0], rdf +
                                               "type", occ + methodsMparams)

    elif isinstance(methodsMparams, list):
        if len(methodsMparams) > 1:

            methodsID = give_me_new_IDs(len(methodsMparams) + 1)
            methodList = []
            for method in range(len(methodsMparams)):
                methodList.append(NSUriref + methodsID[method + 1])
            ListNode1 = "%s%s" % (oop, give_me_new_IDs(1)[0])
            SparqlString += "<%s> <%s> <%s> . " % (NSUriref + funcID[0], oop +
                                                   "hasMethod", ListNode1)
            SparqlString += "<%s> <%s> <%s> . " % (ListNode1, rdf + "type",
                                                   oop + "List")
            ListString1 = ""
            for elem in methodList:
                if elem[0:4] == "http":
                    elem = "<" + elem + ">"
                ListString1 += elem
                ListString1 += " "
            ListString1 = ListString1[:-1]
            SparqlString += "<%s> <%s> (%s) . " % (
                ListNode1, oop + "hasListContent", ListString1)

            i = 0

            if isinstance(methodsMparams[i][1], list):

                for entry in methodList:
                    SparqlString += "<%s> <%s> <%s> . " % (
                        entry, rdf + "type", occ + methodsMparams[i][0][0])

                    ListNode2 = "%s%s" % (oop, give_me_new_IDs(1)[0])
                    SparqlString += "<%s> <%s> <%s> . " % (
                        entry, oop + "hasParameter", ListNode2)
                    SparqlString += "<%s> <%s> <%s> . " % (
                        ListNode2, rdf + "type", oop + "List")

                    ListString2 = ""
                    for elem in methodsMparams[i][1]:
                        if elem[0:4] == "http":
                            elem = "<" + elem + ">"
                        ListString2 += elem
                        ListString2 += " "
                    ListString2 = ListString2[:-1]
                    SparqlString += "<%s> <%s> (%s) . " % (
                        ListNode2, oop + "hasListContent", ListString2)
                    i = i + 1

            else:
                for entry in methodList:
                    if isinstance(methodsMparams[i], list):
                        SparqlString += "<%s> <%s> <%s> . " % (
                            entry, rdf + "type", occ + methodsMparams[i][0])
                        SparqlString += "<%s> <%s> <%s> . " % (
                            entry, oop + "hasParameter", methodsMparams[i][1])
                    else:
                        SparqlString += "<%s> <%s> <%s> . " % (
                            entry, rdf + "type", occ + methodsMparams[i])
                    i = i + 1

        elif len(methodsMparams) == 1:

            methodsID = give_me_new_IDs(len(methodsMparams))
            SparqlString += "<%s> <%s> <%s> . " % (NSUriref + funcID[0],
                                                   oop + "hasMethod",
                                                   NSUriref + methodsID[0])
            SparqlString += "<%s> <%s> <%s> . " % (NSUriref + methodsID[0],
                                                   rdf + "type", occ +
                                                   methodsMparams[0][0][0])
            if len(methodsMparams[0][1]) == 1:
                SparqlString += "<%s> <%s> <%s> . " % (NSUriref + methodsID[0],
                                                       oop + "hasParameter",
                                                       methodsMparams[0][1][0])
            elif len(methodsMparams[0][1]) > 1:
                ListNode3 = "%s%s" % (oop, give_me_new_IDs(1)[0])
                SparqlString += "<%s> <%s> <%s> . " % (
                    NSUriref + methodsID[0], oop + "hasParameter", ListNode3)
                SparqlString += "<%s> <%s> <%s> . " % (ListNode3, rdf + "type",
                                                       oop + "List")

                ListString3 = ""
                for elem in methodsMparams[0][1]:
                    if elem[0:4] == "http":
                        elem = "<" + elem + ">"
                    ListString3 += elem
                    ListString3 += " "
                ListString3 = ListString3[:-1]
                SparqlString += "<%s> <%s> (%s) . " % (
                    ListNode3, oop + "hasListContent", ListString3)
    return SparqlString


def move_a_Shape(SparqlString,
                 inst,
                 Raffstore1,
                 ElementToMove,
                 dx,
                 dy,
                 dz,
                 hasStartPoint=False):

    if hasStartPoint != False:
        IDListSep = give_me_new_IDs(3)
        ElementToMove = "<" + ElementToMove + ">"
        insert = "<" + Raffstore1 + IDListSep[1] + ">"
        SparqlString = sparqlInsertClass(
            SparqlString,
            Raffstore1,
            hasStartPoint,
            "BRepBuilderAPI_Transform",
            [ElementToMove, insert],
            "Shape",
        )

        SparqlString = sparqlInsertClass(
            SparqlString,
            Raffstore1,
            Raffstore1 + IDListSep[1],
            "gp_Trsf",
            [],
            [[["SetTranslation"], [Raffstore1 + IDListSep[2]]]],
        )
        SparqlString = sparqlInsertClass(
            SparqlString,
            Raffstore1,
            Raffstore1 + IDListSep[2],
            "gp_Vec",
            [dx, dy, dz],
            [],
        )

        return SparqlString, Raffstore1 + IDListSep[0]
    else:
        IDListSep = give_me_new_IDs(3)

        ElementToMove = "<" + ElementToMove + ">"
        insert = "<" + Raffstore1 + IDListSep[1] + ">"

        SparqlString = sparqlInsertClass(
            SparqlString,
            Raffstore1,
            Raffstore1 + IDListSep[0],
            "BRepBuilderAPI_Transform",
            [ElementToMove, insert],
            "Shape",
        )
        SparqlString = sparqlInsertClass(
            SparqlString,
            Raffstore1,
            Raffstore1 + IDListSep[1],
            "gp_Trsf",
            [],
            [[["SetTranslation"], [Raffstore1 + IDListSep[2]]]],
        )

        SparqlString = sparqlInsertClass(
            SparqlString,
            Raffstore1,
            Raffstore1 + IDListSep[2],
            "gp_Vec",
            [dx, dy, dz],
            [],
        )
        return SparqlString, Raffstore1 + IDListSep[0]


def rotate_a_Shape(SparqlString, Raffstore1, ElementToRotate, Axis, AngleInRad):
    # rotate a shape is not the new version !!! Have to update this
    IDListSep = give_me_new_IDs(4)
    SparqlString = sparqlInsertClass(
        SparqlString,
        Raffstore1,
        Raffstore1 + IDListSep[0],
        "BRepBuilderAPI_Transform",
        [ElementToRotate, Raffstore1 + IDListSep[1]],
        "Shape",
    )
    SparqlString = sparqlInsertClass(
        SparqlString,
        Raffstore1,
        Raffstore1 + IDListSep[1],
        "gp_Trsf",
        [],
        [[["SetRotation"], [Raffstore1 + IDListSep[2], AngleInRad]]],
    )
    SparqlString = sparqlInsertClass(SparqlString, Raffstore1,
                                     Raffstore1 + IDListSep[2], Axis, [], [])

    rotatedShape = Raffstore1 + IDListSep[0]
    return rotatedShape


def cutA_fromB(SparqlString, Raffstore1, firstElement, SecondElement):
    IDListSep = give_me_new_IDs(2)
    SparqlString = sparqlInsertClass(
        SparqlString,
        Raffstore1,
        Raffstore1 + IDListSep[0],
        "BRepAlgoAPI_Cut",
        [firstElement, SecondElement],
        "Shape",
    )
    return SparqlString, Raffstore1 + IDListSep[0]
