import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QSplitter,
    QPushButton,
    QFormLayout,
    QSpinBox,
    QCheckBox,
)

from iteradraw.presentation.pyside.widgets import FolderWidget


class SlideshowTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QSplitter()  # divider between folder tree and right panel
        layout.setHandleWidth(4)

        self.folderset = FolderWidget(folderset=None)

        right_panel = QWidget()
        form = QFormLayout(right_panel)
        form.addRow("Timer (seconds):", QSpinBox())
        form.addRow("Shuffle:", QCheckBox())
        form.addRow(QPushButton("Start"))

        layout.addWidget(self.folderset)
        layout.addWidget(right_panel)
        layout.setStretchFactor(0, 3)
        layout.setStretchFactor(1, 1)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(layout)


class FolderPanel(QWidget):
    def __init__(self, /):
        super().__init__()
        QVBoxLayout(self)
        self._create_header()
        # get folders
        # iterate over foldersets creating folderwidgets

    def _create_header(self):
        """
        Build the header for the folder section of the GUI.

        Includes a button to add more FolderSets and section title.
        """
        ...


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DrawThis")
        self.resize(960, 1080)

        tabs = QTabWidget()
        tabs.addTab(SlideshowTab(), "Slideshow")
        tabs.addTab(QWidget(), "⚙")  # user prefs placeholder

        self.setCentralWidget(tabs)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
