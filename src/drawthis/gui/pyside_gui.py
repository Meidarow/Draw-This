import sys

from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QTreeView,
    QSplitter,
    QPushButton,
    QFormLayout,
    QSpinBox,
    QCheckBox,
)


class SlideshowTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QSplitter()  # divider between folder tree and right panel
        layout.setHandleWidth(4)

        # Left: Folder Tree
        self.tree = QTreeView()
        self.tree.setHeaderHidden(True)
        self.model = QStandardItemModel()
        self.root_item = self.model.invisibleRootItem()

        # Fill with example data
        self.populate_tree()
        self.tree.setModel(self.model)

        # Right: Timer + Start button
        right_panel = QWidget()
        form = QFormLayout(right_panel)
        form.addRow("Timer (seconds):", QSpinBox())
        form.addRow("Shuffle:", QCheckBox())
        form.addRow(QPushButton("Start"))

        layout.addWidget(self.tree)
        layout.addWidget(right_panel)
        layout.setStretchFactor(0, 3)
        layout.setStretchFactor(1, 1)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(layout)

    def populate_tree(self):
        """Temporary stub showing folder group + subfolders."""
        group = QStandardItem("Art Studies")
        for name in ["Figures", "Portraits", "Landscapes"]:
            child = QStandardItem(name)
            child.setCheckable(True)
            group.appendRow(child)
        group.setCheckable(True)
        self.root_item.appendRow(group)


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
