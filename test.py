#from rust_noise import *

#gen = MapDataGenerator(1024.0, 256)
#data = gen.generate_map_data()

def gen_world(world_chunks=12):
    world = []

    # Calculate the number of chunks in each dimension
    chunks_per_dimension = int(world_chunks ** 0.5)

    for y in range(chunks_per_dimension):
        for x in range(chunks_per_dimension):
            chunk_name = f"Chunk_{x}_{y}"

            # Check if the desired number of chunks is reached
            if len(world) >= world_chunks:
                return world

            world.append(chunk_name)

    return world


print(gen_world(12))


def get_matrix(self, filename='matrix.npy'):
    if os.path.exists(f'map_data/{filename}'):
        print(f'loading: {filename}')
        return TerrainMatrix.load_matrix(filename=filename)
    else:
        print(f'Generating and saving: {filename}')
        self.generate_map_data()
        print(f'Loading: {filename}')
        return TerrainMatrix.load_matrix(filename=filename)