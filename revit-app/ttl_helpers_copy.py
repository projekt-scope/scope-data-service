from rdflib import Graph, Literal, Namespace, RDF, XSD
from rdflib.term import BNode, URIRef
import itertools
import random

myCharset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

oop = Namespace("https://projekt-scope.de/ontologies/oop#")
occ = Namespace("https://projekt-scope.de/ontologies/occ#")
omg = Namespace("https://w3id.org/omg#")


def add_iter(graph, s, p, o):

    if not isinstance(s, list):
        s = [s]
    if not isinstance(p, list):
        p = [p]
    if not isinstance(o, list):
        o = [o]

    result = list(itertools.product(*[s, p, o]))
    for i1 in result:
        graph.add((i1[0], i1[1], i1[2]))


def createList(graph, ListItems):
    """
    this function converts a "python" list to an ordered rdf-list
    """

    if not isinstance(ListItems, list) or ListItems == []:
        raise TypeError("ListItems must be of type list with at least one element")

    ListNode = oop[give_me_new_IDs(1)[0]]
    graph.add((ListNode, RDF.type, oop.List))
    ItemName = BNode()
    graph.add((ListNode, oop.hasListContent, ItemName))
    for i1 in range(len(ListItems) - 1):
        Item = ListItems[i1]
        NextItem = BNode()
        if type(Item) == URIRef:
            graph.add((ItemName, RDF.first, Item))
        else:
            graph.add((ItemName, RDF.first, Literal(Item)))
        graph.add((ItemName, RDF.rest, NextItem))
        ItemName = NextItem

    if type(ListItems[-1]) == URIRef:
        graph.add((NextItem, RDF.first, ListItems[-1]))
    else:
        graph.add((NextItem, RDF.first, Literal(ListItems[-1])))

    graph.add((NextItem, RDF.rest, RDF.nil))

    return ListNode


def give_me_new_IDs(RangeIDs):
    IDList = []
    for IDs in range(RangeIDs):
        IDList.append("_%s" % "".join(random.choice(myCharset) for _ in range(8)))
    return IDList


def createTTLofClass(g, NSUriref, ITEMuriref, classname, cparams, methodsMparams):
    funcID = give_me_new_IDs(1)
    g.add((ITEMuriref, omg.hasComplexGeometryDescription, NSUriref[funcID[0]]))
    g.add((NSUriref[funcID[0]], RDF.type, occ[classname]))

    if len(cparams) == 1:
        cparamsID = give_me_new_IDs(1)
        g.add((NSUriref[funcID[0]], oop.hasParameter, cparams[0]))
    elif len(cparams) > 1:
        cparamsID = createList(g, cparams)
        g.add((NSUriref[funcID[0]], oop.hasParameter, cparamsID))

    if isinstance(methodsMparams, str):
        methodsID = give_me_new_IDs(1)
        g.add((NSUriref[funcID[0]], oop.hasMethod, NSUriref[methodsID[0]]))
        g.add((NSUriref[methodsID[0]], RDF.type, occ[methodsMparams]))
    elif isinstance(methodsMparams, list):
        # print((methodsMparams))
        if len(methodsMparams) > 1:
            methodsID = give_me_new_IDs(len(methodsMparams) + 1)
            methodList = []
            for method in range(len(methodsMparams)):
                methodList.append(NSUriref[methodsID[method + 1]])
            methodsIDLN = createList(g, methodList)
            g.add((NSUriref[funcID[0]], oop.hasMethod, methodsIDLN))

            i = 0
            # print((methodsMparams[i][1]))

            if isinstance(methodsMparams[i][1], list):
                for entry in methodList:
                    g.add((entry, RDF.type, occ[methodsMparams[i][0][0]]))
                    mparamsID = createList(g, methodsMparams[i][1])
                    g.add((entry, oop.hasParameter, mparamsID))

                    i = i + 1
            else:
                for entry in methodList:
                    if isinstance(methodsMparams[i], list):
                        g.add((entry, RDF.type, occ[methodsMparams[i][0]]))
                        g.add((entry, oop.hasParameter, methodsMparams[i][1]))
                    else:
                        g.add((entry, RDF.type, occ[methodsMparams[i]]))
                        # g.add((entry, occ.hasParameter, methodsMparams[i][1]))

                    i = i + 1

        elif len(methodsMparams) == 1:
            methodsID = give_me_new_IDs(len(methodsMparams))
            g.add((NSUriref[funcID[0]], oop.hasMethod, NSUriref[methodsID[0]]))
            g.add((NSUriref[methodsID[0]], RDF.type, occ[methodsMparams[0][0][0]]))
            if len(methodsMparams[0][1]) == 1:
                g.add(
                    (NSUriref[methodsID[0]], oop.hasParameter, methodsMparams[0][1][0])
                )
            elif len(methodsMparams[0][1]) > 1:
                mparamsparamsID = createList(g, methodsMparams[0][1])
                g.add((NSUriref[methodsID[0]], oop.hasParameter, mparamsparamsID))


def move_a_Shape(g, Raffstore1, ElementToMove, dx, dy, dz, hasStartPoint=False):
    if hasStartPoint != False:
        IDListSep = give_me_new_IDs(3)
        createTTLofClass(
            g,
            Raffstore1,
            hasStartPoint,
            "BRepBuilderAPI_Transform",
            [ElementToMove, Raffstore1[IDListSep[1]]],
            "Shape",
        )
        createTTLofClass(
            g,
            Raffstore1,
            Raffstore1[IDListSep[1]],
            "gp_Trsf",
            [],
            [[["SetTranslation"], [Raffstore1[IDListSep[2]]]]],
        )
        createTTLofClass(
            g,
            Raffstore1,
            Raffstore1[IDListSep[2]],
            "gp_Vec",
            [Literal(dx), Literal(dy), Literal(dz)],
            [],
        )

        movedShape = Raffstore1[IDListSep[0]]
        return movedShape
    else:
        IDListSep = give_me_new_IDs(3)
        createTTLofClass(
            g,
            Raffstore1,
            Raffstore1[IDListSep[0]],
            "BRepBuilderAPI_Transform",
            [ElementToMove, Raffstore1[IDListSep[1]]],
            "Shape",
        )
        createTTLofClass(
            g,
            Raffstore1,
            Raffstore1[IDListSep[1]],
            "gp_Trsf",
            [],
            [[["SetTranslation"], [Raffstore1[IDListSep[2]]]]],
        )
        createTTLofClass(
            g,
            Raffstore1,
            Raffstore1[IDListSep[2]],
            "gp_Vec",
            [Literal(dx), Literal(dy), Literal(dz)],
            [],
        )

        movedShape = Raffstore1[IDListSep[0]]
        return movedShape


def rotate_a_Shape(g, Raffstore1, ElementToRotate, Axis, AngleInRad):

    IDListSep = give_me_new_IDs(4)
    createTTLofClass(
        g,
        Raffstore1,
        Raffstore1[IDListSep[0]],
        "BRepBuilderAPI_Transform",
        [ElementToRotate, Raffstore1[IDListSep[1]]],
        "Shape",
    )
    createTTLofClass(
        g,
        Raffstore1,
        Raffstore1[IDListSep[1]],
        "gp_Trsf",
        [],
        [[["SetRotation"], [Raffstore1[IDListSep[2]], Literal(AngleInRad)]]],
    )
    createTTLofClass(g, Raffstore1, Raffstore1[IDListSep[2]], Axis, [], [])

    rotatedShape = Raffstore1[IDListSep[0]]
    return rotatedShape


def cutA_fromB(g, Raffstore1, firstElement, SecondElement):
    IDListSep = give_me_new_IDs(2)
    createTTLofClass(
        g,
        Raffstore1,
        Raffstore1[IDListSep[0]],
        "BRepAlgoAPI_Cut",
        [firstElement, SecondElement],
        "Shape",
    )

    cutShape = Raffstore1[IDListSep[0]]
    return cutShape


def generate_box_with_gPnt(g, Object1, pointobject, boxobject, px, py, pz, x, y, z):

    createTTLofClass(
        g,
        Object1,
        pointobject,
        "gp_Pnt",
        [
            Literal(px, datatype=XSD.double),
            Literal(py, datatype=XSD.double),
            Literal(pz, datatype=XSD.double),
        ],
        [],
    )
    # box
    createTTLofClass(
        g,
        Object1,
        boxobject,
        "BRepPrimAPI_MakeBox",
        [
            pointobject,
            Literal(x, datatype=XSD.double),
            Literal(y, datatype=XSD.double),
            Literal(z, datatype=XSD.double),
        ],
        "Shape",
    )


def generate_sphere_with_gPnt(g, Object1, pointobject, sphereobject, px, py, pz, r):

    createTTLofClass(
        g,
        Object1,
        pointobject,
        "gp_Pnt",
        [
            Literal(px, datatype=XSD.double),
            Literal(py, datatype=XSD.double),
            Literal(pz, datatype=XSD.double),
        ],
        [],
    )
    # sphere
    createTTLofClass(
        g,
        Object1,
        sphereobject,
        "BRepPrimAPI_MakeSphere",
        [pointobject, Literal(r, datatype=XSD.double)],
        "Shape",
    )


def generate_cylinder_with_gPnt(
    g, Object1, pointobject, gpDirobject, axobject, cylinder, px, py, pz, dir, r, h
):

    createTTLofClass(
        g,
        Object1,
        pointobject,
        "gp_Pnt",
        [
            Literal(px, datatype=XSD.double),
            Literal(py, datatype=XSD.double),
            Literal(pz, datatype=XSD.double),
        ],
        [],
    )

    if dir == "x":
        createTTLofClass(
            g,
            Object1,
            gpDirobject,
            "gp_Dir",
            [
                Literal(1, datatype=XSD.double),
                Literal(0, datatype=XSD.double),
                Literal(0, datatype=XSD.double),
            ],
            [],
        )
    if dir == "y":
        createTTLofClass(
            g,
            Object1,
            gpDirobject,
            "gp_Dir",
            [
                Literal(0, datatype=XSD.double),
                Literal(1, datatype=XSD.double),
                Literal(0, datatype=XSD.double),
            ],
            [],
        )
    if dir == "z":
        createTTLofClass(
            g,
            Object1,
            gpDirobject,
            "gp_Dir",
            [
                Literal(0, datatype=XSD.double),
                Literal(0, datatype=XSD.double),
                Literal(1, datatype=XSD.double),
            ],
            [],
        )

    createTTLofClass(g, Object1, axobject, "gp_Ax2", [pointobject, gpDirobject], [])

    # cylinder
    createTTLofClass(
        g,
        Object1,
        cylinder,
        "BRepPrimAPI_MakeCylinder",
        [axobject, Literal(r, datatype=XSD.double), Literal(h, datatype=XSD.double)],
        "Shape",
    )

