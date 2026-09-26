"""Path Health report — list books with empty, missing, or incorrect paths."""

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
    QPushButton,
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
    build_modern_button_style,
    build_table_polish_style,
)
from src.accessibility.theme_manager import ThemeManager
from src.core.library_root import IMPORT_DEFAULT_DIRECTORY_KEY
from src.core.path_health import (
    FILTER_ALL,
    FILTER_INCORRECT,
    FILTER_MISSING,
    STATUS_EMPTY,
    STATUS_INCORRECT,
    STATUS_MISSING,
    PathHealthCounts,
    PathHealthRow,
    iter_book_path_checks,
    row_matches_filter,
)
from src.database.connection import DatabaseManager
from src.database.models import Collection, SearchFilter
from src.database.queries import BookQueries, CollectionQueries
from src.ui.accessible_dialog import AccessibleDialog
from src.ui.book_details import BookDetailsWindow
from src.ui.help_router import install_shift_f1_help
from src.ui.import_progress_window import ImportProgressWindow


class PathHealthWindow(AccessibleDialog):
    """Report books whose stored path is empty, missing, or not under library root."""

    COL_AUTHOR = 0
    COL_TITLE = 1
    COL_PATH = 2

    ALLOWED_ALT_LETTERS = "CFLSX/"

    def __init__(
        self,
        db: DatabaseManager,
        scaler: UIScaler,
        theme_manager: ThemeManager | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self.db = db
        self.scaler = scaler
        self.theme_manager = theme_manager
        self.book_queries = BookQueries(db)
        self.collection_queries = CollectionQueries(db)
        self._rows: list[PathHealthRow] = []
        self._scan_rows_all: list[PathHealthRow] = []
        self._scanned_total = 0
        self._last_scan_status = ""
        self._loading = False
        self._is_scanning = False
        self.progress_window: ImportProgressWindow | None = None

        self.setWindowIcon(get_app_icon())
        self.setWindowTitle("Check Books Path")
        self.setAccessibleName("Check Books Path Window")
        self.setAccessibleDescription(
            "Lists books whose stored path is blank, missing on disk, or not "
            "under the collection library root. Press Enter on a row to open Book Details."
        )
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMinimumSize(720, 480)
        self.resize(960, 560)

        self.setup_ui()
        self.apply_visual_tooltips()
        self.apply_control_styles()
        self.setup_shortcuts()
        self.installEventFilter(self)
        self._load_collection_options()
        if hasattr(self.scaler, "scale_changed"):
            self.scaler.scale_changed.connect(self.on_scale_changed)
        QTimer.singleShot(0, self._initial_focus)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        collection_label = QLabel("&Collection:")
        self.collection_combo = QComboBox()
        self.collection_combo.setAccessibleName("Check books path collection")
        self.collection_combo.setAccessibleDescription(
            "All Collections or one collection whose book paths to check - Alt+C"
        )
        collection_label.setBuddy(self.collection_combo)
        header_layout.addWidget(collection_label)
        header_layout.addWidget(self.collection_combo, 1)

        filter_label = QLabel("&Filter:")
        self.filter_combo = QComboBox()
        self.filter_combo.setAccessibleName("Check books path filter")
        self.filter_combo.setAccessibleDescription(
            "Missing: blank or not playable after Play remap. "
            "Incorrect: playable via remap, or on disk but not under the library root. "
            "All: both missing and incorrect. Alt+F"
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
        self.scan_button.clicked.connect(self.run_scan)
        header_layout.addWidget(self.scan_button)

        layout.addLayout(header_layout)

        self.table = QTableWidget()
        self.table.setAccessibleName("Check books path list")
        self.table.setAccessibleDescription(
            "Books with invalid paths for the selected filter. "
            "Use Up and Down arrows to move between rows. "
            "Enter opens Book Details - Alt+L"
        )
        apply_tooltip_accessibility(
            self.table,
            "Check books path list",
            "Books with invalid paths for the selected filter",
        )
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Author", "Title", "Path"])
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
        header.setSectionResizeMode(self.COL_PATH, QHeaderView.Interactive)
        self._stretch_columns = {
            self.COL_AUTHOR: 2.2,
            self.COL_TITLE: 3.0,
            self.COL_PATH: 3.5,
        }
        self.table.doubleClicked.connect(self.on_open_details)
        self.table.installEventFilter(self)
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
        self.setTabOrder(self.scan_button, self.table)
        self.setTabOrder(self.table, self.export_button)

        self.collection_combo.currentIndexChanged.connect(self.on_collection_changed)
        self.filter_combo.currentIndexChanged.connect(self.on_filter_changed)

    def apply_visual_tooltips(self):
        apply_visual_tooltip_map(
            {
                self.collection_combo: "Collection to scan",
                self.filter_combo: (
                    "Missing = blank or not on disk; "
                    "Incorrect = off library root; "
                    "All = missing and incorrect"
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

        for widget in self.findChildren(QComboBox):
            widget.setStyleSheet("")
        for widget in self.findChildren(QPushButton):
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

    def _focus_table(self):
        if self.table.rowCount() > 0:
            if self.table.currentRow() < 0:
                self.table.setCurrentCell(0, self.COL_TITLE)
            self.table.setFocus()
        else:
            self.set_status("No rows in the list.", announce=True)

    def _initial_focus(self):
        self.collection_combo.setFocus(Qt.TabFocusReason)
        self.set_status("Press Scan to check paths.", announce=True)

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

        self.collection_combo.setCurrentIndex(0)
        self.collection_combo.blockSignals(False)
        self._loading = False

    def on_collection_changed(self, _index: int = -1):
        if self._loading:
            return
        self._rows = []
        self._scan_rows_all = []
        self._scanned_total = 0
        self._fill_table()
        self.export_button.setEnabled(False)
        self.set_status("Press Scan to check paths.", announce=True)

    def on_filter_changed(self, _index: int = -1):
        if self._loading or self._is_scanning:
            return
        if self._scan_rows_all:
            self._apply_filter_to_cached_rows(announce=True)
        else:
            self.set_status("Press Scan to check paths.", announce=True)

    def _apply_filter_to_cached_rows(self, *, announce: bool) -> None:
        filter_key = self.filter_combo.currentData() or FILTER_ALL
        self._rows = [
            row
            for row in self._scan_rows_all
            if row_matches_filter(row.status, filter_key)
        ]
        self._fill_table()
        self.export_button.setEnabled(bool(self._rows))
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
            self.table.setCurrentCell(0, self.COL_TITLE)
            if announce:
                self.table.setFocus()
        QTimer.singleShot(0, self.update_stretch_columns)

    def eventFilter(self, source, event):
        if source is self.table and event.type() == QEvent.KeyPress:
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

    def run_scan(self):
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
            books = self.book_queries.get_all(SearchFilter(order_by="Author"))
            root = ""
            collection_roots = self._collection_roots_map()
        else:
            books = self.book_queries.get_all(
                SearchFilter(collection_id=int(collection_id), order_by="Author")
            )
            root = self._selected_collection_root()
            collection_roots = None
        self._scanned_total = len(books)
        if self._scanned_total == 0:
            self._rows = []
            self._scan_rows_all = []
            self._fill_table()
            self.export_button.setEnabled(False)
            msg = (
                "No books in the library."
                if scan_all
                else "No books in this collection."
            )
            self._last_scan_status = msg
            self.set_status(msg, announce=True)
            self.scan_button.setFocus()
            return

        theme = self.theme_manager
        if theme is None:
            theme = ThemeManager(QApplication.instance())

        self._is_scanning = True
        self.scan_button.setEnabled(False)
        self.collection_combo.setEnabled(False)
        self.filter_combo.setEnabled(False)
        self.export_button.setEnabled(False)

        progress = ImportProgressWindow(self.scaler, theme, parent=self)
        progress.setWindowTitle("Check Books Path Progress")
        progress.setAccessibleName("Check Books Path Progress")
        progress.setAccessibleDescription(
            "Shows Missing, Incorrect, and Valid counts while checking book paths. "
            "Escape to cancel."
        )
        progress.help_doc_override = "24_path_health.md"
        progress.set_activity_label("scan")
        progress.set_compact_mode(True)
        progress.finished.connect(self._on_progress_window_closed)
        self.progress_window = progress
        progress.show()
        progress.raise_()
        progress.activateWindow()

        counts = PathHealthCounts()
        scanned_rows: list[PathHealthRow] = []
        matched_rows: list[PathHealthRow] = []
        scan_start = time.perf_counter()
        next_ui = scan_start
        ui_interval = 0.15
        canceled = False

        progress.set_status(
            "0 books scanned: Missing 0 | Incorrect 0 | Valid 0",
            announce=True,
        )

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
                    progress.set_status(
                        f"{counts.processed} books scanned: "
                        f"Missing {counts.missing} | Incorrect {counts.incorrect} | "
                        f"Valid {counts.valid} | Elapsed {elapsed}"
                    )
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
                done_status = (
                    f"{prefix}{counts.processed} books scanned: "
                    f"Missing {counts.missing} | Incorrect {counts.incorrect} | "
                    f"Valid {counts.valid} | Elapsed {elapsed}"
                )
                self.progress_window.set_status(done_status, announce=True)
                self.progress_window._scan_active = False
                self.progress_window.close()
                self.progress_window = None

        self._scan_rows_all = scanned_rows
        self._rows = matched_rows
        self._fill_table()
        self._announce_scan_result(
            filter_key=filter_key,
            matched_count=len(matched_rows),
            counts=counts,
            canceled=canceled,
        )
        self.export_button.setEnabled(bool(self._rows))
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
        counters = (
            f"{counts.processed} books scanned: "
            f"Missing {counts.missing} | Incorrect {counts.incorrect} | "
            f"Valid {counts.valid}"
        )
        if shown == 0:
            if filter_key == FILTER_INCORRECT:
                msg = (
                    f"{prefix}{counters}. No incorrect paths in the list. "
                    "Try Missing or All."
                )
            elif filter_key == FILTER_MISSING:
                msg = (
                    f"{prefix}{counters}. No missing paths in the list."
                )
            else:
                msg = f"{prefix}{counters}. No invalid paths in the list."
        elif filter_key == FILTER_ALL:
            msg = f"{prefix}{counters}. Showing {shown} invalid."
        elif filter_key == FILTER_MISSING:
            msg = f"{prefix}{counters}. Showing {shown} missing."
        else:
            msg = f"{prefix}{counters}. Showing {shown} incorrect."
        self._last_scan_status = msg
        self.set_status(msg, announce=announce)

    def _fill_table(self):
        self.table.setRowCount(len(self._rows))
        for row_index, row in enumerate(self._rows):
            path_display = row.path or "(empty)"
            if row.status == STATUS_INCORRECT and row.resolved_path:
                status_label = f"incorrect, plays from {row.resolved_path}"
            elif row.status in (STATUS_EMPTY, STATUS_MISSING):
                status_label = "missing"
            else:
                status_label = row.status.casefold()
            values = [row.author, row.title, path_display]
            accessible = (
                f"{row.author}, {row.title}, path {path_display}, {status_label}"
            )
            for col, text in enumerate(values):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                item.setData(Qt.AccessibleTextRole, accessible if col == 0 else text)
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

    def _selected_row(self) -> PathHealthRow | None:
        row = self.table.currentRow()
        if 0 <= row < len(self._rows):
            return self._rows[row]
        return None

    def on_open_details(self):
        selected = self._selected_row()
        if selected is None:
            self.set_status("Select a book row first.", announce=True)
            return
        book = self.book_queries.get_by_id(selected.book_id)
        if book is None:
            self.set_status("Book no longer in the library.", announce=True)
            self.run_scan()
            return
        details = BookDetailsWindow(
            self.db,
            self.scaler,
            book=book,
            books_list=[book],
            current_index=0,
            theme_manager=self.theme_manager,
            parent=self,
        )
        QTimer.singleShot(0, details.on_edit_mode)
        details.exec()
        data_changed = getattr(details, "_data_was_changed", False)
        details.deleteLater()
        if data_changed:
            self.run_scan()
        else:
            self.table.setFocus()

    def on_export_csv(self):
        if not self._rows:
            self.set_status("Nothing to export.", announce=True)
            return
        default_path = Path.home() / "Documents"
        if not default_path.is_dir():
            default_path = Path.home()
        today = datetime.now().strftime("%Y%m%d")
        suggested = str(default_path / f"abcs_path_health_{today}.csv")
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Check Books Path to CSV",
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
                    ["Author", "Title", "Path", "Status", "Collection"]
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
            ("Alt+S", "Scan"),
            ("Alt+L", "Jump to list"),
            ("Enter", "Open Book Details"),
            ("Alt+X", "Export list to CSV"),
            ("Escape", "Cancel scan or close window"),
            ("Alt+/", "Read status bar"),
            ("F1", "Show this help"),
        ]
        exec_f1_shortcuts_dialog(
            self, "Keyboard Shortcuts - Check Books Path", shortcuts
        )

    def accept(self):
        announce_dialog_closed(self)
        super().accept()

    def reject(self):
        if self._is_scanning and self.progress_window is not None:
            self.progress_window.on_close_requested()
            return
        announce_dialog_closed(self)
        super().reject()
