from datetime import datetime
from utils.file_operations import modify_filename, setup_logging
from utils.point_cloud_utils import get_current_step
from stages.point_cloud_cleaning_stage import cleaning_stage
from stages.point_cloud_preprocessing_stage import preprocessing_stage
from utils.db_utils import import_to_db, link_scan_to_tree, get_db_connection
from utils.config import STAGE_PREFIXES, DB_CRED
import os
import open3d as o3d
import logging


def steps_to_process_point_cloud(filepath, log_path, upload_flag):
    """
    Parameters:
    filepath (str): Path to the point cloud file to be processed.
    log_path (str): Path to the directory where logs should be stored.

    Returns:
    str: Path to the processed point cloud file if all stages complete successfully.
    None: If processing is incomplete due to a stage not completing or an error.
    
    Description:
    Processes a point cloud file sequentially through defined stages.
    The function identifies the current stage based on the file's naming convention, then applies the appropriate
    processing functions for each stage in sequence. If a stage completes successfully, the file is prepared for the next stage.
    Processing halts if a stage fails to complete or an error occurs.
    
    Notes:
    Acts as the driver code for --process, where main.py currently defines all argparse functions
    """
    
    new_filepath = filepath
    stage, current_step = get_current_step(filepath)
    stage_index = next((index for index, (name, _) in enumerate(STAGE_PREFIXES) if name == stage), 0)

    # Called the base name of the file being processed to easily reference. 
    log_filename = os.path.splitext(os.path.basename(filepath))[0]
    setup_logging(log_filename, log_path)

    for index in range(stage_index, len(STAGE_PREFIXES)):
        print(index)
        step_complete = False  # default for each iteration
        stage_name, stage_prefix = STAGE_PREFIXES[index]
        try:
            # Process the point cloud based on the current stage
            if stage_name == STAGE_PREFIXES[0][0]:
                new_filepath, step_complete = cleaning_stage(new_filepath, current_step, stage_prefix, log_path)
                geometry_col_name = "cleaned_scan"
                scan_type = "cleaned_tree_id"
                table_name = "cleaned_tree"
            elif stage_name == STAGE_PREFIXES[1][0]:
                new_filepath, step_complete = preprocessing_stage(new_filepath, current_step, stage_prefix, log_path)
                geometry_col_name = "preprocessed_scan"
                scan_type = "preprocessed_tree_id"
                table_name = "preprocessed_tree"
            

            if step_complete and upload_flag:
                # Upload logic
                additional_data = {"created": datetime.now()}
                scan_id = import_to_db(new_filepath, table_name, geometry_col_name, additional_data)
                tree_name = os.path.splitext(os.path.basename(new_filepath))[0][:-4]
                link_scan_to_tree(tree_name, scan_id, scan_type)
                logging.info(f"{stage_name.capitalize()} scan uploaded and linked: {scan_id} for tree {tree_name}")

            if not step_complete:
                print(f"Stage '{stage_name}' did not complete")
                break

            if index + 1 < len(STAGE_PREFIXES):
                next_stage_prefix = STAGE_PREFIXES[index + 1][1]
                new_filepath = modify_filename(new_filepath, next_stage_prefix, "0")
                current_step = 0

        except Exception as e:
            # Handle any exceptions during the processing of the current stage
            print(f"An error occurred during the '{stage_name}' stage: {e}")
            return None
        
    return new_filepath
    