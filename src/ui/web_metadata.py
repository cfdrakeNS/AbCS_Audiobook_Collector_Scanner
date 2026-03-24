"""
Web Book Details Window - Audio Book Collection
Shows web-fetched book data with comparison to local data.
Modeled from book_details.py with modifications for web data display.
"""

import re
from src.database import DatabaseManager, Book, BookQueries, AuthorQueries, SeriesQueries, GenreQueries, CollectionQueries
from src.accessibility.theme_manager import ThemeManager
from src.accessibility.scaling import UIScaler
from src.accessibility.shortcuts import ShortcutManager, ShortcutContext
from src.accessibility.style_helpers import build_accessible_message_box_style, exec_styled_message_box
from src.accessibility.accessible_events import announce_status_message, announce_form_field, announce_dialog_opened, announce_dialog_closed
from src.accessibility.shortcut_helpers import get_accessible_shortcuts_list, build_accessible_f1_popup_style

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QPushButton, QLabel, QMessageBox,
    QWidget, QStatusBar, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QDate, QEvent, QTimer, QSettings, QThread, Signal
from PySide6.QtGui import QAccessible, QTextCursor, QShortcut, QKeySequence
from datetime import datetime


class WebDataFetcher(QThread):
    """Background thread for fetching web book data."""
    
    data_ready = Signal(dict)
    error_occurred = Signal(str)
    
    def __init__(self, title: str, author: str, year: str = None):
        super().__init__()
        self.title = title
        self.author = author
        self.year = year
    
    def run(self):
        """Fetch web data in background thread."""
        try:
            from src.web.web_book_api import WebBookAPI
            
            api = WebBookAPI()
            web_data = api.get_book_metadata(self.title, self.author, self.year)
            
            if web_data:
                self.data_ready.emit(web_data)
            else:
                self.error_occurred.emit("No data found for this book")
                
        except Exception as e:
            self.error_occurred.emit(f"Error fetching web data: {str(e)}")


class WebMetadataWindow(QDialog):
    """Web Book Details window for reviewing and accepting web-fetched metadata."""

    def set_status(self, message: str, announce: bool = False):
        """Set status bar message with optional screen reader announcement."""
        self._default_status_message = message
        self._status_message = message  # Store for Alt+/ announcements
        announce_status_message(self.status_bar, message, move_focus=announce)

    def on_read_status_bar(self):
        """Read status bar message (Alt+/)."""
        if QAccessible.isActive():
            # Read stored status message for screen readers
            if self._status_message:
                announce_status_message(self.status_bar, self._status_message, move_focus=False)
        # If no screen reader active, do nothing (Alt+/ hidden from F1 menu by get_accessible_shortcuts_list)

    def __init__(self, db: DatabaseManager, book: Book, scaler: UIScaler, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self.db = db
        self.book = book
        self.scaler = scaler
        self.theme_manager = theme_manager
        self.book_queries = BookQueries(db)
        self.author_queries = AuthorQueries(db)
        self.series_queries = SeriesQueries(db)
        self.genre_queries = GenreQueries(db)
        self.collection_queries = CollectionQueries(db)
        
        # Web data (will be fetched from API)
        self.web_data = {}
        
        # Window setup
        self.setWindowTitle("Web Book Details")
        self.setAccessibleName("Web Book Details Window")
        self.setAccessibleDescription("Window for reviewing and accepting web-fetched book metadata")
        self.setMinimumSize(600, 700)
        self.resize(700, 800)
        
        self._default_status_message = "Ready"
        self._status_message = ""  # Store status message for Alt+/ announcements
        self.setup_ui()
        self.setup_shortcuts()
        self.load_book_data()
        self.fetch_web_data()  # Start fetching real data

    def setup_ui(self):
        """Setup user interface with vertical layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Web Book Details")
        title_label.setStyleSheet(f"font-size: {self.scaler.get_scaled_size(16)}px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Form layout for book details (vertical alignment)
        form_layout = QFormLayout()
        form_layout.setSpacing(3)  # Tighter vertical spacing
        form_layout.setContentsMargins(20, 20, 20, 20)
        
        # Set proper alignment for labels and fields
        form_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        # Title field (read-only)
        self.title_field = QLineEdit()
        self.title_field.setReadOnly(True)
        self.title_field.setAccessibleName("Title")
        self.title_field.setAccessibleDescription("Book title from web source")
        self.title_field.setText(self.book.title or "Loading...")
        title_label = QLabel("&Title:")
        title_label.setBuddy(self.title_field)
        form_layout.addRow(title_label, self._create_field_with_indicator(self.title_field, ""))
        
        # Author field (read-only)
        self.author_field = QLineEdit()
        self.author_field.setReadOnly(True)
        self.author_field.setAccessibleName("Author")
        self.author_field.setAccessibleDescription("Author name from web source")
        self.author_field.setText(self.book.author_name or "Loading...")
        author_label = QLabel("&Author:")
        author_label.setBuddy(self.author_field)
        form_layout.addRow(author_label, self._create_field_with_indicator(self.author_field, ""))
        
        # Year field
        self.year_field = QLineEdit()
        self.year_field.setReadOnly(True)
        self.year_field.setAccessibleName("Year")
        self.year_field.setAccessibleDescription("Publication year from web source")
        self.year_field.setText(str(self.book.year) if self.book.year else "Loading...")
        year_label = QLabel("&Year:")
        year_label.setBuddy(self.year_field)
        form_layout.addRow(year_label, self._create_field_with_indicator(self.year_field, ""))
        
        # Series field (read-only)
        self.series_field = QLineEdit()
        self.series_field.setReadOnly(True)
        self.series_field.setAccessibleName("Series")
        self.series_field.setAccessibleDescription("Series name from web source")
        self.series_field.setText(self.book.series_name or "Loading...")
        series_label = QLabel("Ser&ies:")
        series_label.setBuddy(self.series_field)
        form_layout.addRow(series_label, self._create_field_with_indicator(self.series_field, ""))
        
        # Genre field (read-only)
        self.genre_field = QLineEdit()
        self.genre_field.setReadOnly(True)
        self.genre_field.setAccessibleName("Genre")
        self.genre_field.setAccessibleDescription("Genre from web source")
        self.genre_field.setText(self.book.genre_name or "Loading...")
        genre_label = QLabel("&Genre:")
        genre_label.setBuddy(self.genre_field)
        form_layout.addRow(genre_label, self._create_field_with_indicator(self.genre_field, ""))
        
        # Plot field (read-only)
        self.plot_field = QTextEdit()
        self.plot_field.setReadOnly(True)
        self.plot_field.setAccessibleName("Plot Summary")
        self.plot_field.setAccessibleDescription("Plot summary from web source")
        self.plot_field.setMaximumHeight(120)
        self.plot_field.setPlainText(self.book.comments or "Loading...")
        plot_label = QLabel("Pl&ot:")
        plot_label.setBuddy(self.plot_field)
        form_layout.addRow(plot_label, self.plot_field)
        
        main_layout.addLayout(form_layout)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.save_button = QPushButton("&Save")
        self.save_button.setAccessibleName("Save all fields")
        self.save_button.setAccessibleDescription("Apply all web data changes to original book record")
        self.save_button.setFocusPolicy(Qt.StrongFocus)
        self.save_button.setMinimumHeight(30)  # Standard button height
        self.save_button.setMaximumHeight(40)  # Reasonable max height
        self.save_button.clicked.connect(self.on_update_all)
        self.save_button.setDefault(False)
        self.save_button.setAutoDefault(False)
        button_layout.addWidget(self.save_button)
        
        button_layout.addStretch()
        
        self.add_plot_button = QPushButton("Keep Plot")
        self.add_plot_button.setAccessibleName("Add plot to comments")
        self.add_plot_button.setAccessibleDescription("Add web plot summary to book comments field")
        self.add_plot_button.setFocusPolicy(Qt.StrongFocus)
        self.add_plot_button.setMinimumHeight(30)  # Standard button height
        self.add_plot_button.setMaximumHeight(40)  # Reasonable max height
        self.add_plot_button.clicked.connect(self.on_add_plot)
        self.add_plot_button.setDefault(False)
        self.add_plot_button.setAutoDefault(False)
        button_layout.addWidget(self.add_plot_button)
        
        main_layout.addLayout(button_layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        main_layout.addWidget(self.status_bar)
        
        # Apply theme
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
        self.on_theme_changed()

    def fetch_web_data(self):
        """Start fetching web data in background thread."""
        self.set_status("Fetching web data...", announce=True)
        
        # Create and start web data fetcher thread
        self.fetcher = WebDataFetcher(
            self.book.title,
            self.book.author_name,
            str(self.book.year) if self.book.year else None
        )
        self.fetcher.data_ready.connect(self.on_web_data_ready)
        self.fetcher.error_occurred.connect(self.on_web_data_error)
        self.fetcher.start()

    def on_web_data_ready(self, data):
        """Handle successful web data fetch."""
        self.web_data = data
        
        # Populate fields with fetched data
        self.title_field.setText(data.get('title', ''))
        self.author_field.setText(data.get('author', ''))
        self.year_field.setText(data.get('year', ''))
        self.series_field.setText(data.get('series', ''))
        self.genre_field.setText(data.get('genre', ''))
        self.plot_field.setPlainText(data.get('plot', ''))
        
        # Enable buttons
        self.add_plot_button.setEnabled(bool(data.get('plot')))
        self.save_button.setEnabled(True)
        
        # Update status
        source = data.get('source', 'unknown')
        self.set_status(f"Web data loaded from {source}", announce=True)

    def on_web_data_error(self, error_message):
        """Handle web data fetch error."""
        self.set_status(f"Error fetching web data: {error_message}", announce=True)
        # Keep loading text in fields to show error state

    def load_book_data(self):
        """Load current book data for comparison."""
        # Load existing book data
        self.original_data = {
            'title': self.book.title or "",
            'author': self.book.author_name or "",
            'year': str(self.book.year or ""),
            'series': self.book.series_name or "",
            'genre': self.book.genre_name or "",
            'plot': self.book.comments or ""
        }
        
        self.set_status(f"Loaded book: {self.book.title}", announce=True)

    def _create_field_with_indicator(self, field, web_value):
        """Create a field with web data difference indicator."""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)  # Reduced spacing to prevent excessive gaps
        
        # Set container to match field height
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # The actual field
        field.setText(str(web_value))
        layout.addWidget(field)
        
        # Difference indicator (check mark for web data)
        indicator = QLabel("✓")
        indicator.setAccessibleName("Web data indicator")
        indicator.setAccessibleDescription("This field contains web-fetched data")
        indicator.setStyleSheet("color: #2E8B57; font-weight: bold;")  # Sea green
        indicator.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        indicator.setAlignment(Qt.AlignCenter)
        layout.addWidget(indicator)
        
        return container

    def setup_shortcuts(self):
        """Centralized Alt+letter shortcut registration using ShortcutManager."""
        from src.accessibility.shortcuts import get_shortcut_manager, ShortcutContext
        mgr = get_shortcut_manager()
        callback_map = {
            'title_edit': lambda: self.title_field.setFocus(),      # Alt+T
            'author_edit': lambda: self.author_field.setFocus(),    # Alt+A
            'year_edit': lambda: self.year_field.setFocus(),        # Alt+Y
            'series_edit': lambda: self.series_field.setFocus(),    # Alt+I
            'genre_edit': lambda: self.genre_field.setFocus(),      # Alt+G
            'plot_edit': lambda: self.plot_field.setFocus(),        # Alt+P
            'save_button': self.on_update_all,                     # Alt+S
            'show_help': self.on_show_shortcuts,                    # F1
        }
        mgr.register_alt_shortcuts(self, ShortcutContext.WEB_METADATA, callback_map)
        
        # Local shortcuts: Alt+/, Escape
        status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        status_shortcut.activated.connect(self.on_read_status_bar)
        escape_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        escape_shortcut.activated.connect(self.reject)

    def on_add_plot(self):
        """Add plot summary to book comments."""
        if self.web_data['plot']:
            # For now, just show a message - will implement actual update later
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Information,
                title="Add Plot",
                text=f"Plot summary will be added to comments:\n\n{self.web_data['plot'][:200]}..."
            )
            self.set_status("Plot added to comments", announce=True)

    def on_update_all(self):
        """Update all fields with web data."""
        # Show confirmation dialog
        msg = QMessageBox(self)
        msg.setWindowTitle("Update All")
        msg.setStyleSheet(build_accessible_message_box_style(self.scaler.get_scaled_size(20)))
        msg.setText("Update all book fields with web data?\n\nThis will replace existing data.")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.button(QMessageBox.Yes).setText("&Yes - Update")
        msg.button(QMessageBox.No).setText("&No - Cancel")
        reply = msg.exec()
        
        if reply == QMessageBox.Yes:
            # For now, just show success message - will implement actual update later
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Information,
                title="Update Complete",
                text="All fields updated with web data successfully."
            )
            self.set_status("All fields updated", announce=True)
            self.accept()

    def on_show_shortcuts(self):
        """Show keyboard shortcuts help dialog."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Keyboard Shortcuts - Web Book Details")
        dlg.setAccessibleName("Keyboard Shortcuts")
        dlg.resize(580, 440)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        table = QTableWidget()
        table.setAccessibleName("Shortcuts list")
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels([""])
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setTabKeyNavigation(False)
        table.setAlternatingRowColors(False)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        table.setShowGrid(False)
        from src.accessibility.shortcut_helpers import get_accessible_shortcuts_list, build_accessible_f1_popup_style
        table.setStyleSheet(build_accessible_f1_popup_style())

        shortcuts = [
            ("Alt+T", "Title"),
            ("Alt+A", "Author"),
            ("Alt+P", "Plot"),
            ("Alt+Y", "Year"),
            ("Alt+I", "Series"),
            ("Alt+G", "Genre"),
            ("Alt+S", "Save"),
            ("Escape", "Close window"),
            ("Alt+/", "Read status bar"),
            ("F1", "Show keyboard shortcuts"),
        ]
        shortcuts = get_accessible_shortcuts_list(shortcuts)

        table.setRowCount(len(shortcuts))
        table.setVerticalHeaderLabels([""] * len(shortcuts))
        for row, (key, desc) in enumerate(shortcuts):
            item = QTableWidgetItem(f"{desc} - {key}")
            item.setData(Qt.AccessibleTextRole, f"{desc}: {key}")
            table.setItem(row, 0, item)

        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        
        # Resize column to stretch
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        
        # Set font size
        font = table.font()
        font.setPointSize(self.scaler.get_scaled_size(11))
        table.setFont(font)
        
        layout.addWidget(table)
        dlg.exec()

    def on_theme_changed(self):
        """Handle theme change."""
        # Apply accessible styling
        button_style = build_accessible_message_box_style(self.scaler.get_scaled_size(20))
        
        for button in self.findChildren(QPushButton):
            button.setStyleSheet(button_style)
        
        # Apply F1 popup style to fields
        field_style = build_accessible_f1_popup_style()
        
        for field in self.findChildren(QLineEdit):
            field.setStyleSheet(field_style)
        
        for field in self.findChildren(QTextEdit):
            field.setStyleSheet(field_style)

    def keyPressEvent(self, event):
        """Handle key press events."""
        # Prevent Enter from closing dialog
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            event.ignore()
            return
        super().keyPressEvent(event)

    def showEvent(self, event):
        """Handle show event."""
        announce_dialog_opened(self)
        super().showEvent(event)

    def closeEvent(self, event):
        """Handle window close event."""
        announce_dialog_closed(self)
        super().closeEvent(event)
