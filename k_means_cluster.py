# April Shin
# CS 170 Algorithms, Fall 2019
# Project Drop off TA's Home

import random
import copy
import math
from dijkstra import Graph
from read_file import File
from input_generator import GraphCreator

# Turn on and off to print debugging statements
debug = False
debug_startingk = False
debug_k_medians = False
debug_k = False
debug_approx_k = False

# To utitize multiple k values to approximate k (optimal number of clusters for optimal solution)
k_is_approximated = True

# The K_Medians_Cluster class generates k number of clusters of homes using an approximated k to optimize the clustering i.e. obtain a high Dunn Index
class K_Medians_Cluster():

    def __init__(self, homes, graph, num_trials):
        # key: total sum distance
        # value: centers for that total sum distance
        self.sumdist_cent_hist = {}

        # key: total sum distance
        # value: centers and corresponding cluster points for that toal sum distance
        self.sumdist_cluster_hist = {}

        self.sumdist_hist = [] # list of total sum distances
        self.homes = homes
        self.graph = graph
        self.first_center = 0
        self.distances = self.get_distance_list_fast(self.graph)
        self.k_potentials = []
        self.k_trials(num_trials) # Generate num_trials potential k values to find best value of k to cluster
        self.ith_k = 0
        self.dunn_index = 0



    def get_distance_list_fast(self, adj_mat):
        """
        Returns a list of the shortest distances from all node to all others in the parameter adjacency matrix.
        index corresponds to node, value correponds to distances.
        :param adj_mat: An adjacency matrix (mxn array) for the graph to calculate distances from
        :return: A list with shortest distances from all nodes to all others
        """
        distances = [0 for j in range(len(adj_mat))]
        dijkstras = [0 for j in range(len(adj_mat))]
        graph = Graph()
        for i in range(len(adj_mat)):
            distances[i] = [0 for j in range(len(adj_mat))]
            dijkstras[i] = graph.dijkstra(adj_mat, i)[0]
        for i in range(len(adj_mat)):
            for j in range(len(adj_mat)):
                distances[i][j] = dijkstras[i][j]
        return distances


    def k_trials(self, num_trials):
        '''
        Generate all k values you want apply to k_medians_clustering for k approximation
        The k that generates best cluster_quality is the number
        :param num_trials: int number of different k values to generate clusters
        '''

        # Divide length of homes into intervals. We will only be organizing the homes into clusters.
        interval_len = math.ceil(len(self.homes)/num_trials)

        if debug_k:
            print("num trials: ", num_trials)
            print("interval length: ", interval_len)
            print("home length: ", len(self.homes))

        self.k_potentials = []
        pos = 1

        if len(self.homes) == 1:
            self.k_potentials.append(pos)
            num_trials = 1
        # Set the midpoint of each interval as the value of k until you have num_trials k values or already traversed through all intervals.
        while (len(self.k_potentials) < num_trials) and (pos < len(self.homes)):
            if pos + interval_len <= len(self.homes):
                upper_limit = pos + interval_len - 1
                if debug_k:
                    print("upper_limit: ", upper_limit)
                    print("lower_limit: ", pos)
            else:
                # If at the last interval of the length of the graph
                upper_limit = len(self.homes) - 1
            self.k_potentials.append(pos + int((upper_limit - pos)/2))
            pos += interval_len


    def k_starting_centers(self, distances_copy, center_arr, i, k):
        '''
        Choose k starting centers by starting with a random location and choosing next center to be the furthest location from the current center.
        Following centers will be chosen to be the furthest location from all previously chosen centers.
        :param distances_copy: adjacency matrix consisting of distances between every pair of locations
               center_arr: Empty list of length k to store generated k centers.
                             First element initalized to be the randomly generated starting center
                i: iteration count, start from 0
                k: approximated k value for creating k clusters
        :return: list of center location indices
        '''

        if i == (k-1):
            return center_arr

        if debug_startingk:
            print("first_center: ",self.first_center)
            print("center_arr: ", center_arr)

        # Cluster all locations wrt centers in center_arr
        cluster_dict = self.clustering(center_arr, k, False)

        if debug_startingk:
            print("size of home: ", len(self.homes))
            print("size: ", len(cluster_dict[center_arr[0]]))
            print("starting cluster_dict: ", cluster_dict)

        # Locate the farthest location from all center points.
        farthest_loc = center_arr[0]
        for center in cluster_dict.keys():
            max_dist = 0
            for cluster_p in cluster_dict[center]:
                dist = distances_copy[center][cluster_p]
                if dist > max_dist:
                    max_dist = dist
                    farthest_loc = cluster_p

        # If the farthest location is not already a center point, set as an additional center point
        if farthest_loc not in center_arr:
            center_arr.append(farthest_loc)
            return self.k_starting_centers(distances_copy, center_arr, i + 1, k)
        else:
            # If the farthest location is already a center point, temporarily set its distance to all points to the centers as -1.
            # This is to guarantee that this point will not be the farthest point another time.
            distances_copy[center_arr[i]][farthest_loc] = -1
            return self.k_starting_centers(distances_copy, center_arr, i, k)


    def clustering(self, k_centers, k, homesBool):
        '''
        Cluster the homes to the closest center (least Euclidean distance).
        :param k_centers: list of center indices of each clusters
        :param k: int value of clusters to create
        :param homesBool: a boolean to determine whether homes or all locations will be clustered
        :return: a dictionary with key being the center index and value being list of location indices belonging to its cluster
        '''

        if debug:
            print("clustering")
        centers_dict = {key: [] for key in k_centers}
        if homesBool:
            # We only want to assign homes to centers
            for i in self.homes: # self.homes is a list
                if i not in k_centers:
                    center_dist = [self.distances[i][j] for j in k_centers]
                    center_index = center_dist.index(min(center_dist))
                    center_for_loc = k_centers[center_index]
                    centers_dict.update(center_for_loc=centers_dict[center_for_loc].append(i))
            centers_dict.pop('center_for_loc', None)
            centers_dict = self.verify_clustering(centers_dict, k)

        else:
            # Clustering method is also used for generating starting k centers wrt all locations
            for i in range(len(self.graph)): # self.graph is a nested list
                if i not in k_centers:
                    center_dist = [self.distances[i][j] for j in k_centers]
                    center_index = center_dist.index(min(center_dist))
                    center_for_loc = k_centers[center_index]
                    centers_dict.update(center_for_loc = centers_dict[center_for_loc].append(i))
            centers_dict.pop('center_for_loc', None)

        return centers_dict


    def verify_clustering(self, centers_dict, k):
        '''
        If a cluster is of size one and the center is not a location, then change center to home
        If a cluster is of size zero, and if center is not a home, then remove cluster. Otherwise, add home center as a cluster point as well.
        :param centers_dict: dictionary with key being center indices and value being list of cluster point indices in center's cluster
        :param k: int value for number of clusters to create
        :return: an updated dictionary with key being the center index and value being list of location indices belonging to its cluster
        '''

        replace_key = {}
        remove_key = {}
        for i in (centers_dict):
            if debug:
                print("i (the key error): ", i)
            if len(centers_dict[i]) == 1:
                if i not in self.homes:
                    home = centers_dict[i][0]
                    replace_key[i] = [home]
            if len(centers_dict[i]) == 0:
                # When a center has no points, delete cluster.
                if i not in self.homes:
                    remove_key[i] = []
                else:
                    centers_dict[i] = [i]

        # For all clusters of size 1 with a center not a home, change center to be the home in cluster.
        for i in replace_key:
            centers_dict.pop(i)
            centers_dict[replace_key[i][0]] = replace_key[i]

        # For all clusters of size 0 with a center not a home, delete cluster.
        for i in remove_key:
            centers_dict.pop(i)

        return centers_dict


    def improved_centers(self, centers_dict):
        '''
        Steps to improve cluster centers:
        1. Get all cluster points in each cluster
        2. Compute the sum of all distances from each location in matrix to all cluster points to all points
        3. Result: list of location's sum of distances
        4. The location with the min sum is the new center of that cluster
        These steps are why the algorithm is called k-median. We essentially identify the Euclidean median using distances, and choose the nearest location to the median to be the new center.
        :param centers_dict: dictionary with key being the center index and value being list of location indices belonging to its cluster
        :return: list of improved center indices
        '''

        new_centers = []
        for center in centers_dict:
            loc_sumdist = [0 for i in range(len(self.graph))]
            for loc in range(len(self.graph)):
                sumdist = 0
                for cluster_p in centers_dict[center]:
                    sumdist += self.distances[loc][cluster_p]
                loc_sumdist[loc] = sumdist
            new_centers.append(loc_sumdist.index(min(loc_sumdist)))

        return new_centers


    def clustering_quality(self, centers_dict):
        '''
        Compute two quantities that describe quality of clusters:
        1. Average of the average sum of distances within each cluster
        2. Dunn Index: To compute the Dunn Index,
             let a = min of (center1 - center2) squared
             let b = max of (sum of distances from center to cluster points)
             Then the dunn_index = max(a/b)
        A larger Dunn Index indicates a higher cluster quality/
        Therefore, for a better quality clustering, we want the smallest distance between centers of different clusters to be as big as possible
        and the diameter of the largest cluster to be as small as possible.
        Dunn Index is stored as a class instance.
        :param centers_dict: dictionary with key being the center index and value being list of location indices belonging to its cluster
        :return: float, Average of the average sum of distances within each cluster (i.e. average of intra-cluster average distance)
        '''
        cluster_avg = [0 for i in range(len(centers_dict))]
        count = 0

        cluster_sums = []
        for center in centers_dict.keys():
            cluster_sum = 0
            for cluster_p in centers_dict[center]:
                cluster_sum += self.distances[center][cluster_p]
            cluster_sums.append(cluster_sum)
            cluster_avg[count] = cluster_sum/len(centers_dict[center])
            count += 1

        sum_avg = 0
        for avg in cluster_avg:
            sum_avg += avg
        avgavgsum_cluster = sum_avg/len(cluster_avg)

        # Compute the Dunn Index
        min_center_diff = math.inf # min_center_diff is denoted as a in the explanation above
        for center1 in centers_dict:
            for center2 in centers_dict:
                if center1 != center2:
                    dist = self.distances[center1][center2]
                    if dist < min_center_diff:
                        min_center_diff = float(dist)
        if debug_k_medians:
            print("min_center_diff: ", min_center_diff)

        max_cluster_diameter = float(max(cluster_sums)) # max_cluster_diameter is denoted as b in the explanation above

        if debug_k_medians:
            print("max_cluster_diameter: ", max_cluster_diameter)
        if max_cluster_diameter == 0: # Only applicable when number of homes == 1
            max_cluster_diameter = 1
        self.dunn_index = min_center_diff/max_cluster_diameter

        if debug_k_medians:
            print("freshly computed self.dunn_index: ", self.dunn_index)

        return avgavgsum_cluster


    def get_min_sum(self):
        return min(self.sumdist_hist)


    def k_medians_clustering(self, centers_dict=None, prev_totalsum=0, curr_totalsum=math.inf, i=1, epsilon=0.5, k_centers=[]):
        '''
        Perform k_medians_clustering to group homes into k clusters with the following steps:
        1. At the first iteration, generate the initial k centers (look at k_starting_centers method for thorough procedure).
            If approximating k, k is obtained by k_trials method to test wide range of k values. Otherwise, use a single value k to create clusters.
        2. Construct clusters using generated k centers.
        3. Compute the average of the average sum of distances (denoted as ___total_sum) within each cluster (i.e. average of intra-cluster average distances)
           as well as the Dunn Index in order to quantify the quality of the clusters generated in Step 2.
        4. Generate improved centers using previously generated clusters.
        5. Repeat steps 2, 3, and 4 with improved centers at each iteration.
           If a new average of intra-cluster average distances is generated, save into archive of all cluster history.
           Otherwise, if this average was previously generated
           or if the difference of previous and currently generated averages are converging to a value less than manually chosen epsilon,
           stop algorithm and return the set of clusters with the minimum average of intra-cluster average distances.
        :param centers_dict: dictionary with key being the center index and value being list of location indices belonging to its cluster
        :param prev_totalsum: float value of average of intra-cluster average distances generated in previous iteration
        :param curr_totalsum: float value of average of intra-cluster average distances generated in current iteration
        :param i: int count of iteration
        :param epsilon: float value to set a limit to which the difference of prev_totalsum and curr_totalsum can converge
        :param k_centers: list of k centers
        :return: list of center indices, dictionary with key of center index and value of corresponding cluster point indices, Dunn Index of the returned clusters
        '''

        if debug_k_medians:
            print("prev_totalsum: ", prev_totalsum)
            print("curr_totalsum: ", curr_totalsum)

        if i > 1:
            # Checking archive if current total sum was already generated in the past (to avoid generating the same centers)
            if curr_totalsum in self.sumdist_hist:
                if debug_k_medians:
                    print("Already saw this total sum in the past. Return best centers from archive.")
                # return the centers of the minimum total sum distance generated
                minsum = self.sumdist_hist[self.sumdist_hist.index(min(self.sumdist_hist))]
                centers = self.sumdist_cent_hist[minsum].copy()
                cl_dict = self.sumdist_cluster_hist[minsum].copy()
                self.sumdist_cluster_hist = {}
                self.sumdist_hist = []
                self.sumdist_cent_hist = {}
                return centers, cl_dict, self.dunn_index
            else:
                if debug_k_medians:
                    print("curr_centers_dict: ", centers_dict)
                    print("storing: ", centers_dict.keys())
                centers = []
                for center in centers_dict:
                    centers.append(center)
                # Store total sum and center points into archive
                self.sumdist_hist.append(curr_totalsum)
                self.sumdist_cent_hist[curr_totalsum] = centers
                self.sumdist_cluster_hist[curr_totalsum] = centers_dict

        # Setting a limit as the average of intra-cluster average distances converge.
        # We choose to set a limit of the converging difference between previous and current qualities obtained.
        # If number of iterations exceed 100, stop algorithm
        if abs(prev_totalsum - curr_totalsum) < epsilon or i > 100:
            minsum = self.sumdist_hist[self.sumdist_hist.index(min(self.sumdist_hist))]
            centers = self.sumdist_cent_hist[minsum].copy()
            cl_dict = self.sumdist_cluster_hist[minsum].copy()
            self.sumdist_cluster_hist = {}
            self.sumdist_hist = []
            self.sumdist_cent_hist = {}
            return centers, cl_dict, self.dunn_index

        # Retrieving potential k values
        k = self.k_potentials[self.ith_k]
        if debug_k_medians:
            print("centers_dict: ", centers_dict)

        # First iteration. Generate initial k centers
        if i == 1:
            center = []
            center.append(self.first_center)
            if k_is_approximated:
                k_centers = self.k_starting_centers(copy.deepcopy(self.distances), center, 0, k)
            else:
                # If choose not to approximate the value k and manually set k values
                if len(self.graph) <= 50:
                    if len(self.graph) == 1 or len(self.graph) == 2:
                        k = int(len(self.graph)/2)
                    else:
                        k = int(len(self.graph)/3)
                elif len(self.graph) <= 100:
                    k = int(len(self.graph)/5.5)
                elif len(self.graph) <= 200:
                    k = int(len(self.graph)/11)
                k_centers = self.k_starting_centers(copy.deepcopy(self.distances), center, 0, k)

        # Cluster homes wrt inital centers
        centers_dict = self.clustering(k_centers, k, True)

        # Compute the average of the average sum of distances within each cluster (i.e. average of intra-cluster average distances)
        new_totalsum = self.clustering_quality(centers_dict)

        if debug_k_medians:
            print("dunn_index", self.dunn_index)

        # Generate improved centers
        new_centers = self.improved_centers(centers_dict)

        return self.k_medians_clustering(centers_dict, curr_totalsum, new_totalsum, i + 1, epsilon, new_centers)


    def approx_best_clustering(self):
        '''
        To approximately find the optimal k number of clusters, run k-medians clustering algorithm to generate k clusters for each potential value k,
        generated in k_trials method.
        The k value with the highest Dunn Index for the generated clusters is the optimal k value.
        :return: list of optimal centers, dictionary with keys being optimal centers and values being a list of corresponding cluster points
        '''
        self.first_center = random.randint(0, len(self.graph) - 1)
        all_clustering = {}
        if debug_approx_k:
            print("self.k_potentials: ", self.k_potentials)
        for i in self.k_potentials:
            if debug_approx_k:
                print("k: ", i)
            centers, centers_dict, dunn_index = self.k_medians_clustering()
            all_clustering[dunn_index] = [centers, centers_dict]
            self.ith_k += 1

        # The bigger the value of Dunn Index, the better the quality of clustering
        max_dunn_index = -1
        best_clustering = []
        for dunn_index in all_clustering:
            if debug_approx_k:
                print("dunn_index(bigger better): ", dunn_index)
            if dunn_index > max_dunn_index:
                max_dunn_index = dunn_index
                best_clustering = all_clustering[dunn_index]
        if debug_approx_k:
            print("\nbest clustering quality(bigger better): ",max_dunn_index)
            print("best clustering: ", best_clustering)
        return best_clustering[0], best_clustering[1]


# Sources:
# Dunn Index: https://cran.r-project.org/web/packages/clusterCrit/vignettes/clusterCrit.pdf
# k-meansclustering (used as guidance for construction k-medians clustering): https://www.analyticsvidhya.com/blog/2019/08/comprehensive-guide-k-means-clustering/
# towardsdatascience.com
# Euclidean Median: https://web.math.princeton.edu/~amits/publications/NLEM.pdf


