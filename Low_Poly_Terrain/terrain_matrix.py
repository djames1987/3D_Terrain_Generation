import numpy as np

class TerrainMatrix:

    @staticmethod
    def gen_matrix(map_size, map_depth):
        return np.zeros((map_depth, map_size, map_size))

    @staticmethod
    def update_matrix(pos, data, matrix):
        matrix[pos[0]][pos[1]][pos[2]] = data

    @staticmethod
    def search_matrix(pos, matrix):
        return matrix[pos[0]][pos[1]][pos[2]]

    @staticmethod
    def load_matrix(filename='terrain_matrix.npy'):
        return np.load(f'map_data/{filename}')

    @staticmethod
    def save_matrix(matrix, filename='terrain_matrix.npy'):
        np.save(f'map_data/{filename}', matrix)

    # Encoding and Decoding to save space not needed yet
    @staticmethod
    def encode(data):
        pass

    @staticmethod
    def decode(data):
        pass