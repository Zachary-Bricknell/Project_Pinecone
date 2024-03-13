import argparse
import os
import shutil
import sys

# Add the backend directory to sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
    
from utils.point_cloud_utils import point_cloud_visualizer
from utils.file_operations import find_processed_file
from point_cloud_processor import extract_tree_taper
from stages.point_cloud_processing_stage import processing_stage

def process(original_path, destination_directory):
    """
    Description:
    This function will process a raw point cloud of a specified tree, resulting in a tree taper of that tree
    and performing calculations at pre-defined heights, standardized by the Ministry of Natural Resources and Forestry.
    The processed point cloud is saved in the destination directory. 
    
    Parameters:
    original_path (str): The path to the point cloud that is to be processed
    destination_directory(str): The destination directory to save the new processed point cloud
    
    Return:
    point_cloud_metrics(List): A list of dictionaries containing the metrics derived from the tree taper
    processed_point_cloud (str): The filepath of the processed point cloud 
    """
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    filename = os.path.basename(original_path)
    
    existing_file = find_processed_file(filename, destination_directory)
    if existing_file is None:
        destination_path = os.path.join(destination_directory, filename)

        shutil.copyfile(original_path, destination_path)
    else:
        #A existing file is in the destination, so update to reference that one, effectively skipping steps that have been done. 
        destination_path = existing_file

    processed_point_cloud = extract_tree_taper(destination_path, destination_directory)
    point_cloud_metrics = processing_stage(processed_point_cloud, destination_directory)
    return point_cloud_metrics, processed_point_cloud

# Function to visualize the point cloud
def visualize_point_cloud(path_to_visualize, original_path = None):
    """
    Description:
    Calls the point_cloud_visualizer() to draw and visualize an open3d object. Visualizes the point cloud,
    or a visualization of both the original point cloud, and the processed point cloud in a single window.
    
    Parameters:
    path_to_visualize (str): The path to the processed point cloud
    original_path (str, Default: None): The path to the original point cloud 
    """
    point_cloud_visualizer(path_to_visualize, original_path)

# Function to process and then visualize the point cloud
def process_and_visualize(original_path, destination_directory):
    """
    Description:
    Processes a point cloud by calling process() and than visualizes both the original and the processed point cloud
    calling visualize() after.
    
    Parameters:
    original_path (str): The path to the point cloud to be processed
    destination_directory (str): The path to the destination directory to save the processed point cloud
    """
    starting_point_cloud = original_path
    point_cloud_metrics, processed_file_path = process(original_path, destination_directory)
    visualize_point_cloud(processed_file_path, starting_point_cloud)
    return point_cloud_metrics

def main():
    """
    Description:
    Original definition of using argparse to pass values between the front and backend.
    No longer used but retained for reference/testing.
    """
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
        visualize_point_cloud(args.path)
    elif args.process and args.visualize:
        process_and_visualize(args.path, destination_directory)

if __name__ == "__main__":
    main()