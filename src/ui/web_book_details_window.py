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
    QWidget, QStatusBar, QFrame
)
from PySide6.QtCore import Qt, QDate, QEvent, QTimer, QSettings
from PySide6.QtGui import QAccessible, QTextCursor, QShortcut, QKeySequence
from datetime import datetime


class WebBookDetailsWindow(QDialog):
    """Web Book Details window for reviewing and accepting web-fetched metadata."""

    def set_status(self, message: str, announce: bool = False):
        """Set status bar message with optional screen reader announcement."""
        self._default_status_message = message
        announce_status_message(self.status_bar, message, move_focus=announce)

    def on_read_status_bar(self):
        """Read current status bar message (Alt+/)."""
        status_text = self.status_bar.currentMessage() or self._default_status_message
        if QAccessible.isActive():
            self.set_status(status_text, announce=True)
        else:
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Information,
                title="Status Bar",
                text=f"No screen reader active.\n\nStatus: {status_text}",
            )

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
        
        # Web data (fake for now)
        self.web_data = self._get_fake_web_data()
        
        # Window setup
        self.setWindowTitle("Web Book Details")
        self.setAccessibleName("Web Book Details Window")
        self.setAccessibleDescription("Window for reviewing and accepting web-fetched book metadata")
        self.setMinimumSize(600, 700)
        self.resize(700, 800)
        
        self._default_status_message = "Ready"
        self.setup_ui()
        self.setup_shortcuts()
        self.load_book_data()

    def _get_fake_web_data(self):
        """Get fake web data for testing."""
        return {
            'title': 'The Great Gatsby: Enhanced Edition',
            'author': 'F. Scott Fitzgerald',
            'year': '1925',
            'series': 'Classic Literature Collection',
            'genre': 'Fiction > Classic Literature',
            'plot': 'A classic American novel set in the Jazz Age, exploring themes of wealth, love, and the American Dream through the mysterious Jay Gatsby.',
            'isbn': '978-0-7432-7356-5',
            'publisher': 'Scribner',
            'pages': '180'
        }

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
        form_layout.setSpacing(10)
        
        # Title field (read-only)
        self.title_field = QLineEdit()
        self.title_field.setReadOnly(True)
        self.title_field.setAccessibleName("Title")
        self.title_field.setAccessibleDescription("Book title from web source")
        form_layout.addRow("Title:", self._create_field_with_indicator(self.title_field, self.web_data['title']))
        
        # Author field (read-only, was combo box)
        self.author_field = QLineEdit()
        self.author_field.setReadOnly(True)
        self.author_field.setAccessibleName("Author")
        self.author_field.setAccessibleDescription("Author name from web source")
        form_layout.addRow("Author:", self._create_field_with_indicator(self.author_field, self.web_data['author']))
        
        # Year field
        self.year_field = QLineEdit()
        self.year_field.setReadOnly(True)
        self.year_field.setAccessibleName("Year")
        self.year_field.setAccessibleDescription("Publication year from web source")
        form_layout.addRow("Year:", self._create_field_with_indicator(self.year_field, self.web_data['year']))
        
        # Series field (read-only, was combo box)
        self.series_field = QLineEdit()
        self.series_field.setReadOnly(True)
        self.series_field.setAccessibleName("Series")
        self.series_field.setAccessibleDescription("Series name from web source")
        form_layout.addRow("Series:", self._create_field_with_indicator(self.series_field, self.web_data['series']))
        
        # Genre field (read-only, was combo box)
        self.genre_field = QLineEdit()
        self.genre_field.setReadOnly(True)
        self.genre_field.setAccessibleName("Genre")
        self.genre_field.setAccessibleDescription("Genre from web source")
        form_layout.addRow("Genre:", self._create_field_with_indicator(self.genre_field, self.web_data['genre']))
        
        # Plot/Comments field
        self.plot_field = QTextEdit()
        self.plot_field.setReadOnly(True)
        self.plot_field.setAccessibleName("Plot Summary")
        self.plot_field.setAccessibleDescription("Plot summary from web source")
        self.plot_field.setMaximumHeight(120)
        form_layout.addRow("Plot:", self._create_field_with_indicator(self.plot_field, self.web_data['plot']))
        
        main_layout.addLayout(form_layout)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.add_plot_button = QPushButton("Add Plot")
        self.add_plot_button.setAccessibleName("Add plot to comments")
        self.add_plot_button.setAccessibleDescription("Add web plot summary to book comments field")
        self.add_plot_button.clicked.connect(self.on_add_plot)
        button_layout.addWidget(self.add_plot_button)
        
        button_layout.addStretch()
        
        self.update_all_button = QPushButton("Update All")
        self.update_all_button.setAccessibleName("Update all fields")
        self.update_all_button.setAccessibleDescription("Apply all web data changes to original book record")
        self.update_all_button.clicked.connect(self.on_update_all)
        button_layout.addWidget(self.update_all_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setAccessibleName("Cancel")
        self.cancel_button.setAccessibleDescription("Close window without making changes")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        main_layout.addWidget(self.status_bar)
        
        # Apply theme
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
        self.on_theme_changed()

    def _create_field_with_indicator(self, field, web_value):
        """Create a field with web data difference indicator."""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # The actual field
        field.setText(str(web_value))
        layout.addWidget(field)
        
        # Difference indicator (check mark for web data)
        indicator = QLabel("✓")
        indicator.setAccessibleName("Web data indicator")
        indicator.setAccessibleDescription("This field contains web-fetched data")
        indicator.setStyleSheet("color: green; font-weight: bold;")
        indicator.setFixedWidth(20)
        layout.addWidget(indicator)
        
        return container

    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # F1 for help
        help_shortcut = QShortcut(QKeySequence("F1"), self)
        help_shortcut.activated.connect(self.on_show_shortcuts)
        
        # Alt+/ for status bar
        status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        status_shortcut.activated.connect(self.on_read_status_bar)
        
        # Escape to close
        escape_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        escape_shortcut.activated.connect(self.reject)

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

    def on_add_plot(self):
        """Add plot summary to book comments."""
        if self.web_data['plot']:
            # For now, just show a message - will implement actual update later
            QMessageBox.information(
                self,
                "Add Plot",
                f"Plot summary will be added to comments:\n\n{self.web_data['plot'][:100]}..."
            )
            self.set_status("Plot added to comments", announce=True)

    def on_update_all(self):
        """Update all fields with web data."""
        # Show confirmation dialog
        reply = QMessageBox.question(
            self,
            "Update All",
            "Update all book fields with web data?\n\nThis will replace existing data.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # For now, just show success message - will implement actual update later
            QMessageBox.information(
                self,
                "Update Complete",
                "All fields updated with web data successfully."
            )
            self.set_status("All fields updated", announce=True)
            self.accept()

    def on_show_shortcuts(self):
        """Show keyboard shortcuts help dialog."""
        shortcuts = [
            ("F1", "Show this help"),
            ("Alt+/", "Read status bar"),
            ("Escape", "Close window"),
        ]
        
        # Centralize Alt+/ visibility for screen readers
        shortcuts = get_accessible_shortcuts_list(shortcuts)
        
        dlg = QDialog(self)
        dlg.setWindowTitle("Keyboard Shortcuts - Web Book Details")
        dlg.setAccessibleName("Keyboard Shortcuts")
        dlg.resize(400, 200)
        
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        
        for key, desc in shortcuts:
            label = QLabel(f"{desc} - {key}")
            label.setWordWrap(True)
            layout.addWidget(label)
        
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
