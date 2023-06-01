from settings import *
from terrain_matrix import *
from rust_noise import *
from panda3d.core import Geom, GeomNode, GeomVertexWriter, GeomVertexFormat, GeomVertexData, GeomTriangles, Point3, LVector3f, BitMask32
import os
from scipy.spatial import Delaunay
from panda3d.bullet import BulletTriangleMesh, BulletTriangleMeshShape, BulletRigidBodyNode

class TerrainManager:
    def __init__(self, base, physics_world):

        # Load ShowBase
        self.base = base

        # Load Physics
        self.physics_world = physics_world

        # Load map generation settings
        self.map_size = MapSettings.MAP_SIZE
        self.max_height = MapSettings.MAX_HEIGHT
        self.octaves = MapSettings.OCTAVES
        self.persistence = MapSettings.PERSISTENCE
        self.lacunarity = MapSettings.LACUNARITY
        self.amplitude = MapSettings.AMPLITUDE
        self.frequency = MapSettings.FREQUENCY
        self.resolution_factor = MapSettings.RESOLUTION_FACTOR

        # Load/generate terrain matrix
        #self.matrix = self.get_matrix()

    def get_matrix(self, filename='matrix.npy'):
        if os.path.exists(f'map_data/{filename}'):
            print(f'loading: {filename}')
            return TerrainMatrix.load_matrix(filename=filename)
        else:
            print(f'Generating and saving: {filename}')
            self.gen_terrain()
            print(f'Loading: {filename}')
            return TerrainMatrix.load_matrix(filename=filename)

    def gen_terrain(self):
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

    from scipy.spatial import Delaunay

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

        # Create grid points and add vertex data
        grid_points = []

        for y in range(effective_map_size):
            for x in range(effective_map_size):
                h = TerrainMatrix.search_matrix((0, y * self.resolution_factor, x * self.resolution_factor),
                                                self.matrix)
                vertex.addData3f(Point3(x * self.resolution_factor, y * self.resolution_factor, h))
                normal.addData3f(LVector3f(0, 0, 1))
                color.addData4f(0, h / self.max_height, 0, 1)
                grid_points.append([x * self.resolution_factor, y * self.resolution_factor])

        # Perform Delaunay triangulation
        tri = Delaunay(grid_points)
        triangles = tri.simplices

        # Create the triangles
        tris = GeomTriangles(Geom.UHStatic)

        for triangle in triangles:
            tris.addVertices(triangle[0], triangle[1], triangle[2])
            tris.closePrimitive()

        # Assemble the geometry
        geom = Geom(vdata)
        geom.addPrimitive(tris)
        node = GeomNode('terrain')
        node.addGeom(geom)
        node_path = self.base.render.attachNewNode(node)
        node_path.writeBamFile('terrain.bam')

        mesh = BulletTriangleMesh()
        mesh.addGeom(geom)
        shap = BulletTriangleMeshShape(mesh, dynamic=False)
        ground = self.base.render.attachNewNode(BulletRigidBodyNode('Ground'))
        ground.node().addShape(shap)
        ground.setCollideMask(BitMask32.allOn())
        self.physics_world.attachRigidBody(ground.node())
        ground.setPos(-self.map_size / 2, -self.map_size / 2, -self.max_height / 2)
        ground.setScale(1.0)
        ground.writeBamFile('collison.bam')

        # Scale and position the model
        node_path.setPos(-self.map_size / 2, -self.map_size / 2, -self.max_height / 2)
        node_path.setScale(1.0)
        #node_path.setRenderModeWireframe()

    def test_load(self):
        terrain = self.base.loader.loadModel("terrain.bam")
        terrain_collison = self.base.loader.loadModel('collison.bam')

        terrain.reparentTo(self.base.render)
        terrain.setPos(-self.map_size / 2, -self.map_size / 2, -self.max_height / 2)
        terrain.setScale(1.0)

        terrain_collison.setPos(-self.map_size / 2, -self.map_size / 2, -self.max_height / 2)
        terrain_collison.setScale(1.0)
        self.physics_world.attachRigidBody(terrain_collison.node())

