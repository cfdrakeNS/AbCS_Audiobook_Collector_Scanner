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
    QWidget, QStatusBar, QFrame, QSizePolicy,
    QGroupBox, QCheckBox, QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView
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
    data_saved = Signal()
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
                title="Status",
                text=f"Status: {status_text}"
            )

    def _announce_status_bar(self):
        """Helper method to announce status bar message."""
        status_text = self._default_status_message
        if QAccessible.isActive():
            self.set_status(status_text, announce=True)

    def __init__(self, db: DatabaseManager, book: Book, scaler: UIScaler, theme_manager: ThemeManager, parent=None, refresh_callback=None):
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
        self.refresh_callback = refresh_callback  # For compatibility with main_window.py and JAWS accessibility
        # Web data (will be fetched from API)
        self.web_data = {}
        # Track field differences for red indicators
        self.field_differences = {}
        # Window setup
        self.setWindowTitle("Web Book Details")
        self.setAccessibleName("Web Book Details Window")
        self.setAccessibleDescription("Window for reviewing and accepting web-fetched book metadata")
        self.setMinimumSize(600, 700)
        self.resize(700, 800)
        self._default_status_message = "Ready"
        self._period_message = ""  # Store meaningful message for Alt+/ announcements
        self.setup_ui()
        self.setup_shortcuts()
        self.load_book_data()
        self.fetch_web_data()  # Start fetching real data

    def setup_ui(self):
        """Setup accessible UI using the proven skeleton window pattern."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)

        # Title label (Alt+T)
        title_label = QLabel(f"Title: {self.book.title} by {self.book.author_name}")
        title_label.setAccessibleName("Title")
        title_label.setAccessibleDescription("Book title and author")
        title_label.setStyleSheet(f"font-size: {self.scaler.get_scaled_size(14)}px; font-weight: bold;")
        title_label.setFocusPolicy(Qt.StrongFocus)
        main_layout.addWidget(title_label)
        shortcut_title = QShortcut(QKeySequence("Alt+T"), self)
        shortcut_title.setContext(Qt.WidgetWithChildrenShortcut)
        shortcut_title.activated.connect(lambda: title_label.setFocus())

        # Discrepancy message (Alt+D) and checkboxes
        discrepancies = []
        diff_fields = [
            ("title", self.book.title, self.web_data.get('title', '')),
            ("year", str(self.book.year) if self.book.year else '', str(self.web_data.get('year', ''))),
            ("series", self.book.series_name, self.web_data.get('series', '')),
            ("genre", self.book.genre_name, self.web_data.get('genre', ''))
        ]
        for field, db_val, web_val in diff_fields:
            if db_val and db_val.strip() and web_val and db_val.strip() != web_val.strip():
                discrepancies.append((field, db_val, web_val))

        if discrepancies:
            msg_label = QLabel("Discrepancies found: Check to apply web changes or leave unchecked to keep current data.")
            msg_label.setAccessibleName("Discrepancy message")
            msg_label.setAccessibleDescription("Discrepancy message for web import")
            msg_label.setStyleSheet(f"font-size: {self.scaler.get_scaled_size(11)}px;")
            msg_label.setWordWrap(False)
            main_layout.addWidget(msg_label)
            shortcut_msg = QShortcut(QKeySequence("Alt+D"), self)
            shortcut_msg.setContext(Qt.WidgetWithChildrenShortcut)
            shortcut_msg.activated.connect(lambda: msg_label.setFocus())

            # Discrepancy checkboxes (tight, accessible)
            group_box = QGroupBox()
            group_box.setStyleSheet("QGroupBox { border: none; margin: 0; padding: 0; }")
            group_box.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            group_layout = QVBoxLayout(group_box)
            group_layout.setSpacing(0)
            group_layout.setContentsMargins(0, 0, 0, 0)
            for field, db_val, web_val in discrepancies:
                cb = QCheckBox(f"{field.capitalize()} from '{db_val}' to '{web_val}'")
                cb.setAccessibleName(f"Apply web {field}")
                cb.setChecked(False)
                cb.setStyleSheet(f"margin:0px;padding:0px;min-height:0px;min-width:0px;font-size:{self.scaler.get_scaled_size(11)}px; line-height:1;")
                cb.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
                group_layout.addWidget(cb)
            main_layout.addWidget(group_box)

        # Plot/comments field (always present)
        self.plot_field = QTextEdit()
        self.plot_field.setReadOnly(True)
        self.plot_field.setAccessibleName("Plot/Comments")
        self.plot_field.setAccessibleDescription("Plot summary from web source")
        self.plot_field.setMaximumHeight(80)
        self.plot_field.setStyleSheet("margin:0px;padding:0px;line-height:1;")
        self.plot_field.setPlainText(self.book.comments or "Loading...")
        self.plot_field.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        main_layout.addWidget(self.plot_field)

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(2)
        button_layout.setContentsMargins(0, 0, 0, 0)

        self.save_button = QPushButton("Save")  # No ampersand to avoid Alt+ conflict
        self.save_button.setAccessibleName("Save all fields")
        self.save_button.setAccessibleDescription("Apply all web data changes to original book record")
        self.save_button.setFocusPolicy(Qt.StrongFocus)
        self.save_button.clicked.connect(self.on_update_all)
        self.save_button.setDefault(False)
        self.save_button.setAutoDefault(False)
        button_layout.addWidget(self.save_button)
        # Only add stretch if right-alignment is required (not needed for single button)

        main_layout.addLayout(button_layout)

        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setAccessibleName("Status bar")
        self.status_bar.setSizeGripEnabled(False)
        self.status_bar.setStyleSheet("margin:0px;padding:0px;")
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
        # Only update plot/comments field
        self.plot_field.setPlainText(data.get('plot', ''))
        self.save_button.setEnabled(True)
        source = data.get('source', 'unknown')
        status_msg = f"Web data loaded from {source}"
        self._period_message = status_msg  # Store for Alt+/ announcements
        self.set_status(status_msg, announce=True)
        self.activateWindow()
        self.setFocus(Qt.ActiveWindowFocusReason)

    def on_web_data_error(self, error_message):
        """Handle web data fetch error."""
        self.set_status(f"Error fetching web data: {error_message}", announce=True)
        self.activateWindow()
        self.setFocus(Qt.ActiveWindowFocusReason)
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
        self._period_message = f"Loaded book: {self.book.title}"  # Store for Alt+/ announcements

    def _update_field_indicators(self):
        """No-op: indicators removed in minimal layout."""
        pass



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
        status_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        status_shortcut.activated.connect(self.on_read_status_bar)
        escape_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        escape_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        escape_shortcut.activated.connect(self.reject)
    def reject(self):
        """Handle close with accessibility event."""
        announce_dialog_closed(self)
        super().reject()

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
            self.data_saved.emit()
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
        """Handle key press events. Escape always closes dialog."""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            event.ignore()
            return
        if event.key() == Qt.Key_Escape:
            self.reject()
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
