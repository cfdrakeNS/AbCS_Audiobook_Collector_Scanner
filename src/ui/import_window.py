"""
Import Window
Main interface for scanning folders and importing audiobooks.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QStatusBar, QProgressBar,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QFileDialog, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, QSettings, QTimer, QItemSelectionModel, QEvent
from PySide6.QtGui import QShortcut, QKeySequence, QAccessible
from datetime import datetime
import os
import time
from typing import Optional

from database import (
    DatabaseManager, BookQueries, AuthorQueries,
    GenreQueries, CollectionQueries, Book, Collection
)
from core import BookScanner, ImportValidator, ImportScanner
from accessibility.scaling import UIScaler
from accessibility.theme_manager import ThemeManager
from accessibility.key_filters import is_unmapped_alt_letter
from accessibility.accessible_events import (
    announce_status_message, announce_dialog_opened, announce_dialog_closed
)
from ui.import_detail_window import ImportDetailWindow


class ImportWindow(QDialog):
    """
    Import dialog for scanning folders and importing metadata.
    """

    ALLOWED_ALT_LETTERS = {
        'A', 'B', 'C', 'F', 'I', 'L', 'O', 'S', 'V', 'W'
    }

    COL_AUTHOR = 0
    COL_TITLE = 1
    COL_YEAR = 2
    COL_ERROR = 3
    COL_PATH = 4

    SCENARIO_LABELS = {
        "mass_standard": "Mass Standard Import",
        "series_from_directory": "Mass Import - Series From Directory",
        "series_from_filename": "Mass Import - Series From File Name",
        "single_item": "Single Author / Book Import",
    }

    @staticmethod
    def _format_elapsed(seconds: float) -> str:
        """Format elapsed seconds as MM:SS or HH:MM:SS."""
        total_seconds = max(0, int(round(seconds)))
        hours, remainder = divmod(total_seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"

    def __init__(self, db: DatabaseManager, scaler: UIScaler,
                 theme_manager: ThemeManager, parent=None):
        super().__init__(parent)

        self.db = db
        self.scaler = scaler
        self.theme_manager = theme_manager
        self.settings = QSettings('AbCS', 'AudioBookCollector')

        self.book_queries = BookQueries(self.db)
        self.author_queries = AuthorQueries(self.db)
        self.genre_queries = GenreQueries(self.db)
        self.collection_queries = CollectionQueries(self.db)
        self.scanner = BookScanner()
        self.validator = ImportValidator()
        self.import_scanner = ImportScanner()

        self._loading = False
        self.scanned_items = []
        self.selected_rows = set()
        self.selection_anchor_row = None
        self._updating_selection_ui = False
        self.allowed_extensions = None
        self.include_subfolders = True
        self.default_collection_id = None
        self.current_collection_name = ""
        self.import_scenario_mode = "mass_standard"
        self.current_formats_text = "None"
        self.current_mode_text = self.SCENARIO_LABELS.get(
            self.import_scenario_mode, "Mass Standard Import"
        )
        self.author_fallback_mode = "folder"
        self.title_fallback_mode = "file"
        self.flip_author_names = False
        self.autocorrect_trim_whitespace = False
        self.autocorrect_strip_leading_punctuation = False
        self.autocorrect_remove_non_alphanumeric = False
        self.autocorrect_proper_case = False
        self.autocorrect_move_leading_the = False
        self.reader_keywords = ["reader", "read by", "narrator", "narrated by"]
        self._summary_counts = {
            "scanned": 0,
            "valid": 0,
            "errors": 0,
            "duplicates": 0,
        }
        self._default_status_message = "Ready"
        self._base_window_title = "Import Audiobooks"
        self._is_adding = False
        self._cancel_add_requested = False
        self._is_scanning = False
        self._cancel_scan_requested = False
        self._scan_prompt_open = False

        self.setup_ui()
        self.install_alt_key_filters()
        self.apply_control_styles()
        self.load_preferences()
        self.connect_signals()
        self.setup_shortcuts()
        self.scaler.scale_changed.connect(self.on_scale_changed)

        self._update_header_info_line()
        self.setAccessibleName(self._base_window_title)
        self.setAccessibleDescription(
            "Scan folders for audiobooks and import metadata")
        self.resize(1100, 600)
        self.setMinimumWidth(900)

        announce_dialog_opened(self, self.windowTitle())
        self.update_summary()

    def _get_target_collection_id(self) -> Optional[int]:
        """Get selected target collection ID for imports."""
        if hasattr(self, "collection_combo"):
            selected_id = self.collection_combo.currentData()
            if selected_id is None:
                return None
            self.default_collection_id = int(selected_id)
            return self.default_collection_id

        if self.default_collection_id is not None:
            return self.default_collection_id

        collections = self.collection_queries.get_all()
        if collections:
            self.default_collection_id = collections[0].collection_id
            return self.default_collection_id

        default_collection = Collection(name="Default", active=True)
        self.default_collection_id = self.collection_queries.insert(
            default_collection)
        return self.default_collection_id

    @staticmethod
    def _normalize_year(value):
        """Normalize year to int or None."""
        if value is None:
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            value = value.strip()
            if value.isdigit():
                return int(value)
        return None

    def _build_book_from_scan(self, data: dict) -> Book:
        """Create a Book object from scanned data."""
        title = (data.get("title") or "").strip()
        author_text = (data.get("author") or "").strip()
        genre_text = (data.get("genre") or "").strip()
        reader_text = (data.get("narrator") or "").strip()
        target_collection_id = self._get_target_collection_id()
        if target_collection_id is None:
            raise ValueError("No collection selected")

        author_id = self.author_queries.get_or_create(author_text)
        genre_id = None
        if genre_text:
            genre_id = self.genre_queries.get_or_create(genre_text)

        return Book(
            title=title,
            author_id=author_id,
            year=self._normalize_year(data.get("year")),
            series_id=None,
            genre_id=genre_id,
            collection_id=target_collection_id,
            reader=reader_text,
            time_hours=int(data.get("time_hours") or 0),
            time_minutes=int(data.get("time_minutes") or 0),
            tracks=int(data.get("tracks") or 0),
            size_mb=float(data.get("size_mb") or 0.0),
            bitrate=int(data.get("bitrate") or 0),
            file_format=str(data.get("format") or ""),
            path=str(data.get("folder") or ""),
            comments=str(data.get("comment") or ""),
            date_added=datetime.now(),
            source="Import",
        )

    def setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Header section
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        collection_label = QLabel("Co&llection:")
        self.collection_combo = QComboBox()
        self.collection_combo.setAccessibleName("Import collection")
        self.collection_combo.setAccessibleDescription(
            "Select target collection for imported books - Alt+L")
        collection_label.setBuddy(self.collection_combo)
        header_layout.addWidget(collection_label)
        header_layout.addWidget(self.collection_combo, 1)

        folder_label = QLabel("&Folder:")
        self.folder_edit = QLineEdit()
        self.folder_edit.setReadOnly(True)
        self.folder_edit.setAccessibleName("Folder path")
        self.folder_edit.setAccessibleDescription(
            "Folder to scan for imports - Alt+F")
        folder_label.setBuddy(self.folder_edit)
        header_layout.addWidget(folder_label)
        header_layout.addWidget(self.folder_edit, 1)

        self.browse_button = QPushButton("Bro&wse")
        self.browse_button.setAccessibleName("Browse")
        self.browse_button.setAccessibleDescription(
            "Browse for a folder to scan - Alt+W")
        self.browse_button.setDefault(False)
        self.browse_button.setAutoDefault(True)
        header_layout.addWidget(self.browse_button)

        error_filter_label = QLabel("Err&or Filter:")
        self.error_filter_combo = QComboBox()
        self.error_filter_combo.setAccessibleName("Import error filter")
        self.error_filter_combo.setAccessibleDescription(
            "Filter import list by All, Valid, Warning, Error, or Duplicate - Alt+O")
        self.error_filter_combo.addItem("All", "all")
        self.error_filter_combo.addItem("Valid", "valid")
        self.error_filter_combo.addItem("Warning", "warning")
        self.error_filter_combo.addItem("Error", "error")
        self.error_filter_combo.addItem("Duplicate", "duplicate")
        error_filter_label.setBuddy(self.error_filter_combo)
        header_layout.addWidget(error_filter_label)
        header_layout.addWidget(self.error_filter_combo)

        self.scan_button = QPushButton("&Scan")
        self.scan_button.setAccessibleName("Scan")
        self.scan_button.setAccessibleDescription(
            "Scan the selected folder for audio files - Alt+S")
        self.scan_button.setDefault(False)
        self.scan_button.setAutoDefault(True)
        self.scan_button.setEnabled(False)
        header_layout.addWidget(self.scan_button)

        layout.addLayout(header_layout)

        # Detail section: import list table
        self.table = QTableWidget()
        self.table.setAccessibleName("Import list")
        self.table.setAccessibleDescription(
            "List of scanned files with validation results")

        columns = [
            "Author",
            "Title",
            "Year",
            "Error Type",
            "File/Folder",
        ]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)

        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setSectionsClickable(False)
        self.table.verticalHeader().setHighlightSections(False)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setMinimumSectionSize(60)

        # Keep compact metadata column fixed to content, size remaining columns proportionally.
        header.setSectionResizeMode(
            self.COL_YEAR, QHeaderView.Fixed)
        header.setSectionResizeMode(self.COL_AUTHOR, QHeaderView.Interactive)
        header.setSectionResizeMode(self.COL_TITLE, QHeaderView.Interactive)
        header.setSectionResizeMode(self.COL_ERROR, QHeaderView.Interactive)
        header.setSectionResizeMode(self.COL_PATH, QHeaderView.Interactive)

        # Proportional widths: Author, Title, Error Type, File/Folder
        self._stretch_columns = {
            self.COL_AUTHOR: 2.2,
            self.COL_TITLE: 3.0,
            self.COL_ERROR: 2.3,
            self.COL_PATH: 3.0,
        }

        layout.addWidget(self.table, 1)

        # Footer section
        footer_layout = QHBoxLayout()

        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        footer_layout.addWidget(self.status_bar, 1)

        self.scan_progress = QProgressBar()
        self.scan_progress.setAccessibleName("Scan progress")
        self.scan_progress.setAccessibleDescription(
            "Shows progress while scanning audio files")
        self.scan_progress.setMinimum(0)
        self.scan_progress.setMaximum(100)
        self.scan_progress.setValue(0)
        self.scan_progress.setVisible(False)
        self.scan_progress.setFixedWidth(220)
        footer_layout.addWidget(self.scan_progress)

        self.import_selected_button = QPushButton("Add Selected")
        self.import_selected_button.setAccessibleName("Add Selected")
        self.import_selected_button.setAccessibleDescription(
            "Add selected valid items - Alt+I")
        self.import_selected_button.setDefault(False)
        self.import_selected_button.setAutoDefault(True)
        footer_layout.addWidget(self.import_selected_button)

        self.import_all_button = QPushButton("Add All &Valid")
        self.import_all_button.setAccessibleName("Add All Valid")
        self.import_all_button.setAccessibleDescription(
            "Add all valid items - Alt+V")
        self.import_all_button.setDefault(False)
        self.import_all_button.setAutoDefault(True)
        footer_layout.addWidget(self.import_all_button)

        self.cancel_button = QPushButton("&Cancel")
        self.cancel_button.setAccessibleName("Cancel")
        self.cancel_button.setAccessibleDescription(
            "Close import window - Alt+C")
        self.cancel_button.setDefault(False)
        self.cancel_button.setAutoDefault(True)
        footer_layout.addWidget(self.cancel_button)
        self._update_cancel_button_state()

        self.setTabOrder(self.collection_combo, self.folder_edit)
        self.setTabOrder(self.folder_edit, self.browse_button)
        self.setTabOrder(self.browse_button, self.error_filter_combo)
        self.setTabOrder(self.error_filter_combo, self.scan_button)
        self.setTabOrder(self.scan_button, self.table)

        layout.addLayout(footer_layout)

    def apply_control_styles(self):
        """Apply consistent styling to inputs and buttons."""
        scale_pct = self.scaler.current_scale
        base_height = 20
        scaled_height = int(base_height * (scale_pct / 100.0))
        base_font_size = int(9 * (scale_pct / 100.0))

        font = self.font()
        font.setPointSize(base_font_size)
        self.setFont(font)

        lineedit_style = f"""
            QLineEdit {{
                min-height: {scaled_height}px;
                max-height: {scaled_height}px;
                padding: 2px 4px;
                border: 1px solid palette(dark);
                border-radius: 3px;
            }}
            QLineEdit:focus {{
                border: 2px solid palette(highlight);
                background-color: palette(base);
            }}
        """

        combo_style = f"""
            QComboBox {{
                min-height: {scaled_height}px;
                max-height: {scaled_height}px;
                padding: 2px 4px;
                border: 1px solid palette(dark);
                border-radius: 3px;
            }}
            QComboBox:focus {{
                border: 2px solid palette(highlight);
                background-color: palette(base);
            }}
        """

        button_style = f"""
            QPushButton {{
                padding: 4px 12px;
                min-height: {scaled_height - 4}px;
                max-height: {scaled_height - 4}px;
                border: 1px solid palette(dark);
                border-radius: 3px;
                background-color: palette(button);
            }}
            QPushButton:focus {{
                background-color: palette(highlight);
                color: palette(highlighted-text);
                border: 2px solid palette(dark);
            }}
        """

        for widget in self.findChildren(QLineEdit):
            widget.setStyleSheet(lineedit_style)
        for widget in self.findChildren(QComboBox):
            widget.setStyleSheet(combo_style)
        for widget in self.findChildren(QPushButton):
            widget.setStyleSheet(button_style)

        self.table.setColumnWidth(
            self.COL_YEAR, max(self.scaler.get_scaled_size(68), 56))

        progress_style = f"""
            QProgressBar {{
                min-height: {scaled_height - 2}px;
                max-height: {scaled_height - 2}px;
                border: 1px solid palette(dark);
                border-radius: 3px;
                text-align: center;
                background-color: palette(base);
            }}
            QProgressBar::chunk {{
                background-color: palette(highlight);
            }}
        """
        self.scan_progress.setStyleSheet(progress_style)

        table_style = """
            QTableView::item:selected {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }
            QTableView::item:selected:!active {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }
            QTableView::item:focus {
                outline: none;
                border: none;
            }
            QTableView {
                outline: 0;
            }
        """
        self.table.setStyleSheet(table_style)

    def on_scale_changed(self, value: int):
        """Refresh control styles when zoom changes."""
        self.apply_control_styles()
        self.update_stretch_columns()

    def load_preferences(self):
        """Load import preferences into header fields."""
        self._loading = True

        default_dir = self.settings.value(
            "import/default_directory", "", type=str)
        self.folder_edit.setText(default_dir)

        self.include_subfolders = self.settings.value(
            "import/include_subfolders", True, type=bool)

        formats = []
        allowed_extensions = set()
        for key, label in [
            ("mp3", "MP3"),
            ("m4a", "M4A"),
            ("m4b", "M4B"),
            ("flac", "FLAC"),
            ("ogg", "OGG"),
            ("wav", "WAV"),
            ("wma", "WMA"),
        ]:
            enabled = self.settings.value(
                f"import/formats/{key}", True, type=bool)
            if enabled:
                formats.append(label)
                allowed_extensions.add(f".{key}")

        self.allowed_extensions = allowed_extensions if allowed_extensions else None
        self.current_formats_text = ", ".join(formats) if formats else "None"

        self.import_scenario_mode = self.settings.value(
            "import/scenario/mode", "mass_standard", type=str)
        self.current_mode_text = self.SCENARIO_LABELS.get(
            self.import_scenario_mode, "Mass Standard Import")
        self.author_fallback_mode = self.settings.value(
            "import/fallback/author", "folder", type=str)
        self.title_fallback_mode = self.settings.value(
            "import/fallback/title", "file", type=str)
        self.flip_author_names = self.settings.value(
            "import/flip_author_name", False, type=bool)
        self.autocorrect_trim_whitespace = self.settings.value(
            "import/autocorrect/trim_whitespace", False, type=bool)
        self.autocorrect_strip_leading_punctuation = self.settings.value(
            "import/autocorrect/strip_leading_punctuation", False, type=bool)
        self.autocorrect_remove_non_alphanumeric = self.settings.value(
            "import/autocorrect/remove_non_alphanumeric", False, type=bool)
        self.autocorrect_proper_case = self.settings.value(
            "import/autocorrect/proper_case", False, type=bool)
        self.autocorrect_move_leading_the = self.settings.value(
            "import/autocorrect/move_leading_the_title",
            False,
            type=bool,
        )

        keywords = self.settings.value(
            "import/reader_keywords",
            "reader, read by, narrator, narrated by",
            type=str,
        )
        parsed_keywords = [
            key.strip().lower() for key in keywords.split(",") if key.strip()
        ]
        if parsed_keywords:
            self.reader_keywords = parsed_keywords

        self.import_scanner.configure(
            scenario_mode=self.import_scenario_mode,
            author_fallback_mode=self.author_fallback_mode,
            title_fallback_mode=self.title_fallback_mode,
            reader_keywords=self.reader_keywords,
            trim_whitespace=self.autocorrect_trim_whitespace,
            strip_leading_punctuation=self.autocorrect_strip_leading_punctuation,
            remove_non_alphanumeric=self.autocorrect_remove_non_alphanumeric,
            proper_case_fields=self.autocorrect_proper_case,
            move_leading_the_title=self.autocorrect_move_leading_the,
        )
        self.validator.reload_settings()
        self._update_header_info_line()

        self._load_collection_options()

        self._loading = False

    def _load_collection_options(self):
        """Load target collection options for imports."""
        self.collection_combo.blockSignals(True)
        self.collection_combo.clear()

        collections = self.collection_queries.get_all(active_only=True)
        if not collections:
            default_collection = Collection(name="Default", active=True)
            new_id = self.collection_queries.insert(default_collection)
            collections = [Collection(
                collection_id=new_id, name="Default", active=True)]

        require_selection = len(collections) > 1
        if require_selection:
            self.collection_combo.addItem("None", None)

        for collection in collections:
            self.collection_combo.addItem(
                collection.name, collection.collection_id)

        saved_collection_id = self.settings.value(
            "import/collection_id", 0, type=int)
        if require_selection:
            index = 0
        else:
            index = self.collection_combo.findData(saved_collection_id)
            if index < 0:
                index = 0
        self.collection_combo.setCurrentIndex(index)

        selected_id = self.collection_combo.currentData()
        if selected_id is None:
            self.default_collection_id = None
            self.current_collection_name = ""
        else:
            self.default_collection_id = int(selected_id)
            self.current_collection_name = self.collection_combo.currentText()

        self._update_scan_enabled_state()
        self.collection_combo.blockSignals(False)

    def _update_scan_enabled_state(self):
        """Enable scan only when a target collection is selected."""
        selected_id = self.collection_combo.currentData()
        self.scan_button.setEnabled(selected_id is not None)

    def connect_signals(self):
        """Connect signals to handlers."""
        self.browse_button.clicked.connect(self.on_browse)
        self.scan_button.clicked.connect(self.on_scan)
        self.error_filter_combo.currentIndexChanged.connect(
            self.on_error_filter_changed)
        self.collection_combo.currentIndexChanged.connect(
            self.on_collection_changed)
        self.import_selected_button.clicked.connect(self.on_import_selected)
        self.import_all_button.clicked.connect(self.on_import_all)
        self.cancel_button.clicked.connect(self.on_cancel)
        self.table.cellDoubleClicked.connect(self.on_open_detail)
        self.table.itemSelectionChanged.connect(
            self.on_table_selection_changed)
        self.table.mousePressEvent = self.table_mouse_press
        self.table.keyPressEvent = self.table_key_press

    def _update_cancel_button_state(self):
        """Show Close when idle; show Cancel while scanning."""
        if self._is_scanning:
            self.cancel_button.setText("&Cancel")
            self.cancel_button.setAccessibleName("Cancel")
            self.cancel_button.setAccessibleDescription(
                "Cancel running scan - Alt+C")
        else:
            self.cancel_button.setText("C&lose")
            self.cancel_button.setAccessibleName("Close")
            self.cancel_button.setAccessibleDescription(
                "Close import window - Alt+C")

    def _confirm_cancel_scan(self) -> bool:
        """Ask whether to cancel an active scan."""
        if self._scan_prompt_open:
            return False

        self._scan_prompt_open = True
        try:
            msg = QMessageBox(self)
            msg.setWindowTitle("Cancel Scan")
            msg.setIcon(QMessageBox.Question)
            msg.setText(
                "Cancel the current scan?\n\n"
                "Yes: stop scanning and discard partial scan results.\n"
                "No: continue scanning."
            )
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)
            self._style_message_box(msg)
            result = msg.exec()
            return result == QMessageBox.Yes
        finally:
            self._scan_prompt_open = False

    def install_alt_key_filters(self):
        """Install key filters to block unmapped Alt+letter input."""
        widgets = []
        widgets.extend(self.findChildren(QLineEdit))
        widgets.extend(self.findChildren(QTableWidget))
        for widget in widgets:
            widget.installEventFilter(self)

    def eventFilter(self, source, event):
        """Block Alt+letter input for letters that are not mapped shortcuts."""
        if is_unmapped_alt_letter(event, self.ALLOWED_ALT_LETTERS):
            event.accept()
            return True

        return super().eventFilter(source, event)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        help_shortcut = QShortcut(QKeySequence("F1"), self)
        help_shortcut.activated.connect(self.on_show_shortcuts)

        focus_list_shortcut = QShortcut(QKeySequence("Alt+B"), self)
        focus_list_shortcut.activated.connect(self.on_focus_list)

        open_detail_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        open_detail_shortcut.activated.connect(self.on_open_detail_selected)

        open_detail_shortcut_num = QShortcut(QKeySequence("Ctrl+Enter"), self)
        open_detail_shortcut_num.activated.connect(
            self.on_open_detail_selected)

        read_status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        read_status_shortcut.activated.connect(self.on_read_status_bar)

        add_selected_shortcut = QShortcut(QKeySequence("Alt+I"), self)
        add_selected_shortcut.activated.connect(self.on_import_selected)

        add_all_shortcut = QShortcut(QKeySequence("Alt+V"), self)
        add_all_shortcut.activated.connect(self.on_import_all)

    def on_show_shortcuts(self):
        """Show keyboard shortcuts help dialog."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Keyboard Shortcuts - Import Window")
        dlg.setAccessibleName("Keyboard Shortcuts")
        dlg.resize(560, 420)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        table = QTableWidget()
        table.setAccessibleName("Shortcuts list")
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels([""])

        shortcuts = [
            ("Alt+/", "Read status bar"),
            ("Alt+F", "Folder field"),
            ("Alt+W", "Browse"),
            ("Alt+O", "Error filter"),
            ("Alt+L", "Import collection"),
            ("Alt+S", "Scan"),
            ("Alt+B", "Focus import list"),
            ("Ctrl+Enter", "Open selected import detail"),
            ("Alt+I", "Add selected"),
            ("Alt+V", "Add all valid"),
            ("Alt+C", "Close window"),
            ("F1", "Show keyboard shortcuts"),
        ]

        table.setRowCount(len(shortcuts))
        table.setVerticalHeaderLabels([""] * len(shortcuts))
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setTabKeyNavigation(False)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setStyleSheet(
            "QTableWidget:focus { border: none; outline: none; }"
            "QTableWidget::item:selected { border: none; outline: none; }"
        )

        for row, (key, desc) in enumerate(shortcuts):
            item = QTableWidgetItem(f"{desc} - {key}")
            item.setData(Qt.AccessibleTextRole, f"{desc}: {key}")
            table.setItem(row, 0, item)

        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        font = table.font()
        font.setPointSize(self.scaler.get_scaled_size(11))
        table.setFont(font)

        layout.addWidget(table)

        close_button = QPushButton("Close")
        close_button.setAccessibleName("Close")
        close_button.clicked.connect(dlg.accept)
        btn_font = close_button.font()
        btn_font.setPointSize(self.scaler.get_scaled_size(11))
        close_button.setFont(btn_font)
        layout.addWidget(close_button)

        dlg.setTabOrder(table, close_button)

        dlg.exec()

    def set_status(self, message: str, announce: bool = False):
        """Set status bar message with optional screen reader announcement."""
        self._default_status_message = message
        announce_status_message(self.status_bar, message, move_focus=announce)

    def on_read_status_bar(self):
        """Read current status bar message (Alt+/)."""
        status_text = self._default_status_message
        if QAccessible.isActive():
            self.set_status(status_text, announce=True)
        else:
            QMessageBox.information(
                self,
                "Status Bar",
                f"No screen reader active.\n\nStatus: {status_text}")

    def on_focus_list(self):
        """Move focus to import list table (Alt+B)."""
        self.table.setFocus()
        if self.table.rowCount() > 0 and self.table.currentRow() < 0:
            first_visible = self._first_visible_row()
            if first_visible >= 0:
                self.table.setCurrentCell(first_visible, 0)
        self.set_status("Import list focused")

    def _update_header_info_line(self):
        """Update read-only info line below header controls."""
        flip_text = "On" if self.flip_author_names else "Off"
        info_text = (
            f"Formats: {self.current_formats_text}    "
            f"Mode: {self.current_mode_text}    "
            f"Flip Author: {flip_text}"
        )
        self.setWindowTitle(f"{self._base_window_title} - {info_text}")

    def _first_visible_row(self) -> int:
        """Return first visible row index or -1 when all rows hidden."""
        for row in range(self.table.rowCount()):
            if not self.table.isRowHidden(row):
                return row
        return -1

    def _style_message_box(self, msg: QMessageBox):
        """Apply consistent no-border focus style to message-box buttons."""
        msg.setStyleSheet(
            "QPushButton:focus { border: none; outline: none; }"
            "QPushButton::focus { border: none; outline: none; }"
        )

    def _matches_error_filter(self, item: dict) -> bool:
        """Check whether a scanned item matches current error filter."""
        selected_filter = self.error_filter_combo.currentData()
        status = item.get("status", "")

        if selected_filter == "all":
            return True
        if selected_filter == "valid":
            return status == "OK"
        if selected_filter == "warning":
            return status == "Warning"
        if selected_filter == "error":
            return status in ("Error", "Failed")
        if selected_filter == "duplicate":
            return bool(item.get("is_duplicate")) or status == "Duplicate"

        return True

    def _apply_error_filter(self):
        """Apply current error filter to table row visibility."""
        if not self.scanned_items:
            return

        self._updating_selection_ui = True
        self.table.clearSelection()
        self._updating_selection_ui = False
        self.selected_rows.clear()
        self.selection_anchor_row = None

        for row, item in enumerate(self.scanned_items):
            self.table.setRowHidden(row, not self._matches_error_filter(item))

    def _get_filtered_count(self) -> int:
        """Return number of scanned items matching the active error filter."""
        if not self.scanned_items:
            return 0
        return sum(1 for item in self.scanned_items if self._matches_error_filter(item))

    def on_error_filter_changed(self):
        """Handle error filter combo change."""
        if self._loading:
            return
        self._apply_error_filter()
        first_visible = self._first_visible_row()
        if first_visible >= 0:
            self.table.setCurrentCell(first_visible, self.COL_TITLE)
            self.table.setCurrentIndex(
                self.table.model().index(first_visible, self.COL_TITLE)
            )
            self.table.setFocus(Qt.TabFocusReason)
        self.restore_summary_status()

    def on_collection_changed(self):
        """Handle target collection change for imports."""
        selected_id = self.collection_combo.currentData()
        if selected_id is None:
            self.default_collection_id = None
            self.current_collection_name = ""
            self.settings.setValue("import/collection_id", 0)
            self._update_scan_enabled_state()
            self.set_status("Select a collection to enable scan")
            return

        self.default_collection_id = int(selected_id)
        self.current_collection_name = self.collection_combo.currentText().strip()
        self.settings.setValue("import/collection_id",
                               self.default_collection_id)
        self._update_scan_enabled_state()
        self.set_status(f"Import collection: {self.current_collection_name}")

    def _restore_focus_after_scan(self):
        """Return keyboard focus to Import Window after scan/progress window closes."""
        self.raise_()
        self.activateWindow()
        if self.table.rowCount() > 0:
            if self.table.currentRow() < 0:
                first_visible = self._first_visible_row()
                if first_visible >= 0:
                    self.table.setCurrentCell(first_visible, self.COL_TITLE)
            self.table.setFocus(Qt.TabFocusReason)
        else:
            self.scan_button.setFocus(Qt.TabFocusReason)

    def on_table_selection_changed(self):
        """Announce row selection count in status bar."""
        if self._updating_selection_ui:
            return

        model = self.table.selectionModel()
        selected_indexes = model.selectedIndexes()
        self.selected_rows.clear()

        row_cell_counts = {}
        for idx in selected_indexes:
            row = idx.row()
            row_cell_counts[row] = row_cell_counts.get(row, 0) + 1

        col_count = self.table.columnCount()
        for row, count in row_cell_counts.items():
            if count == col_count:
                self.selected_rows.add(row)

        if self.selected_rows:
            self.announce_selection()
        else:
            self.restore_summary_status()

    def _row_title(self, row: int) -> str:
        """Return title text for a table row."""
        if row < 0:
            return "Unknown"
        item = self.table.item(row, self.COL_TITLE)
        if item and item.text().strip():
            return item.text().strip()
        if 0 <= row < len(self.scanned_items):
            return (self.scanned_items[row].get("book", {}).get("title") or "Unknown").strip() or "Unknown"
        return "Unknown"

    def announce_selection(self):
        """Announce selection with focused title, aligned with Main Window behavior."""
        if not self.selected_rows:
            return

        count = len(self.selected_rows)
        current_row = self.table.currentRow()
        title = self._row_title(current_row)
        shortcuts_text = "Alt+I Add selected, Alt+V Add all valid, Alt+C Close"

        if count == 1:
            message = f"{title} - selected. {shortcuts_text}"
        else:
            message = f"{title} - {count} selected. {shortcuts_text}"

        self.set_status(message, announce=True)

    def update_summary(self, scanned: int = 0, valid: int = 0,
                       errors: int = 0, duplicates: int = 0,
                       announce: bool = False):
        """Update status bar summary."""
        self._summary_counts = {
            "scanned": scanned,
            "valid": valid,
            "errors": errors,
            "duplicates": duplicates,
        }
        filtered = self._get_filtered_count()
        filter_value = self.error_filter_combo.currentData()
        message = (
            f"Scanned: {scanned} | Valid: {valid} | "
            f"Errors: {errors} | Duplicates: {duplicates} | "
            f"Filtered: {filtered}"
        )
        if filter_value and filter_value != "all":
            message += f" | Filter: {self.error_filter_combo.currentText()}"
        self.set_status(message, announce=announce)

    def _format_error_summary(self, errors: list[str]) -> str:
        """Format error list with compact E:/W: prefixes for readability."""
        formatted_errors: list[str] = []
        for err in errors:
            err_text = str(err).strip()
            if not err_text:
                continue
            if err_text.startswith(("E:", "W:")):
                formatted_errors.append(err_text)
                continue
            prefix = "W:" if self.validator.categorize_error(
                err_text) == "warning" else "E:"
            formatted_errors.append(f"{prefix} {err_text}")
        return "; ".join(formatted_errors)

    def restore_summary_status(self):
        """Restore scan summary message after transient selection messages."""
        self.update_summary(
            scanned=self._summary_counts["scanned"],
            valid=self._summary_counts["valid"],
            errors=self._summary_counts["errors"],
            duplicates=self._summary_counts["duplicates"],
        )

    def _show_info_popup(self, title: str, message: str):
        """Show an informational popup."""
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        self._style_message_box(msg)
        msg.exec()

    def on_browse(self):
        """Open folder browser for scan root."""
        current_dir = self.folder_edit.text().strip() or ""
        selected = QFileDialog.getExistingDirectory(
            self, "Select Import Folder", current_dir)
        if selected:
            self.folder_edit.setText(selected)
            self.set_status("Import folder selected")

    def on_scan(self):
        """Scan the selected folder for audiobooks."""
        self.validator.reload_settings()

        target_collection_id = self._get_target_collection_id()
        if target_collection_id is None:
            self.set_status("Select a collection before scanning")
            self.collection_combo.setFocus(Qt.TabFocusReason)
            return

        folder_path = self.folder_edit.text().strip()
        if not folder_path:
            self.set_status("Select a folder before scanning")
            return

        self.raise_()
        self.activateWindow()
        self.scan_button.setFocus(Qt.TabFocusReason)

        if self.table.rowCount() > 0:
            self.table.setRowCount(0)
        self.scanned_items = []
        self.selected_rows.clear()
        self.selection_anchor_row = None
        self.update_summary(0, 0, 0, 0)

        self._is_scanning = True
        self._cancel_scan_requested = False
        self._update_cancel_button_state()
        scan_was_canceled = False

        self.scan_button.setEnabled(False)
        self.browse_button.setEnabled(False)
        self.scan_progress.setVisible(True)
        self.scan_progress.setRange(0, 100)
        self.scan_progress.setValue(0)
        self.scan_progress.setFormat("Scanning... %p%")
        scan_start = time.perf_counter()
        elapsed_text = "00:00"

        def on_progress(processed: int, total: int, file_path: str):
            if total <= 0:
                return
            percent = int((processed / total) * 100)
            current_elapsed = self._format_elapsed(
                time.perf_counter() - scan_start)
            self.scan_progress.setValue(percent)
            self.scan_progress.setFormat(f"Scanning {processed}/{total}")
            self.status_bar.showMessage(
                f"Scanning {processed}/{total}: {os.path.basename(file_path)}"
            )
            QApplication.processEvents()

        try:
            books = self.scanner.scan_folder(
                folder_path,
                include_subfolders=self.include_subfolders,
                allowed_extensions=self.allowed_extensions,
                progress_callback=on_progress,
                cancel_check=lambda: self._cancel_scan_requested,
            )
            scan_was_canceled = self._cancel_scan_requested
        finally:
            elapsed = time.perf_counter() - scan_start
            elapsed_text = self._format_elapsed(elapsed)
            self._is_scanning = False
            self._cancel_scan_requested = False
            self._update_cancel_button_state()
            self.scan_button.setEnabled(True)
            self.browse_button.setEnabled(True)
            if scan_was_canceled:
                self.scan_progress.setFormat(f"Scan canceled ({elapsed_text})")
            else:
                self.scan_progress.setValue(100)
                self.scan_progress.setFormat(f"Scan complete ({elapsed_text})")

        existing_books = self.book_queries.get_all()
        existing_list = [
            {
                "title": b.title,
                "author": b.author_name,
                "year": b.year,
                "collection_id": b.collection_id,
            }
            for b in existing_books
        ]

        self.table.setRowCount(len(books))

        valid_count = 0
        error_count = 0
        duplicate_count = 0

        for row, book in enumerate(books):
            self.import_scanner.apply_preferences(book)

            if self.flip_author_names:
                author_value = (book.get("author") or "").strip()
                if author_value:
                    book["author"] = self.validator.flip_author_name(
                        author_value)

            errors = list(book.get("errors", []))
            errors.extend(self.validator.validate_book(book))

            is_duplicate = self.validator.is_duplicate(
                book,
                existing_list,
                target_collection_id=target_collection_id,
            )
            if is_duplicate:
                has_duplicate_error = any(
                    str(err).strip().lower() == "duplicate"
                    for err in errors
                )
                if not has_duplicate_error:
                    errors.append("Duplicate")
                duplicate_count += 1

            has_hard_error = any(
                self.validator.categorize_error(err) in ("read", "parse")
                for err in errors
            )
            has_warning = any(
                self.validator.categorize_error(err) == "warning"
                for err in errors
            )

            status = "OK"
            if is_duplicate:
                status = "Duplicate"
            elif has_hard_error:
                status = "Error"
                error_count += 1
            elif has_warning:
                status = "Warning"
                valid_count += 1
            else:
                valid_count += 1

            error_summary = self._format_error_summary(errors)

            self.table.setItem(
                row, self.COL_AUTHOR, QTableWidgetItem(book.get("author", "")))
            self.table.setItem(
                row, self.COL_TITLE, QTableWidgetItem(book.get("title", "")))
            self.table.setItem(
                row, self.COL_YEAR, QTableWidgetItem(str(book.get("year") or "")))
            self.table.setItem(row, self.COL_ERROR,
                               QTableWidgetItem(error_summary))
            self.table.setItem(
                row, self.COL_PATH, QTableWidgetItem(book.get("folder", "")))

            self.scanned_items.append({
                "book": book,
                "status": status,
                "errors": errors,
                "is_duplicate": is_duplicate
            })

        if not books:
            self._restore_focus_after_scan()
            if scan_was_canceled:
                self.set_status(
                    f"Scan canceled. No partial results found. Elapsed: {elapsed_text}")
            else:
                self.set_status(
                    f"No audio files found. Elapsed: {elapsed_text}")
            self.update_summary(0, 0, 0, 0)
            return

        self.update_summary(
            scanned=len(books),
            valid=valid_count,
            errors=error_count,
            duplicates=duplicate_count,
            announce=True)
        self._apply_error_filter()

        self._restore_focus_after_scan()

        summary_message = (
            f"Scanned: {len(books)} | Valid: {valid_count} | "
            f"Errors: {error_count} | Duplicates: {duplicate_count} | "
            f"Elapsed: {elapsed_text}"
        )
        if scan_was_canceled:
            self.set_status(
                f"Scan canceled. Partial results kept. {summary_message}")
            self._show_info_popup(
                "Scan Canceled (Partial Results)",
                f"Partial results kept.\n\n{summary_message}")
        else:
            self.set_status(f"Scan complete. {summary_message}")
            self._show_info_popup("Scan Complete", summary_message)

        # Move focus to first title after summary announcement has started
        def focus_first_title():
            first_visible = self._first_visible_row()
            if first_visible >= 0:
                self.table.setCurrentCell(first_visible, self.COL_TITLE)
                self.table.setFocus(Qt.TabFocusReason)

        QTimer.singleShot(250, focus_first_title)

        # Re-apply proportional widths after data population.
        self.update_stretch_columns()

    def on_import_selected(self):
        """Add selected valid items."""
        if not self.scanned_items:
            self.set_status("No scanned items to add")
            return

        selected_rows = {index.row() for index in self.table.selectedIndexes()}
        if not selected_rows:
            self.set_status("Select one or more rows to add")
            return

        self._import_rows(sorted(selected_rows))

    def on_import_all(self):
        """Add all valid items."""
        if not self.scanned_items:
            self.set_status("No scanned items to add")
            return

        eligible_rows = []
        for idx, item in enumerate(self.scanned_items):
            if item["status"] == "OK":
                eligible_rows.append(idx)

        if not eligible_rows:
            self.set_status("No valid items to add")
            return

        self._import_rows(eligible_rows)

    def _refresh_summary_from_items(self):
        """Recalculate summary counters from current scanned items."""
        scanned = len(self.scanned_items)
        valid = 0
        errors = 0
        duplicates = 0

        for item in self.scanned_items:
            status = item.get("status")
            if item.get("is_duplicate"):
                duplicates += 1
            if status in ("Error", "Failed") and not item.get("is_duplicate"):
                errors += 1
            elif status in ("OK", "Warning"):
                valid += 1

        self.update_summary(scanned=scanned, valid=valid,
                            errors=errors, duplicates=duplicates)
        self._apply_error_filter()

    def _import_rows(self, row_indices):
        """Add rows by index from scanned_items."""
        self._is_adding = True
        self._cancel_add_requested = False

        imported = 0
        skipped = 0
        failed = 0
        rows_to_remove = []
        inserted_book_ids = []

        try:
            for row in row_indices:
                QApplication.processEvents()
                if self._cancel_add_requested:
                    break

                if row < 0 or row >= len(self.scanned_items):
                    continue

                item = self.scanned_items[row]
                status = item.get("status")
                if status not in ("OK", "Warning"):
                    skipped += 1
                    continue

                book_data = item.get("book", {})
                title = (book_data.get("title") or "").strip()
                author_text = (book_data.get("author") or "").strip()
                if not title or not author_text:
                    skipped += 1
                    continue

                try:
                    book = self._build_book_from_scan(book_data)
                    book_id = self.book_queries.insert(book)
                    inserted_book_ids.append(book_id)
                    imported += 1
                    rows_to_remove.append(row)
                except Exception as exc:
                    failed += 1
                    item["status"] = "Failed"
                    error_item = self.table.item(row, self.COL_ERROR)
                    error_text = error_item.text() if error_item else ""
                    combined_error = (
                        error_text + "; " if error_text else "") + f"E: {str(exc)}"
                    self.table.setItem(
                        row, self.COL_ERROR, QTableWidgetItem(combined_error))

            if self._cancel_add_requested:
                if inserted_book_ids:
                    self.book_queries.delete_many(inserted_book_ids)
                self.set_status(
                    f"Add canceled. No books were added | Skipped: {skipped} | Failed: {failed}")
                return

            if rows_to_remove:
                sorted_rows_to_remove = sorted(set(rows_to_remove))
                next_focus_row = sorted_rows_to_remove[0]

                for row in reversed(sorted_rows_to_remove):
                    if 0 <= row < len(self.scanned_items):
                        del self.scanned_items[row]
                        self.table.removeRow(row)

                self.selected_rows.clear()
                self.selection_anchor_row = None

                if self.table.rowCount() > 0:
                    target_row = min(next_focus_row, self.table.rowCount() - 1)
                    self.table.setCurrentCell(target_row, self.COL_TITLE)
                    self.table.setFocus(Qt.TabFocusReason)

                self._refresh_summary_from_items()

            self.set_status(
                f"Added: {imported} | Skipped: {skipped} | Failed: {failed}")

            remaining = len(self.scanned_items)
            self._show_info_popup(
                "Add Complete",
                f"Books added: {imported}\nLeft in import list: {remaining}")
        finally:
            self._is_adding = False
            self._cancel_add_requested = False

    def _apply_detail_edits(self, row: int, detail_window: ImportDetailWindow):
        """Apply edits returned from ImportDetailWindow to scanned item + table."""
        item = self.scanned_items[row]
        for key in [
            "title", "author", "year", "narrator",
            "genre", "series", "collection", "comment"
        ]:
            if key in detail_window.book_data:
                item["book"][key] = detail_window.book_data[key]

        self.table.setItem(row, self.COL_TITLE, QTableWidgetItem(
            detail_window.book_data.get("title", "")))
        self.table.setItem(row, self.COL_AUTHOR, QTableWidgetItem(
            detail_window.book_data.get("author", "")))
        self.table.setItem(row, self.COL_YEAR, QTableWidgetItem(
            str(detail_window.book_data.get("year") or "")))

    def _focus_import_row(self, row: int):
        """Restore focus to a row in the import list after closing detail."""
        if self.table.rowCount() == 0:
            return

        target_row = max(0, min(row, self.table.rowCount() - 1))
        self.table.setCurrentCell(target_row, self.COL_TITLE)
        self.table.scrollTo(self.table.model().index(
            target_row, self.COL_TITLE))
        self.table.setFocus(Qt.TabFocusReason)

    def on_open_detail(self, row: int = 0, col: int = 0):
        """Open import detail window to view/edit scanned metadata."""
        if self.table.rowCount() == 0:
            self.set_status("No items to view")
            return

        if row < 0 or row >= len(self.scanned_items):
            self.set_status("Select a valid row")
            return

        while 0 <= row < len(self.scanned_items):
            item = self.scanned_items[row]
            book_data = item.get("book", {})
            errors = list(item.get("errors", []))
            if item.get("is_duplicate"):
                has_duplicate_error = any(
                    str(err).strip().lower() == "duplicate"
                    for err in errors
                )
                if not has_duplicate_error:
                    errors.append("Duplicate")

            detail_window = ImportDetailWindow(
                self.db, self.scaler, self.theme_manager,
                book_data=book_data.copy(), errors=errors,
                current_index=row, total_count=len(self.scanned_items),
                parent=self)

            result = detail_window.exec()

            if result == QDialog.Accepted:
                self._apply_detail_edits(row, detail_window)
                self.set_status("Changes applied to import item")
                self._focus_import_row(row)
                return

            if result == ImportDetailWindow.RESULT_PREV:
                self._apply_detail_edits(row, detail_window)
                if row > 0:
                    row -= 1
                else:
                    self.set_status("Already at first item")
                    self._focus_import_row(row)
                    return
                continue

            if result == ImportDetailWindow.RESULT_NEXT:
                self._apply_detail_edits(row, detail_window)
                if row < len(self.scanned_items) - 1:
                    row += 1
                else:
                    self.set_status("Already at last item")
                    self._focus_import_row(row)
                    return
                continue

            if result == ImportDetailWindow.RESULT_SKIP:
                if 0 <= row < len(self.scanned_items):
                    del self.scanned_items[row]
                    self.table.removeRow(row)
                    self.selected_rows.clear()
                    self.selection_anchor_row = None
                    self._refresh_summary_from_items()

                    if self.table.rowCount() > 0:
                        target_row = min(row, self.table.rowCount() - 1)
                        self._focus_import_row(target_row)
                    self.set_status("Import item discarded")
                return

            self._focus_import_row(row)
            return

    def _get_selected_or_current_row(self) -> int:
        """Return selected row, current row, or -1 if unavailable."""
        if self.selected_rows:
            return min(self.selected_rows)

        current_row = self.table.currentRow()
        if current_row >= 0:
            return current_row

        if self.table.rowCount() > 0:
            return 0

        return -1

    def on_open_detail_selected(self):
        """Open detail window for selected/current row."""
        row = self._get_selected_or_current_row()
        if row < 0:
            self.set_status("No items to view")
            return
        self.on_open_detail(row, self.table.currentColumn())

    def on_cancel(self):
        """Handle cancel request for add-in-progress or close dialog."""
        if self._is_scanning:
            if self._confirm_cancel_scan():
                self._cancel_scan_requested = True
                self.set_status("Canceling scan...")
            else:
                self.set_status("Continuing scan")
            return

        if self._is_adding:
            msg = QMessageBox(self)
            msg.setWindowTitle("Stop Add")
            msg.setIcon(QMessageBox.Question)
            msg.setText(
                "Stop adding books now?\n\n"
                "Any books added in this run will be removed so no partial adds remain."
            )
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)
            self._style_message_box(msg)
            result = msg.exec()

            if result == QMessageBox.Yes:
                self._cancel_add_requested = True
                self.set_status("Stopping add operation...")
            else:
                self.set_status("Continuing add operation")
            return

        self.reject()

    def table_mouse_press(self, event):
        """Handle mouse press with main-window style row selection."""
        if event.button() == Qt.LeftButton:
            index = self.table.indexAt(event.position().toPoint())
            if not index.isValid():
                QTableWidget.mousePressEvent(self.table, event)
                return

            modifiers = event.modifiers()
            row = index.row()

            if modifiers & Qt.ShiftModifier:
                if self.selection_anchor_row is None:
                    self.selection_anchor_row = row
                self._select_row_range(
                    self.selection_anchor_row, row, index.column())
                event.accept()
                return

            self._updating_selection_ui = True
            self.table.clearSelection()
            self.table.selectionModel().clearSelection()
            self._updating_selection_ui = False
            self.selected_rows.clear()
            self.selection_anchor_row = None
            self.restore_summary_status()
            self.table.setCurrentCell(index.row(), index.column())
            event.accept()
            return

        QTableWidget.mousePressEvent(self.table, event)

    def table_key_press(self, event):
        """Handle table key presses with main-window style selection behavior."""
        if event.key() in (Qt.Key_Up, Qt.Key_Down, Qt.Key_PageUp, Qt.Key_PageDown, Qt.Key_Home, Qt.Key_End):
            modifiers = event.modifiers()

            if modifiers & Qt.ShiftModifier:
                if self.selection_anchor_row is not None:
                    self.extend_selection_with_arrow(event.key())
                    event.accept()
                    return
                self.move_current_without_selection(event.key())
                event.accept()
                return

            if modifiers & Qt.ControlModifier:
                QTableWidget.keyPressEvent(self.table, event)
                return

            self.move_current_without_selection(event.key())
            event.accept()
            return

        if event.key() in (Qt.Key_Left, Qt.Key_Right):
            self.move_column_without_selection(event.key())
            event.accept()
            return

        if event.key() == Qt.Key_Space and (event.modifiers() & Qt.ShiftModifier):
            row = self.table.currentRow()
            col = self.table.currentColumn() if self.table.currentColumn() >= 0 else 0
            if row >= 0:
                self.selection_anchor_row = row
                self._select_row_range(row, row, col)
            event.accept()
            return

        QTableWidget.keyPressEvent(self.table, event)

    def move_current_without_selection(self, key: int):
        """Move current cell and clear selection when navigating rows."""
        row_count = self.table.rowCount()
        col_count = self.table.columnCount()
        if row_count == 0 or col_count == 0:
            return

        visible_rows = [r for r in range(
            row_count) if not self.table.isRowHidden(r)]
        if not visible_rows:
            return

        row = self.table.currentRow(
        ) if self.table.currentRow() >= 0 else visible_rows[0]
        if row not in visible_rows:
            row = visible_rows[0]
        col = self.table.currentColumn() if self.table.currentColumn() >= 0 else 0
        page_step = max(self.table.verticalScrollBar().pageStep() - 1, 1)
        current_visible_index = visible_rows.index(row)

        changing_rows = False
        if key == Qt.Key_Up:
            row = visible_rows[max(current_visible_index - 1, 0)]
            changing_rows = True
        elif key == Qt.Key_Down:
            row = visible_rows[min(
                current_visible_index + 1, len(visible_rows) - 1)]
            changing_rows = True
        elif key == Qt.Key_PageUp:
            row = visible_rows[max(current_visible_index - page_step, 0)]
            changing_rows = True
        elif key == Qt.Key_PageDown:
            row = visible_rows[min(
                current_visible_index + page_step, len(visible_rows) - 1)]
            changing_rows = True
        elif key == Qt.Key_Home:
            row = visible_rows[0]
            changing_rows = True
        elif key == Qt.Key_End:
            row = visible_rows[-1]
            changing_rows = True

        if changing_rows:
            self._updating_selection_ui = True
            self.table.clearSelection()
            self.table.selectionModel().clearSelection()
            self._updating_selection_ui = False
            self.selected_rows.clear()
            self.selection_anchor_row = None
            self.restore_summary_status()

        self.table.setCurrentCell(row, col)
        self.table.setCurrentIndex(self.table.model().index(row, col))
        self.table.scrollTo(self.table.model().index(row, col))

    def move_column_without_selection(self, key: int):
        """Move between columns without changing row selection state."""
        col_count = self.table.columnCount()
        if col_count == 0:
            return

        row = self.table.currentRow() if self.table.currentRow() >= 0 else 0
        col = self.table.currentColumn() if self.table.currentColumn() >= 0 else 0

        if key == Qt.Key_Left:
            col = max(col - 1, 0)
        elif key == Qt.Key_Right:
            col = min(col + 1, col_count - 1)

        self.table.setCurrentCell(row, col)
        self.table.setCurrentIndex(self.table.model().index(row, col))
        self.table.scrollTo(self.table.model().index(row, col))

    def extend_selection_with_arrow(self, key: int):
        """Extend row selection from anchor using Shift+navigation keys."""
        if self.selection_anchor_row is None:
            return

        row_count = self.table.rowCount()
        if row_count == 0:
            return

        visible_rows = [r for r in range(
            row_count) if not self.table.isRowHidden(r)]
        if not visible_rows:
            return
        if self.selection_anchor_row not in visible_rows:
            self.selection_anchor_row = visible_rows[0]

        row = self.table.currentRow(
        ) if self.table.currentRow() >= 0 else visible_rows[0]
        if row not in visible_rows:
            row = visible_rows[0]
        col = self.table.currentColumn() if self.table.currentColumn() >= 0 else 0
        page_step = max(self.table.verticalScrollBar().pageStep() - 1, 1)
        current_visible_index = visible_rows.index(row)

        target_row = row
        if key == Qt.Key_Up:
            target_row = visible_rows[max(current_visible_index - 1, 0)]
        elif key == Qt.Key_Down:
            target_row = visible_rows[min(
                current_visible_index + 1, len(visible_rows) - 1)]
        elif key == Qt.Key_PageUp:
            target_row = visible_rows[max(
                current_visible_index - page_step, 0)]
        elif key == Qt.Key_PageDown:
            target_row = visible_rows[min(
                current_visible_index + page_step, len(visible_rows) - 1)]
        elif key == Qt.Key_Home:
            target_row = visible_rows[0]
        elif key == Qt.Key_End:
            target_row = visible_rows[-1]

        self._select_row_range(self.selection_anchor_row, target_row, col)

    def _select_row_range(self, anchor_row: int, target_row: int, current_col: int = 0):
        """Select full rows between anchor and target using item selection mode."""
        row_count = self.table.rowCount()
        visible_rows = [r for r in range(
            row_count) if not self.table.isRowHidden(r)]
        if not visible_rows:
            return
        if anchor_row not in visible_rows:
            anchor_row = visible_rows[0]
        if target_row not in visible_rows:
            target_row = visible_rows[0]

        start_row = min(anchor_row, target_row)
        end_row = max(anchor_row, target_row)

        self._updating_selection_ui = True
        self.table.selectionModel().clearSelection()

        col_count = self.table.columnCount()
        for row in range(start_row, end_row + 1):
            if self.table.isRowHidden(row):
                continue
            for col in range(col_count):
                index = self.table.model().index(row, col)
                self.table.selectionModel().select(index, QItemSelectionModel.Select)

        self.table.setCurrentCell(target_row, current_col)
        self.table.setCurrentIndex(
            self.table.model().index(target_row, current_col))
        self.table.scrollTo(self.table.model().index(target_row, current_col))
        self._updating_selection_ui = False

        self.selected_rows = {
            row for row in range(start_row, end_row + 1)
            if not self.table.isRowHidden(row)
        }
        self.announce_selection()

    def keyPressEvent(self, event):
        """Override to prevent Enter from closing the dialog."""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            event.ignore()
            return
        super().keyPressEvent(event)

    def resizeEvent(self, event):
        """Keep import table stretch columns proportional on window resize."""
        super().resizeEvent(event)
        self.update_stretch_columns()

    def showEvent(self, event):
        """Apply initial proportional import column widths after layout."""
        super().showEvent(event)
        QTimer.singleShot(0, self.update_stretch_columns)

    def update_stretch_columns(self):
        """Update Import table stretch column widths proportionally."""
        if not hasattr(self, '_stretch_columns') or not hasattr(self, 'table'):
            return

        header = self.table.horizontalHeader()
        fixed_width = 0
        for col in range(self.table.columnCount()):
            if col not in self._stretch_columns:
                fixed_width += header.sectionSize(col)

        available = self.table.viewport().width() - fixed_width
        if available < 100:
            return

        total_weight = sum(self._stretch_columns.values())
        for col, weight in self._stretch_columns.items():
            width = int(available * weight / total_weight)
            self.table.setColumnWidth(col, max(width, 90))

    def accept(self):
        """Handle dialog accept."""
        announce_dialog_closed(self)
        super().accept()

    def reject(self):
        """Handle dialog reject."""
        announce_dialog_closed(self)
        super().reject()

    def closeEvent(self, event):
        """Intercept close while scanning to confirm cancel/continue."""
        if self._is_scanning:
            if self._confirm_cancel_scan():
                self._cancel_scan_requested = True
                self.set_status("Canceling scan...")
            else:
                self.set_status("Continuing scan")
            event.ignore()
            return

        super().closeEvent(event)
