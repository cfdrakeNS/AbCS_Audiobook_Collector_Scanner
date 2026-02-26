"""Backup and restore management dialog."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QEvent, QTimer
from PySide6.QtGui import QKeySequence, QShortcut, QAccessible
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QStatusBar,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
)

from accessibility.scaling import UIScaler
from accessibility.accessible_events import announce_status_message
from accessibility.style_helpers import build_accessible_button_style, exec_styled_message_box
from accessibility.theme_manager import ThemeManager
from accessibility.key_filters import is_unmapped_alt_letter
from database import DatabaseManager


class BackupRestoreWindow(QDialog):
    """Manage database backups, restore, and full reset."""

    ALLOWED_ALT_LETTERS = {
        'B', 'C', 'D', 'F', 'L', 'O', 'R', 'T'
    }

    ALT_SHORTCUT_STATUS = {
        Qt.Key_B: "Alt+B: Backup",
        Qt.Key_C: "Alt+C: Close",
        Qt.Key_D: "Alt+D: Delete",
        Qt.Key_F: "Alt+F: Full reset",
        Qt.Key_L: "Alt+L: Backup list",
        Qt.Key_O: "Alt+O: Browse",
        Qt.Key_R: "Alt+R: Restore",
        Qt.Key_T: "Alt+T: Focus restore file",
    }

    def __init__(
        self,
        db: DatabaseManager,
        scaler: UIScaler,
        theme_manager: ThemeManager,
        parent=None,
    ):
        super().__init__(parent)

        self.db = db
        self.scaler = scaler
        self.theme_manager = theme_manager
        self.data_changed = False
        self._default_status_message = "Ready"

        self.setup_ui()
        self.setup_shortcuts()
        self.install_event_filters()
        self.apply_control_styles()
        self.refresh_backup_list()

        self.setWindowTitle("Backup / Restore")
        self.setAccessibleName("Backup Restore")
        self.setAccessibleDescription(
            "Manage backups, restore from backup, or reset the database"
        )
        self.resize(860, 520)
        self.set_status("Ready")
        QTimer.singleShot(
            0, lambda: self.close_button.setFocus(Qt.TabFocusReason))

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        backups_label = QLabel("Backup &List:")
        self.backup_list = QTableWidget()
        self.backup_list.setAccessibleName("Backup list")
        self.backup_list.setAccessibleDescription(
            "List of available backup files"
        )
        self.backup_list.setColumnCount(1)
        self.backup_list.setHorizontalHeaderLabels(["Backup File"])
        self.backup_list.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.backup_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.backup_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.backup_list.verticalHeader().setVisible(False)
        self.backup_list.horizontalHeader().setStretchLastSection(True)
        self.backup_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.backup_list.setShowGrid(False)
        self.backup_list.setAlternatingRowColors(True)
        self.backup_list.setStyleSheet(
            """
            QTableWidget::item {
                margin: 0px;
                padding: 1px 4px;
            }
            QTableWidget::item:selected,
            QTableWidget::item:selected:active,
            QTableWidget::item:selected:!active {
                border: none;
                outline: none;
            }
            QTableWidget:focus {
                border: none;
                outline: none;
            }
            """
        )
        backups_label.setBuddy(self.backup_list)
        layout.addWidget(backups_label)
        layout.addWidget(self.backup_list, 1)

        browse_layout = QHBoxLayout()
        self.browse_button = QPushButton("Br&owse")
        self.browse_button.setAccessibleName("Browse")
        self.browse_button.setAccessibleDescription(
            "Browse for a backup file to restore - Alt+O"
        )
        browse_layout.addWidget(self.browse_button)
        browse_layout.addStretch(1)
        layout.addLayout(browse_layout)

        restore_layout = QHBoxLayout()
        restore_label = QLabel("Res&tore file:")
        self.restore_path_edit = QLineEdit()
        self.restore_path_edit.setReadOnly(True)
        self.restore_path_edit.setAccessibleName("Restore file")
        self.restore_path_edit.setAccessibleDescription(
            "Selected backup file to restore - Alt+T"
        )
        restore_label.setBuddy(self.restore_path_edit)
        restore_layout.addWidget(restore_label)
        restore_layout.addWidget(self.restore_path_edit, 1)
        layout.addLayout(restore_layout)

        footer_layout = QHBoxLayout()
        self.backup_button = QPushButton("&Backup")
        self.backup_button.setAccessibleName("Backup")
        self.backup_button.setAccessibleDescription(
            "Create a backup in the default backup folder - Alt+B"
        )

        self.restore_button = QPushButton("&Restore")
        self.restore_button.setAccessibleName("Restore")
        self.restore_button.setAccessibleDescription(
            "Restore from selected backup file - Alt+R"
        )

        self.delete_button = QPushButton("&Delete")
        self.delete_button.setAccessibleName("Delete")
        self.delete_button.setAccessibleDescription(
            "Delete selected backup file - Alt+D"
        )

        self.full_reset_button = QPushButton("&Full Reset")
        self.full_reset_button.setAccessibleName("Full Reset")
        self.full_reset_button.setAccessibleDescription(
            "Clear all data and recreate an empty database - Alt+F"
        )

        self.close_button = QPushButton("&Close")
        self.close_button.setAccessibleName("Close")
        self.close_button.setAccessibleDescription(
            "Close this window - Alt+C"
        )

        footer_layout.addWidget(self.backup_button)
        footer_layout.addWidget(self.restore_button)
        footer_layout.addWidget(self.delete_button)
        footer_layout.addWidget(self.full_reset_button)
        footer_layout.addStretch(1)
        footer_layout.addWidget(self.close_button)
        layout.addLayout(footer_layout)

        self.status_bar = QStatusBar()
        self.status_bar.setAccessibleName("Status")
        self.status_bar.setAccessibleDescription("Backup restore status")
        layout.addWidget(self.status_bar)

        self.backup_list.currentCellChanged.connect(self.on_backup_selected)
        self.backup_list.itemSelectionChanged.connect(
            self._update_delete_button_visibility)
        self.browse_button.clicked.connect(self.on_browse)
        self.backup_button.clicked.connect(self.on_backup)
        self.restore_button.clicked.connect(self.on_restore)
        self.delete_button.clicked.connect(self.on_delete_backup)
        self.full_reset_button.clicked.connect(self.on_full_reset)
        self.close_button.clicked.connect(self.accept)

        self.setTabOrder(self.backup_list, self.browse_button)
        self.setTabOrder(self.browse_button, self.restore_path_edit)
        self.setTabOrder(self.restore_path_edit, self.backup_button)
        self.setTabOrder(self.backup_button, self.restore_button)
        self.setTabOrder(self.restore_button, self.delete_button)
        self.setTabOrder(self.delete_button, self.full_reset_button)
        self.setTabOrder(self.full_reset_button, self.close_button)

        self._update_delete_button_visibility()

    def setup_shortcuts(self):
        escape_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        escape_shortcut.activated.connect(self.accept)

        self.list_shortcut = QShortcut(QKeySequence("Alt+L"), self)
        self.list_shortcut.activated.connect(self.focus_backup_list)

        self.restore_file_shortcut = QShortcut(QKeySequence("Alt+T"), self)
        self.restore_file_shortcut.activated.connect(self.focus_restore_file)

        self.help_shortcut = QShortcut(QKeySequence("F1"), self)
        self.help_shortcut.activated.connect(self.on_show_shortcuts)

        self.status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.status_shortcut.activated.connect(self.on_read_status_bar)

        self.status_shortcut_shift = QShortcut(QKeySequence("Alt+?"), self)
        self.status_shortcut_shift.activated.connect(self.on_read_status_bar)

        self.status_shortcut_equal = QShortcut(QKeySequence("Alt+="), self)
        self.status_shortcut_equal.activated.connect(self.on_read_status_bar)

    def install_event_filters(self):
        """Install key event filters on dialog and key child controls."""
        self.installEventFilter(self)
        self.backup_list.installEventFilter(self)
        self.browse_button.installEventFilter(self)
        self.restore_path_edit.installEventFilter(self)
        self.backup_button.installEventFilter(self)
        self.restore_button.installEventFilter(self)
        self.delete_button.installEventFilter(self)
        self.full_reset_button.installEventFilter(self)
        self.close_button.installEventFilter(self)
        self.status_bar.installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() in (QEvent.FocusIn, QEvent.FocusOut):
            QTimer.singleShot(0, self._update_delete_button_visibility)

        if event.type() == QEvent.KeyPress:
            is_alt_only = bool(event.modifiers() & Qt.AltModifier) and not bool(
                event.modifiers() & (Qt.ControlModifier | Qt.MetaModifier)
            )
            if is_alt_only:
                status_text = self.ALT_SHORTCUT_STATUS.get(event.key())
                if status_text:
                    self.set_status(status_text, announce=False)

            if is_unmapped_alt_letter(event, self.ALLOWED_ALT_LETTERS):
                return True
        return super().eventFilter(source, event)

    def apply_control_styles(self):
        button_style = build_accessible_button_style(
            self.scaler.get_scaled_size(34))
        for button in self.findChildren(QPushButton):
            button.setStyleSheet(button_style)

    def focus_backup_list(self):
        self.backup_list.setFocus()
        if self.backup_list.rowCount() > 0 and self.backup_list.currentRow() < 0:
            self.backup_list.setCurrentCell(0, 0)
        self._update_delete_button_visibility()

    def focus_restore_file(self):
        self.restore_path_edit.setFocus(Qt.ShortcutFocusReason)

    def on_show_shortcuts(self):
        """Show keyboard shortcuts help dialog."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Keyboard Shortcuts - Backup / Restore")
        dlg.setAccessibleName("Keyboard Shortcuts")
        dlg.resize(460, 440)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        shortcuts = [
            ("Alt+/", "Read status bar"),
            ("Alt+L", "Backup list"),
            ("Alt+O", "Browse for restore file"),
            ("Alt+T", "Focus restore file"),
            ("Alt+B", "Create backup"),
            ("Alt+R", "Run restore from selected backup"),
            ("Alt+D", "Delete selected backup"),
            ("Alt+F", "Full reset"),
            ("Alt+C", "Close window"),
            ("Escape", "Close window"),
            ("F1", "Show this help"),
        ]

        table = QTableWidget()
        table.setAccessibleName("Shortcuts list")
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels([""])
        table.setRowCount(len(shortcuts))
        table.setVerticalHeaderLabels([""] * len(shortcuts))
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setTabKeyNavigation(False)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setStyleSheet(
            "QTableWidget:focus { border: none; outline: none; }")

        for row, (key, description) in enumerate(shortcuts):
            combined_text = f"{description} - {key}"
            item = QTableWidgetItem(combined_text)
            item.setData(Qt.AccessibleTextRole, f"{description}: {key}")
            table.setItem(row, 0, item)

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)

        font = table.font()
        font.setPointSize(self.scaler.get_scaled_size(11))
        table.setFont(font)
        layout.addWidget(table)

        close_btn = QPushButton("Close")
        close_btn.setAccessibleName("Close")
        close_btn.clicked.connect(dlg.accept)
        btn_font = close_btn.font()
        btn_font.setPointSize(self.scaler.get_scaled_size(11))
        close_btn.setFont(btn_font)
        layout.addWidget(close_btn)

        dlg.setTabOrder(table, close_btn)
        dlg.exec()

    def on_read_status_bar(self):
        status_text = self.status_bar.currentMessage() or self._default_status_message
        if QAccessible.isActive():
            self.set_status(status_text, announce=True)
        else:
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Information,
                title="Status Bar",
                text=f"No screen reader active.\n\nStatus: {status_text}",
            )

    def _set_restore_path(self, path_text: str):
        self.restore_path_edit.setText(path_text)
        self.restore_button.setEnabled(bool(path_text.strip()))

    def _has_backup_list_selection(self) -> bool:
        selected_items = self.backup_list.selectedItems()
        if not selected_items:
            return False
        selected_item = selected_items[0]
        selected_path = (selected_item.data(Qt.UserRole) or "").strip()
        return bool(selected_path)

    def _is_backup_list_focused(self) -> bool:
        app = QApplication.instance()
        if app is None:
            return False
        focus_widget = app.focusWidget()
        return focus_widget in (self.backup_list, self.backup_list.viewport())

    def _update_delete_button_visibility(self):
        should_show = self._is_backup_list_focused() and self._has_backup_list_selection()
        self.delete_button.setVisible(should_show)

    def _add_backup_item(self, path: Path):
        row = self.backup_list.rowCount()
        self.backup_list.insertRow(row)
        item = QTableWidgetItem(path.name)
        item.setData(Qt.UserRole, str(path))
        item.setToolTip(str(path))
        self.backup_list.setItem(row, 0, item)

    def refresh_backup_list(self):
        selected_path = self.restore_path_edit.text().strip()
        self.backup_list.setRowCount(0)

        backups = self.db.list_backups()
        for backup_path in backups:
            self._add_backup_item(backup_path)

        if selected_path:
            self._select_backup_path(selected_path)
        elif backups:
            self.backup_list.setCurrentCell(0, 0)
        else:
            self._set_restore_path("")

        self._update_delete_button_visibility()

    def _select_backup_path(self, path_text: str):
        normalized = str(Path(path_text).resolve())
        for index in range(self.backup_list.rowCount()):
            item = self.backup_list.item(index, 0)
            item_path = item.data(Qt.UserRole)
            if item_path and str(Path(item_path).resolve()) == normalized:
                self.backup_list.setCurrentCell(index, 0)
                self._update_delete_button_visibility()
                return
        self.backup_list.clearSelection()
        self._set_restore_path(path_text)
        self._update_delete_button_visibility()

    def on_backup_selected(self, current_row: int, _current_col: int, _prev_row: int, _prev_col: int):
        if current_row < 0:
            self._set_restore_path("")
            self._update_delete_button_visibility()
            return

        current = self.backup_list.item(current_row, 0)
        path_text = (current.data(Qt.UserRole)
                     if current is not None else "") or ""
        self._set_restore_path(path_text)
        self._update_delete_button_visibility()

    def on_browse(self):
        backup_dir = str(self.db.get_backup_directory())
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Backup File",
            backup_dir,
            "Database Files (*.db *.sqlite *.sqlite3);;All Files (*.*)",
        )
        if not file_path:
            return

        self._select_backup_path(file_path)
        self.set_status(f"Selected backup: {Path(file_path).name}")

    def on_backup(self):
        try:
            backup_path = self.db.create_manual_backup()
        except Exception as exc:
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Critical,
                title="Backup Failed",
                text=f"Backup failed.\n\n{exc}",
            )
            self.set_status("Backup failed")
            return

        self.refresh_backup_list()
        self._select_backup_path(str(backup_path))
        self.set_status(f"Backup created: {backup_path.name}")

    def on_restore(self):
        restore_path = self.restore_path_edit.text().strip()
        if not restore_path:
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Warning,
                title="No Backup Selected",
                text="Select a backup file to restore.",
            )
            self.set_status("Restore canceled: no backup selected")
            return

        confirm = exec_styled_message_box(
            self,
            self.scaler.get_scaled_size(20),
            icon=QMessageBox.Warning,
            title="Confirm Restore",
            text=(
                "Restore from selected backup?\n\n"
                "Current data will be replaced by the selected backup."
            ),
            buttons=QMessageBox.Yes | QMessageBox.No,
            default_button=QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            self.set_status("Restore canceled")
            return

        try:
            self.db.restore_from_backup(restore_path)
        except Exception as exc:
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Critical,
                title="Restore Failed",
                text=f"Restore failed.\n\n{exc}",
            )
            self.set_status("Restore failed")
            return

        self.data_changed = True
        self.refresh_backup_list()
        self._select_backup_path(restore_path)
        self.set_status("Restore completed")

    def on_delete_backup(self):
        current_row = self.backup_list.currentRow()
        current_item = self.backup_list.item(
            current_row, 0) if current_row >= 0 else None
        backup_path = ""
        if current_item is not None:
            backup_path = (current_item.data(Qt.UserRole) or "").strip()

        if not backup_path:
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Warning,
                title="No Backup Selected",
                text="Select a backup file to delete.",
            )
            self.set_status("Delete canceled: no backup selected")
            return

        backup_name = Path(backup_path).name
        confirm = exec_styled_message_box(
            self,
            self.scaler.get_scaled_size(20),
            icon=QMessageBox.Warning,
            title="Confirm Delete",
            text=(
                "Delete selected backup file?\n\n"
                f"{backup_name}"
            ),
            buttons=QMessageBox.Yes | QMessageBox.No,
            default_button=QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            self.set_status("Delete backup canceled")
            return

        deleted_row = current_row
        try:
            self.db.delete_backup_file(backup_path)
        except Exception as exc:
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Critical,
                title="Delete Failed",
                text=f"Delete backup failed.\n\n{exc}",
            )
            self.set_status("Delete backup failed")
            return

        self.refresh_backup_list()
        if self.backup_list.rowCount() > 0:
            self.backup_list.setCurrentCell(
                min(max(deleted_row, 0), self.backup_list.rowCount() - 1),
                0,
            )
        self.set_status(f"Deleted backup: {backup_name}")

    def on_full_reset(self):
        confirm = exec_styled_message_box(
            self,
            self.scaler.get_scaled_size(20),
            icon=QMessageBox.Warning,
            title="Confirm Full Reset",
            text=(
                "Full reset will clear all books and rebuild a new database.\n\n"
                "A backup will be created first. Continue?"
            ),
            buttons=QMessageBox.Yes | QMessageBox.No,
            default_button=QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            self.set_status("Full reset canceled")
            return

        try:
            backup_path = self.db.full_reset_database(create_backup=True)
        except Exception as exc:
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Critical,
                title="Full Reset Failed",
                text=f"Full reset failed.\n\n{exc}",
            )
            self.set_status("Full reset failed")
            return

        self.data_changed = True
        self.refresh_backup_list()

        if backup_path is not None:
            self._select_backup_path(str(backup_path))
            self.set_status(
                f"Full reset complete. Backup created: {backup_path.name}")
        else:
            self.set_status("Full reset complete")

    def set_status(self, message: str, announce: bool = True):
        self._default_status_message = message
        announce_status_message(self.status_bar, message, move_focus=announce)
