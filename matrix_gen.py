from numpy import *
from ursina import floor
from noise import *

# first number = 1 for voxel cube 0 for empty
# first 3 numbers after the . = voxel cube type
# numbers 4,5,6,7,8,9 = top, bottom, front, back, right, left - 1 if thr side is exposed to air 0 otherwise
# last number = 9 to mark end of line

class TerrainMatrix:
    def __init__(self, x, y):
        self.types = [
            1.000,  # Air
            1.001,  # Grass
            1.002,  # Dirt
            1.003,  # Stone
        ]

        self.scale = 10
        self.octaves = 6
        self.persistence = 0.5
        self.lacunarity = 2.0
        self.chunk_x = x
        self.chunk_y = y

    def height_gen(self, x, y):
        z = pnoise2(x / self.scale,
                    y / self.scale,
                    octaves=self.octaves,
                    persistence=self.persistence,
                    lacunarity=self.lacunarity) * self.scale
        return floor(z)

    def build_matrix(self):
        terrain_matrix = zeros((256, 64, 64))

        for i in range(0, 100):
            for x in range(0, 64):
                for y in range(0, 64):
                    terrain_matrix[i][x][y] = 1.0030000009

        for x in range(0, 64):
            for y in range(0, 64):
                z = self.height_gen((x + self.chunk_x), (y + self.chunk_y)) + 100
                terrain_matrix[z][x][y] = 1.0010000009
                print(x, z, y)

        return terrain_matrix