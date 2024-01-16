# Preprocessing goes here, default text to update in git
import os
import open3d as o3d
import numpy as np
from sklearn.ensemble import IsolationForest
import time
from stages.point_cloud_cleaning_stage import *

#DBSCAN Clustering
#In here I am using the np,bincount to count the number of the points in each cluster that exists
#Then I am using the np.argmax to find the largest from these clusters and then using this cluster saving it and removing all the other small clusters that might
#be wondering outside the tree, these ensures that the tree will be the only main cluster

def keep_only_largest_cluster(point_cloud, eps=0.05, min_points=10):
    # Perform DBSCAN clustering
    labels = np.array(point_cloud.cluster_dbscan(eps=eps, min_points=min_points, print_progress=True))

    # Find the index of the largest cluster
    largest_cluster_idx = np.argmax(np.bincount(labels[labels >= 0]))
    print(f"Only keeping the largest cluster: {largest_cluster_idx}")

    # Keep only the points that are part of the largest cluster
    largest_cluster_indices = np.where(labels == largest_cluster_idx)[0]

    return point_cloud.select_by_index(largest_cluster_indices)

#Using the IsolationForest Algorithm to remove the outliers
#it can be tuned as you wish, you can update the contamination which will indicate how hard it will go on the things, anomalies like if you will
#Put it to 0.5 it might skip the points that are needed and count it as an anomalies, the bigger the tree has outliers number should be tuned accordingly for the best results.
def remove_noise_ml(point_cloud, contamination=0.12):
    xyz = np.asarray(point_cloud.points)
    model = IsolationForest(contamination=contamination)
    model.fit(xyz)
    outliers = model.predict(xyz)
    inliers_mask = outliers > 0
    point_cloud = point_cloud.select_by_index(np.where(inliers_mask)[0])

    return point_cloud


def preprocessing_stage(filepath, current_step, stage_prefix, num_iterations=12):
    point_cloud = o3d.io.read_point_cloud(filepath)
    
    # Applying machine learning-based outlier removal iteratively 
    startTime = time.time()
    for iteration in range(num_iterations):
        try:
            print(f"Iteration {iteration + 1}: Removing Machine Learning Outliers.")
            point_cloud = remove_noise_ml(point_cloud)
            print("Machine Learning Outliers removed.")
        except Exception as e:
            print(f"Failed to remove Machine Learning Outliers: {e}")

    # After the previous step, we need something that will remove the clusters that are left, I am thinking of DBSCAN clustering which shows the amazing results.
    try:
        print("Removing small clusters that may represent nodes.")
        point_cloud = keep_only_largest_cluster(point_cloud)
        print("Small clusters removed.")
    except Exception as e:
        print(f"Failed to remove small clusters: {e}")

    endTime = time.time()
    totalTime = endTime - startTime
    print(f"total time needed for the whole process is: {totalTime}")

    # Save the final processed point cloud
    o3d.io.write_point_cloud(filepath, point_cloud)

    return filepath, True