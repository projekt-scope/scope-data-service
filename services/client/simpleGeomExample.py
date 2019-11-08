
from python import TDB_Helpers
import revit2occ
import sys
sys.path.append('revit-app')


# url = "http://10.200.29.203:22631"
url = "http://127.0.0.1:22631"

BIM = "https://projekt-scope.de/ontologies/BIM#"
omg = "https://w3id.org/omg#"

GraphID = "http://simpleGeomExample"

SparqlString = "INSERT DATA { GRAPH <%s> {" % GraphID

IDListMain = TDB_Helpers.give_me_new_IDs(5)

inst = "ToDeleteInMovedShape"

SparqlString = TDB_Helpers.sparqlInsertClass(
    SparqlString,
    BIM,
    BIM + IDListMain[0],
    "BRepPrimAPI_MakeCylinder",
    [
        4,
        7,
    ],
    "Shape",
)

movedShape = TDB_Helpers.move_a_Shape(SparqlString, inst, BIM,
                                      BIM + IDListMain[0], 1, 2, 2)
SparqlString = movedShape[0]

SparqlString = TDB_Helpers.sparqlInsertClass(
    SparqlString,
    BIM,
    BIM + IDListMain[1],
    "BRepPrimAPI_MakeBox",
    [8, 8, 6],
    "Shape",
)

cutShape = TDB_Helpers.cutA_fromB(SparqlString, BIM, BIM + IDListMain[1],
                                  movedShape[1])
SparqlString = cutShape[0]

SparqlString += "<%s> <%s> '%s' . " % ("http://irgendeinExample1.de",
                                       BIM + "isPartOfProject", "ProjectName")

SparqlString += "<%s> <%s> <%s> . " % ("http://irgendeinExample1.de",
                                       omg + "hasGeometry", cutShape[1])

SparqlString += "} }"
print(SparqlString)
print(url)
revit2occ.sendSparqlString(SparqlString, url)
