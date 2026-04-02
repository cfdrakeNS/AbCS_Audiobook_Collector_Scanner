"""Book List Import Window - Import books from spreadsheet files."""

from __future__ import annotations

import csv
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
        def read_csv(filepath):
            raise ImportError("pandas not available - install with: pip install pandas")

        @staticmethod
        def read_excel(filepath):
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
    QRadioButton,
    QButtonGroup,
    QLineEdit,
    QStatusBar,
    QMessageBox,
    QFileDialog,
    QHeaderView,
    QAbstractItemView,
    QCheckBox,
    QTextEdit,
    QWidget,
)
from PySide6.QtGui import QShortcut, QKeySequence, QAccessible, QAction

from src.database import BookQueries, CollectionQueries, ReadingQueries
from src.accessibility.scaling import UIScaler
from src.accessibility.accessible_events import announce_status_message
from src.accessibility.style_helpers import exec_styled_message_box
from src.accessibility.theme_manager import ThemeManager
from src.accessibility.shortcuts import get_shortcut_manager, ShortcutContext
from src.accessibility.key_filters import is_unmapped_alt_letter


class BookListImportWindow(QDialog):
    """Book List Import window with full accessibility support."""

    # Alt+Key filtering for accessibility
    ALLOWED_ALT_LETTERS = "W M T A Y P S G R I H B C V N U /"

    def __init__(self, db, scaler: UIScaler, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self.db = db
        self.scaler = scaler
        self.theme_manager = theme_manager
        self.book_queries = BookQueries(db)
        self.collection_queries = CollectionQueries(db)
        self.reading_queries = ReadingQueries(db)

        # Check for pandas availability
        if not PANDAS_AVAILABLE:
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Critical,
                title="Missing Dependencies",
                text="Book List Import requires pandas and openpyxl.\n\nPlease install with:\npip install pandas openpyxl",
                buttons=QMessageBox.Ok,
                default_button=QMessageBox.Ok,
            )
            self.reject()
            return

        # State
        self.selected_file = None
        self.file_data = None
        self.column_count = 0
        self.import_mode = "new"  # "new" or "read_date"
        self._default_status_message = "Ready"

        # Window setup
        self.setWindowTitle("Book List Import")
        self.setAccessibleName("Book List Import Window")
        self.setAccessibleDescription(
            "Import books from spreadsheet files with field mapping"
        )
        self.setMinimumSize(900, 700)
        self.resize(1000, 800)

        self.setup_ui()
        self.apply_theme()

        # Focus on file selector initially
        self.file_edit.setFocus()

        # Apply button styling to match other windows
        self.apply_button_styling()

        # Install event filters for combo box anti-noise pattern
        self.install_combo_filters()

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
        file_label.setAccessibleName("File label")
        self.file_edit = QLineEdit()
        self.file_edit.setReadOnly(True)
        self.file_edit.setAccessibleName("Selected file")
        self.file_edit.setAccessibleDescription("Path to selected spreadsheet file")
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

        # Options and controls above mapping table
        options_layout = QHBoxLayout()

        # Instructions only
        instructions_group = QGroupBox("Instructions")
        instructions_group.setAccessibleName("Instructions group")
        instructions_layout = QVBoxLayout(instructions_group)

        self.instructions_edit = QTextEdit()
        self.instructions_edit.setReadOnly(True)
        self.instructions_edit.setAccessibleName("Usage instructions")
        self.instructions_edit.setAccessibleDescription(
            "Step-by-step instructions for using the book list import"
        )
        self.instructions_edit.setFocusPolicy(Qt.StrongFocus)  # Allow tab focus
        self.instructions_edit.setText(
            "1. Select an Excel (.xlsx, .xls) or CSV file using the Browse button\n"
            "2. Map spreadsheet columns to book fields using the dropdown combos\n"
            "3. Use checkboxes in Options column for import settings\n"
            "4. Title and Author fields are required for import\n"
            "5. Click Preview to verify your field mapping\n"
            "6. Click Import to process the file"
        )
        self.instructions_edit.setStyleSheet(
            "QTextEdit { background-color: palette(base); border: 1px solid palette(mid); padding: 5px; }"
        )

        # Set instructions height with scaling
        min_height = self.scaler.get_scaled_size(80)
        max_height = self.scaler.get_scaled_size(120)
        self.instructions_edit.setMinimumHeight(min_height)
        self.instructions_edit.setMaximumHeight(max_height)

        instructions_layout.addWidget(self.instructions_edit)
        instructions_group.setLayout(instructions_layout)
        options_layout.addWidget(instructions_group)

        main_layout.addLayout(options_layout)

        # Field mapping table with instructions and checkboxes on right side
        mapping_container = QWidget()
        mapping_layout = QHBoxLayout(mapping_container)
        mapping_layout.setContentsMargins(0, 0, 0, 0)
        mapping_layout.setSpacing(12)
        mapping_layout.setAlignment(Qt.AlignTop)  # Align all panels to top

        # Left side - Field mapping table (takes more space)
        mapping_group = QGroupBox("Field Mapping")
        mapping_group.setAccessibleName("Field mapping group")
        mapping_table_layout = QVBoxLayout(mapping_group)
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

        # Set column widths with scaling
        field_width = self.scaler.get_scaled_size(150)
        combo_width = self.scaler.get_scaled_size(120)
        self.mapping_table.setColumnWidth(0, field_width)  # Field name
        self.mapping_table.setColumnWidth(1, combo_width)  # Column selector

        # Add padding to prevent text cutoff
        self.mapping_table.setStyleSheet(
            """
            QTableWidget {
                gridline-color: palette(mid);
            }
            QTableWidget::item {
                padding: 5px;
            }
        """
        )

        # Disable tab navigation on table - we'll handle combo navigation directly
        self.mapping_table.setTabKeyNavigation(False)
        self.mapping_table.setFocusPolicy(Qt.NoFocus)  # Table itself doesn't get focus

        mapping_table_layout.addWidget(self.mapping_table)
        mapping_group.setLayout(mapping_table_layout)

        # Add table to layout with stretch factor (takes more space)
        mapping_layout.addWidget(mapping_group, 3)  # Stretch factor 3

        # Right side - Options checkboxes (takes less space)
        options_group = QGroupBox("Options")
        options_group.setAccessibleName("Options group")
        options_layout = QVBoxLayout(options_group)
        options_layout.setAlignment(Qt.AlignTop)  # Align to top
        options_group.setMaximumWidth(250)  # Limit width of options panel

        # Load Books checkbox
        self.load_books_check = QCheckBox("Load Books")
        self.load_books_check.setAccessibleName("Load Books")
        self.load_books_check.setChecked(True)
        self.load_books_check.toggled.connect(self.on_load_books_toggled)
        options_layout.addWidget(self.load_books_check)

        # Add Read Date checkbox
        self.add_read_date_check = QCheckBox("Add Read Date")
        self.add_read_date_check.setAccessibleName("Add Read Date")
        self.add_read_date_check.toggled.connect(self.on_add_read_date_toggled)
        options_layout.addWidget(self.add_read_date_check)

        # File has header checkbox
        self.file_has_header_check = QCheckBox("Does the file have a header row?")
        self.file_has_header_check.setAccessibleName("Does the file have a header row")
        self.file_has_header_check.setChecked(True)
        self.file_has_header_check.toggled.connect(self.on_file_has_header_toggled)
        options_layout.addWidget(self.file_has_header_check)

        options_layout.addStretch()
        options_group.setLayout(options_layout)

        # Add options to layout with smaller stretch factor
        mapping_layout.addWidget(options_group, 1)  # Stretch factor 1

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
        button_layout.addStretch()

        self.preview_button = QPushButton("Preview")
        self.preview_button.setAccessibleName("Preview button")
        self.preview_button.setAccessibleDescription(
            "Preview import mapping and data - Alt+C"
        )
        self.preview_button.clicked.connect(self.preview_import)
        self.preview_button.setEnabled(False)

        self.import_button = QPushButton("Import")
        self.import_button.setAccessibleName("Import button")
        self.import_button.setAccessibleDescription(
            "Import books from spreadsheet - Alt+V"
        )
        self.import_button.clicked.connect(self.import_books)
        self.import_button.setEnabled(False)

        button_layout.addWidget(self.preview_button)
        button_layout.addWidget(self.import_button)

        main_layout.addLayout(button_layout)

        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setAccessibleName("Status bar")
        main_layout.addWidget(self.status_bar)

        # Set initial status
        self.set_status("Ready - Select a spreadsheet file to begin")

        # Set up tab order for accessibility
        if self.field_mappings:
            prev_combo = None
            for field in [
                "title",
                "author",
                "year",
                "plot",
                "series",
                "genre",
                "reader",
                "read_date",
                "time_hours",
                "tracks",
            ]:
                if self.field_mappings.get(field):
                    if prev_combo:
                        self.setTabOrder(prev_combo, self.field_mappings[field])
                    prev_combo = self.field_mappings[field]
            # Last combo to preview button
            if prev_combo:
                self.setTabOrder(prev_combo, self.preview_button)
        else:
            self.setTabOrder(self.instructions_edit, self.preview_button)
        self.setTabOrder(self.preview_button, self.import_button)

    def setup_mapping_table(self):
        """Setup the field mapping table rows with checkboxes in options column."""
        fields = [
            ("title", "Title *"),
            ("author", "Author *"),
            ("year", "Year"),
            ("plot", "Plot"),
            ("series", "Series"),
            ("genre", "Genre"),
            ("reader", "Reader"),
            ("read_date", "Read Date"),
            ("time_hours", "Time"),
            ("tracks", "Tracks"),
        ]

        self.mapping_table.setRowCount(len(fields))
        self.field_mappings = {}

        for row, (field_name, field_label) in enumerate(fields):
            # Field label (no tab focus)
            label = QLabel(field_label)
            label.setAccessibleName(field_label)
            label.setFocusPolicy(Qt.NoFocus)  # Remove from tab order
            self.mapping_table.setCellWidget(row, 0, label)

            # Column selection combo
            combo = QComboBox()
            combo.setAccessibleName(f"{field_label}")
            combo.addItem("None")
            # Set combo width with scaling for proper text display
            min_width = self.scaler.get_scaled_size(80)
            max_width = self.scaler.get_scaled_size(150)
            combo.setMinimumWidth(min_width)
            combo.setMaximumWidth(max_width)

            # Connect mapping change signal
            combo.currentIndexChanged.connect(
                lambda idx, r=row, f=field_name: self.on_mapping_changed(r, f, idx)
            )

            # Install event filter for Alt+Down support
            combo.installEventFilter(self)

            self.mapping_table.setCellWidget(row, 1, combo)
            self.field_mappings[field_name] = combo

            # Options column - removed (checkboxes moved to right panel)

        # Set empty header labels to suppress row numbers
        self.mapping_table.setVerticalHeaderLabels([""] * len(fields))

        # Local shortcuts
        self.help_shortcut = QShortcut(QKeySequence("F1"), self)
        self.help_shortcut.activated.connect(self.on_show_shortcuts)

        self.status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.status_shortcut.activated.connect(self.on_read_status_bar)

        # Centralized shortcuts using ShortcutManager (AbCS standard)
        from src.accessibility.shortcuts import get_shortcut_manager, ShortcutContext

        mgr = get_shortcut_manager()
        callback_map = {
            "browse_button": lambda: self.browse_file(),
            "new_books_check": lambda: self.load_books_check.click(),
            "read_date_check": lambda: self.add_read_date_check.click(),
            "file_has_header_check": lambda: self.file_has_header_check.click(),
            "preview_button": lambda: self.preview_import(),
            "import_button": lambda: self.import_books(),
        }
        mgr.register_alt_shortcuts(
            self, ShortcutContext.BOOK_LIST_IMPORT_WINDOW, callback_map
        )

    def on_load_books_toggled(self, checked: bool):
        """Handle Load Books checkbox toggle."""
        if checked:
            self.import_mode = "new"
            self.set_status("Mode changed to: Load Books")
        else:
            self.set_status("Load Books disabled")

    def on_add_read_date_toggled(self, checked: bool):
        """Handle Add Read Date checkbox toggle."""
        if checked:
            self.import_mode = "read_date"
            self.set_status("Mode changed to: Add Read Date")
        else:
            self.set_status("Add Read Date disabled")

    def on_file_has_header_toggled(self, checked: bool):
        """Handle File has header checkbox toggle."""
        if self.file_data is not None:
            self.reload_file_with_headers(checked)
        self.set_status(f"File has header: {'Yes' if checked else 'No'}")

    def toggle_mode(self):
        """Toggle between import modes."""
        if hasattr(self, "load_books_check") and self.load_books_check.isChecked():
            self.load_books_check.setChecked(False)
            if hasattr(self, "add_read_date_check"):
                self.add_read_date_check.setChecked(True)
        else:
            if hasattr(self, "add_read_date_check"):
                self.add_read_date_check.setChecked(False)
            if hasattr(self, "load_books_check"):
                self.load_books_check.setChecked(True)
        self.on_mode_changed(0 if self.new_books_radio.isChecked() else 1, True)

    def focus_mapping_row(self, row: int):
        """Focus the combo box in the specified mapping row."""
        combo = self.mapping_table.cellWidget(row, 1)
        if combo:
            combo.setFocus()
            combo.showPopup()

    def on_show_shortcuts(self):
        """Show keyboard shortcuts help dialog (accessible, centralized)."""
        from src.accessibility.shortcut_helpers import (
            get_accessible_shortcuts_list,
            build_accessible_f1_popup_style,
        )

        shortcuts = [
            ("Alt+W", "Browse for file"),
            ("Alt+N", "Import new books"),
            ("Alt+U", "Update read dates"),
            ("Alt+H", "File has headers"),
            ("Alt+T", "Title"),
            ("Alt+A", "Author"),
            ("Alt+Y", "Year"),
            ("Alt+P", "Plot"),
            ("Alt+S", "Series"),
            ("Alt+G", "Genre"),
            ("Alt+R", "Reader"),
            ("Alt+E", "Read Date"),
            ("Alt+M", "Time"),
            ("Alt+B", "Tracks"),
            ("Alt+C", "Preview import"),
            ("Alt+I", "Import books"),
            ("Alt+/", "Read status bar"),
            ("F1", "Show this help"),
            ("Escape", "Close window"),
        ]

        dlg = QDialog(self)
        dlg.setWindowTitle("Keyboard Shortcuts - Book List Import")
        dlg.setAccessibleName("Keyboard Shortcuts")
        dlg.resize(560, 420)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        table = QTableWidget()
        table.setAccessibleName("Shortcuts list")
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
        dlg.exec()

    def show_accessible_message(self, title: str, message: str, icon_type=None):
        """Show accessible message with table format like main window stats."""
        from PySide6.QtWidgets import (
            QDialog,
            QVBoxLayout,
            QTableWidget,
            QTableWidgetItem,
            QPushButton,
        )
        from PySide6.QtCore import Qt

        dlg = QDialog(self)
        dlg.setWindowTitle(title)
        dlg.setAccessibleName(title)
        dlg.resize(400, 200)

        layout = QVBoxLayout(dlg)

        # Create table for message content
        table = QTableWidget()
        table.setRowCount(1)
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels(["Message"])
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)

        # Add message as table item
        item = QTableWidgetItem(message)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        table.setItem(0, 0, item)
        table.resizeColumnsToContents()
        table.setFocus()

        layout.addWidget(table)

        # Add OK button
        button = QPushButton("OK")
        button.clicked.connect(dlg.accept)
        button.setDefault(True)
        layout.addWidget(button)

        dlg.exec()

    def on_read_status_bar(self):
        """Read status bar message for screen readers."""
        if QAccessible.isActive():
            announce_status_message(self.status_bar, self._default_status_message)

    def browse_file(self):
        """Browse for spreadsheet file."""
        file_filter = "Spreadsheet Files (*.xlsx *.xls *.csv);;Excel Files (*.xlsx *.xls);;CSV Files (*.csv);;All Files (*.*)"

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Spreadsheet File", "", file_filter
        )

        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path: str):
        """Load and parse the selected file."""
        try:
            self.set_status("Loading file...")

            # Load file based on extension
            if file_path.lower().endswith(".csv"):
                self.file_data = pd.read_csv(file_path)
            else:
                # Excel files
                self.file_data = pd.read_excel(file_path)

            self.selected_file = file_path
            self.file_edit.setText(file_path)
            self.column_count = len(self.file_data.columns)

            # Update column combos
            self.update_column_combos()

            # Enable buttons
            self.preview_button.setEnabled(True)
            self.import_button.setEnabled(True)

            self.set_status(
                f"Loaded {len(self.file_data)} rows with {self.column_count} columns"
            )

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

    def update_column_combos(self):
        """Update column selection combos with letters A-Z for spreadsheet compatibility."""
        # Generate column letters like Excel: A, B, C..., Z (always 26 options)
        column_letters = []
        for i in range(26):
            column_letters.append(chr(65 + i))  # A-Z

        for combo in self.field_mappings.values():
            combo.clear()
            combo.addItem("None")
            combo.addItems(column_letters)
            # Set combo width with scaling for proper text display
            min_width = self.scaler.get_scaled_size(80)
            max_width = self.scaler.get_scaled_size(150)
            combo.setMinimumWidth(min_width)
            combo.setMaximumWidth(max_width)

        # Set default mappings: Title=A, Author=B (common spreadsheet format)
        self.set_default_mappings()

    def set_default_mappings(self):
        """Set default column mappings for testing - A-J for all 10 fields."""
        # Default mapping: All fields map to A-J for testing
        default_mappings = {
            "title": 0,  # Column A
            "author": 1,  # Column B
            "year": 2,  # Column C
            "plot": 3,  # Column D
            "series": 4,  # Column E
            "genre": 5,  # Column F
            "reader": 6,  # Column G
            "read_date": 7,  # Column H
            "time_hours": 8,  # Column I
            "tracks": 9,  # Column J
        }

        for field, column_index in default_mappings.items():
            if field in self.field_mappings and self.column_count > column_index:
                # Set to column letter (add 1 for "None" option)
                self.field_mappings[field].setCurrentIndex(column_index + 1)

    def on_new_books_toggled(self, checked: bool):
        """Handle new books checkbox toggle with mutual exclusivity."""
        if checked:
            self.read_date_check.setChecked(False)
            self.import_mode = "new"
            self.set_status("Mode changed to: Import New Books")

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
                if has_headers:
                    self.file_data = pd.read_csv(self.selected_file)
                else:
                    self.file_data = pd.read_csv(self.selected_file, header=None)
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

    def on_read_date_toggled(self, checked: bool):
        """Handle read date checkbox toggle with mutual exclusivity."""
        if checked:
            self.new_books_check.setChecked(False)
            self.import_mode = "read_date"
            self.set_status("Mode changed to: Update Read Dates")

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

    def validate_mapping(self) -> Tuple[bool, str]:
        """Validate the field mapping."""
        mapping = self.get_field_mapping()

        # Check required fields
        if mapping["title"] is None:
            return False, "Title field is required"
        if mapping["author"] is None:
            return False, "Author field is required"

        # Check if any fields are mapped
        mapped_fields = [field for field, col in mapping.items() if col is not None]
        if len(mapped_fields) < 2:  # At least title + author
            return False, "At least Title and Author must be mapped"

        return True, "Mapping is valid"

    def preview_import(self):
        """Preview the import with current settings."""
        if not self.file_data is not None:
            self.set_status("No file loaded")
            return

        # Validate mapping
        is_valid, message = self.validate_mapping()
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
            return

        mapping = self.get_field_mapping()

        # Show preview dialog
        preview_text = self.generate_preview_text(mapping)

        exec_styled_message_box(
            self,
            self.scaler.get_scaled_size(20),
            icon=QMessageBox.Information,
            title="Import Preview",
            text=preview_text,
            buttons=QMessageBox.Ok,
            default_button=QMessageBox.Ok,
        )

    def generate_preview_text(self, mapping: Dict[str, Optional[int]]) -> str:
        """Generate preview text for the import."""
        lines = [f"File: {self.selected_file}"]
        lines.append(f"Rows: {len(self.file_data)}")
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
            "genre": "Genre",
            "reader": "Reader",
            "read_date": "Read Date",
            "time_hours": "Time",
            "tracks": "Tracks",
        }

        for field, col_index in mapping.items():
            if col_index is not None:
                column_name = self.file_data.columns[col_index]
                lines.append(
                    f"  {field_labels[field]} → Column {col_index + 1} ({column_name})"
                )

        lines.append("")
        lines.append("Ready to import?")

        return "\n".join(lines)

    def import_books(self):
        """Import books from the loaded file."""
        if not self.file_data is not None:
            self.set_status("No file loaded")
            return

        # Validate mapping
        is_valid, message = self.validate_mapping()
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
            return

        # Confirm import
        reply = exec_styled_message_box(
            self,
            self.scaler.get_scaled_size(20),
            icon=QMessageBox.Question,
            title="Confirm Import",
            text=f"Import {len(self.file_data)} books from {self.selected_file}?",
            buttons=QMessageBox.Yes | QMessageBox.No,
            default_button=QMessageBox.No,
        )

        if reply != QMessageBox.Yes:
            return

        # Perform import
        try:
            self.set_status("Importing books...")

            if self.import_mode == "new":
                success_count, error_count = self.import_new_books()
            else:
                success_count, error_count = self.update_read_dates()

            # Show results
            result_text = (
                f"Import completed:\n{success_count} books processed successfully"
            )
            if error_count > 0:
                result_text += f"\n{error_count} books had errors"

            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Information,
                title="Import Complete",
                text=result_text,
                buttons=QMessageBox.Ok,
                default_button=QMessageBox.Ok,
            )

            self.set_status(
                f"Import complete: {success_count} successful, {error_count} errors"
            )

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
        mapping = self.get_field_mapping()
        success_count = 0
        error_count = 0

        # Ensure "Book List" collection exists
        book_list_collection = self.get_or_create_book_list_collection()

        for index, row in self.file_data.iterrows():
            try:
                # Extract data
                title = str(row.iloc[mapping["title"]]).strip()
                author = str(row.iloc[mapping["author"]]).strip()

                if not title or not author or title == "nan" or author == "nan":
                    error_count += 1
                    continue

                # Check for duplicates
                existing = self.book_queries.find_by_title_author(title, author)
                if existing:
                    error_count += 1
                    continue

                # Create book data
                book_data = {
                    "title": title,
                    "author_name": author,
                    "collection_id": book_list_collection.id,
                }

                # Add optional fields
                if mapping["year"] is not None:
                    year = row.iloc[mapping["year"]]
                    if pd.notna(year):
                        book_data["year"] = int(year) if str(year).isdigit() else None

                if mapping["plot"] is not None:
                    plot = row.iloc[mapping["plot"]]
                    if pd.notna(plot) and str(plot) != "nan":
                        book_data["plot"] = str(plot)

                if mapping["series"] is not None:
                    series = row.iloc[mapping["series"]]
                    if pd.notna(series) and str(series) != "nan":
                        book_data["series_name"] = str(series)

                if mapping["genre"] is not None:
                    genre = row.iloc[mapping["genre"]]
                    if pd.notna(genre) and str(genre) != "nan":
                        book_data["genre"] = str(genre)

                if mapping["reader"] is not None:
                    reader = row.iloc[mapping["reader"]]
                    if pd.notna(reader) and str(reader) != "nan":
                        book_data["reader"] = str(reader)

                if mapping["read_date"] is not None:
                    read_date = row.iloc[mapping["read_date"]]
                    if pd.notna(read_date) and str(read_date) != "nan":
                        book_data["read_date"] = str(read_date)

                if mapping["time_hours"] is not None:
                    time_hours = row.iloc[mapping["time_hours"]]
                    if pd.notna(time_hours) and str(time_hours) != "nan":
                        book_data["time_hours"] = float(time_hours)

                if mapping["tracks"] is not None:
                    tracks = row.iloc[mapping["tracks"]]
                    if pd.notna(tracks) and str(tracks) != "nan":
                        book_data["tracks"] = (
                            int(tracks) if str(tracks).isdigit() else None
                        )

                # Insert book
                self.book_queries.create_book(book_data)
                success_count += 1

            except Exception as e:
                print(f"Error importing row {index}: {e}")
                error_count += 1
                continue

        return success_count, error_count

    def update_read_dates(self) -> Tuple[int, int]:
        """Update read dates for existing books."""
        mapping = self.get_field_mapping()
        success_count = 0
        error_count = 0

        for index, row in self.file_data.iterrows():
            try:
                # Extract data
                title = str(row.iloc[mapping["title"]]).strip()
                author = str(row.iloc[mapping["author"]]).strip()

                if not title or not author or title == "nan" or author == "nan":
                    error_count += 1
                    continue

                # Find existing book
                existing_book = self.book_queries.find_by_title_author(title, author)
                if not existing_book:
                    error_count += 1
                    continue

                # Update read date if provided
                if mapping["read_date"] is not None:
                    read_date = row.iloc[mapping["read_date"]]
                    if pd.notna(read_date) and str(read_date) != "nan":
                        self.book_queries.update_book(
                            existing_book.id, {"read_date": str(read_date)}
                        )
                        success_count += 1
                    else:
                        error_count += 1
                else:
                    error_count += 1

            except Exception as e:
                print(f"Error updating row {index}: {e}")
                error_count += 1
                continue

        return success_count, error_count

    def get_or_create_book_list_collection(self):
        """Get or create the 'Book List' collection."""
        collection = self.collection_queries.find_by_name("Book List")
        if not collection:
            collection = self.collection_queries.create_collection(
                {
                    "name": "Book List",
                    "description": "Books imported from spreadsheet files",
                }
            )
        return collection

    def set_status(self, message: str, announce: bool = False):
        """Set status message and optionally announce to screen reader."""
        self._default_status_message = message
        self.status_bar.showMessage(message)

        if announce:
            announce_status_message(message)

    def apply_theme(self):
        """Apply the current theme."""
        self.theme_manager._apply_theme()
