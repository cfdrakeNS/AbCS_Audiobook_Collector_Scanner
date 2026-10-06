"""Check Book Locations — list books with empty, missing, or incorrect paths."""

from __future__ import annotations

import csv
import time
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QEvent, QSettings, Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMenu,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from src.accessibility.accessible_events import (
    announce_dialog_closed,
    announce_status_message,
    configure_status_bar_accessibility,
    read_status_bar_message,
)
from src.accessibility.icon_helper import (
    apply_decorative_action_icon,
    get_app_icon,
)
from src.accessibility.key_filters import is_unmapped_alt_letter
from src.accessibility.scaling import UIScaler
from src.accessibility.shortcut_helpers import (
    build_accessible_f1_popup_style,
    exec_f1_shortcuts_dialog,
)
from src.accessibility.shortcuts import (
    ShortcutContext,
    get_shortcut_manager,
)
from src.accessibility.style_helpers import (
    apply_tooltip_accessibility,
    apply_visual_tooltip_map,
    build_accessible_combo_box_style,
    build_modern_button_style,
    build_table_polish_style,
    exec_styled_message_box,
)
from src.accessibility.theme_manager import ThemeManager, get_theme_manager
from src.core.library_root import (
    IMPORT_DEFAULT_DIRECTORY_KEY,
    root_path_issue,
)
from src.core.path_health import (
    FILTER_ALL,
    FILTER_INCORRECT,
    FILTER_MISSING,
    STATUS_EMPTY,
    STATUS_MISSING,
    STATUS_RESOLVED,
    PathHealthCounts,
    PathHealthRow,
    _root_for_book,
    build_path_health_row,
    iter_book_path_checks,
    row_matches_filter,
    sort_path_health_rows,
)
from src.database.connection import DatabaseManager
from src.database.models import Collection, SearchFilter
from src.database.queries import BookQueries, CollectionQueries
from src.ui.accessible_dialog import AccessibleDialog
from src.ui.book_details import BookDetailsWindow
from src.ui.help_router import install_shift_f1_help
from src.ui.import_progress_window import ImportProgressWindow
from src.ui.table_clipboard import copy_plain_text


class PathHealthWindow(AccessibleDialog):
    """Report books whose stored path is empty, missing, or not under the collection folder."""

    COL_AUTHOR = 0
    COL_TITLE = 1
    COL_ERROR = 2
    COL_PATH = 3

    ALLOWED_ALT_LETTERS = "CFILSX/"

    GUIDE_TEXT = (
        "Choose a collection and filter, then press Scan. Each book is checked "
        "against its stored path, then under the collection folder: the author "
        "folder, then the series folder when the book has a series. When the "
        "book is found in the collection folder, the path is corrected, the book "
        "is not listed, and it is counted as Corrected. Missing: the book cannot "
        "be found. Incorrect: the path is outside the collection folder, Listen "
        "cannot play it, and the book is not in the collection folder. A path "
        "Listen can play is valid and is not listed. Press Enter on a book to open "
        "Book Details."
    )

    def __init__(
        self,
        db: DatabaseManager,
        scaler: UIScaler,
        theme_manager: ThemeManager | None = None,
        parent=None,
        initial_collection_id: int | None = None,
    ):
        super().__init__(parent)
        self._initial_collection_id = initial_collection_id
        self._open_focus_pending = True
        self.db = db
        self.scaler = scaler
        self.theme_manager = theme_manager
        self.book_queries = BookQueries(db)
        self.collection_queries = CollectionQueries(db)
        self._rows: list[PathHealthRow] = []
        self._scan_rows_all: list[PathHealthRow] = []
        self._scan_books: dict[int, object] = {}
        self._scanned_total = 0
        self._last_scan_status = ""
        self._loading = False
        self._is_scanning = False
        self.progress_window: ImportProgressWindow | None = None
        self._book_details: BookDetailsWindow | None = None

        self.setWindowIcon(get_app_icon())
        self.setWindowTitle("Check Book Locations")
        self.setAccessibleName("Check Book Locations Window")
        self.setAccessibleDescription(
            "Lists books whose stored path is blank, missing on disk, or not "
            "under the collection folder. Press Enter on a row to open Book Details."
        )
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMinimumSize(720, 480)
        self.resize(1280, 747)

        self.setup_ui()
        self.apply_visual_tooltips()
        self.apply_control_styles()
        self.setup_shortcuts()
        self.installEventFilter(self)
        self._load_collection_options()
        if hasattr(self.scaler, "scale_changed"):
            self.scaler.scale_changed.connect(self.on_scale_changed)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        collection_label = QLabel("&Collection:")
        self.collection_combo = QComboBox()
        self.collection_combo.setAccessibleName("Check book locations collection")
        self.collection_combo.setAccessibleDescription(
            "All Collections or one collection whose book paths to check - Alt+C"
        )
        collection_label.setBuddy(self.collection_combo)
        header_layout.addWidget(collection_label)
        header_layout.addWidget(self.collection_combo, 1)

        filter_label = QLabel("&Filter:")
        self.filter_combo = QComboBox()
        self.filter_combo.setAccessibleName("Check book locations filter")
        self.filter_combo.setAccessibleDescription(
            "Missing: the book cannot be found. "
            "Incorrect: outside the collection folder and Listen cannot play it. "
            "All: missing and incorrect. Alt+F"
        )
        for label, data in (
            ("Missing", FILTER_MISSING),
            ("Incorrect", FILTER_INCORRECT),
            ("All", FILTER_ALL),
        ):
            self.filter_combo.addItem(label, data)
        all_index = self.filter_combo.findData(FILTER_ALL)
        self.filter_combo.setCurrentIndex(0 if all_index < 0 else all_index)
        filter_label.setBuddy(self.filter_combo)
        header_layout.addWidget(filter_label)
        header_layout.addWidget(self.filter_combo)

        self.scan_button = QPushButton("Scan")
        self.scan_button.setAccessibleName("Scan")
        self.scan_button.setAccessibleDescription(
            "Scan books in the selected collection - Alt+S"
        )
        self.scan_button.setDefault(False)
        self.scan_button.setAutoDefault(False)
        self.scan_button.clicked.connect(lambda: self.run_scan())
        header_layout.addWidget(self.scan_button)

        layout.addLayout(header_layout)

        self.guide_label = QLabel(self.GUIDE_TEXT)
        self.guide_label.setWordWrap(True)
        self.guide_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.guide_label.setObjectName("checkBookLocationsGuide")
        self.guide_label.setFocusPolicy(Qt.TabFocus)
        self.guide_label.setAccessibleName(self.GUIDE_TEXT)
        self.guide_label.setAccessibleDescription(
            "How this scan works - Alt+I"
        )
        self.guide_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        layout.addWidget(self.guide_label)

        self.table = QTableWidget()
        self.table.setAccessibleName("Check book locations list")
        self.table.setAccessibleDescription(
            "Books with invalid paths for the selected filter. "
            "Use Up and Down arrows to move between rows. "
            "Enter opens Book Details - Alt+L"
        )
        apply_tooltip_accessibility(
            self.table,
            "Check book locations list",
            "Books with invalid paths for the selected filter",
        )
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Author", "Title", "Error", "Path"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setTabKeyNavigation(False)
        self.table.setFocusPolicy(Qt.StrongFocus)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(False)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        vh = self.table.verticalHeader()
        vh.setVisible(False)
        vh.setSectionsClickable(False)
        vh.setHighlightSections(False)
        vh.setAccessibleName("")
        vh.setAccessibleDescription("")
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setMinimumSectionSize(60)
        header.setSectionsClickable(False)
        header.setAccessibleName("")
        header.setAccessibleDescription("")
        header.setSectionResizeMode(self.COL_AUTHOR, QHeaderView.Interactive)
        header.setSectionResizeMode(self.COL_TITLE, QHeaderView.Interactive)
        header.setSectionResizeMode(self.COL_ERROR, QHeaderView.Interactive)
        header.setSectionResizeMode(self.COL_PATH, QHeaderView.Interactive)
        self._stretch_columns = {
            self.COL_AUTHOR: 2.2,
            self.COL_TITLE: 3.0,
            self.COL_ERROR: 2.0,
            self.COL_PATH: 3.5,
        }
        self.table.doubleClicked.connect(self.on_open_details)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._on_table_context_menu)
        layout.addWidget(self.table, 1)

        footer_layout = QHBoxLayout()
        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        configure_status_bar_accessibility(self.status_bar)
        footer_layout.addWidget(self.status_bar, 1)

        self.export_button = QPushButton("Export")
        self.export_button.setAccessibleName("Export")
        self.export_button.setAccessibleDescription(
            "Export the invalid path list to CSV - Alt+X"
        )
        self.export_button.setDefault(False)
        self.export_button.setAutoDefault(False)
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self.on_export_csv)

        footer_layout.addWidget(self.export_button)
        layout.addLayout(footer_layout)

        self.setTabOrder(self.collection_combo, self.filter_combo)
        self.setTabOrder(self.filter_combo, self.scan_button)
        self.setTabOrder(self.scan_button, self.guide_label)
        self.setTabOrder(self.guide_label, self.table)
        self.setTabOrder(self.table, self.export_button)

        self.collection_combo.currentIndexChanged.connect(self.on_collection_changed)
        self.filter_combo.currentIndexChanged.connect(self.on_filter_changed)

        for widget in (
            self.collection_combo,
            self.filter_combo,
            self.scan_button,
            self.guide_label,
            self.table,
            self.export_button,
        ):
            widget.installEventFilter(self)

    def apply_visual_tooltips(self):
        apply_visual_tooltip_map(
            {
                self.collection_combo: "Collection to scan",
                self.filter_combo: (
                    "Missing = not found; "
                    "Incorrect = outside the collection folder and Listen cannot play it; "
                    "All = every problem"
                ),
                self.scan_button: "Scan the selected collection",
                self.export_button: "Export list to CSV",
                self.table: "Invalid book paths",
            }
        )

    def apply_control_styles(self):
        scale_pct = self.scaler.current_scale
        base_height = 20
        scaled_height = int(base_height * (scale_pct / 100.0))
        base_font_size = int(9 * (scale_pct / 100.0))

        font = self.font()
        font.setPointSize(base_font_size)
        self.setFont(font)

        button_style = build_modern_button_style(scaled_height)
        status_style = f"""
            QStatusBar {{
                border: 1px solid palette(mid);
                border-radius: {self.scaler.get_scaled_size(5)}px;
                padding: 2px 6px;
                background-color: palette(base);
            }}
        """
        self.scan_button.setObjectName("primaryActionButton")
        self.status_bar.setStyleSheet(status_style)
        self.guide_label.setStyleSheet(
            "QLabel#checkBookLocationsGuide {"
            "  background-color: palette(base);"
            "  border: 1px solid palette(mid);"
            "  padding: 5px;"
            "}"
            "QLabel#checkBookLocationsGuide:focus {"
            "  border: 2px solid palette(highlight);"
            "}"
        )

        combo_style = build_accessible_combo_box_style(scaled_height)
        for widget in (self.collection_combo, self.filter_combo):
            widget.setStyleSheet(combo_style)
        for widget in (self.scan_button, self.export_button):
            widget.setStyleSheet(button_style)

        apply_decorative_action_icon(self.scan_button, "scan", self.scaler)
        apply_decorative_action_icon(self.export_button, "export", self.scaler)
        table_style = (
            build_accessible_f1_popup_style()
            + build_table_polish_style("QTableWidget")
            + f"""
            QTableWidget {{
                border: 1px solid palette(mid);
                border-radius: {self.scaler.get_scaled_size(5)}px;
            }}
            """
        )
        self.table.setStyleSheet(table_style)

    def on_scale_changed(self, _value: int):
        self.apply_control_styles()
        self.update_stretch_columns()

    def setup_shortcuts(self):
        shortcut_mgr = get_shortcut_manager()
        callback_map = {
            "collection_combo": self._focus_collection_combo,
            "filter_combo": self._focus_filter_combo,
            "guide_label": self._focus_guide_label,
            "scan_button": self.scan_button.click,
            "path_list_table": self._focus_table,
            "export_button": self.export_button.click,
        }
        shortcut_mgr.register_alt_shortcuts(
            self, ShortcutContext.PATH_HEALTH_WINDOW, callback_map
        )
        self.help_shortcut = QShortcut(QKeySequence("F1"), self)
        self.help_shortcut.activated.connect(self.on_show_shortcuts)
        self.context_help_shortcut = install_shift_f1_help(self)
        self.escape_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.escape_shortcut.activated.connect(self._on_escape)
        # Alt+/ stays local (same as Import) and uses read_status_bar_message.
        self.status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.status_shortcut.activated.connect(self.on_read_status_bar)

    def _focus_collection_combo(self):
        self.collection_combo.setFocus()
        self.collection_combo.showPopup()

    def _focus_filter_combo(self):
        self.filter_combo.setFocus()
        self.filter_combo.showPopup()

    def _focus_guide_label(self):
        self.guide_label.setFocus(Qt.ShortcutFocusReason)

    def _focus_table(self):
        if self.table.rowCount() > 0:
            if self.table.currentRow() < 0:
                self.table.setCurrentCell(0, self.COL_TITLE)
            self.table.setFocus()
        else:
            self.set_status("No rows in the list.", announce=True)

    def _initial_focus(self):
        self.collection_combo.setFocus(Qt.TabFocusReason)
        self.set_status("Press Scan to check paths.", announce=False)

    def _load_collection_options(self):
        """Load All Collections plus active collections (main-window style)."""
        self._loading = True
        self.collection_combo.blockSignals(True)
        self.collection_combo.clear()
        self.collection_combo.addItem("All Collections", None)

        collections = self.collection_queries.get_all(active_only=True)
        if not collections:
            default_collection = Collection(name="Default", active=True)
            new_id = self.collection_queries.insert(default_collection)
            collections = [
                Collection(collection_id=new_id, name="Default", active=True)
            ]

        collections = sorted(
            collections,
            key=lambda collection: (collection.name or "").casefold(),
        )
        for collection in collections:
            self.collection_combo.addItem(collection.name, collection.collection_id)

        initial_index = 0
        if self._initial_collection_id is not None:
            found = self.collection_combo.findData(self._initial_collection_id)
            if found >= 0:
                initial_index = found
        self.collection_combo.setCurrentIndex(initial_index)
        self.collection_combo.blockSignals(False)
        self._loading = False

    def on_collection_changed(self, _index: int = -1):
        if self._loading:
            return
        self._rows = []
        self._scan_rows_all = []
        self._scan_books = {}
        self._scanned_total = 0
        self._fill_table()
        self._sync_action_buttons()
        self.set_status("Press Scan to check paths.", announce=self.isVisible())

    def on_filter_changed(self, _index: int = -1):
        if self._loading or self._is_scanning:
            return
        if self._scan_rows_all:
            self._apply_filter_to_cached_rows(announce=True, reset_focus=True)
        else:
            self.set_status("Press Scan to check paths.", announce=True)

    def _apply_filter_to_cached_rows(
        self,
        *,
        announce: bool,
        focus_book_id: int | None = None,
        focus_column: int | None = None,
        focus_fallback_index: int | None = None,
        reset_focus: bool = False,
    ) -> None:
        filter_key = self.filter_combo.currentData() or FILTER_ALL
        self._rows = sort_path_health_rows(
            [
                row
                for row in self._scan_rows_all
                if row_matches_filter(row.status, filter_key)
            ]
        )
        preserved_col = (
            self.COL_TITLE if focus_column is None else focus_column
        )
        if focus_book_id is None and not reset_focus:
            selected = self._selected_row()
            if selected is not None:
                focus_book_id = selected.book_id
                col = self.table.currentColumn()
                if col >= 0:
                    preserved_col = col
        self._fill_table()
        self._sync_action_buttons()
        counts = PathHealthCounts()
        for row in self._scan_rows_all:
            counts.record(row.status)
        self._announce_scan_result(
            filter_key=filter_key,
            matched_count=len(self._rows),
            counts=counts,
            canceled=False,
            announce=announce,
        )
        if self._rows:
            if focus_book_id is not None:
                self._restore_table_focus(
                    focus_book_id,
                    preserved_col,
                    fallback_index=focus_fallback_index,
                )
            elif reset_focus:
                self.table.setCurrentCell(0, self.COL_TITLE)
            if announce:
                self.table.setFocus()
        QTimer.singleShot(0, self.update_stretch_columns)

    def eventFilter(self, source, event):
        if isinstance(source, QComboBox) and event.type() == QEvent.FocusIn:
            line = source.lineEdit()
            if line is not None:
                QTimer.singleShot(0, line.deselect)
        if (
            isinstance(source, QComboBox)
            and event.type() == QEvent.KeyPress
            and event.key() in (Qt.Key_Up, Qt.Key_Down)
        ):
            if event.modifiers() & Qt.AltModifier:
                source.showPopup()
            else:
                QApplication.beep()
            event.accept()
            return True
        if (
            source is self.scan_button
            and event.type() == QEvent.KeyPress
            and event.key() in (Qt.Key_Return, Qt.Key_Enter)
            and not event.modifiers() & ~Qt.KeypadModifier
        ):
            if self.scan_button.isEnabled():
                self.scan_button.click()
            event.accept()
            return True
        if source is self.table and event.type() == QEvent.KeyPress:
            if event.matches(QKeySequence.Copy):
                if self._copy_current_table_cell(announce=True):
                    event.accept()
                    return True
            if event.key() == Qt.Key_Tab and not event.modifiers():
                self.focusNextChild()
                event.accept()
                return True
            if event.key() == Qt.Key_Backtab:
                self.focusPreviousChild()
                event.accept()
                return True
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.on_open_details()
                event.accept()
                return True
        if event.type() == QEvent.KeyPress and is_unmapped_alt_letter(
            event, self.ALLOWED_ALT_LETTERS
        ):
            event.accept()
            return True
        return super().eventFilter(source, event)

    def set_status(self, message: str, announce: bool = False):
        announce_status_message(self.status_bar, message, move_focus=announce)

    def _sync_action_buttons(self) -> None:
        self.export_button.setEnabled(bool(self._rows))
    def _on_escape(self):
        if self.progress_window is not None and self.progress_window.isVisible():
            self.progress_window.on_close_requested()
            return
        self.reject()

    def on_read_status_bar(self):
        """Alt+/ — read status via centralized helper (forward while progress is open)."""
        if self.progress_window is not None and self.progress_window.isVisible():
            self.progress_window.on_read_status_bar()
            return
        read_status_bar_message(
            self.status_bar,
            fallback=self._last_scan_status or "Ready",
        )

    @staticmethod
    def _format_elapsed(seconds: float) -> str:
        total = max(0, int(seconds))
        minutes, secs = divmod(total, 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"

    def _on_progress_window_closed(self, _result: int = 0):
        self.progress_window = None

    def _prefs_import_dir(self) -> str:
        settings = QSettings("AbCS", "AbCS")
        try:
            value = settings.value(IMPORT_DEFAULT_DIRECTORY_KEY, "", type=str)
        except TypeError:
            value = settings.value(IMPORT_DEFAULT_DIRECTORY_KEY, "")
        return (value or "").strip()

    def _selected_collection_root(self) -> str:
        collection_id = self.collection_combo.currentData()
        if collection_id is None:
            return ""
        collection = self.collection_queries.get_by_id(int(collection_id))
        if collection is None:
            return ""
        return (collection.root_path or "").strip()

    def _collection_roots_map(self) -> dict[int, str]:
        roots: dict[int, str] = {}
        for collection in self.collection_queries.get_all(active_only=True):
            if collection.collection_id is None:
                continue
            roots[int(collection.collection_id)] = (
                collection.root_path or ""
            ).strip()
        return roots

    def _collection_folder_problems(self, books, scan_all: bool) -> list[str]:
        """One line per scanned collection whose folder is unset, missing, or has no audio."""
        if scan_all:
            used_ids = {getattr(book, "collection_id", None) for book in books}
            collections = [
                c
                for c in self.collection_queries.get_all(active_only=True)
                if c.collection_id in used_ids
            ]
        else:
            collection = self.collection_queries.get_by_id(
                int(self.collection_combo.currentData())
            )
            collections = [collection] if collection is not None else []
        problems: list[str] = []
        for collection in sorted(collections, key=lambda c: (c.name or "").casefold()):
            name = collection.name or "Unnamed"
            root = (collection.root_path or "").strip()
            if not root:
                problems.append(f"The {name} collection has no collection folder set.")
                continue
            issue = root_path_issue(root)
            if issue == "missing":
                problems.append(f"The {name} collection folder is missing - {root}.")
            elif issue:
                problems.append(
                    f"The {name} collection folder has no audiobook files - {root}."
                )
        return problems

    def _warn_collection_folder_problems(self, problems: list[str]) -> None:
        self.set_status(
            "Collection folder problem. Books cannot be resolved without it.",
            announce=False,
        )
        exec_styled_message_box(
            self,
            self.scaler.get_scaled_size(20),
            icon=QMessageBox.Warning,
            title="Collection folder",
            text=(
                "\n".join(problems)
                + "\n\nCheck Book Locations uses the collection folder to find each "
                "book's location, so these books cannot be resolved. To fix, open "
                "Manage > Collections, edit the collection, and update the "
                "collection folder.\n\nThe scan will continue."
            ),
        )

    def run_scan(self, warn_folder: bool = True):
        if self._is_scanning:
            self.set_status("Scan already in progress.", announce=True)
            return
        if self.collection_combo.currentIndex() < 0:
            self.set_status("Select a collection first.", announce=True)
            self.collection_combo.setFocus()
            return

        collection_id = self.collection_combo.currentData()
        filter_key = self.filter_combo.currentData() or FILTER_ALL
        import_dir = self._prefs_import_dir()
        scan_all = collection_id is None
        if scan_all:
            books = self.book_queries.get_all(
                SearchFilter(order_by="Author"), include_comments=False
            )
            root = ""
            collection_roots = self._collection_roots_map()
        else:
            books = self.book_queries.get_all(
                SearchFilter(collection_id=int(collection_id), order_by="Author"),
                include_comments=False,
            )
            root = self._selected_collection_root()
            collection_roots = None
        self._scanned_total = len(books)
        self._scan_books = {
            int(book.book_id): book for book in books if book.book_id is not None
        }
        if self._scanned_total == 0:
            self._rows = []
            self._scan_rows_all = []
            self._fill_table()
            self._sync_action_buttons()
            msg = (
                "No books found."
                if scan_all
                else "No books in this collection."
            )
            self._last_scan_status = msg
            self.set_status(msg, announce=True)
            self.scan_button.setFocus()
            return

        if warn_folder:
            problems = self._collection_folder_problems(books, scan_all)
            if problems:
                self._warn_collection_folder_problems(problems)

        theme = self.theme_manager
        if theme is None:
            theme = get_theme_manager(QApplication.instance())

        self._is_scanning = True

        progress = ImportProgressWindow(self.scaler, theme, parent=self)
        progress.setWindowTitle("Check Book Locations Progress")
        progress.setAccessibleName("Check Book Locations Progress")
        progress.setAccessibleDescription(
            "Shows Missing, Corrected, Incorrect, and Valid counts while checking "
            "book paths. Escape to cancel."
        )
        progress.help_doc_override = "24_check_book_locations.md"
        progress.set_activity_label("scan")
        progress.set_compact_mode(True)
        progress.setWindowModality(Qt.WindowModal)
        progress.finished.connect(self._on_progress_window_closed)
        self.progress_window = progress
        progress.show()
        progress.raise_()
        progress.activateWindow()
        # Focus must enter the progress window before Scan is disabled, or Qt
        # moves it to the instructions label and the screen reader reads them.
        progress.scan_progress.setFocus(Qt.OtherFocusReason)
        QApplication.processEvents()
        self.scan_button.setEnabled(False)
        self.collection_combo.setEnabled(False)
        self.filter_combo.setEnabled(False)
        self.export_button.setEnabled(False)

        counts = PathHealthCounts()
        scanned_rows: list[PathHealthRow] = []
        matched_rows: list[PathHealthRow] = []
        scan_start = time.perf_counter()
        next_ui = scan_start
        ui_interval = 0.15
        canceled = False

        progress.set_status(counts.summary(), announce=True)

        try:
            for row in iter_book_path_checks(
                books,
                collection_root=root,
                collection_roots=collection_roots,
                import_dir=import_dir,
                cancel_check=lambda: bool(
                    self.progress_window and self.progress_window.cancel_requested
                ),
            ):
                if self.progress_window and self.progress_window.cancel_requested:
                    canceled = True
                    break
                counts.record(row.status)
                scanned_rows.append(row)
                if row_matches_filter(row.status, filter_key):
                    matched_rows.append(row)

                now = time.perf_counter()
                is_last = counts.processed >= self._scanned_total
                if is_last or now >= next_ui:
                    elapsed = self._format_elapsed(now - scan_start)
                    progress.update_scan_progress(
                        processed=counts.processed,
                        total=self._scanned_total,
                        elapsed_text=elapsed,
                        current_title=row.title,
                        current_author=row.author,
                    )
                    progress.set_status(f"{counts.summary()} | Elapsed {elapsed}")
                    next_ui = now + ui_interval
                    QApplication.processEvents()
                    if self.progress_window and self.progress_window.cancel_requested:
                        canceled = True
                        break
            else:
                if self.progress_window and self.progress_window.cancel_requested:
                    canceled = True
        finally:
            self._is_scanning = False
            self.scan_button.setEnabled(True)
            self.collection_combo.setEnabled(True)
            self.filter_combo.setEnabled(True)
            if self.progress_window is not None:
                elapsed = self._format_elapsed(time.perf_counter() - scan_start)
                prefix = "Canceled. " if canceled else ""
                done_status = f"{prefix}{counts.summary()} | Elapsed {elapsed}"
                self.progress_window.set_status(done_status, announce=True)
                self.progress_window._scan_active = False
                self.progress_window.close()
                self.progress_window = None

        self._save_corrected_paths(scanned_rows)
        self._scan_rows_all = scanned_rows
        self._rows = sort_path_health_rows(matched_rows)
        self._fill_table()
        self._announce_scan_result(
            filter_key=filter_key,
            matched_count=len(matched_rows),
            counts=counts,
            canceled=canceled,
        )
        self._sync_action_buttons()
        if self._rows:
            self.table.setCurrentCell(0, self.COL_TITLE)
            self.table.setFocus()
        else:
            self.scan_button.setFocus()
        QTimer.singleShot(0, self.update_stretch_columns)

    def _announce_scan_result(
        self,
        *,
        filter_key: str,
        matched_count: int,
        counts: PathHealthCounts,
        canceled: bool,
        announce: bool = True,
    ) -> None:
        prefix = "Canceled. " if canceled else ""
        shown = matched_count
        counters = counts.summary()
        kind = {
            FILTER_MISSING: "missing",
            FILTER_INCORRECT: "incorrect",
        }.get(filter_key, "problem")
        if shown == 0:
            msg = f"{prefix}{counters}. No {kind} paths in the list."
            if filter_key != FILTER_ALL:
                msg += " Try All."
        else:
            msg = f"{prefix}{counters}. Showing {shown} {kind}."
        self._last_scan_status = msg
        self.set_status(msg, announce=announce)

    def _fill_table(self):
        self.table.setUpdatesEnabled(False)
        try:
            self._fill_table_rows()
        finally:
            self.table.setUpdatesEnabled(True)

    def _fill_table_rows(self):
        self.table.setRowCount(len(self._rows))
        for row_index, row in enumerate(self._rows):
            path_display = row.path or "(empty)"
            if row.status in (STATUS_EMPTY, STATUS_MISSING):
                status_label = f"missing. {row.reason}" if row.reason else "missing"
            else:
                status_label = row.status.casefold()
            error_display = status_label[:1].upper() + status_label[1:]
            # Focus lands on Title, so the full summary lives there.
            accessible = {
                self.COL_AUTHOR: f"{row.author}, {status_label}",
                self.COL_TITLE: (
                    f"{row.title}, by {row.author}, {status_label}, path {path_display}"
                ),
                self.COL_ERROR: error_display,
                self.COL_PATH: f"path {path_display}",
            }
            values = [row.author, row.title, error_display, path_display]
            for col, text in enumerate(values):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                item.setData(Qt.AccessibleTextRole, accessible[col])
                item.setData(Qt.UserRole, row.book_id)
                self.table.setItem(row_index, col, item)

    def update_stretch_columns(self):
        """Keep Author / Title / Path proportional like Import."""
        if not hasattr(self, "_stretch_columns") or not hasattr(self, "table"):
            return
        available = self.table.viewport().width()
        if available < 100:
            return
        total_weight = sum(self._stretch_columns.values())
        for col, weight in self._stretch_columns.items():
            width = int(available * weight / total_weight)
            self.table.setColumnWidth(col, max(width, 90))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_stretch_columns()

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self.update_stretch_columns)
        if self._open_focus_pending:
            self._open_focus_pending = False
            QTimer.singleShot(0, self._initial_focus)

    def _selected_row(self) -> PathHealthRow | None:
        row = self.table.currentRow()
        if 0 <= row < len(self._rows):
            return self._rows[row]
        return None

    def _restore_table_focus(
        self,
        book_id: int,
        column: int,
        fallback_index: int | None = None,
    ) -> None:
        column = column if 0 <= column < self.table.columnCount() else self.COL_TITLE
        for row_index, row in enumerate(self._rows):
            if row.book_id == book_id:
                self.table.setCurrentCell(row_index, column)
                return
        if not self._rows:
            return
        # The edited book left the problem list. The same index is now the next book.
        if fallback_index is None:
            target = 0
        else:
            target = min(max(int(fallback_index), 0), len(self._rows) - 1)
        self.table.setCurrentCell(target, column)

    def _copy_current_table_cell(self, *, announce: bool = False) -> bool:
        row = self.table.currentRow()
        col = self.table.currentColumn()
        if row < 0 or col < 0:
            return False
        item = self.table.item(row, col)
        if item is None:
            return False
        if not copy_plain_text(item.text()):
            return False
        if announce:
            self.set_status("Copied.", announce=True)
        return True

    def _on_table_context_menu(self, pos) -> None:
        """Right-click / Menu key: Copy the cell under the pointer."""
        item = self.table.itemAt(pos)
        if item is None:
            return
        self.table.setCurrentCell(item.row(), item.column())
        menu = QMenu(self.table)
        menu.setAccessibleName("Check book locations list menu")
        copy_action = menu.addAction("Copy")
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.setEnabled(item.text() != "")
        chosen = menu.exec(self.table.viewport().mapToGlobal(pos))
        if chosen == copy_action:
            self._copy_current_table_cell(announce=True)

    def _path_check_context(self):
        """Collection root(s) and import folder for a single-book path re-check."""
        collection_id = self.collection_combo.currentData()
        scan_all = collection_id is None
        import_dir = self._prefs_import_dir()
        if scan_all:
            return True, "", self._collection_roots_map(), import_dir
        return False, self._selected_collection_root(), None, import_dir

    def _refresh_books_after_details(self, book_ids: set[int]) -> None:
        """Re-check only books edited in Book Details; do not run a full Scan."""
        if not book_ids or not self._scan_rows_all:
            self.table.setFocus()
            return
        selected = self._selected_row()
        focus_book_id = selected.book_id if selected is not None else None
        focus_index = self.table.currentRow()
        focus_column = self.table.currentColumn()
        if focus_column < 0:
            focus_column = self.COL_TITLE
        _scan_all, root, collection_roots, import_dir = self._path_check_context()
        index_by_id = {row.book_id: idx for idx, row in enumerate(self._scan_rows_all)}
        for book_id in book_ids:
            book = self.book_queries.get_by_id(book_id)
            if book is None:
                continue
            self._scan_books[int(book_id)] = book
            book_root = _root_for_book(
                book,
                collection_root=root,
                collection_roots=collection_roots,
            )
            new_row = build_path_health_row(
                book,
                collection_root=book_root,
                import_dir=import_dir,
            )
            if new_row is None:
                continue
            idx = index_by_id.get(book_id)
            if idx is not None:
                self._scan_rows_all[idx] = new_row
        self._apply_filter_to_cached_rows(
            announce=False,
            focus_book_id=focus_book_id,
            focus_column=focus_column,
            focus_fallback_index=focus_index,
        )
        QTimer.singleShot(0, self.table.setFocus)

    def on_open_details(self):
        selected = self._selected_row()
        if selected is None:
            self.set_status("Select a book row first.", announce=True)
            return
        book = self.book_queries.get_by_id(selected.book_id)
        if book is None:
            self.set_status("Book no longer in the database.", announce=True)
            self.run_scan(warn_folder=False)
            return
        books_list = []
        current_index = 0
        for row in self._rows:
            if row.book_id == selected.book_id:
                current_index = len(books_list)
                books_list.append(book)
                continue
            listed = self._scan_books.get(row.book_id)
            if listed is not None:
                books_list.append(listed)
        details = self._book_details
        if details is None:
            details = BookDetailsWindow(
                self.db,
                self.scaler,
                book=book,
                books_list=books_list,
                current_index=current_index,
                theme_manager=self.theme_manager,
                parent=self,
                keep_edit_mode=True,
            )
            self._book_details = details
            QTimer.singleShot(0, details.on_edit_mode)
        else:
            details.book = book
            details.books_list = books_list
            details.current_index = current_index
            details.is_new = False
            details._data_was_changed = False
            details._books_touched_in_session.clear()
            # Stay in edit mode. Dropping to view reloaded the plot list and
            # scanned the book folder on every open.
            details._in_edit_mode = True
            details.load_book_data()
            QTimer.singleShot(0, details.on_edit_mode)
        details.exec()
        touched = set(getattr(details, "_books_touched_in_session", set()))
        if getattr(details, "_data_was_changed", False) and touched:
            self._refresh_books_after_details(touched)
        else:
            self.table.setFocus()

    def _save_corrected_paths(self, rows: list[PathHealthRow]) -> int:
        """Store the found folder for every resolved book in one commit."""
        resolved = [
            row
            for row in rows
            if row.status == STATUS_RESOLVED and row.resolved_path
        ]
        if not resolved:
            return 0
        for row in resolved:
            self.book_queries.update_path(row.book_id, row.resolved_path, commit=False)
            book = self._scan_books.get(row.book_id)
            if book is not None:
                book.path = row.resolved_path
        self.db.connect().commit()
        return len(resolved)

    def on_export_csv(self):
        if not self._rows:
            self.set_status("Nothing to export.", announce=True)
            return
        default_path = Path.home() / "Documents"
        if not default_path.is_dir():
            default_path = Path.home()
        today = datetime.now().strftime("%Y%m%d")
        suggested = str(default_path / f"abcs_check_book_locations_{today}.csv")
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Check Book Locations to CSV",
            suggested,
            "CSV Files (*.csv);;All Files (*)",
        )
        if not file_path:
            # Keep the last scan message; do not leave "Export canceled" on the bar.
            return
        try:
            with open(file_path, "w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(
                    [
                        "Author",
                        "Title",
                        "Path",
                        "Status",
                        "Collection",
                        "Reason",
                    ]
                )
                for row in self._rows:
                    status_label = (
                        STATUS_MISSING
                        if row.status == STATUS_EMPTY
                        else row.status
                    )
                    writer.writerow(
                        [
                            row.author,
                            row.title,
                            row.path,
                            status_label,
                            row.collection_name,
                            row.reason,
                        ]
                    )
            self.set_status(
                f"Exported {len(self._rows)} row(s) to {file_path}",
                announce=True,
            )
        except OSError as exc:
            self.set_status(f"Export failed: {exc}", announce=True)

    def on_show_shortcuts(self):
        shortcuts = [
            ("Alt+C", "Collection"),
            ("Alt+F", "Filter"),
            ("Alt+Down", "Open the Collection or Filter list"),
            ("Alt+I", "Info instructions"),
            ("Alt+S", "Scan"),
            ("Alt+L", "Jump to list"),
            ("Enter", "Open Book Details"),
            ("Ctrl+C", "Copy focused cell"),
            ("Right-click", "Copy cell"),
            ("Page Up/Down in Book Details", "Previous or next listed book"),
            ("Alt+X", "Export list to CSV"),
            ("Escape", "Cancel scan or close window"),
            ("Alt+/", "Read status bar"),
            ("F1", "Show this help"),
        ]
        exec_f1_shortcuts_dialog(
            self, "Keyboard Shortcuts - Check Book Locations", shortcuts
        )

    def _release_book_details(self) -> None:
        if self._book_details is not None:
            self._book_details.close()
            self._book_details.deleteLater()
            self._book_details = None

    def accept(self):
        announce_dialog_closed(self)
        self._release_book_details()
        super().accept()

    def reject(self):
        if self._is_scanning and self.progress_window is not None:
            self.progress_window.on_close_requested()
            return
        announce_dialog_closed(self)
        self._release_book_details()
        super().reject()
