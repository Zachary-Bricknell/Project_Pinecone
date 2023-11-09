import sys
import pyvista as pv
import os
from pyvistaqt import BackgroundPlotter
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QWidget, QHBoxLayout, QLineEdit, QPushButton

resource_dir = os.path.join(os.path.dirname(__file__), 'resources')

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # Set PyVista settings such that the poitns remain the proper size
        pv.set_plot_theme('document')
        pv.global_theme.interactive = False
        pv.global_theme.point_size = 1

	# Change the icon to the Pinecone icon
        icon_path = '../resources/icons/temp_icon.ico'
        self.setWindowIcon(QIcon(icon_path))

        # Load the point cloud
        point_cloud = pv.read("../resources/sample_data/sample1.ply") #Change path to file spot

        # Compute the height of the point cloud, temporary for just diaplying a height value
        min_bound = point_cloud.bounds[4]  # z min
        max_bound = point_cloud.bounds[5]  # z max
        height = max_bound - min_bound

        # Initialize the BackgroundPlotter object such that the PyVista window wont also open
        self.plotter = BackgroundPlotter(show=False)
        self.plotter.add_mesh(point_cloud, color=True)
        self.plotter.set_background('white')

        # Main layout
        layout = QVBoxLayout()

        # Display the height, Currently just the distance between the two lowest and highest z points
        height_label = QLabel(f"Height: {height:.2f} units")
        layout.addWidget(height_label)
  
        # Input layout for CM
        input_layout = QHBoxLayout()
        input_label = QLabel("Enter CM:")
        input_layout.addWidget(input_label)

        # User input field
        self.input_field = QLineEdit()
        input_layout.addWidget(self.input_field)

        # Submit button
        radius_submit_button = QPushButton("Submit")
        radius_submit_button.clicked.connect(self.on_submit)
        input_layout.addWidget(radius_submit_button)

        # Input layout added to main layout
        layout.addLayout(input_layout)

        # Output label for radius at a point, Currently will just say coming soon
        self.radius_label = QLabel("")
        layout.addWidget(self.radius_label)

        # Add the plotter to the layout
        self.frame = QWidget()  # This will hold the plotter
        self.frame.setLayout(QVBoxLayout())
        self.frame.layout().addWidget(self.plotter.interactor)
        layout.addWidget(self.frame)

        # Central widget
        central_widget = QWidget()
        central_widget.setLayout(layout)

        # Set central widget
        self.setCentralWidget(central_widget)
        self.show()

    def on_submit(self):
        # Placeholder for radius output
        self.radius_label.setText("Coming Soon...")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('../resources/icons/temp_icon.ico'))  # Set the icon early
    window = MainWindow()
    sys.exit(app.exec_())