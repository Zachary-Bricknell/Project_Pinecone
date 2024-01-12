import unittest
from point_cloud_utils import *
import open3d as o3d 
import numpy as np
from file_operations import read_point_cloud

# Reading the point cloud (XYZ format file)
read_point_cloud("C:/Users/N1ko/Project_Pinecone/backend/w07-2018-tree27.xyz")

class TestPointCloudFunctions(unittest.TestCase):
    #Testing the remove statistical outlier method
    def test_remove_statistical_outliers(self):
        
        point_cloud = read_point_cloud("C:/Users/N1ko/Project_Pinecone/backend/w07-2018-tree27.xyz")
        original_size = len(point_cloud.points)
        point_cloud = remove_statistical_outliers(point_cloud)
        self.assertTrue(len(point_cloud.points) < original_size)  # # Expecting fewer points after processing
        print(f"Original size of the point cloud was: {original_size} and after the running the remove statistical outliers method the points reduced till: {len(point_cloud.points)}")
        print(f"Total points removed: {original_size - len(point_cloud.points)}")    
        print("-"*50)
        
    #Testing the remove radius outlier method    
    def test_remove_radius_outliers(self):
        
        point_cloud = read_point_cloud("C:/Users/N1ko/Project_Pinecone/backend/w07-2018-tree27.xyz")
        original_size = len(point_cloud.points)
        point_cloud = remove_radius_outliers(point_cloud,nb_neighbors=15, radius=0.05)
        self.assertTrue(len(point_cloud.points) < original_size)  # # Expecting fewer points after processing
        print(f"Original size of the point cloud was: {original_size} and after the running the remove radius outliers method the points reduced till: {len(point_cloud.points)}")
        print(f"Total points removed: {original_size - len(point_cloud.points)}")
        print("-"*50)
        
    #Testing the remove machine learning outliers using the Isolation forest Algorithm    
    def test_remove_ml_outliers(self):
        
        point_cloud = read_point_cloud("C:/Users/N1ko/Project_Pinecone/backend/w07-2018-tree27.xyz")
        original_size = len(point_cloud.points)
        point_cloud = remove_noise_ml(point_cloud)
        self.assertTrue(len(point_cloud.points) < original_size)  # # Expecting fewer points after processing
        print(f"Original size of the point cloud was: {original_size} and after the running the machine learning outliers removal method the points reduced till: {len(point_cloud.points)}")
        print(f"Total points removed: {original_size - len(point_cloud.points)}")
        print("-"*50)
        
    #Testing DBSCAN Clustering Concept by removing the small clusters and keeping the largest one on the graph    
    def test_Dbscan_Clustering(self):
      
        point_cloud = read_point_cloud("C:/Users/N1ko/Project_Pinecone/backend/w07-2018-tree27.xyz")
        original_size = len(point_cloud.points)
        point_cloud = keep_only_largest_cluster(point_cloud, eps=0.05, min_points=10)
        self.assertTrue(len(point_cloud.points) < original_size)  # Expect fewer points after clustering
        print(f"Original size of the point cloud was: {original_size} and after DBSCAN clustering, the points reduced to: {len(point_cloud.points)}")
        print(f"Total points removed: {original_size - len(point_cloud.points)}")
        print("-"*50)
        
    #Testing pre process method 
    def test_Pre_Process_Point_Cloud(self):
        
        point_cloud = read_point_cloud("C:/Users/N1ko/Project_Pinecone/backend/w07-2018-tree27.xyz")
        original_size = len(point_cloud.points)
        point_cloud = pre_process_point_cloud(point_cloud, nb_neighbors=15, std_ratio=1.0, radius=0.05, voxel_size=0.05)
        self.assertTrue(len(point_cloud.points) < original_size)  # Expecting fewer points after processing
        print(f"Original size of the point cloud was: {original_size} and after processing, the points reduced to: {len(point_cloud.points)}")
        print(f"Total points removed: {original_size - len(point_cloud.points)}")
        print("-"*50)
        
    #Testing process point cloud method    
    def test_process_PointCloud(self):
        
        point_cloud = read_point_cloud("C:/Users/N1ko/Project_Pinecone/backend/w07-2018-tree27.xyz")
        original_size = len(point_cloud.points)
        point_cloud = process_point_cloud(point_cloud, num_iterations=7, voxel_size=0.05, radius=0.1, min_neighbors=30)
        self.assertTrue(len(point_cloud.points) < original_size)  # Expecting fewer points after processing
        print(f"Original size of the point cloud was: {original_size} and after processing, the points reduced to: {len(point_cloud.points)}")
        print(f"Total points removed: {original_size - len(point_cloud.points)}")
        print("-"*50)
        
        
        
if __name__ == '__main__':
    unittest.main()
   