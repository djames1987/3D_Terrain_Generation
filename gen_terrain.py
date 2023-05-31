from panda3d.core import Geom, GeomNode, GeomTriangles, GeomVertexFormat, GeomVertexData, GeomVertexWriter, Point3
from panda3d.core import LPoint3f, LVector3f, loadPrcFile, BitMask32
from panda3d.physics import *
from terrain_matrix import *
from rust_noise import *
import os
from direct.showbase.ShowBase import ShowBase
from ralph_player import *
from panda3d.core import CollisionTraverser, CollisionHandlerQueue
from panda3d.core import CollisionNode, CollisionSphere, CollisionPolygon
from panda3d.core import BitMask32

loadPrcFile('settings.prc')


class MatrixUtil(ShowBase):
    def __init__(self, map_size=1024, max_height=128, octaves=5, persistence=0.5, lacunarity=0.9, amplitude=0.13, frequency=0.29, resolution_factor=8):
        ShowBase.__init__(self)
        self.enableParticles()


        self.map_size = map_size
        self.max_height = max_height
        self.octaves = octaves
        self.persistence = persistence
        self.lacunarity = lacunarity
        self.amplitude = amplitude
        self.frequency = frequency
        self.resolution_factor = resolution_factor

        self.matrix = self.get_matrix()
        self.render_terrain()
        self.player = Ralph(self, self.matrix)
        #self.render.setRenderModeWireframe(True)
        #self.camera.setPos(0, 10, 10)
        #self.camLens.setFov(80)

    def get_matrix(self, filename='matrix.npy'):
        if os.path.exists(f'map_data/{filename}'):
            print(f'loading: {filename}')
            return TerrainMatrix.load_matrix(filename=filename)
        else:
            print(f'Generating and saving: {filename}')
            self.generate_map_data()
            print(f'Loading: {filename}')
            return TerrainMatrix.load_matrix(filename=filename)

    def generate_map_data(self):
        gen = MapDataGenerator(self.map_size,
                               self.max_height,
                               self.octaves,
                               self.persistence,
                               self.lacunarity,
                               self.amplitude,
                               self.frequency)

        data = gen.generate_map_data()

        if os.path.exists('map_data/'):
            TerrainMatrix.save_matrix(data, filename='matrix.npy')
        else:
            os.mkdir('map_data/')
            TerrainMatrix.save_matrix(data, filename='matrix.npy')

    def render_terrain(self):
        # The effective map size at the chosen resolution
        effective_map_size = self.map_size // self.resolution_factor

        # Prepare the geometry data structures
        format = GeomVertexFormat.get_v3n3c4()
        vdata = GeomVertexData('vertices', format, Geom.UHStatic)
        vdata.setNumRows(effective_map_size * effective_map_size)

        # Create the geometry writers
        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        color = GeomVertexWriter(vdata, 'color')

        for z in range(self.max_height):
            for y in range(effective_map_size):
                for x in range(effective_map_size):
                    # Sample the height from the original data
                    h = TerrainMatrix.search_matrix((z, y*self.resolution_factor, x*self.resolution_factor), self.matrix)

                    vertex.addData3f(Point3(x*self.resolution_factor, y*self.resolution_factor, h))
                    normal.addData3f(LVector3f(0, 0, 1))
                    color.addData4f(0, h / self.max_height, 0, 1)

        # Create the triangles
        tris = GeomTriangles(Geom.UHStatic)

        for y in range(effective_map_size - 1):
            for x in range(effective_map_size - 1):
                i1 = y * effective_map_size + x
                i2 = y * effective_map_size + (x + 1)
                i3 = (y + 1) * effective_map_size + x
                i4 = (y + 1) * effective_map_size + (x + 1)
                tris.addVertices(i1, i2, i3)
                tris.addVertices(i2, i4, i3)
                tris.closePrimitive()

        # Assemble the geometry
        geom = Geom(vdata)
        geom.addPrimitive(tris)
        # Create a collision node
        coll_node = CollisionNode('terrainCollNode')
        coll_node.setIntoCollideMask(BitMask32.bit(1))  # Replace with the appropriate collision mask

        # Add the collision polygons (triangles) to the collision node
        for y in range(effective_map_size - 1):
            for x in range(effective_map_size - 1):
                i1 = y * effective_map_size + x
                i2 = y * effective_map_size + (x + 1)
                i3 = (y + 1) * effective_map_size + x
                i4 = (y + 1) * effective_map_size + (x + 1)

                vertex1 = Point3(x * self.resolution_factor, y * self.resolution_factor, TerrainMatrix.search_matrix(
                    (z, y * self.resolution_factor, x * self.resolution_factor), self.matrix))
                vertex2 = Point3((x + 1) * self.resolution_factor, y * self.resolution_factor,
                                 TerrainMatrix.search_matrix(
                                     (z, y * self.resolution_factor, (x + 1) * self.resolution_factor), self.matrix))
                vertex3 = Point3(x * self.resolution_factor, (y + 1) * self.resolution_factor,
                                 TerrainMatrix.search_matrix(
                                     (z, (y + 1) * self.resolution_factor, x * self.resolution_factor), self.matrix))
                vertex4 = Point3((x + 1) * self.resolution_factor, (y + 1) * self.resolution_factor,
                                 TerrainMatrix.search_matrix(
                                     (z, (y + 1) * self.resolution_factor, (x + 1) * self.resolution_factor),
                                     self.matrix))

                coll_node.addSolid(CollisionPolygon(vertex1, vertex2, vertex3))
                coll_node.addSolid(CollisionPolygon(vertex2, vertex4, vertex3))

        # Attach the collision node to the terrain node path

        node = GeomNode('terrain')
        node.addGeom(geom)
        node_path = self.render.attachNewNode(node)
        node_path.attachNewNode(coll_node)
        # Scale and position the model
        node_path.setPos(-self.map_size / 2, -self.map_size / 2, -self.max_height / 2)
        node_path.setScale(1.0)


new = MatrixUtil()
new.run()