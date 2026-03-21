"""Reusable manager window for authors, genres, series, and collections."""

from __future__ import annotations

import re
import sqlite3
from typing import Literal

from PySide6.QtCore import Qt, QEvent, QSignalBlocker, QTimer
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

from src.accessibility.accessible_events import announce_status_message
from src.accessibility.scaling import UIScaler
from src.accessibility.style_helpers import build_accessible_button_style, exec_styled_message_box
from src.accessibility.shortcut_helpers import build_accessible_f1_popup_style
from src.accessibility.theme_manager import ThemeManager
from src.database import (
    DatabaseManager,
    AuthorQueries,
    GenreQueries,
    SeriesQueries,
    CollectionQueries,
    Collection,
)

NameListType = Literal["author", "genre", "series", "collection"]


class NameListWindow(QDialog):
    """Window for adding and editing names in reference tables."""

    def on_find_enter_pressed(self):
        # Trigger find on Enter in the find box
        text = self.find_edit.text()
        if text.strip():
            found = self.find_first_match(text)
            if found:
                # Focus the list after finding a match
                self.focus_list()
    
    def on_clear_find(self):
        """Clear find box and reset filter (Alt+F)"""
        self.find_edit.clear()
        # Show all rows by clearing the filter
        for row in range(self.table.rowCount()):
            self.table.setRowHidden(row, False)
        # Focus the list instead of staying in find box
        self.focus_list()
        total_count = self.table.rowCount()
        self.set_status(f"Find cleared. Showing all {total_count} {self.entity_plural.lower()}.", announce=True)

    def on_find_text_changed(self, text):
        # Real-time filtering as user types - manual implementation for QTableWidget
        search_text = text.strip().lower()
        visible_count = 0
        total_count = self.table.rowCount()
        
        for row in range(self.table.rowCount()):
            item = self.table.item(row, self.COL_NAME)
            if item:
                name = item.text().lower()
                matches = search_text in name if search_text else True
                self.table.setRowHidden(row, not matches)
                if matches:
                    visible_count += 1
        
        # Announce filter results to screen reader
        if search_text:
            if visible_count > 0:
                announce_status_message(
                    self.status_bar, 
                    f"Found {visible_count} matches for '{text}'",
                    move_focus=True
                )
                # Focus first match if exists
                for row in range(self.table.rowCount()):
                    if not self.table.isRowHidden(row):
                        self.table.selectRow(row)
                        self.table.scrollToItem(self.table.item(row, self.COL_NAME))
                        break
            else:
                announce_status_message(
                    self.status_bar, 
                    f"No matches found for '{text}'",
                    move_focus=True
                )
        else:
            # Find box cleared, show all items
            announce_status_message(
                self.status_bar, 
                f"Showing all {total_count} {self.entity_plural.lower()}",
                move_focus=True
            )

    COL_NAME = 0
    COL_ACTIVE = 1
    COL_USAGE = 2
    AUTHOR_FIND_HINT = " enter for next, alt+F new search "

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
        self._collection_editor_locked = False
        self._last_find_row = -1

        self._configure_type_metadata()

        self.setup_ui()
        self.setup_shortcuts()
        self.load_items(populate_editor=False)
        self._finalize_initial_collection_ui_state()

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
            f"Manage {self.entity_plural.lower()}: add and edit entries."
        )
        self.resize(720, 480)

        self.table.installEventFilter(self)
        if not self.is_collection_mode:
            self.find_edit.installEventFilter(self)
        self.name_edit.installEventFilter(self)
        if not focused_initial_match:
            if self.is_collection_mode:
                QTimer.singleShot(0, lambda: self.focus_list())
            else:
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

        self.find_label = find_label
        if self.is_collection_mode:
            self.find_label.setVisible(False)
            self.find_edit.setVisible(False)

        name_label = QLabel("Na&me:")
        self.name_edit = QLineEdit()
        self.name_edit.setAccessibleName(f"{self.entity_singular} name")
        self.name_edit.setAccessibleDescription(
            f"Edit {self.entity_singular.lower()} name - Alt+M"
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
        self.table.setAlternatingRowColors(False)
        self.table.setStyleSheet(build_accessible_f1_popup_style())
        self.table.verticalHeader().setVisible(False)
        self.table.setVerticalHeaderLabels([])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setMinimumSectionSize(60)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        if self.is_collection_mode:
            self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(-1, QHeaderView.ResizeToContents)
        
        # Connect proxy model to table for filtering
        # Note: For QTableWidget, we'll handle filtering differently
        # since QTableWidget doesn't work directly with QSortFilterProxyModel
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.table, 1)

        footer_layout = QHBoxLayout()

        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        footer_layout.addWidget(self.status_bar, 1)

        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.on_edit)
        self.edit_button.setAccessibleDescription(
            f"Edit highlighted {self.entity_singular.lower()} row - Alt+E"
        )
        footer_layout.addWidget(self.edit_button)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.on_save)
        self.save_button.setAccessibleDescription(
            f"Save current {self.entity_singular.lower()} - Alt+S"
        )
        footer_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Cance&l")
        self.cancel_button.clicked.connect(self.on_cancel_edit)
        self.cancel_button.setAccessibleDescription(
            f"Cancel current {self.entity_singular.lower()} edit - Alt+L"
        )
        footer_layout.addWidget(self.cancel_button)

        button_style = build_accessible_button_style(
            self.scaler.get_scaled_size(20)
        )

        for button in (
            self.edit_button,
            self.save_button,
            self.cancel_button,
        ):
            button.setStyleSheet(button_style)

        layout.addLayout(footer_layout)

        QTimer.singleShot(0, self._apply_tab_order)

    def _apply_tab_order(self):
        """Apply tab order safely for current mode and visible controls."""
        chain = []

        if self.is_collection_mode:
            chain.append(self.table)
            if self.name_edit.isVisible() and self.name_edit.isEnabled():
                chain.append(self.name_edit)
            if self.active_check.isVisible() and self.active_check.isEnabled():
                chain.append(self.active_check)
        else:
            if self.find_edit.isVisible() and self.find_edit.isEnabled():
                chain.append(self.find_edit)
            if self.name_edit.isVisible() and self.name_edit.isEnabled():
                chain.append(self.name_edit)
            chain.append(self.table)

        footer_buttons = [
            self.edit_button,
            self.save_button,
            self.cancel_button,
        ]

        chain.extend([
            button for button in footer_buttons
            if button is not None and button.isVisible() and button.isEnabled()
        ])

        if self.is_collection_mode:
            chain.append(self.table)
        elif self.find_edit.isVisible() and self.find_edit.isEnabled():
            chain.append(self.find_edit)

        for first, second in zip(chain, chain[1:]):
            if first.window() is self and second.window() is self:
                self.setTabOrder(first, second)

    def eventFilter(self, source, event):
        """Allow Tab/Shift+Tab to move focus out of table to footer controls."""
        if event.type() == QEvent.KeyPress and source in (self.name_edit, self.find_edit):
            if event.modifiers() & Qt.AltModifier:
                key = event.key()
                if Qt.Key_A <= key <= Qt.Key_Z and key not in self._allowed_alt_letter_keys():
                    event.accept()
                    return True

        if not self.is_collection_mode and source == self.find_edit and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.on_find_enter_pressed()
                return True

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
                next_footer_button = self.edit_button
                for button in (
                    self.edit_button,
                    self.save_button,
                    self.cancel_button,
                ):
                    if button is not None and button.isVisible() and button.isEnabled():
                        next_footer_button = button
                        break
                next_footer_button.setFocus(Qt.TabFocusReason)
                return True
            if key in (Qt.Key_Backtab, Qt.Key_Tab) and (event.modifiers() & Qt.ShiftModifier):
                if self.is_collection_mode:
                    if self._collection_editor_locked:
                        self.edit_button.setFocus(Qt.BacktabFocusReason)
                    else:
                        self.active_check.setFocus(Qt.BacktabFocusReason)
                else:
                    self.name_edit.setFocus(Qt.BacktabFocusReason)
                return True

        return super().eventFilter(source, event)

    def _allowed_alt_letter_keys(self) -> set[int]:
        keys = {
            Qt.Key_B,
            Qt.Key_E,
            Qt.Key_L,
            Qt.Key_M,
            Qt.Key_S,
        }
        if not self.is_collection_mode:
            keys.add(Qt.Key_F)
        if self.is_collection_mode:
            keys.add(Qt.Key_A)
        return keys

    def setup_shortcuts(self):
        from src.accessibility.shortcuts import get_shortcut_manager, ShortcutContext
        mgr = get_shortcut_manager()
        callback_map = {
            'table': self.focus_list,
            'save_button': self.on_save,
            'edit_button': self.on_edit,
            'name_edit': self.focus_name_edit,
            'find_edit': self.on_clear_find if not self.is_collection_mode else self.focus_find_edit,
            'active_check': self.focus_active_check if hasattr(self, 'active_check') else lambda: None,
            'cancel_button': self.on_cancel_edit,
        }
        mgr.register_alt_shortcuts(
            self, ShortcutContext.NAMELIST_WINDOW, callback_map)

        # Local QShortcuts for Alt+/, F1, and Escape
        se_shortcut = QShortcut(QKeySequence("F1"), self)
        se_shortcut.activated.connect(self.on_show_shortcuts)

        self.status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.status_shortcut.activated.connect(self.on_read_status)

        self.escape_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.escape_shortcut.activated.connect(self.accept)

        # Add direct Alt+F shortcut for clearing find
        if not self.is_collection_mode:
            self.clear_find_shortcut = QShortcut(QKeySequence("Alt+F"), self)
            self.clear_find_shortcut.activated.connect(self.on_clear_find)

        if not self.is_collection_mode:
            self.find_edit.textChanged.connect(self.on_find_text_changed)
            self.find_edit.returnPressed.connect(self.on_find_enter_pressed)
        self.name_edit.returnPressed.connect(self.on_name_edit_enter_pressed)

    def focus_name_edit(self):
        self.name_edit.setFocus(Qt.ShortcutFocusReason)

    def focus_find_edit(self):
        self.find_edit.setFocus(Qt.ShortcutFocusReason)

    def focus_active_check(self):
        if hasattr(self, 'active_check'):
            self.active_check.setFocus(Qt.ShortcutFocusReason)

    def set_status(self, message: str, announce: bool = False):
        message = self._format_status_message(message)
        announce_status_message(self.status_bar, message, move_focus=announce)

        parent = self.parent()
        if parent and hasattr(parent, "set_status"):
            parent.set_status(message, announce=False)

    def _format_status_message(self, message: str) -> str:
        text = (message or "").strip()
        if not text:
            return text

        if "Alt+E" in text:
            return text

        is_find_message = (
            text.startswith("Found ")
            or text.startswith("No matching ")
            or self.AUTHOR_FIND_HINT.strip() in text
        )
        if is_find_message:
            return text

        is_edit_mode = (
            bool(getattr(self, "save_button", None))
            and self.save_button.isVisible()
            and self.name_edit.isEnabled()
        )
        if is_edit_mode:
            return text

        return f"{text} Alt+E"

    def _book_count_for_item(self, item_id: int) -> int:
        query = f"SELECT COUNT(*) FROM books WHERE {self.book_fk_column} = ?"
        row = self.db.fetch_one(query, (item_id,))
        return int(row[0]) if row else 0

    def _usage_column(self) -> int:
        return self.COL_USAGE if self.is_collection_mode else self.COL_ACTIVE

    def _active_collection_count(self) -> int:
        if not self.is_collection_mode:
            return 0
        return len(self.query.get_all(active_only=True))

    def load_items(self, preserve_id: int | None = None, populate_editor: bool = True):
        if self.is_collection_mode:
            items = self.query.get_all(active_only=False)
        else:
            items = self.query.get_all()

        selected_row = -1
        target_row = -1
        selection_model = self.table.selectionModel()
        table_model = self.table.model()
        table_blocker = QSignalBlocker(self.table)
        selection_blocker = QSignalBlocker(
            selection_model) if selection_model else None
        model_blocker = QSignalBlocker(table_model) if table_model else None
        self.table.setUpdatesEnabled(False)
        try:
            self.table.setRowCount(len(items))
            self.table.setVerticalHeaderLabels([""] * len(items))

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
                    active_item = QTableWidgetItem(
                        "Yes" if item.active else "No")
                    active_item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, self.COL_ACTIVE, active_item)
                self.table.setItem(row, self._usage_column(), usage_item)

                if preserve_id is not None and item_id == preserve_id:
                    selected_row = row

            if selected_row >= 0 and 0 <= selected_row < self.table.rowCount():
                target_row = selected_row
            elif self.table.rowCount() > 0:
                target_row = 0

            if target_row >= 0:
                self.table.selectRow(target_row)
                self.table.setCurrentCell(target_row, self.COL_NAME)
                if not populate_editor:
                    self.name_edit.clear()
            else:
                self.current_item_id = None
                self.name_edit.clear()
                self.set_status(
                    f"No {self.entity_plural.lower()} available.", announce=True)
        finally:
            self.table.setUpdatesEnabled(True)
            del table_blocker
            if selection_blocker is not None:
                del selection_blocker
            if model_blocker is not None:
                del model_blocker

        if target_row >= 0 and populate_editor:
            self.on_selection_changed()

    def _set_collection_editor_locked(self, locked: bool, clear_name: bool = False):
        """Lock/unlock name editor controls until Edit is chosen."""

        self._collection_editor_locked = locked
        self.name_edit.setEnabled(not locked)
        if self.is_collection_mode:
            self.active_check.setEnabled(not locked)

        if clear_name:
            self.name_edit.clear()

        if locked:
            self.name_edit.setPlaceholderText("Press Alt+E for Edit")
        else:
            self.name_edit.setPlaceholderText("")

        self._update_collection_action_buttons()

    def _update_collection_action_buttons(self):
        """Show proper actions by mode: locked list vs editing/new."""

        editing_mode = not self._collection_editor_locked
        self.edit_button.setVisible(not editing_mode)
        self.save_button.setVisible(editing_mode)
        self.cancel_button.setVisible(editing_mode)
        self._apply_tab_order()

    def _force_locked_button_state(self):
        """Force locked-mode button visibility after queued UI events."""
        self._collection_editor_locked = True
        self.edit_button.setVisible(True)
        self.save_button.setVisible(False)
        self.cancel_button.setVisible(False)
        self._apply_tab_order()

    def _selected_item_id(self) -> int | None:
        model = self.table.selectionModel()
        if not model:
            return None

        selected_rows = model.selectedRows(self.COL_NAME)
        if not selected_rows:
            return None

        row = selected_rows[0].row()

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

        if self._collection_editor_locked:
            if self.is_collection_mode:
                self.active_check.setChecked(bool(item.active))
            self._set_edit_hint_status(item.name)
            return

        self.name_edit.setText(item.name)
        if self.is_collection_mode:
            self.active_check.setChecked(bool(item.active))
        self._set_edit_hint_status(item.name)

    def on_edit(self):
        """Enable editing for the highlighted row in non-author lists."""
        item_id = self._selected_item_id()
        if item_id is None:
            self.set_status(
                f"Select a {self.entity_singular.lower()} row to edit.",
                announce=True,
            )
            return

        item = self.query.get_by_id(item_id)
        if item is None:
            self.set_status(
                f"Selected {self.entity_singular.lower()} no longer exists.",
                announce=True,
            )
            self.load_items()
            return

        self.current_item_id = item_id
        self._set_collection_editor_locked(False)
        self.name_edit.setText(item.name)
        if self.is_collection_mode:
            self.active_check.setChecked(bool(item.active))
        self.name_edit.setFocus(Qt.TabFocusReason)
        self.name_edit.selectAll()
        self._set_edit_hint_status(item.name)

    def on_save(self) -> bool:
        name = self._to_proper_case(self.name_edit.text())
        self.name_edit.setText(name)
        active = self.active_check.isChecked() if self.is_collection_mode else True

        if self._collection_editor_locked:
            self.set_status("Press Alt+E for Edit.", announce=True)
            return False

        model = self.table.selectionModel()
        has_selected_row = bool(model and model.selectedRows())
        if has_selected_row:
            selected_id = self._selected_item_id()
            if selected_id is not None:
                self.current_item_id = selected_id

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
            return False

        if self.current_item_id is None:
            self.set_status(
                f"Select a {self.entity_singular.lower()} row and press Alt+E.",
                announce=True,
            )
            return False

        if self.is_collection_mode:
            existing = self.query.get_by_id(self.current_item_id)
            if existing is None:
                self.set_status(
                    "Selected collection no longer exists.", announce=True)
                self.load_items()
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
            return False

        self.load_items(preserve_id=self.current_item_id)
        self._set_collection_editor_locked(True)
        QTimer.singleShot(0, self._force_locked_button_state)
        self.set_status(
            f"{self.entity_singular} saved: {name}.", announce=True)
        return True

    def on_name_edit_enter_pressed(self):
        """Enter in Name Edit should behave exactly like pressing Save."""
        if not (self.save_button.isVisible() and self.save_button.isEnabled()):
            return

        save_succeeded = self.on_save()
        if not save_succeeded:
            return

        self._set_collection_editor_locked(True)
        self._force_locked_button_state()
        QTimer.singleShot(0, self._force_locked_button_state)

        QTimer.singleShot(0, self.focus_list)

    def _finalize_initial_collection_ui_state(self):
        """Set initial collection mode state: list focused, editor locked."""
        self._set_collection_editor_locked(True)

    def on_read_status(self):
        message = self._build_read_status_message()
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

    def _build_read_status_message(self) -> str:
        row = self.table.currentRow()
        if row < 0:
            return self.status_bar.currentMessage().strip() or "Ready"

        name_item = self.table.item(row, self.COL_NAME)
        usage_item = self.table.item(row, self._usage_column())

        name_text = (name_item.text() if name_item else "").strip()
        usage_text = (usage_item.text() if usage_item else "0").strip() or "0"

        if not name_text:
            return self.status_bar.currentMessage().strip() or "Ready"

        return f"{name_text} - books {usage_text}, Alt+E Edit, Escape Close"

    def on_show_shortcuts(self):
        """Show keyboard shortcuts help dialog (accessible, centralized)."""
        from src.accessibility.shortcut_helpers import get_accessible_shortcuts_list, build_accessible_f1_popup_style
        shortcuts = [
            ("Alt+F", "Find") if not self.is_collection_mode else None,
            ("Alt+M", "Name edit"),
            ("Alt+E", "Edit selected row"),
            ("Alt+B", "Jump to list"),
            ("Alt+A", "Active checkbox") if self.is_collection_mode else None,
            ("Alt+S", "Save") if self.save_button.isVisible() and self.save_button.isEnabled() else None,
            ("Alt+L", "Cancel edit/new") if self.cancel_button.isVisible(
            ) and self.cancel_button.isEnabled() else None,
            ("Escape", "Close window"),
            ("Alt+/", "Read status bar"),
            ("F1", "Show this help"),
        ]
        shortcuts = [item for item in shortcuts if item is not None]
        filtered_shortcuts = get_accessible_shortcuts_list(shortcuts)

        dlg = QDialog(self)
        dlg.setWindowTitle(f"Keyboard Shortcuts - {self.entity_plural}")
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

        scale_pct = self.scaler.current_scale
        base_font_size = int(11 * (scale_pct / 100.0))
        font = table.font()
        font.setPointSize(base_font_size)
        table.setFont(font)

        layout.addWidget(table)

        dlg.exec()

    def on_cancel_edit(self):
        """Cancel current New/Edit mode and return to locked list mode."""
        preserve_id = self._selected_item_id()
        if preserve_id is None:
            preserve_id = self.current_item_id

        self.load_items(preserve_id=preserve_id, populate_editor=False)
        self._set_collection_editor_locked(True)
        self.focus_list()
        self.set_status("Edit canceled.")

    def find_first_match(self, text: str) -> bool:
        search_text = self._normalize_find_value(text)
        if not search_text:
            return False

        # Count total matches for position announcement
        total_matches = 0
        first_match_row = -1
        
        for row in range(self.table.rowCount()):
            item = self.table.item(row, self.COL_NAME)
            name = item.text() if item else ""
            
            if self._is_find_match(name, search_text, is_author_mode=self.is_author_mode):
                total_matches += 1
                if first_match_row == -1:
                    first_match_row = row

        if first_match_row >= 0:
            self._focus_row(first_match_row)
            self._last_find_row = first_match_row
            item = self.table.item(first_match_row, self.COL_NAME)
            suffix = self.AUTHOR_FIND_HINT if self.is_author_mode else ""
            
            # Enhanced announcement with position
            position_text = f"Showing match 1 of {total_matches}" if total_matches > 1 else "Showing only match"
            self.set_status(
                f"Found {self.entity_singular.lower()}: {item.text()}. {position_text}.{suffix}",
                announce=True
            )
            return True

        suffix = self.AUTHOR_FIND_HINT if self.is_author_mode else ""
        self.set_status(
            f"No matching {self.entity_plural.lower()} for '{text}'.{suffix}", announce=False)
        return False

    def find_next_match(self):
        self._find_direction(forward=True)

    def find_previous_match(self):
        self._find_direction(forward=False)

    def _find_direction(self, forward: bool):
        text = self._normalize_find_value(self.find_edit.text())
        if not text or self.table.rowCount() == 0:
            return

        # Count total matches for position announcement
        total_matches = 0
        matches_positions = []
        
        for row in range(self.table.rowCount()):
            item = self.table.item(row, self.COL_NAME)
            name = item.text() if item else ""
            if self._is_find_match(name, text, is_author_mode=self.is_author_mode):
                total_matches += 1
                matches_positions.append(row)

        if total_matches == 0:
            suffix = self.AUTHOR_FIND_HINT if self.is_author_mode else ""
            self.set_status(
                f"No matching {self.entity_plural.lower()} for '{text}'.{suffix}", announce=True)
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
            name = item.text() if item else ""
            if self._is_find_match(name, text, is_author_mode=self.is_author_mode):
                self._focus_row(row)
                self._last_find_row = row
                
                # Find current position in matches
                current_position = matches_positions.index(row) + 1
                position_text = f"Showing match {current_position} of {total_matches}"
                
                suffix = self.AUTHOR_FIND_HINT if self.is_author_mode else ""
                self.set_status(
                    f"Found {self.entity_singular.lower()}: {item.text()}. {position_text}.{suffix}",
                    announce=True
                )
                return

        suffix = self.AUTHOR_FIND_HINT if self.is_author_mode else ""
        self.set_status(
            f"No matching {self.entity_plural.lower()} for '{text}'.{suffix}", announce=True)

    def _focus_row(self, row: int):
        if row < 0 or row >= self.table.rowCount():
            return
        self.table.selectRow(row)
        self.table.setCurrentCell(row, self.COL_NAME)
        item = self.table.item(row, self.COL_NAME)
        if item is not None:
            self.table.scrollToItem(item)

    @staticmethod
    def _normalize_find_value(text: str) -> str:
        normalized = (text or "").strip().casefold()
        normalized = re.sub(r"[^\w\s]", " ", normalized)
        normalized = " ".join(normalized.split())
        return normalized

    @classmethod
    def _is_find_match(cls, candidate: str, search_text: str, *, is_author_mode: bool) -> bool:
        normalized_search = cls._normalize_find_value(search_text)
        if not normalized_search:
            return False

        normalized_candidate = cls._normalize_find_value(candidate)
        if normalized_search in normalized_candidate:
            return True

        compact_search = normalized_search.replace(" ", "")
        compact_candidate = normalized_candidate.replace(" ", "")
        if compact_search and compact_search in compact_candidate:
            return True

        if not is_author_mode:
            return False

        search_tokens = [
            token for token in normalized_search.split(" ") if token]
        return bool(search_tokens) and all(token in normalized_candidate for token in search_tokens)

    def focus_list(self):
        row_count = self.table.rowCount()
        if row_count > 0:
            row = self.table.currentRow()
            if row < 0 or row >= row_count:
                row = 0
            self.table.setCurrentCell(row, self.COL_NAME)
            name_item = self.table.item(row, self.COL_NAME)
            if name_item:
                self._set_edit_hint_status(name_item.text())
        self.table.setFocus(Qt.TabFocusReason)

    def _set_edit_hint_status(self, item_name: str):
        name_text = (item_name or "").strip() or self.entity_singular.lower()
        if self.is_collection_mode:
            self.set_status(f"To edit {name_text} press Alt+E")
        else:
            self.set_status(f"To edit {name_text} name press Alt+E")
