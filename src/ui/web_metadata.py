
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
from PySide6.QtCore import Qt, QTimer, Signal, QEvent
from PySide6.QtGui import QShortcut, QKeySequence, QAccessible

from src.accessibility.scaling import UIScaler
from src.accessibility.theme_manager import ThemeManager
from src.accessibility.accessible_events import announce_dialog_opened, announce_dialog_closed
from src.accessibility.key_filters import is_unmapped_alt_letter

from src.database import DatabaseManager, Book
from src.database.queries import BookQueries, AuthorQueries, SeriesQueries, GenreQueries
from src.web.web_book_api import WebBookAPI




class WebMetadataWindow(QDialog):
    """
    Web metadata window with PROVEN accessibility foundation.
    
    F1, Alt+/, and Escape work out of box.
    Built incrementally from accessible skeleton.
    """

    # List of allowed Alt+key shortcuts for Web Metadata
    ALLOWED_ALT_KEYS = {'T', 'A', 'P', 'Y', 'I', 'G', 'S', '/', '?', 'F1'}

    # Signal emitted when data is saved
    data_saved = Signal()

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
        # Make window wider for proper plot field letterbox shape
        self.resize(800, 600)
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
        # Theme is applied globally via ThemeManager; do not call apply_theme (private). If you want to change theme, use set_theme().
        self.setup_shortcuts()
        # Add status bar at the very bottom (after all layouts)
        layout.addWidget(self.status_bar)
        self.load_book_data()
        
        # Install event filter for Alt-letter hygiene
        self.installEventFilter(self)
        
        # CRITICAL: Set focus to first field with web differences when window opens
        # JAWS requires focus to be set for Alt+keys to work properly
        QTimer.singleShot(0, self.set_focus_to_first_differing_field)

    def eventFilter(self, source, event):
        """Event filter to enforce Alt-letter hygiene and block unmapped Alt keys."""
        if event.type() == QEvent.KeyPress:
            key = event.key()
            modifiers = event.modifiers()
            
            # Block unused Alt+letter keys using the allowlist
            if is_unmapped_alt_letter(event, self.ALLOWED_ALT_KEYS):
                QApplication.beep()
                return True  # Consume the event
                
        return super().eventFilter(source, event)


    def setup_ui(self, layout):
        # Main layout with two-column structure
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # Removed header text boxes (Current, From Web) as per user request

        # Helper to create a two-column row with checkbox
        def create_two_column_row(label_text, current_edit, web_edit, checkbox):
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(10)

            # Left column - Current data
            left_label = QLabel(label_text)
            left_label.setMinimumWidth(80)
            left_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            row_layout.addWidget(left_label)

            current_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            row_layout.addWidget(current_edit)

            # Right column - Web data label (initially hidden)
            web_label = QLabel("Web")
            web_label.setMinimumWidth(80)
            web_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            web_label.setVisible(False)
            row_layout.addWidget(web_label)

            web_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            web_edit.setVisible(False)
            row_layout.addWidget(web_edit)

            # Checkbox
            checkbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            checkbox.setVisible(False)
            row_layout.addWidget(checkbox)

            # Indicator (for show_indicator logic)
            indicator = QLabel("✓")
            indicator.setAccessibleName("Web data indicator")
            indicator.setAccessibleDescription("This field contains web-fetched data")
            indicator.setStyleSheet("color: #2E8B57; font-weight: bold;")
            indicator.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            indicator.setAlignment(Qt.AlignCenter)
            indicator.setVisible(False)
            row_layout.addWidget(indicator)

            # Store reference for toggling
            row_widget._web_label = web_label
            row_widget._web_edit = web_edit
            row_widget._checkbox = checkbox
            row_widget._indicator = indicator
            return row_widget

        # Title fields
        self.title_edit = QLineEdit()
        self.title_edit.setAccessibleName("Current Title")
        self.title_edit.setAccessibleDescription("Current book title")
        self.title_web_edit = QLineEdit()
        self.title_web_edit.setAccessibleName("Web Title")
        self.title_web_edit.setAccessibleDescription("Book title from web source")
        self.title_web_edit.setReadOnly(True)
        self.title_checkbox = QCheckBox()
        self.title_checkbox.setAccessibleName("Keep Web Title")
        self.title_checkbox.setAccessibleDescription("Apply web title to current book")
        self.title_checkbox.setChecked(False)
        title_row = create_two_column_row("Title:", self.title_edit, self.title_web_edit, self.title_checkbox)
        self.title_row = title_row
        self.main_layout.addWidget(title_row)

        # Author fields
        self.author_edit = QLineEdit()
        self.author_edit.setAccessibleName("Current Author")
        self.author_edit.setAccessibleDescription("Current author name")
        self.author_web_edit = QLineEdit()
        self.author_web_edit.setAccessibleName("Web Author")
        self.author_web_edit.setAccessibleDescription("Author name from web source")
        self.author_web_edit.setReadOnly(True)
        self.author_checkbox = QCheckBox()
        self.author_checkbox.setAccessibleName("Keep Web Author")
        self.author_checkbox.setAccessibleDescription("Apply web author to current book")
        self.author_checkbox.setChecked(False)
        author_row = create_two_column_row("Author:", self.author_edit, self.author_web_edit, self.author_checkbox)
        self.author_row = author_row
        self.main_layout.addWidget(author_row)

        # Year fields
        self.year_edit = QLineEdit()
        self.year_edit.setAccessibleName("Current Year")
        self.year_edit.setAccessibleDescription("Current publication year")
        self.year_edit.setPlaceholderText("YYYY")
        self.year_edit.setObjectName("year_edit")
        self.year_web_edit = QLineEdit()
        self.year_web_edit.setAccessibleName("Web Year")
        self.year_web_edit.setAccessibleDescription("Publication year from web source")
        self.year_web_edit.setPlaceholderText("YYYY")
        self.year_web_edit.setReadOnly(True)
        self.year_checkbox = QCheckBox()
        self.year_checkbox.setAccessibleName("Keep Web Year")
        self.year_checkbox.setAccessibleDescription("Apply web year to current book")
        self.year_checkbox.setChecked(False)
        self.year_checkbox.setShortcut("Alt+Y")
        year_row = create_two_column_row("Year (Alt+Y):", self.year_edit, self.year_web_edit, self.year_checkbox)
        self.year_row = year_row
        self.main_layout.addWidget(year_row)

        # Series fields
        self.series_edit = QLineEdit()
        self.series_edit.setAccessibleName("Current Series")
        self.series_edit.setAccessibleDescription("Current series name")
        self.series_web_edit = QLineEdit()
        self.series_web_edit.setAccessibleName("Web Series")
        self.series_web_edit.setAccessibleDescription("Series name from web source")
        self.series_web_edit.setReadOnly(True)
        self.series_checkbox = QCheckBox()
        self.series_checkbox.setAccessibleName("Keep Web Series")
        self.series_checkbox.setAccessibleDescription("Apply web series to current book")
        self.series_checkbox.setChecked(False)
        series_row = create_two_column_row("Series:", self.series_edit, self.series_web_edit, self.series_checkbox)
        self.series_row = series_row
        self.main_layout.addWidget(series_row)


        # Genre fields
        self.genre_edit = QLineEdit()
        self.genre_edit.setAccessibleName("Current Genre")
        self.genre_edit.setAccessibleDescription("Current genre")
        self.genre_web_edit = QLineEdit()
        self.genre_web_edit.setAccessibleName("Web Genre")
        self.genre_web_edit.setAccessibleDescription("Genre from web source")
        self.genre_web_edit.setReadOnly(True)
        self.genre_checkbox = QCheckBox()
        self.genre_checkbox.setAccessibleName("Keep Web Genre")
        self.genre_checkbox.setAccessibleDescription("Apply web genre to current book")
        self.genre_checkbox.setChecked(False)
        genre_row = create_two_column_row("&Genre:", self.genre_edit, self.genre_web_edit, self.genre_checkbox)
        self.genre_row = genre_row
        self.main_layout.addWidget(genre_row)

        # Plot field (always present, below two-column layout)
        self.plot_edit = QTextEdit()
        self.plot_edit.setReadOnly(True)
        self.plot_edit.setAccessibleName("Plot Summary")
        self.plot_edit.setAccessibleDescription("Plot summary from web source")
        self.plot_edit.setMinimumHeight(40)  # Like book_details
        self.plot_edit.setTabChangesFocus(True)
        self.plot_edit.textChanged.connect(self._adjust_plot_height)
        plot_label = QLabel("Plot:")
        plot_label.setMinimumWidth(80)
        plot_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        plot_row = QWidget()
        plot_layout = QHBoxLayout(plot_row)
        plot_layout.setContentsMargins(0, 0, 0, 0)
        plot_layout.setSpacing(10)
        plot_layout.addWidget(plot_label)
        plot_layout.addWidget(self.plot_edit)
        self.plot_row = plot_row  # Store reference for hiding/showing
        self.main_layout.addWidget(plot_row)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save")
        self.save_button.setAccessibleName("Save web metadata")
        self.save_button.setAccessibleDescription("Save changes - Alt+S")
        self.save_button.setFocusPolicy(Qt.StrongFocus)
        self.save_button.setDefault(False)
        self.save_button.setAutoDefault(False)
        self.save_button.clicked.connect(self.on_save_clicked)
        button_layout.addWidget(self.save_button)
        
        button_layout.addStretch()
        
        self.main_layout.addLayout(button_layout)
        
        # CRITICAL: Add the main_layout to the window layout
        layout.addLayout(self.main_layout)

    def _adjust_plot_height(self):
        """Adjust plot QTextEdit height to fit content (modeled after book_details)."""
        text = self.plot_edit.toPlainText().strip()
        if not text:
            self.plot_edit.setFixedHeight(25)
            return
        doc = self.plot_edit.document()
        doc.setTextWidth(self.plot_edit.viewport().width())
        doc_height = doc.size().height()
        margins = self.plot_edit.contentsMargins()
        frame_width = self.plot_edit.frameWidth() * 2
        needed_height = int(doc_height + margins.top() + margins.bottom() + frame_width + 5)
        new_height = max(40, min(400, needed_height))  # Increased max height from 200 to 400
        self.plot_edit.setFixedHeight(new_height)
    
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
        """Load book data into fields and fetch web data."""
        if self.book:
            self.title_edit.setText(self.book.title or "")
            self.author_edit.setText(self.book.author_name or "")
            self.year_edit.setText(str(self.book.year) if self.book.year else "")
            self.series_edit.setText(self.book.series_name or "")
            self.genre_edit.setText(self.book.genre_name or "")
            self.plot_edit.setPlainText(self.book.comments or "")
            
            # Show plot row if book has existing plot data, hide if empty
            if self.book.comments and self.book.comments.strip():
                self.plot_row.setVisible(True)
            else:
                self.plot_row.setVisible(False)

            # Initialize web fields and labels as hidden
            for row in [self.title_row, self.author_row, self.year_row, self.series_row, self.genre_row]:
                row._web_label.setVisible(False)
                row._web_edit.setVisible(False)
                row._checkbox.setVisible(False)

        # Auto-fetch web data when window opens
        self.fetch_web_data()
    
    def set_focus_to_first_differing_field(self):
        """Set focus to first field that has web differences, fallback to plot."""
        # Check fields in order: title, author, year, series, genre
        field_order = [
            (self.title_edit, 'title'),
            (self.author_edit, 'author'),
            (self.year_edit, 'year'),
            (self.series_edit, 'series'),
            (self.genre_edit, 'genre')
        ]
        
        # Find first field with differences
        for field, field_name in field_order:
            if field_name in self.field_differences:
                field.setFocus()
                return
        
        # No differences found, focus on plot
        self.plot_edit.setFocus()
    
    def fetch_web_data(self):
        """Fetch web data from API with status updates."""
        # Check if parent is book_details and use current form values if so
        parent_is_book_details = (self.parent_window and 
                                hasattr(self.parent_window, '__class__') and 
                                'book_details' in str(type(self.parent_window).__module__).lower())
        
        if parent_is_book_details and hasattr(self.parent_window, 'title_edit'):
            # Use current values from book_details form (user may have edited them)
            title = self.parent_window.title_edit.text().strip()
            author = self.parent_window.author_combo.currentText().strip()
            year_value = self.parent_window.year_spin.value()
            year = None if year_value == self.parent_window.year_spin.minimum() else str(year_value)
        else:
            # Use database values (main window or fallback)
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
            # Build status message: Difference - ...
            diff_fields = [k.capitalize() for k in self.field_differences.keys()]
            diff_str = f" - Difference - {', '.join(diff_fields)}" if diff_fields else ""
            msg = f"Web data found{diff_str}"
            self.set_status(msg, announce=True)
        else:
            # No web data found - show popup and close window
            from src.accessibility.style_helpers import exec_styled_message_box
            title_text = title or "Unknown Title"
            author_text = author or "Unknown Author"
            message_text = f"No web data found for:\n\n{title_text} by {author_text}"
            
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Information,
                title="Web Search",
                text=message_text,
                buttons=QMessageBox.Ok,
                default_button=QMessageBox.Ok
            )
            self.clear_web_indicators()
            # Close the window - user can edit in book_details and try again
            QTimer.singleShot(0, self.close)
    
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
        """Update UI fields with web data and track differences. Show web columns and checkboxes only for changed fields."""
        self.web_data = web_data
        self.field_differences = {}
        
        # Helper to handle field comparison and visibility
        def handle_field_comparison(web_value, current_value, web_edit, checkbox, field_name, row_widget):
            current_str = str(current_value).strip() if current_value is not None else ""
            web_str = str(web_value).strip() if web_value is not None else ""
            
            if web_value and (current_value is None or current_str == ""):
                # DB field is empty and web data exists - show web data but hide checkbox (auto-applied)
                web_edit.setText(web_str)
                row_widget._web_label.setVisible(True)   # Show web column so user can see the data
                row_widget._web_edit.setVisible(True)    # Show web data
                row_widget._checkbox.setVisible(False)   # Hide checkbox (not needed for empty DB fields)
                checkbox.setVisible(False)               # Also hide checkbox directly
                self.field_differences[field_name] = web_str
                return True
            elif web_value and current_value is not None and current_str != "" and web_str.lower() != current_str.lower():
                # Data differs and DB field is NOT empty - show web column and checkbox
                web_edit.setText(web_str)
                row_widget._web_label.setVisible(True)
                row_widget._web_edit.setVisible(True)
                row_widget._checkbox.setVisible(True)
                checkbox.setChecked(True)
                self.field_differences[field_name] = web_str
                return True
            else:
                # Data is same or no web data - hide web column and checkbox
                row_widget._web_label.setVisible(False)
                row_widget._web_edit.setVisible(False)
                row_widget._checkbox.setVisible(False)
                checkbox.setChecked(False)
                return False
        
        # Title
        handle_field_comparison(
            web_data.get('title'), 
            self.book.title, 
            self.title_web_edit, 
            self.title_checkbox, 
            'title',
            self.title_row
        )
        
        # Author
        handle_field_comparison(
            web_data.get('author'), 
            self.book.author_name, 
            self.author_web_edit, 
            self.author_checkbox, 
            'author',
            self.author_row
        )
        
        # Year
        handle_field_comparison(
            web_data.get('year'), 
            self.book.year, 
            self.year_web_edit, 
            self.year_checkbox, 
            'year',
            self.year_row
        )
        
        # Series
        handle_field_comparison(
            web_data.get('series'), 
            self.book.series_name, 
            self.series_web_edit, 
            self.series_checkbox, 
            'series',
            self.series_row
        )
        
        # Genre
        handle_field_comparison(
            web_data.get('genre'), 
            self.book.genre_name, 
            self.genre_web_edit, 
            self.genre_checkbox, 
            'genre',
            self.genre_row
        )
        
        # Plot (update plot field with web data)
        if web_data.get('plot'):
            plot = web_data['plot']
            rating_line = ""
            source_line = ""
            publisher_line = ""
            
            # Extract rating, source, and publisher from web data
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
            
            # Build the plot display: rating and source on same line at top, publisher at end
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
                plot_lines.append(plot)
            if publisher_line:
                plot_lines.append(publisher_line)
            
            # Remove any blank lines between sections
            formatted_plot = "\n".join([line for line in plot_lines if line.strip() != ""]).strip()
            self.plot_edit.setPlainText(formatted_plot)
            self.field_differences['plot'] = 'found'
            # Show plot row when data is available
            self.plot_row.setVisible(True)
        else:
            # Hide plot row when no plot data is available
            self.plot_row.setVisible(False)
    
    # Removed: show_changes_popup (was for testing only)
    
    def show_indicator(self, field, show, color=None):
        """Show or hide the web data indicator and checkbox for a field. Color: 'green' or 'red'."""
        # Find the indicator label in the field's container
        container = None
        if field is self.title_edit:
            container = self.title_row
        elif field is self.author_edit:
            container = self.author_row
        elif field is self.year_edit:
            container = self.year_row
        elif field is self.series_edit:
            container = self.series_row
        elif field is self.genre_edit:
            container = self.genre_row
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
        
        # Escape - local shortcut with confirmation if web data present
        self.close_shortcut = QShortcut(QKeySequence("Escape"), self)
        self.close_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.close_shortcut.activated.connect(self.on_escape_pressed)
        
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
        self.year_shortcut.activated.connect(lambda: self.year_edit.setFocus())
        
        self.series_shortcut = QShortcut(QKeySequence("Alt+I"), self)
        self.series_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.series_shortcut.activated.connect(lambda: self.series_edit.setFocus())
        
        self.genre_shortcut = QShortcut(QKeySequence("Alt+G"), self)
        self.genre_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.genre_shortcut.activated.connect(lambda: self.genre_edit.setFocus())
        
        self.save_shortcut = QShortcut(QKeySequence("Alt+S"), self)
        self.save_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.save_shortcut.activated.connect(
            lambda: self.on_save_clicked() if self.save_button.isVisible() else None)
    
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

    def on_escape_pressed(self):
        """Handle escape key - show save confirmation before closing."""
        from src.accessibility.style_helpers import exec_styled_message_box
        
        reply = exec_styled_message_box(
            self,
            self.scaler.get_scaled_size(20),
            icon=QMessageBox.Question,
            title="Confirm Save",
            text="Save web data?",
            buttons=QMessageBox.Yes | QMessageBox.No,
            default_button=QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            self.accept()  # Save and close
        elif reply == QMessageBox.No:
            announce_dialog_closed(self)
            # Return focus to parent window's table if available
            if self.parent_window and hasattr(self.parent_window, 'table'):
                # Use QTimer to ensure focus is set after dialog closes
                QTimer.singleShot(0, lambda: self.parent_window._restore_table_focus(
                    self.parent_window.table.currentRow(), 
                    self.parent_window.table.currentColumn()
                ))
            super().reject()  # Close without saving

    def on_save_clicked(self):
        """Handle save button click - save and close without confirmation."""
        self.accept()  # Save and close directly

    def accept(self):
        """Save and accept - update database with web data based on checkbox selection and auto-apply logic."""
        # Build list of applied fields for status bar
        applied_fields = []
        
        if self.book and self.db:
            try:
                # Apply web data based on field differences and checkbox state
                # Title
                if 'title' in self.field_differences:
                    if self.title_row._checkbox.isVisible():
                        # Field differs - apply if checked
                        if self.title_checkbox.isChecked():
                            self.book.title = self.title_web_edit.text().strip()
                            applied_fields.append('Title')
                    else:
                        # DB field was empty - auto-apply web data
                        self.book.title = self.title_web_edit.text().strip()
                        applied_fields.append('Title')
                
                # Author
                if 'author' in self.field_differences:
                    if self.author_row._checkbox.isVisible():
                        # Field differs - apply if checked
                        if self.author_checkbox.isChecked():
                            author_name = self.author_web_edit.text().strip()
                            if author_name:
                                author = self.author_queries.get_by_name(author_name)
                                if not author:
                                    author_id = self.author_queries.insert(author_name)
                                else:
                                    author_id = author.author_id
                                self.book.author_id = author_id
                                applied_fields.append('Author')
                    else:
                        # DB field was empty - auto-apply web data
                        author_name = self.author_web_edit.text().strip()
                        if author_name:
                            author = self.author_queries.get_by_name(author_name)
                            if not author:
                                author_id = self.author_queries.insert(author_name)
                            else:
                                author_id = author.author_id
                            self.book.author_id = author_id
                            applied_fields.append('Author')
                
                # Year
                if 'year' in self.field_differences:
                    if self.year_row._checkbox.isVisible():
                        # Field differs - apply if checked
                        if self.year_checkbox.isChecked():
                            year_text = self.year_web_edit.text().strip()
                            try:
                                self.book.year = int(year_text) if year_text else None
                                applied_fields.append('Year')
                            except ValueError:
                                self.book.year = None
                    else:
                        # DB field was empty - auto-apply web data
                        year_text = self.year_web_edit.text().strip()
                        try:
                            self.book.year = int(year_text) if year_text else None
                            applied_fields.append('Year')
                        except ValueError:
                            self.book.year = None
                
                # Series
                if 'series' in self.field_differences:
                    if self.series_row._checkbox.isVisible():
                        # Field differs - apply if checked
                        if self.series_checkbox.isChecked():
                            series_text = self.series_web_edit.text().strip()
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
                            applied_fields.append('Series')
                    else:
                        # DB field was empty - auto-apply web data
                        series_text = self.series_web_edit.text().strip()
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
                        applied_fields.append('Series')
                
                # Genre
                if 'genre' in self.field_differences:
                    if self.genre_row._checkbox.isVisible():
                        # Field differs - apply if checked
                        if self.genre_checkbox.isChecked():
                            genre_name = self.genre_web_edit.text().strip()
                            if genre_name:
                                genre = self.genre_queries.get_by_name(genre_name)
                                if not genre:
                                    genre_id = self.genre_queries.insert(genre_name)
                                else:
                                    genre_id = genre.genre_id
                                self.book.genre_id = genre_id
                                applied_fields.append('Genre')
                    else:
                        # DB field was empty - auto-apply web data
                        genre_name = self.genre_web_edit.text().strip()
                        if genre_name:
                            genre = self.genre_queries.get_by_name(genre_name)
                            if not genre:
                                genre_id = self.genre_queries.insert(genre_name)
                            else:
                                genre_id = genre.genre_id
                            self.book.genre_id = genre_id
                            applied_fields.append('Genre')

                # Plot
                if 'plot' in self.field_differences:
                    # Use the plot field as-is (already contains rating/source/publisher if available)
                    plot = self.plot_edit.toPlainText().strip()
                    if plot:
                        self.book.comments = plot
                        applied_fields.append('Plot')

                # Save to database
                self.book_queries.update(self.book)
                
                # Emit signal to notify main window of data save
                self.data_saved.emit()

                # Status message
                if applied_fields:
                    status_msg = f"Updated: {', '.join(applied_fields)}"
                else:
                    status_msg = "No changes applied"
                self.set_status(status_msg, announce=True)
                
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
