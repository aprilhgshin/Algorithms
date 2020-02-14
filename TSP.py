# What needs to be made?

# 1. You need a proper TSP approx
# 2. You need dijkstras to calculate way between the nodes
# 3. You need a function which takes a graph and a set of cluster (centers) + locations
# The function should find the shortest distances between all those clusters
# Then the function should return a new graph containing only those clusters and the shortest paths
# between them. Then you can give this to TSP to calculate the best route between the clusters.

import math
import tspy
from tspy.solvers import TwoOpt_solver
from input_generator import GraphCreator
from dijkstra import Graph
from read_file import File
from k_means_cluster import K_Medians_Cluster

debug = False
testing = False

def tsp_approx(ad_mat):
    """
    Provided with an adjacency matrix, it will return tsp path for that input.
    :param ad_mat_file: The adjacency matrix
    :return: Tsp path in indexes
    """
    tsp = tspy.TSP()
    tsp.read_mat(ad_mat)

    two = TwoOpt_solver('NN')
    return two.solve(tsp)


def calculate_cluster_distances(ad_mat, indexes):
    """
    Calculate the distances between the given list of indexes in the given adjacency matrix, using dijkstra.
    :param ad_mat: The adjacency matrix representing the graph
    :param indexes: The indexes you want to calculate distances for
    :return: A dict {node: {other_node: distance}}
    """
    distances = {}
    graph = Graph()
    # Each node maintains a list with nodes distances to itself
    for i in indexes:
        for j in indexes:
            distances[i] = {j:0}
    for i in indexes:
        for j in indexes:
            try:
                distances[i][j] = graph.dijkstra(ad_mat, i)[0][j]
            except:
                distances[i][j] = 0

    return distances


def create_cluster_graph(cluster_matrix):
    """
    Given a dictionary like the on returned from "calculate_cluster_distances", i.e. {node: {other_node: distance}},
    this function will create a graph (as adjacency matrix) with only those nodes.
    :param cluster_matrix: The cluster matrix to create graph from
    :return: The adjacency matrix of the new graph
    """
    matrix = [['' for j in range(len(cluster_matrix))] for i in range(len(cluster_matrix))]
    row_numbers = {}
    row = 0
    for i in cluster_matrix.keys():
        row_numbers[i] = row
        row += 1
    for key in cluster_matrix.keys():
        for keykey in cluster_matrix[key].keys():
            matrix[row_numbers[key]][row_numbers[keykey]] = cluster_matrix[key][keykey]

    return matrix


def get_distance_dict(adj_mat):
    """
    Returns a dictionary of the shortest distances from all node to all others in the parameter adjacency matrix.
    :param adj_mat: A adjacency matrix (mxn array) for the graph to calculate distances from
    :return: A dictionary with shortest distances from all nodes to all others
    """
    distances = {}
    graph = Graph()
    for i in range(len(adj_mat)):
        distances[i] = {}
    for i in range(len(adj_mat)):
        for j in range(len(adj_mat)):
            distances[i][j] = graph.dijkstra(adj_mat, i)[0][j]

    return distances


def get_distance_dict_fast(adj_mat):
    """
    Returns a dictionary of the shortest distances from all node to all others in the parameter adjacency matrix.
    :param adj_mat: A adjacency matrix (mxn array) for the graph to calculate distances from
    :return: A dictionary with shortest distances from all nodes to all others
    """
    distances = {}
    dijkstras = {}
    graph = Graph()
    for i in range(len(adj_mat)):
        distances[i] = {}
        dijkstras[i] = graph.dijkstra(adj_mat, i)[0]
    for i in range(len(adj_mat)):
        for j in range(len(adj_mat)):
            distances[i][j] = dijkstras[i][j]

    return distances


def get_path_dict(adj_mat):
    """
    Returns a dictionary where the key values are node-indexes and the values are a new dict.
    The keys in this new dict are all nodes in graph. The values for these keys are shortest paths from original
    node to key node.
    :param adj_mat:
    :return:
    """
    paths = {}
    graph = Graph()
    for i in range(len(adj_mat)):
        paths[i] = {}
    for i in range(len(adj_mat)):
        for j in range(len(adj_mat)):
            if i == j:
                paths[i][j] = [i]
            else:
                paths[i][j] = graph.dijkstra(adj_mat, i)[j+1]

    return paths


def find_shortest_traversal(matrix, node_list):
    """
    Given a matrix and a list of nodes, this function will output the shortest traversal visiting the nodes in that order.
    :param matrix: The matrix
    :param node_list: The list of nodes
    :return: List with path
    """
    path = [node_list[0]]
    graph = Graph()
    for i in range(len(node_list[:-1])):
        path.extend(graph.dijkstra(graph=matrix, src=node_list[i])[node_list[i+1]+1][1:])
    return path


def start_shift(path, start):
    """
    Shifts a path (i.e. [1,2,3,4,5,6,1] such that it starts at 'start'-param.
    I.e. it start=4 it would return [4,5,6,1,2,3,4]
    :param path:
    :param start:
    :return:
    """
    if path[0] == start:
        return path
    else:
        start_index = path.index(start)
        new_path = []
        path = path[:-1]  # Old start is also old end, we don't want to dupe this in new path
        for i in path[start_index:]:
            new_path.append(i)
        for i in path[:start_index+1]:
            new_path.append(i)

    return new_path


def get_path_with_names(path, locations):
    """
    Given a path with indexes, and a set of locations, it will return the path but with name from the locations list.
    :param path:
    :param locations:
    :return:
    """
    new_path = []
    for node in path:
        new_path.append(locations[node])
    return new_path


def convert_drop_off_plan_to_names(plan, locations):
    """
    Given an output plan {node_index: [dropoffs_indexes]} and a set of locations, it will return the dropoff plan
    but with names instead of indexes.
    :param plan:
    :param locations:
    :return:
    """
    new_plan = {}
    for key in plan.keys():
        new_plan[locations[key]] = []
        for val in plan[key]:
            new_plan[locations[key]].append(locations[val])
    return new_plan


def calculate_path_distance(path, distances):
    """
    Calculates the distance traversed in a given path. Expects a distance-dict ({node: {other_node: distance}}) for the
    graph containing the path.
    :param path: The path to get distance for
    :param distances: The distance-dict for graph
    :return: The total distance traversed by the path
    """
    total_distance = 0
    for i in range(len(path)-1):
        total_distance += distances[path[i]][path[i+1]]
    return total_distance


def get_home_indices(locations, homes):
    """
    Takes a list of locations and a list of homes (both as strings).
    Returns the indices of location that corresponds to each home.
    :param locations: List of locations
    :param homes: List of homes
    :return: List of indices in locations of location that corresponds to each home.
    """
    indexes = []
    for home in homes:
        indexes.append(locations.index(home))
    return indexes

"""
METHOD NOT WORKING: NEED TO BE ABLE TO KNOW THE CLUSTER-CENTER OF ANY NODE
def assert_tsp_optimal(drop_offs, clustering):
    # Invert clustering so we can lookup center from node
    inv_clustering = {}
    for key in clustering.keys():
        inv_clustering[key] = key
        for node in clustering[key]:
            inv_clustering[node] = key
    # Delete clusters whos locations were not used as drop-offs.
    used = {center: False for center in clustering.keys()}
    for node in drop_offs.keys():
        used[inv_clustering[node]] = True

    # Would mean all are True (visited)
    if len(set(used.values())) == 1:
        optimal = True
    else:
        optimal = False

    centers_in_use = []
    for key in used.keys():
        if used[key]:
            centers_in_use.append(key)

    return optimal, centers_in_use
"""

def algorithm(input_file, output_file):
    """
    Drive TA's Home Algorithm.
    :param input_file: Input file
    :param output_file: Output file
    """
    # Generate the matrix from file
    mat = GraphCreator.get_matrix_from_file(input_file)

    # Find locations and homes.
    locations = GraphCreator.get_locations_from_file(input_file)
    homes = GraphCreator.get_homes_from_file(input_file)
    home_indexes = get_home_indices(locations, homes)
    start_loc = locations.index(GraphCreator.get_starting_location_from_file(input_file).strip())


    # Do some stuff to get the clusters
    # Cluster-centers should come from aprils funciton
    k_medians = K_Medians_Cluster(home_indexes, mat, num_trials=6)
    

    cluster_centers = k_medians.approx_best_clustering()[0]
    #cluster_centers = [1, 5, 7, 14, 32]  # Should be aprils_output.keys()

    # Add starting location to cluster centers so that it is included in our path
    if start_loc not in cluster_centers:
        cluster_centers.append(start_loc)

    # Calculate the closest distances between the clusters so that we can run TSP
    cluster_distances = calculate_cluster_distances(mat, cluster_centers)

    # Create a graph with only clusters to use for TSP
    cluster_graph = create_cluster_graph(cluster_distances)

    # Get distance dict to use for drop-offs
    distance_dict = get_distance_dict_fast(mat)

    if len(cluster_centers) > 1:
        # Do the TSP approx:
        tsp = tsp_approx(cluster_graph)
        # Convert back to indexes in original graph
        nodes_in_original = [cluster_centers[i] for i in tsp]
        # Make it so that we start at start location
        nodes_in_original = start_shift(nodes_in_original, start_loc)

        # Then find actual path between nodes:
        path_in_original = find_shortest_traversal(mat, nodes_in_original)

    else:
        path_in_original = cluster_centers

    # Calculate the distance for the path (FOR TESTING)
    if debug:
        print("path distance: ",calculate_path_distance(path_in_original, distance_dict))
        print("total sum: ", k_medians.get_min_sum())

    # We know path, we know homes. See where it is optimal to drop everyone of.
    drop_offs = {}
    unique_stops = list(set(path_in_original))
    # Found out which drop off location is best for each home
    for home_index in home_indexes:
        best = unique_stops[0]
        for i in range(len(unique_stops)):
            if distance_dict[home_index][unique_stops[i]] < distance_dict[home_index][best]:
                best = unique_stops[i]
        drop_offs[home_index] = best

    # Invert dropoffs so we can see where we should drop of every TA
    drop_off_plan = {val: [] for val in list(set(drop_offs.values()))}

    for key in drop_offs.keys():
        drop_off_plan[drop_offs[key]].append(key)

    # Get everything nesecarry to create output
    # Path with names instead of indexes
    path = get_path_with_names(path_in_original, locations)
    # Number of dropoffs
    num_dropoffs = len(drop_off_plan.keys())
    # Drop off plan with names instead of indexes
    drop_off_plan = convert_drop_off_plan_to_names(drop_off_plan, locations)

    # Now wright it all to the output file
    with open(output_file, 'w') as file:
        for loc in path:
            file.write("{} ".format(loc))
        file.write("\n")
        file.write("{}\n".format(num_dropoffs))
        for key in drop_off_plan:
            drop_off_string = key
            for val in drop_off_plan[key]:
                drop_off_string += " {}".format(val)
            file.write("{}\n".format(drop_off_string))
    file.close()

    #if testing:
    #    return {"totalsum": k_medians.get_min_sum(), "pathdistance":calculate_path_distance(path_in_original, distance_dict)}




#if testing:
#    algorithm('inputs/10_50.in', 'outputs/10_50.out')

#41_100
# algorithm('inputs/41_100.in', 'outputs/41_100.out')