from utils.file_operations import modify_filename
from utils.point_cloud_utils import get_current_step, STAGE_PREFIXES
from stages.point_cloud_cleaning_stage import cleaning_stage
from stages.point_cloud_preprocessing_stage import preprocessing_stage


def process_point_cloud(filepath, log_path):
    """
    Parameters:
    filepath (str): The file path of the point cloud to be processed.

    Returns:
    str: Filepath of the processed point cloud after completing the current stage.
    None: If the point cloud processing does not complete a stage or if an error occurs.

    Description:
    Processes a point cloud file through various stages such as cleaning, 
    preprocessing, and any subsequent stages as defined by the file's current step.
    
    This function determines the current stage of the point cloud file based on its naming convention.
    Depending on the stage, it routes the file to the appropriate processing function. The processing
    starts from the cleaning stage for raw data. Once a stage is completed, the function can be extended
    to move the file to the next processing stage. If the current stage is 'preprocessing', the respective
    function needs to be called.

    The function currently handles the cleaning stage and can be extended to handle additional stages as
    needed. For each stage, the respective function is expected to return a new filepath for the processed 
    file and a boolean indicating whether all defined steps are completed to indicate completion.
    """
    
    step_complete = True
    new_filepath = filepath
    stage, current_step = get_current_step(filepath)
    # Raw data starts at the cleaning stage.
    if stage == 'cleaning':        
        new_filepath, step_complete = cleaning_stage(new_filepath, current_step, STAGE_PREFIXES['cleaning'], log_path)
        if step_complete:
            stage = 'preprocessing'
            current_step = 0
            new_filepath = modify_filename(filepath, "_pp", "0") 
            
    if stage == 'preprocessing' and step_complete:
        new_filepath, step_complete = preprocessing_stage(new_filepath, current_step, STAGE_PREFIXES['preprocessing'], log_path) 

    return new_filepath if stage and step_complete else None
    