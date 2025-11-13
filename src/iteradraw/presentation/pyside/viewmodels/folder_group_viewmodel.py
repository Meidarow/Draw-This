from PySide6.QtGui import (
    QStandardItemModel,
    QStandardItem,
    Qt,
    QDesktopServices,
)
from PySide6.QtWidgets import QFileDialog, QInputDialog

from iteradraw.application.commands.folder_commands import (
    AddFolderCommand,
    RemoveFolderCommand,
    SetAllFoldersEnabledCommand,
    SetFolderEnabledCommand,
    DeleteFolderSetCommand,
    RenameFolderSetCommand,
)
from iteradraw.domain.events.domain_events import (
    FolderAdded,
    FolderRemoved,
    FolderSetRenamed,
)

"""
Viewmodel for the FolderGroupView GUI component.
"""


class FolderGroupViewModel(QStandardItemModel):
    def __init__(self, command_bus, event_bus, parent):
        super().__init__(parent)
        self.view = parent
        self.command_bus = command_bus
        self.event_bus = event_bus
        self.is_handling_change = False
        self.bind_signals()

    def populate(self, folderset) -> None:
        self.itemChanged.disconnect(self.on_checkbox_changed)
        group = self._build_and_configure_group(
            folderset_id=folderset.uuid, group_name=folderset.display_name
        )
        self.invisibleRootItem().appendRow(group)
        for f in folderset.all:
            item = self._build_and_configure_item(f.path, f.enabled)
            group.appendRow(item)
        group.setCheckState(self._calculate_state_for_parent(parent=group))
        self.itemChanged.connect(self.on_checkbox_changed)

    def bind_signals(self) -> None:
        self.itemChanged.connect(self.on_checkbox_changed)

    # =========================================================================
    # Signal Slots
    #    Slots for signals emmited in the GUI
    #
    # Naming convention:
    #    on_"command"() -> command describes GUI action
    # =========================================================================

    def on_add_folder_to_group(self) -> None:
        """ """
        parent_item = self.invisibleRootItem().child(0)
        index = parent_item.index()
        folderset_id = self.data(index, Qt.ItemDataRole.UserRole)
        folder_path = QFileDialog().getExistingDirectory()
        if folder_path:
            self.add_folder_to_folderset(folderset_id, folder_path)

    # noinspection PyMethodMayBeStatic
    def on_open_folder_from_group(self, item) -> None:
        QDesktopServices.openUrl(item.text())

    def on_remove_folder_from_group(self, item) -> None:
        if self._confirm_delete(
            "Would you like to remove this folder from this group?"
        ):
            parent_item = self.invisibleRootItem().child(0)
            index = parent_item.index()
            folderset_id = self.data(index, Qt.ItemDataRole.UserRole)
            folder_path = item.text()
            self.remove_folder_from_folderset(folderset_id, folder_path)

    def on_rename_folder_group(self) -> None:
        parent_item = self.invisibleRootItem().child(0)
        index = parent_item.index()
        folderset_id = self.data(index, Qt.ItemDataRole.UserRole)
        name, ok = QInputDialog().getText(self.view, "New name:", "")
        if name and ok:
            self.rename_folderset(folderset_id, name)

    def on_delete_folder_group(self) -> None:
        if self._confirm_delete(
            "Would you like to permanently delete this group?"
        ):
            parent_item = self.invisibleRootItem().child(0)
            index = parent_item.index()
            folderset_id = self.data(index, Qt.ItemDataRole.UserRole)
            self.delete_folderset(folderset_id=folderset_id)

    def on_checkbox_changed(self, item: QStandardItem) -> None:
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
                new_state = item.checkState()
                self._set_state_for_all_children(
                    parent_item=item,
                    check_state=new_state,
                )
                self.set_all_folders_enabled(
                    folderset_id=item.data(Qt.ItemDataRole.UserRole),
                    enabled=(Qt.CheckState.Checked == new_state),
                )
            else:
                parent = item.parent()
                new_state = self._calculate_state_for_parent(parent=parent)
                parent.setCheckState(new_state)
                self.set_folder_enabled(
                    folderset_id=parent.data(Qt.ItemDataRole.UserRole),
                    folder_path=item.text(),
                    enabled=(Qt.CheckState.Checked == item.checkState()),
                )
        finally:
            self.is_handling_change = False

    # =========================================================================
    # Event Slots:
    #    Slots for events isued on the event_bus
    #
    # Naming convention:
    #    on_"event_happened"() -> event describes past happening
    # =========================================================================

    def on_folder_added_to_folderset(self, event: FolderAdded) -> None:
        parent_item = self.invisibleRootItem().child(0)
        parent_item.appendRow(
            self._build_and_configure_item(event.folder_path, event.enabled)
        )

    def on_folder_removed_from_folderset(self, event: FolderRemoved):
        parent_item = self.invisibleRootItem().child(0)
        for child_row in range(parent_item.rowCount()):
            child_item = parent_item.child(child_row)
            if not child_item.text() == event.folder_path:
                continue
            parent_item.removeRow(child_row)
            return

    def on_folderset_renamed(self, event: FolderSetRenamed):
        parent_item = self.invisibleRootItem().child(0)
        parent_item.setText(event.new_name)

    """
    on_folderset_deleted:
        Folder group removal is handled by FolderPanelView
    """

    # =========================================================================
    # Command Dispatchers:
    #    Methods that issue commands on the command bus.
    #
    # Naming convention:
    #    "action"() -> action describes application layer command
    # =========================================================================

    def add_folder_to_folderset(self, folderset_id, folder_path) -> None:
        cmd = AddFolderCommand(
            folder_path=folder_path,
            enabled=True,
            folderset_id=folderset_id,
        )
        self.command_bus.dispatch(cmd)

    def remove_folder_from_folderset(self, folderset_id, folder_path) -> None:
        cmd = RemoveFolderCommand(
            folder_path=folder_path, folderset_id=folderset_id
        )
        self.command_bus.dispatch(cmd)

    def set_folder_enabled(self, folderset_id, folder_path, enabled) -> None:
        cmd = SetFolderEnabledCommand(
            folderset_id=folderset_id,
            folder_path=folder_path,
            target_enabled=enabled,
        )
        self.command_bus.dispatch(cmd)

    def set_all_folders_enabled(self, folderset_id, enabled) -> None:
        cmd = SetAllFoldersEnabledCommand(
            folderset_id=folderset_id,
            target_enabled=enabled,
        )
        self.command_bus.dispatch(cmd)

    def rename_folderset(self, folderset_id, name) -> None:
        cmd = RenameFolderSetCommand(folderset_id=folderset_id, new_name=name)
        self.command_bus.dispatch(cmd)

    def delete_folderset(self, folderset_id) -> None:
        cmd = DeleteFolderSetCommand(folderset_id=folderset_id)
        self.command_bus.dispatch(cmd)

    # =========================================================================
    # Private Helpers
    # =========================================================================

    @staticmethod
    def _set_state_for_all_children(
        parent_item: QStandardItem, check_state: Qt.CheckState
    ) -> None:
        for child_row in range(parent_item.rowCount()):
            child = parent_item.child(child_row)
            child.setCheckState(check_state)

    @staticmethod
    def _calculate_state_for_parent(parent: QStandardItem) -> Qt.CheckState:
        checked_count = 0
        total_children = parent.rowCount()

        for i in range(total_children):
            if parent.child(i).checkState() == Qt.CheckState.Checked:
                checked_count += 1

        if checked_count == 0:
            return Qt.CheckState.Unchecked
        elif checked_count == total_children:
            return Qt.CheckState.Checked
        else:
            return Qt.CheckState.PartiallyChecked

    @staticmethod
    def _build_and_configure_group(folderset_id, group_name) -> QStandardItem:
        group = QStandardItem(group_name)
        group.setDropEnabled(True)
        group.setDragEnabled(False)
        group.setCheckable(True)
        group.setAutoTristate(True)
        group.setEditable(False)
        group.setData(
            folderset_id,
            Qt.ItemDataRole.UserRole,
        )
        return group

    @staticmethod
    def _build_and_configure_item(
        folder_path: str, enabled: bool
    ) -> QStandardItem:
        item = QStandardItem(folder_path)
        item.setDragEnabled(True)
        item.setDropEnabled(False)
        item.setCheckable(True)
        item.setEditable(False)
        item.setCheckState(
            Qt.CheckState.Checked if enabled else Qt.CheckState.Unchecked
        )
        return item

    def _confirm_delete(self, message: str) -> bool:
        """
        Reusable helper to show a "Yes/No" confirmation dialog.
        Returns True if the user clicks Yes, False otherwise.
        """
        from PySide6.QtWidgets import QMessageBox  # Keep import local

        reply = QMessageBox.question(
            self.view,
            "Confirm Delete",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return reply == QMessageBox.StandardButton.Yes
