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
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QGroupBox,
    QRadioButton, QButtonGroup, QLineEdit, QStatusBar,
    QMessageBox, QFileDialog, QHeaderView, QAbstractItemView
)
from PySide6.QtGui import QShortcut, QKeySequence, QAccessible

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
    ALLOWED_ALT_LETTERS = "F M T A Y P S G R I H B C V L /"

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
                self, self.scaler.get_scaled_size(20),
                icon=QMessageBox.Critical,
                title="Missing Dependencies",
                text="Book List Import requires pandas and openpyxl.\n\nPlease install with:\npip install pandas openpyxl",
                buttons=QMessageBox.Ok,
                default_button=QMessageBox.Ok
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
        self.setAccessibleDescription("Import books from spreadsheet files with field mapping")
        self.setMinimumSize(900, 700)
        self.resize(1000, 800)
        
        self.setup_ui()
        self.setup_shortcuts()
        self.apply_theme()
        
        # Focus on file selector initially
        self.file_edit.setFocus()

    def setup_ui(self):
        """Setup the user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(12, 12, 12, 12)
        
        # File selection section
        file_group = QGroupBox("File Selection")
        file_group.setAccessibleName("File selection group")
        file_layout = QHBoxLayout(file_group)
        
        file_label = QLabel("Spreadsheet File:")
        file_label.setAccessibleName("File label")
        
        self.file_edit = QLineEdit()
        self.file_edit.setAccessibleName("File path")
        self.file_edit.setAccessibleDescription("Path to the spreadsheet file to import")
        self.file_edit.setReadOnly(True)
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.setAccessibleName("Browse button")
        self.browse_button.setAccessibleDescription("Browse for spreadsheet file - Alt+F")
        self.browse_button.clicked.connect(self.browse_file)
        
        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_edit)
        file_layout.addWidget(self.browse_button)
        
        main_layout.addWidget(file_group)
        
        # Import mode selection
        mode_group = QGroupBox("Import Mode")
        mode_group.setAccessibleName("Import mode group")
        mode_layout = QVBoxLayout(mode_group)
        
        self.mode_button_group = QButtonGroup(self)
        
        self.new_books_radio = QRadioButton("Import New Books")
        self.new_books_radio.setAccessibleName("Import new books mode")
        self.new_books_radio.setAccessibleDescription("Create new book records from spreadsheet")
        self.new_books_radio.setChecked(True)
        
        self.read_date_radio = QRadioButton("Update Read Dates for Existing Books")
        self.read_date_radio.setAccessibleName("Update read dates mode")
        self.read_date_radio.setAccessibleDescription("Update read dates for existing books matching title and author")
        
        self.mode_button_group.addButton(self.new_books_radio, 0)
        self.mode_button_group.addButton(self.read_date_radio, 1)
        self.mode_button_group.idToggled.connect(self.on_mode_changed)
        
        mode_layout.addWidget(self.new_books_radio)
        mode_layout.addWidget(self.read_date_radio)
        
        main_layout.addWidget(mode_group)
        
        # Field mapping table
        mapping_group = QGroupBox("Field Mapping")
        mapping_group.setAccessibleName("Field mapping group")
        mapping_layout = QVBoxLayout(mapping_group)
        
        # Create table for field mapping
        self.mapping_table = QTableWidget()
        self.mapping_table.setAccessibleName("Field mapping table")
        self.mapping_table.setAccessibleDescription("Map spreadsheet columns to book fields")
        
        # Setup table columns
        self.mapping_table.setColumnCount(2)
        self.mapping_table.setHorizontalHeaderLabels(["Field", "Spreadsheet Column"])
        
        # Setup table rows
        self.setup_mapping_table()
        
        # Table styling
        header = self.mapping_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        
        self.mapping_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.mapping_table.setAlternatingRowColors(True)
        
        # Hide vertical headers for accessibility
        self.mapping_table.verticalHeader().setVisible(False)
        
        mapping_layout.addWidget(self.mapping_table)
        
        main_layout.addWidget(mapping_group)
        
        # Collection info
        collection_layout = QHBoxLayout()
        collection_label = QLabel("Target Collection:")
        collection_label.setAccessibleName("Collection label")
        
        self.collection_label = QLabel('"Book List" (auto-created if needed)')
        self.collection_label.setAccessibleName("Target collection")
        self.collection_label.setStyleSheet("font-weight: bold; color: #0066cc;")
        
        collection_layout.addWidget(collection_label)
        collection_layout.addWidget(self.collection_label)
        collection_layout.addStretch()
        
        main_layout.addLayout(collection_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.preview_button = QPushButton("Preview")
        self.preview_button.setAccessibleName("Preview button")
        self.preview_button.setAccessibleDescription("Preview import mapping and data - Alt+C")
        self.preview_button.clicked.connect(self.preview_import)
        self.preview_button.setEnabled(False)
        
        self.import_button = QPushButton("Import")
        self.import_button.setAccessibleName("Import button")
        self.import_button.setAccessibleDescription("Import books from spreadsheet - Alt+V")
        self.import_button.clicked.connect(self.import_books)
        self.import_button.setEnabled(False)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setAccessibleName("Cancel button")
        self.cancel_button.setAccessibleDescription("Close window without importing - Alt+L")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.preview_button)
        button_layout.addWidget(self.import_button)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setAccessibleName("Status bar")
        main_layout.addWidget(self.status_bar)
        
        # Set initial status
        self.set_status("Ready - Select a spreadsheet file to begin")
        
        # Set tab order
        self.setTabOrder(self.browse_button, self.new_books_radio)
        self.setTabOrder(self.new_books_radio, self.read_date_radio)
        self.setTabOrder(self.read_date_radio, self.mapping_table)
        self.setTabOrder(self.mapping_table, self.preview_button)
        self.setTabOrder(self.preview_button, self.import_button)
        self.setTabOrder(self.import_button, self.cancel_button)

    def setup_mapping_table(self):
        """Setup the field mapping table rows."""
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
            ("tracks", "Tracks")
        ]
        
        self.mapping_table.setRowCount(len(fields))
        self.field_mappings = {}
        
        for row, (field_name, field_label) in enumerate(fields):
            # Field name column
            field_item = QTableWidgetItem(field_label)
            field_item.setFlags(field_item.flags() & ~Qt.ItemIsEditable)
            if field_name in ["title", "author"]:
                field_item.setData(Qt.AccessibleTextRole, f"{field_label} - Required field")
            self.mapping_table.setItem(row, 0, field_item)
            
            # Column selection combo
            combo = QComboBox()
            combo.setAccessibleName(f"{field_label} column mapping")
            combo.addItem("None")
            combo.currentIndexChanged.connect(lambda idx, r=row, f=field_name: self.on_mapping_changed(r, f, idx))
            
            self.mapping_table.setCellWidget(row, 1, combo)
            self.field_mappings[field_name] = combo

    def setup_shortcuts(self):
        """Setup keyboard shortcuts using ShortcutManager."""
        mgr = get_shortcut_manager()
        callback_map = {
            'browse_button': self.browse_file,
            'preview_button': self.preview_import,
            'import_button': self.import_books,
        }
        mgr.register_alt_shortcuts(self, ShortcutContext.IMPORT_WINDOW, callback_map)
        
        # Local shortcuts
        self.help_shortcut = QShortcut(QKeySequence("F1"), self)
        self.help_shortcut.activated.connect(self.on_show_shortcuts)
        
        self.status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.status_shortcut.activated.connect(self.on_read_status_bar)
        
        self.close_shortcut = QShortcut(QKeySequence("Alt+L"), self)
        self.close_shortcut.activated.connect(self.reject)

    def on_show_shortcuts(self):
        """Show keyboard shortcuts help dialog."""
        shortcuts = [
            ("Alt+F", "Browse for spreadsheet file"),
            ("Alt+M", "Toggle import mode"),
            ("Alt+T", "Title field mapping"),
            ("Alt+A", "Author field mapping"),
            ("Alt+Y", "Year field mapping"),
            ("Alt+P", "Plot field mapping"),
            ("Alt+S", "Series field mapping"),
            ("Alt+G", "Genre field mapping"),
            ("Alt+R", "Reader field mapping"),
            ("Alt+I", "Read Date field mapping"),
            ("Alt+H", "Time field mapping"),
            ("Alt+B", "Tracks field mapping"),
            ("Alt+C", "Preview import"),
            ("Alt+V", "Import books"),
            ("Alt+L", "Close window"),
            ("Alt+/", "Read status bar"),
            ("F1", "Show this help"),
            ("Escape", "Close window")
        ]
        
        # Create help dialog
        dlg = QDialog(self)
        dlg.setWindowTitle("Book List Import - Keyboard Shortcuts")
        dlg.setAccessibleName("Keyboard shortcuts help dialog")
        dlg.setAccessibleDescription("List of all keyboard shortcuts for book list import")
        dlg.resize(500, 600)
        
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Keyboard Shortcuts")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Shortcuts table
        table = QTableWidget()
        table.setRowCount(len(shortcuts))
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Shortcut", "Action"])
        
        # Disable mouse tracking for accessibility
        table.setMouseTracking(False)
        table.viewport().setMouseTracking(False)
        table.setAttribute(Qt.WA_Hover, False)
        table.viewport().setAttribute(Qt.WA_Hover, False)
        
        # Populate table
        for row, (shortcut, action) in enumerate(shortcuts):
            shortcut_item = QTableWidgetItem(shortcut)
            action_item = QTableWidgetItem(action)
            table.setItem(row, 0, shortcut_item)
            table.setItem(row, 1, action_item)
        
        # Style table
        table.horizontalHeader().setStretchLastSection(True)
        table.setColumnWidth(0, 150)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Apply accessible styling
        from src.accessibility.shortcut_helpers import build_accessible_f1_popup_style
        table.setStyleSheet(build_accessible_f1_popup_style())
        
        layout.addWidget(table)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(dlg.accept)
        layout.addWidget(close_button)
        
        dlg.exec()

    def on_read_status_bar(self):
        """Read status bar message for screen readers."""
        if QAccessible.isActive():
            announce_status_message(self._default_status_message)

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
            if file_path.lower().endswith('.csv'):
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
            
            self.set_status(f"Loaded {len(self.file_data)} rows with {self.column_count} columns")
            
        except Exception as e:
            exec_styled_message_box(
                self, self.scaler.get_scaled_size(20),
                icon=QMessageBox.Critical,
                title="File Error",
                text=f"Could not load file:\n{str(e)}",
                buttons=QMessageBox.Ok,
                default_button=QMessageBox.Ok
            )
            self.set_status("File loading failed")

    def update_column_combos(self):
        """Update column selection combos with actual columns."""
        column_names = [f"Column {i+1}" for i in range(self.column_count)]
        
        for combo in self.field_mappings.values():
            combo.clear()
            combo.addItem("None")
            combo.addItems(column_names)

    def on_mode_changed(self, button_id: int, checked: bool):
        """Handle import mode change."""
        if checked:
            self.import_mode = "new" if button_id == 0 else "read_date"
            mode_text = "Import New Books" if self.import_mode == "new" else "Update Read Dates"
            self.set_status(f"Mode changed to: {mode_text}")

    def on_mapping_changed(self, row: int, field: str, column_index: int):
        """Handle field mapping change."""
        # Validation could be added here
        pass

    def get_field_mapping(self) -> Dict[str, Optional[int]]:
        """Get the current field mapping."""
        mapping = {}
        for field, combo in self.field_mappings.items():
            column_index = combo.currentIndex() - 1  # Subtract 1 for "None" option
            mapping[field] = column_index if column_index >= 0 else None
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
                self, self.scaler.get_scaled_size(20),
                icon=QMessageBox.Warning,
                title="Mapping Error",
                text=message,
                buttons=QMessageBox.Ok,
                default_button=QMessageBox.Ok
            )
            return
        
        mapping = self.get_field_mapping()
        
        # Show preview dialog
        preview_text = self.generate_preview_text(mapping)
        
        exec_styled_message_box(
            self, self.scaler.get_scaled_size(20),
            icon=QMessageBox.Information,
            title="Import Preview",
            text=preview_text,
            buttons=QMessageBox.Ok,
            default_button=QMessageBox.Ok
        )

    def generate_preview_text(self, mapping: Dict[str, Optional[int]]) -> str:
        """Generate preview text for the import."""
        lines = [f"File: {self.selected_file}"]
        lines.append(f"Rows: {len(self.file_data)}")
        lines.append(f"Mode: {'Import New Books' if self.import_mode == 'new' else 'Update Read Dates'}")
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
            "tracks": "Tracks"
        }
        
        for field, col_index in mapping.items():
            if col_index is not None:
                column_name = self.file_data.columns[col_index]
                lines.append(f"  {field_labels[field]} → Column {col_index + 1} ({column_name})")
        
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
                self, self.scaler.get_scaled_size(20),
                icon=QMessageBox.Warning,
                title="Mapping Error",
                text=message,
                buttons=QMessageBox.Ok,
                default_button=QMessageBox.Ok
            )
            return
        
        # Confirm import
        reply = exec_styled_message_box(
            self, self.scaler.get_scaled_size(20),
            icon=QMessageBox.Question,
            title="Confirm Import",
            text=f"Import {len(self.file_data)} books from {self.selected_file}?",
            buttons=QMessageBox.Yes | QMessageBox.No,
            default_button=QMessageBox.No
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
            result_text = f"Import completed:\n{success_count} books processed successfully"
            if error_count > 0:
                result_text += f"\n{error_count} books had errors"
            
            exec_styled_message_box(
                self, self.scaler.get_scaled_size(20),
                icon=QMessageBox.Information,
                title="Import Complete",
                text=result_text,
                buttons=QMessageBox.Ok,
                default_button=QMessageBox.Ok
            )
            
            self.set_status(f"Import complete: {success_count} successful, {error_count} errors")
            
        except Exception as e:
            exec_styled_message_box(
                self, self.scaler.get_scaled_size(20),
                icon=QMessageBox.Critical,
                title="Import Error",
                text=f"Import failed:\n{str(e)}",
                buttons=QMessageBox.Ok,
                default_button=QMessageBox.Ok
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
                    "collection_id": book_list_collection.id
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
                        book_data["tracks"] = int(tracks) if str(tracks).isdigit() else None
                
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
                        self.book_queries.update_book(existing_book.id, {"read_date": str(read_date)})
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
            collection = self.collection_queries.create_collection({
                "name": "Book List",
                "description": "Books imported from spreadsheet files"
            })
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

    def keyPressEvent(self, event):
        """Handle key press events with accessibility filtering."""
        # Handle Alt+letter filtering
        if event.modifiers() & Qt.AltModifier and event.text().upper():
            if event.text().upper() in self.ALLOWED_ALT_LETTERS:
                # Let the event through for allowed Alt+letters
                super().keyPressEvent(event)
            else:
                # Block unmapped Alt+letters
                event.accept()
                return
        
        # Handle Escape
        if event.key() == Qt.Key_Escape:
            self.reject()
            return
        
        super().keyPressEvent(event)
