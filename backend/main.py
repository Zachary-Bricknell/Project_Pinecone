import argparse
from utils.file_operations import read_point_cloud
from utils.point_cloud_utils import process_point_cloud, save_processed_file, visualize_point_cloud


def main(args):
    path = args.path
    point_cloud = read_point_cloud(path)

    if point_cloud is None:
        print("Failed to read point cloud, no data.")
        return

    filename = os.path.splitext(os.path.basename(path))[0]
    directory = os.path.dirname(path)

    # if --processed
    if args.process:
        point_cloud = process_point_cloud(point_cloud)
        processed_file_path = save_processed_file(directory, filename, point_cloud)
        print(f"Processed point cloud saved as: {processed_file_path}")
        path = processed_file_path  # Update path to processed file for visualization
    # if --visualize
    if args.visualize:
        visualize_point_cloud(path)

# Defines what each argument will call. 
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process and/or visualize point cloud files.")
    parser.add_argument("path", help="Path to the point cloud file")
    parser.add_argument("--process", action="store_true", help="Process the point cloud file")
    parser.add_argument("--visualize", action="store_true", help="Visualize the point cloud file")
    args = parser.parse_args()

    main(args)
