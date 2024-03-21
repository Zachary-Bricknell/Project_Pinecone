from tkinter.tix import Tree
import open3d as o3d
import logging
from utils.point_cloud_utils import calculate_diameter_at_height, get_height
from utils.file_operations import get_base_filename
import csv
import math

### Added for log testing, remove when implemented ###
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.file_operations import setup_logging

def processing_stage(filepath, log_path):
    """
    Description:
    Analyzes a tree point cloud to measure the Circumference, to obtain Diameter, at various heights by taking in a point cloud of a cleaned tree taper.
    The heights required are defined by the Ministry of Natural Resources and Forestry. DBH Defined at 1.3 meters, it measures this, and the heights below DBH
    (0.1, 0.5, and 0.9) and then starting from DBH, it calculates the rest of the tree divided into 10 equal segments. 
    Creates a csv file in a directory called ./csv in the same directory filepath is located with the information appended to it in a standardized format of 
    Tree name, Total height, Increment for the cookies above dbh, estimated volume, the height and diameter for the remaining 9 cookies as individual entries each(so 2 for each cookie)
    
    Parameters:
    filepath (str): The file path of the point cloud.
    log_path (str): The path to store log files.
    
    Returns:
    measurements(list of dictionaries): a list of dictionaries denoting height of the measurement ('height') 
        and the diameter ('diameter') at that height. 
    """
    point_cloud = o3d.io.read_point_cloud(filepath)

    base_height, highest_point, total_height = get_height(point_cloud)
    
    # DBH Measurements
    DBH = 1.3 
    under_dbh_height = [0.1, 0.5, 0.9]

    # Above DBH Measurements
    number_of_cookies = 10
    increment_height = (total_height - DBH) / number_of_cookies
    measurements = []
    current_height = base_height + DBH

    base_directory, base_filename, _ = get_base_filename(filepath)
    tree_info = {
        'tree_name': base_filename,
        'tree_height': total_height,
        'increment': increment_height,
        'taper volume': 0  
    }

    # Below DBH
    for height in under_dbh_height:
        diameter = calculate_diameter_at_height(point_cloud, base_height + height)
        measurements.append([height, diameter])

    # From DBH upward
    for _ in range(number_of_cookies):
        diameter = calculate_diameter_at_height(point_cloud, current_height)
        measurements.append([current_height - base_height, diameter])
        current_height += increment_height

    # Calculate volume based on the previous measurments using volume of a cone for each segment, and appending the results
    total_volume = 0
    for i in range(1, len(measurements)):
        height1, diameter1 = measurements[i - 1]
        height2, diameter2 = measurements[i]
        h = height2 - height1
       
        r1 = diameter1 / 2
       
        r2 = diameter2 / 2

        volume = (1/3) * math.pi * h * (r1**2 + r1*r2 + r2**2)
        round(volume,2)
        total_volume += volume
        
    tree_info['taper volume'] = total_volume

    # Prepare row data for CSV output
    row_data = [
        tree_info['tree_name'],
        tree_info['tree_height'],
        tree_info['increment'],
        tree_info['taper volume']
    ]
    # Add measurements to the row data
    for measurement in measurements:
        row_data.extend(measurement)
   
    headers = ['tree_name', 'tree_height', 'increment', 'volume']
    for i in range(1, len(row_data) // 2): 
        headers.extend([f'height_{i}', f'diameter_{i}'])
    
    # Write a csv to a new (or existing) directory called /csv
    csv_directory = base_directory + "/csv"
    if not os.path.exists(csv_directory):
        os.makedirs(csv_directory)        
    csv_filename = os.path.join(csv_directory, base_filename + ".csv")
    
    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)  
        writer.writerow(row_data)
        
    return csv_filename