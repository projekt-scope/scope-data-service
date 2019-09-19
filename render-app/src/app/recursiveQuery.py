import OCC
from OCC import Core
from OCC.Core.BRepPrimAPI import *
from OCC.Core.BRepAlgoAPI import *
import rdflib
from SPARQLWrapper import SPARQLWrapper, JSON

"""
recursive written script which tries to find all geometric information and 
gives back all occ classes including their parameters and methods. 
it is recursive because one has to start with the "last" node in the graph.
"""


def geomQuery(g, obj):

    qGF = (
        """
    SELECT ?CompGeomDesc ?CompGeomDescType WHERE
    {
        <%s> omg:hasComplexGeometryDescription ?CompGeomDesc . 
        ?CompGeomDesc rdf:type ?CompGeomDescType
    }
    """
        % obj
    )

    qres_qGF = g.query(qGF)

    if len(qres_qGF) != 0:
        # find OCC class and className

        occName = qres_qGF.bindings[0]["CompGeomDesc"]

        ResOCC_className = qres_qGF.bindings[0]["CompGeomDescType"]
        OCC_classname = ResOCC_className.split("#")[-1]
        OCC_module = OCC_classname.split("_")[0]

        occClass = getattr(getattr(OCC.Core, OCC_module), OCC_classname)

        # find class parameters (if any) and initialize class

        cparams = paramQuery(g, occName)
        objres = occClass(*cparams)

        # find methods incl. method parameters (if any)

        qCM = (
            """
        SELECT ?Method ?oneMethod WHERE
        {
            <%s> oop:hasMethod ?Method . 
            OPTIONAL { ?Method rdf:rest*/rdf:first ?oneMethod . } 
        }
        """
            % occName
        )

        qres_qCM = g.query(qCM)
        methods = []
        if len(qres_qCM) != 0:

            if len(qres_qCM.bindings) > 1:
                for entry in qres_qCM.bindings:
                    if isinstance(entry["oneMethod"], rdflib.term.URIRef):
                        methods.append(entry["oneMethod"])
                    else:
                        pass
            else:
                methods.append(qres_qCM.bindings[0]["Method"])
            for methodname in methods:

                qMN = (
                    """
                SELECT ?o WHERE
                {
                <%s> rdf:type ?o .
                }
                """
                    % methodname
                )
                qres_qMN = g.query(qMN)

                for row_qMN in qres_qMN:
                    for col_qMN in row_qMN:
                        methodtypestr = col_qMN.split("#")[-1]

                mparams = paramQuery(g, methodname)

                # initialize methods of occClass with mparams

                if methodtypestr in ["Shape", "Edge", "Curve", "Wire", "Face"]:
                    objres = getattr(objres, methodtypestr)(*mparams)

                else:
                    getattr(objres, methodtypestr)(*mparams)

        return objres


# find all parameters (doesn't matter if list or single)
def paramQuery(g, elementX):

    qP = (
        """
    SELECT ?o WHERE
    {
        <%s> oop:hasParameter ?o .
    }
    """
        % elementX
    )

    qres_qP = g.query(qP)

    params = []

    if len(qres_qP) != 0:

        for row_qP in qres_qP:
            for col_qP in row_qP:
                if isinstance(col_qP, rdflib.term.BNode):
                    qPL = (
                        """
                    SELECT ?item ?type WHERE
                    {
                        <%s> oop:hasParameter ?o .
                        ?o rdf:rest*/rdf:first ?item .
                        BIND(DATATYPE(?item) AS ?type)
                    }
                    """
                        % elementX
                    )

                    ############## TODO !!!!!! Error Handling if Datatypes are wrong or not given !!!!! ###############################

                    qres_qPL = g.query(qPL)
                    for row_qPL in qres_qPL:
                        if row_qPL[1] != None:
                            Datatype = row_qPL[1].split("#")[-1]

                        if isinstance(row_qPL[0], rdflib.term.URIRef):
                            paramname = row_qPL[0]
                            params.append(geomQuery(g, paramname))
                        elif Datatype == "integer":
                            try:
                                params.append(int(row_qPL[0]))
                            except:
                                raise ValueError(
                                    "can't convert given Integer to python Integer"
                                )
                                # or without err message just append the col
                                params.append(row_qPL[0])
                        elif Datatype == "double" or Datatype == "float":
                            try:
                                params.append(float(row_qPL[0]))
                            except:
                                raise ValueError(
                                    "can't convert given double to python float"
                                )
                                # or without err message just append the col
                                params.append(row_qPL[0])
                        else:
                            params.append(row_qPL[0])
                    params = params[1:]
                elif isinstance(col_qP, rdflib.term.URIRef):
                    params.append(geomQuery(g, col_qP))

                else:
                    params.append(col_qP)
    return params


#################################################################################################################
