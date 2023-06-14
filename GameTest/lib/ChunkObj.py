# This Class Defines A Chunk Object For The Terrain
from GameTest.config.settings import *
from panda3d.core import Vec2, Vec3, NodePath, Geom, GeomTriangles, GeomVertexWriter, GeomNode, GeomVertexFormat, GeomVertexData
from panda3d.bullet import *
import noise
import os
import pickle
import random


class ChunkObj:
    def __init__(self, base, pos, world_physics):

        r = random.random()
        g = random.random()
        b = random.random()

        # Load In ShowBase From Main
        self.base = base

        # Load In World Physics
        self.pWorld = world_physics

        # Load In Settings
        self.chunkSize = CHUNKSIZE
        self.octaves = OCTAVES
        self.persistence = PERSISTENCE
        self.lacunarity = LACUNARITY
        self.amplitude = AMPLITUDE
        self.frequency = FREQUENCY
        self.resolution = RESOLUTION

        # Chunk Position
        self.chunkPos = Vec2(pos.x, pos.y)

        # Chunk FileName
        self.fileName = f'Chunk{pos.x}_{pos.y}.bam'

        # Chunk Object
        self.chunk = self.get_chunk()

        # Collision Node
        self.chunk_collision = self.create_collision_node()

        self.chunk.setColor(r, g, b, 1)

    def get_chunk(self):
        if os.path.exists(f'data/map_data/{self.fileName}'):
            chunk = self.load_chunk()
            return chunk
        else:
            chunk = self.gen_chunk()
            return chunk

    def load_chunk(self):
        return self.base.loader.loadModel(f'data/map_data/{self.fileName}')

    def save_chunk(self):
        if self.chunk:
            self.chunk.writeBamFile(f'data/map_data/{self.fileName}')

    def gen_chunk(self):

        format = GeomVertexFormat.getV3n3c4()

        vdata = GeomVertexData('chunk', format, Geom.UHStatic)
        vdata.setNumRows(3)

        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        color = GeomVertexWriter(vdata, 'color')

        for x in range(self.chunkSize):
            for y in range(self.chunkSize):
                global_x = self.chunkPos.x * (self.chunkSize - 1) + x
                global_y = self.chunkPos.y * (self.chunkSize - 1) + y
                h = self.amplitude * noise.snoise2(global_x * self.frequency, global_y * self.frequency, self.octaves, self.persistence, self.lacunarity)
                vertex.addData3(global_x, global_y, h)
                normal.addData3(0, 0, 1)
                color.addData4(0, 0.5, 0.5, 1)

        prim = GeomTriangles(Geom.UHStatic)

        for x in range(self.chunkSize - 1):
            for y in range(self.chunkSize - 1):
                v1 = x * self.chunkSize + y
                v2 = v1 + 1
                v3 = v1 + self.chunkSize
                v4 = v3 + 1

                prim.addVertices(v1, v3, v2)
                prim.addVertices(v2, v3, v4)

        geom = Geom(vdata)
        geom.addPrimitive(prim)

        gnode = GeomNode(f'{self.chunkPos[0]}_{self.chunkPos[1]}')
        gnode.addGeom(geom)
        node_path = NodePath(gnode)
        mesh = BulletTriangleMesh()
        mesh.addGeom(geom)
        shape = BulletTriangleMeshShape(mesh, dynamic=False)
        collision_node = BulletRigidBodyNode(f'{self.chunkPos.x}_{self.chunkPos.y}')
        collision_node.addShape(shape)

        with open(f'data/map_data/Collision_{self.chunkPos.x}_{self.chunkPos.y}.pickle', 'wb') as f:
            pickle.dump(collision_node, f)

        node_path.writeBamFile(f'data/map_data/{self.fileName}')

        return node_path

    def create_collision_node(self):
        with open(f'data/map_data/Collision_{self.chunkPos.x}_{self.chunkPos.y}.pickle', 'rb') as f:
            collision_node = pickle.load(f)

            return collision_node
