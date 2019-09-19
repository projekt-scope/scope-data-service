# this file contains the import functions
# from threejs rendering to genreate jsons
import os
import uuid
import sys

from OCC.Core.Visualization import Tesselator

# from OCC.Extend.TopologyUtils import is_edge, is_wire, discretize_edge, discretize_wire


def generate_json_from_shape(
    shape,
    uri,
    export_edges=False,
    color=(0.65, 0.65, 0.65),
    specular_color=(1, 1, 1),
    shininess=0.9,
    transparency=0.0,
    line_color=(0, 0.0, 0.0),
    line_width=2.0,
    mesh_quality=1.0,
    filename="test",
):
    # if the shape is an edge or a wire, use the related functions
    # if is_edge(shape):
    #     print("discretize an edge")
    #     pnts = discretize_edge(shape)
    #     edge_hash = "edg%s" % uuid.uuid4().hex
    #     str_to_write = export_edgedata_to_json(edge_hash, pnts)
    #     edge_full_path = os.path.join(self._path, edge_hash + ".json")
    #     with open(edge_full_path, "w") as edge_file:
    #         edge_file.write(str_to_write)

    #     # store this edge hash
    #     self._3js_edges[edge_hash] = [color, line_width]
    #     return True
    # elif is_wire(shape):
    #     print("discretize a wire")
    #     pnts = discretize_wire(shape)
    #     wire_hash = "wir%s" % uuid.uuid4().hex
    #     str_to_write = export_edgedata_to_json(wire_hash, pnts)
    #     wire_full_path = os.path.join(self._path, wire_hash + ".json")
    #     print(wire_full_path)
    #     with open(wire_full_path, "w") as wire_file:
    #         wire_file.write(str_to_write)

    #     # store this edge hash
    #     self._3js_edges[wire_hash] = [color, line_width]
    #     return True

    # TODO change uuid here
    # shape_uuid = uuid.uuid4().hex
    shape_uuid = uri
    # shape_hash = "shp%s" % shape_uuid
    shape_hash = "shp%s" % uuid.uuid4().hex
    # tesselate
    tess = Tesselator(shape)
    tess.Compute(
        compute_edges=export_edges,
        mesh_quality=mesh_quality,
        uv_coords=False,
        parallel=True,
    )

    sys.stdout.flush()
    # export to 3JS
    # shape_full_path = os.path.join(self._path, shape_hash + '.json')
    # print(f'{shape_full_path} shape path')
    dirpath = os.getcwd()
    staticpath = "src/app/render/static/shapes"
    shape_full_path = os.path.join(dirpath, staticpath, shape_hash + ".json")

    # generate the mesh
    # tess.ExportShapeToThreejs(shape_hash, shape_full_path)
    # and also to JSON
    with open(shape_full_path, "w") as json_file:
        json_file.write(tess.ExportShapeToThreejsJSONString(shape_uuid))
    # draw edges if necessary
    # if export_edges:
    #     # export each edge to a single json
    #     # get number of edges
    #     nbr_edges = tess.ObjGetEdgeCount()
    #     for i_edge in range(nbr_edges):
    #         # after that, the file can be appended
    #         str_to_write = ""
    #         edge_point_set = []
    #         nbr_vertices = tess.ObjEdgeGetVertexCount(i_edge)
    #         for i_vert in range(nbr_vertices):
    #             edge_point_set.append(tess.GetEdgeVertex(i_edge, i_vert))
    #         # write to file
    #         #edge_hash = "edg%s" % uuid.uuid4().hex
    #         # str_to_write += export_edgedata_to_json(edge_hash, edge_point_set)
    #         # create the file
    #         # edge_full_path = os.path.join(self._path, edge_hash + ".json")
    #         with open(edge_full_path, "w") as edge_file:
    #             edge_file.write(str_to_write)
    #         # store this edge hash, with black color
    #         # self._3js_edges[hash] = [(0, 0, 0), line_width]
    return shape_hash
