<<<<<<< HEAD
import argparse
import os
from utils.file_operations import read_point_cloud
from utils.point_cloud_utils import process_point_cloud, save_processed_file, visualize_point_cloud


def main(args):
    path = args.path
    point_cloud = read_point_cloud(path)

    if point_cloud is None:
        print("Failed to read point cloud, no data.")
        return
=======
import os
import open3d as o3d
import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering
import numpy as np
import matplotlib.pyplot as plt
from utils.file_operations import read_point_cloud
from utils.point_cloud_utils import process_point_cloud, save_processed_file

class PointCloudApp:
    def __init__(self, width, height):
        self.app = gui.Application.instance
        self.app.initialize()

        self.window = gui.Application.instance.create_window("Project Pinecone", width, height)
        self.widget3d = gui.SceneWidget()
        self.widget3d.scene = rendering.Open3DScene(self.window.renderer)

        self.setup_layout(width, height)
        self.window.show(True)

    def setup_layout(self, width, height):
        em = self.window.theme.font_size
        vert = gui.Vert(0, gui.Margins(em, em, em, em))

        open_button = gui.Button("Open File")
        open_button.set_on_clicked(self.on_open_button_clicked)
        vert.add_child(open_button)

        self.window.add_child(self.widget3d)
        self.window.add_child(vert)

        def on_layout(layout_context):
            r = self.window.content_rect
            vert.frame = gui.Rect(r.get_right() - 20 * em, r.y, 20 * em, r.height)
            self.widget3d.frame = gui.Rect(r.x, r.y, r.get_right() - 20 * em, r.height)
        self.window.set_on_layout(on_layout)

        self.widget3d.scene.set_background([0, 0, 0, 1])

    def on_open_button_clicked(self):
        dlg = gui.FileDialog(gui.FileDialog.OPEN, "Choose file to load", self.window.theme)
        dlg.set_on_cancel(self.on_file_dialog_cancel)
        dlg.set_on_done(self.on_file_dialog_done)
        self.window.show_dialog(dlg)

    def on_file_dialog_cancel(self):
        self.window.close_dialog()

    def on_file_dialog_done(self, path):
        self.window.close_dialog()
        self.process_and_visualize_file(path)

    def process_and_visualize_file(self, path):
        try:
            print("Attempting to process file")
            processed_file_path = process_file(path)

            if processed_file_path is None:
                print("No processing required or failed to read point cloud.")
                return

            point_cloud = o3d.io.read_point_cloud(processed_file_path)
            self.visualize_point_cloud(point_cloud)
        except Exception as e:
            print(f"Failed to process and visualize the point cloud: {e}")

    def visualize_point_cloud(self, point_cloud):
        try:
            material = rendering.MaterialRecord()
            material.point_size = 1.0
            self.widget3d.scene.add_geometry("Tree Point Cloud", point_cloud, material)
            self.widget3d.setup_camera(60, point_cloud.get_axis_aligned_bounding_box(), point_cloud.get_center())
            print("Point cloud visualized.")
        except Exception as e:
            print(f"Failed to visualize the point cloud: {e}")

    def run(self):
        self.app.run()

def process_file(path):
    point_cloud = read_point_cloud(path)
    if point_cloud is None:
        return None
>>>>>>> main

    filename = os.path.splitext(os.path.basename(path))[0]
    directory = os.path.dirname(path)

<<<<<<< HEAD
    if args.process:
        point_cloud = process_point_cloud(point_cloud)
        processed_file_path = save_processed_file(directory, filename, point_cloud)
        print(f"Processed point cloud saved as: {processed_file_path}")
        path = processed_file_path  # Update path to processed file for visualization

    if args.visualize:
        visualize_point_cloud(path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process and/or visualize point cloud files.")
    parser.add_argument("path", help="Path to the point cloud file")
    parser.add_argument("--process", action="store_true", help="Process the point cloud file")
    parser.add_argument("--visualize", action="store_true", help="Visualize the point cloud file")
    args = parser.parse_args()

    main(args)
=======
    if filename.startswith('pineconed_') or os.path.basename(directory) == "processed":
        return None

    point_cloud = process_point_cloud(point_cloud)
    processed_file_path = save_processed_file(directory, filename, point_cloud)
    return processed_file_path

if __name__ == "__main__":
    app = PointCloudApp(width=1024, height=768)
    app.run()
>>>>>>> main
