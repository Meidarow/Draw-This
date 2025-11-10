from PySide6.QtGui import QStandardItemModel, QStandardItem, Qt
from PySide6.QtWidgets import QWidget, QTreeView

from iteradraw.domain.models.folder import FolderSet, Folder

"""
Custom PySide QtGui widgets.
"""


class FolderWidget(QWidget):
    """
    Build a singe FolderSet's GUI widget, a tree with checkboxes,
    triple state for the tree-root and double state for each branch.
    """

    def __init__(self, folderset):
        super().__init__()
        self.tree = QTreeView()
        self.tree.setHeaderHidden(True)
        self.model = QStandardItemModel()
        self.root_item = self.model.invisibleRootItem()

        folderset = FolderSet(
            name="Figures",
            _folders={
                "path": Folder(path="path", enabled=True),
                "path2": Folder(path="path2", enabled=False),
            },
        )
        # Fill with example data
        self.populate_tree(folderset)
        self.tree.setModel(self.model)

    def populate_tree(self, folderset: FolderSet):
        """Temporary stub showing folder group + subfolders."""
        group = QStandardItem(folderset.name)
        for folder in folderset.all:
            child = QStandardItem(folder.path)
            child.setCheckable(True)
            child.setCheckState(
                Qt.CheckState.Checked
                if folder.enabled
                else Qt.CheckState.Unchecked
            )
            group.setCheckable(True)
            group.appendRow(child)
        group.setAutoTristate(True)
        self.root_item.appendRow(group)


class TimerWidget(QWidget): ...
