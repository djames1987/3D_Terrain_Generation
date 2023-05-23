from ursina import *

from util import *


class Chunk:
    def __init__(self, chunk_size=64, chunk_height=256, octaves=4, scale=0.1):
        self.chunk_size = chunk_size
        self.chunk_height = chunk_height
        self.octaves = octaves
        self.scale = scale


    def gen_cube(self, x, y, z):
        vertices = [(x, y, z), (x + 1, y, z), (x + 1, y, z + 1), (x, y, z + 1),
                    (x, y + 1, z), (x + 1, y + 1, z), (x + 1, y + 1, z + 1), (x, y + 1, z + 1)]

        # Generate all six faces
        faces = [(0, 1, 5, 4),  # bottom
                 (4, 5, 6, 7),  # top
                 (3, 2, 6, 7),  # right
                 (1, 0, 3, 2),  # left
                 (0, 4, 7, 3),  # front
                 (1, 2, 6, 5)]  # back

        return vertices, faces


    def gen_chunk(self, min_point, max_point, octree):
        culled_voxels = cull_faces(octree)

        vertices = []
        faces = []
        for voxel in culled_voxels:
            v, f = self.gen_cube(*voxel)
            vertices += v
            faces += [[i + len(vertices) - 8 for i in face] for face in f]

        chunk_mesh = Mesh(vertices=vertices, triangles=faces)
        return Entity(model=chunk_mesh)
