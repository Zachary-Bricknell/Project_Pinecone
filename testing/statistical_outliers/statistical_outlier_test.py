import open3d as o3d
import numpy as np

# Return the number of points removed from statistical outlier removal
def statistical_outlier_removal(pcd, nb_neighbors, std_ratio):
    original_num_points = len(pcd.points)
    _, ind = pcd.remove_statistical_outlier(nb_neighbors=nb_neighbors, std_ratio=std_ratio)
    inlier_cloud = pcd.select_by_index(ind)
    num_points_removed = original_num_points - len(inlier_cloud.points)
    return num_points_removed

# Load a PLY point cloud file
pcd = o3d.io.read_point_cloud('../resources/sample_data/sample1.ply')

# Parameters to iterate over
nb_neighbors_range = range(10, 30)  # From 1 to 10
std_ratio_range = np.arange(1.0, 3.0, 0.1)  # From 1.0 to 2.0 in steps of 0.1

# Array to store results
results = np.zeros((len(nb_neighbors_range), len(std_ratio_range)))

# Iterate over the parameters and compute the number of points removed
for i, nb_neighbors in enumerate(nb_neighbors_range):
    for j, std_ratio in enumerate(std_ratio_range):
        num_points_removed = statistical_outlier_removal(pcd, nb_neighbors, std_ratio)
        results[i, j] = num_points_removed

# Print to console and also save a copy of the results in the PWD
np.savetxt("outlier_removal_results.txt", results, fmt='%d')
print(results)
