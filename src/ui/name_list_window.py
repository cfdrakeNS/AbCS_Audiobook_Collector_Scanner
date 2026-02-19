"""Reusable manager window for authors, genres, series, and collections."""

from __future__ import annotations

import sqlite3
from typing import Literal

from PySide6.QtCore import Qt, QEvent, QTimer
from PySide6.QtGui import QKeySequence, QShortcut, QAccessible
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
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
    QHeaderView,
)

from accessibility.accessible_events import announce_status_message
from accessibility.scaling import UIScaler
from accessibility.style_helpers import build_accessible_button_style, exec_styled_message_box
from accessibility.theme_manager import ThemeManager
from database import (
    DatabaseManager,
    AuthorQueries,
    GenreQueries,
    SeriesQueries,
    CollectionQueries,
    Collection,
)

NameListType = Literal["author", "genre", "series", "collection"]


class NameListWindow(QDialog):
    """Window for adding, editing, and deleting names in reference tables."""

    COL_NAME = 0
    COL_ACTIVE = 1
    COL_USAGE = 2

    def __init__(
        self,
        db: DatabaseManager,
        scaler: UIScaler,
        theme_manager: ThemeManager,
        list_type: NameListType,
        initial_name: str | None = None,
        parent=None,
    ):
        super().__init__(parent)

        self.db = db
        self.scaler = scaler
        self.theme_manager = theme_manager
        self.list_type = list_type
        self.initial_name = (initial_name or "").strip()
        self.current_item_id: int | None = None
        self._last_find_row = -1

        self._configure_type_metadata()

        self.setup_ui()
        self.setup_shortcuts()
        self.load_items()

        focused_initial_match = False
        if self.initial_name:
            self.find_edit.setText(self.initial_name)
            focused_initial_match = self.find_first_match(self.initial_name)
            if focused_initial_match:
                self.focus_list()
                self.find_edit.clear()

        self.setWindowTitle(f"{self.entity_plural} Manager")
        self.setAccessibleName(f"{self.entity_plural} Manager")
        self.setAccessibleDescription(
            f"Manage {self.entity_plural.lower()}: add, edit, and delete when unused."
        )
        self.resize(720, 480)

        self.table.installEventFilter(self)
        self.find_edit.installEventFilter(self)
        self.name_edit.installEventFilter(self)
        if not focused_initial_match:
            QTimer.singleShot(
                0, lambda: self.find_edit.setFocus(Qt.TabFocusReason))

    def _configure_type_metadata(self):
        self.is_collection_mode = False
        self.is_author_mode = self.list_type == "author"

        if self.list_type == "author":
            self.entity_singular = "Author"
            self.entity_plural = "Authors"
            self.id_column = "author_id"
            self.book_fk_column = "author_id"
            self.query = AuthorQueries(self.db)
            return

        if self.list_type == "genre":
            self.entity_singular = "Genre"
            self.entity_plural = "Genres"
            self.id_column = "genre_id"
            self.book_fk_column = "genre_id"
            self.query = GenreQueries(self.db)
            return

        if self.list_type == "collection":
            self.entity_singular = "Collection"
            self.entity_plural = "Collections"
            self.id_column = "collection_id"
            self.book_fk_column = "collection_id"
            self.query = CollectionQueries(self.db)
            self.is_collection_mode = True
            return

        self.entity_singular = "Series"
        self.entity_plural = "Series"
        self.id_column = "series_id"
        self.book_fk_column = "series_id"
        self.query = SeriesQueries(self.db)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        find_label = QLabel("&Find:")
        self.find_edit = QLineEdit()
        self.find_edit.setAccessibleName(f"Find {self.entity_plural.lower()}")
        self.find_edit.setAccessibleDescription(
            f"Type to jump to matching {self.entity_singular.lower()} - Alt+F"
        )
        find_label.setBuddy(self.find_edit)
        header_layout.addWidget(find_label)
        header_layout.addWidget(self.find_edit, 1)

        name_label = QLabel("Name &Edit:")
        self.name_edit = QLineEdit()
        self.name_edit.setAccessibleName(f"{self.entity_singular} name")
        self.name_edit.setAccessibleDescription(
            f"Edit {self.entity_singular.lower()} name - Alt+E"
        )
        name_label.setBuddy(self.name_edit)
        header_layout.addWidget(name_label)
        header_layout.addWidget(self.name_edit, 1)

        if self.is_collection_mode:
            self.active_check = QCheckBox("&Active")
            self.active_check.setAccessibleName("Collection active")
            self.active_check.setAccessibleDescription(
                "Collection active status - Alt+A"
            )
            self.active_check.setChecked(True)
            header_layout.addWidget(self.active_check)

        layout.addLayout(header_layout)

        self.table = QTableWidget()
        self.table.setAccessibleName(f"{self.entity_plural} list")
        self.table.setAccessibleDescription(
            f"List of {self.entity_plural.lower()} and book usage"
        )
        if self.is_collection_mode:
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels(
                [self.entity_singular, "Active", "Books"])
        else:
            self.table.setColumnCount(2)
            self.table.setHorizontalHeaderLabels(
                [self.entity_singular, "Books"])
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
        self.table.setColumnWidth(
            self.COL_NAME, 460 if self.is_collection_mode else 520)
        if self.is_collection_mode:
            self.table.setColumnWidth(self.COL_ACTIVE, 120)
        self.table.setColumnWidth(self.COL_USAGE, 90)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.table, 1)

        footer_layout = QHBoxLayout()

        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        footer_layout.addWidget(self.status_bar, 1)

        self.new_button = QPushButton("&New")
        self.new_button.clicked.connect(self.on_new)
        self.new_button.setAccessibleDescription(
            f"Create a new {self.entity_singular.lower()} entry - Alt+N"
        )
        footer_layout.addWidget(self.new_button)

        self.save_button = QPushButton("Sa&ve")
        self.save_button.clicked.connect(self.on_save)
        self.save_button.setAccessibleDescription(
            f"Save current {self.entity_singular.lower()} - Alt+V"
        )
        footer_layout.addWidget(self.save_button)

        self.delete_button = QPushButton("&Delete")
        self.delete_button.clicked.connect(self.on_delete)
        self.delete_button.setAccessibleDescription(
            f"Delete selected {self.entity_singular.lower()} if unused - Alt+D"
        )
        footer_layout.addWidget(self.delete_button)

        if self.is_author_mode:
            self.new_button.setVisible(False)
            self.delete_button.setVisible(False)
            self.new_button.setEnabled(False)
            self.delete_button.setEnabled(False)

        self.close_button = QPushButton("&Close")
        self.close_button.clicked.connect(self.accept)
        self.close_button.setAccessibleDescription(
            f"Close {self.entity_singular.lower()} window - Alt+C"
        )
        footer_layout.addWidget(self.close_button)

        button_style = build_accessible_button_style(
            self.scaler.get_scaled_size(20)
        )
        for button in (
            self.new_button,
            self.save_button,
            self.delete_button,
            self.close_button,
        ):
            button.setStyleSheet(button_style)

        layout.addLayout(footer_layout)

        self.setTabOrder(self.find_edit, self.name_edit)
        if self.is_collection_mode:
            self.setTabOrder(self.name_edit, self.active_check)
            self.setTabOrder(self.active_check, self.table)
        else:
            self.setTabOrder(self.name_edit, self.table)
        if self.is_author_mode:
            self.setTabOrder(self.table, self.save_button)
            self.setTabOrder(self.save_button, self.close_button)
        else:
            self.setTabOrder(self.table, self.new_button)
            self.setTabOrder(self.new_button, self.save_button)
            self.setTabOrder(self.save_button, self.delete_button)
            self.setTabOrder(self.delete_button, self.close_button)
        self.setTabOrder(self.close_button, self.find_edit)

    def eventFilter(self, source, event):
        """Allow Tab/Shift+Tab to move focus out of table to footer controls."""
        if event.type() == QEvent.FocusIn and isinstance(source, QLineEdit):
            QTimer.singleShot(
                0,
                lambda w=source: (
                    w.deselect(),
                    w.setCursorPosition(len(w.text()))
                )
            )

        if source == self.table and event.type() == QEvent.KeyPress:
            key = event.key()
            if key == Qt.Key_Tab and not (event.modifiers() & Qt.ShiftModifier):
                next_footer_button = self.new_button
                for button in (
                    self.new_button,
                    self.save_button,
                    self.delete_button,
                    self.close_button,
                ):
                    if button.isVisible() and button.isEnabled():
                        next_footer_button = button
                        break
                next_footer_button.setFocus(Qt.TabFocusReason)
                return True
            if key in (Qt.Key_Backtab, Qt.Key_Tab) and (event.modifiers() & Qt.ShiftModifier):
                if self.is_collection_mode:
                    self.active_check.setFocus(Qt.BacktabFocusReason)
                else:
                    self.name_edit.setFocus(Qt.BacktabFocusReason)
                return True

        return super().eventFilter(source, event)

    def setup_shortcuts(self):
        self.help_shortcut = QShortcut(QKeySequence("F1"), self)
        self.help_shortcut.activated.connect(self.on_show_shortcuts)

        self.status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.status_shortcut.activated.connect(self.on_read_status)

        self.find_next_shortcut = QShortcut(QKeySequence("F3"), self)
        self.find_next_shortcut.activated.connect(self.find_next_match)

        self.find_prev_shortcut = QShortcut(QKeySequence("Shift+F3"), self)
        self.find_prev_shortcut.activated.connect(self.find_previous_match)

        self.list_shortcut = QShortcut(QKeySequence("Alt+B"), self)
        self.list_shortcut.activated.connect(self.focus_list)

        self.find_edit.textChanged.connect(self.on_find_text_changed)
        self.find_edit.returnPressed.connect(self.on_find_enter_pressed)

    def set_status(self, message: str, announce: bool = False):
        announce_status_message(self.status_bar, message, move_focus=announce)

        parent = self.parent()
        if parent and hasattr(parent, "set_status"):
            parent.set_status(message, announce=False)

    def _book_count_for_item(self, item_id: int) -> int:
        query = f"SELECT COUNT(*) FROM books WHERE {self.book_fk_column} = ?"
        row = self.db.fetch_one(query, (item_id,))
        return int(row[0]) if row else 0

    def _active_collection_count(self) -> int:
        if not self.is_collection_mode:
            return 0
        return len(self.query.get_all(active_only=True))

    def load_items(self, preserve_id: int | None = None):
        if self.is_collection_mode:
            items = self.query.get_all(active_only=False)
        else:
            items = self.query.get_all()

        self.table.setRowCount(len(items))
        selected_row = -1

        for row, item in enumerate(items):
            item_id = getattr(item, self.id_column)
            name_item = QTableWidgetItem(item.name)
            name_item.setData(Qt.UserRole, item_id)
            name_item.setData(Qt.AccessibleTextRole, item.name)

            usage_count = self._book_count_for_item(item_id)
            usage_item = QTableWidgetItem(str(usage_count))
            usage_item.setTextAlignment(Qt.AlignCenter)

            self.table.setItem(row, self.COL_NAME, name_item)
            if self.is_collection_mode:
                active_item = QTableWidgetItem("Yes" if item.active else "No")
                active_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, self.COL_ACTIVE, active_item)
            self.table.setItem(row, self.COL_USAGE, usage_item)

            if preserve_id is not None and item_id == preserve_id:
                selected_row = row

        if selected_row >= 0:
            self.table.selectRow(selected_row)
            self.table.setCurrentCell(selected_row, self.COL_NAME)
            return

        if self.table.rowCount() > 0:
            self.table.selectRow(0)
            self.table.setCurrentCell(0, self.COL_NAME)
        else:
            if self.is_author_mode:
                self.current_item_id = None
                self.name_edit.clear()
                self.set_status("No authors available.", announce=True)
            else:
                self.on_new()

    def _selected_item_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0:
            return None

        name_item = self.table.item(row, self.COL_NAME)
        if name_item is None:
            return None

        data = name_item.data(Qt.UserRole)
        return int(data) if data is not None else None

    def on_selection_changed(self):
        item_id = self._selected_item_id()
        if item_id is None:
            return

        item = self.query.get_by_id(item_id)
        if item is None:
            return

        self.current_item_id = item_id
        self.name_edit.setText(item.name)
        if self.is_collection_mode:
            self.active_check.setChecked(bool(item.active))
        self._set_edit_hint_status(item.name)

    def on_new(self):
        if self.is_author_mode:
            self.set_status("New author entries are disabled.", announce=True)
            return

        self.current_item_id = None
        self.table.clearSelection()
        self.name_edit.clear()
        if self.is_collection_mode:
            self.active_check.setChecked(True)
        self.name_edit.setFocus(Qt.TabFocusReason)
        self.set_status(f"New {self.entity_singular.lower()} entry.")

    def on_save(self):
        name = self.name_edit.text().strip()
        active = self.active_check.isChecked() if self.is_collection_mode else True

        if not name:
            self.set_status(
                f"{self.entity_singular} name is required.", announce=True)
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Warning,
                title=self.entity_singular,
                text=f"{self.entity_singular} name cannot be blank.",
            )
            return

        if self.current_item_id is None:
            if self.is_author_mode:
                self.set_status(
                    "Authors can only be corrected, not created here.", announce=True)
                return

            try:
                if self.is_collection_mode:
                    new_id = self.query.insert(
                        Collection(name=name, active=active))
                else:
                    new_id = self.query.insert(name)
            except sqlite3.IntegrityError:
                exec_styled_message_box(
                    self,
                    self.scaler.get_scaled_size(20),
                    icon=QMessageBox.Warning,
                    title=self.entity_singular,
                    text=f"A {self.entity_singular.lower()} with this name already exists.",
                )
                self.set_status(
                    f"Duplicate {self.entity_singular.lower()} name.", announce=True)
                return

            self.current_item_id = new_id
            self.load_items(preserve_id=new_id)
            self.set_status(
                f"{self.entity_singular} created: {name}.", announce=True)
            return

        if self.is_collection_mode:
            existing = self.query.get_by_id(self.current_item_id)
            if existing is None:
                self.set_status(
                    "Selected collection no longer exists.", announce=True)
                self.load_items()
                return

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
                return

        try:
            if self.is_collection_mode:
                self.query.update(
                    Collection(
                        collection_id=self.current_item_id,
                        name=name,
                        active=active,
                    )
                )
            else:
                self.query.update(self.current_item_id, name)
        except sqlite3.IntegrityError:
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Warning,
                title=self.entity_singular,
                text=f"A {self.entity_singular.lower()} with this name already exists.",
            )
            self.set_status(
                f"Duplicate {self.entity_singular.lower()} name.", announce=True)
            return

        self.load_items(preserve_id=self.current_item_id)
        self.set_status(
            f"{self.entity_singular} saved: {name}.", announce=True)

    def on_delete(self):
        if self.is_author_mode:
            self.set_status("Author deletion is disabled.", announce=True)
            return

        if self.current_item_id is None:
            self.set_status(
                f"Select a {self.entity_singular.lower()} to delete.", announce=True)
            return

        item = self.query.get_by_id(self.current_item_id)
        if item is None:
            self.set_status(
                f"Selected {self.entity_singular.lower()} no longer exists.", announce=True
            )
            self.load_items()
            return

        if self.is_collection_mode and item.active and self._active_collection_count() <= 1:
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

        usage_count = self._book_count_for_item(self.current_item_id)
        if usage_count > 0:
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Warning,
                title=self.entity_singular,
                text=f"Cannot delete '{item.name}' because {usage_count} book{'s' if usage_count != 1 else ''} use it.",
            )
            self.set_status(
                f"Delete blocked: {self.entity_singular.lower()} is in use.", announce=True
            )
            return

        answer = exec_styled_message_box(
            self,
            self.scaler.get_scaled_size(20),
            icon=QMessageBox.Question,
            title=f"Delete {self.entity_singular}",
            text=f"Delete {self.entity_singular.lower()} '{item.name}'?",
            buttons=QMessageBox.Yes | QMessageBox.No,
            default_button=QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            self.set_status("Delete canceled.")
            return

        self.query.delete(self.current_item_id)
        self.current_item_id = None
        self.load_items()
        self.set_status(
            f"{self.entity_singular} deleted: {item.name}.", announce=True)

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
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Keyboard Shortcuts - {self.entity_plural}")
        dlg.setAccessibleName("Keyboard Shortcuts")
        dlg.resize(460, 500)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        shortcuts = [
            ("Alt+/", "Read status bar"),
            ("Alt+F", "Find"),
            ("F3", "Find next"),
            ("Shift+F3", "Find previous"),
            ("Alt+E", "Name edit"),
            ("Alt+B", "Jump to list"),
            ("Alt+A", "Active checkbox") if self.is_collection_mode else None,
            ("Alt+V", "Save"),
            ("Alt+D", "Delete") if not self.is_author_mode else None,
            ("Alt+C", "Close window"),
            ("F1", "Show this help"),
        ]
        shortcuts = [item for item in shortcuts if item is not None]

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
        close_btn.setStyleSheet(
            build_accessible_button_style(self.scaler.get_scaled_size(20))
        )
        layout.addWidget(close_btn)

        dlg.exec()

    def on_find_text_changed(self, text: str):
        text = text.strip()
        if not text:
            self._last_find_row = -1
            return
        self.find_first_match(text)

    def on_find_enter_pressed(self):
        text = self.find_edit.text().strip()
        if not text:
            return

        if self.find_first_match(text):
            self.focus_list()

    def find_first_match(self, text: str) -> bool:
        text_lower = text.strip().lower()
        if not text_lower:
            return False

        for row in range(self.table.rowCount()):
            item = self.table.item(row, self.COL_NAME)
            name = item.text().strip().lower() if item else ""
            if text_lower in name:
                self._focus_row(row)
                self._last_find_row = row
                self.set_status(
                    f"Found {self.entity_singular.lower()}: {item.text()}.")
                return True

        self.set_status(
            f"No matching {self.entity_plural.lower()} for '{text}'.", announce=True)
        return False

    def find_next_match(self):
        self._find_direction(forward=True)

    def find_previous_match(self):
        self._find_direction(forward=False)

    def _find_direction(self, forward: bool):
        text = self.find_edit.text().strip().lower()
        if not text or self.table.rowCount() == 0:
            return

        start_row = self._last_find_row if self._last_find_row >= 0 else self.table.currentRow()
        if start_row < 0:
            start_row = 0

        step = 1 if forward else -1
        row_count = self.table.rowCount()
        row = start_row

        for _ in range(row_count):
            row = (row + step) % row_count
            item = self.table.item(row, self.COL_NAME)
            name = item.text().strip().lower() if item else ""
            if text in name:
                self._focus_row(row)
                self._last_find_row = row
                self.set_status(
                    f"Found {self.entity_singular.lower()}: {item.text()}.")
                return

        self.set_status(
            f"No matching {self.entity_plural.lower()} for '{self.find_edit.text().strip()}'.",
            announce=True,
        )

    def _focus_row(self, row: int):
        self.table.selectRow(row)
        self.table.setCurrentCell(row, self.COL_NAME)
        self.table.scrollToItem(self.table.item(row, self.COL_NAME))

    def focus_list(self):
        if self.table.rowCount() > 0:
            row = self.table.currentRow()
            if row < 0:
                row = 0
            self.table.setCurrentCell(row, self.COL_NAME)
            name_item = self.table.item(row, self.COL_NAME)
            if name_item:
                self._set_edit_hint_status(name_item.text())
        self.table.setFocus(Qt.TabFocusReason)

    def _set_edit_hint_status(self, item_name: str):
        name_text = (item_name or "").strip() or self.entity_singular.lower()
        self.set_status(f"To edit {name_text} name press alt+e")
