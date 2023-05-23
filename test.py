from ursina import *
from chunk_gen import Chunk
import util

app = Ursina()

region_position = (1, 0)
region_size = (4, 1)
chunk_size = (64, 64, 256)
max_depth = 8

region_min_point, region_max_point, chunk_bounding_boxes = util.calculate_region_and_chunk_bounding_boxes(region_position, region_size, chunk_size)

# Construct the Octree for the region
region_octree = util.construct_octree(region_min_point, region_max_point, chunk_bounding_boxes, max_depth)
print('Octree')
# Generate chunk for each bounding box in the octree
chunk = Chunk()
for box in chunk_bounding_boxes:
    chunk.gen_chunk(box[0], box[1], region_octree)

EditorCamera()
app.run()