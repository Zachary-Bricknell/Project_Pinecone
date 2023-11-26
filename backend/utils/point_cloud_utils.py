import os
import open3d as o3d
import numpy as np


<<<<<<< HEAD
# main processing code, Currently just preprocessing
=======

>>>>>>> main
def process_point_cloud(point_cloud, nb_neighbors=15, std_ratio=1.0, radius=0.05, voxel_size=0.02):
    # Statistical Outlier Removal
    try:
        print("Removing Statistical Outliers.")
        _, ind = point_cloud.remove_statistical_outlier(nb_neighbors=nb_neighbors, std_ratio=std_ratio)
        point_cloud = point_cloud.select_by_index(ind)
        print("Statistical Outliers removed.")
    except Exception as e:
        print(f"Failed to remove Statistical Outliers: {e}")

    # # Radius Outlier Removal (Still testing)
    # try:
    #     _, rad_ind = point_cloud.remove_radius_outlier(nb_points=nb_neighbors, radius=radius)
    #     point_cloud = point_cloud.select_by_index(rad_ind)
    #     print("Radius Outliers removed.")
    # except Exception as e:
    #     print(f"Failed to remove Radius Outliers: {e}")

    # Voxel Downsampling
    try:
        print("Voxel Downsampling.")
        point_cloud = point_cloud.voxel_down_sample(voxel_size=voxel_size)
        print("Voxel Downsampling completed.")
    except Exception as e:
        print(f"Failed to Voxel Downsample: {e}")

    return point_cloud

<<<<<<< HEAD
#Saving the point cloud to a directory called processed, witht he file getting the prefix `pineconed_` 
=======
>>>>>>> main
def save_processed_file(directory, filename, point_cloud):
    processed_directory = os.path.join(directory, "processed")
    if not os.path.exists(processed_directory):
        os.makedirs(processed_directory)

    processed_file_path = os.path.join(processed_directory, f'pineconed_{filename}.ply')
    o3d.io.write_point_cloud(processed_file_path, point_cloud)
    return processed_file_path

<<<<<<< HEAD
# Visualize the point cloud
def visualize_point_cloud(path):
    point_cloud = o3d.io.read_point_cloud(path)
    if point_cloud is None:
        raise ValueError("Could not read point cloud for visualization.")

    vis = o3d.visualization.Visualizer()
    vis.create_window()
    vis.add_geometry(point_cloud)
    vis.run()
    vis.destroy_window()
=======
>>>>>>> main
