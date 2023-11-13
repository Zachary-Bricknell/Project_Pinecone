import open3d as o3d
import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering

class PointCloudApp:
    def __init__(self, width, height):
        self.app = gui.Application.instance
        self.app.initialize()

        # Create a window and set its size
        self.window = gui.Application.instance.create_window("PointCloudApp", width, height)

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

        # Create an Open File button
        open_button = gui.Button("Open File")
        open_button.set_on_clicked(self.on_open_button_clicked)
        vert.add_child(open_button)

        # Add the 3D widget and the vertical layout to the window
        self.window.add_child(self.widget3d)
        self.window.add_child(vert)

        # Define how to layout the scene when the window is resized
        def on_layout(layout_context):
            r = self.window.content_rect
            vert.frame = gui.Rect(r.get_right() - 20 * em, r.y, 20 * em, r.height)
            self.widget3d.frame = gui.Rect(r.x, r.y, r.get_right() - 20 * em, r.height)

        self.window.set_on_layout(on_layout)

    def on_open_button_clicked(self):
        # This is where you would add the file dialog and loading logic
        dlg = gui.FileDialog(gui.FileDialog.OPEN, "Choose file to load", self.window.theme)
        dlg.set_on_cancel(self.on_file_dialog_cancel)
        dlg.set_on_done(self.on_file_dialog_done)
        self.window.show_dialog(dlg)

    def on_file_dialog_cancel(self):
        self.window.close_dialog()

    def on_file_dialog_done(self, path):
        self.window.close_dialog()
        # Load the point cloud and add it to the scene
        point_cloud = o3d.io.read_point_cloud(path)
        # Adjust scaling of the points (1 is original size, Default is greater)
        material = rendering.MaterialRecord()
        material.point_size = 1.0  # Set the point size to 1
        #Apply the pointcould to the scene
        self.widget3d.scene.add_geometry("Tree Point Cloud", point_cloud, rendering.MaterialRecord())
        self.widget3d.setup_camera(60, point_cloud.get_axis_aligned_bounding_box(), point_cloud.get_center())

    def run(self):
        self.app.run()

if __name__ == "__main__":
    app = PointCloudApp(width=1024, height=768)
    app.run()
