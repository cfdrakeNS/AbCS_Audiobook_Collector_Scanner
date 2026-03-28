"""Collection management window (centralized shortcuts)."""

from __future__ import annotations

import re
import sqlite3

from PySide6.QtCore import QEvent, Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut, QAccessible
import sys
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QDialog,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QCheckBox,
)

from src.accessibility.accessible_events import announce_status_message, announce_dialog_opened, announce_dialog_closed
from src.accessibility.scaling import UIScaler
from src.accessibility.style_helpers import build_accessible_button_style, exec_styled_message_box
from src.accessibility.theme_manager import ThemeManager
from src.accessibility.key_filters import is_unmapped_alt_letter
from src.accessibility.shortcuts import get_shortcut_manager, ShortcutContext
from src.database import Collection, CollectionQueries, DatabaseManager


class CollectionWindow(QDialog):
    """
    Collection management window with PROVEN accessibility foundation.
    
    F1, Alt+/, and Escape work out of box.
    Built incrementally from accessible skeleton.
    """
    
    # Alt+letter keys that are allowed to pass through
    ALLOWED_ALT_LETTERS = {
        'B', 'E', 'N', 'S', 'F', '/'
    }
    
    def keyPressEvent(self, event):
        # If you want to handle Alt+D, add logic here. Otherwise, just call the base method.
        super().keyPressEvent(event)

    COL_NAME = 0
    COL_ACTIVE = 1

    @staticmethod
    def _to_proper_case(text: str) -> str:
        value = text.strip().lower()
        if not value:
            return ""
        return re.sub(
            r"(^|[\s\-'])([a-z])",
            lambda match: f"{match.group(1)}{match.group(2).upper()}",
            value,
        )

    def __init__(self, db: DatabaseManager, scaler: UIScaler, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)

        self.db = db
        self.scaler = scaler
        self.theme_manager = theme_manager
        self.collection_queries = CollectionQueries(db)

        self.current_collection_id: int | None = None
        self._is_new_entry_mode = False
        self._editor_locked = False

        self.setup_ui()
        self.setup_shortcuts()
        self.load_collections(populate_editor=False)
        self._set_editor_locked(True)
        self.name_edit.installEventFilter(self)
        QTimer.singleShot(
            0,
            lambda: self.focus_list() if self.table.rowCount() > 0 else None,
        )

        self.setWindowTitle("Collection Manager")
        self.setAccessibleName("Collection Manager")
        self.setAccessibleDescription(
            "Manage collections: add, edit active status, and delete when unused."
        )
        self.resize(760, 480)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        name_label = QLabel("Na&me:")
        self.name_edit = QLineEdit()
        self.name_edit.setAccessibleName("Collection name")
        self.name_edit.setAccessibleDescription("Enter collection name")
        name_label.setBuddy(self.name_edit)
        header_layout.addWidget(name_label)
        header_layout.addWidget(self.name_edit, 1)

        self.active_check = QCheckBox("&Active")
        self.active_check.setAccessibleName("Collection active")
        self.active_check.setAccessibleDescription("Collection active status")
        self.active_check.setChecked(True)
        header_layout.addWidget(self.active_check)

        layout.addLayout(header_layout)

        self.table = QTableWidget()
        self.table.setAccessibleName("Collections list")
        self.table.setAccessibleDescription(
            "List of collections with active status")
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Collection", "Active"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(False)
        from src.accessibility.shortcut_helpers import build_accessible_f1_popup_style
        self.table.setStyleSheet(build_accessible_f1_popup_style())
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setMinimumSectionSize(60)
        self.table.setColumnWidth(self.COL_NAME, 520)
        self.table.setColumnWidth(self.COL_ACTIVE, 120)
        self.table.currentCellChanged.connect(self.on_selection_changed)
        layout.addWidget(self.table, 1)

        footer_layout = QHBoxLayout()

        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        footer_layout.addWidget(self.status_bar, 1)

        self.new_button = QPushButton("New")
        self.new_button.clicked.connect(self.on_new)
        self.new_button.setAccessibleDescription("Create new collection")
        footer_layout.addWidget(self.new_button)

        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.on_edit)
        self.edit_button.setAccessibleDescription("Edit highlighted collection")
        footer_layout.addWidget(self.edit_button)

        self.save_button = QPushButton("&Save")
        self.save_button.clicked.connect(self.on_save)
        self.save_button.setAccessibleDescription("Save current collection")
        footer_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.on_cancel_edit)
        self.cancel_button.setAccessibleDescription("Cancel current new/edit and return to list")
        footer_layout.addWidget(self.cancel_button)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.on_delete)
        self.delete_button.setAccessibleDescription("Delete selected collection if unused")
        footer_layout.addWidget(self.delete_button)

        button_style = build_accessible_button_style(
            self.scaler.get_scaled_size(20)
        )
        for button in (
            self.new_button,
            self.edit_button,
            self.save_button,
            self.cancel_button,
            self.delete_button,
        ):
            button.setStyleSheet(button_style)
            button.installEventFilter(self)

            self.installEventFilter(self)

        layout.addLayout(footer_layout)

        QTimer.singleShot(0, self._apply_tab_order)

    def setup_shortcuts(self):
        from src.accessibility.shortcuts import get_shortcut_manager, ShortcutContext
        mgr = get_shortcut_manager()
        # Map widget IDs to callbacks for Alt+letter shortcuts
        callback_map = {
            'new_button': self.new_button.click,
            'edit_button': self.edit_button.click,
            'save_button': self.save_button.click,
            'cancel_button': self.cancel_button.click,
            'delete_button': self.delete_button.click,
            'table': self.focus_list,
        }
        mgr.register_alt_shortcuts(
            self, ShortcutContext.COLLECTION_WINDOW, callback_map)

        # Local QShortcuts for F1, Escape, Alt+/
        self.help_shortcut = QShortcut(QKeySequence("F1"), self)
        self.help_shortcut.activated.connect(self.on_show_shortcuts)

        self.escape_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.escape_shortcut.activated.connect(self.accept)

        self.status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.status_shortcut.activated.connect(self.on_read_status)

        self.name_edit.returnPressed.connect(self.on_name_edit_enter_pressed)

    def set_status(self, message: str, announce: bool = False):
        announce_status_message(self.status_bar, message, move_focus=announce)

        parent = self.parent()
        if parent and hasattr(parent, "set_status"):
            parent.set_status(message, announce=False)

    def load_collections(self, preserve_id: int | None = None, populate_editor: bool = True):
        collections = self.collection_queries.get_all(active_only=False)

        self.table.setRowCount(len(collections))
        selected_row = -1

        for row, collection in enumerate(collections):
            name_item = QTableWidgetItem(collection.name)
            name_item.setData(Qt.UserRole, collection.collection_id)
            active_item = QTableWidgetItem(
                "Yes" if collection.active else "No")

            self.table.setItem(row, self.COL_NAME, name_item)
            self.table.setItem(row, self.COL_ACTIVE, active_item)

            if preserve_id is not None and collection.collection_id == preserve_id:
                selected_row = row

        if selected_row >= 0:
            if not populate_editor:
                self.table.blockSignals(True)
            self.table.selectRow(selected_row)
            self.table.setCurrentCell(selected_row, self.COL_NAME)
            if not populate_editor:
                self.table.blockSignals(False)
                self.name_edit.clear()
            return

        if self.table.rowCount() > 0:
            if not populate_editor:
                self.table.blockSignals(True)
            self.table.selectRow(0)
            self.table.setCurrentCell(0, self.COL_NAME)
            if not populate_editor:
                self.table.blockSignals(False)
                self.name_edit.clear()
        else:
            self.on_new()

    def _set_editor_locked(self, locked: bool, clear_name: bool = False):
        self._editor_locked = locked
        self.name_edit.setEnabled(not locked)
        self.active_check.setEnabled(not locked)

        if clear_name:
            self.name_edit.clear()

        if locked:
            self.name_edit.setPlaceholderText(
                "Press Alt+N for New or Alt+E for Edit")
        else:
            self.name_edit.setPlaceholderText("")

        editing_mode = not locked
        self.new_button.setVisible(not editing_mode)
        self.edit_button.setVisible(not editing_mode)
        self.save_button.setVisible(editing_mode)
        self.cancel_button.setVisible(editing_mode)
        self.delete_button.setVisible(not editing_mode)

        self._apply_tab_order()

    def _apply_tab_order(self):
        """Apply tab order safely for currently visible controls."""
        footer_buttons = [
            self.new_button,
            self.edit_button,
            self.save_button,
            self.cancel_button,
            self.delete_button,
        ]
        visible_footer_buttons = [
            button for button in footer_buttons
            if button.isVisible() and button.isEnabled() and button.window() is self
        ]

        chain = [self.table]
        if not self._editor_locked:
            chain.extend([self.name_edit, self.active_check])
        chain.extend(visible_footer_buttons)
        chain.append(self.table)

        for first, second in zip(chain, chain[1:]):
            if first.window() is self and second.window() is self:
                self.setTabOrder(first, second)

    def _selected_collection_id(self) -> int | None:
        # Use currentRow() like backup_restore_window.py
        current_row = self.table.currentRow()
        if current_row < 0:
            return None
            
        name_item = self.table.item(current_row, self.COL_NAME)
        if name_item is None:
            return None

        data = name_item.data(Qt.UserRole)
        return int(data) if data is not None else None

    def _active_collection_count(self) -> int:
        return len(self.collection_queries.get_all(active_only=True))

    def _book_count_for_collection(self, collection_id: int) -> int:
        row = self.db.fetch_one(
            "SELECT COUNT(*) FROM books WHERE collection_id = ?",
            (collection_id,),
        )
        return int(row[0]) if row else 0

    def on_selection_changed(self, current_row: int, current_col: int, prev_row: int, prev_col: int):
        """Handle cell selection change like backup_restore_window.py"""
        if current_row < 0:
            self.current_collection_id = None
            return

        collection_id = self._selected_collection_id()
        if collection_id is None:
            return

        collection = self.collection_queries.get_by_id(collection_id)
        if collection is None:
            return

        self.current_collection_id = collection.collection_id
        if self._editor_locked:
            self.set_status(f"To edit {collection.name} press Alt+E")
            return

        self._is_new_entry_mode = False
        self.name_edit.setText(collection.name)
        self.active_check.setChecked(collection.active)
        self.set_status(
            f"Selected collection: {collection.name}."
        )

    def on_new(self):
        self.current_collection_id = None
        self._is_new_entry_mode = True
        self.table.clearSelection()
        self._set_editor_locked(False, clear_name=True)
        self.active_check.setChecked(True)
        self.name_edit.setFocus(Qt.TabFocusReason)
        self.set_status("New collection entry.")

    def on_edit(self):
        collection_id = self._selected_collection_id()
        if collection_id is None:
            self.set_status("Select a collection row to edit.", announce=True)
            return

        collection = self.collection_queries.get_by_id(collection_id)
        if collection is None:
            self.set_status(
                "Selected collection no longer exists.", announce=True)
            self.load_collections()
            return

        self.current_collection_id = collection.collection_id
        self._is_new_entry_mode = False
        self._set_editor_locked(False)
        self.name_edit.setText(collection.name)
        self.active_check.setChecked(collection.active)
        self.name_edit.setFocus(Qt.TabFocusReason)
        self.name_edit.setCursorPosition(len(self.name_edit.text()))
        self.set_status(f"Selected collection: {collection.name}.")

    def on_save(self) -> bool:
        name = self._to_proper_case(self.name_edit.text())
        self.name_edit.setText(name)
        active = self.active_check.isChecked()

        if self._editor_locked:
            self.set_status(
                "Press Alt+N for New or Alt+E for Edit.", announce=True)
            return False

        model = self.table.selectionModel()
        has_selected_row = bool(model and model.selectedRows())
        if has_selected_row and not self._is_new_entry_mode:
            selected_id = self._selected_collection_id()
            if selected_id is not None:
                self.current_collection_id = selected_id

        if not name:
            self.set_status("Collection name is required.", announce=True)
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Warning,
                title="Collection",
                text="Collection name cannot be blank.",
            )
            return False

        if self.current_collection_id is None or self._is_new_entry_mode:
            try:
                new_id = self.collection_queries.insert(
                    Collection(name=name, active=active)
                )
            except sqlite3.IntegrityError:
                exec_styled_message_box(
                    self,
                    self.scaler.get_scaled_size(20),
                    icon=QMessageBox.Warning,
                    title="Collection",
                    text="A collection with this name already exists.",
                )
                self.set_status("Duplicate collection name.", announce=True)
                return False

            self.current_collection_id = new_id
            self.load_collections(preserve_id=new_id)
            self._is_new_entry_mode = False
            self._set_editor_locked(True)
            self.set_status(f"Collection created: {name}.", announce=True)
            # Focus management: return to the new row
            QTimer.singleShot(100, lambda: self.focus_and_select_row(new_id))
            return True

        existing = self.collection_queries.get_by_id(
            self.current_collection_id)
        if existing is None:
            self.set_status(
                "Selected collection no longer exists.", announce=True)
            self.load_collections()
            return False

        if existing.active and not active and self._active_collection_count() <= 1:
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Warning,
                title="Collection",
                text="At least one collection must remain active.",
            )
            self.set_status(
                "Cannot deactivate the last active collection.", announce=True)
            return False

        try:
            self.collection_queries.update(
                Collection(
                    collection_id=self.current_collection_id,
                    name=name,
                    active=active,
                )
            )
        except sqlite3.IntegrityError:
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Warning,
                title="Collection",
                text="A collection with this name already exists.",
            )
            self.set_status("Duplicate collection name.", announce=True)
            return False

        self.load_collections(preserve_id=self.current_collection_id)
        self._set_editor_locked(True)
        self.set_status(f"Collection saved: {name}.", announce=True)
        # Focus management: return to the updated row
        QTimer.singleShot(100, lambda: self.focus_and_select_row(self.current_collection_id))
        return True

    def on_name_edit_enter_pressed(self):
        """Enter in Name field should act like Save and return focus to updated row."""
        if self.save_button.isVisible() and self.save_button.isEnabled() and self.on_save():
            QTimer.singleShot(0, self.focus_list)

    def on_cancel_edit(self):
        """Cancel current New/Edit mode and return to locked list mode."""
        preserve_id = self._selected_collection_id()
        if preserve_id is None:
            preserve_id = self.current_collection_id

        self._is_new_entry_mode = False
        self.load_collections(preserve_id=preserve_id, populate_editor=False)
        self._set_editor_locked(True)
        self.focus_list()
        self.set_status("Edit canceled.")

    def focus_list(self):
        if self.table.rowCount() > 0:
            row = self.table.currentRow()
            if row < 0:
                row = 0
            self.table.setCurrentCell(row, self.COL_NAME)
        self.table.setFocus(Qt.TabFocusReason)

    def focus_and_select_row(self, collection_id: int):
        """Focus and select a specific row by collection ID."""
        for row in range(self.table.rowCount()):
            item = self.table.item(row, self.COL_NAME)
            if item and item.data(Qt.UserRole) == collection_id:
                self.table.selectRow(row)
                self.table.setCurrentCell(row, self.COL_NAME)
                self.table.setFocus(Qt.TabFocusReason)
                break

    def on_delete(self):
        collection_id = self._selected_collection_id()
        if collection_id is None:
            self.set_status("Select a collection to delete.", announce=True)
            return

        collection = self.collection_queries.get_by_id(collection_id)
        if collection is None:
            self.set_status(
                "Selected collection no longer exists.", announce=True)
            self.load_collections()
            self._set_editor_locked(True)
            return

        if collection.active and self._active_collection_count() <= 1:
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Warning,
                title="Collection",
                text="At least one collection must remain active.",
            )
            self.set_status(
                "Cannot delete the last active collection.", announce=True)
            return

        usage_count = self._book_count_for_collection(collection.collection_id)
        if usage_count > 0:
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Warning,
                title="Collection",
                text=f"Cannot delete '{collection.name}' because {usage_count} book{'s' if usage_count != 1 else ''} use it.",
            )
            self.set_status(
                "Delete blocked: collection is in use.", announce=True)
            return

        answer = exec_styled_message_box(
            self,
            self.scaler.get_scaled_size(20),
            icon=QMessageBox.Question,
            title="Delete Collection",
            text=f"Delete collection '{collection.name}'?",
            buttons=QMessageBox.Yes | QMessageBox.No,
            default_button=QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            self.set_status("Delete canceled.")
            return

        self.collection_queries.delete(collection.collection_id)
        self.current_collection_id = None
        self.load_collections()
        self._set_editor_locked(True)
        self.set_status(
            f"Collection deleted: {collection.name}.", announce=True)

    def on_read_status(self):
        message = self.status_bar.currentMessage().strip() or "Ready"
        if QAccessible.isActive():
            self.set_status(message, announce=True)
            return

        exec_styled_message_box(
            self,
            self.scaler.get_scaled_size(20),
            icon=QMessageBox.Information,
            title="Status",
            text=f"No screen reader active.\n\nStatus: {message}",
        )

    def on_show_shortcuts(self):
        """Show keyboard shortcuts help dialog (accessible, centralized)."""
        from src.accessibility.shortcut_helpers import get_accessible_shortcuts_list, build_accessible_f1_popup_style
        shortcuts = [
            ("Alt+B", "Jump to list"),
            ("Alt+N", "New"),
            ("Alt+E", "Edit selected row"),
            ("Alt+S", "Save"),
            ("Alt+D", "Delete"),
            ("Escape", "Close window"),
            ("Alt+/", "Read status bar"),
            ("F1", "Show this help"),
        ]
        filtered_shortcuts = get_accessible_shortcuts_list(shortcuts)

        dlg = QDialog(self)
        dlg.setWindowTitle("Keyboard Shortcuts - Collection")
        dlg.setAccessibleName("Keyboard Shortcuts")
        dlg.resize(460, 500)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        table = QTableWidget()
        table.setAccessibleName("Shortcuts list")
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels([""])
        table.setRowCount(len(filtered_shortcuts))
        table.setVerticalHeaderLabels([""] * len(filtered_shortcuts))
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setTabKeyNavigation(False)
        table.setAlternatingRowColors(False)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setStyleSheet(build_accessible_f1_popup_style())

        for row, (key, description) in enumerate(filtered_shortcuts):
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

        dlg.exec()

    def eventFilter(self, source, event):
        """Filter events for Alt+key handling - PROVEN accessibility pattern."""
        if event.type() == QEvent.KeyPress:
            if is_unmapped_alt_letter(event, self.ALLOWED_ALT_LETTERS):
                QApplication.beep()
                return True
        return super().eventFilter(source, event)
