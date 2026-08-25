"""Collection management window (centralized shortcuts)."""

from __future__ import annotations

import re
import sqlite3

from PySide6.QtCore import QEvent, Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut, QAccessible
from src.ui.accessible_dialog import AccessibleDialog
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

from src.accessibility.accessible_events import (
    announce_status_message,
    announce_dialog_opened,
    announce_dialog_closed,
    configure_status_bar_accessibility,
    read_status_bar_message,
)
from src.accessibility.scaling import UIScaler
from src.accessibility.icon_helper import apply_decorative_action_icon, get_app_icon
from src.accessibility.style_helpers import (
    apply_status_bar_tooltip,
    apply_visual_tooltip_map,
    build_modern_button_style,
    build_table_polish_style,
    exec_styled_message_box,
    MESSAGE_BOX_DELETE_CONFIRM_ICONS,
)
from src.accessibility.theme_manager import ThemeManager
from src.accessibility.key_filters import is_unmapped_alt_letter
from src.accessibility.shortcuts import get_shortcut_manager, ShortcutContext
from src.database import Collection, CollectionQueries, DatabaseManager


class CollectionWindow(AccessibleDialog):
    """
    Collection management window with PROVEN accessibility foundation.

    F1, Alt+/, and Escape work out of box.
    Built incrementally from accessible skeleton.
    """

    # Alt+letter keys that are allowed to pass through (no status bar hint)
    ALLOWED_ALT_LETTERS = {"E", "L", "N", "S", "D", "/"}

    def __init__(
        self,
        db: DatabaseManager,
        scaler: UIScaler,
        theme_manager: ThemeManager,
        parent=None,
    ):
        from src.accessibility.icon_helper import get_app_icon

        super().__init__(parent)
        self.setWindowIcon(get_app_icon())

        self.db = db
        self.scaler = scaler
        self.theme_manager = theme_manager
        self.collection_queries = CollectionQueries(db)

        self.current_collection_id: int | None = None
        self._is_new_entry_mode = False
        self._editor_locked = False

        self.setup_ui()
        self.apply_visual_tooltips()
        self.setup_shortcuts()
        self.load_collections(populate_editor=False)
        self._set_editor_locked(True)
        self.name_edit.installEventFilter(self)
        # Accessibility: Tab/Shift+Tab moves focus out of table
        self.table.keyPressEvent = self.accessible_table_key_press
        QTimer.singleShot(
            0,
            lambda: self.focus_list() if self.table.rowCount() > 0 else None,
        )

        self.setWindowTitle("Collection Manager")
        self.setAccessibleName("Collection Manager")
        self.setAccessibleDescription(
            "Manage collections: add, edit active status, and delete when unused."
        )

    # Alt+letter keys that are allowed to pass through (no status bar hint)
    ALLOWED_ALT_LETTERS = {"E", "L", "N", "S", "D", "/"}

    def keyPressEvent(self, event):
        # If you want to handle Alt+D, add logic here. Otherwise, just call the base method.
        super().keyPressEvent(event)

    COL_NAME = 0
    COL_ACTIVE = 1

    def __init__(
        self,
        db: DatabaseManager,
        scaler: UIScaler,
        theme_manager: ThemeManager,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowIcon(get_app_icon())

        self.db = db
        self.scaler = scaler
        self.theme_manager = theme_manager
        self.collection_queries = CollectionQueries(db)

        self.current_collection_id: int | None = None
        self._is_new_entry_mode = False
        self._editor_locked = False

        self.setup_ui()
        self.apply_visual_tooltips()
        self.apply_control_styles()
        self.scaler.scale_changed.connect(self.on_scale_changed)
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
        self.setup_shortcuts()
        self.load_collections(populate_editor=False)
        self._set_editor_locked(True)
        self.name_edit.installEventFilter(self)
        # Accessibility: Tab/Shift+Tab moves focus out of table
        self.table.keyPressEvent = self.accessible_table_key_press
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
            "List of collections with active status. "
            "Use Up and Down arrows to move between entries."
        )
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Collection", "Active"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setTabKeyNavigation(False)
        self.table.setFocusPolicy(Qt.StrongFocus)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(False)
        vh = self.table.verticalHeader()
        vh.setVisible(False)
        vh.setAccessibleDescription("Table row headers are hidden.")
        vh.setAccessibleName("Table Row Headers")
        vh.setHighlightSections(False)
        vh.setSectionsClickable(False)
        vh.setSectionsMovable(False)
        vh.setFocusPolicy(Qt.NoFocus)
        vh.setEnabled(False)
        self.table.setVerticalHeaderLabels([])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setMinimumSectionSize(60)
        self.table.setColumnWidth(self.COL_NAME, 520)
        self.table.setColumnWidth(self.COL_ACTIVE, 120)
        self.table.currentCellChanged.connect(self.on_selection_changed)
        layout.addWidget(self.table, 1)

        footer_layout = QHBoxLayout()

        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        configure_status_bar_accessibility(self.status_bar)
        footer_layout.addWidget(self.status_bar, 1)

        self.new_button = QPushButton("New")
        self.new_button.clicked.connect(self.on_new)
        self.new_button.setAccessibleDescription("Create new collection")
        footer_layout.addWidget(self.new_button)

        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.on_edit)
        self.edit_button.setAccessibleDescription("Edit highlighted collection")
        footer_layout.addWidget(self.edit_button)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.on_save)
        self.save_button.setAccessibleDescription("Save current collection")
        footer_layout.addWidget(self.save_button)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.on_delete)
        self.delete_button.setAccessibleDescription(
            "Delete selected collection if unused"
        )
        footer_layout.addWidget(self.delete_button)

        for button in (
            self.new_button,
            self.edit_button,
            self.save_button,
            self.delete_button,
        ):
            button.setDefault(False)
            button.setAutoDefault(False)
            button.installEventFilter(self)

        self.installEventFilter(self)
        layout.addLayout(footer_layout)

        QTimer.singleShot(0, self._apply_tab_order)

    def apply_control_styles(self):
        """Modern buttons, table polish, and status bar styling."""
        from src.accessibility.shortcut_helpers import build_accessible_f1_popup_style

        scaled_height = int(20 * (self.scaler.current_scale / 100.0))
        button_style = build_modern_button_style(scaled_height)
        table_style = (
            build_accessible_f1_popup_style()
            + build_table_polish_style("QTableWidget", cell_borders=False)
            + f"""
            QTableWidget {{
                border: 1px solid palette(mid);
                border-radius: {self.scaler.get_scaled_size(5)}px;
            }}
            """
        )
        status_style = f"""
            QStatusBar {{
                border: 1px solid palette(mid);
                border-radius: {self.scaler.get_scaled_size(5)}px;
                padding: 2px 6px;
                background-color: palette(base);
            }}
        """
        checkbox_style = """
            QCheckBox::indicator,
            QCheckBox::indicator:unchecked {
                border: 2px solid palette(highlight);
                background-color: palette(base);
            }
            QCheckBox::indicator:checked {
                border: 2px solid palette(highlight);
                background-color: palette(highlight);
                image: none;
            }
            QCheckBox::indicator:disabled {
                border: 1px solid palette(mid);
                background-color: palette(window);
            }
        """

        self.save_button.setObjectName("primaryActionButton")
        self.delete_button.setObjectName("destructiveActionButton")
        self.new_button.setObjectName("")
        self.edit_button.setObjectName("")

        for button in (
            self.new_button,
            self.edit_button,
            self.save_button,
            self.delete_button,
        ):
            button.setStyleSheet(button_style)

        self.table.setStyleSheet(table_style)
        self.status_bar.setStyleSheet(status_style)
        self.active_check.setStyleSheet(checkbox_style)
        self._apply_action_button_icons()

    def _apply_action_button_icons(self):
        """Decorative icons beside footer button text."""
        apply_decorative_action_icon(self.new_button, "new", self.scaler)
        apply_decorative_action_icon(self.edit_button, "edit", self.scaler)
        apply_decorative_action_icon(self.save_button, "save", self.scaler)
        apply_decorative_action_icon(self.delete_button, "delete", self.scaler)

    def on_scale_changed(self, _scale_percentage: int):
        self.apply_control_styles()

    def on_theme_changed(self, _theme_name: str):
        self.apply_control_styles()

    def apply_visual_tooltips(self):
        """Short sighted-user tooltips paired with screen reader descriptions."""
        apply_visual_tooltip_map(
            {
                self.name_edit: "Collection name to add or edit",
                self.active_check: "Include this collection in filters when active",
                self.table: "List of collections",
                self.new_button: "Create a new collection",
                self.edit_button: "Edit the highlighted collection",
                self.save_button: "Save the current collection",
                self.delete_button: "Delete the selected collection if unused",
            }
        )
        apply_status_bar_tooltip(self.status_bar, "Collection manager status")

    def setup_shortcuts(self):
        from src.accessibility.shortcuts import get_shortcut_manager, ShortcutContext

        mgr = get_shortcut_manager()
        # Map widget IDs to callbacks for Alt+letter shortcuts
        callback_map = {
            "new_button": self.new_button.click,
            "edit_button": self.edit_button.click,
            "save_button": self.on_save,
            "delete_button": self.delete_button.click,
            "table": self.focus_list,
        }
        mgr.register_alt_shortcuts(
            self, ShortcutContext.COLLECTION_WINDOW, callback_map
        )

        # Local QShortcuts for F1, Escape, and Alt+/
        self.help_shortcut = QShortcut(QKeySequence("F1"), self)
        self.help_shortcut.activated.connect(self.on_show_shortcuts)

        from src.ui.help_router import install_shift_f1_help

        self.context_help_shortcut = install_shift_f1_help(self)

        self.escape_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.escape_shortcut.activated.connect(self.on_escape_pressed)

        self.status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.status_shortcut.activated.connect(self.on_read_status)

        self.name_edit.returnPressed.connect(self.on_name_edit_enter_pressed)

    def set_status(self, message: str, announce: bool = False):
        announce_status_message(self.status_bar, message, move_focus=announce)

        parent = self.parent()
        if parent and hasattr(parent, "set_status"):
            parent.set_status(message, announce=False)

    def load_collections(
        self, preserve_id: int | None = None, populate_editor: bool = True
    ):
        collections = self.collection_queries.get_all(active_only=False)

        self.table.setRowCount(len(collections))
        selected_row = -1

        for row, collection in enumerate(collections):
            active_label = "Yes" if collection.active else "No"
            accessible_text = f"{collection.name}, Active: {active_label}"

            name_item = QTableWidgetItem(collection.name)
            name_item.setData(Qt.UserRole, collection.collection_id)
            name_item.setData(Qt.AccessibleTextRole, accessible_text)

            active_item = QTableWidgetItem(active_label)
            active_item.setData(Qt.AccessibleTextRole, accessible_text)

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
            self.name_edit.setPlaceholderText("Press Alt+N for New or Alt+E for Edit")
        else:
            self.name_edit.setPlaceholderText("Alt+S to Save, Escape to Cancel")

        editing_mode = not locked
        self.new_button.setVisible(not editing_mode)
        self.edit_button.setVisible(not editing_mode)
        self.save_button.setVisible(editing_mode)
        self.delete_button.setVisible(not editing_mode)

        self._apply_tab_order()

    def _apply_tab_order(self):
        """Apply tab order safely for currently visible controls."""
        footer_buttons = [
            self.new_button,
            self.edit_button,
            self.save_button,
            self.delete_button,
        ]
        visible_footer_buttons = [
            button
            for button in footer_buttons
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

    def on_selection_changed(
        self, current_row: int, current_col: int, _prev_row: int, _prev_col: int
    ):
        """Handle cell selection change like backup_restore_window.py"""
        if current_row < 0:
            self.current_collection_id = None
            return

        # Clear status messages when navigating
        self.set_status("")

        collection_id = self._selected_collection_id()
        if collection_id is None:
            return

        collection = self.collection_queries.get_by_id(collection_id)
        if collection is None:
            return

        self.current_collection_id = collection.collection_id
        if self._editor_locked:
            return

        self._is_new_entry_mode = False
        self.name_edit.setText(collection.name)
        self.active_check.setChecked(collection.active)

    def on_new(self):
        self.current_collection_id = None
        self._is_new_entry_mode = True
        self.table.clearSelection()
        self._set_editor_locked(False, clear_name=True)
        self.active_check.setChecked(True)
        self.name_edit.setFocus(Qt.TabFocusReason)
        # Removed status bar Alt+key shortcut message for accessibility

    def on_edit(self):
        collection_id = self._selected_collection_id()
        if collection_id is None:
            return

        collection = self.collection_queries.get_by_id(collection_id)
        if collection is None:
            self.set_status("Selected collection no longer exists.", announce=True)
            self.load_collections()
            self._set_editor_locked(True)
            return

        self.current_collection_id = collection.collection_id
        self._is_new_entry_mode = False
        self._set_editor_locked(False, clear_name=False)
        self.name_edit.setText(collection.name)
        self.active_check.setChecked(collection.active)
        self.name_edit.setFocus(Qt.TabFocusReason)
        self.name_edit.setCursorPosition(len(self.name_edit.text()))
        # Removed status bar Alt+key shortcut message for accessibility

    def on_save(self) -> bool:
        # Always sanitize collection name before saving
        from src.core.validator import ImportValidator

        validator = ImportValidator()
        temp = {"collection": self.name_edit.text()}
        validator.sanitize_metadata(temp)
        name = temp["collection"]
        self.name_edit.setText(name)
        active = self.active_check.isChecked()

        if self._editor_locked:
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
            # Show save message with delay to override navigation clearing
            QTimer.singleShot(
                50, lambda: self.set_status(f"Collection saved: {name}.", announce=True)
            )
            # Focus management: return to the new row
            QTimer.singleShot(100, lambda nid=new_id: self.focus_and_select_row(nid))
            # Explicitly ensure button visibility is correct (last operation)
            QTimer.singleShot(150, self.ensure_normal_buttons_visible)
            return True

        existing = self.collection_queries.get_by_id(self.current_collection_id)
        if existing is None:
            self.set_status("Selected collection no longer exists.", announce=True)
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
                "Cannot deactivate the last active collection.", announce=True
            )
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
        # Show save message with delay to override navigation clearing
        QTimer.singleShot(
            50, lambda: self.set_status(f"Collection saved: {name}.", announce=True)
        )
        # Focus management: return to the updated row
        QTimer.singleShot(
            100, lambda cid=self.current_collection_id: self.focus_and_select_row(cid)
        )
        # Explicitly ensure button visibility is correct (last operation)
        QTimer.singleShot(150, self.ensure_normal_buttons_visible)
        return True

    def on_name_edit_enter_pressed(self):
        """Enter in Name field should act like Save and return focus to updated row."""
        if self.save_button.isVisible() and self.save_button.isEnabled():
            self.on_save()

    def on_escape_pressed(self):
        """Escape key - cancel edit/new mode or close window if not editing."""
        if not self._editor_locked:
            self.on_cancel_edit()
        else:
            self.accept()

    def on_cancel_edit(self):
        """Cancel current New/Edit mode and return to locked list mode."""
        preserve_id = self._selected_collection_id()
        if preserve_id is None:
            preserve_id = self.current_collection_id

        self._is_new_entry_mode = False
        self.load_collections(preserve_id=preserve_id, populate_editor=False)
        self._set_editor_locked(True)
        self.focus_list()

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

    def focus_first_item(self):
        """Focus first item in table."""
        if self.table.rowCount() > 0:
            self.table.selectRow(0)
            self.table.setCurrentCell(0, self.COL_NAME)
            self.table.setFocus(Qt.TabFocusReason)

    def ensure_normal_buttons_visible(self):
        """Ensure normal buttons are visible and save button is hidden."""
        self.save_button.setVisible(False)
        self.new_button.setVisible(True)
        self.edit_button.setVisible(True)
        self.delete_button.setVisible(True)

    def on_delete(self):
        collection_id = self._selected_collection_id()
        if collection_id is None:
            return

        collection = self.collection_queries.get_by_id(collection_id)
        if collection is None:
            self.set_status("Selected collection no longer exists.", announce=True)
            self.load_collections()
            self._set_editor_locked(True)
            return

        if collection.active and self._active_collection_count() <= 1:
            from src.accessibility.icon_helper import get_app_icon

            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Warning,
                title="Collection",
                text="At least one collection must remain active.",
                window_icon=get_app_icon(),
            )
            self.set_status("Cannot delete the last active collection.", announce=True)
            return

        usage_count = self._book_count_for_collection(collection.collection_id)
        if usage_count > 0:
            from src.accessibility.icon_helper import get_app_icon

            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Warning,
                title="Collection",
                text=f"Cannot delete '{collection.name}' because {usage_count} book{'s' if usage_count != 1 else ''} use it.",
                window_icon=get_app_icon(),
            )
            self.set_status("Delete blocked: collection is in use.", announce=True)
            return

        from src.accessibility.icon_helper import get_app_icon

        answer = exec_styled_message_box(
            self,
            self.scaler.get_scaled_size(20),
            icon=QMessageBox.Question,
            title="Delete Collection",
            text=f"Delete collection '{collection.name}'?",
            buttons=QMessageBox.Yes | QMessageBox.No,
            default_button=QMessageBox.No,
            window_icon=get_app_icon(),
            button_icon_roles=MESSAGE_BOX_DELETE_CONFIRM_ICONS,
        )
        if answer != QMessageBox.Yes:
            self.set_status("Delete canceled.")
            return

        self.collection_queries.delete(collection.collection_id)
        self.current_collection_id = None
        self.load_collections()
        self._set_editor_locked(True)
        self.set_status(f"Collection deleted: {collection.name}.", announce=True)
        # Focus management: focus first item after delete
        QTimer.singleShot(100, self.focus_first_item)

    def on_read_status(self):
        read_status_bar_message(self.status_bar, fallback="Ready")

    def on_show_shortcuts(self):
        """Show keyboard shortcuts help dialog (accessible, centralized)."""
        from src.accessibility.shortcut_helpers import (
            get_accessible_shortcuts_list,
            build_accessible_f1_popup_style,
            prepend_help_doc_shortcut,
        )

        shortcuts = [
            ("Alt+L", "Jump to list"),
            ("Alt+N", "New"),
            ("Alt+E", "Edit selected row"),
            ("Alt+S", "Save"),
            ("Alt+D", "Delete"),
            ("Escape", "Cancel edit/new or close window"),
            ("Alt+/", "Read status bar"),
            ("F1", "Show this help"),
        ]
        filtered_shortcuts = prepend_help_doc_shortcut(
            get_accessible_shortcuts_list(shortcuts)
        )

        dlg = AccessibleDialog(self)
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
        """Filter events for Alt+key handling and sanitize name field on FocusOut."""
        if event.type() == QEvent.KeyPress:
            # Handle Enter key on focused buttons (autoDefault/default are
            # disabled on these buttons, so Qt won't click them on Enter
            # unless we do it explicitly here).
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                if isinstance(source, QPushButton) and source.hasFocus():
                    source.click()
                    return True

            if is_unmapped_alt_letter(event, self.ALLOWED_ALT_LETTERS):
                QApplication.beep()
                return True

        # Always sanitize name field on FocusOut
        if source == self.name_edit and event.type() == QEvent.FocusOut:
            from src.core.validator import ImportValidator

            validator = ImportValidator()
            temp = {"collection": self.name_edit.text()}
            validator.sanitize_metadata(temp)
            sanitized = temp["collection"]
            if sanitized != self.name_edit.text():
                self.name_edit.setText(sanitized)

        return super().eventFilter(source, event)

    def accessible_table_key_press(self, event):
        """Custom key handler: Tab/Shift+Tab move focus out of table for accessibility."""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            event.accept()
            return
        if event.key() == Qt.Key_Tab and not event.modifiers() & Qt.ControlModifier:
            self.focusNextChild()
            event.accept()
            return
        elif event.key() == Qt.Key_Backtab:
            self.focusPreviousChild()
            event.accept()
            return
        # Otherwise, default table navigation
        QTableWidget.keyPressEvent(self.table, event)
