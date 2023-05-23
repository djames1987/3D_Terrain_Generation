import json


class Octree:
    def __init__(self, region):
        self.root = Node(region)


class Node:
    def __init__(self, region):
        self.region = region
        self.children = []
        self.voxel_cubes = []

    def add_voxel_cube(self, voxel_cube_data):
        self.voxel_cubes.append(voxel_cube_data)


class Region:
    def __init__(self, min_x, min_y, min_z, max_x, max_y, max_z):
        self.min_x = min_x
        self.min_y = min_y
        self.min_z = min_z
        self.max_x = max_x
        self.max_y = max_y
        self.max_z = max_z


def subdivide(node):
    region = node.region
    mid_x = (region.min_x + region.max_x) // 2
    mid_y = (region.min_y + region.max_y) // 2
    mid_z = (region.min_z + region.max_z) // 2

    # Create child regions
    regions = [
        Region(region.min_x, region.min_y, region.min_z, mid_x, mid_y, mid_z),
        Region(region.min_x, region.min_y, mid_z, mid_x, mid_y, region.max_z),
        Region(region.min_x, mid_y, region.min_z, mid_x, region.max_y, mid_z),
        Region(region.min_x, mid_y, mid_z, mid_x, region.max_y, region.max_z),
        Region(mid_x, region.min_y, region.min_z, region.max_x, mid_y, mid_z),
        Region(mid_x, region.min_y, mid_z, region.max_x, mid_y, region.max_z),
        Region(mid_x, mid_y, region.min_z, region.max_x, region.max_y, mid_z),
        Region(mid_x, mid_y, mid_z, region.max_x, region.max_y, region.max_z),
    ]

    # Create child nodes
    for child_region in regions:
        child_node = Node(child_region)
        node.children.append(child_node)

        # Recursively subdivide child nodes if necessary
        if should_subdivide(child_node):
            subdivide(child_node)


def should_subdivide(node):
    # Modify this condition based on your criteria for subdivision
    return len(node.voxel_cubes) > 64


def find_target_node(node, voxel_cube_position):
    # Check if the voxel cube's position lies within the node's region
    if is_position_inside_region(voxel_cube_position, node.region):
        # If the node has no children, it is the target node
        if len(node.children) == 0:
            return node
        else:
            # Recursively search among the child nodes
            for child_node in node.children:
                target_node = find_target_node(child_node, voxel_cube_position)
                if target_node:
                    return target_node

    return None  # Return None if the target node is not found


def is_position_inside_region(position, region):
    min_x, min_y, min_z = region.min_x, region.min_y, region.min_z
    max_x, max_y, max_z = region.max_x, region.max_y, region.max_z
    x, y, z = position

    return min_x <= x <= max_x and min_y <= y <= max_y and min_z <= z <= max_z


def search_node(node, search_criteria):
    # Check if the current node satisfies the search criteria
    if satisfies_criteria(node, search_criteria):
        return node

    # Recursively search among the child nodes
    for child_node in node.children:
        target_node = search_node(child_node, search_criteria)
        if target_node:
            return target_node

    return None  # Return None if the target node is not found


def satisfies_criteria(node, search_criteria):
    # Modify this function based on your specific search criteria
    # Return True if the node satisfies the search criteria, False otherwise
    voxel_cubes = node.voxel_cubes
    for voxel_cube in voxel_cubes:
        if voxel_cube == search_criteria:
            return True
    return False


def search_node_by_position(node, search_position):
    # Check if any voxel cube in the current node has the desired position
    for voxel_cube in node.voxel_cubes:
        if voxel_cube['position'] == search_position:
            return node

    # Recursively search among the child nodes
    for child_node in node.children:
        target_node = search_node_by_position(child_node, search_position)
        if target_node:
            return target_node

    return None  # Return None if the target node is not found


def save_octree(octree, filename):
    serialized_octree = serialize_octree(octree)
    with open(filename, 'w') as file:
        json.dump(serialized_octree, file)


def serialize_octree(octree):
    serialized_nodes = serialize_nodes(octree.root)
    serialized_octree = {
        'root': serialized_nodes
    }
    return serialized_octree


def serialize_nodes(node):
    serialized_node = {
        'region': {
            'min_x': node.region.min_x,
            'min_y': node.region.min_y,
            'min_z': node.region.min_z,
            'max_x': node.region.max_x,
            'max_y': node.region.max_y,
            'max_z': node.region.max_z
        },
        'voxel_cubes': node.voxel_cubes,
        'children': []
    }

    for child_node in node.children:
        serialized_child_node = serialize_nodes(child_node)
        serialized_node['children'].append(serialized_child_node)

    return serialized_node


def load_octree(filename):
    with open(filename, 'r') as file:
        serialized_octree = json.load(file)
    return deserialize_octree(serialized_octree)


def deserialize_octree(serialized_octree):
    root_node = deserialize_nodes(serialized_octree['root'])
    octree = Octree(None)  # Create an Octree instance with a temporary root
    octree.root = root_node
    return octree


def deserialize_nodes(serialized_node):
    region = Region(serialized_node['region']['min_x'],
                    serialized_node['region']['min_y'],
                    serialized_node['region']['min_z'],
                    serialized_node['region']['max_x'],
                    serialized_node['region']['max_y'],
                    serialized_node['region']['max_z'])

    node = Node(region)
    node.voxel_cubes = serialized_node['voxel_cubes']

    for serialized_child_node in serialized_node['children']:
        child_node = deserialize_nodes(serialized_child_node)
        node.children.append(child_node)

    return node


def modify_voxel_cube_by_position(octree, search_position, new_data):
    target_node = search_node_by_position(octree.root, search_position)
    if target_node:
        for i, voxel_cube in enumerate(target_node.voxel_cubes):
            if voxel_cube['position'] == search_position:
                target_node.voxel_cubes[i] = new_data
                break


def initialize_octree_with_air(octree, voxel_cube_data):
    fill_node_with_air(octree.root, voxel_cube_data)


def fill_node_with_air(node, voxel_cube_data):
    node.voxel_cubes = [voxel_cube_data]

    # Recursively fill child nodes with air
    for child_node in node.children:
        fill_node_with_air(child_node, voxel_cube_data)


def initialize_octree_with_region(octree, region, voxel_cube_data):
    initialize_node_with_region(octree.root, region, voxel_cube_data)


def initialize_node_with_region(node, region, voxel_cube_data):
    node.region = region

    if should_subdivide(node):
        subdivide_node(node)

        # Recursively initialize child nodes with corresponding regions
        child_regions = get_subregions(region)
        for child_node, child_region in zip(node.children, child_regions):
            initialize_node_with_region(child_node, child_region, voxel_cube_data)
    else:
        voxel_cubes = []
        for x in range(region.min_x, region.max_x + 1):
            for y in range(region.min_y, region.max_y + 1):
                for z in range(region.min_z, region.max_z + 1):
                    voxel_cube = voxel_cube_data.copy()
                    voxel_cube['position'] = (x, y, z)
                    voxel_cubes.append(voxel_cube)
        node.voxel_cubes = voxel_cubes


def subdivide_node(node):
    # Subdivide the node into eight child nodes
    region = node.region
    mid_x = (region.min_x + region.max_x) // 2
    mid_y = (region.min_y + region.max_y) // 2
    mid_z = (region.min_z + region.max_z) // 2

    # Create child regions
    regions = [
        Region(region.min_x, region.min_y, region.min_z, mid_x, mid_y, mid_z),
        Region(region.min_x, region.min_y, mid_z, mid_x, mid_y, region.max_z),
        Region(region.min_x, mid_y, region.min_z, mid_x, region.max_y, mid_z),
        Region(region.min_x, mid_y, mid_z, mid_x, region.max_y, region.max_z),
        Region(mid_x, region.min_y, region.min_z, region.max_x, mid_y, mid_z),
        Region(mid_x, region.min_y, mid_z, region.max_x, mid_y, region.max_z),
        Region(mid_x, mid_y, region.min_z, region.max_x, region.max_y, mid_z),
        Region(mid_x, mid_y, mid_z, region.max_x, region.max_y, region.max_z),
    ]

    # Create child nodes
    for child_region in regions:
        child_node = Node(child_region)
        node.children.append(child_node)


def get_subregions(region):
    # Get subregions for a given region
    min_x, min_y, min_z = region.min_x, region.min_y, region.min_z
    max_x, max_y, max_z = region.max_x, region.max_y, region.max_z
    mid_x = (min_x + max_x) // 2
    mid_y = (min_y + max_y) // 2
    mid_z = (min_z + max_z) // 2

    subregions = [
        Region(min_x, min_y, min_z, mid_x, mid_y, max_z),
        Region(min_x, min_y, mid_z, mid_x, mid_y, max_z),
        Region(min_x, mid_y, min_z, mid_x, max_y, max_z),
        Region(min_x, mid_y, mid_z, mid_x, max_y, max_z),
        Region(mid_x, min_y, min_z, max_x, mid_y, max_z),
        Region(mid_x, min_y, mid_z, max_x, mid_y, max_z),
        Region(mid_x, mid_y, min_z, max_x, max_y, max_z),
        Region(mid_x, mid_y, mid_z, max_x, max_y, max_z),
    ]

    return subregions


def add_voxel_cubes(octree, voxel_cube_data_list):
    for voxel_cube_data in voxel_cube_data_list:
        position = voxel_cube_data['position']
        target_node = search_node_by_position(octree.root, position)
        if target_node:
            target_node.voxel_cubes.append(voxel_cube_data)


def test():
    pass
    # Define the initial region for the terrain
    # initial_region = Region(0, 0, 0, 100, 100, 100)
    # region = Region(0, 0, 0, 256, 256, 256)
    # Create the Octree
    # octree = Octree(region)

    # Subdivide the Octree starting from the root node
    # subdivide(octree.root)

    # Assuming you have an Octree instance named 'octree'

    # Create voxel cube data
    # voxel_cube_data = {'position': (10, 20, 30), 'color': 'red', 'type': 'grass'}
    # voxel_cube_position = (10, 20, 30)  # Example voxel cube position

    # Find the target node based on the voxel cube's position
    # target_node = find_target_node(octree.root, voxel_cube_position)

    # Add voxel cube data to the target node
    # if target_node:
    #    target_node.add_voxel_cube(voxel_cube_data)

    # Assuming you have an Octree instance named 'octree'

    # Define the search criteria for the voxel cube
    # search_criteria = {'color': 'red', 'type': 'grass'}

    # Search the Octree for the target node
    # target_node = search_node(octree.root, search_criteria)

    # if target_node:
    # Target node found
    #    print("Target node found!")
    #     print(target_node.voxel_cubes)
    # else:
    #     Target node not found
    #     print("Target node not found.")

    # Assuming you have an Octree instance named 'octree'

    # Define the position of the voxel cube you want to search for
    # search_position = (10, 20, 30)  # Example search position

    # Search the Octree for the target node based on position
    # target_node = search_node_by_position(octree.root, search_position)

    # if target_node:
    #    Target node found
    #    print("Target node found!")
    # else:
    # Target node not found
    # print("Target node not found.")

    # Assuming you have an Octree instance named 'octree'

    # Define the voxel cube data for an "Air" block
    # air_voxel_cube_data = {'type': 'Air', 'color': 'transparent'}

    # Initialize the Octree with "Air" blocks
    # initialize_octree_with_air(octree, air_voxel_cube_data)
    # Define the voxel cube data for an "Air" block
    # air_voxel_cube_data = {'type': 'Air', 'color': 'transparent'}

    # Initialize the Octree with the region divided into four chunks
    # initialize_octree_with_region(octree, region, air_voxel_cube_data)

    # save_octree(octree, 'octree.json')
# Define the voxel cube data to be added
    # new_voxel_cube_data_list = [
    #    {'position': (10, 20, 30), 'color': 'red', 'type': 'grass'},
    #    {'position': (15, 25, 35), 'color': 'blue', 'type': 'water'},
    # Add more voxel cube data as needed
# ]

# Add the voxel cubes to the existing Octree
# add_voxel_cubes(octree, new_voxel_cube_data_list)
# test()

# octree = load_octree('octree.json')
# search_position = (10, 20, 30)  # Example search position
# target_node = search_node_by_position(octree.root, search_position)
# if target_node:
    # Target node found
#    print("Target node found!")
# else:
    # Target node not found
#    print("Target node not found.")
