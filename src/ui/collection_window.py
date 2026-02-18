"""Collection management window."""

from __future__ import annotations

import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut, QAccessible
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
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

from accessibility.accessible_events import announce_status_message
from accessibility.scaling import UIScaler
from accessibility.theme_manager import ThemeManager
from database import Collection, CollectionQueries, DatabaseManager


class CollectionWindow(QDialog):
    """Window for adding, editing, and deleting collections."""

    COL_NAME = 0
    COL_ACTIVE = 1

    def __init__(self, db: DatabaseManager, scaler: UIScaler, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)

        self.db = db
        self.scaler = scaler
        self.theme_manager = theme_manager
        self.collection_queries = CollectionQueries(db)

        self.current_collection_id: int | None = None

        self.setup_ui()
        self.setup_shortcuts()
        self.load_collections()

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

        name_label = QLabel("&Name:")
        self.name_edit = QLineEdit()
        self.name_edit.setAccessibleName("Collection name")
        self.name_edit.setAccessibleDescription(
            "Enter collection name - Alt+N")
        name_label.setBuddy(self.name_edit)
        header_layout.addWidget(name_label)
        header_layout.addWidget(self.name_edit, 1)

        self.active_check = QCheckBox("&Active")
        self.active_check.setAccessibleName("Collection active")
        self.active_check.setAccessibleDescription(
            "Collection active status - Alt+A")
        self.active_check.setChecked(True)
        header_layout.addWidget(self.active_check)

        layout.addLayout(header_layout)

        self.table = QTableWidget()
        self.table.setAccessibleName("Collections list")
        self.table.setAccessibleDescription(
            "List of collections with active status")
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Collection", "Active"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(
            """
            QTableView::item:selected,
            QTableView::item:selected:active,
            QTableView::item:selected:!active {
                border: none;
                outline: none;
            }
            QTableView::item:focus {
                border: none;
                outline: none;
            }
            QTableWidget::item:selected,
            QTableWidget::item:selected:focus {
                border: none;
                outline: none;
            }
            QTableWidget:focus {
                border: none;
                outline: none;
            }
            """
        )
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setMinimumSectionSize(60)
        self.table.setColumnWidth(self.COL_NAME, 520)
        self.table.setColumnWidth(self.COL_ACTIVE, 120)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.table, 1)

        footer_layout = QHBoxLayout()

        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        footer_layout.addWidget(self.status_bar, 1)

        self.new_button = QPushButton("&New")
        self.new_button.clicked.connect(self.on_new)
        self.new_button.setAccessibleDescription(
            "Create a new collection entry - Alt+N")
        footer_layout.addWidget(self.new_button)

        self.save_button = QPushButton("Sa&ve")
        self.save_button.clicked.connect(self.on_save)
        self.save_button.setAccessibleDescription(
            "Save current collection - Alt+V")
        footer_layout.addWidget(self.save_button)

        self.delete_button = QPushButton("&Delete")
        self.delete_button.clicked.connect(self.on_delete)
        self.delete_button.setAccessibleDescription(
            "Delete selected collection if unused - Alt+D")
        footer_layout.addWidget(self.delete_button)

        self.close_button = QPushButton("&Close")
        self.close_button.clicked.connect(self.accept)
        self.close_button.setAccessibleDescription(
            "Close collection window - Alt+C")
        footer_layout.addWidget(self.close_button)

        layout.addLayout(footer_layout)

    def setup_shortcuts(self):
        self.help_shortcut = QShortcut(QKeySequence("F1"), self)
        self.help_shortcut.activated.connect(self.on_show_shortcuts)

        self.status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.status_shortcut.activated.connect(self.on_read_status)

    def set_status(self, message: str, announce: bool = False):
        announce_status_message(self.status_bar, message, move_focus=announce)

        parent = self.parent()
        if parent and hasattr(parent, "set_status"):
            parent.set_status(message, announce=False)

    def load_collections(self, preserve_id: int | None = None):
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
            self.table.selectRow(selected_row)
            self.table.setCurrentCell(selected_row, self.COL_NAME)
            return

        if self.table.rowCount() > 0:
            self.table.selectRow(0)
            self.table.setCurrentCell(0, self.COL_NAME)
        else:
            self.on_new()

    def _selected_collection_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0:
            return None

        name_item = self.table.item(row, self.COL_NAME)
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

    def on_selection_changed(self):
        collection_id = self._selected_collection_id()
        if collection_id is None:
            return

        collection = self.collection_queries.get_by_id(collection_id)
        if collection is None:
            return

        self.current_collection_id = collection.collection_id
        self.name_edit.setText(collection.name)
        self.active_check.setChecked(collection.active)
        self.set_status(
            f"Selected collection: {collection.name}."
        )

    def on_new(self):
        self.current_collection_id = None
        self.table.clearSelection()
        self.name_edit.clear()
        self.active_check.setChecked(True)
        self.name_edit.setFocus(Qt.TabFocusReason)
        self.set_status("New collection entry.")

    def on_save(self):
        name = self.name_edit.text().strip()
        active = self.active_check.isChecked()

        if not name:
            self.set_status("Collection name is required.", announce=True)
            QMessageBox.warning(self, "Collection",
                                "Collection name cannot be blank.")
            return

        if self.current_collection_id is None:
            try:
                new_id = self.collection_queries.insert(
                    Collection(name=name, active=active)
                )
            except sqlite3.IntegrityError:
                QMessageBox.warning(
                    self,
                    "Collection",
                    "A collection with this name already exists.",
                )
                self.set_status("Duplicate collection name.", announce=True)
                return

            self.current_collection_id = new_id
            self.load_collections(preserve_id=new_id)
            self.set_status(f"Collection created: {name}.", announce=True)
            return

        existing = self.collection_queries.get_by_id(
            self.current_collection_id)
        if existing is None:
            self.set_status(
                "Selected collection no longer exists.", announce=True)
            self.load_collections()
            return

        if existing.active and not active and self._active_collection_count() <= 1:
            QMessageBox.warning(
                self,
                "Collection",
                "At least one collection must remain active.",
            )
            self.set_status(
                "Cannot deactivate the last active collection.", announce=True)
            return

        try:
            self.collection_queries.update(
                Collection(
                    collection_id=self.current_collection_id,
                    name=name,
                    active=active,
                )
            )
        except sqlite3.IntegrityError:
            QMessageBox.warning(
                self,
                "Collection",
                "A collection with this name already exists.",
            )
            self.set_status("Duplicate collection name.", announce=True)
            return

        self.load_collections(preserve_id=self.current_collection_id)
        self.set_status(f"Collection saved: {name}.", announce=True)

    def on_delete(self):
        if self.current_collection_id is None:
            self.set_status("Select a collection to delete.", announce=True)
            return

        collection = self.collection_queries.get_by_id(
            self.current_collection_id)
        if collection is None:
            self.set_status(
                "Selected collection no longer exists.", announce=True)
            self.load_collections()
            return

        if collection.active and self._active_collection_count() <= 1:
            QMessageBox.warning(
                self,
                "Collection",
                "At least one collection must remain active.",
            )
            self.set_status(
                "Cannot delete the last active collection.", announce=True)
            return

        usage_count = self._book_count_for_collection(collection.collection_id)
        if usage_count > 0:
            QMessageBox.warning(
                self,
                "Collection",
                f"Cannot delete '{collection.name}' because {usage_count} book{'s' if usage_count != 1 else ''} use it.",
            )
            self.set_status(
                "Delete blocked: collection is in use.", announce=True)
            return

        answer = QMessageBox.question(
            self,
            "Delete Collection",
            f"Delete collection '{collection.name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            self.set_status("Delete canceled.")
            return

        self.collection_queries.delete(collection.collection_id)
        self.current_collection_id = None
        self.load_collections()
        self.set_status(
            f"Collection deleted: {collection.name}.", announce=True)

    def on_read_status(self):
        message = self.status_bar.currentMessage().strip() or "Ready"
        if QAccessible.isActive():
            self.set_status(message, announce=True)
            return

        QMessageBox.information(
            self,
            "Status",
            f"No screen reader active.\n\nStatus: {message}",
        )

    def on_show_shortcuts(self):
        shortcuts = [
            "F1: Keyboard shortcuts",
            "Alt+/: Read status",
            "Alt+N: Collection name",
            "Alt+A: Active checkbox",
            "Alt+V: Save",
            "Alt+D: Delete",
            "Alt+C: Close",
        ]
        QMessageBox.information(
            self,
            "Keyboard Shortcuts - Collection Window",
            "\n".join(shortcuts),
        )
