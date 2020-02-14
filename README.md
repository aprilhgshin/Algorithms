# Drop off TA's Home Project
This algorithm implements a NP-hard problem of generating the optimal path that minimizes the total energy cost. As each TA is dropped off at a drop off location or their home, we aim to minimize the total energy expended from driving each TA to a location and TA's walking from a drop off location to their homes. For each unit distance, driving uses 2/3 the energy used by a walking TA.

## Instructions
To use the algorithm, simply import "algorithm" from TSP.
This is the DTH-algorithm, it will work by itself.
However, you will need the following modules to run it:
- tspy

PS: On one of our machines will not run the tspy module, giving an error in scipy.
For the one of us for which it works, we are using python 3.6.3

This library is installable trough pip.
"pip install tspy"

All you have to do is provide the algorithm with a input-file and a output-file,
like this: algorithm(input_file, output_file).

The algorithm is assuming that the input_file is a valid input-file as described in the project specification.
When called, the algorithm will do it's magic and write it's suggested solution as an output-file to the provided
output-file-path provided as a parameter.



## How does the algorithm work?
The algorithm should be provided with two parameters, paths for an input file and an output file. 
The first step on the way to deciding a good drop-off strategy for the input file is clustering the homes in the graph. 

#### K-Medians Clustering Algorithm (with approximated k):
We create the K_Medians_Cluster class to generate k number of clusters of homes using an approximated k to optimize the clustering i.e. obtain a high Dunn Index. <br/>
For each cluster Cn , where n ≤ N and N is the number of clusters, define the Dunn Index as: <br/>

<p align="center">
  Dunn Index = max (dist(ci , cj)) / min (diam(Cn))
</p>

for 1 ≤ i, j ≤ N and ci is a center of Ci  and cj is a center of Cj. <br/>
A larger Dunn Index indicates a higher cluster quality. Therefore, for a better quality clustering, we want the smallest distance between centers of different clusters to be as big as possible
and the diameter of the largest cluster to be as small as possible. In essence, we aim to maximize the amount of TA's we can drop off in each drop-off location while minimizing the distance they walk and the distance Rao drives. 
Then follow the procedure:
Initialize a set of potential k values to generate various numbers of clusters with possibly differing Dunn Index values (at each incrementing interval from 1 to number of homes, choose the midpoints to the potential values of k).
Compute the distance between every location using dijkstra.
Choose k starting centers by starting with a random location and choose next set of centers to be the farthest location from all previously chosen centers.
Perform k medians clustering to group homes into k clusters with the following steps:
1. At the first iteration, generate the initial k centers. As we are approximating k, k_trials method to test a wide range of k values. <br/>
2. Construct clusters using the k center points by setting each home to the closest center. 
Verify  validity of clusters by making sure every cluster contains a home. Otherwise, discard the cluster. Additionally, if a cluster is of size 1 and its center is not a home, then change the center to be the home. <br/>
3. Compute average of intra-cluster average distances i.e. the average of the average sum of distances within each cluster as well as the Dunn Index in order to quantify the quality of the clusters generated in Step 2. <br/>
4. Generate improved centers using previously generated clusters by identifying the Euclidean median of each cluster using distances, and choosing the nearest location to the median to be the new center - hence k-medians clustering.
Repeat steps 2, 3, and 4 with improved centers at each iteration.
However, if a new average of intra-cluster average distances is generated, save into archive of all cluster history. Otherwise, if this average was previously generated or if the difference of previous and currently generated averages are converging to a value less than manually chosen epsilon, stop the algorithm and return the set of clusters with the minimum average of intra-cluster average distances.
As the aim is to generate the optimal k number of clusters, run k-medians clustering algorithm to generate k clusters for each potential value k.
The k value with the highest Dunn Index for the generated clusters is the best approximated k value. Ultimately, we obtain a k clusters with an approximated k to yield a highest Dunn Index.

#### TSP (with additions)
Since we have clustered using k-medians, the idea is that we can use the clusters as an initial idea of what our path should be. Since the centers should not be too far away from its surrounding nodes (the homes in this case), it shouldn't be too far to walk for the TA’s if they are dropped off at the cluster-center for the cluster containing their home. 
Since the cluster-centers are serving as reference-points for our path, we also add our starting point to the cluster-centers, if it not already is one, as the path need to contain this point. The algorithm then calculates the distance between the centers using dijkstras, and then uses a tsp-approximation algorithm (pip library tspy) to find the optimal route in the graph that visits all cluster-centers at least once. The algorithm then modifies the suggested TSP-tour to make sure that we start and end at the starting location provided in the input. The car will not deviate from this suggested tour during its run. Finally, to determine where to drop off the different TA's, the algorithm analyzes all the nodes that the car will be visiting on it's tour, and decides what TA's is optimal to drop off at any node. After the algorithm has decided on its path for traversal and its drop-off locations, it proceeds to write the results to the specified output file. 


April Shin, Fredrik Waaler <br/>
CS 170 Algorithms <br/>
UC Berkeley
