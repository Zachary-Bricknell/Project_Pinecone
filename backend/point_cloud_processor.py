from turtle import setup
from backend.stages.point_cloud_processing_stage import processing_stage
from utils.file_operations import modify_filename, setup_logging, get_base_filename
from utils.point_cloud_utils import get_current_stage
from stages.point_cloud_cleaning_stage import cleaning_stage
from stages.point_cloud_preprocessing_stage import preprocessing_stage
from utils.config import STAGE_PREFIXES
from utils.db_utils import import_to_db, link_scan_to_tree  
import logging
import open3d as o3d
from datetime import datetime  # Required for timestamping uploads


def extract_tree_taper(filepath, log_path, upload_flag=False):
    """
    Description:
    Processes a point cloud file sequentially through defined stages.
    The function identifies the current stage based on the file's naming convention, then applies the appropriate
    processing functions for each stage in sequence. If a stage completes successfully, the file is prepared for the next stage.
    Processing halts if a stage fails to complete or an error occurs. Updates the filename on success to denote preprocessiong completion. 
    
    Parameters:
    filepath (str): Path to the point cloud file to be processed.
    log_path (str): Path to the directory where logs should be stored.
    upload_flag (bool): upload_flag (bool): If True, uploads the original scan to the 'raw_lidar' table, the cleaned scan to the 'cleaned_tree' table, and the preprocessed scan to the 'preprocessed_tree' table in the database. Each upload is linked to a tree entry.
    
    Returns:
    str: Path to the processed point cloud file if all stages complete successfully.
    None: If processing is incomplete due to a stage not completing or an error.
    """
    _, base_filename, _ = get_base_filename(filepath)
    setup_logging(base_filename, log_path)
    stages_map = {
        'cleaning': cleaning_stage,
        'preprocessing': preprocessing_stage,
    }

    initial_stage = get_current_stage(filepath)
    logging.info(f"Initial processing stage: {initial_stage}")
    if initial_stage == STAGE_PREFIXES[-1][0]:
        return filepath
    # Before starting any processing, upload the original file to raw_lidar if upload_flag is True
    if upload_flag:
        additional_data = {"created": datetime.now()} # Timestamp of when it is uploaded
        scan_id = import_to_db(filepath, "raw_lidar", "raw_scan", additional_data)
        tree_name = base_filename  # Get the tree name
        link_scan_to_tree(tree_name, scan_id, "raw_lidar_id")
        logging.info(f"Original scan uploaded: {scan_id} for tree {tree_name}")
    for stage_name, _ in STAGE_PREFIXES:
        if stage_name == "processing":
            continue
        if stage_name in stages_map:
            logging.info(f"Checking stage: {stage_name}")

            # Check if it is the current stage, or next stage to be completed
            if initial_stage == stage_name or initial_stage == "new" or initial_stage == "":
                logging.info(f"Starting stage: {stage_name}")
                
                try:
                    stage_function = stages_map[stage_name]
                    filepath, process_success = stage_function(filepath, log_path)
                    if not process_success:
                        logging.error(f"Stage '{stage_name}' did not complete successfully.")
                        return None
                    # After cleaning, upload the cleaned scan to cleaned_tree if upload_flag is True
                    if upload_flag and stage_name == "cleaning":
                        additional_data = {"created": datetime.now()} # Timestamp of when it is uploaded
                        scan_id = import_to_db(filepath, "cleaned_tree", "cleaned_scan", additional_data)
                        link_scan_to_tree(tree_name, scan_id, "cleaned_tree_id")
                        logging.info(f"Cleaned scan uploaded and linked: {scan_id} for tree {base_filename}")
                    # After preprocessing, upload the preprocessed scan to preprocessed_tree if upload_flag is True
                    if upload_flag and stage_name == "preprocessing":
                        additional_data = {"created": datetime.now()} # Timestamp of when it is uploaded
                        scan_id = import_to_db(filepath, "preprocessed_tree", "preprocessed_scan", additional_data)
                        link_scan_to_tree(tree_name, scan_id, "preprocessed_tree_id")
                        logging.info(f"Preprocessed scan uploaded and linked: {scan_id} for tree {base_filename}")
                except Exception as e:
                    logging.error(f"An error occurred during the '{stage_name}' stage: {e}")
                    return None                
            # Flag to continue to the next stages
            initial_stage = "new"
            
        else:
            logging.error(f"No processing function defined for stage '{stage_name}'")

    logging.info("Processing completed for all stages.")
    new_filepath = modify_filename(filepath, STAGE_PREFIXES[-1][1])
    return new_filepath