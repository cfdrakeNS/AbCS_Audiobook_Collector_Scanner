"""Book List Import Window - Import books from spreadsheet files."""

from __future__ import annotations

import csv
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

    # Create a dummy pd module to prevent import errors
    class DummyPandas:
        class DataFrame:
            def __init__(self, data=None):
                self.data = data or []
                self.columns = []

            def __len__(self):
                return len(self.data)

            def iloc(self):
                return self.data

        @staticmethod
        def read_csv(_filepath):
            raise ImportError("pandas not available - install with: pip install pandas")

        @staticmethod
        def read_excel(_filepath):
            raise ImportError("pandas not available - install with: pip install pandas")

        notna = lambda x: x is not None

    pd = DummyPandas()

from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QGroupBox,
    QLineEdit,
    QStatusBar,
    QMessageBox,
    QFileDialog,
    QHeaderView,
    QAbstractItemView,
    QCheckBox,
    QTextEdit,
    QWidget,
    QScrollArea,
    QSizePolicy,
)
from PySide6.QtGui import QShortcut, QKeySequence, QAccessible, QAction

from src.database import (
    BookQueries,
    CollectionQueries,
    ReadingQueries,
    AuthorQueries,
    SeriesQueries,
    GenreQueries,
)
from src.accessibility.scaling import UIScaler
from src.accessibility.accessible_events import announce_status_message
from src.accessibility.style_helpers import (
    exec_styled_message_box,
    build_accessible_message_box_style,
)
from src.accessibility.theme_manager import ThemeManager
from src.accessibility.shortcuts import get_shortcut_manager, ShortcutContext
from src.accessibility.key_filters import is_unmapped_alt_letter


class BookListImportWindow(QDialog):
    """Book List Import window with full accessibility support."""

    # Alt+Key filtering for accessibility
    ALLOWED_ALT_LETTERS = "W M T A Y P S G R I H F C V O E /"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from src.accessibility.icon_helper import get_app_icon

        self.setWindowIcon(get_app_icon())

    def _normalize_title_for_match(self, title: str) -> str:
        """Normalize title for matching: strip series number, move trailing article to beginning, clean, re-append series number if present."""
        from src.web.web_book_api import WebBookAPI

        api = WebBookAPI()
        t, series_number = api._strip_series_number(title)
        t = api._move_article_to_beginning(t)
        t = api._clean_text_field(t)
        if series_number:
            t = f"{t} - {series_number}"
        return t.lower()

    def _normalize_author_for_match(self, author: str) -> str:
        """Normalize author for matching: clean and canonicalize as for DB fields."""
        from src.web.web_book_api import WebBookAPI

        api = WebBookAPI()
        return api._apply_author_transformations(author).lower()

    def __init__(self, db, scaler: UIScaler, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self.db = db
        self.scaler = scaler
        self.theme_manager = theme_manager
        self.book_queries = BookQueries(db)
        self.collection_queries = CollectionQueries(db)
        self.reading_queries = ReadingQueries(db)
        self.author_queries = AuthorQueries(db)
        self.series_queries = SeriesQueries(db)
        self.genre_queries = GenreQueries(db)
        self.import_errors = []  # Track errors for CSV export

        # Check for pandas availability
        if not PANDAS_AVAILABLE:
            from src.accessibility.icon_helper import get_app_icon

            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Critical,
                title="Missing Dependencies",
                text="Book List Import requires pandas and openpyxl.\n\nPlease install with:\npip install pandas openpyxl",
                buttons=QMessageBox.Ok,
                default_button=QMessageBox.Ok,
                window_icon=get_app_icon(),
            )
            self.reject()
            return

        # State
        self.selected_file = None
        self.file_data = None
        self.column_count = 0
        self.import_mode = "new"  # "new" or "read_date"
        self._default_status_message = "Ready"

        # Window setup - match Book Details open size.
        self.setWindowTitle("Book List Import")
        self.setAccessibleName("Book List Import Window")
        self.setAccessibleDescription(
            "Import books from spreadsheet files with field mapping"
        )
        # Keep the window resizable to narrower widths like ImportWindow.
        self.setMinimumSize(560, 350)
        self.resize(350, 200)

        self.setup_ui()
        self.apply_theme()

        # Keep this window responsive to runtime zoom changes.
        self.scaler.scale_changed.connect(self.on_scale_changed)
        self.on_scale_changed(self.scaler.current_scale)

        # Initial focus is applied in showEvent so screen readers announce instructions first.

        # Apply button styling to match other windows
        self.apply_button_styling()

        # Install event filters for combo box anti-noise pattern
        self.install_combo_filters()

        # Setup shortcuts using centralized ShortcutManager
        self.setup_shortcuts()

    def on_scale_changed(self, _scale_percentage: int):
        """Recompute fixed metrics so this window scales like the rest of the app."""
        if not hasattr(self, "mapping_table"):
            return

        # Recompute panel widths
        if hasattr(self, "left_widget"):
            self.left_widget.setMinimumWidth(110)
            self.left_widget.setMaximumWidth(320)
        if hasattr(self, "right_widget"):
            self.right_widget.setMaximumWidth(self.scaler.get_scaled_size(220))
        if hasattr(self, "mapping_group"):
            self.mapping_group.setMaximumWidth(16777215)

        # Recompute table and combo sizing
        header = self.mapping_table.horizontalHeader()
        self._update_mapping_field_column_width()
        combo_width = max(100, self.scaler.get_scaled_size(130))
        self.mapping_table.setColumnWidth(1, combo_width)
        self.mapping_table.setMaximumWidth(16777215)
        header.resizeSections(QHeaderView.ResizeToContents)

        # Keep mapping combos readable at low scales.
        min_combo_width = max(90, self.scaler.get_scaled_size(120))
        max_combo_width = max(130, self.scaler.get_scaled_size(160))
        for combo in self.field_mappings.values():
            combo.setMinimumWidth(min_combo_width)
            combo.setMaximumWidth(max_combo_width)

        # Use a direct scale-based row height.  sizeHint() picks up the global
        # scaler min-height (44px at 100%) which would make the table huge.
        row_height = max(22, self.scaler.get_scaled_size(26))
        for row in range(self.mapping_table.rowCount()):
            self.mapping_table.setRowHeight(row, row_height)

        header_height = self.mapping_table.horizontalHeader().height()
        frame = self.mapping_table.frameWidth() * 2
        table_height = (
            header_height + (row_height * self.mapping_table.rowCount()) + frame + 4
        )
        self.mapping_table.setMinimumHeight(table_height)
        self.mapping_table.setMaximumHeight(table_height)

        # Scale the window size itself so it grows/shrinks with zoom level.
        min_w = max(760, self.scaler.get_scaled_size(760))
        min_h = max(300, self.scaler.get_scaled_size(450))
        self.setMinimumSize(min_w, min_h)
        scaled_w = max(min_w, self.scaler.get_scaled_size(850))
        scaled_h = max(min_h, self.scaler.get_scaled_size(500))
        self.resize(scaled_w, scaled_h)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts using ShortcutManager (except F1, Escape, Alt+/)."""
        from src.accessibility.shortcuts import get_shortcut_manager, ShortcutContext

        mgr = get_shortcut_manager()
        callback_map = {
            "browse_button": lambda: self.browse_file(),
            "options_group": self.focus_options_section,
            "title_mapping": lambda: self.focus_mapping_combo("title"),
            "author_mapping": lambda: self.focus_mapping_combo("author"),
            "year_mapping": lambda: self.focus_mapping_combo("year"),
            "plot_mapping": lambda: self.focus_mapping_combo("plot"),
            "series_mapping": lambda: self.focus_mapping_combo("series"),
            "genre_mapping": lambda: self.focus_mapping_combo("genre"),
            "reader_mapping": lambda: self.focus_mapping_combo("reader"),
            "read_date_mapping": lambda: self.focus_mapping_combo("read_date"),
            "time_mapping": lambda: self.focus_mapping_combo("time"),
            "tracks_mapping": lambda: self.focus_mapping_combo("tracks"),
            "export_button": lambda: self.export_errors_csv(),
            "import_button": lambda: self.import_books(),
        }
        mgr.register_alt_shortcuts(
            self, ShortcutContext.BOOK_LIST_IMPORT_WINDOW, callback_map
        )

        # F1 help shortcut remains local
        self.help_shortcut = QShortcut(QKeySequence("F1"), self)
        self.help_shortcut.activated.connect(self.on_show_shortcuts)

        # Alt+/ remains local for status bar read
        self.read_status_bar_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.read_status_bar_shortcut.activated.connect(self.on_read_status_bar)

        # Alt+H local shortcut for instructions focus
        self.instructions_shortcut = QShortcut(QKeySequence("Alt+H"), self)
        self.instructions_shortcut.activated.connect(self.focus_instructions_section)

    def focus_mapping_combo(self, field_name):
        """Focus the combo box for the specified field mapping."""
        if hasattr(self, "field_mappings") and field_name in self.field_mappings:
            self.field_mappings[field_name].setFocus()
            self.field_mappings[field_name].showPopup()

    def focus_options_section(self):
        """Focus first control in Options section."""
        if hasattr(self, "load_books_check"):
            self.load_books_check.setFocus()
            self.set_status("Options section")

    def focus_instructions_section(self):
        """Focus instructions section."""
        if hasattr(self, "instructions_label"):
            self.instructions_label.setFocus()
            self.set_status("How to use instructions")

    def showEvent(self, event):
        """Set initial focus to instructions when window first opens."""
        super().showEvent(event)
        QTimer.singleShot(0, self.focus_instructions_section)

    def install_combo_filters(self):
        """Install event filters on combo boxes for anti-noise pattern."""
        for widget in self.findChildren(QComboBox):
            widget.installEventFilter(self)

    def eventFilter(self, source, event):
        """Event filter for combo box anti-noise pattern and Alt+letter filtering."""
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QEvent

        # Handle combo box anti-noise pattern
        if isinstance(source, QComboBox) and event.type() == QEvent.KeyPress:
            key = event.key()
            modifiers = event.modifiers()

            # Block plain Up/Down arrows on combo boxes
            if key in (Qt.Key_Up, Qt.Key_Down) and modifiers == Qt.NoModifier:
                QApplication.beep()
                return True

            # Allow Alt+Up/Down to open dropdown
            if key in (Qt.Key_Up, Qt.Key_Down) and modifiers & Qt.AltModifier:
                source.showPopup()
                return True

        # Handle Alt+letter filtering
        if event.type() == QEvent.KeyPress:
            key = event.key()
            modifiers = event.modifiers()

            # Handle Escape to close window
            if key == Qt.Key_Escape:
                self.reject()
                return True

            # Handle Alt+letter filtering
            if modifiers & Qt.AltModifier and event.text().upper():
                if event.text().upper() in self.ALLOWED_ALT_LETTERS:
                    # Let the event through for allowed Alt+letters
                    return super().eventFilter(source, event)
                else:
                    # Block unmapped Alt+letters
                    QApplication.beep()
                    return True

        return super().eventFilter(source, event)

    def keyPressEvent(self, event):
        """Handle Enter key for focused buttons (Pattern #18: Global Enter anti-pattern avoidance)."""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            focused_widget = self.focusWidget()
            if isinstance(focused_widget, QPushButton):
                # Let Qt handle Enter on buttons (default behavior)
                focused_widget.click()
                event.accept()
                return
        super().keyPressEvent(event)

    def apply_button_styling(self):
        """Apply button styling to match book_details window."""
        scaled_height = self.scaler.get_scaled_size(24)

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

        for widget in self.findChildren(QPushButton):
            widget.setStyleSheet(button_style)
            widget.setDefault(False)
            widget.setAutoDefault(False)

    def setup_ui(self):
        """Setup the user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)

        # File selection
        file_group = QGroupBox("File Selection")
        file_group.setAccessibleName("File selection group")
        file_layout = QHBoxLayout(file_group)

        file_label = QLabel("Spreadsheet file:")
        file_label.setAccessibleName("")
        file_label.setAccessibleDescription("")
        self.file_edit = QLineEdit()
        self.file_edit.setReadOnly(True)
        self.file_edit.setAccessibleName("Selected file")
        self.file_edit.setAccessibleDescription("Path to selected spreadsheet file")
        self.file_edit.setMinimumWidth(0)
        self.file_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.browse_button = QPushButton("Browse...")
        self.browse_button.setAccessibleName("Browse for file")
        self.browse_button.setAccessibleDescription(
            "Browse for spreadsheet file - Alt+W"
        )
        self.browse_button.clicked.connect(self.browse_file)

        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_edit)
        file_layout.addWidget(self.browse_button)

        main_layout.addWidget(file_group)

        # Field mapping container with instructions on left, table on right
        mapping_container = QWidget()
        mapping_layout = QHBoxLayout(mapping_container)
        mapping_layout.setContentsMargins(0, 0, 0, 0)
        mapping_layout.setSpacing(12)
        mapping_layout.setAlignment(Qt.AlignTop)  # Align all panels to top

        # Left side - Instructions
        instructions_group = QGroupBox("Instructions")
        instructions_group.setAccessibleName("Instructions group")
        instructions_layout = QVBoxLayout(instructions_group)
        # Move instructions group down a bit for visual separation
        instructions_layout.setContentsMargins(0, 16, 0, 0)

        # Instructions text for screen readers (single sentence format)
        instructions_text = (
            "How to use: Select an Excel .xlsx or .xls or OpenDocument .ods or CSV file using the Browse button. "
            "Map spreadsheet columns to book fields using the dropdown combos. "
            "Use checkboxes in Options column for import settings. "
            "Title and Author fields are required for import. "
            "Click Import to process the file. "
            "Press Alt+H to return focus to these instructions."
        )

        self.instructions_label = QLabel(
            "How to use:\n"
            "1 Select an Excel (.xlsx, .xls), OpenDocument (.ods), or CSV file using the Browse button\n"
            "2 Map spreadsheet columns to book fields using the dropdown combos\n"
            "3 Use checkboxes in Options column for import settings\n"
            "4 Title and Author fields are required for import\n"
            "5 Click Import to process the file\n"
            "Press Alt+H to return focus to these instructions"
        )
        self.instructions_label.setWordWrap(True)
        self.instructions_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # NO setTextInteractionFlags — keeps Qt using QAccessibleInterface (name-based)
        # instead of QAccessibleTextInterface (line-by-line) so the screen reader reads the whole text
        self.instructions_label.setFocusPolicy(Qt.TabFocus)

        # Put the full text here — this is what the screen reader reads on focus
        self.instructions_label.setAccessibleName(instructions_text)
        self.instructions_label.setAccessibleDescription(
            "Step-by-step instructions for using the book list import"
        )

        # Set fixed height to fit all text without scrolling
        fixed_height = self.scaler.get_scaled_size(200)
        self.instructions_label.setMinimumHeight(fixed_height)
        self.instructions_label.setMinimumWidth(0)
        self.instructions_label.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )

        # Match the visual style
        self.instructions_label.setStyleSheet(
            "QLabel {"
            "  background-color: palette(base);"
            "  border: 1px solid palette(mid);"
            "  padding: 5px;"
            "}"
        )

        # Set instructions size to be narrower on the left
        # (instructions_group will be added to left_layout below)
        instructions_layout.addWidget(self.instructions_label)
        instructions_group.setLayout(instructions_layout)

        # Right side - Field mapping table (takes more space)
        mapping_group = QGroupBox("Field Mapping")
        self.mapping_group = mapping_group
        mapping_group.setAccessibleName("Field mapping group")
        mapping_group.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Maximum)
        mapping_table_layout = QVBoxLayout(mapping_group)
        mapping_table_layout.setContentsMargins(4, 4, 4, 4)
        mapping_table_layout.setSpacing(0)
        mapping_table_layout.setAlignment(Qt.AlignTop)  # Align to top

        # Create table for field mapping
        self.mapping_table = QTableWidget()
        self.mapping_table.setAccessibleName("Mapping table")
        self.mapping_table.setAccessibleDescription(
            "Map spreadsheet columns to book fields"
        )

        # Setup table columns - Field, Column (no options column)
        self.mapping_table.setColumnCount(2)

        self.mapping_table.setHorizontalHeaderLabels(["Field", "Column"])

        # Lock first column (Field names) - no selection, no focus
        self.mapping_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.mapping_table.setSelectionBehavior(QAbstractItemView.SelectItems)
        # We'll lock the first column by making items non-editable after setup

        # Setup table rows
        self.setup_mapping_table()

        # Table styling and navigation
        header = self.mapping_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setStretchLastSection(
            False
        )  # Prevent column 1 expanding past combo_width

        # Combo column fixed; field column auto-sizes to label text.
        # Reduce combo column and table width by 1/3 for better fit at high zoom
        combo_width = self.scaler.get_scaled_size(90)
        self.mapping_table.setColumnWidth(1, combo_width)  # Column selector

        # Max width: labels auto-size + fixed combo + border/scrollbar overhead
        self.mapping_table.setMaximumWidth(self.scaler.get_scaled_size(220))
        mapping_group.setMaximumWidth(self.scaler.get_scaled_size(230))

        # Suppress the global scaler min-height (44px at 100%) on these small
        # mapping combos so rows stay compact.  Widget-level stylesheet wins
        # over app-level stylesheet, so this overrides the global rule.
        self.mapping_table.setStyleSheet("""
            QTableWidget {
                gridline-color: palette(mid);
            }
            QTableWidget::item {
                padding: 2px 4px;
            }
            QComboBox {
                min-height: 0px;
            }
        """)

        # Disable tab navigation on table - we'll handle combo navigation directly
        self.mapping_table.setTabKeyNavigation(False)
        self.mapping_table.setFocusPolicy(Qt.NoFocus)  # Table itself doesn't get focus

        mapping_table_layout.addWidget(self.mapping_table)
        mapping_group.setLayout(mapping_table_layout)

        # Options group for right side
        options_group = QGroupBox("Options")
        options_group.setAccessibleName("Options group")
        options_layout = QVBoxLayout(options_group)
        options_layout.setAlignment(Qt.AlignTop)  # Align to top
        # Move options group down a bit for visual separation
        options_layout.setContentsMargins(0, 16, 0, 0)

        # Import Type subgroup
        import_type_group = QGroupBox("Import Type")
        import_type_group.setAccessibleName("Import Type group")
        import_type_layout = QVBoxLayout(import_type_group)
        # Move import type group down a bit for visual separation
        import_type_layout.setContentsMargins(0, 12, 0, 0)

        # Load Books checkbox
        self.load_books_check = QCheckBox("Add Book From List")
        self.load_books_check.setAccessibleName("Add Book From List")
        self.load_books_check.setChecked(True)
        self.load_books_check.toggled.connect(self.on_load_books_toggled)
        import_type_layout.addWidget(self.load_books_check)

        # Add Read Date checkbox
        self.add_read_date_check = QCheckBox("Add Read Date from List")
        self.add_read_date_check.setAccessibleName("Add Read Date from List")
        self.add_read_date_check.toggled.connect(self.on_add_read_date_toggled)
        import_type_layout.addWidget(self.add_read_date_check)

        import_type_group.setLayout(import_type_layout)
        options_layout.addWidget(import_type_group)

        # File has header checkbox
        self.file_has_header_check = QCheckBox("My file Has Header")
        self.file_has_header_check.setAccessibleName("My file Has Header")
        self.file_has_header_check.setChecked(True)
        self.file_has_header_check.toggled.connect(self.on_file_has_header_toggled)
        options_layout.addWidget(self.file_has_header_check)

        options_group.setLayout(options_layout)
        options_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # Add left widget first (instructions) - wider by 1/3
        left_layout = QVBoxLayout()
        left_layout.addWidget(instructions_group)
        left_layout.addStretch()

        left_widget = QWidget()
        self.left_widget = left_widget
        left_widget.setLayout(left_layout)
        # Double instructions panel width (was max 320)
        left_widget.setMinimumWidth(220)
        left_widget.setMaximumWidth(640)
        mapping_layout.addWidget(left_widget, 2)  # Give more stretch to instructions

        # Add options second (center)
        right_layout = QVBoxLayout()
        right_layout.addWidget(options_group)
        right_layout.addStretch()

        right_widget = QWidget()
        self.right_widget = right_widget
        right_widget.setLayout(right_layout)
        # Reduce options panel width by 1/4 (was 180)
        right_widget.setMaximumWidth(135)
        mapping_layout.addWidget(right_widget, 1)  # Less stretch for options

        # Add table third (far right) - wrapped same as other panels so AlignTop works
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.addWidget(mapping_group)
        table_layout.addStretch()
        table_widget = QWidget()
        table_widget.setLayout(table_layout)
        mapping_layout.addWidget(table_widget)

        main_layout.addWidget(mapping_container)

        # Hide vertical headers for accessibility
        self.mapping_table.verticalHeader().setVisible(False)
        # Set empty header labels to suppress row numbers
        self.mapping_table.setVerticalHeaderLabels([""] * self.mapping_table.rowCount())

        # Disable mouse tracking for accessibility
        self.mapping_table.setMouseTracking(False)
        self.mapping_table.viewport().setMouseTracking(False)
        self.mapping_table.setAttribute(Qt.WA_Hover, False)
        self.mapping_table.viewport().setAttribute(Qt.WA_Hover, False)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignLeft)
        button_layout.setSpacing(8)

        self.import_button = QPushButton("Import")
        self.import_button.setAccessibleName("Import button")
        self.import_button.setAccessibleDescription(
            "Import books from spreadsheet - Alt+I"
        )
        self.import_button.clicked.connect(self.import_books)
        self.import_button.setEnabled(True)

        self.export_button = QPushButton("Export Errors")
        self.export_button.setAccessibleName("Export Errors")
        self.export_button.setAccessibleDescription(
            "Export import errors to CSV spreadsheet - Alt+X"
        )
        self.export_button.clicked.connect(self.export_errors_csv)
        self.export_button.setEnabled(True)

        button_layout.addWidget(self.import_button)
        button_layout.addWidget(self.export_button)

        main_layout.addLayout(button_layout)

        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setAccessibleName("")
        self.status_bar.setAccessibleDescription("")
        main_layout.addWidget(self.status_bar)

        # Set initial status
        self.set_status("Ready - Select a spreadsheet file to begin")

        # Set up tab order for accessibility: mapping combos in table row order, then import/export buttons
        if self.field_mappings and hasattr(self, "mapping_table"):
            prev_widget = None
            for row in range(self.mapping_table.rowCount()):
                combo_container = self.mapping_table.cellWidget(row, 1)
                if combo_container is not None and combo_container.layout() is not None:
                    # The combo is the first widget in the container's layout
                    combo = None
                    for i in range(combo_container.layout().count()):
                        w = combo_container.layout().itemAt(i).widget()
                        if isinstance(w, QComboBox):
                            combo = w
                            break
                    if combo:
                        if prev_widget:
                            self.setTabOrder(prev_widget, combo)
                        prev_widget = combo
            # Last combo to import button
            if prev_widget:
                self.setTabOrder(prev_widget, self.import_button)
        else:
            self.setTabOrder(self.instructions_label, self.import_button)
        self.setTabOrder(self.import_button, self.export_button)

    def setup_mapping_table(self):
        """Setup the field mapping table rows with checkboxes in options column."""
        fields = [
            ("title", "* Title"),
            ("author", "* Author"),
            ("year", "Year"),
            ("plot", "Plot"),
            ("series", "Series"),
            ("series_no", "Series #"),
            ("genre", "Genre"),
            ("reader", "Reader"),
            ("read_date", "  Read Date"),
            ("time_hours", "Time"),
            ("tracks", "Files"),
        ]

        self.mapping_table.setRowCount(len(fields))
        self.field_mappings = {}

        for row, (field_name, field_label) in enumerate(fields):
            # Field label (no tab focus)
            label = QLabel(field_label)
            label.setAccessibleName(field_label)
            label.setFocusPolicy(Qt.NoFocus)  # Remove from tab order
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            # Use a slightly smaller font so labels take less horizontal space
            lbl_font = label.font()
            lbl_font.setPointSize(self.scaler.get_scaled_size(9))
            label.setFont(lbl_font)
            self.mapping_table.setCellWidget(row, 0, label)

            # Column selection combo
            combo = QComboBox()
            combo.setAccessibleName(f"{field_label}")
            combo.addItem("None")
            # Keep selector wide enough for labels like AA/AB and long fonts.
            min_width = self.scaler.get_scaled_size(90)
            max_width = self.scaler.get_scaled_size(130)
            combo.setMinimumWidth(min_width)
            combo.setMaximumWidth(max_width)

            # Connect mapping change signal
            combo.currentIndexChanged.connect(
                lambda idx, r=row, f=field_name: self.on_mapping_changed(r, f, idx)
            )

            # Install event filter for Alt+Down support
            combo.installEventFilter(self)

            # Wrap combo in a container aligned left+vcenter to prevent vertical floating on scale
            combo_container = QWidget()
            combo_container.setFocusPolicy(Qt.NoFocus)
            combo_layout = QHBoxLayout(combo_container)
            combo_layout.setContentsMargins(0, 0, 0, 0)
            combo_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            combo_layout.addWidget(combo)
            self.mapping_table.setCellWidget(row, 1, combo_container)
            self.field_mappings[field_name] = combo

            # Options column - removed (checkboxes moved to right panel)

        # Set empty header labels to suppress row numbers
        self.mapping_table.setVerticalHeaderLabels([""] * len(fields))

        # Ensure long field labels like "Read Date" are fully visible.
        self._update_mapping_field_column_width()

        # Set table height after rows are created to eliminate empty space
        row_height = self.scaler.get_scaled_size(25)
        table_height = row_height * len(fields) + 30  # Add header and minimal padding
        self.mapping_table.setMinimumHeight(table_height)
        self.mapping_table.setMaximumHeight(table_height)

    def _update_mapping_field_column_width(self):
        """Size the Field column based on the widest label widget."""
        if not hasattr(self, "mapping_table"):
            return

        widest = 0
        for row in range(self.mapping_table.rowCount()):
            widget = self.mapping_table.cellWidget(row, 0)
            if widget is not None:
                widest = max(widest, widget.sizeHint().width())

        padding = self.scaler.get_scaled_size(18)
        min_width = self.scaler.get_scaled_size(95)
        self.mapping_table.setColumnWidth(0, max(min_width, widest + padding))

    def on_load_books_toggled(self, checked: bool):
        """Handle Load Books checkbox toggle - mutually exclusive."""
        if checked:
            self.import_mode = "new"
            self.add_read_date_check.blockSignals(True)
            self.add_read_date_check.setChecked(False)
            self.add_read_date_check.blockSignals(False)
            self._apply_mode_field_availability()
            self.set_status("Mode changed to: Add Books From List")
        else:
            self.add_read_date_check.blockSignals(True)
            self.add_read_date_check.setChecked(True)
            self.add_read_date_check.blockSignals(False)
            self.import_mode = "read_date"
            self._apply_mode_field_availability()
            self.set_status("Mode changed to: Add Read Date")

    def on_add_read_date_toggled(self, checked: bool):
        """Handle Add Read Date checkbox toggle - mutually exclusive."""
        if checked:
            self.import_mode = "read_date"
            self.load_books_check.blockSignals(True)
            self.load_books_check.setChecked(False)
            self.load_books_check.blockSignals(False)
            self._apply_mode_field_availability()
            self.set_status("Mode changed to: Add Read Date")
        else:
            self.load_books_check.blockSignals(True)
            self.load_books_check.setChecked(True)
            self.load_books_check.blockSignals(False)
            self.import_mode = "new"
            self._apply_mode_field_availability()
            self.set_status("Mode changed to: Add Books From List")

    def _apply_mode_field_availability(self):
        """Enable/disable mapping combos based on current import mode."""
        if not hasattr(self, "field_mappings"):
            return

        if self.import_mode == "read_date":
            allowed_fields = {"title", "author", "year", "read_date"}
            for field, combo in self.field_mappings.items():
                combo.setEnabled(field in allowed_fields)
        else:
            for combo in self.field_mappings.values():
                combo.setEnabled(True)

    def on_file_has_header_toggled(self, checked: bool):
        """Handle File has header checkbox toggle."""
        if self.file_data is not None:
            self.reload_file_with_headers(checked)
        self.set_status(f"File has header: {'Yes' if checked else 'No'}")

    def on_show_shortcuts(self):
        """Show keyboard shortcuts help dialog (accessible, centralized)."""
        from src.accessibility.shortcut_helpers import (
            get_accessible_shortcuts_list,
            build_accessible_f1_popup_style,
        )

        shortcuts = [
            ("Alt+W", "Browse for file"),
            ("Alt+O", "Options section"),
            ("Alt+H", "Instructions"),
            ("Alt+T", "Title"),
            ("Alt+A", "Author"),
            ("Alt+Y", "Year"),
            ("Alt+P", "Plot"),
            ("Alt+S", "Series"),
            ("Alt+G", "Genre"),
            ("Alt+R", "Reader"),
            ("Alt+E", "Read Date"),
            ("Alt+M", "Time"),
            ("Alt+F", "Files"),
            ("Alt+I", "Import books"),
            ("Alt+X", "Export errors to CSV"),
            ("Alt+/", "Read status bar"),
            ("F1", "Show this help"),
            ("Escape", "Close window"),
        ]

        dlg = QDialog(self)
        dlg.setWindowTitle("Keyboard Shortcuts - Book List Import")
        dlg.setAccessibleName("Keyboard Shortcuts")
        dlg.setAccessibleDescription(
            "Dialog listing keyboard shortcuts for Book List Import. Use arrow keys to read line by line."
        )
        dlg.resize(560, 420)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        table = QTableWidget()
        table.setAccessibleName("Shortcuts list")
        table.setAccessibleDescription(
            "Read-only list of keyboard shortcuts for Book List Import."
        )
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels([""])

        table.setRowCount(len(shortcuts))
        table.setVerticalHeaderLabels([""] * len(shortcuts))
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setTabKeyNavigation(False)
        table.setAlternatingRowColors(False)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        table.setShowGrid(False)

        # Disable mouse tracking for accessibility
        table.setMouseTracking(False)
        table.viewport().setMouseTracking(False)
        table.setAttribute(Qt.WA_Hover, False)
        table.viewport().setAttribute(Qt.WA_Hover, False)

        # Centralize Alt+/ visibility and order for screen readers
        shortcuts = get_accessible_shortcuts_list(shortcuts)
        table.setStyleSheet(build_accessible_f1_popup_style())

        for row, (key, desc) in enumerate(shortcuts):
            item = QTableWidgetItem(f"{desc} - {key}")
            item.setData(Qt.AccessibleTextRole, f"{desc}: {key}")
            table.setItem(row, 0, item)

        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        font = table.font()
        font.setPointSize(self.scaler.get_scaled_size(11))
        table.setFont(font)

        layout.addWidget(table)
        dlg.setLayout(layout)

        QTimer.singleShot(0, lambda: table.setFocus(Qt.TabFocusReason))
        dlg.exec()

    def on_read_status_bar(self):
        """Read status bar message for screen readers (matches main window pattern)."""
        status_text = self.status_bar.currentMessage() or self._default_status_message
        if QAccessible.isActive():
            announce_status_message(self.status_bar, status_text, move_focus=True)
        else:
            from src.accessibility.icon_helper import get_app_icon

            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Information,
                title="Status Bar",
                text=f"No screen reader active.\n\nStatus: {status_text}",
                window_icon=get_app_icon(),
            )

    def browse_file(self):
        """Browse for spreadsheet file."""
        file_filter = "Spreadsheet Files (*.xlsx *.xls *.ods *.csv);;Excel/OpenDocument Files (*.xlsx *.xls *.ods);;CSV Files (*.csv);;All Files (*.*)"

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Spreadsheet File", "", file_filter
        )

        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path: str):
        """Load and parse the selected file."""
        try:
            self.set_status("Loading file...")
            has_headers = self.file_has_header_check.isChecked()

            # Load file based on extension
            if file_path.lower().endswith(".csv"):
                self.file_data = self._read_csv_with_fallback(
                    file_path, has_headers=has_headers
                )
            elif file_path.lower().endswith(".ods"):
                self.file_data = pd.read_excel(
                    file_path,
                    engine="odf",
                    header=0 if has_headers else None,
                )
            else:
                # Excel files
                self.file_data = pd.read_excel(
                    file_path,
                    header=0 if has_headers else None,
                )

            self.selected_file = file_path
            self.file_edit.setText(file_path)
            self.column_count = len(self.file_data.columns)

            # Update column combos
            self.update_column_combos()

            # Move focus to first import type checkbox
            self.load_books_check.setFocus()

            self.set_status(
                f"Loaded {len(self.file_data)} rows with {self.column_count} columns"
            )

        except ImportError:
            if file_path.lower().endswith(".ods"):
                exec_styled_message_box(
                    self,
                    self.scaler.get_scaled_size(20),
                    icon=QMessageBox.Critical,
                    title="Missing Dependency",
                    text="OpenDocument (.ods) support requires odfpy.\n\nInstall with:\npip install odfpy",
                    buttons=QMessageBox.Ok,
                    default_button=QMessageBox.Ok,
                )
                self.set_status("Missing dependency: odfpy")
                return
            raise
        except Exception as e:
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Critical,
                title="File Error",
                text=f"Could not load file:\n{str(e)}",
                buttons=QMessageBox.Ok,
                default_button=QMessageBox.Ok,
            )
            self.set_status("File loading failed")

    def _read_csv_with_fallback(self, file_path: str, has_headers: bool = True):
        """Read CSV with fallback encodings used by legacy spreadsheet exports."""
        encodings = ["utf-8-sig", "utf-8", "cp1252", "latin1"]
        last_error = None
        header_value = 0 if has_headers else None

        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding, header=header_value)
                return df
            except UnicodeDecodeError as e:
                last_error = e

        if last_error is not None:
            raise last_error
        return pd.read_csv(file_path, header=header_value)

    def _excel_column_label(self, index: int) -> str:
        """Convert zero-based index to Excel-style labels (A..Z, AA..ZZ...)."""
        index += 1
        label = ""
        while index > 0:
            index, rem = divmod(index - 1, 26)
            label = chr(65 + rem) + label
        return label

    def _parse_time_value(self, value) -> Optional[Tuple[int, int]]:
        """Parse duration values into (hours, minutes)."""
        if value is None or not pd.notna(value):
            return None

        text = str(value).strip()
        if not text or text.lower() == "nan":
            return None

        if isinstance(value, (int, float)):
            numeric = float(value)
            if numeric < 0:
                return None
            total_minutes = (
                int(round(numeric * 24 * 60))
                if 0 < numeric < 1
                else int(round(numeric * 60))
            )
            return total_minutes // 60, total_minutes % 60

        hh_mm = re.fullmatch(r"(\d{1,3}):(\d{1,2})(?::(\d{1,2}))?", text)
        if hh_mm:
            hours = int(hh_mm.group(1))
            minutes = int(hh_mm.group(2))
            seconds = int(hh_mm.group(3) or 0)
            total_minutes = hours * 60 + minutes + (1 if seconds >= 30 else 0)
            return total_minutes // 60, total_minutes % 60

        h_match = re.search(r"(\d+)\s*h", text.lower())
        m_match = re.search(r"(\d+)\s*m", text.lower())
        if h_match or m_match:
            hours = int(h_match.group(1)) if h_match else 0
            minutes = int(m_match.group(1)) if m_match else 0
            total_minutes = hours * 60 + minutes
            return total_minutes // 60, total_minutes % 60

        try:
            numeric = float(text.replace(",", ""))
        except ValueError:
            return None

        if numeric < 0:
            return None
        total_minutes = (
            int(round(numeric * 24 * 60))
            if 0 < numeric < 1
            else int(round(numeric * 60))
        )
        return total_minutes // 60, total_minutes % 60

    def _parse_read_date_value(self, value):
        """Parse spreadsheet read-date values into a date object.

        Supports common list formats such as:
        - YYYY-MM-DD / YYYY/MM/DD
        - DD-MM-YYYY / DD/MM/YYYY / DD.MM.YYYY
        - DD-MM-YY / DD/MM/YY / DD.MM.YY
        - Month-name forms like 04-Apr-26, 4 April 2026
        """
        from datetime import date as date_type

        if value is None or not pd.notna(value):
            return None

        if isinstance(value, (datetime, date_type)):
            return value.date() if isinstance(value, datetime) else value

        text = str(value).strip()
        if not text or text.lower() == "nan":
            return None

        # Strip time component if present (e.g., "2026-04-04 00:00:00").
        text = text.split(" ")[0].strip()

        formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%d.%m.%Y",
            "%m/%d/%Y",
            "%d-%m-%y",
            "%d/%m/%y",
            "%d.%m.%y",
            "%m/%d/%y",
            "%d-%b-%y",
            "%d-%b-%Y",
            "%d %b %Y",
            "%d %B %Y",
            "%b %d %Y",
            "%B %d %Y",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(text, fmt).date()
            except ValueError:
                continue

        return None

    def update_column_combos(self):
        """Update column combos with Excel-style labels for all detected columns."""
        column_letters = [
            self._excel_column_label(i) for i in range(max(0, self.column_count))
        ]

        for combo in self.field_mappings.values():
            combo.clear()
            combo.addItem("None")
            combo.addItems(column_letters)
            # Set combo width with scaling for proper text display
            min_width = self.scaler.get_scaled_size(90)
            max_width = self.scaler.get_scaled_size(130)
            combo.setMinimumWidth(min_width)
            combo.setMaximumWidth(max_width)

        # Set default mappings: Title=A, Author=B (common spreadsheet format)
        self.set_default_mappings()

    def set_default_mappings(self):
        """Set default column mappings - Title=A, Author=B."""
        default_mappings = {
            "title": 0,  # Column A
            "author": 1,  # Column B
        }

        for field, column_index in default_mappings.items():
            if field in self.field_mappings and self.column_count > column_index:
                # Set to column letter (add 1 for "None" option)
                self.field_mappings[field].setCurrentIndex(column_index + 1)

    def on_headers_toggled(self, checked: bool):
        """Handle headers checkbox toggle."""
        if self.file_data is not None:
            # Reload file with new header setting
            self.reload_file_with_headers(checked)

    def reload_file_with_headers(self, has_headers: bool):
        """Reload the current file with updated header setting."""
        if not self.selected_file:
            return

        try:
            file_ext = os.path.splitext(self.selected_file)[1].lower()

            if file_ext == ".csv":
                # Load CSV with or without headers
                self.file_data = self._read_csv_with_fallback(
                    self.selected_file, has_headers=has_headers
                )
            elif file_ext == ".ods":
                self.file_data = pd.read_excel(
                    self.selected_file,
                    engine="odf",
                    header=0 if has_headers else None,
                )
            else:
                # Load Excel files with or without headers
                if has_headers:
                    self.file_data = pd.read_excel(self.selected_file)
                else:
                    self.file_data = pd.read_excel(self.selected_file, header=None)

            self.column_count = len(self.file_data.columns)
            self.update_column_combos()

            header_status = "with headers" if has_headers else "without headers"
            self.set_status(
                f"Reloaded file {header_status}: {len(self.file_data)} rows, {self.column_count} columns"
            )

        except Exception as e:
            self.set_status(f"Error reloading file: {str(e)}")

    def on_mapping_changed(self, row: int, field: str, column_index: int):
        """Handle field mapping change."""
        # Validation could be added here
        pass

    def get_field_mapping(self) -> Dict[str, Optional[int]]:
        """Get the current field mapping from column letters to indices."""
        mapping = {}
        for field, combo in self.field_mappings.items():
            column_index = combo.currentIndex() - 1  # Subtract 1 for "None" option
            if column_index >= 0:
                # Convert column letter to index (A=0, B=1, ..., Z=25)
                mapping[field] = column_index
            else:
                mapping[field] = None
        return mapping

    def validate_mapping(self) -> Tuple[bool, str, Optional[str]]:
        """Validate the field mapping."""
        mapping = self.get_field_mapping()

        # Check required fields
        if mapping["title"] is None:
            return False, "Title field is required", "title"
        if mapping["author"] is None:
            return False, "Author field is required", "author"

        # In Add Read Date mode, read date mapping is required.
        if self.import_mode == "read_date" and mapping["read_date"] is None:
            return (
                False,
                "Read Date field is required when Add Read Date from List is selected",
                "read_date",
            )

        # Check if any fields are mapped
        mapped_fields = [field for field, col in mapping.items() if col is not None]
        if len(mapped_fields) < 2:  # At least title + author
            return False, "At least Title and Author must be mapped", None

        return True, "Mapping is valid", None

    def generate_preview_text(self, mapping: Dict[str, Optional[int]]) -> str:
        """Generate preview text for the import."""
        file_name = os.path.basename(self.selected_file) if self.selected_file else ""
        lines = [f"Rows: {len(self.file_data)}"]
        lines.append(
            f"Mode: {'Import New Books' if self.import_mode == 'new' else 'Update Read Dates'}"
        )
        lines.append("")
        lines.append("Field Mapping:")

        field_labels = {
            "title": "Title",
            "author": "Author",
            "year": "Year",
            "plot": "Plot",
            "series": "Series",
            "series_no": "Series #",
            "genre": "Genre",
            "reader": "Reader",
            "read_date": "Read Date",
            "time_hours": "Time",
            "tracks": "Files",
        }

        for field, col_index in mapping.items():
            if col_index is not None:
                column_name = self.file_data.columns[col_index]
                lines.append(
                    f"  {field_labels[field]} → Column {col_index + 1} ({column_name})"
                )

        lines.append("")
        lines.append("Ready to import?")
        lines.append(f"File: {file_name}")

        return "\n".join(lines)

    def import_books(self):
        """Import books from the loaded file with preview confirmation."""
        if not self.file_data is not None:
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Warning,
                title="File Required",
                text="Select a spreadsheet file before importing.",
                buttons=QMessageBox.Ok,
                default_button=QMessageBox.Ok,
            )
            self.set_status("No file loaded. Select a spreadsheet file first.")
            self.browse_button.setFocus(Qt.TabFocusReason)
            return

        # Validate mapping
        is_valid, message, focus_field = self.validate_mapping()
        if not is_valid:
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Warning,
                title="Mapping Error",
                text=message,
                buttons=QMessageBox.Ok,
                default_button=QMessageBox.Ok,
            )
            if focus_field and focus_field in self.field_mappings:
                focus_combo = self.field_mappings[focus_field]
                focus_combo.setFocus(Qt.TabFocusReason)
                focus_combo.showPopup()
            return

        # Show preview info in confirm dialog with accessible properties
        mapping = self.get_field_mapping()
        preview_text = self.generate_preview_text(mapping)

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("Confirm Import")
        msg.setText(preview_text)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        msg.setAccessibleName("Confirm Import")
        msg.setAccessibleDescription(preview_text)
        msg.setStyleSheet(
            build_accessible_message_box_style(self.scaler.get_scaled_size(20))
        )
        reply = msg.exec()

        if reply != QMessageBox.Yes:
            self.set_status("Import cancelled")
            return

        # Perform import
        try:
            self.set_status("Importing books...")

            if self.import_mode == "new":
                success_count, error_count = self.import_new_books()
            else:
                success_count, error_count = self.update_read_dates()

            # Show results
            if self.import_mode == "new":
                result_text = f"{success_count} books added to Book List collection"
                status_text = f"{success_count} books added to Book List collection, {error_count} errors"
            else:
                result_text = f"{success_count} read dates added to books"
                status_text = (
                    f"{success_count} read dates added to books, {error_count} errors"
                )
            if error_count > 0:
                result_text += f"\n{error_count} books had errors"
                result_text += (
                    "\nUse Export Errors (Alt+X) to save error details to CSV"
                )

            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Information,
                title="Import Complete",
                text=result_text,
                buttons=QMessageBox.Ok,
                default_button=QMessageBox.Ok,
            )

            self.set_status(status_text)
            # Set focus to file text box after import completes
            self.file_edit.setFocus(Qt.TabFocusReason)

        except Exception as e:
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Critical,
                title="Import Error",
                text=f"Import failed:\n{str(e)}",
                buttons=QMessageBox.Ok,
                default_button=QMessageBox.Ok,
            )
            self.set_status("Import failed")

    def import_new_books(self) -> Tuple[int, int]:
        """Import new books from the spreadsheet."""
        from src.database.models import Book

        mapping = self.get_field_mapping()
        success_count = 0
        error_count = 0
        self.import_errors = []  # Reset errors

        # Ensure "Book List" collection exists
        book_list_collection = self.get_or_create_book_list_collection()

        for index, row in self.file_data.iterrows():
            try:
                # Extract required fields
                title = str(row.iloc[mapping["title"]]).strip()
                author = str(row.iloc[mapping["author"]]).strip()

                if not title or not author or title == "nan" or author == "nan":
                    self.import_errors.append(
                        {
                            "row": index + 1,
                            "title": title,
                            "author": author,
                            "reason": "Missing title or author",
                        }
                    )
                    error_count += 1
                    continue

                # Series number logic
                series_no = None
                if "series_no" in mapping and mapping["series_no"] is not None:
                    val = row.iloc[mapping["series_no"]]
                    if (
                        pd.notna(val)
                        and str(val).strip()
                        and str(val).strip().lower() != "nan"
                    ):
                        series_no = str(val).strip()

                # Series logic
                series = None
                if mapping.get("series") is not None:
                    val = row.iloc[mapping["series"]]
                    if (
                        pd.notna(val)
                        and str(val).strip()
                        and str(val).strip().lower() != "nan"
                    ):
                        series = str(val).strip()

                # Append series number to title if both present
                title_for_save = title
                if series and series_no:
                    # Only append if not already present
                    if not re.search(
                        rf"\\(\\s*{re.escape(series)}\\s*#?\\s*{re.escape(series_no)}\\s*\\)",
                        title,
                        re.IGNORECASE,
                    ):
                        title_for_save = f"{title} ({series} #{series_no})"

                # Normalize title and author for matching (with appended series number)
                norm_title = self._normalize_title_for_match(title_for_save)
                norm_author = self._normalize_author_for_match(author)
                # Check for duplicates using normalized title and normalized author
                dup_row = self.db.fetch_one(
                    "SELECT b.book_id FROM books b "
                    "JOIN authors a ON b.author_id = a.author_id "
                    "WHERE lower(b.title) = ? AND lower(trim(a.name)) = ?",
                    (norm_title, norm_author),
                )
                if dup_row:
                    self.import_errors.append(
                        {
                            "row": index + 1,
                            "title": title_for_save,
                            "author": author,
                            "reason": "Duplicate - book already exists",
                        }
                    )
                    error_count += 1
                    continue

                # Get or create author
                author_id = self.author_queries.get_or_create(author, commit=False)

                # Build Book object
                book = Book(
                    title=title_for_save,
                    author_id=author_id,
                    collection_id=book_list_collection.collection_id,
                )

                # Add optional fields
                if mapping.get("year") is not None:
                    year = row.iloc[mapping["year"]]
                    if pd.notna(year):
                        try:
                            book.year = int(year)
                        except (ValueError, TypeError):
                            pass

                if mapping.get("plot") is not None:
                    plot = row.iloc[mapping["plot"]]
                    if pd.notna(plot) and str(plot) != "nan":
                        book.comments = str(plot)

                if series:
                    book.series_id = self.series_queries.get_or_create(
                        series, commit=False
                    )

                if mapping.get("genre") is not None:
                    genre = row.iloc[mapping["genre"]]
                    if pd.notna(genre) and str(genre) != "nan":
                        book.genre_id = self.genre_queries.get_or_create(
                            str(genre), commit=False
                        )

                if mapping.get("reader") is not None:
                    reader = row.iloc[mapping["reader"]]
                    if pd.notna(reader) and str(reader) != "nan":
                        book.reader = str(reader)

                if mapping.get("read_date") is not None:
                    read_date = row.iloc[mapping["read_date"]]
                    if pd.notna(read_date) and str(read_date) != "nan":
                        parsed_read_date = self._parse_read_date_value(read_date)
                        if parsed_read_date is not None:
                            book.read_date = parsed_read_date

                if mapping.get("time_hours") is not None:
                    time_value = row.iloc[mapping["time_hours"]]
                    parsed_time = self._parse_time_value(time_value)
                    if parsed_time is not None:
                        book.time_hours, book.time_minutes = parsed_time

                if mapping.get("tracks") is not None:
                    tracks = row.iloc[mapping["tracks"]]
                    if pd.notna(tracks) and str(tracks) != "nan":
                        try:
                            book.tracks = int(tracks)
                        except (ValueError, TypeError):
                            pass

                # Insert book
                self.book_queries.insert(book, commit=False)
                success_count += 1

            except Exception as e:
                self.import_errors.append(
                    {
                        "row": index + 1,
                        "title": title,
                        "author": author,
                        "reason": str(e),
                    }
                )
                error_count += 1
                continue

        # Commit all changes at once
        self.db.connect().commit()
        return success_count, error_count

    def update_read_dates(self) -> Tuple[int, int]:
        """Update read dates for existing books."""
        mapping = self.get_field_mapping()
        success_count = 0
        error_count = 0
        self.import_errors = []  # Reset errors

        for index, row in self.file_data.iterrows():
            try:
                # Extract required fields
                title = str(row.iloc[mapping["title"]]).strip()
                author = str(row.iloc[mapping["author"]]).strip()

                if not title or not author or title == "nan" or author == "nan":
                    self.import_errors.append(
                        {
                            "row": index + 1,
                            "title": title,
                            "author": author,
                            "reason": "Missing title or author",
                        }
                    )
                    error_count += 1
                    continue

                # Series number logic
                series_no = None
                if "series_no" in mapping and mapping["series_no"] is not None:
                    val = row.iloc[mapping["series_no"]]
                    if (
                        pd.notna(val)
                        and str(val).strip()
                        and str(val).strip().lower() != "nan"
                    ):
                        series_no = str(val).strip()

                # Series logic
                series = None
                if mapping.get("series") is not None:
                    val = row.iloc[mapping["series"]]
                    if (
                        pd.notna(val)
                        and str(val).strip()
                        and str(val).strip().lower() != "nan"
                    ):
                        series = str(val).strip()

                # Append series number to title if both present
                title_for_match = title
                if series and series_no:
                    if not re.search(
                        rf"\\(\\s*{re.escape(series)}\\s*#?\\s*{re.escape(series_no)}\\s*\\)",
                        title,
                        re.IGNORECASE,
                    ):
                        title_for_match = f"{title} ({series} #{series_no})"

                # Normalize title for matching (with appended series number)
                norm_title = self._normalize_title_for_match(title_for_match)
                # Find existing book by normalized title + author using SQL
                existing_row = self.db.fetch_one(
                    "SELECT b.book_id FROM books b "
                    "JOIN authors a ON b.author_id = a.author_id "
                    "WHERE lower(b.title) = ? AND a.name = ?",
                    (norm_title, author),
                )
                if not existing_row:
                    self.import_errors.append(
                        {
                            "row": index + 1,
                            "title": title_for_match,
                            "author": author,
                            "reason": "Book not found in database",
                        }
                    )
                    error_count += 1
                    continue

                # Get the full book object
                existing_book = self.book_queries.get_by_id(existing_row["book_id"])
                if not existing_book:
                    self.import_errors.append(
                        {
                            "row": index + 1,
                            "title": title_for_match,
                            "author": author,
                            "reason": "Could not load book record",
                        }
                    )
                    error_count += 1
                    continue

                # Update read date if provided
                if mapping.get("read_date") is not None:
                    read_date = row.iloc[mapping["read_date"]]
                    if pd.notna(read_date) and str(read_date) != "nan":
                        parsed_read_date = self._parse_read_date_value(read_date)
                        if parsed_read_date is not None:
                            existing_book.read_date = parsed_read_date
                            self.book_queries.update(existing_book)
                            success_count += 1
                        else:
                            self.import_errors.append(
                                {
                                    "row": index + 1,
                                    "title": title_for_match,
                                    "author": author,
                                    "reason": "Invalid date format. Supported examples: YYYY-MM-DD, DD-MM-YY, DD/MM/YYYY",
                                }
                            )
                            error_count += 1
                    else:
                        self.import_errors.append(
                            {
                                "row": index + 1,
                                "title": title_for_match,
                                "author": author,
                                "reason": "Read date is empty",
                            }
                        )
                        error_count += 1
                else:
                    self.import_errors.append(
                        {
                            "row": index + 1,
                            "title": title_for_match,
                            "author": author,
                            "reason": "Read Date column not mapped",
                        }
                    )
                    error_count += 1

            except Exception as e:
                self.import_errors.append(
                    {
                        "row": index + 1,
                        "title": title,
                        "author": author,
                        "reason": str(e),
                    }
                )
                error_count += 1
                continue

        return success_count, error_count

    def export_errors_csv(self):
        """Export import errors to CSV spreadsheet."""
        import csv
        import os
        from datetime import datetime
        from PySide6.QtWidgets import QFileDialog

        if not self.import_errors:
            self.set_status("No errors to export")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"Import_Book_list_errors_{timestamp}.csv"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Import Errors",
            default_name,
            "CSV Files (*.csv);;All Files (*.*)",
        )
        if not file_path:
            self.set_status("Export cancelled")
            self._ensure_read_status_bar_shortcut()
            return

        if not file_path.lower().endswith(".csv"):
            file_path += ".csv"

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Row", "Title", "Author", "Error"])
                for err in self.import_errors:
                    writer.writerow(
                        [err["row"], err["title"], err["author"], err["reason"]]
                    )
        except Exception as exc:
            self.set_status(f"Export failed: {str(exc)}", announce=True)
            self._ensure_read_status_bar_shortcut()
            return

        self.set_status(
            f"Exported {len(self.import_errors)} error(s) to CSV: {os.path.basename(file_path)}",
            announce=True,
        )
        from src.accessibility.icon_helper import get_app_icon
        from src.accessibility.style_helpers import exec_styled_message_box

        exec_styled_message_box(
            self,
            self.scaler.get_scaled_size(20),
            icon=QMessageBox.Information,
            title="Export Complete",
            text=f"Exported to:\n{file_path}",
            window_icon=get_app_icon(),
        )
        self._ensure_read_status_bar_shortcut()

    def _ensure_read_status_bar_shortcut(self):
        """Ensure Alt+/ shortcut for reading status bar is always active."""
        # Defensive: If shortcut was deleted or lost, re-create it
        if (
            not hasattr(self, "read_status_bar_shortcut")
            or self.read_status_bar_shortcut is None
        ):
            self.read_status_bar_shortcut = QShortcut(QKeySequence("Alt+/"), self)
            self.read_status_bar_shortcut.activated.connect(self.on_read_status_bar)
        else:
            # Sometimes after modal dialogs, shortcut can be disabled; re-enable if needed
            self.read_status_bar_shortcut.setEnabled(True)

    def get_or_create_book_list_collection(self):
        """Get or create the 'Book List' collection."""
        from src.database.models import Collection

        # Search existing collections by name
        all_collections = self.collection_queries.get_all(active_only=False)
        for col in all_collections:
            if col.name == "Book List":
                return col

        # Create new collection if not found
        new_collection = Collection(name="Book List", active=True)
        new_id = self.collection_queries.insert(new_collection)
        new_collection.collection_id = new_id
        return new_collection

    def set_status(self, message: str, announce: bool = False):
        """Set status message and optionally announce to screen reader."""
        self._default_status_message = message
        announce_status_message(self.status_bar, message, move_focus=announce)

    def apply_theme(self):
        """Apply the current theme."""
        self.theme_manager._apply_theme()
        self.setStyleSheet(
            "QGroupBox {"
            "  border: 1px solid palette(mid);"
            "  border-radius: 3px;"
            "  margin-top: 12px;"
            "  padding-top: 8px;"
            "}"
            "QGroupBox::title {"
            "  subcontrol-origin: margin;"
            "  subcontrol-position: top left;"
            "  left: 8px;"
            "  padding: 0 4px;"
            "  background-color: palette(window);"
            "}"
        )
