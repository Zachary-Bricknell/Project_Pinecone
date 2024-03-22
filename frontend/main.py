import sys
from PyQt5.QtWidgets import (
    
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QListWidget,
    QListWidgetItem,
    QGroupBox,
    QGridLayout,
    QLineEdit,
)

from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor
import os
import csv


# Add the root directory to sys.path if not already included
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now you can import your modules from the root directory
from backend.main import process, visualize_point_cloud, process_and_visualize
from backend.utils.file_operations import get_base_filename


class WorkerThread(QThread):
    finished = pyqtSignal(str)
    update_status = pyqtSignal(str)

    def __init__(self, function, args):
        super().__init__()
        self.function = function
        self.args = args
        self.stopped = False  # Flag to indicate if the thread is stopped

    def run(self):
        self.update_status.emit(
            '<html><head><style>*{font-size: 20px;}</style></head><body><p style="color: blue;">Processing...</p></body></html>'
        )
        try:
            csv_file_path = self.function(
                *self.args
            )  # This should return the path to the CSV file as a string
            if not self.stopped:  # Check if the thread is not stopped
                self.finished.emit(csv_file_path)  # Emit the string path
        except Exception as e:
            if not self.stopped:
                self.update_status.emit(f"Error: {str(e)}")
        finally:
            if not self.stopped:
                self.update_status.emit("Ready")
                # If processing failed and no path is returned, emit an empty string
                self.finished.emit("")

    def stop_thread(self):  # Method to stop the thread
        self.stopped = True


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_path = None  # Initialize file_path attribute
        self.file_queue = []
        self.current_thread = None  # Track the current thread

        self.setWindowTitle("Pinecone Project")
        self.setFixedSize(QSize(650, 700))

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        file_box = QGroupBox("Files")
        file_layout = QVBoxLayout(file_box)

        self.file_path_label = QLabel("Drag and drop files here or click Browse", self)
        self.file_path_label.setAlignment(Qt.AlignCenter)
        file_layout.addWidget(self.file_path_label)

        self.file_list = QListWidget(self)
        self.file_list.itemDoubleClicked.connect(
            self.execute_item
        )  # Connect double-click event
        self.file_list.setDragEnabled(True)  # Enable drag and drop
        self.file_list.setDragDropMode(QListWidget.DragDrop)
        self.file_list.setSelectionMode(
            QListWidget.SingleSelection
        )  # Single item selection
        file_layout.addWidget(self.file_list)

        main_layout.addWidget(file_box)

        self.status_label = QLabel("Ready", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)

        self.browse_button = QPushButton("Browse", self)
        self.browse_button.clicked.connect(self.browse_file)
        main_layout.addWidget(self.browse_button)

        self.setup_drag_and_drop()

        self.process_button = QPushButton("Process File", self)
        self.process_button.clicked.connect(self.process_file)
        self.process_button.setEnabled(False)
        main_layout.addWidget(self.process_button)

        self.visualize_button = QPushButton("Visualize File", self)
        self.visualize_button.clicked.connect(self.visualize_file)
        self.visualize_button.setEnabled(False)
        main_layout.addWidget(self.visualize_button)

        self.process_and_visualize_button = QPushButton(
            "Process and Visualize File", self
        )
        self.process_and_visualize_button.clicked.connect(
            self.process_and_visualize_file
        )
        self.process_and_visualize_button.setEnabled(False)
        main_layout.addWidget(self.process_and_visualize_button)

        self.apply_button_styles()

        self.stop_button = QPushButton(
            "Stop Processing", self
        )  # Change stop button text
        self.stop_button.clicked.connect(
            self.stop_processing
        )  # Connect stop button event
        main_layout.addWidget(self.stop_button)

    def process_done(self, csv_file_path):
        if csv_file_path:
            try:
                tree_info = {}
                with open(csv_file_path, "r") as csvfile:
                    reader = csv.DictReader(csvfile)
                    tree_info = next(reader)
            except Exception as e:
                self.update_status(f"Error reading CSV: {e}")
                return

            if tree_info:
                self.status_label.setText("Processing done")
                self.tree_info_window = TreeInfoWindow(tree_info)
                self.tree_info_window.show()
            else:
                self.status_label.setText("Error: No data found in CSV.")
        else:
             self.status_label.setText("Displaying Tree Information")

        self.process_next_file()

    def apply_button_styles(self):
        style = """
           QPushButton {
    background-color: #4CAF50;
    border: none;
    color: white;
    padding: 10px 20px;
    text-align: center;
    text-decoration: none;
    font-size: 16px;
    border-radius: 5px;
}

QPushButton:hover {
    background-color: #45a049;
}

QPushButton:disabled {
    background-color: #cccccc;
    color: #666666;
}

QLabel {
    font-size: 16px;
}

QGroupBox {
    border: 2px solid #4CAF50;
    border-radius: 5px;
    margin-top: 10px;
}

QGroupBox:title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 5px;
}

QLineEdit {
    background-color: #f0f0f0;
    border: 1px solid #ccc;
    padding: 5px;
    border-radius: 5px;
}

QListWidget {
    background-color: #ffffff;
    border: 1px solid #ccc;
    padding: 5px;
    border-radius: 5px;
}

QListWidget::item:selected {
    background-color: #d9edf7;
    color: black;
}

QListWidget::item:selected:!active {
    color: #333333;
}

        """
        self.setStyleSheet(style)

    def setup_drag_and_drop(self):
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            self.file_list.addItem(file_path)
            self.file_queue.append(file_path)
            self.process_button.setEnabled(True)
            self.visualize_button.setEnabled(True)
            self.process_and_visualize_button.setEnabled(True)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open XYZ File", "", "XYZ Files (*.xyz)"
        )
        if file_path:
            self.file_path = file_path
            self.file_list.addItem(file_path)
            self.file_queue.append(file_path)
            self.process_button.setEnabled(True)
            self.visualize_button.setEnabled(True)
            self.process_and_visualize_button.setEnabled(True)

    def start_thread(self, function, args):
        self.current_thread = WorkerThread(function, args)  # Assign the current thread
        self.current_thread.finished.connect(self.process_done)
        self.current_thread.update_status.connect(self.update_status)
        self.disable_buttons()
        self.current_thread.finished.connect(
            self.enable_buttons
        )  # Enable buttons after processing
        self.current_thread.start()

    def execute_item(self, item):  # New method for double-click execution
        file_path = item.text()
        self.file_queue.append(file_path)
        destination_directory = os.path.join(os.path.dirname(file_path), "pinecone")
        if not os.path.exists(destination_directory):
            os.makedirs(destination_directory)
        self.start_thread(process, (file_path, destination_directory))

    def process_file(self):
        if self.file_queue:
            file_path = self.file_queue.pop(0)
            destination_directory = os.path.join(os.path.dirname(file_path), "pinecone")
            if not os.path.exists(destination_directory):
                os.makedirs(destination_directory)
            self.start_thread(process, (file_path, destination_directory))

    def visualize_file(self):
        if self.file_queue:
            file_path = self.file_queue.pop(0)
            self.start_thread(visualize_point_cloud, (file_path,))

    def process_and_visualize_file(self):
        if self.file_queue:
            file_path = self.file_queue.pop(0)
            destination_directory = os.path.join(os.path.dirname(file_path), "pinecone")
            self.start_thread(process_and_visualize, (file_path, destination_directory))

    def stop_processing(self):  # Method to stop the processing
        if self.current_thread and self.current_thread.isRunning():
            self.current_thread.stop_thread()
            self.update_status("Processing stopped")
            self.current_thread = None  # Reset the current thread
        self.enable_buttons()  # Enable buttons after stopping processing

    def disable_buttons(self):
        self.browse_button.setEnabled(False)
        self.process_button.setEnabled(False)
        self.visualize_button.setEnabled(False)
        self.process_and_visualize_button.setEnabled(False)
        self.stop_button.setEnabled(True)  # Enable the stop button

    def enable_buttons(self):
        self.browse_button.setEnabled(True)
        self.process_button.setEnabled(True)
        self.visualize_button.setEnabled(True)
        self.process_and_visualize_button.setEnabled(True)
        self.stop_button.setEnabled(False)  # Disable the stop button

    def update_status(self, message):
        self.status_label.setText(message)

    def process_next_file(self):
        if self.file_queue:
            self.process_file()

    def delete_file(self):
        selected_item = self.file_list.currentItem()
        if selected_item is not None:
            selected_index = self.file_list.indexFromItem(selected_item).row()
            if selected_index < len(self.file_queue):
                del self.file_queue[selected_index]
                self.file_list.takeItem(selected_index)


from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QGroupBox,
    QGridLayout,
    QLineEdit,
)
from PyQt5.QtCore import Qt


class TreeInfoWindow(QMainWindow):
    def __init__(self, tree_info):
        super().__init__()
        self.setWindowTitle("Tree Information")
        self.setGeometry(100, 100, 1000, 1000)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        tree_information_group = QGroupBox("Tree Information", self)
        tree_information_layout = QGridLayout(tree_information_group)

        # Define the fields to display based on the CSV headers
        fields_to_display = list(tree_info.keys())

        for i, field in enumerate(fields_to_display):
            label = QLabel(
                f"{field.replace('_', ' ').title()}:", tree_information_group
            )
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            label.setFont(
                QFont("Roboto", 12)
            )  # Set a modern-looking font and increase font size
            entry = QLineEdit(tree_information_group)
            entry.setText(
                str(tree_info[field])
            )  # Use the header field to get the value
            entry.setReadOnly(True)
            entry.setStyleSheet(
                "QLineEdit { background-color: #f0f0f0; border: 1px solid #ccc; padding: 2px; border-radius: 4px; }"
            )
            tree_information_layout.addWidget(label, i, 0)
            tree_information_layout.addWidget(entry, i, 1)

        layout.addWidget(tree_information_group)

        self.set_background_style(layout)  # Apply custom background style

    def set_background_style(self, layout):
        # Customize background style for the window
        pal = self.palette()
        gradient_color = QColor("#f2f2f2")  # Light gray background color
        pal.setColor(QPalette.Window, gradient_color)
        self.setPalette(pal)
        self.setAutoFillBackground(True)
        layout.setContentsMargins(10, 10, 10, 10)  # Add margins to the layout

    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
