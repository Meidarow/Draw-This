from enum import StrEnum
from typing import Optional

from PySide6.QtGui import QAction, Qt
from PySide6.QtWidgets import (
    QWidget,
    QTreeView,
    QVBoxLayout,
    QGroupBox,
    QMenu,
)

from iteradraw.application.commands.folder_commands import AddFolderSetCommand
from iteradraw.domain.events.domain_events import FolderSetAdded
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

    class _UiBuilder:
        def __init__(self, parent):
            self._parent = parent

        def build(self):
            self._configure_widget()
            self._create_header()
            self._install_layout()

        def _configure_widget(self):
            self._parent.setObjectName("FolderGroupBox")

        def _create_header(self):
            """
            Build the header for the folder section of the GUI.

            Includes a button to add more FolderSets and section title.
            """
            ...

        def _install_layout(self):
            self.layout = QVBoxLayout()
            self._parent.setLayout(self.layout)

    def __init__(self, command_bus, event_bus):
        super().__init__()
        self.command_bus = command_bus
        self.event_bus = event_bus
        self._ui = self._UiBuilder(self)
        self._ui.build()

    def _bind_signals(self):
        self.event_bus.subscribe(
            FolderSetAdded,
            lambda event: self.add_folder_group(event.folderset),
        )

    def add_folderset(self, folderset_name: Optional[str]):
        cmd = AddFolderSetCommand(display_name=folderset_name)
        self.command_bus.dispatch(cmd)

    def add_folder_group(self, folderset: FolderSet):
        vm = FolderGroupViewModel(self.command_bus, self.event_bus)
        vm.populate(folderset)
        folder_group = FolderGroupView(vm)
        self.layout().addWidget(folder_group)

    def remove_folder_group(self): ...


class FolderGroupView(QWidget):
    """
    Widget for single FolderSet's folder group.
    A tree with checkboxes, triple state for the tree-root and double state
    for each branch.

    Core Behaviors:
        -Accepts drop operations on unique folders, and rejects duplicates.
        -Defines context menu actions for the folder group and its folders.

    Note: Data-bound, uses View <-> Viewmodel architecture.
          Its viewmodel class is FolderGroupViewModel.
    """

    class Actions(StrEnum):
        ADD_FOLDER = "add_folder"
        REMOVE_FOLDER = "remove_folder"
        OPEN_FOLDER = "open_folder"
        DELETE_FOLDERSET = "delete_folderset"
        RENAME_FOLDERSET = "rename_folderset"

    class _UiBuilder:
        """
        Handles all reusable UI building implementation.

        Core Responsabilites:
            -Create/Configure tree view UI parameters.
            -Install the tree view into parent.
        """

        def __init__(self, parent):
            self._parent = parent
            self.tree: Optional[QTreeView] = None

        def build(self):
            self._create_widget()
            self._configure_tree()
            self._install_layout()
            self._create_actions()

        def _create_widget(self):
            self.tree = QTreeView()

        def _configure_tree(self):
            self.tree.setModel(self._parent.model)
            self.tree.setObjectName("FolderGroupItem")
            self.tree.setContextMenuPolicy(
                Qt.ContextMenuPolicy.CustomContextMenu
            )
            self.tree.setHeaderHidden(True)
            # Enable Drag/Drop behavior
            self.tree.setAcceptDrops(True)
            self.tree.setDragEnabled(True)

        def _install_layout(self):
            main_layout = QVBoxLayout(self._parent)
            main_layout.addWidget(self.tree)

        def _create_actions(self):
            # folder actions:
            self._parent.action[self._parent.Actions.REMOVE_FOLDER] = QAction(
                "Remove folder"
            )
            self._parent.action[self._parent.Actions.OPEN_FOLDER] = QAction(
                "Open folder"
            )

            # folderset actions:
            self._parent.action[self._parent.Actions.ADD_FOLDER] = QAction(
                "Add folder"
            )
            self._parent.action[self._parent.Actions.DELETE_FOLDERSET] = (
                QAction("Delete group")
            )
            self._parent.action[self._parent.Actions.RENAME_FOLDERSET] = (
                QAction("Rename group")
            )

    def __init__(self, viewmodel: FolderGroupViewModel):
        super().__init__()
        self.model = viewmodel
        self.action = {}
        self._ui = self._UiBuilder(self)
        self._ui.build()
        self.tree = self._ui.tree
        self.tree.customContextMenuRequested.connect(
            self._on_context_menu_requested
        )

    def _on_context_menu_requested(self, position):
        """
        Deploys the correct menu depending on context.

        Notes:

        """
        index = self.tree.indexAt(position)
        if not index.isValid():  # user right-clicked in empty space
            self._build_foldergroup__menu(position)
            return

        item = self.model.itemFromIndex(index)
        if item.hasChildren():  # user right-clicked folder group name
            self._build_foldergroup__menu(position)
            return

        self._build_folder_menu(item, position)

    def _build_foldergroup__menu(self, position):
        menu = QMenu()

        menu.addAction(self.action[self.Actions.ADD_FOLDER])
        menu.addAction(self.action[self.Actions.DELETE_FOLDERSET])
        menu.addAction(self.action[self.Actions.RENAME_FOLDERSET])

        self.action[self.Actions.ADD_FOLDER].triggered.disconnect()
        self.action[self.Actions.DELETE_FOLDERSET].triggered.disconnect()
        self.action[self.Actions.RENAME_FOLDERSET].triggered.disconnect()

        self.action[self.Actions.ADD_FOLDER].triggered.connect(
            lambda: self.model.on_add_folder_to_group(position)
        )
        self.action[self.Actions.DELETE_FOLDERSET].triggered.connect(
            lambda: self.model.on_delete_folder_group(position)
        )
        self.action[self.Actions.RENAME_FOLDERSET].triggered.connect(
            lambda: self.model.on_rename_folder_group(position)
        )

        menu.exec(self.tree.viewport().mapToGlobal(position))

    def _build_folder_menu(self, item, position):
        menu = QMenu()

        menu.addAction(self.action[self.Actions.REMOVE_FOLDER])
        menu.addAction(self.action[self.Actions.OPEN_FOLDER])
        self.action[self.Actions.REMOVE_FOLDER].triggered.connect(
            lambda: self.model.on_remove_folder_from_group(item, position)
        )
        self.action[self.Actions.OPEN_FOLDER].triggered.connect(
            lambda: self.model.on_open_folder_from_group(item, position)
        )

        menu.exec(self.tree.viewport().mapToGlobal(position))
