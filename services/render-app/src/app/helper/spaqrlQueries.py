from rdflib import Graph


def filterBlanknodes(g):
    filterBlanknodes = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                construct {
                ?s ?p ?o
                }

                where {

                ?s ?p ?o .
                    filter(?p!=rdf:first&&?p!=rdf:rest&&!isBlank(?o))
                }

    """
    qres = g.query(filterBlanknodes)
    return qres


def queryAllFromNode(uri, g):
    print(uri)
    queryAllNodes = """
            prefix x: <urn:ex:>

        construct {
        ?s ?p ?o
        }

        where {
        <%s> (x:|!x:)* ?s .
        ?s ?p ?o .
        }
        """ % (
        uri
    )

    qres = g.query(queryAllNodes)
    newg = Graph().parse(data=qres.serialize(format="xml"))
    newg = newg.serialize(format="n3")

    g = Graph()
    g.parse(data=newg, format="n3")
    # for subj, pred, obj in g:
    #     print(f"subj {subj}")
    #     print(f"pred {pred}")
    #     print(f"obj {obj}")

    return g


def getOrderedLists(g):
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?s ?item ?p
    WHERE {
        ?s ?p ?o . 
        ?o rdf:rest*/rdf:first ?item
        filter(?p!=rdf:first&&?p!=rdf:rest)

    }

    """
    qres = g.query(query)
    # print(qres)
    # for subj, pred, obj in qres:
    #     print(f"subj {subj}")
    #     print(f"pred {pred}")
    #     print(f"obj {obj}")

    return qres
