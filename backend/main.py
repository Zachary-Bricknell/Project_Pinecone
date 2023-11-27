<<<<<<< HEAD
import argparse
=======
<<<<<<< HEAD
import argparse
import os
from utils.file_operations import read_point_cloud
from utils.point_cloud_utils import process_point_cloud, save_processed_file, visualize_point_cloud


def main(args):
    path = args.path
    point_cloud = read_point_cloud(path)

    if point_cloud is None:
        print("Failed to read point cloud, no data.")
        return
=======
import os
import open3d as o3d
import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering
import numpy as np
import matplotlib.pyplot as plt
>>>>>>> 13a3050bf4deec8a16364a06bf0121f58345a880
from utils.file_operations import read_point_cloud
from utils.point_cloud_utils import process_point_cloud, save_processed_file, visualize_point_cloud


def main(args):
    path = args.path
    point_cloud = read_point_cloud(path)

    if point_cloud is None:
<<<<<<< HEAD
        print("Failed to read point cloud, no data.")
        return
=======
        return None
>>>>>>> main
>>>>>>> 13a3050bf4deec8a16364a06bf0121f58345a880

    filename = os.path.splitext(os.path.basename(path))[0]
    directory = os.path.dirname(path)

<<<<<<< HEAD
    # if --processed
=======
<<<<<<< HEAD
>>>>>>> 13a3050bf4deec8a16364a06bf0121f58345a880
    if args.process:
        point_cloud = process_point_cloud(point_cloud)
        processed_file_path = save_processed_file(directory, filename, point_cloud)
        print(f"Processed point cloud saved as: {processed_file_path}")
        path = processed_file_path  # Update path to processed file for visualization
<<<<<<< HEAD
    # if --visualize
    if args.visualize:
        visualize_point_cloud(path)
=======

    if args.visualize:
        visualize_point_cloud(path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process and/or visualize point cloud files.")
    parser.add_argument("path", help="Path to the point cloud file")
    parser.add_argument("--process", action="store_true", help="Process the point cloud file")
    parser.add_argument("--visualize", action="store_true", help="Visualize the point cloud file")
    args = parser.parse_args()

    main(args)
=======
    if filename.startswith('pineconed_') or os.path.basename(directory) == "processed":
        return None

    point_cloud = process_point_cloud(point_cloud)
    processed_file_path = save_processed_file(directory, filename, point_cloud)
    return processed_file_path
>>>>>>> 13a3050bf4deec8a16364a06bf0121f58345a880

# Defines what each argument will call. 
if __name__ == "__main__":
<<<<<<< HEAD
    parser = argparse.ArgumentParser(description="Process and/or visualize point cloud files.")
    parser.add_argument("path", help="Path to the point cloud file")
    parser.add_argument("--process", action="store_true", help="Process the point cloud file")
    parser.add_argument("--visualize", action="store_true", help="Visualize the point cloud file")
    args = parser.parse_args()

    main(args)
=======
    app = PointCloudApp(width=1024, height=768)
    app.run()
>>>>>>> main
>>>>>>> 13a3050bf4deec8a16364a06bf0121f58345a880
