"""
Viewmodels for interface between GUI layer and application layer.
"""

from PySide6.QtGui import QStandardItemModel, QStandardItem, Qt
from PySide6.QtWidgets import QFileDialog, QInputDialog

from iteradraw.application.commands.folder_commands import (
    AddFolderCommand,
    RemoveFolderCommand,
    SetAllFoldersEnabledCommand,
    SetFolderEnabledCommand,
)
from iteradraw.domain.events.domain_events import FolderAdded


class FolderGroupViewModel(QStandardItemModel):
    def __init__(self, command_bus, event_bus):
        super().__init__()
        self.command_bus = command_bus
        self.event_bus = event_bus
        self.is_handling_change = False
        self._bind_signals()

    def _bind_signals(self):
        self.itemChanged.connect(self.on_checkbox_changed)

    def populate(self, folderset):
        self.itemChanged.disconnect(self.on_checkbox_changed)
        group = QStandardItem(folderset.display_name)
        group.setDropEnabled(True)
        group.setDragEnabled(False)
        group.setCheckable(True)
        group.setAutoTristate(True)
        group.setEditable(False)
        group.setData(
            folderset.uuid,
            Qt.ItemDataRole.UserRole,
        )
        self.invisibleRootItem().appendRow(group)

        for f in folderset.all:
            item = self._build_item(f.path, f.enabled)
            group.appendRow(item)
        self.itemChanged.connect(self.on_checkbox_changed)

    def add_folder(self, folderset_id, folder_path):
        cmd = AddFolderCommand(
            folder_path=folder_path,
            enabled=True,
            folderset_id=folderset_id,
        )
        self.command_bus.dispatch(cmd)

    def remove_folder(self, folderset_id, folder_path):
        cmd = RemoveFolderCommand(
            folder_path=folder_path, folderset_id=folderset_id
        )
        self.command_bus.dispatch(cmd)

    # =============================================================================
    # Slots
    # =============================================================================

    def on_add_folder_to_group(self, position):
        parent_item = self.invisibleRootItem().child(0)
        index = parent_item.index()
        folderset_id = self.data(index, Qt.ItemDataRole.UserRole)
        folder_path = QFileDialog().getExistingDirectory()
        self.add_folder(folderset_id, folder_path)

    def on_folder_added_to_group(self, event: FolderAdded):
        parent_item = self.invisibleRootItem().child(0)
        parent_item.appendRow(
            self._build_item(event.folder_path, event.enabled)
        )

    def on_rename_folder_group(self, position):
        parent_item = self.invisibleRootItem().child(0)
        index = parent_item.index()
        folderset_id = self.data(index, Qt.ItemDataRole.UserRole)
        name = QInputDialog().getText(self.parent(), "New name:", "")
        self.rename_folderset(folderset_id, name)

    def on_delete_folder_group(self, position): ...

    def on_remove_folder_from_group(self, item, position): ...

    def on_open_folder_from_group(self, item, position): ...

    def on_checkbox_changed(self, item: QStandardItem):
        """
        Slot for itemChanged signal.

        Behavior:
            -Evaluates whether checkbox belogns to parent or child widget.
                -Parent: aligns all children to parent new state.
                -Child: evaluates new parent state based on all siblings.
        """
        if self.is_handling_change:
            return
        self.is_handling_change = True
        try:
            if item.hasChildren():
                self._set_state_for_all_children(parent_item=item)
            else:
                self._calculate_state_for_parent(child_item=item)
        finally:
            self.is_handling_change = False

    def _set_state_for_all_children(self, parent_item: QStandardItem):
        new_state = parent_item.checkState()
        for child_row in range(parent_item.rowCount()):
            child = parent_item.child(child_row)
            child.setCheckState(new_state)

        cmd = SetAllFoldersEnabledCommand(
            folderset_id=parent_item.data(Qt.ItemDataRole.UserRole),
            target_enabled=(Qt.CheckState.Checked == new_state),
        )
        self.command_bus.dispatch(cmd)

    def _calculate_state_for_parent(self, child_item: QStandardItem):
        parent = child_item.parent()
        checked_count = 0
        total_children = parent.rowCount()

        for i in range(total_children):
            if parent.child(i).checkState() == Qt.CheckState.Checked:
                checked_count += 1

        if checked_count == 0:
            parent.setCheckState(Qt.CheckState.Unchecked)
        elif checked_count == total_children:
            parent.setCheckState(Qt.CheckState.Checked)
        else:
            parent.setCheckState(Qt.CheckState.PartiallyChecked)

        cmd = SetFolderEnabledCommand(
            folderset_id=parent.data(Qt.ItemDataRole.UserRole),
            folder_path=child_item.text(),
            target_enabled=(Qt.CheckState.Checked == child_item.checkState()),
        )
        self.command_bus.dispatch(cmd)

    @staticmethod
    def _build_item(folder_path: str, enabled: bool) -> QStandardItem:
        item = QStandardItem(folder_path)
        item.setDragEnabled(True)
        item.setDropEnabled(False)
        item.setCheckable(True)
        item.setEditable(False)
        item.setCheckState(
            Qt.CheckState.Checked if enabled else Qt.CheckState.Unchecked
        )
        return item
