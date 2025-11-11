from typing import Optional

from PySide6.QtWidgets import (
    QWidget,
    QTreeView,
    QVBoxLayout,
    QGroupBox,
)

from iteradraw.application.commands.folder_commands import AddFolderSetCommand
from iteradraw.domain.models.folder import FolderSet
from iteradraw.presentation.pyside.viewmodels.folder_viewmodels import (
    FolderGroupViewModel,
)

"""
Custom PySide QtGui views for the folder panel of the main tab.
"""


class FolderPanelView(QGroupBox):
    """
    Aggregate view of FolderGroupViews.

    """

    def __init__(self, command_bus, event_bus):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setObjectName("FolderGroupBox")
        self.command_bus = command_bus
        self.event_bus = event_bus
        self.setLayout(self.layout)

    def _create_header(self):
        """
        Build the header for the folder section of the GUI.

        Includes a button to add more FolderSets and section title.
        """
        ...

    def add_folderset(self, folderset_name: Optional[str]):
        cmd = AddFolderSetCommand(display_name=folderset_name)
        self.command_bus.dispatch(cmd)

    def add_folder_group(self, folderset: FolderSet):
        vm = FolderGroupViewModel(
            command_bus=self.command_bus, event_bus=self.event_bus
        )
        folder_group = FolderGroupView(viewmodel=vm)
        vm.populate(folderset=folderset)
        self.layout.addWidget(folder_group)

    def remove_folder_group(self):
        ...


class FolderGroupView(QWidget):
    """
    Build a singe FolderSet's GUI widget, a tree with checkboxes,
    triple state for the tree-root and double state for each branch.

    Note: Data-bound, uses View <-> Viewmodel architecture.
          Its viewmodel class is FolderGroupViewModel.
    """

    def __init__(self, viewmodel: FolderGroupViewModel):
        super().__init__()
        self.tree = QTreeView()
        self.tree.setHeaderHidden(True)
        self.tree.setObjectName("FolderGroupItem")
        self.model = viewmodel
        self.tree.setAcceptDrops(True)
        self.tree.setDragEnabled(True)
        # Fill with example data
        self.tree.setModel(self.model)
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.tree)
