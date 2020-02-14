import random
from string import ascii_letters
from dijkstra import Graph


TEST_MODE = True
random_gen = random.Random()


class GraphCreator:

    triangulated = 0

    def __init__(self, test_mode=False):
        self.test_mode = test_mode


    @staticmethod
    def get_matrix_from_file(input_file):
        with open(input_file) as file:
            lines = file.read().splitlines()

        locations = lines[2].split()
        drop_of = lines[1]
        homes = lines[3].split()

        home_indexes = []
        for i in range(len(locations)):
            if locations[i] in homes:
                home_indexes.append(i)

        # Create matrix from file
        matrix = []
        for i in lines[5:]:
            matrix.append(i.split())

        for i in range(len(matrix)):
            for j in range(len(matrix)):
                if matrix[i][j] == 'x':
                    matrix[i][j] = 0
                else:
                    matrix[i][j] = float(matrix[i][j])

        return matrix

    @staticmethod
    def get_home_indices(input_file):
        with open(input_file) as file:
            lines = file.read().splitlines()
        locations = lines[2].split()
        homes = lines[3].split()
        home_indices = []
        for i in range(len(locations)):
            if locations[i] in homes:
                home_indices.append(i)
        return home_indices


    @staticmethod
    def get_locations_from_file(input_file):
        with open(input_file) as file:
            lines = file.read().splitlines()
        file.close()

        return lines[2].split()

    @staticmethod
    def get_starting_location_from_file(input_file):
        with open(input_file) as file:
            lines = file.read().splitlines()
        file.close()

        return lines[4]

    @staticmethod
    def get_homes_from_file(input_file):
        with open(input_file) as file:
            lines = file.read().splitlines()
        file.close()

        return lines[3].split()

    @staticmethod
    def generate_adjacency_matrix(num_loc, x=1):
        """
        By default, it will assume that the null-entries in the matrix are represented by the
        string 'x'. However, if this is not the case, set the x-parameter to something different than 1, and
        it will assume your null-entries are marked as int(0).
        :param num_loc:
        :param x:
        :return:
        """
        if x == 1:
            x = 'x'
        else:
            x = 0
        adjacency_matrix = []
        # First generate with all distances as one:
        for loc_num in range(num_loc):
            # Initialize node with no incident edges
            adjacency = [x for c in range(num_loc)]
            # Add already existing edges
            for prev_adjacency in range(loc_num):
                if adjacency_matrix[prev_adjacency][loc_num] != x:
                    adjacency[prev_adjacency] = adjacency_matrix[prev_adjacency][loc_num]

            # Count number of incident edges:
            edge_num = 0
            for node in adjacency:
                if node != x:
                    edge_num += 1

            # Aiming for an average of 1 to (num_loc / 8) edges incident for every node.
            new_edges = 0
            if edge_num < int(num_loc/8):
                # New edges are only added between this node and upcoming nodes.
                # We find out how many new edges we possibly can add, and generate a random subset of these.
                # Min function make sure we don't go for adding more edges than what is possible ot subsequent nodes
                # If there are nodes left to add edges to:
                if loc_num != num_loc-1:  # BAD SOLUTION.. :/
                    new_edges = random_gen.randint(1, min(int(num_loc/8)-edge_num, num_loc-(loc_num+1)))

            # Ensure that graph is connected
            if edge_num == 0 and new_edges == 0:
                new_edges = 1

            # Always add to one previous node, so that we ensure graph is connected:
            if loc_num != 0:
                rand_prev = random_gen.randint(0, loc_num-1)
                if adjacency[rand_prev] == x:
                    adjacency[rand_prev] = random_gen.randint(1, 10)
                    new_edges -= 1

            # Nodes we can add new edges to:
            pos_new_neighbours = [i for i in range(loc_num + 1, num_loc)]
            for new_edge in range(new_edges):
                adjacency[pos_new_neighbours.pop(random_gen.randint(0, len(pos_new_neighbours)-1))] = random_gen.randint(1, 10)

            adjacency_matrix.append(adjacency)

        for a in range(len(adjacency_matrix)):
            for i in range(num_loc):
                adjacency_matrix[i][a] = adjacency_matrix[a][i]

        return adjacency_matrix

    # One line for each location - entry  j in line i marks the distance of edge from node i to j. 'x' if no edge.
    # index i,i should also be 'x', no edge from a node to itself. # Distances max value 2bil, max 5 decimals.
    # Graph must be connected - any line needs an entry to represent an edge from every node.
    # Enforce triangle inequality

    # For every vertex, v - traverse neighbours, n. If any neighbour has a edge to a node k, and there is an edge k,v.
    # Then w(v,n) < w(v,k) + w(k,n)

    # Keep track of altered edges to makes sure that we don't overwrite any previous progress.
    @staticmethod
    def triangulate_graph(adjacency_matrix, x=1):
        """
        Enforces the triangle inequality on the nodes represented in an adjacency matrix.
        :param adjacency_matrix:
        :param x:
        :return:
        """
        altered = []
        for v in range(len(adjacency_matrix)):
            # If there is an edge from v to n:
            for n in range(len(adjacency_matrix[v])):
                if adjacency_matrix[v][n] != 'x':
                    # Check if n has edges to a node k that is connected to v
                    for k in range(len(adjacency_matrix[n])):
                        # Don't want to count the same edge backwards
                        if k == v:
                            pass
                        else:
                            # If there is an edge from n to k, and from k to v
                            if adjacency_matrix[n][k] != 'x' and adjacency_matrix[k][v] != 'x':
                                # Make sure that the triangle inequality w(v,n) < w(v,k) + w(k,n) # COULD BE BECAUSE OF ADJMAT NOT SYMMETRIC
                                if adjacency_matrix[v][n] > adjacency_matrix[v][k] + adjacency_matrix[k][n]:
                                    if (v, k) not in altered:
                                        new_weight = random_gen.randint(abs(adjacency_matrix[n][v] - adjacency_matrix[k][n]), adjacency_matrix[k][n] + adjacency_matrix[v][n] )
                                        if new_weight == 0:
                                            new_weight = 1
                                        adjacency_matrix[v][k] = new_weight
                                        adjacency_matrix[k][v] = new_weight
                                        altered.extend([(v, k), (k, v)])
                                    elif (k, n) not in altered:
                                        new_weight = random_gen.randint(abs(adjacency_matrix[k][v] - adjacency_matrix[v][n]) , adjacency_matrix[k][v] + adjacency_matrix[v][n] )
                                        if new_weight == 0:
                                            new_weight = 1
                                        adjacency_matrix[k][n] = new_weight
                                        adjacency_matrix[n][k] = new_weight
                                        altered.extend([(k, n), (n, k)])
                                    elif (v, n) not in altered:
                                        new_weight = random_gen.randint(abs(adjacency_matrix[k][v] - adjacency_matrix[k][n]) , adjacency_matrix[k][n] + adjacency_matrix[v][k] )
                                        if new_weight == 0:
                                            new_weight = 1
                                        adjacency_matrix[n][v] = new_weight
                                        adjacency_matrix[v][n] = new_weight
                                        altered.extend([(v, n), (n, v)])
                                    else:
                                        raise (TypeError("Not possible to triangulate graph"))

        return adjacency_matrix

    def generate_input_file(self, num_loc=50):
        num_homes = random_gen.randint(int(num_loc / 2), int(num_loc / 3)*2)
        locations = self._generate_locations(num_loc)
        homes = self._get_random_homes(locations, num_homes)
        start = locations[random_gen.randint(0, len(locations) - 1)]
        matrix = self.generate_adjacency_matrix(num_loc)
        self.triangulate_graph(matrix)

        with open("{}.in".format(num_loc), 'w') as writer:
            writer.write(str(num_loc))
            writer.write("\n")
            writer.write(str(num_homes))
            writer.write("\n")
            writer.writelines(["%s " % loc for loc in locations])
            writer.write("\n")
            writer.writelines(["%s " % home for home in homes])
            writer.write("\n")
            writer.write(start)
            writer.write("\n")
            for node in matrix:
                writer.writelines(["%s " % dist for dist in node])
                writer.write("\n")

        writer.close()

    @staticmethod
    def _generate_locations(n):
        locations = []
        for loc in range(n):
            name = ''
            for i in range(random_gen.randint(5, 10)):
                name += random_gen.choice(ascii_letters)
            locations += [name]
        return locations

    @staticmethod
    def _get_random_homes(locations, num_homes):
        location_copy = locations.copy()
        homes = []
        for home in range(num_homes):
            homes.append(location_copy.pop(random_gen.randint(0, len(location_copy) - 1)))

        return homes




def output_path(ad_mat):
    # Create a graph
    graph = Graph()
    visited = [0]  # Start at node 0
    home_drops = []
    path = [0]
    while len(visited) != len(ad_mat):
        remaining = []
        for node in range(len(ad_mat)):
            if node not in visited:
                remaining.append(node)
        best = remaining[0]
        for j in remaining[1:]:
            if graph.dijkstra(ad_mat, visited[-1])[0][j] < graph.dijkstra(ad_mat, visited[-1])[0][best]:
                best = j
        path.extend(graph.dijkstra(ad_mat, visited[-1])[best+1][1:])
        visited.append(best)

    # Route from end node to start node
    path.extend(graph.dijkstra(ad_mat, visited[-1])[1][1:])

    return path

def output_generator(input_file):
    with open(input_file) as file:
        lines = file.read().splitlines()

    locations = lines[2].split()
    drop_of = lines[1]
    homes = lines[3].split()

    home_indexes = []
    for i in range(len(locations)):
        if locations[i] in homes:
            home_indexes.append(i)

    # Create matrix from file
    matrix = []
    for i in lines[5:]:
        matrix.append(i.split())

    for i in range(len(matrix)):
        for j in range(len(matrix)):
            if matrix[i][j] == 'x':
                matrix[i][j] = 0
            else:
                matrix[i][j] = int(matrix[i][j])

    path_indexes = output_path(matrix)
    path = [locations[j] for j in path_indexes]

    file.close()
    with open('{}.out'.format(len(locations)), 'w') as file:
        file.writelines(['%s ' % stop for stop in path])
        file.write('\n')
        file.write(drop_of)
        file.write('\n')
        for home in home_indexes:
            file.write('{} {}'.format(locations[home], locations[home]))
            file.write('\n')

    file.close()


if __name__ == 'main':
    generator = GraphCreator()
    generator.generate_input_file(50)
    generator.generate_input_file(100)
    generator.generate_input_file(200)

    output_generator('50.in')
    output_generator('100.in')
    output_generator('200.in')

