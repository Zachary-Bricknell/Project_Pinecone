import argparse
import os
import shutil
from utils.point_cloud_utils import visualize_point_cloud
from point_cloud_processor import process_point_cloud

def main(args):
    original_path = args.path
    processed_file_path = None

    # If --process is called, copy the file into the destination folder if specified, or a folder called 'pinecone'
    if args.process:
        destination_directory = args.destination if args.destination else os.path.join(os.path.dirname(original_path), "pinecone")

        # Create the destination directory if it not exist
        if not os.path.exists(destination_directory):
            os.makedirs(destination_directory)

        # Copy the file into the destination directory
        filename = os.path.basename(original_path)
        destination_path = os.path.join(destination_directory, filename)
        shutil.copyfile(original_path, destination_path)

        # Process the point cloud using the path to the copied file, retaining the original datas integrity. 
        processed_file_path = process_point_cloud(destination_path, destination_directory)
        print(f"Processed point cloud saved as: {processed_file_path}")

    # Visualize the point cloud, prioritizing the processed file if available, checkes if --processed was called previously which produced a definition for processed_file_path
    if args.visualize:
        path_to_visualize = processed_file_path if processed_file_path else original_path
        visualize_point_cloud(path_to_visualize)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process and/or visualize point cloud files.")
    parser.add_argument("path", help="Path to the point cloud file")
    parser.add_argument("--destination", help="Destination directory for processed files", default=None)
    parser.add_argument("--process", action="store_true", help="Process the point cloud")
    parser.add_argument("--visualize", action="store_true", help="Visualize the point cloud")
    args = parser.parse_args()
    main(args)
