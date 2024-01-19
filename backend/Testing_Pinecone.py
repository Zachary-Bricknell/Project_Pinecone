import unittest
import open3d as o3d
from stages.point_cloud_cleaning_stage import *
from stages.point_cloud_preprocessing_stage import *

# Reading the point cloud (XYZ format file)
pointCloudFile = "../var/jenkins_home/file.xyz"
point_cloud = o3d.io.read_point_cloud(pointCloudFile)

class TestPointCloudFunctions(unittest.TestCase):
    # Testing the remove statistical outlier method
    def test_remove_statistical_outliers(self):
        original_size = len(point_cloud.points)
        point_cloud_removed = remove_statistical_outliers(point_cloud, pointCloudFile, nb_neighbors=20, std_ratio=2.0, current_stage_prefix="3")
        new_point_cloud = o3d.io.read_point_cloud(point_cloud_removed)
        self.assertTrue(len(new_point_cloud.points) < original_size)
        print(f"Original size: {original_size}, After removing statistical outliers: {len(new_point_cloud.points)}")
        print(f"Total points removed 1: {original_size - len(new_point_cloud.points)}")
        print("-" * 50)

    # Testing the remove radius outlier method
    def test_remove_radius_outliers(self):
        original_size = len(point_cloud.points)
        point_cloud_removed = remove_radius_outliers(point_cloud, pointCloudFile, current_stage_prefix="cl432", nb_neighbors=15, radius=0.05)
        new_point_cloud = o3d.io.read_point_cloud(point_cloud_removed)
        self.assertTrue(len(new_point_cloud.points) < original_size)
        print(f"Original size: {original_size}, After removing radius outliers: {len(new_point_cloud.points)}")
        print(f"Total points removed 2: {original_size - len(new_point_cloud.points)}")
        print("-" * 50)

    # Testing the remove machine learning outliers using the Isolation Forest Algorithm

    # Testing pre process method
    def test_Pre_Process_Point_Cloud(self):
        point_cloud = o3d.io.read_point_cloud(pointCloudFile)
        original_size = len(point_cloud.points)
        print(f"before running the pre_processing stage the point clouds that exist in the xyz file is: {original_size}")

        # Use the output filename from preprocessing_stage
        preprocessing_stage(pointCloudFile, "", 12)
        new_point_cloud = o3d.io.read_point_cloud(pointCloudFile)

        # self.assertTrue(len(point_cloud.points) < original_size)  # Expecting fewer points after procclearessing
        print(f"Original size of the point cloud was: {original_size} and after processing, the points reduced to: {len(new_point_cloud.points)}")
        print(f"Total points removed 3: {original_size - len(new_point_cloud.points)}")
        print("-" * 50)

    def test_cleaning_stage(self):
        input_filepath = pointCloudFile
        current_step = 0
        stage_prefix = "cl432"
        statistical_nb_neighbors = 20
        std_ratio = 1.0
        radius_nb_neighbors = 15
        radius = 0.05
        voxel_size = 0.02

        output_filepath, done_cleaning_data = cleaning_stage(
            input_filepath, current_step, stage_prefix,
            statistical_nb_neighbors, std_ratio,
            radius_nb_neighbors, radius, voxel_size
        )

        self.assertTrue(done_cleaning_data, "Cleaning not completed.")
        self.assertTrue(output_filepath != input_filepath, "Output file path is the same as input file path.")
        self.assertTrue(o3d.io.read_point_cloud(output_filepath).has_points(), "Output point cloud is empty.")


if __name__ == '__main__':
    unittest.main()