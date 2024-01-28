import argparse
import os
import shutil
import sys

# Add the backend directory to sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
    
from utils.point_cloud_utils import visualize_point_cloud
from point_cloud_processor import steps_to_process_point_cloud

# Function to process the point cloud
def process(original_path, destination_directory):
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    filename = os.path.basename(original_path)
    destination_path = os.path.join(destination_directory, filename)

    shutil.copyfile(original_path, destination_path)

    processed_point_cloud = steps_to_process_point_cloud(destination_path, destination_directory)

    return processed_point_cloud

# Function to visualize the point cloud
def visualize(path_to_visualize):
    visualize_point_cloud(path_to_visualize)

# Function to process and then visualize the point cloud
def process_and_visualize(original_path, destination_directory):
    processed_file_path = process(original_path, destination_directory)
    visualize(processed_file_path)

def main():
    parser = argparse.ArgumentParser(description="Process and/or visualize point cloud files.")
    parser.add_argument("path", help="Path to the point cloud file")
    parser.add_argument("--destination", help="Destination directory for processed files", default=None)
    parser.add_argument("--process", action="store_true", help="Process the point cloud")
    parser.add_argument("--visualize", action="store_true", help="Visualize the point cloud")
    args = parser.parse_args()

    destination_directory = args.destination if args.destination else os.path.join(os.path.dirname(args.path), "pinecone")

    if args.process and not args.visualize:
        process(args.path, destination_directory)
    elif args.visualize and not args.process:
        visualize(args.path)
    elif args.process and args.visualize:
        process_and_visualize(args.path, destination_directory)

if __name__ == "__main__":
    main()