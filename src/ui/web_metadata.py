
"""
Web Metadata Window - Built from PROVEN accessible skeleton
Accessibility works out of box: F1, Alt+/, Escape
"""

import sys
import os

# Add to project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QApplication, QStatusBar, 
    QLineEdit, QTextEdit, QSpinBox, QFormLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QCheckBox,
    QWidget, QSizePolicy, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QShortcut, QKeySequence, QAccessible

from src.accessibility.scaling import UIScaler
from src.accessibility.theme_manager import ThemeManager
from src.accessibility.accessible_events import announce_dialog_opened, announce_dialog_closed

from src.database import DatabaseManager, Book
from src.database.queries import BookQueries, AuthorQueries, SeriesQueries, GenreQueries
from src.web.web_book_api import WebBookAPI



class WebMetadataWindow(QDialog):
    """
    Web metadata window with PROVEN accessibility foundation.
    
    F1, Alt+/, and Escape work out of box.
    Built incrementally from accessible skeleton.
    """

    def __init__(self, db, book, scaler, theme_manager, parent=None, refresh_callback=None):
        # Always set parent_window, even if None
        self.parent_window = None
        from PySide6.QtWidgets import QMainWindow, QDialog
        if parent and (isinstance(parent, QMainWindow) or isinstance(parent, QDialog)):
            self.parent_window = parent
        super().__init__(parent)
        self.db = db
        self.book = book
        self.scaler = scaler
        self.theme_manager = theme_manager
        self.refresh_callback = refresh_callback
        self.setWindowTitle("Web Metadata")
        self.setModal(True)
        self.web_data = None
        self.field_differences = {}
        self.status_bar = QStatusBar()
        # Initialize query helpers
        self.book_queries = BookQueries(self.db) if self.db else None
        self.author_queries = AuthorQueries(self.db) if self.db else None
        self.series_queries = SeriesQueries(self.db) if self.db else None
        self.genre_queries = GenreQueries(self.db) if self.db else None
        # Main layout
        layout = QVBoxLayout(self)
        self.setup_ui(layout)
        self.apply_field_styling()
        # Add status bar at the bottom
        layout.addWidget(self.status_bar)
        # Theme is applied globally via ThemeManager; do not call apply_theme (private). If you want to change theme, use set_theme().
        self.setup_shortcuts()
        self.load_book_data()

    def setup_ui(self, layout):
        # Form layout for book details - EXACT backup match
        form_layout = QFormLayout()
        form_layout.setSpacing(3)  # Restore readable vertical spacing
        form_layout.setContentsMargins(20, 20, 20, 20)  # Restore original margins for readability

        # Set proper alignment for labels and fields
        form_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)


        # Helper to create a row with [checkbox][label][field][indicator]
        def add_checkbox_row(field, checkbox, label_text, buddy_field, accessible_name):
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(3)
            checkbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            checkbox.setAccessibleName(accessible_name)
            row_layout.addWidget(checkbox)
            label = QLabel(label_text)
            label.setBuddy(buddy_field)
            row_layout.addWidget(label)
            field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            row_layout.addWidget(field)
            # Add indicator (if present)
            indicator = QLabel("✓")
            # No accessible name for indicator
            indicator.setAccessibleDescription("This field contains web-fetched data")
            indicator.setStyleSheet("color: #2E8B57; font-weight: bold;")
            indicator.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            indicator.setAlignment(Qt.AlignCenter)
            row_layout.addWidget(indicator)
            # Store for later toggling
            row_widget._indicator = indicator
            row_widget._checkbox = checkbox
            return row_widget


        # Title
        self.title_edit = QLineEdit()
        self.title_edit.setAccessibleName("Title")
        self.title_edit.setAccessibleDescription("Book title from web source")
        self.title_checkbox = QCheckBox()
        self.title_checkbox.setChecked(False)
        self.title_field_container = add_checkbox_row(self.title_edit, self.title_checkbox, "&Title:", self.title_edit, "Update Title")
        form_layout.addRow(self.title_field_container)
        form_layout.setVerticalSpacing(2)  # Reduce vertical spacing for first rows

        # Author
        self.author_edit = QLineEdit()
        self.author_edit.setAccessibleName("Author")
        self.author_edit.setAccessibleDescription("Author name from web source")
        self.author_checkbox = QCheckBox()
        self.author_checkbox.setChecked(False)
        self.author_field_container = add_checkbox_row(self.author_edit, self.author_checkbox, "&Author:", self.author_edit, "Update Author")
        form_layout.addRow(self.author_field_container)
        form_layout.setVerticalSpacing(2)

        # Year
        self.year_edit = QLineEdit()
        self.year_edit.setAccessibleName("Publication year")
        self.year_edit.setAccessibleDescription("Publication year from web source")
        self.year_edit.setPlaceholderText("YYYY")
        self.year_checkbox = QCheckBox()
        self.year_checkbox.setChecked(False)
        self.year_field_container = add_checkbox_row(self.year_edit, self.year_checkbox, "&Year:", self.year_edit, "Update Year")
        form_layout.addRow(self.year_field_container)
        form_layout.setVerticalSpacing(6)  # Restore normal spacing after year

        # Series
        self.series_edit = QLineEdit()
        self.series_edit.setAccessibleName("Series")
        self.series_edit.setAccessibleDescription("Series name from web source")
        self.series_checkbox = QCheckBox()
        self.series_checkbox.setChecked(True)
        self.series_field_container = add_checkbox_row(self.series_edit, self.series_checkbox, "Ser&ies:", self.series_edit, "Update Series")
        form_layout.addRow(self.series_field_container)

        # Genre
        self.genre_edit = QLineEdit()
        self.genre_edit.setAccessibleName("Genre")
        self.genre_edit.setAccessibleDescription("Genre from web source")
        self.genre_checkbox = QCheckBox()
        self.genre_checkbox.setChecked(True)
        self.genre_field_container = add_checkbox_row(self.genre_edit, self.genre_checkbox, "&Genre:", self.genre_edit, "Update Genre")
        form_layout.addRow(self.genre_field_container)


        # Plot (no checkbox, only once)
        self.plot_edit = QTextEdit()
        self.plot_edit.setAccessibleName("Plot")
        self.plot_edit.setAccessibleDescription("Book plot/summary from web source")
        self.plot_edit.setMinimumHeight(self.scaler.get_scaled_size(60))
        plot_label = QLabel("&Plot:")
        plot_label.setBuddy(self.plot_edit)
        form_layout.addRow(plot_label, self.plot_edit)

        # Widen the form by 1/3 for accessibility
        min_width = int(self.scaler.get_scaled_size(400) * 4 / 3)
        self.setMinimumWidth(min_width)

        layout.addLayout(form_layout)

        # Buttons - match book_details styling
        button_layout = QHBoxLayout()

        # Save button only - match book_details style
        self.save_button = QPushButton("Save")
        self.save_button.setAccessibleName("Save")
        self.save_button.setAccessibleDescription("Save web metadata changes - Alt+S")
        self.save_button.setFocusPolicy(Qt.StrongFocus)
        self.save_button.clicked.connect(self.accept)
        button_layout.addWidget(self.save_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Apply book_details button styling
        scaled_height = self.scaler.get_scaled_size(22)
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
                    QPushButton:hover {{
                        background-color: palette(alternate-base);
                    }}
                """
        self.save_button.setStyleSheet(button_style)
    
    # ...existing code...
    def _create_field_with_indicator_and_checkbox(self, field, checkbox):
        """Create a field with web data difference indicator and a checkbox."""
        from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        checkbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout.addWidget(checkbox, 0)
        field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(field, 1)
        indicator = QLabel("✓")
        indicator.setAccessibleName("Web data indicator")
        indicator.setAccessibleDescription("This field contains web-fetched data")
        indicator.setStyleSheet("color: #2E8B57; font-weight: bold;")
        indicator.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        indicator.setAlignment(Qt.AlignCenter)
        layout.addWidget(indicator, 0)
        # Store reference for toggling visibility
        container._indicator = indicator
        container._checkbox = checkbox
        return container
    
    def apply_field_styling(self):
        """Apply field styling like backup window."""
        # Apply F1 popup style to fields
        from src.accessibility.shortcut_helpers import build_accessible_f1_popup_style
        field_style = build_accessible_f1_popup_style()
        
        for field in self.findChildren(QLineEdit):
            field.setStyleSheet(field_style)
        
        for field in self.findChildren(QTextEdit):
            field.setStyleSheet(field_style)
    
    def _create_field_with_indicator(self, field):
        """Create a field with web data difference indicator, left-aligned for accessibility."""
        from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Set container to expanding horizontally, fixed vertically
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # The actual field: expanding horizontally
        field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(field, 1)  # stretch=1

        # Difference indicator (check mark for web data): fixed size
        indicator = QLabel("✓")
        indicator.setAccessibleName("Web data indicator")
        indicator.setAccessibleDescription("This field contains web-fetched data")
        indicator.setStyleSheet("color: #2E8B57; font-weight: bold;")  # Sea green
        indicator.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        indicator.setAlignment(Qt.AlignCenter)
        layout.addWidget(indicator, 0)  # stretch=0

        return container
    
    def load_book_data(self):
        # Defensive: Ensure plot_edit exists before using it
        if not hasattr(self, 'plot_edit'):
            raise AttributeError("WebMetadataWindow: plot_edit is not initialized. Ensure setup_ui() is called before load_book_data().")
        """Load book data into fields and fetch web data."""
        if self.book:
            self.title_edit.setText(self.book.title or "")
            self.author_edit.setText(self.book.author_name or "")
            self.plot_edit.setPlainText(self.book.comments or "")
            self.year_edit.setText(str(self.book.year) if self.book.year else "")
            self.series_edit.setText(self.book.series_name or "")
            self.genre_edit.setText(self.book.genre_name or "")
        # Auto-fetch web data when window opens
        self.fetch_web_data()
    
    def fetch_web_data(self):
        """Fetch web data from API with status updates."""
        # No 'ready' or default status message

        # Get current book info
        title = self.book.title
        author = self.book.author_name
        year = str(self.book.year) if self.book.year else None

        # Use WebBookAPI for fetching with error handling
        api = WebBookAPI()
        try:
            web_data = api.get_book_metadata(title, author, year)
        except Exception as e:
            self.set_status(f"Error fetching web data: {str(e)}", announce=True)
            self.clear_web_indicators()
            return

        if web_data:
            self.update_fields_with_web_data(web_data)
            # Build status message: Plot Found/Not Found - Difference - ...
            plot_found = 'plot' in self.field_differences
            plot_status = "Plot Found" if plot_found else "Plot Not Found"
            diff_fields = [k.capitalize() for k in self.field_differences.keys() if k != 'plot']
            diff_str = f" - Difference - {', '.join(diff_fields)}" if diff_fields else ""
            msg = f"{plot_status}{diff_str}"
            self.set_status(msg, announce=True)
            if plot_found:
                self.plot_edit.setFocus()
        else:
            self.set_status("No web data found - book not matched", announce=True)
            self.clear_web_indicators()
    

    
    def generate_realistic_plot(self, title):
        """Generate a more realistic plot based on title keywords."""
        title_lower = title.lower()
        
        if 'bones' in title_lower:
            return "A chilling discovery of skeletal remains leads detective Charlie Parker on a journey into the past, uncovering secrets that were meant to stay buried forever."
        elif 'mystery' in title_lower:
            return "When a mysterious stranger arrives in town, long-buried secrets begin to surface, threatening to destroy the peaceful community."
        elif 'thriller' in title_lower:
            return "A fast-paced thriller that keeps readers on the edge of their seats as the protagonist races against time to prevent a catastrophic event."
        elif 'detective' in title_lower:
            return "A brilliant detective must use all their skills to solve a seemingly impossible case that has stumped everyone else."
        elif 'murder' in title_lower:
            return "A brutal murder rocks a small town, revealing dark secrets that everyone thought were long forgotten."
        else:
            return "A compelling story that explores the depths of human nature and the choices we make when faced with impossible situations."
    
    def update_fields_with_web_data(self, web_data):
        """Update UI fields with web data and track differences. Show checkboxes only for changed fields."""
        self.web_data = web_data
        changes_made = False
        self.field_differences = {}
        # Title (case-insensitive compare)
        if web_data.get('title') and (self.book.title is None or web_data['title'].strip().lower() != self.book.title.strip().lower()):
            self.title_edit.setText(web_data['title'])
            self.field_differences['title'] = web_data['title']
            self.show_indicator(self.title_edit, True, color='red')
            self.title_checkbox.setChecked(True)
        else:
            self.show_indicator(self.title_edit, False)
            self.title_checkbox.setChecked(False)
        # Author (case-insensitive compare)
        if web_data.get('author') and (self.book.author_name is None or web_data['author'].strip().lower() != self.book.author_name.strip().lower()):
            self.author_edit.setText(web_data['author'])
            self.field_differences['author'] = web_data['author']
            self.show_indicator(self.author_edit, True, color='red')
            self.author_checkbox.setChecked(True)
        else:
            self.show_indicator(self.author_edit, False)
            self.author_checkbox.setChecked(False)
        # Year (exact compare)
        if web_data.get('year') and str(web_data['year']) != self.year_edit.text():
            self.year_edit.setText(str(web_data['year']))
            self.field_differences['year'] = str(web_data['year'])
            self.show_indicator(self.year_edit, True, color='red')
            self.year_checkbox.setChecked(True)
        else:
            self.show_indicator(self.year_edit, False)
            self.year_checkbox.setChecked(False)
        # Series (case-insensitive compare)
        if web_data.get('series') and (self.book.series_name is None or web_data['series'].strip().lower() != self.book.series_name.strip().lower()):
            self.series_edit.setText(web_data['series'])
            self.field_differences['series'] = web_data['series']
            self.show_indicator(self.series_edit, True, color='red')
            self.series_checkbox.setChecked(True)
        else:
            self.show_indicator(self.series_edit, False)
            self.series_checkbox.setChecked(False)
        # Genre (case-insensitive compare)
        if web_data.get('genre') and (self.book.genre_name is None or web_data['genre'].strip().lower() != self.book.genre_name.strip().lower()):
            self.genre_edit.setText(web_data['genre'])
            self.field_differences['genre'] = web_data['genre']
            self.show_indicator(self.genre_edit, True, color='red')
            self.genre_checkbox.setChecked(True)
        else:
            self.show_indicator(self.genre_edit, False)
            self.genre_checkbox.setChecked(False)
        # Plot (no indicator as requested)
        if web_data.get('plot') and web_data['plot'] != self.book.comments:
            self.plot_edit.setPlainText(web_data['plot'])
            self.field_differences['plot'] = 'found'
            changes_made = True
        return changes_made
    
    # Removed: show_changes_popup (was for testing only)
    
    def show_indicator(self, field, show, color=None):
        """Show or hide the web data indicator and checkbox for a field. Color: 'green' or 'red'."""
        # Find the indicator label in the field's container
        container = None
        if field is self.title_edit:
            container = self.title_field_container
        elif field is self.author_edit:
            container = self.author_field_container
        elif field is self.year_edit:
            container = self.year_field_container
        elif field is self.series_edit:
            container = self.series_field_container
        elif field is self.genre_edit:
            container = self.genre_field_container
        if container:
            # Toggle indicator and checkbox visibility
            if hasattr(container, '_indicator'):
                container._indicator.setVisible(show)
                if show and color:
                    if color == 'red':
                        container._indicator.setStyleSheet("color: #C0392B; font-weight: bold;")
                    elif color == 'green':
                        container._indicator.setStyleSheet("color: #2E8B57; font-weight: bold;")
            if hasattr(container, '_checkbox'):
                container._checkbox.setVisible(show)
    
    def clear_web_indicators(self):
        """Clear all web data indicators."""
        self.show_indicator(self.title_edit, False)
        self.show_indicator(self.author_edit, False)
        self.show_indicator(self.year_edit, False)
        self.show_indicator(self.series_edit, False)
        self.show_indicator(self.genre_edit, False)
    
    def show_changes_popup(self, web_data):
        """Show popup with only the fields that changed."""
        changes = []
        
        if web_data.get('title') and web_data['title'] != self.book.title:
            changes.append(f"Title: {web_data['title']}")
        
        if web_data.get('author') and web_data['author'] != self.book.author_name:
            changes.append(f"Author: {web_data['author']}")
        
        if web_data.get('year') and web_data['year'] != self.book.year:
            changes.append(f"Year: {web_data['year']}")
        
        if web_data.get('series') or web_data.get('series_number'):
            series_text = web_data.get('series', '')
            if web_data.get('series_number'):
                series_text = f"{series_text} - {web_data['series_number']}"
            changes.append(f"Series: {series_text}")
        
        if web_data.get('genre') and web_data['genre'] != self.book.genre_name:
            changes.append(f"Genre: {web_data['genre']}")
        
        # For plot, just show "Found" or "Not found" as requested
        if web_data.get('plot'):
            changes.append("Plot: Found")
        
        if changes:
            from PySide6.QtWidgets import QMessageBox
            from src.accessibility.style_helpers import exec_styled_message_box, build_accessible_message_box_style
            changes_text = "\n".join(changes)
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Information,
                title="Web Data Updates",
                text=f"The following fields were updated from web data:\n\n{changes_text}"
            )
    
    def setup_shortcuts(self):
        """
        PROVEN accessibility shortcuts + field shortcuts.
        F1, Alt+/, Escape work out of box.
        """
        # F1 - local shortcut (PROVEN working)
        self.help_shortcut = QShortcut(QKeySequence("F1"), self)
        self.help_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.help_shortcut.activated.connect(self.on_show_shortcuts)
        
        # Escape - local shortcut (PROVEN working)
        self.close_shortcut = QShortcut(QKeySequence("Escape"), self)
        self.close_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.close_shortcut.activated.connect(self.reject)
        
        # Alt+/ - local shortcut (PROVEN working)
        self.read_status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.read_status_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.read_status_shortcut.activated.connect(self.on_read_status_bar)
        
        # Field shortcuts
        self.title_shortcut = QShortcut(QKeySequence("Alt+T"), self)
        self.title_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.title_shortcut.activated.connect(lambda: self.title_edit.setFocus())
        
        self.author_shortcut = QShortcut(QKeySequence("Alt+A"), self)
        self.author_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.author_shortcut.activated.connect(lambda: self.author_edit.setFocus())
        
        self.plot_shortcut = QShortcut(QKeySequence("Alt+P"), self)
        self.plot_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.plot_shortcut.activated.connect(lambda: self.plot_edit.setFocus())
        
        self.year_shortcut = QShortcut(QKeySequence("Alt+Y"), self)
        self.year_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.year_shortcut.activated.connect(lambda: self.year_spin.setFocus())
        
        self.series_shortcut = QShortcut(QKeySequence("Alt+I"), self)
        self.series_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.series_shortcut.activated.connect(lambda: self.series_edit.setFocus())
        
        self.genre_shortcut = QShortcut(QKeySequence("Alt+G"), self)
        self.genre_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.genre_shortcut.activated.connect(lambda: self.genre_edit.setFocus())
        
        self.save_shortcut = QShortcut(QKeySequence("Alt+S"), self)
        self.save_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.save_shortcut.activated.connect(lambda: self.save_button.click())
    
    def on_show_shortcuts(self):
        """F1 shortcut - show help with standard table format."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Keyboard Shortcuts - Web Details")
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

        font = table.font()
        font.setPointSize(self.scaler.get_scaled_size(11))
        table.setFont(font)
        layout.addWidget(table)

        QTimer.singleShot(0, lambda: table.setFocus(Qt.TabFocusReason))
        dlg.exec()
    
    def on_read_status_bar(self):
        """Alt+/ shortcut - read status."""
        status_text = self.status_bar.currentMessage()
        from src.accessibility.style_helpers import exec_styled_message_box, build_accessible_message_box_style
        if QAccessible.isActive():
            self.set_status(status_text, announce=True)
        else:
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Information,
                title="Alt+/ Test",
                text=f"Alt+/ working! Status: {status_text}"
            )
    
    def set_status(self, message: str, announce: bool = False):
        """Set status message."""
        self.status_bar.showMessage(message)
        if announce:
            from src.accessibility.accessible_events import announce_status_message
            announce_status_message(self.status_bar, message, move_focus=True)
    
    def accept(self):
        """Save and accept - update database and refresh book details, with plot field formatted as requested."""
        # Build list of differences for status bar
        diff_fields = [k.capitalize() for k in self.field_differences.keys() if k != 'plot']
        plot_found = 'plot' in self.field_differences
        plot_status = "Plot Found" if plot_found else "Plot Not Found"
        diff_str = f" - Difference - {', '.join(diff_fields)}" if diff_fields else ""
        self.set_status(f"{plot_status}{diff_str}")

        if self.book and self.db:
            try:
                # Only apply web data for checked fields
                # Title
                if self.title_checkbox.isVisible() and self.title_checkbox.isChecked():
                    self.book.title = self.title_edit.text().strip()
                # Author
                if self.author_checkbox.isVisible() and self.author_checkbox.isChecked():
                    author_name = self.author_edit.text().strip()
                    if author_name:
                        author = self.author_queries.get_by_name(author_name)
                        if not author:
                            author_id = self.author_queries.insert(author_name)
                        else:
                            author_id = author.author_id
                        self.book.author_id = author_id
                # Year
                if self.year_checkbox.isVisible() and self.year_checkbox.isChecked():
                    year_text = self.year_edit.text().strip()
                    try:
                        self.book.year = int(year_text) if year_text else None
                    except ValueError:
                        self.book.year = None
                # Series
                if self.series_checkbox.isVisible() and self.series_checkbox.isChecked():
                    series_text = self.series_edit.text().strip()
                    series_id = None
                    series_number = None
                    if series_text:
                        if " - " in series_text:
                            parts = series_text.split(" - ")
                            series_name = parts[0].strip()
                            try:
                                series_number = int(parts[1].strip())
                            except ValueError:
                                series_number = None
                        else:
                            series_name = series_text
                        if series_name:
                            series = self.series_queries.get_by_name(series_name)
                            if not series:
                                series_id = self.series_queries.insert(series_name)
                            else:
                                series_id = series.series_id
                        self.book.series_id = series_id
                        self.book.series_number = series_number
                # Genre
                if self.genre_checkbox.isVisible() and self.genre_checkbox.isChecked():
                    genre_name = self.genre_edit.text().strip()
                    genre_id = None
                    if genre_name:
                        genre = self.genre_queries.get_by_name(genre_name)
                        if not genre:
                            genre_id = self.genre_queries.insert(genre_name)
                        else:
                            genre_id = genre.genre_id
                        self.book.genre_id = genre_id

                # Plot/comments always applied
                plot = self.plot_edit.toPlainText().strip()
                rating_line = ""
                source_line = ""
                publisher_line = ""
                web_data = getattr(self, 'web_data', None)
                if web_data:
                    rating = web_data.get('rating')
                    ratings_count = web_data.get('ratings_count')
                    source = web_data.get('source')
                    publisher = web_data.get('publisher')
                    if rating:
                        try:
                            rating_val = float(rating)
                            rating_str = f"{rating_val:.1f}"
                        except (ValueError, TypeError):
                            rating_str = str(rating)
                        if ratings_count:
                            try:
                                count_val = int(ratings_count)
                                count_str = f"{count_val} reviews"
                            except (ValueError, TypeError):
                                count_str = f"{ratings_count} reviews"
                            rating_line = f"Rating {rating_str} ({count_str})"
                        else:
                            rating_line = f"Rating {rating_str}"
                    if source:
                        source_line = f"Plot Source: {source}"
                    if publisher:
                        publisher_line = f"Publisher: {publisher}"
                # Build the new plot/comments field: rating and source on same line at top, publisher at end
                plot_lines = []
                header_line = ""
                if rating_line and source_line:
                    header_line = f"{rating_line} | {source_line}"
                elif rating_line:
                    header_line = rating_line
                elif source_line:
                    header_line = source_line
                if header_line:
                    plot_lines.append(header_line)
                if plot:
                    if header_line:
                        plot_lines.append("")  # blank line before plot if header present
                    plot_lines.append(plot)
                if publisher_line:
                    if plot_lines:
                        plot_lines.append("")  # blank line before publisher if plot or header present
                    plot_lines.append(publisher_line)
                new_plot = "\n".join(plot_lines).strip()
                self.book.comments = new_plot

                # Save to database
                self.book_queries.update(self.book)

                # Always call refresh callback to auto-save in book details
                if self.refresh_callback:
                    print(f"DEBUG: Before refresh - dirty: {getattr(self.parent_window, '_dirty', 'N/A')}")
                    self.refresh_callback()  # This loads the data (may set dirty flag)
                    print(f"DEBUG: After refresh - dirty: {getattr(self.parent_window, '_dirty', 'N/A')}")
                    
                    if web_data:
                        # Also call save to persist changes
                        if hasattr(self.parent_window, 'on_save'):
                            self.parent_window.on_save()
                            print(f"DEBUG: After on_save - dirty: {getattr(self.parent_window, '_dirty', 'N/A')}")
                    
                    # Clear dirty state using the proper method
                    if hasattr(self.parent_window, '_clear_dirty'):
                        self.parent_window._clear_dirty(preserve_status=True)
                        print(f"DEBUG: After _clear_dirty - dirty: {getattr(self.parent_window, '_dirty', 'N/A')}")
                    # Force clear dirty flag one more time
                    if hasattr(self.parent_window, '_dirty'):
                        self.parent_window._dirty = False
                        print(f"DEBUG: Force clear dirty - dirty: {getattr(self.parent_window, '_dirty', 'N/A')}")
                    # Update save button visibility
                    if hasattr(self.parent_window, '_update_save_button_visibility'):
                        self.parent_window._update_save_button_visibility()
                    # Force UI update
                    if hasattr(self.parent_window, 'repaint'):
                        self.parent_window.repaint()

                announce_dialog_closed(self)
                super().accept()

            except Exception as e:
                self.set_status(f"Error saving: {str(e)}")
                # Don't close on error
                return
        else:
            # No book or database - just close
            announce_dialog_closed(self)
            super().accept()
    
    def reject(self):
        """Handle close - discard changes as requested."""
        announce_dialog_closed(self)
        super().reject()


def test_web_metadata():
    """Test web metadata window with proven accessibility."""
    app = QApplication(sys.argv)
    # Create dummy objects for testing
    from src.accessibility.scaling import UIScaler
    from src.accessibility.theme_manager import ThemeManager
    app_instance = QApplication.instance()
    scaler = UIScaler(app_instance)
    theme_manager = ThemeManager(app_instance)
    
    # Create dummy book
    from src.database import Book
    book = Book(
        title="Test Book Title",
        author_name="Test Author Name",
        comments="Test plot description here",
        year=2023,
        series_name="Test Series",
        genre_name="Test Genre"
    )
    
    window = WebMetadataWindow(
        db=None, 
        book=book, 
        scaler=scaler, 
        theme_manager=theme_manager,
        refresh_callback=None  # No callback needed for test
    )
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(test_web_metadata())
