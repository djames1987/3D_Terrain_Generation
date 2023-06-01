from panda3d.core import Point3, Geom, GeomVertexFormat, GeomVertexData
from panda3d.core import GeomTriangles, GeomVertexWriter, GeomNode
from direct.showbase.ShowBase import ShowBase
from scipy.spatial import Delaunay
import numpy as np
import random


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Set up the geometry
        format = GeomVertexFormat.get_v3n3c4()
        vdata = GeomVertexData('vertices', format, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        color = GeomVertexWriter(vdata, 'color')

        # Set up a grid of points
        grid_size = 50
        grid_points = []

        for x in range(grid_size):
            for y in range(grid_size):
                z = random.uniform(0, 1)  # Random height
                vertex.addData3(x, y, z)
                normal.addData3(0, 0, 1)
                color.addData4(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), 1)
                grid_points.append([x, y])

        # Perform Delaunay triangulation
        tri = Delaunay(grid_points)
        triangles = tri.simplices

        # Set up the geometry
        geom = Geom(vdata)
        tris = GeomTriangles(Geom.UHStatic)

        for triangle in triangles:
            tris.addVertices(triangle[0], triangle[1], triangle[2])
            tris.closePrimitive()

        geom.addPrimitive(tris)

        # Create the node and attach it to the scene
        node = GeomNode('gnode')
        node.addGeom(geom)
        node_path = self.render.attachNewNode(node)
        node_path.setTwoSided(True)  # Makes the terrain visible from below
        node_path.setRenderModeWireframe()


app = MyApp()
app.run()
