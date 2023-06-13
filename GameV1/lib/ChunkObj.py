# This Class Defines A Chunk Object For The Terrain
from GameV1.config.settings import *
from panda3d.core import Vec2, Vec3, NodePath, Geom, GeomTriangles, GeomVertexWriter, GeomNode, GeomVertexFormat, GeomVertexData
from scipy.spatial import Delaunay
import noise
import os
import random


class ChunkObj:
    def __init__(self, base, pos):

        r = random.random()
        g = random.random()
        b = random.random()

        # Load In ShowBase From Main
        self.base = base

        # Load In Settings
        self.chunkSize = CHUNKSIZE
        self.octaves = OCTAVES
        self.persistence = PERSISTENCE
        self.lacunarity = LACUNARITY

        # Chunk Position
        self.chunkPos = Vec2(pos.x, pos.y)

        # Chunk FileName
        self.fileName = f'Chunk{pos.x}_{pos.y}.bam'

        # Chunk Object
        self.chunk = self.get_chunk()

        # Set Chunk Position For Indexing
        self.chunk.setPos(Vec3(pos.x - 1, pos.y - 1, 0))
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

        # Set up the 2D points for the Delaunay triangulation
        #points = []
        #for x in range(self.chunkSize):
        #    for y in range(self.chunkSize):
        #        points.append([x, y])

        # Compute the Delaunay triangulation
        #tri = Delaunay(points)

        vdata = GeomVertexData('chunk', format, Geom.UHStatic)
        #vdata.setNumRows(len(points))
        vdata.setNumRows(3)

        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        color = GeomVertexWriter(vdata, 'color')

        for x in range(self.chunkSize):
            for y in range(self.chunkSize):
                h = noise.snoise2(x, y, self.octaves, self.persistence, self.lacunarity)
                vertex.addData3(x, y, h)
                normal.addData3(0, 0, 1)
                color.addData4(0, 0.5, 0.5, 1)

        # Iterate through the points to generate the heights and write to the vertex data
        #for i in range(len(points)):
            #h = noise.snoise2(points[i][0], points[i][1], self.octaves, self.persistence, self.lacunarity)
        #    vertex.addData3(points[i][0], points[i][1], 0)
        #    normal.addData3(0, 0, 1)
        #    color.addData4(0, 0.5, 0.5, 1)

        prim = GeomTriangles(Geom.UHStatic)

        for x in range(self.chunkSize - 1):
            for y in range(self.chunkSize - 1):
                v1 = x * self.chunkSize + y
                v2 = v1 + 1
                v3 = v1 + self.chunkSize
                v4 = v3 + 1

                prim.addVertices(v1, v3, v2)
                prim.addVertices(v2, v3, v4)

        # Iterate through the Delaunay triangles and add them to the primitive
        #for triangle in tri.simplices:
        #    prim.addVertices(triangle[0], triangle[1], triangle[2])

        geom = Geom(vdata)
        geom.addPrimitive(prim)

        gnode = GeomNode(f'{self.chunkPos[0]}_{self.chunkPos[1]}')
        gnode.addGeom(geom)
        node_path = NodePath(gnode)
        node_path.writeBamFile(f'data/map_data/{self.fileName}')

        return node_path

