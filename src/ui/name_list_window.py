"""Reusable manager window for authors, genres, series, and collections."""

from __future__ import annotations

import re
import sqlite3
from typing import Literal

from PySide6.QtCore import Qt, QEvent, QSignalBlocker, QTimer
from PySide6.QtGui import QKeySequence, QShortcut, QAccessible
from src.ui.accessible_dialog import AccessibleDialog
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHeaderView,
)

from src.accessibility.accessible_events import (
    announce_status_message,
    configure_status_bar_accessibility,
    read_status_bar_message,
)
from src.accessibility.scaling import UIScaler
from src.accessibility.icon_helper import apply_decorative_action_icon
from src.accessibility.style_helpers import (
    apply_status_bar_tooltip,
    apply_visual_tooltip_map,
    build_modern_button_style,
    build_table_polish_style,
    exec_styled_message_box,
)
from src.accessibility.shortcut_helpers import build_accessible_f1_popup_style
from src.accessibility.theme_manager import ThemeManager
from src.ui.table_clipboard import copy_plain_text
from src.database import (
    DatabaseManager,
    AuthorQueries,
    GenreQueries,
    SeriesQueries,
    CollectionQueries,
    Collection,
)

NameListType = Literal["author", "genre", "series", "collection"]


class NameListWindow(AccessibleDialog):
    """Window for adding and editing names in reference tables."""

    def __init__(self, *args, **kwargs):
        from src.accessibility.icon_helper import get_app_icon

        super().__init__(*args, **kwargs)
        self.setWindowIcon(get_app_icon())

    def on_find_enter_pressed(self):
        text = self.find_edit.text()
        if not text.strip():
            return
        found = self.find_first_match(text, visible_only=True)
        if found:
            self.focus_list()
        else:
            self._apply_find_filter()
            self.find_edit.setFocus(Qt.ShortcutFocusReason)

    def on_clear_find(self):
        """Clear the current find text and reset the list (Alt+F)."""
        self.find_edit.clear()
        self._apply_find_filter()
        self.find_edit.setFocus(Qt.ShortcutFocusReason)
        total_count = self.table.rowCount()
        self.set_status(
            f"Find cleared. Showing all {total_count} {self.entity_plural.lower()}.",
            announce=False,
        )

    def _escape_from_find_to_list(self) -> None:
        """Escape in Find: clear the filter if needed and move focus to the list."""
        if self.find_edit.text().strip():
            self.find_edit.clear()
            self._apply_find_filter()
        selected = self._selected_item_id()
        if selected is not None:
            name_item = self.table.item(self.table.currentRow(), self.COL_NAME)
            name = name_item.text() if name_item else self.entity_singular.lower()
            self.set_status(name, announce=False)
        else:
            self.set_status(
                f"Showing all {self.table.rowCount()} {self.entity_plural.lower()}.",
                announce=False,
            )
        self.focus_list()

    def on_alt_f_pressed(self):
        self.on_clear_find()

    def on_find_text_changed(self, _text: str = ""):
        self._apply_find_filter()

    def _apply_find_filter(self) -> None:
        text = self.find_edit.text()
        search_text = text.strip()
        total_count = self.table.rowCount()
        visible_count = 0

        for row in range(total_count):
            self.table.setRowHidden(row, False)

        if search_text:
            for row in range(total_count):
                item = self.table.item(row, self.COL_NAME)
                name = item.text() if item else ""
                if self._row_visible_for_live_find(name, text):
                    visible_count += 1
                else:
                    self.table.setRowHidden(row, True)

        self._sync_table_focus_for_find_filter(bool(search_text))

        if search_text:
            if visible_count > 0:
                self.status_bar.showMessage(
                    f"Found {visible_count} matches for '{text}'"
                )
            else:
                self.status_bar.showMessage(f"No matches found for '{text}'")
        else:
            self.status_bar.showMessage(
                f"Showing all {total_count} {self.entity_plural.lower()}"
            )

    @staticmethod
    def _table_focus_policy_for_find_filter(has_search: bool) -> Qt.FocusPolicy:
        # StrongFocus: Tab reaches the list and Ctrl+C works after a find.
        # (has_search kept for call-site compatibility; policy no longer changes.)
        return Qt.StrongFocus

    def _sync_table_focus_for_find_filter(self, has_search: bool) -> None:
        if self.is_collection_mode:
            return
        self.table.setFocusPolicy(
            self._table_focus_policy_for_find_filter(has_search)
        )
        # Do not steal focus back to Find when the list is focused during a filter.

    COL_NAME = 0
    COL_ACTIVE = 1
    COL_USAGE = 2
    AUTHOR_FIND_HINT = " enter for next, clear and start a new search "

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

        self._configure_type_metadata()

        self.setup_ui()
        self.apply_visual_tooltips()
        self.apply_control_styles()
        self.scaler.scale_changed.connect(self.on_scale_changed)
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
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
        self.table.viewport().installEventFilter(self)
        if not self.is_collection_mode:
            self.find_edit.installEventFilter(self)
        self.name_edit.installEventFilter(self)

        if self.table.rowCount() > 0:
            initial_row = self._initial_table_row(focused_initial_match)
            if initial_row is not None:
                self.table.setCurrentCell(initial_row, self.COL_NAME)
                self.table.selectRow(initial_row)
        if focused_initial_match:
            self.table.setFocus()
        elif not self.is_collection_mode:
            self.find_edit.setFocus()
        else:
            self.table.setFocus()

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
            f"Type to jump to matching {self.entity_singular.lower()}"
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
            f"Edit {self.entity_singular.lower()} name"
        )
        name_label.setBuddy(self.name_edit)
        header_layout.addWidget(name_label)
        header_layout.addWidget(self.name_edit, 1)

        if self.is_collection_mode:
            self.active_check = QCheckBox("&Active")
            self.active_check.setAccessibleName("Collection active")
            self.active_check.setAccessibleDescription("Collection active status")
            self.active_check.setChecked(True)
            header_layout.addWidget(self.active_check)

        layout.addLayout(header_layout)

        self.table = QTableWidget()
        self.table.setAccessibleName(f"{self.entity_plural} list")
        self.table.setAccessibleDescription(
            f"List of {self.entity_plural.lower()} and book usage. "
            "Use Up and Down arrows to move between entries."
        )
        if self.is_collection_mode:
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels(
                [self.entity_singular, "Active", "Books"]
            )
        else:
            self.table.setColumnCount(2)
            self.table.setHorizontalHeaderLabels([self.entity_singular, "Books"])
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
        self.table.setShowGrid(False)
        self.table.setMouseTracking(False)
        self.table.viewport().setMouseTracking(False)
        self.table.setAttribute(Qt.WA_Hover, False)
        self.table.viewport().setAttribute(Qt.WA_Hover, False)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setMinimumSectionSize(60)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        if self.is_collection_mode:
            self.table.horizontalHeader().setSectionResizeMode(
                1, QHeaderView.ResizeToContents
            )
        self.table.horizontalHeader().setSectionResizeMode(
            -1, QHeaderView.ResizeToContents
        )

        # Connect proxy model to table for filtering
        # Note: For QTableWidget, we'll handle filtering differently
        # since QTableWidget doesn't work directly with QSortFilterProxyModel
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.cellDoubleClicked.connect(self._on_table_double_clicked)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._on_table_context_menu)
        layout.addWidget(self.table, 1)

        footer_layout = QHBoxLayout()

        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        configure_status_bar_accessibility(self.status_bar)
        footer_layout.addWidget(self.status_bar, 1)

        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.on_edit)
        self.edit_button.setAccessibleDescription(
            f"Edit highlighted {self.entity_singular.lower()} row"
        )
        footer_layout.addWidget(self.edit_button)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.on_save)
        self.save_button.setAccessibleDescription(
            f"Save current {self.entity_singular.lower()}"
        )
        footer_layout.addWidget(self.save_button)

        layout.addLayout(footer_layout)

        QTimer.singleShot(0, self._apply_tab_order)

    def apply_control_styles(self):
        """Modern buttons, table polish, and status bar styling."""
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

        self.save_button.setObjectName("primaryActionButton")
        self.edit_button.setObjectName("")

        for button in (self.edit_button, self.save_button):
            button.setStyleSheet(button_style)

        self.table.setStyleSheet(table_style)
        self.status_bar.setStyleSheet(status_style)
        self._apply_action_button_icons()

    def _apply_action_button_icons(self):
        apply_decorative_action_icon(self.edit_button, "edit", self.scaler)
        apply_decorative_action_icon(self.save_button, "save", self.scaler)

    def on_scale_changed(self, _scale_percentage: int):
        self.apply_control_styles()

    def on_theme_changed(self, _theme_name: str):
        self.apply_control_styles()

    def apply_visual_tooltips(self):
        """Short sighted-user tooltips paired with screen reader descriptions."""
        tooltip_map = {
            self.find_edit: f"Search {self.entity_plural.lower()}",
            self.name_edit: f"{self.entity_singular} name to add or edit",
            self.table: f"List of {self.entity_plural.lower()}",
            self.edit_button: f"Edit highlighted {self.entity_singular.lower()}",
            self.save_button: f"Save current {self.entity_singular.lower()}",
        }
        if hasattr(self, "active_check"):
            tooltip_map[self.active_check] = "Whether this collection is active"
        apply_visual_tooltip_map(tooltip_map)
        apply_status_bar_tooltip(self.status_bar, "Manager status")

    def _apply_tab_order(self):
        """Apply tab order safely for current mode and visible controls.

        Author/series/genre: Find, list, Name, then buttons.
        Collection: list, editor controls, then buttons.
        """
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
            chain.append(self.table)
            if self.name_edit.isVisible() and self.name_edit.isEnabled():
                chain.append(self.name_edit)

        footer_buttons = [
            self.edit_button,
            self.save_button,
        ]

        chain.extend(
            [
                button
                for button in footer_buttons
                if button is not None and button.isVisible() and button.isEnabled()
            ]
        )

        if self.is_collection_mode:
            chain.append(self.table)
        elif self.find_edit.isVisible() and self.find_edit.isEnabled():
            chain.append(self.find_edit)

        for first, second in zip(chain, chain[1:]):
            if first.window() is self and second.window() is self:
                self.setTabOrder(first, second)

    def eventFilter(self, source, event):
        """Allow Tab/Shift+Tab to move focus out of table to footer controls. Also sanitize name field on FocusOut."""
        if event.type() == QEvent.KeyPress and source in (
            self.name_edit,
            self.find_edit,
        ):
            if event.modifiers() & Qt.AltModifier:
                key = event.key()
                if (
                    Qt.Key_A <= key <= Qt.Key_Z
                    and key not in self._allowed_alt_letter_keys()
                ):
                    event.accept()
                    return True

        if (
            not self.is_collection_mode
            and source == self.find_edit
            and event.type() == QEvent.KeyPress
        ):
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                event.accept()
                self.on_find_enter_pressed()
                return True
            if event.key() == Qt.Key_Escape:
                event.accept()
                self._escape_from_find_to_list()
                return True

        if (
            event.type() == QEvent.FocusIn
            and isinstance(source, QLineEdit)
            and source is not self.find_edit
        ):
            QTimer.singleShot(
                0, lambda w=source: (w.deselect(), w.setCursorPosition(len(w.text())))
            )

        # --- Always sanitize name field on FocusOut ---
        if source == self.name_edit and event.type() == QEvent.FocusOut:
            from src.core.validator import ImportValidator

            validator = ImportValidator()
            # Map to correct field for sanitization
            field_map = {
                "author": "author",
                "genre": "genre",
                "series": "series",
                "collection": "collection",
            }
            field = field_map.get(self.list_type, "author")
            temp = {field: self.name_edit.text()}
            validator.sanitize_metadata(temp)
            sanitized = temp[field]
            if sanitized != self.name_edit.text():
                self.name_edit.setText(sanitized)

        if (
            not self.is_collection_mode
            and source in (self.table, self.table.viewport())
            and event.type() == QEvent.KeyPress
            and self.find_edit.text().strip()
            and self._route_table_typing_to_find(event)
        ):
            return True

        if source == self.table and event.type() == QEvent.KeyPress:
            key = event.key()
            if event.matches(QKeySequence.Copy):
                if self._copy_current_name():
                    event.accept()
                    return True
            if key in (Qt.Key_Return, Qt.Key_Enter):
                event.accept()
                return True
            if key == Qt.Key_Tab and not (event.modifiers() & Qt.ShiftModifier):
                # Leave the list for the name field (or first footer button).
                if self.name_edit.isVisible() and self.name_edit.isEnabled():
                    self.name_edit.setFocus(Qt.TabFocusReason)
                else:
                    next_footer_button = self.edit_button
                    for button in (
                        self.edit_button,
                        self.save_button,
                    ):
                        if (
                            button is not None
                            and button.isVisible()
                            and button.isEnabled()
                        ):
                            next_footer_button = button
                            break
                    next_footer_button.setFocus(Qt.TabFocusReason)
                return True
            if key in (Qt.Key_Backtab, Qt.Key_Tab) and (
                event.modifiers() & Qt.ShiftModifier
            ):
                if self.is_collection_mode:
                    if self._collection_editor_locked:
                        self.edit_button.setFocus(Qt.BacktabFocusReason)
                    else:
                        self.active_check.setFocus(Qt.BacktabFocusReason)
                elif self.find_edit.isVisible() and self.find_edit.isEnabled():
                    self.find_edit.setFocus(Qt.BacktabFocusReason)
                else:
                    self.name_edit.setFocus(Qt.BacktabFocusReason)
                return True

        return super().eventFilter(source, event)

    def _allowed_alt_letter_keys(self) -> set[int]:
        keys = {
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
            "table": self.focus_list,
            "save_button": self.on_save,
            "edit_button": self.on_edit,
            "name_edit": self.focus_name_edit,
            "find_edit": (
                self.on_clear_find
                if not self.is_collection_mode
                else self.focus_find_edit
            ),
            "active_check": (
                self.focus_active_check
                if hasattr(self, "active_check")
                else lambda: None
            ),
        }
        mgr.register_alt_shortcuts(self, ShortcutContext.NAMELIST_WINDOW, callback_map)

        # Local QShortcuts for Alt+/, F1, and Escape
        se_shortcut = QShortcut(QKeySequence("F1"), self)
        se_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        se_shortcut.activated.connect(self.on_show_shortcuts)

        from src.ui.help_router import install_shift_f1_help

        self.context_help_shortcut = install_shift_f1_help(
            self, shortcut_context=Qt.WidgetWithChildrenShortcut
        )

        self.status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.status_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.status_shortcut.activated.connect(self.on_read_status)

        # Escape key for cancel functionality
        self.escape_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.escape_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.escape_shortcut.activated.connect(self.on_cancel_edit)

        if not self.is_collection_mode:
            self.find_edit.textChanged.connect(self.on_find_text_changed)
        self.name_edit.returnPressed.connect(self.on_name_edit_enter_pressed)

    def focus_name_edit(self):
        self.name_edit.setFocus(Qt.ShortcutFocusReason)

    def focus_find_edit(self):
        self.find_edit.setFocus(Qt.ShortcutFocusReason)

    def focus_active_check(self):
        if hasattr(self, "active_check"):
            self.active_check.setFocus(Qt.ShortcutFocusReason)

    @staticmethod
    def _format_status_message(window, message: str) -> str:
        """Append Alt+E hint in browse mode; skip find results and edit mode."""
        msg = (message or "").strip()
        if not msg:
            return msg

        save_button = getattr(window, "save_button", None)
        name_edit = getattr(window, "name_edit", None)
        in_edit_mode = (
            save_button is not None
            and name_edit is not None
            and save_button.isVisible()
            and name_edit.isEnabled()
        )
        if in_edit_mode:
            return msg

        lower = msg.lower()
        if "no matching" in lower:
            return msg
        if "enter for next" in lower:
            return msg
        if "alt+e" in lower:
            return msg

        return f"{msg} Alt+E"

    def set_status(self, message: str, announce: bool = False):
        # Accessibility: forcibly remove ALL shortcut hints from status bar
        msg = (message or "").strip()
        import re

        # Remove all Alt+X, Ctrl+X, Enter, Escape, and any 'press ...' or 'shortcut' phrases
        msg = re.sub(r" ?Alt\+[A-Z](:[\w ]+)?", "", msg)
        msg = re.sub(r" ?Ctrl\+[A-Z](:[\w ]+)?", "", msg)
        msg = re.sub(r" ?Enter(:[\w ]+)?", "", msg)
        msg = re.sub(r" ?Escape(:[\w ]+)?", "", msg)
        msg = re.sub(r" ?[Pp]ress [^.,;]+", "", msg)
        msg = re.sub(r" ?shortcut[s]?:?[^.,;]*", "", msg)
        msg = re.sub(r" ?\([^)]+shortcut[^)]*\)", "", msg)
        msg = re.sub(r" ?\([^)]+Alt\+[^)]*\)", "", msg)
        msg = re.sub(r" ?\([^)]+Ctrl\+[^)]*\)", "", msg)
        msg = re.sub(r" ?\([^)]+Enter[^)]*\)", "", msg)
        msg = re.sub(r" ?\([^)]+Escape[^)]*\)", "", msg)
        msg = re.sub(r"[.,;: ]+$", "", msg)  # Remove trailing punctuation
        announce_status_message(self.status_bar, msg, move_focus=announce)
        parent = self.parent()
        if parent and hasattr(parent, "set_status"):
            parent.set_status(msg, announce=False)

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
        selection_blocker = QSignalBlocker(selection_model) if selection_model else None
        model_blocker = QSignalBlocker(table_model) if table_model else None
        self.table.setUpdatesEnabled(False)
        try:
            self.table.setRowCount(len(items))
            self.table.setVerticalHeaderLabels([""] * len(items))

            for row, item in enumerate(items):
                item_id = getattr(item, self.id_column)
                usage_count = self._book_count_for_item(item_id)
                active_label = None
                if self.is_collection_mode:
                    active_label = "Yes" if item.active else "No"
                accessible_text = self._row_accessible_text(
                    item.name, usage_count, active=active_label
                )

                name_item = QTableWidgetItem(item.name)
                name_item.setData(Qt.UserRole, item_id)
                name_item.setData(Qt.AccessibleTextRole, accessible_text)

                usage_item = QTableWidgetItem(str(usage_count))
                usage_item.setTextAlignment(Qt.AlignCenter)
                usage_item.setData(Qt.AccessibleTextRole, accessible_text)

                self.table.setItem(row, self.COL_NAME, name_item)
                if self.is_collection_mode:
                    active_item = QTableWidgetItem(active_label)
                    active_item.setTextAlignment(Qt.AlignCenter)
                    active_item.setData(Qt.AccessibleTextRole, accessible_text)
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
                    f"No {self.entity_plural.lower()} available.", announce=True
                )
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
        self._apply_tab_order()

    def _force_locked_button_state(self):
        """Force locked-mode button visibility after queued UI events."""
        self._collection_editor_locked = True
        self.edit_button.setVisible(True)
        self.save_button.setVisible(False)
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

    def _on_table_double_clicked(self, row: int, _column: int) -> None:
        """Double-click a row to start Edit, same as Alt+E / Edit button."""
        if row < 0:
            return
        self.table.setCurrentCell(row, self.COL_NAME)
        self.on_edit()

    def on_edit(self):
        """Enable editing for the highlighted row in non-author lists."""
        # Use currentRow() like collection_window.py
        current_row = self.table.currentRow()
        if current_row < 0:
            if self.table.rowCount() > 0:
                current_row = 0
                self.table.setCurrentCell(current_row, self.COL_NAME)
            else:
                self.set_status(
                    f"No {self.entity_singular.lower()} available to edit.",
                    announce=True,
                )
                return

        name_item = self.table.item(current_row, self.COL_NAME)
        if name_item is None:
            self.set_status(
                f"No {self.entity_singular.lower()} available to edit.",
                announce=True,
            )
            return

        data = name_item.data(Qt.UserRole)
        if data is None:
            return

        item_id = int(data)
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
        # Always sanitize name field before saving
        from src.core.validator import ImportValidator

        validator = ImportValidator()
        field_map = {
            "author": "author",
            "genre": "genre",
            "series": "series",
            "collection": "collection",
        }
        field = field_map.get(self.list_type, "author")
        temp = {field: self.name_edit.text()}
        validator.sanitize_metadata(temp)
        name = temp[field]
        # Ensure author field is sanitized even if user did not leave the field
        if field == "author":
            temp2 = {"author": name}
            validator.sanitize_metadata(temp2)
            name = temp2["author"]
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
            self.set_status(f"{self.entity_singular} name is required.", announce=True)
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
                self.set_status("Selected collection no longer exists.", announce=True)
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
                    "Cannot deactivate the last active collection.", announce=True
                )
                return False

        try:
            if self.is_collection_mode:
                self.query.update(
                    Collection(
                        collection_id=self.current_item_id,
                        name=name,
                        active=active,
                        root_path=existing.root_path or "",
                    )
                )
            else:
                current_item = self.query.get_by_id(self.current_item_id)
                if (
                    current_item
                    and current_item.name.lower() == name.lower()
                    and current_item.name != name
                ):
                    # This is just a case change - use temporary name to avoid UNIQUE constraint
                    temp_name = f"temp_{self.current_item_id}_{name}"
                    self.query.update(
                        self.current_item_id, temp_name
                    )  # Step 1: change to temp
                    self.query.update(
                        self.current_item_id, name
                    )  # Step 2: change to final case
                else:
                    existing_other = self.query.get_by_name(name)
                    other_id = (
                        getattr(existing_other, self.id_column, None)
                        if existing_other is not None
                        else None
                    )
                    if (
                        existing_other is not None
                        and other_id is not None
                        and other_id != self.current_item_id
                    ):
                        return self._merge_into_existing_name(
                            current_item, existing_other, other_id
                        )
                    # Normal update
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
                f"Duplicate {self.entity_singular.lower()} name.", announce=True
            )
            return False

        self.load_items(preserve_id=self.current_item_id, populate_editor=False)
        self._set_collection_editor_locked(True)
        QTimer.singleShot(0, self._force_locked_button_state)
        saved_id = self.current_item_id
        self.set_status(f"{self.entity_singular} saved: {name}.", announce=True)
        QTimer.singleShot(
            0, lambda item_id=saved_id: self.focus_and_select_row(item_id)
        )
        return True

    def _merge_into_existing_name(self, current_item, existing_other, other_id: int) -> bool:
        """Ask to move books onto an existing name, then merge or leave unchanged."""
        source_name = (current_item.name if current_item else "") or ""
        target_name = existing_other.name or ""
        book_count = self._book_count_for_item(self.current_item_id)
        reply = exec_styled_message_box(
            self,
            self.scaler.get_scaled_size(20),
            icon=QMessageBox.Question,
            title=self.entity_singular,
            text=(
                f"A {self.entity_singular.lower()} with this name already exists. "
                f"Update {book_count} books from {source_name} to {target_name}?"
            ),
            buttons=QMessageBox.Yes | QMessageBox.No,
            default_button=QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            self.set_status(
                f"Duplicate {self.entity_singular.lower()} name.", announce=True
            )
            return False

        updated = self.query.merge(self.current_item_id, other_id)
        result_text = (
            f"{updated} books. {self.entity_singular} changed from "
            f"{source_name} to {target_name}."
        )
        exec_styled_message_box(
            self,
            self.scaler.get_scaled_size(20),
            icon=QMessageBox.Information,
            title=self.entity_singular,
            text=result_text,
        )
        self.current_item_id = other_id
        self.load_items(preserve_id=other_id, populate_editor=False)
        self._set_collection_editor_locked(True)
        QTimer.singleShot(0, self._force_locked_button_state)
        self.set_status(result_text, announce=True)
        QTimer.singleShot(
            0, lambda item_id=other_id: self.focus_and_select_row(item_id)
        )
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

    def _finalize_initial_collection_ui_state(self):
        """Set initial collection mode state: list focused, editor locked."""
        self._set_collection_editor_locked(True)
        # Note: focus is handled by the main __init__ logic

    def on_read_status(self):
        read_status_bar_message(self.status_bar, fallback="Ready")

    def on_show_shortcuts(self):
        """Show keyboard shortcuts help dialog."""
        shortcuts = [
            ("Alt+M", "Name edit"),
            ("Alt+E", "Edit selected row"),
            ("Alt+L", "Jump to list"),
            ("Ctrl+C", "Copy selected name"),
            ("Alt+A", "Active checkbox") if self.is_collection_mode else None,
            (
                ("Alt+F", "Clear find and start a new search")
                if not self.is_collection_mode
                else None
            ),
            (
                ("Alt+S", "Save")
                if self.save_button.isVisible() and self.save_button.isEnabled()
                else None
            ),
            (
                ("Escape", "Return to list from Find")
                if not self.is_collection_mode
                else ("Escape", "Cancel edit/Close window")
            ),
            ("Alt+/", "Read status bar"),
            ("F1", "Show this help"),
        ]
        shortcuts = [item for item in shortcuts if item is not None]

        from src.accessibility.shortcut_helpers import (
            get_accessible_shortcuts_list,
            build_accessible_f1_popup_style,
            prepend_help_doc_shortcut,
        )

        shortcuts = prepend_help_doc_shortcut(get_accessible_shortcuts_list(shortcuts))

        dlg = AccessibleDialog(self)
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
        table.setRowCount(len(shortcuts))
        table.setVerticalHeaderLabels([""] * len(shortcuts))
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setTabKeyNavigation(False)
        table.setAlternatingRowColors(False)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        table.setShowGrid(False)

        # Disable hover highlighting for low-vision comfort
        table.setMouseTracking(False)
        table.viewport().setMouseTracking(False)
        table.setAttribute(Qt.WA_Hover, False)
        table.viewport().setAttribute(Qt.WA_Hover, False)

        table.setStyleSheet(build_accessible_f1_popup_style())

        for row, (key, description) in enumerate(shortcuts):
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
        """Cancel current New/Edit mode and return to locked list mode, or close window."""
        if (
            not self.is_collection_mode
            and self.find_edit.hasFocus()
            and self.find_edit.isVisible()
        ):
            self._escape_from_find_to_list()
            return

        if self._collection_editor_locked:
            # If not editing, close the window
            self.accept()
            return

        # If editing, show save changes dialog like other windows
        from src.accessibility.style_helpers import (
            apply_message_box_button_icons,
            build_accessible_message_box_style,
            set_message_box_button_accessibility,
            MESSAGE_BOX_UNSAVED_THREE_ICONS,
        )

        from src.accessibility.icon_helper import get_app_icon

        msg = QMessageBox(self)
        msg.setWindowIcon(get_app_icon())
        msg.setWindowTitle("Unsaved Changes")
        msg.setStyleSheet(
            build_accessible_message_box_style(self.scaler.get_scaled_size(20))
        )
        msg.setText(
            "You have unsaved changes.\n\n"
            "Yes = Save and close\n"
            "No = Continue editing\n"
            "Cancel = Discard changes and close"
        )
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        msg.button(QMessageBox.Yes).setText("&Yes")
        msg.button(QMessageBox.No).setText("&No")
        msg.button(QMessageBox.Cancel).setText("&Cancel")
        set_message_box_button_accessibility(
            msg,
            {
                QMessageBox.Yes: ("Yes, save and close", "Save changes and close"),
                QMessageBox.No: ("No, continue editing", "Return to editing"),
                QMessageBox.Cancel: (
                    "Cancel, discard changes and close",
                    "Discard changes and close",
                ),
            },
        )
        apply_message_box_button_icons(msg, self.scaler, MESSAGE_BOX_UNSAVED_THREE_ICONS)

        reply = msg.exec()

        if reply == QMessageBox.Yes:
            # Save and close
            if self.on_save():
                self.accept()
            return
        elif reply == QMessageBox.No:
            # Continue editing
            return
        else:  # Cancel - discard changes and close
            preserve_id = self._selected_item_id()
            if preserve_id is None:
                preserve_id = self.current_item_id
            self.load_items(preserve_id=preserve_id, populate_editor=False)
            self._set_collection_editor_locked(True)
            self.focus_list()
            self.set_status("Changes discarded.", announce=True)
            self.accept()

    @classmethod
    def _best_match_row_from_entries(
        cls,
        entries: list[tuple[int, str]],
        text: str,
        *,
        is_author_mode: bool,
    ) -> tuple[int, int]:
        search_text = cls._normalize_find_value(text)
        if not search_text:
            return -1, 0

        total_matches = 0
        best_match_row = -1
        best_rank: int | None = None
        best_name_len: int | None = None

        for row, name in entries:
            rank = cls._find_match_rank(
                name, search_text, is_author_mode=is_author_mode
            )
            if rank is None:
                continue

            total_matches += 1
            name_len = len(cls._normalize_find_value(name))
            if (
                best_rank is None
                or rank < best_rank
                or (rank == best_rank and name_len < (best_name_len or 0))
            ):
                best_rank = rank
                best_match_row = row
                best_name_len = name_len

        return best_match_row, total_matches

    def find_first_match(self, text: str, *, visible_only: bool = False) -> bool:
        entries: list[tuple[int, str]] = []
        for row in range(self.table.rowCount()):
            if visible_only and self.table.isRowHidden(row):
                continue
            item = self.table.item(row, self.COL_NAME)
            name = item.text() if item else ""
            entries.append((row, name))

        best_match_row, total_matches = self._best_match_row_from_entries(
            entries,
            text,
            is_author_mode=self.is_author_mode,
        )

        if best_match_row >= 0:
            self._focus_row(best_match_row)
            item = self.table.item(best_match_row, self.COL_NAME)
            suffix = self.AUTHOR_FIND_HINT if self.is_author_mode else ""

            # Enhanced announcement with position
            position_text = (
                f"Showing match 1 of {total_matches}"
                if total_matches > 1
                else "Showing only match"
            )
            self.set_status(
                f"Found {self.entity_singular.lower()}: {item.text()}. {position_text}.{suffix}",
                announce=True,
            )
            return True

        suffix = self.AUTHOR_FIND_HINT if self.is_author_mode else ""
        self.set_status(
            f"No matching {self.entity_plural.lower()} for '{text}'.{suffix}",
            announce=False,
        )
        return False

    def _focus_row(self, row: int):
        if row < 0 or row >= self.table.rowCount():
            return
        self.table.selectRow(row)
        self.table.setCurrentCell(row, self.COL_NAME)
        item = self.table.item(row, self.COL_NAME)
        if item is not None:
            self.table.scrollToItem(item)

    @staticmethod
    def _row_accessible_text(
        name: str, usage_count: int, *, active: str | None = None
    ) -> str:
        book_label = "1 book" if usage_count == 1 else f"{usage_count} books"
        if active is not None:
            return f"{name}: Active {active}: {book_label}"
        return f"{name}: {book_label}"

    @staticmethod
    def _initial_table_row(focused_initial_match: bool) -> int | None:
        return None if focused_initial_match else 0

    @classmethod
    def _row_visible_for_live_find(cls, name: str, text: str) -> bool:
        if not (text or "").strip():
            return True
        search_raw = text.casefold()
        if search_raw in name.casefold():
            return True
        search = cls._normalize_find_value(text)
        if not search:
            return True
        return search in cls._normalize_find_value(name)

    def _copy_current_name(self) -> bool:
        """Copy the selected name to the clipboard."""
        row = self.table.currentRow()
        if row < 0:
            return False
        name_item = self.table.item(row, self.COL_NAME)
        if name_item is None:
            return False
        if not copy_plain_text(name_item.text()):
            return False
        self.set_status("Copied.", announce=False)
        return True

    def _on_table_context_menu(self, pos) -> None:
        """Right-click / Menu key: Copy the name under the pointer."""
        item = self.table.itemAt(pos)
        if item is None:
            return
        self.table.setCurrentCell(item.row(), self.COL_NAME)
        menu = QMenu(self.table)
        menu.setAccessibleName(f"{self.entity_singular} list menu")
        copy_action = menu.addAction("Copy")
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.setEnabled(item.text() != "")
        chosen = menu.exec(self.table.viewport().mapToGlobal(pos))
        if chosen == copy_action:
            self._copy_current_name()

    def _route_table_typing_to_find(self, event) -> bool:
        """Send plain typing from the list into Find; leave shortcuts alone.

        Ctrl/Alt/Meta chords (for example Ctrl+C) must stay on the list.
        Modifier-only key presses must not steal focus back to Find.
        """
        if event.modifiers() & (
            Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier
        ):
            return False
        key = event.key()
        if key in (
            Qt.Key_Control,
            Qt.Key_Shift,
            Qt.Key_Alt,
            Qt.Key_Meta,
            Qt.Key_AltGr,
            Qt.Key_Return,
            Qt.Key_Enter,
            Qt.Key_Escape,
            Qt.Key_Tab,
            Qt.Key_Backtab,
            Qt.Key_Up,
            Qt.Key_Down,
            Qt.Key_Left,
            Qt.Key_Right,
            Qt.Key_Home,
            Qt.Key_End,
            Qt.Key_PageUp,
            Qt.Key_PageDown,
        ):
            return False

        typed = event.text()
        if key not in (Qt.Key_Backspace, Qt.Key_Delete) and (
            not typed or not typed.isprintable()
        ):
            return False

        self.find_edit.setFocus(Qt.OtherFocusReason)
        current = self.find_edit.text()
        if key == Qt.Key_Backspace:
            self.find_edit.setText(current[:-1])
        elif key == Qt.Key_Delete:
            self.find_edit.setText("")
        else:
            self.find_edit.setText(current + typed)
        event.accept()
        return True

    @staticmethod
    def _normalize_find_value(text: str) -> str:
        normalized = (text or "").strip().casefold()
        normalized = re.sub(r"[^\w\s]", " ", normalized)
        normalized = " ".join(normalized.split())
        return normalized

    @classmethod
    def _find_match_rank(
        cls, candidate: str, search_text: str, *, is_author_mode: bool
    ) -> int | None:
        normalized_search = cls._normalize_find_value(search_text)
        if not normalized_search:
            return None

        normalized_candidate = cls._normalize_find_value(candidate)
        if normalized_candidate == normalized_search:
            return 0

        compact_search = normalized_search.replace(" ", "")
        compact_candidate = normalized_candidate.replace(" ", "")
        if compact_search and compact_search == compact_candidate:
            return 1

        if normalized_search in normalized_candidate:
            if normalized_candidate.startswith(normalized_search):
                return 2
            if normalized_candidate.endswith(normalized_search):
                return 3
            return 4

        if compact_search and compact_search in compact_candidate:
            return 5

        if not is_author_mode:
            return None

        search_tokens = [token for token in normalized_search.split(" ") if token]
        if search_tokens and all(token in normalized_candidate for token in search_tokens):
            return 6

        return None

    @classmethod
    def _is_find_match(
        cls, candidate: str, search_text: str, *, is_author_mode: bool
    ) -> bool:
        return (
            cls._find_match_rank(candidate, search_text, is_author_mode=is_author_mode)
            is not None
        )

    def focus_list(self):
        row_count = self.table.rowCount()
        if row_count > 0:
            row = self.table.currentRow()
            if row < 0 or row >= row_count:
                row = 0  # Always focus first row if no valid current row
            self.table.setCurrentCell(row, self.COL_NAME)
            self.table.selectRow(row)  # Ensure the row is selected
            name_item = self.table.item(row, self.COL_NAME)
            if name_item:
                self._set_edit_hint_status(name_item.text())
        self.table.setFocus(Qt.TabFocusReason)

    def focus_and_select_row(self, item_id: int | None) -> None:
        """Focus and select the list row for the given author, series, genre, or collection id."""
        if item_id is None:
            self.focus_list()
            return
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, self.COL_NAME)
            if name_item is None:
                continue
            data = name_item.data(Qt.UserRole)
            if data is None or int(data) != int(item_id):
                continue
            self.current_item_id = int(item_id)
            selection_model = self.table.selectionModel()
            table_blocker = QSignalBlocker(self.table)
            selection_blocker = (
                QSignalBlocker(selection_model) if selection_model else None
            )
            try:
                self.table.selectRow(row)
                self.table.setCurrentCell(row, self.COL_NAME)
            finally:
                del table_blocker
                if selection_blocker is not None:
                    del selection_blocker
            self.table.setFocus(Qt.TabFocusReason)
            return
        self.focus_list()

    def _set_edit_hint_status(self, item_name: str):
        # Only show the name, no shortcut hints
        name_text = (item_name or "").strip() or self.entity_singular.lower()
        self.set_status(f"{name_text}")
