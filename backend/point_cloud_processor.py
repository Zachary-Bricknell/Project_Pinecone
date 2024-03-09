from utils.file_operations import modify_filename, setup_logging
from utils.point_cloud_utils import get_current_step
from stages.point_cloud_cleaning_stage import cleaning_stage
from stages.point_cloud_preprocessing_stage import preprocessing_stage
from utils.config import STAGE_PREFIXES
import os
import open3d as o3d

def extract_tree_taper(filepath, log_path):
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
    stages_map = {
        'cleaning': cleaning_stage,
        'preprocessing': preprocessing_stage
    }
    
    new_filepath = filepath
    stage, current_step = get_current_step(filepath)
    if stage == "_PC":
        return filepath # Already Preprocessed
    
    stage_index = next((index for index, (name, _) in enumerate(STAGE_PREFIXES) if name == stage), 0)

    # Called the base name of the file being processed to easily reference. 
    log_filename = os.path.splitext(os.path.basename(filepath))[0]
    setup_logging(log_filename, log_path)

    stage_index = next((index for index, s in enumerate(STAGE_PREFIXES) if s[0] == stage), None)

    if stage_index is None:
        print(f"Unknown stage: {stage}")
        return None

    for index in range(stage_index, len(STAGE_PREFIXES)):
        stage_name, stage_prefix = STAGE_PREFIXES[index]
        stage_function = stages_map.get(stage_name)

        if not stage_function: 
            print(f"No processing function defined for stage '{stage_name}'")
            continue

        try:
            new_filepath, step_complete = stage_function(new_filepath, current_step, stage_prefix, log_path)
            if not step_complete:
                print(f"Stage '{stage_name}' did not complete")
                return None

            if index + 1 < len(STAGE_PREFIXES):
                next_stage_name, next_stage_prefix = STAGE_PREFIXES[index + 1]
                new_filepath = modify_filename(new_filepath, next_stage_prefix, "0")
                current_step = 0
                
        except Exception as e:
            print(f"An error occurred during the '{stage_name}' stage: {e}")
            return None

    return new_filepath