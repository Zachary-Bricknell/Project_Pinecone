import os
import open3d as o3d
import numpy as np
from sklearn.ensemble import IsolationForest
import time
from stages.point_cloud_cleaning_stage import *



def remove_outliers_isolation_forest(point_cloud, contamination=0.12):
    """
Parameters:
<point_cloud> (open3d.geometry.PointCloud): the points that exist in the xyz file
<contamination> (float): expected proportion of anomalies (outliers) in the data

Returns:
<point_cloud> (open3d.geometry.PointCloud): this is updated point cloud that has the noise removed

Description:
In this function crucial step is made, where isolation forest algorithm kick in which ensures
the quality of removed points and the accuracy is configured for the results that are close to the best
using this algorithm we make sure we are removing the outliers this is machine learning algorithm 
whcih ensures that it does its job what it was trained for.
Using the IsolationForest Algorithm to remove the outliers
#it can be tuned as you wish, you can update the contamination which will indicate how hard it will go on the things, anomalies like if you will
#Put it to 0.5 it might skip the points that are needed and count it as an anomalies
# the bigger the tree has outliers number should be tuned accordingly for the best results.
"""
    xyz = np.asarray(point_cloud.points)
    model = IsolationForest(contamination=contamination)
    model.fit(xyz)
    outliers = model.predict(xyz)
    inliers_mask = outliers > 0
    point_cloud = point_cloud.select_by_index(np.where(inliers_mask)[0])

    return point_cloud





def keep_only_largest_cluster_DBSCAN(point_cloud, eps=0.05, min_points=10):
    """
Parameters:
<point_cloud> (open3d.geometry.PointCloud): point cloud file
<eps> (float): (epsilon) is a distance parameter that defines the maximum 
distance between two data points in the neighborhood of each other.
<min_points> (int): this is the number what we would consider as a cluster minimum number 

Returns:
<point_cloud.select_by_index(largest_cluster_indices)> (index): returns the largest cluster available

Description:
DBSCAN Clustering
I'm utilizing numpy's bincount to count points in each cluster. 
Then, I use np.argmax to identify the largest cluster and save it. 
I discard smaller clusters outside the main one. This step ensures 
the tree remains the primary cluster in the isolation forest algorithm.
"""
    # Perform DBSCAN clustering
    labels = np.array(point_cloud.cluster_dbscan(eps=eps, min_points=min_points, print_progress=True))

    # Find the index of the largest cluster
    largest_cluster_idx = np.argmax(np.bincount(labels[labels >= 0]))
    print(f"Only keeping the largest cluster: {largest_cluster_idx}")

    # Keep only the points that are part of the largest cluster
    largest_cluster_indices = np.where(labels == largest_cluster_idx)[0]

    return point_cloud.select_by_index(largest_cluster_indices)



def preprocessing_stage(filepath, current_step, stage_prefix, num_iterations=12):
    """
Parameters:
filepath (str): The file path of the input point cloud.
current_step (int): The current step in the preprocessing process.
stage_prefix (str): The prefix of the current step.
num_iterations (int): The number of iterations for machine learning-based outlier removal.

Returns:
filepath (str): The file path of the final processed point cloud.
success (bool): True if the preprocessing is successful, False otherwise.

Description:
This function preprocesses a point cloud by iteratively removing outliers using the Isolation Forest algorithm.
After the iterations, it eliminates small clusters using DBSCAN clustering. 
The function also measures the total execution time, prints it, 
and saves the final processed point cloud to a specified file path. The function returns the file path.
  """
    point_cloud = o3d.io.read_point_cloud(filepath)
    
    # Applying machine learning-based outlier removal iteratively 
    startTime = time.time()
    for iteration in range(num_iterations):
        try:
            print(f"Iteration {iteration + 1}: Removing Machine Learning Outliers.")
            point_cloud = remove_outliers_isolation_forest(point_cloud)
            print("Machine Learning Outliers removed.")
        except Exception as e:
            print(f"Failed to remove Machine Learning Outliers: {e}")

    # After the previous step, we need something that will remove the clusters that are left, I am thinking of DBSCAN clustering which shows the amazing results.
    try:
        print("Removing small clusters that may represent nodes.")
        point_cloud = keep_only_largest_cluster_DBSCAN(point_cloud)
        print("Small clusters removed.")
    except Exception as e:
        print(f"Failed to remove small clusters: {e}")

    endTime = time.time()
    totalTime = endTime - startTime
    print(f"total time needed for the whole process is: {totalTime}")

    # Save the final processed point cloud
    o3d.io.write_point_cloud(filepath, point_cloud)

    return filepath, True