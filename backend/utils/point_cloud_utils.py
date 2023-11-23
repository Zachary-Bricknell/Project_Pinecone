import os
import open3d as o3d
import numpy as np



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

def save_processed_file(directory, filename, point_cloud):
    processed_directory = os.path.join(directory, "processed")
    if not os.path.exists(processed_directory):
        os.makedirs(processed_directory)

    processed_file_path = os.path.join(processed_directory, f'pineconed_{filename}.ply')
    o3d.io.write_point_cloud(processed_file_path, point_cloud)
    return processed_file_path

