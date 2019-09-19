import sys

from OCC.Display.WebGl import x3dom_renderer


try:
    from app.recursiveQuery import geomQuery
except Exception as e:
    print(e)
    from recursiveQuery import geomQuery

# from multiprocessing import Pool
# from OCC.Core.Graphic3d import Graphic3d_NOM_SILVER, Graphic3d_MaterialAspect


from OCC.Display.SimpleGui import init_display


from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB


def exit(event=None):
    sys.exit()


def findObjects(g, qSt):
    qresStart = g.query(qSt)
    ResObjlist = []
    for row in qresStart:
        for col in row:
            ResObjlist.append(col)
    return ResObjlist


# find the whole geom description
# (createGeom in recursiveQuery.py does this recursively)
def createGeom(g, ResObj):
    try:
        oneObj = geomQuery(g, ResObj)
    except Exception as e:
        print(e)
        print("error in create Geom")
        oneObj = None
    return oneObj


def generate_objlist(g):

    qSt = """
        SELECT ?GeomEnt WHERE
        {
            ?x omg:hasGeometry ?GeomEnt .
        }
        """

    ResObjlist = findObjects(g, qSt)
    # print(ResObjlist)
    # try:

    objlist_justGeom = []

    for o in ResObjlist:
        objlist_justGeom.append(createGeom(g, o))

    # except:
    #    raise ValueError("At least one valid Object to render is required")

    objlist = []
    if len(objlist_justGeom) == len(ResObjlist):
        for i in range(len(ResObjlist)):
            objlist.append([objlist_justGeom[i], ResObjlist[i]])

    return objlist


def generate_objlist_no_accessory(g):

    qSt = """
        SELECT ?GeomEnt WHERE
        {
            ?x omg:hasGeometry ?GeomEnt .
        }
        """

    ResObjlist = findObjects(g, qSt)
    # try:

    objlist_justGeom = []
    ResObjlist2 = []

    for o in ResObjlist:
        if not check_if_obj_has_GeometryContext(g, o):
            objlist_justGeom.append(createGeom(g, o))
            ResObjlist2.append(o)

    # except:
    #    raise ValueError("At least one valid Object to render is required")

    objlist = []
    if len(objlist_justGeom) == len(ResObjlist2):
        for i in range(len(ResObjlist2)):
            objlist.append([objlist_justGeom[i], ResObjlist2[i]])

    return objlist


def check_if_obj_has_GeometryContext(g, obj, context="Accessory"):

    context = obj.split("#")[0] + "#" + context

    qGF = """
    SELECT ?CompGeomDesc ?CompGeomDescType WHERE
    {
        <%s> omg:hasComplexGeometryDescription ?CompGeomDesc .
        <%s> omg:hasGeometryContext <%s> .
        ?CompGeomDesc rdf:type ?CompGeomDescType
    }
    """ % (
        obj,
        obj,
        context,
    )

    qres_qGF = g.query(qGF)

    if len(qres_qGF) != 0:
        return True
    else:
        return False


def render_objlist(objlist, bboxlist=[]):

    my_renderer = x3dom_renderer.X3DomRenderer()

    for obj in objlist:
        my_renderer.DisplayShape(obj[0], color=(0.1, 0.2, 0.3), export_edges=True)
    if bboxlist:
        for bbox in bboxlist:
            my_renderer.DisplayShape(
                bbox,
                line_width=3.0,
                line_color=(1, 0.5, 0.3),
                export_edges=True,
                transparency=1,
            )
    my_renderer.render()
    return "Render started"


def render_shape(shape):
    my_renderer = x3dom_renderer.X3DomRenderer()
    my_renderer.DisplayShape(shape, color=(0.1, 0.2, 0.3), export_edges=True)
    my_renderer.render()


def rgb_color(r, g, b):
    return Quantity_Color(r, g, b, Quantity_TOC_RGB)


def display_objlist(objlist, bboxlist=[]):
    display, start_display, add_menu, add_function_to_menu = init_display()
    add_menu("Functions")
    if objlist:
        for obj in objlist:
            # ,color=(rgb_color(185/255, 15/255, 34/255)), update=True)
            display.DisplayShape(obj[0])
    if bboxlist:
        for obj in bboxlist:
            display.DisplayShape(obj, transparency=0.8, update=True)
    # display.Context.SetDisplayMode(AIS_WireFrame)
    display.SetSelectionModeVertex()
    display.FitAll()
    add_function_to_menu("Functions", exit)

    start_display()


def display_shape(shape):
    display, start_display, add_menu, add_function_to_menu = init_display()
    display.DisplayShape(shape, update=True)
    display.FitAll()
    start_display()

