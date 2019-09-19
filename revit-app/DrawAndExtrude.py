from ttl_helpers_copy import *


def x2DDrawAndExtrude(newGraph, project1, x2DDrawing, leng):

    statLen = len(x2DDrawing)
    IDListMain = give_me_new_IDs(statLen + 5)

    newArr = []
    for k in range(len(x2DDrawing)):
        newArr.append(["Add", project1[IDListMain[k + 2]]])
    newArr.append("Close")
    newArr.append("Wire")

    createTTLofClass(
        newGraph,
        project1,
        project1[IDListMain[1]],
        "BRepBuilderAPI_MakePolygon",
        [],
        newArr,
    )

    for k in range(len(x2DDrawing)):
        createTTLofClass(
            newGraph,
            project1,
            project1[IDListMain[k + 2]],
            "gp_Pnt",
            [
                Literal(x2DDrawing[k + 0][0], datatype=XSD.float),
                Literal(x2DDrawing[k + 0][1], datatype=XSD.float),
                Literal(x2DDrawing[k + 0][2], datatype=XSD.float),
            ],
            [],
        )

    createTTLofClass(
        newGraph,
        project1,
        project1[IDListMain[statLen + 2]],
        "BRepBuilderAPI_MakeFace",
        [project1[IDListMain[1]]],
        "Face",
    )

    createTTLofClass(
        newGraph,
        project1,
        project1[IDListMain[statLen + 3]],
        "gp_Vec",
        [
            Literal(0, datatype=XSD.float),
            Literal(0, datatype=XSD.float),
            Literal(leng, datatype=XSD.float),
        ],
        [],
    )
    createTTLofClass(
        newGraph,
        project1,
        project1[IDListMain[statLen + 4]],
        "BRepPrimAPI_MakePrism",
        [project1[IDListMain[statLen + 2]], project1[IDListMain[statLen + 3]]],
        "Shape",
    )

    return newGraph, project1[IDListMain[statLen + 4]]

