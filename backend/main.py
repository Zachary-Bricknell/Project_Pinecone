import os
import open3d as o3d
import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering
import numpy as np
import matplotlib.pyplot as plt
from utils.file_operations import read_point_cloud

class PointCloudApp:
    def __init__(self, width, height):
        self.app = gui.Application.instance
        self.app.initialize()

        # Create a window and set its size
        self.window = gui.Application.instance.create_window("Project_Pinecone", width, height)

        # Create a widget to add to the window
        self.widget3d = gui.SceneWidget()
        self.widget3d.scene = rendering.Open3DScene(self.window.renderer)

        # Setup the layout
        self.setup_layout(width, height)

        # Show the window
        self.window.show(True)

    def setup_layout(self, width, height):
        em = self.window.theme.font_size

        # Create a vertical layout
        vert = gui.Vert(0, gui.Margins(em, em, em, em))

        # Create an Open File button(May be removed as per new UI requirements)
        open_button = gui.Button("Open File")
        open_button.set_on_clicked(self.on_open_button_clicked)
        vert.add_child(open_button)

        # Add the 3D widget and the vertical layout to the window (Menu box)
        self.window.add_child(self.widget3d)
        self.window.add_child(vert)

        # Define how to layout the scene when the window is resized
        def on_layout(layout_context):
            r = self.window.content_rect
            vert.frame = gui.Rect(r.get_right() - 20 * em, r.y, 20 * em, r.height)
            self.widget3d.frame = gui.Rect(r.x, r.y, r.get_right() - 20 * em, r.height)

        self.window.set_on_layout(on_layout)
        
        self.widget3d.scene.set_background([0, 0, 0, 1])

    def on_open_button_clicked(self):
        # Open File Logic (May be removed later based on new UI requirements)
        dlg = gui.FileDialog(gui.FileDialog.OPEN, "Choose file to load", self.window.theme)
        dlg.set_on_cancel(self.on_file_dialog_cancel)
        dlg.set_on_done(self.on_file_dialog_done)
        self.window.show_dialog(dlg)

    def on_file_dialog_cancel(self):
        self.window.close_dialog()

    def on_file_dialog_done(self, path):
        self.window.close_dialog()
        try:
            print(f"Attempting to open file")
            # Load the point cloud using the custom read operation
            point_cloud, path = read_point_cloud(path)
            print(f"File opened successfully")
            if point_cloud is None:
                print("Failed to read point cloud, no data.")
                return

            # Get the filename without extension
            filename_without_extension = os.path.splitext(os.path.basename(path))[0]
            # Get the current directory
            current_directory = os.path.dirname(path)
            
            # Check if the file has been processed
            if filename_without_extension.startswith('pineconed_'):
                print(f"The file starts with pineconed_. Skipping processing.")
            
            # Check if the directory is in the processed directory
            elif os.path.basename(current_directory) == "processed":
                print("The file is already in the processed directory. Skipping processing.")
            

            # Process the file
            else:   
                print(f"Processing the point cloud")
                # Statistical Outlier Removal
                try:
                    _, ind = point_cloud.remove_statistical_outlier(nb_neighbors=15, std_ratio=1.0)
                    point_cloud = point_cloud.select_by_index(ind)
                    print(f"Statistical Outliers removed")
                except Exception as e:
                    print(f"Failed to remove Statistical Outliers: {e}")
                
                # # Radius Outlier Removal requires further testing
                # try:
                #     _, rad_ind = point_cloud.remove_radius_outlier(nb_points=15, radius=0.05)
                #     point_cloud = point_cloud.select_by_index(rad_ind)
                #     print(f"Radius Outliers removed")
                # except Exception as e:
                #     print(f"Failed to remove Radius Outliers: {e}")
                
                # Voxel Downsampling
                try:
                    voxel_size = 0.02 # Size of the voxels
                    point_cloud = point_cloud.voxel_down_sample(voxel_size=voxel_size)
                    print(f"Voxel Downsampled completed")
                except Exception as e:
                    print(f"Failed to Voxel Downsample: {e}")
                    
                print(f"File Processed")
                
                # Save the processed file in the 'processed' directory with the identifier
                processed_directory = os.path.join(current_directory, "processed")
                if not os.path.exists(processed_directory):
                    os.makedirs(processed_directory)

                processed_file_path = os.path.join(processed_directory, 'pineconed_' + filename_without_extension + '.ply')
                o3d.io.write_point_cloud(processed_file_path, point_cloud)
                print(f"Processed point cloud saved as: {processed_file_path}")

            # Adjust scaling of the points (1 for regular)
            material = rendering.MaterialRecord()
            material.point_size = 1.0 
        
            # Apply the point cloud to the scene
            self.widget3d.scene.add_geometry("Tree Point Cloud", point_cloud, material)
            self.widget3d.setup_camera(60, point_cloud.get_axis_aligned_bounding_box(), point_cloud.get_center())

        except Exception as e:
            print(f"Failed to load the point cloud: {e}")

            
    def run(self):
        self.app.run()

if __name__ == "__main__":
    app = PointCloudApp(width=1024, height=768)
    app.run()
