
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
    QDialog, QVBoxLayout, QHBoxLayout, QWidget, QLabel, 
    QLineEdit, QTextEdit, QPushButton, QMessageBox, QFrame, QCheckBox, QApplication, QStatusBar
)
from PySide6.QtCore import Qt, QTimer, Signal, QEvent, QSettings
from PySide6.QtGui import QShortcut, QKeySequence, QAccessible, QAbstractItemView, QSizePolicy

from src.accessibility.scaling import UIScaler
from src.accessibility.theme_manager import ThemeManager
from src.accessibility.accessible_events import announce_dialog_opened, announce_dialog_closed, announce_status_message
from src.accessibility.key_filters import is_unmapped_alt_letter
from src.accessibility.shortcuts import get_shortcut_manager, ShortcutContext
from src.accessibility.style_helpers import build_accessible_button_style

from src.database import DatabaseManager, Book
from src.database.queries import BookQueries, AuthorQueries, SeriesQueries, GenreQueries
from src.web.web_book_api import WebBookAPI




class WebMetadataWindow(QDialog):
    """
    Web metadata window with PROVEN accessibility foundation.
    
    F1, Alt+/, and Escape work out of box.
    Built incrementally from accessible skeleton.
    """

    # List of allowed Alt+key shortcuts for Web Metadata (letters only for event filter)
    ALLOWED_ALT_KEYS = {'T', 'A', 'P', 'Y', 'I', 'G', 'S', 'W', 'R', 'U', 'O', '/', 'F1'}

    # Signal emitted when data is saved
    data_saved = Signal()

    def __init__(self, db, book, scaler, theme_manager, parent=None, refresh_callback=None):
        # Call base class constructor FIRST
        super().__init__(parent)
        
        # Always set parent_window, even if None
        self.parent_window = None
        from PySide6.QtWidgets import QMainWindow, QDialog
        if parent and (isinstance(parent, QMainWindow) or isinstance(parent, QDialog)):
            self.parent_window = parent
        
        self.db = db
        self.book = book
        self.scaler = scaler
        self.theme_manager = theme_manager
        self.refresh_callback = refresh_callback
        self.refresh_count = 0  # Track how many times we've refreshed
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
        
        # Install event filter on QPushButton for Enter key handling
        for widget in self.findChildren(QPushButton):
            widget.installEventFilter(self)
        
        # CRITICAL: Set focus to first field with web differences when window opens
        # JAWS requires focus to be set for Alt+keys to work properly
        QTimer.singleShot(0, self.set_focus_to_first_differing_field)

    def eventFilter(self, source, event):
        """Event filter to enforce Alt-letter hygiene and block unmapped Alt keys."""
        if event.type() == QEvent.KeyPress:
            key = event.key()
            modifiers = event.modifiers()
            
            # Handle Enter key on focused buttons
            if key == Qt.Key_Return or key == Qt.Key_Enter:
                if isinstance(source, QPushButton) and source.hasFocus():
                    source.click()
                    return True
            
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

            # Store reference for toggling
            row_widget._web_label = web_label
            row_widget._web_edit = web_edit
            row_widget._checkbox = checkbox
            return row_widget

        # Title fields
        self.title_edit = QLineEdit()
        self.title_edit.setAccessibleName("Current Title")
        self.title_edit.setAccessibleDescription("Current book title")
        self.title_edit.setReadOnly(True)  # Make read-only
        self.title_edit.setObjectName("title_edit")  # For shortcut manager
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
        self.author_edit.setReadOnly(True)  # Make read-only
        self.author_edit.setObjectName("author_edit")  # For shortcut manager
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
        self.year_edit.setReadOnly(True)  # Make read-only
        self.year_edit.setObjectName("year_edit")
        self.year_web_edit = QLineEdit()
        self.year_web_edit.setAccessibleName("Web Year")
        self.year_web_edit.setAccessibleDescription("Publication year from web source")
        self.year_web_edit.setReadOnly(True)
        self.year_checkbox = QCheckBox()
        self.year_checkbox.setAccessibleName("Keep Web Year")
        self.year_checkbox.setAccessibleDescription("Apply web year to current book")
        self.year_checkbox.setChecked(False)
        # Removed setShortcut to avoid conflict with shortcut manager
        year_row = create_two_column_row("Year:", self.year_edit, self.year_web_edit, self.year_checkbox)
        self.year_row = year_row
        self.main_layout.addWidget(year_row)

        # Series fields
        self.series_edit = QLineEdit()
        self.series_edit.setAccessibleName("Current Series")
        self.series_edit.setAccessibleDescription("Current series name")
        self.series_edit.setReadOnly(True)  # Make read-only
        self.series_edit.setObjectName("series_edit")  # For shortcut manager
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
        self.genre_edit.setReadOnly(True)  # Make read-only
        self.genre_edit.setObjectName("genre_edit")  # For shortcut manager
        self.genre_web_edit = QLineEdit()
        self.genre_web_edit.setAccessibleName("Web Genre")
        self.genre_web_edit.setAccessibleDescription("Genre from web source")
        self.genre_web_edit.setReadOnly(True)
        self.genre_checkbox = QCheckBox()
        self.genre_checkbox.setAccessibleName("Keep Web Genre")
        self.genre_checkbox.setAccessibleDescription("Apply web genre to current book")
        self.genre_checkbox.setChecked(False)
        genre_row = create_two_column_row("Genre:", self.genre_edit, self.genre_web_edit, self.genre_checkbox)
        self.genre_row = genre_row
        self.main_layout.addWidget(genre_row)

        # Plot field - always visible to maintain layout
        plot_layout = QHBoxLayout()
        plot_label = QLabel("&Plot:")
        plot_label.setAccessibleName("Plot field label")
        self.plot_edit = QTextEdit()
        self.plot_edit.setAccessibleName("Plot")
        self.plot_edit.setReadOnly(True)  # Make read-only like other fields
        self.plot_edit.setFocusPolicy(Qt.StrongFocus)  # Ensure it can receive focus for tabbing
        self.plot_edit.setObjectName("plot_edit")  # For shortcut manager
        plot_label.setBuddy(self.plot_edit)
        plot_layout.addWidget(plot_label)
        plot_layout.addWidget(self.plot_edit)
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
        
        # Rating field
        rating_layout = QHBoxLayout()
        rating_label = QLabel("Rating:")
        rating_label.setAccessibleName("Rating field label")
        self.rating_edit = QLineEdit()
        self.rating_edit.setAccessibleName("Rating")
        self.rating_edit.setAccessibleDescription("Alt+R")
        self.rating_edit.setReadOnly(True)  # Make read-only
        self.rating_edit.setObjectName("rating_edit")  # For shortcut manager
        self.rating_edit.setFocusPolicy(Qt.StrongFocus)  # Ensure it can receive focus
        rating_label.setBuddy(self.rating_edit)
        rating_layout.addWidget(rating_label)
        rating_layout.addWidget(self.rating_edit)
        rating_label.setMinimumWidth(80)
        rating_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        rating_row = QWidget()
        rating_layout = QHBoxLayout(rating_row)
        rating_layout.setContentsMargins(0, 0, 0, 0)
        rating_layout.setSpacing(10)
        rating_layout.addWidget(rating_label)
        rating_layout.addWidget(self.rating_edit)
        self.rating_row = rating_row
        self.main_layout.addWidget(rating_row)
        
        # Publisher field
        publisher_layout = QHBoxLayout()
        publisher_label = QLabel("Publisher:")
        publisher_label.setAccessibleName("Publisher field label")
        self.publisher_edit = QLineEdit()
        self.publisher_edit.setAccessibleName("Publisher")
        self.publisher_edit.setAccessibleDescription("Alt+U")
        self.publisher_edit.setReadOnly(True)  # Make read-only
        self.publisher_edit.setObjectName("publisher_edit")  # For shortcut manager
        self.publisher_edit.setFocusPolicy(Qt.StrongFocus)  # Ensure it can receive focus
        publisher_label.setBuddy(self.publisher_edit)
        publisher_layout.addWidget(publisher_label)
        publisher_layout.addWidget(self.publisher_edit)
        publisher_label.setMinimumWidth(80)
        publisher_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        publisher_row = QWidget()
        publisher_layout = QHBoxLayout(publisher_row)
        publisher_layout.setContentsMargins(0, 0, 0, 0)
        publisher_layout.setSpacing(10)
        publisher_layout.addWidget(publisher_label)
        publisher_layout.addWidget(self.publisher_edit)
        self.publisher_row = publisher_row
        self.main_layout.addWidget(publisher_row)
        
        # Source field (for display only, not saved to DB)
        source_layout = QHBoxLayout()
        source_label = QLabel("Source:")
        source_label.setAccessibleName("Source field label")
        self.source_edit = QLineEdit()
        self.source_edit.setAccessibleName("Source")
        self.source_edit.setAccessibleDescription("Alt+O")
        self.source_edit.setReadOnly(True)
        self.source_edit.setObjectName("source_edit")  # For shortcut manager
        self.source_edit.setFocusPolicy(Qt.StrongFocus)  # Ensure it can receive focus
        source_label.setBuddy(self.source_edit)
        source_layout.addWidget(source_label)
        source_layout.addWidget(self.source_edit)
        source_label.setMinimumWidth(80)
        source_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        source_row = QWidget()
        source_layout = QHBoxLayout(source_row)
        source_layout.setContentsMargins(0, 0, 0, 0)
        source_layout.setSpacing(10)
        source_layout.addWidget(source_label)
        source_layout.addWidget(self.source_edit)
        self.source_row = source_row
        self.main_layout.addWidget(source_row)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        self.fetch_button = QPushButton("Refresh Web Info")
        self.fetch_button.setAccessibleName("Refresh Web Info")
        self.fetch_button.setAccessibleDescription("Refresh web data from online sources - Alt+W")
        self.fetch_button.setFocusPolicy(Qt.StrongFocus)
        self.fetch_button.setDefault(False)
        self.fetch_button.setAutoDefault(False)
        self.fetch_button.clicked.connect(lambda: self.fetch_web_data(is_refresh=True))
        self.fetch_button.hide()  # Initially hidden, shown only if found on first attempt
        self.fetch_button.setObjectName("fetch_web_button")  # For shortcut manager
        button_layout.addWidget(self.fetch_button)
        
        self.save_button = QPushButton("Save")
        self.save_button.setAccessibleName("Save web metadata")
        self.save_button.setAccessibleDescription("Save changes - Alt+S")
        self.save_button.setFocusPolicy(Qt.StrongFocus)
        self.save_button.setDefault(True)  # Make it the default button for Enter key
        self.save_button.setAutoDefault(False)
        self.save_button.clicked.connect(self.on_save_clicked)
        self.save_button.setObjectName("save_button")  # For shortcut manager
        button_layout.addWidget(self.save_button)
        
        button_layout.addStretch()
        
        self.main_layout.addLayout(button_layout)
        
        # CRITICAL: Add the main_layout to the window layout
        layout.addLayout(self.main_layout)
        
        # Set explicit tab order for logical keyboard navigation
        self.set_tab_order()

    def set_tab_order(self):
        """Set explicit tab order for logical keyboard navigation."""
        # Define tab order following the actual layout:
        # Current Title → Web Title → Title Checkbox → Current Author → Web Author → Author Checkbox
        # → Current Year → Web Year → Year Checkbox → Current Series → Web Series → Series Checkbox
        # → Current Genre → Web Genre → Genre Checkbox → Plot → Source → Rating → Publisher → Save
        tab_widgets = [
            self.title_edit,        # Current title
            self.title_web_edit,    # Web title
            self.title_checkbox,    # Title checkbox
            self.author_edit,       # Current author
            self.author_web_edit,   # Web author
            self.author_checkbox,   # Author checkbox
            self.year_edit,         # Current year
            self.year_web_edit,     # Web year
            self.year_checkbox,     # Year checkbox
            self.series_edit,       # Current series
            self.series_web_edit,   # Web series
            self.series_checkbox,   # Series checkbox
            self.genre_edit,        # Current genre
            self.genre_web_edit,    # Web genre
            self.genre_checkbox,    # Genre checkbox
            self.plot_edit,         # Plot field
            self.rating_edit,       # Rating field
            self.publisher_edit,    # Publisher field
            self.source_edit,       # Source field (read-only)
            self.save_button        # Save button
        ]
        
        # Set tab order sequentially
        for i in range(len(tab_widgets) - 1):
            self.setTabOrder(tab_widgets[i], tab_widgets[i + 1])

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
    def apply_field_styling(self):
        """Apply field styling like backup window."""
        # Apply F1 popup style to fields
        from src.accessibility.shortcut_helpers import build_accessible_f1_popup_style
        field_style = build_accessible_f1_popup_style()
        
        for field in self.findChildren(QLineEdit):
            field.setStyleSheet(field_style)
        
        for field in self.findChildren(QTextEdit):
            field.setStyleSheet(field_style)
        
        # Apply consistent button styling like other windows
        button_style = build_accessible_button_style(self.scaler.get_scaled_size(20))
        for button in self.findChildren(QPushButton):
            button.setStyleSheet(button_style)
    
    def load_book_data(self):
        """Load book data into fields and fetch web data."""
        if self.book:
            self.title_edit.setText(self.book.title or "")
            self.author_edit.setText(self.book.author_name or "")
            self.year_edit.setText(str(self.book.year) if self.book.year else "")
            self.series_edit.setText(self.book.series_name or "")
            self.genre_edit.setText(self.book.genre_name or "")
            self.plot_edit.setPlainText(self.book.comments or "")
            
            # Initialize new fields
            self.source_edit.clear()
            self.rating_edit.clear()
            self.publisher_edit.clear()
            
            # Plot field is always visible now to maintain layout
            self.plot_row.setVisible(True)

            # Initialize web fields and labels as hidden
            for row in [self.title_row, self.author_row, self.year_row, self.series_row, self.genre_row]:
                row._web_label.setVisible(False)
                row._web_edit.setVisible(False)
                row._checkbox.setVisible(False)

        # Auto-fetch web data when window opens
        self.fetch_web_data(is_refresh=False)
    
    def set_focus_to_first_differing_field(self):
        """Set focus to first field that has web differences, fallback to title."""
        # Always start with title field for accessibility
        self.title_edit.setFocus()
        return
    
    def _read_user_preferences(self) -> tuple[bool, bool]:
        """Read user preferences for title and author formatting."""
        settings = QSettings("AbCS", "AudioBookCollector")
        
        # Check legacy settings if current settings don't exist
        if not settings.contains("import/flip_author_name"):
            legacy_settings = QSettings("AbCS", "AbCS")
            flip_author = legacy_settings.value("import/flip_author_name", False, type=bool)
        else:
            flip_author = settings.value("import/flip_author_name", False, type=bool)
        
        if not settings.contains("import/autocorrect/move_leading_the_title"):
            legacy_settings = QSettings("AbCS", "AbCS")
            move_articles = legacy_settings.value("import/autocorrect/move_leading_the_title", False, type=bool)
        else:
            move_articles = settings.value("import/autocorrect/move_leading_the_title", False, type=bool)
        
        return move_articles, flip_author
    
    def fetch_web_data(self, is_refresh=False):
        """Fetch web data from API with automatic retry through all sources."""
        # Read user preferences for search-time transformations
        move_articles, flip_author = self._read_user_preferences()
        
        # Don't increment refresh counter for automatic retries - only for manual refresh
        if is_refresh:
            # Cap refresh counter at 2 (we have sources 0, 1, 2)
            self.refresh_count = min(self.refresh_count + 1, 2)
            start_refresh_count = self.refresh_count
        else:
            # Initial fetch - start from 0
            self.refresh_count = 0
            start_refresh_count = 0
        
        # Show popup for all requests (initial and refresh)
        source_names = {0: "Primary Web Source", 1: "Secondary Web Source", 2: "Additional Web Source"}
        
        # Get book data for search
        if self.parent_window and hasattr(self.parent_window, 'title_edit'):
            title = self.parent_window.title_edit.text().strip()
            author = self.parent_window.author_combo.currentText().strip()
            year_value = self.parent_window.year_spin.value()
            year = None if year_value == self.parent_window.year_spin.minimum() else str(year_value)
        else:
            # Use database values (main window or fallback)
            title = self.book.title
            author = self.book.author_name
            year = str(self.book.year) if self.book.year else None

        # Use WebBookAPI for fetching with automatic retry and preferences
        api = WebBookAPI()
        web_data = None
        last_error = None
        
        # Try each source automatically until we find data or exhaust all sources
        for current_attempt in range(start_refresh_count, 3):  # Try sources 0, 1, 2
            self.refresh_count = current_attempt
            
            # Show popup for each attempt
            current_source = source_names.get(current_attempt, "Primary Web Source")
            
            popup = QDialog(self)
            popup.setWindowTitle("Please wait")
            popup.setModal(True)
            popup.setWindowFlags(popup.windowFlags() | Qt.WindowStaysOnTopHint)
            layout = QVBoxLayout(popup)
            
            if is_refresh:
                label = QLabel(f"Checking {current_source} for book info, please wait!")
            else:
                label = QLabel(f"Searching {current_source} for book info, please wait!")
                
            layout.addWidget(label)
            popup.setLayout(layout)
            popup.resize(350, 80)
            QTimer.singleShot(1800, popup.accept)  # Auto-close after 1.8 seconds
            popup.show()
            QApplication.processEvents()
            
            try:
                web_data = api.get_book_metadata(title, author, year, refresh=current_attempt, 
                                               move_articles=move_articles, flip_author=flip_author)
                if web_data:
                    # Found data - break out of loop
                    break
            except Exception as e:
                last_error = str(e)
                continue  # Try next source
        
        if web_data:
            # Clean web data for storage according to preferences
            cleaned_web_data = api.clean_web_data_for_storage(web_data, move_articles, flip_author)
            self.update_fields_with_web_data(cleaned_web_data)
            
            # Show refresh button if we haven't checked all sources yet
            source = web_data.get('source', '')
            if self.refresh_count < 2:  # 0=Primary, 1=Secondary, 2=Additional (last one)
                self.fetch_button.show()
                # Build status message: Difference - ...
                diff_fields = [k.capitalize() for k in self.field_differences.keys()]
                diff_str = f" - Difference - {', '.join(diff_fields)}" if diff_fields else ""
                
                # Map internal source names to display names
                display_names = {
                    'google_books': 'Primary Web Source',
                    'open_library': 'Secondary Web Source',
                    'wikidata': 'Additional Web Source'
                }
                source_name = display_names.get(source, 'Unknown Source')
                msg = f"Web data found from {source_name}{diff_str}"
                # Delay status announcement until after popup closes
                QTimer.singleShot(2000, lambda: self.set_status(msg, announce=True))
                # Set focus to first differing field after successful fetch
                QTimer.singleShot(2000, self.set_focus_to_first_differing_field)
            else:
                # Found on third source (Additional Web Source) - hide button and show special message
                self.fetch_button.hide()
                source_name = 'Additional Web Source'  # WikiData
                # Delay status announcement until after popup closes
                QTimer.singleShot(2000, lambda: self.set_status(f"Data from {source_name} - no more sources available", announce=True))
                # Set focus to first differing field after successful fetch
                QTimer.singleShot(2000, self.set_focus_to_first_differing_field)
            return
        else:
            # No data found from any source
            # Don't clear existing data on refresh - only clear on initial failure
            if not is_refresh:
                self.clear_web_indicators()
            
            # Check if this was a refresh and we've exhausted all sources
            if is_refresh and self.refresh_count >= 2:
                # All 3 sources checked, hide button
                self.fetch_button.hide()
                # Show popup for no additional data
                from PySide6.QtWidgets import QMessageBox
                from src.accessibility.style_helpers import build_accessible_message_box_style
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("No Additional Data Found")
                msg.setText("No additional information found in Primary, Secondary, or Additional sources.")
                msg.setStyleSheet(build_accessible_message_box_style(self.scaler.get_scaled_size(20)))
                msg.setStandardButtons(QMessageBox.Ok)
                reply = msg.exec()
                # Set status after popup closes
                self.set_status("No additional data found from any source", announce=True, timeout_ms=3000)
            elif last_error:
                self.set_status(f"Error fetching web data: {last_error}", announce=True, timeout_ms=3000)
            else:
                # Different messages for initial vs refresh
                if is_refresh:
                    self.set_status("No additional data found from other sources", announce=True, timeout_ms=3000)
                else:
                    self.set_status("No web data found from any source", announce=True, timeout_ms=3000)
            
            # Return focus to title field on failure
            self.title_edit.setFocus()
            return
    
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
        
        # Plot (update plot field with web data, including rating and publisher)
        if web_data.get('plot'):
            # Build plot text with rating and publisher
            plot_text = ""
            
            # Add rating at the top if available
            rating = web_data.get('rating')
            ratings_count = web_data.get('ratings_count')
            if rating:
                try:
                    rating_val = float(rating)
                    rating_str = f"Rating: {rating_val:.1f}"
                except (ValueError, TypeError):
                    rating_str = f"Rating: {rating}"
                if ratings_count:
                    try:
                        count_val = int(ratings_count)
                        rating_str += f" ({count_val:,} ratings)"
                    except (ValueError, TypeError):
                        pass
                plot_text += rating_str + "\n"
            
            # Add the actual plot
            plot_text += web_data['plot']
            
            # Add publisher at the bottom if available
            publisher = web_data.get('publisher')
            if publisher:
                plot_text += f"\nPublisher: {publisher}"
            
            # Set the combined text in plot field
            self.plot_edit.setPlainText(plot_text)
            
            # Add plot to field_differences so it gets saved
            current_plot = self.book.comments or ""
            if plot_text.strip() != current_plot.strip():
                self.field_differences['plot'] = plot_text
            
            # Handle source (display only) - show primary/secondary/tertiary
            source = web_data.get('source')
            if source:
                # Use refresh_count for proper source names, not actual source type
                source_names_by_refresh = {0: "Primary", 1: "Secondary", 2: "Additional"}
                source_display = source_names_by_refresh.get(self.refresh_count, "Primary")
                self.source_edit.setText(source_display)
            else:
                self.source_edit.clear()
            
            # Clear separate rating and publisher fields since they're now in plot
            self.rating_edit.clear()
            self.publisher_edit.clear()
        else:
            # Clear all fields if no plot data
            self.plot_edit.clear()
            self.rating_edit.clear()
            self.source_edit.clear()
            self.publisher_edit.clear()
    
    # Removed: show_changes_popup (was for testing only)
    
    def show_indicator(self, field, show, color=None):
        """Show or hide the web data checkbox for a field (indicators removed for low vision)."""
        # Find the checkbox in the field's container
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
            # Toggle checkbox visibility (indicators removed for low vision users)
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
        Setup shortcuts using centralized shortcut manager for consistency.
        F1, Alt+/, Escape work out of box.
        """
        # Use centralized shortcut manager
        shortcut_mgr = get_shortcut_manager()
        
        # Alt+Key shortcuts (centralized)
        # Note: Shortcut mappings are defined in src/accessibility/shortcuts.py
        # This follows the accessibility standards - single source of truth
        callback_map = {
            'title_edit': lambda: self.title_edit.setFocus(),
            'author_edit': lambda: self.author_edit.setFocus(), 
            'plot_edit': lambda: self.plot_edit.setFocus(),
            'year_edit': lambda: self.year_edit.setFocus(),
            'series_edit': lambda: self.series_edit.setFocus(),
            'genre_edit': lambda: self.genre_edit.setFocus(),
            'rating_edit': lambda: self.rating_edit.setFocus(),
            'publisher_edit': lambda: self.publisher_edit.setFocus(),
            'source_edit': lambda: self.source_edit.setFocus(),
            'fetch_web_button': lambda: self.fetch_web_data(is_refresh=True),
            'save_button': lambda: self.on_save_clicked() if self.save_button.isVisible() else None,
            'show_help': lambda: self.on_show_shortcuts(),
            'read_status_bar': lambda: self.on_read_status_bar(),
            'close_window': lambda: self.on_escape_pressed(),
        }
        shortcut_mgr.register_alt_shortcuts(
            self, ShortcutContext.WEB_METADATA, callback_map
        )
    
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
            ("Alt+R", "Rating"),
            ("Alt+U", "Publisher"),
            ("Alt+O", "Source"),
            ("Alt+W", "Refresh Web Info (if found quickly)"),
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
    
    def set_status(self, message: str, timeout_ms: int = 0, announce: bool = False):
        """Set status message with centralized status helper."""
        self.status_bar.showMessage(message)
        if announce:
            announce_status_message(self.status_bar, message, move_focus=True)
        
        # Auto-clear status after timeout if specified
        if timeout_ms > 0:
            QTimer.singleShot(timeout_ms, lambda: self.status_bar.clearMessage())

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

                # Plot (save only the actual plot content, rating and publisher are handled separately)
                if 'plot' in self.field_differences:
                    # Use only the plot field content (rating/source/publisher are in separate fields)
                    plot = self.plot_edit.toPlainText().strip()
                    if plot:
                        self.book.comments = plot
                        applied_fields.append('Plot')
                
                # Rating (save to database if available)
                rating_text = self.rating_edit.text().strip()
                if rating_text:
                    # Extract just the rating number (e.g., "4.5" from "4.5 (1,234 ratings)")
                    import re
                    rating_match = re.match(r'([0-9.]+)', rating_text)
                    if rating_match:
                        try:
                            rating_val = float(rating_match.group(1))
                            # Note: You'll need to add a rating field to your book database table
                            # self.book.rating = rating_val
                            # applied_fields.append('Rating')
                            pass  # Rating field not yet implemented in database
                        except ValueError:
                            pass
                
                # Publisher (save to database if available)
                publisher_text = self.publisher_edit.text().strip()
                if publisher_text:
                    # Note: You'll need to add a publisher field to your book database table
                    # self.book.publisher = publisher_text
                    # applied_fields.append('Publisher')
                    pass  # Publisher field not yet implemented in database
                
                # Source is NOT saved to database (display only for legal safety)

                # Save to database
                self.book_queries.update(self.book)
                
                # Emit signal to notify main window of data save
                self.data_saved.emit()

                # Status message
                if applied_fields:
                    status_msg = f"Updated: {', '.join(applied_fields)}"
                else:
                    status_msg = "No changes applied"
                self.set_status(status_msg, announce=True, timeout_ms=2000)
                
                announce_dialog_closed(self)
                super().accept()
                
            except Exception as e:
                self.set_status(f"Error saving: {str(e)}", announce=True)
                # Return focus to first field on error
                self.set_focus_to_first_differing_field()
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
