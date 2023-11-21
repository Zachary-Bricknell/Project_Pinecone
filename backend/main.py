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
            current_directory = os.path.dirname(path)
            if os.path.basename(current_directory) == "processed":
                print("The file is already in the processed directory. Skipping processing.")
                return

            # Load the point cloud using the custom read operation
            point_cloud = read_point_cloud(path)

            if point_cloud is None:
                print("Failed to read point cloud.")
                return

            # Create a new point cloud object that contains only XYZ coordinates
            xyz_only_point_cloud = o3d.geometry.PointCloud()
            xyz_only_point_cloud.points = point_cloud.points

            # Check if the point cloud has colors
            if not xyz_only_point_cloud.has_colors():
                points = np.asarray(xyz_only_point_cloud.points)
                z = points[:, 2]
                z_normalized = (z - np.min(z)) / (np.max(z) - np.min(z))
                colors = plt.get_cmap("Greens")(z_normalized)[:, :3]  # Use matplotlib's colormap
                xyz_only_point_cloud.colors = o3d.utility.Vector3dVector(colors)

            # Get the filename without extension
            filename_without_extension = os.path.splitext(os.path.basename(path))[0]

            # Process the point cloud if it's not already processed
            if not filename_without_extension.startswith('pineconed_'):
                # Statistical Outlier Removal
                try:
                    _, ind = xyz_only_point_cloud.remove_statistical_outlier(nb_neighbors=15, std_ratio=1.0)
                    xyz_only_point_cloud = xyz_only_point_cloud.select_by_index(ind)
                except Exception as e:
                    print(f"Failed to remove Statistical Outliers: {e}")
                
                # Radius Outlier Removal
                try:
                    _, rad_ind = xyz_only_point_cloud.remove_radius_outlier(nb_points=15, radius=0.05)
                    xyz_only_point_cloud = xyz_only_point_cloud.select_by_index(rad_ind)
                except Exception as e:
                    print(f"Failed to remove Radius Outliers: {e}")
                
                # Voxel Downsampling
                try:
                    voxel_size = 0.02 # Size of the voxels
                    xyz_only_point_cloud = xyz_only_point_cloud.voxel_down_sample(voxel_size=voxel_size)
                except Exception as e:
                    print(f"Failed to Voxel Downsample: {e}")
                
                # Save the processed file in the 'processed' directory with the identifier
                processed_directory = os.path.join(current_directory, "processed")
                if not os.path.exists(processed_directory):
                    os.makedirs(processed_directory)

                processed_file_path = os.path.join(processed_directory, 'pineconed_' + filename_without_extension + '.pcd')
                o3d.io.write_point_cloud(processed_file_path, xyz_only_point_cloud)
                print(f"Processed point cloud saved as XYZ only: {processed_file_path}")

            # Use xyz_only_point_cloud for visualization
            point_cloud = xyz_only_point_cloud

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
