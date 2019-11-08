import TDB_Helpers


def x2DDrawAndExtrude(SparqlString, project1, x2DDrawing, leng):

    statLen = len(x2DDrawing)
    IDListMain = TDB_Helpers.give_me_new_IDs(statLen + 5)

    newArr = []
    for k in range(len(x2DDrawing)):
        newArr.append(["Add", project1 + IDListMain[k + 2]])
    newArr.append("Close")
    newArr.append("Wire")
    SparqlString = TDB_Helpers.sparqlInsertClass(
        SparqlString,
        project1,
        project1 + IDListMain[1],
        "BRepBuilderAPI_MakePolygon",
        [],
        newArr,
    )
    for k in range(len(x2DDrawing)):
        SparqlString = TDB_Helpers.sparqlInsertClass(
            SparqlString,
            project1,
            project1 + IDListMain[k + 2],
            "gp_Pnt",
            [
                x2DDrawing[k + 0][0],
                x2DDrawing[k + 0][1],
                x2DDrawing[k + 0][2],
            ],
            [],
        )

    SparqlString = TDB_Helpers.sparqlInsertClass(
        SparqlString,
        project1,
        project1 + IDListMain[statLen + 2],
        "BRepBuilderAPI_MakeFace",
        [project1 + IDListMain[1]],
        "Face",
    )

    SparqlString = TDB_Helpers.sparqlInsertClass(
        SparqlString,
        project1,
        project1 + IDListMain[statLen + 3],
        "gp_Vec",
        [0, 0, leng],
        [],
    )
    SparqlString = TDB_Helpers.sparqlInsertClass(
        SparqlString,
        project1,
        project1 + IDListMain[statLen + 4],
        "BRepPrimAPI_MakePrism",
        [
            project1 + IDListMain[statLen + 2],
            project1 + IDListMain[statLen + 3]
        ],
        "Shape",
    )

    return SparqlString, project1 + IDListMain[statLen + 4]
