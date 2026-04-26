"""
Web Metadata Window - Built from PROVEN accessible skeleton
Accessibility works out of box: F1, Alt+/, Escape
"""

import sys
import os

# Add to project root to Python path
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QMessageBox,
    QCheckBox,
    QApplication,
    QStatusBar,
    QAbstractItemView,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PySide6.QtCore import Qt, QTimer, Signal, QEvent, QSettings
from PySide6.QtGui import QShortcut, QKeySequence, QAccessible

from src.accessibility.scaling import UIScaler
from src.accessibility.theme_manager import ThemeManager
from src.accessibility.accessible_events import (
    announce_dialog_opened,
    announce_dialog_closed,
    announce_status_message,
)
from src.accessibility.key_filters import is_unmapped_alt_letter
from src.accessibility.shortcuts import get_shortcut_manager, ShortcutContext
from src.accessibility.style_helpers import build_accessible_button_style

from src.database import DatabaseManager, Book
from src.database.queries import BookQueries, AuthorQueries, SeriesQueries, GenreQueries, CollectionQueries
from src.web.web_book_api import WebBookAPI


class WebMetadataWindow(QDialog):

    @staticmethod
    def normalize_db_title(title: str) -> str:
        """Normalize DB title for search/compare: move article to beginning, trim, lowercase, remove embedded spaces."""
        if not title:
            return ""
        # Move trailing article to beginning (e.g., 'moon the' -> 'the moon')
        import re

        t = title.strip()
        match = re.match(r"^(.*?)[,\s]+(the|a|an)$", t, re.IGNORECASE)
        if match:
            base = match.group(1).strip()
            article = match.group(2).lower()
            t = f"{article} {base}"
        return "".join(t.lower().split())

    """
    Web metadata window with PROVEN accessibility foundation.

    F1, Alt+/, and Escape work out of box.
    Built incrementally from accessible skeleton.
    """

    # List of allowed Alt+key shortcuts for Web Metadata (letters only for event filter)
    ALLOWED_ALT_KEYS = {"T", "A", "P", "Y", "I", "N", "G", "S", "R", "/", "F1"}

    # Signal emitted when data is saved
    data_saved = Signal()

    def __init__(
        self,
        db,
        book,
        scaler,
        theme_manager,
        parent=None,
        refresh_callback=None,
        web_data=None,
    ):
        """Initialize web metadata window.

        Args:
            web_data: Pre-fetched web data (if provided, skips auto-fetch)
        """
        super().__init__(parent)
        from src.accessibility.icon_helper import get_app_icon

        self.setWindowIcon(get_app_icon())

        # Store pre-fetched web data if provided
        self.pre_fetched_web_data = web_data

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
        self.setWindowTitle("Web Metadata")
        self.setModal(True)
        # Make window taller for expanded plot field
        self.resize(800, 700)
        self.web_data = None
        self.field_differences = {}
        self.status_bar = QStatusBar()
        # Initialize query helpers
        self.book_queries = BookQueries(self.db) if self.db else None
        self.author_queries = AuthorQueries(self.db) if self.db else None
        self.series_queries = SeriesQueries(self.db) if self.db else None
        self.genre_queries = GenreQueries(self.db) if self.db else None
        self.collection_queries = CollectionQueries(self.db) if self.db else None
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
        # Screen readers require focus to be set for Alt+keys to work properly
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
        title_row = create_two_column_row(
            "Title:", self.title_edit, self.title_web_edit, self.title_checkbox
        )
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
        self.author_checkbox.setAccessibleDescription(
            "Apply web author to current book"
        )
        self.author_checkbox.setChecked(False)
        author_row = create_two_column_row(
            "Author:", self.author_edit, self.author_web_edit, self.author_checkbox
        )
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
        year_row = create_two_column_row(
            "Year:", self.year_edit, self.year_web_edit, self.year_checkbox
        )
        self.year_row = year_row
        self.main_layout.addWidget(year_row)

        # Series fields (with series number)
        series_row = QWidget()
        series_layout = QHBoxLayout(series_row)
        series_layout.setContentsMargins(0, 0, 0, 0)
        series_layout.setSpacing(10)

        # Left column - Current data
        left_label = QLabel("Series:")
        left_label.setMinimumWidth(80)
        left_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        series_layout.addWidget(left_label)

        self.series_edit = QLineEdit()
        self.series_edit.setAccessibleName("Current Series")
        self.series_edit.setAccessibleDescription("Current series name")
        self.series_edit.setReadOnly(True)  # Make read-only
        self.series_edit.setObjectName("series_edit")  # For shortcut manager
        self.series_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        series_layout.addWidget(self.series_edit)

        # Series number label and field
        series_number_label = QLabel("#:")
        series_number_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        series_layout.addWidget(series_number_label)

        self.series_number_edit = QLineEdit()
        self.series_number_edit.setAccessibleName("Series Number")
        self.series_number_edit.setAccessibleDescription("Alt+N")
        self.series_number_edit.setReadOnly(True)
        self.series_number_edit.setMaxLength(2)  # Only 2 digits
        self.series_number_edit.setMaximumWidth(50)  # Small width
        self.series_number_edit.setObjectName(
            "series_number_edit"
        )  # For shortcut manager
        series_layout.addWidget(self.series_number_edit)

        # Right column - Web data label (initially hidden)
        web_label = QLabel("Web")
        web_label.setMinimumWidth(80)
        web_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        web_label.setVisible(False)
        series_layout.addWidget(web_label)

        self.series_web_edit = QLineEdit()
        self.series_web_edit.setAccessibleName("Web Series")
        self.series_web_edit.setAccessibleDescription("Series name from web source")
        self.series_web_edit.setReadOnly(True)
        self.series_web_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.series_web_edit.setVisible(False)
        series_layout.addWidget(self.series_web_edit)

        # Web series number
        self.series_number_web_edit = QLineEdit()
        self.series_number_web_edit.setAccessibleName("Web Series Number")
        self.series_number_web_edit.setAccessibleDescription(
            "Series number from web source"
        )
        self.series_number_web_edit.setReadOnly(True)
        self.series_number_web_edit.setMaxLength(2)
        self.series_number_web_edit.setMaximumWidth(50)
        self.series_number_web_edit.setVisible(False)
        series_layout.addWidget(self.series_number_web_edit)

        # Checkbox
        self.series_checkbox = QCheckBox()
        self.series_checkbox.setAccessibleName("Keep Web Series")
        self.series_checkbox.setAccessibleDescription(
            "Apply web series to current book"
        )
        self.series_checkbox.setChecked(False)
        self.series_checkbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.series_checkbox.setVisible(False)
        series_layout.addWidget(self.series_checkbox)

        # Store reference for toggling
        series_row._web_label = web_label
        series_row._web_edit = self.series_web_edit
        series_row._web_number_edit = self.series_number_web_edit
        series_row._checkbox = self.series_checkbox
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
        genre_row = create_two_column_row(
            "Genre:", self.genre_edit, self.genre_web_edit, self.genre_checkbox
        )
        self.genre_row = genre_row
        self.main_layout.addWidget(genre_row)

        # Plot field - always visible to maintain layout
        plot_layout = QHBoxLayout()
        plot_label = QLabel("&Plot:")
        plot_label.setFocusPolicy(Qt.NoFocus)
        self.plot_edit = QTextEdit()
        self.plot_edit.setAccessibleName("Plot")
        self.plot_edit.setAccessibleDescription("Current plot from web metadata")
        self.plot_edit.setReadOnly(True)  # Make read-only like other fields
        self.plot_edit.setFocusPolicy(
            Qt.StrongFocus
        )  # Ensure it can receive focus for tabbing
        self.plot_edit.setObjectName("plot_edit")  # For shortcut manager
        self.plot_edit.setMinimumHeight(150)  # Give plot more vertical space
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
        rating_label.setFocusPolicy(Qt.NoFocus)
        self.rating_edit = QLineEdit()
        self.rating_edit.setAccessibleName("Rating")
        self.rating_edit.setAccessibleDescription("Current rating from web metadata")
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

        # Publisher field removed - too much inconsistent data from web sources

        # Add buttons
        button_layout = QHBoxLayout()

        # Stretch first to push buttons to the right
        button_layout.addStretch()

        self.save_button = QPushButton("Save")
        self.save_button.setAccessibleName("Save web metadata")
        self.save_button.setAccessibleDescription("Save changes - Alt+S")
        self.save_button.setFocusPolicy(Qt.StrongFocus)
        self.save_button.setDefault(True)  # Make it the default button for Enter key
        self.save_button.setAutoDefault(False)
        self.save_button.clicked.connect(self.on_save_clicked)
        self.save_button.setObjectName("save_button")  # For shortcut manager
        button_layout.addWidget(self.save_button)

        self.main_layout.addLayout(button_layout)

        # CRITICAL: Add the main_layout to the window layout
        layout.addLayout(self.main_layout)

        # Set explicit tab order for logical keyboard navigation
        self.set_tab_order()

    def set_tab_order(self):
        """Set explicit tab order for logical keyboard navigation."""
        # Define tab order following the actual layout:
        # Current Title → Web Title → Title Checkbox → Current Author → Web Author → Author Checkbox
        # → Current Year → Web Year → Year Checkbox → Current Series → Series # → Web Series → Web # → Series Checkbox
        # → Current Genre → Web Genre → Genre Checkbox → Plot → Rating → Save
        tab_widgets = [
            self.title_edit,  # Current title
            self.title_web_edit,  # Web title
            self.title_checkbox,  # Title checkbox
            self.author_edit,  # Current author
            self.author_web_edit,  # Web author
            self.author_checkbox,  # Author checkbox
            self.year_edit,  # Current year
            self.year_web_edit,  # Web year
            self.year_checkbox,  # Year checkbox
            self.series_edit,  # Current series
            self.series_number_edit,  # Current series number
            self.series_web_edit,  # Web series
            self.series_number_web_edit,  # Web series number
            self.series_checkbox,  # Series checkbox
            self.genre_edit,  # Current genre
            self.genre_web_edit,  # Web genre
            self.genre_checkbox,  # Genre checkbox
            self.plot_edit,  # Plot field
            self.rating_edit,  # Rating field
            self.save_button,  # Save button
        ]

        # Set tab order sequentially
        for i in range(len(tab_widgets) - 1):
            self.setTabOrder(tab_widgets[i], tab_widgets[i + 1])

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
            # Check if series_number attribute exists (will be added to DB later)
            if hasattr(self.book, "series_number") and self.book.series_number:
                self.series_number_edit.setText(str(self.book.series_number))
            else:
                self.series_number_edit.clear()
            self.genre_edit.setText(self.book.genre_name or "")
            self.plot_edit.setPlainText(self.book.comments or "")

            # Initialize new fields
            self.rating_edit.clear()
            # Publisher field removed

            # Plot field is always visible now to maintain layout
            self.plot_row.setVisible(True)

            # Initialize web fields and labels as hidden
            for row in [
                self.title_row,
                self.author_row,
                self.year_row,
                self.series_row,
                self.genre_row,
            ]:
                row._web_label.setVisible(False)
                row._web_edit.setVisible(False)
                if hasattr(row, "_web_number_edit"):
                    row._web_number_edit.setVisible(False)
                row._checkbox.setVisible(False)

        # Auto-fetch web data when window opens (only if not pre-fetched)
        if self.pre_fetched_web_data:
            # Use pre-fetched data and apply transformations
            move_articles, flip_author = self._read_user_preferences()
            api = WebBookAPI()
            cleaned_web_data = api.clean_web_data_for_storage(
                self.pre_fetched_web_data, move_articles, flip_author
            )
            self.update_fields_with_web_data(cleaned_web_data)

            # Build status message: Difference - ...
            diff_fields = [k.capitalize() for k in self.field_differences.keys()]
            diff_str = (
                f" - Difference - {', '.join(diff_fields)}" if diff_fields else ""
            )
            msg = f"Web data found{diff_str}"
            self.set_status(msg, announce=True)
            # Requirement: web info returned => focus Plot ONLY if plot is non-empty
            plot_text = cleaned_web_data.get("plot")
            if plot_text and str(plot_text).strip():
                QTimer.singleShot(100, self.plot_edit.setFocus)
            else:
                QTimer.singleShot(100, self.title_edit.setFocus)
        else:
            # No web payload provided to this window.
            QTimer.singleShot(100, self.title_edit.setFocus)

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
            flip_author = legacy_settings.value(
                "import/flip_author_name", False, type=bool
            )
        else:
            flip_author = settings.value("import/flip_author_name", False, type=bool)

        if not settings.contains("import/autocorrect/move_leading_the_title"):
            legacy_settings = QSettings("AbCS", "AbCS")
            move_articles = legacy_settings.value(
                "import/autocorrect/move_leading_the_title", False, type=bool
            )
        else:
            move_articles = settings.value(
                "import/autocorrect/move_leading_the_title", False, type=bool
            )

        return move_articles, flip_author

    # fetch_web_data removed - now handled in main_window.py

    def update_fields_with_web_data(self, web_data):
        """Update UI fields with web data and track differences. Show web columns and checkboxes only for changed fields."""
        self.web_data = web_data
        self.field_differences = {}

        # Helper to handle field comparison and visibility

        def handle_field_comparison(
            web_value, current_value, web_edit, checkbox, field_name, row_widget
        ):
            current_str = (
                str(current_value).strip() if current_value is not None else ""
            )
            web_str = str(web_value).strip() if web_value is not None else ""

            # For title field, normalize for compare/search (trim, lowercase, remove embedded spaces)
            if field_name == "title":
                norm_current = self.normalize_db_title(current_str)
                norm_web = self.normalize_db_title(web_str)
            else:
                norm_current = current_str.lower()
                norm_web = web_str.lower()

            if web_value and (current_value is None or current_str == ""):
                # DB field is empty and web data exists - show web data but hide checkbox (auto-applied)
                web_edit.setText(web_str)
                row_widget._web_label.setVisible(True)
                row_widget._web_edit.setVisible(True)
                row_widget._checkbox.setVisible(False)
                checkbox.setVisible(False)
                self.field_differences[field_name] = web_str
                return True
            elif (
                web_value
                and current_value is not None
                and current_str != ""
                and norm_web != norm_current
            ):
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
            web_data.get("title"),
            self.book.title,
            self.title_web_edit,
            self.title_checkbox,
            "title",
            self.title_row,
        )

        # Author
        handle_field_comparison(
            web_data.get("author"),
            self.book.author_name,
            self.author_web_edit,
            self.author_checkbox,
            "author",
            self.author_row,
        )

        # Year
        handle_field_comparison(
            web_data.get("year"),
            self.book.year,
            self.year_web_edit,
            self.year_checkbox,
            "year",
            self.year_row,
        )

        # Series (handle series name and number separately)
        series_name = web_data.get("series", "")
        series_number = web_data.get("series_number", "")

        # Handle series name
        current_series = self.book.series_name or ""
        if series_name and (
            not current_series or series_name.lower() != current_series.lower()
        ):
            self.series_web_edit.setText(series_name)
            self.series_row._web_label.setVisible(True)
            self.series_web_edit.setVisible(True)
            self.series_checkbox.setVisible(True)
            self.series_checkbox.setChecked(True)
            self.field_differences["series"] = series_name
        else:
            self.series_row._web_label.setVisible(False)
            self.series_web_edit.setVisible(False)
            self.series_checkbox.setVisible(False)

        # Handle series number
        current_series_number = ""
        if hasattr(self.book, "series_number") and self.book.series_number:
            current_series_number = str(self.book.series_number)
        if series_number and (
            not current_series_number or series_number != current_series_number
        ):
            self.series_number_web_edit.setText(series_number)
            # Show web number field if series name is also showing
            if self.series_row._web_label.isVisible():
                self.series_number_web_edit.setVisible(True)
            # Add to field differences if different
            if "series" in self.field_differences:
                self.field_differences["series_number"] = series_number
        else:
            self.series_number_web_edit.setVisible(False)

        # Genre
        handle_field_comparison(
            web_data.get("genre"),
            self.book.genre_name,
            self.genre_web_edit,
            self.genre_checkbox,
            "genre",
            self.genre_row,
        )

        # Plot (store rating in database but only show plot in UI)
        if web_data.get("plot"):
            # Build plot text for database storage (includes rating only)
            plot_text_for_db = ""

            # Add rating at the top if available
            rating = web_data.get("rating")
            ratings_count = web_data.get("ratings_count")
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
                plot_text_for_db += rating_str + "\n"

            # Add the actual plot
            plot_text_for_db += web_data["plot"]

            # Set only the plot text in the UI field (no rating)
            self.plot_edit.setPlainText(web_data["plot"])

            # Add the full plot text (with rating) to field_differences for DB storage
            current_plot = self.book.comments or ""
            if plot_text_for_db.strip() != current_plot.strip():
                self.field_differences["plot"] = plot_text_for_db

            # Show rating in separate UI field
            if rating:
                try:
                    rating_val = float(rating)
                    rating_display = f"{rating_val:.1f}"
                except (ValueError, TypeError):
                    rating_display = str(rating)
                if ratings_count:
                    try:
                        count_val = int(ratings_count)
                        rating_display += f" ({count_val:,} ratings)"
                    except (ValueError, TypeError):
                        pass
                self.rating_edit.setText(rating_display)
            else:
                self.rating_edit.clear()
        else:
            # Clear all fields if no plot data
            self.plot_edit.clear()
            self.rating_edit.clear()

    def setup_shortcuts(self):
        """
        Setup shortcuts with local control keys and centralized field keys.
        F1, Alt+/, and Escape are local-only by design.
        """
        # Use centralized shortcut manager
        shortcut_mgr = get_shortcut_manager()

        # Alt+Key shortcuts (centralized)
        # Note: Shortcut mappings are defined in src/accessibility/shortcuts.py
        # This follows the accessibility standards - single source of truth
        callback_map = {
            "title_edit": lambda: self.title_edit.setFocus(),
            "author_edit": lambda: self.author_edit.setFocus(),
            "plot_edit": lambda: self.plot_edit.setFocus(),
            "year_edit": lambda: self.year_edit.setFocus(),
            "series_edit": lambda: self.series_edit.setFocus(),
            "series_number_edit": lambda: self.series_number_edit.setFocus(),
            "genre_edit": lambda: self.genre_edit.setFocus(),
            "rating_edit": lambda: self.rating_edit.setFocus(),
            "save_button": lambda: (
                self.on_save_clicked() if self.save_button.isVisible() else None
            ),
        }
        shortcut_mgr.register_alt_shortcuts(
            self, ShortcutContext.WEB_METADATA, callback_map
        )

        # Local-only shortcuts for consistency across windows
        self.help_shortcut = QShortcut(QKeySequence("F1"), self)
        self.help_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.help_shortcut.activated.connect(self.on_show_shortcuts)

        self.status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.status_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.status_shortcut.activated.connect(self.on_read_status_bar)

        self.escape_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.escape_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.escape_shortcut.activated.connect(self.on_escape_pressed)

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
        from src.accessibility.shortcut_helpers import (
            get_accessible_shortcuts_list,
            build_accessible_f1_popup_style,
        )

        table.setStyleSheet(build_accessible_f1_popup_style())

        shortcuts = [
            ("Alt+T", "Title"),
            ("Alt+A", "Author"),
            ("Alt+P", "Plot"),
            ("Alt+Y", "Year"),
            ("Alt+I", "Series"),
            ("Alt+N", "Series #"),
            ("Alt+G", "Genre"),
            ("Alt+R", "Rating"),
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
        """Alt+/ shortcut - read status. Do nothing if no screen reader active."""
        status_text = self.status_bar.currentMessage()
        if QAccessible.isActive():
            self.set_status(status_text, announce=True)
        # else: do nothing (no popup)

    def set_status(self, message: str, timeout_ms: int = 0, announce: bool = False):
        """Set status message with centralized status helper."""
        self.status_bar.showMessage(message)
        if announce:
            announce_status_message(self.status_bar, message, move_focus=True)

        # Auto-clear status after timeout if specified
        if timeout_ms > 0:
            def safe_clear_status():
                try:
                    if self.status_bar:
                        self.status_bar.clearMessage()
                except RuntimeError:
                    pass  # Widget already destroyed
            QTimer.singleShot(timeout_ms, safe_clear_status)

    def on_escape_pressed(self):
        """Handle escape key - show save confirmation before closing."""
        from src.accessibility.style_helpers import exec_styled_message_box

        from src.accessibility.icon_helper import get_app_icon

        reply = exec_styled_message_box(
            self,
            self.scaler.get_scaled_size(20),
            icon=QMessageBox.Question,
            title="Confirm Save",
            text="Save web data?",
            buttons=QMessageBox.Yes | QMessageBox.No,
            default_button=QMessageBox.Yes,
            window_icon=get_app_icon(),
        )

        if reply == QMessageBox.Yes:
            self.accept()  # Save and close
        elif reply == QMessageBox.No:
            announce_dialog_closed(self)
            # Return focus to parent window's table if available
            if self.parent_window and hasattr(self.parent_window, "table"):
                # Use QTimer to ensure focus is set after dialog closes
                QTimer.singleShot(
                    0, lambda: self.parent_window._restore_table_focus_context(None)
                )
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
                if "title" in self.field_differences:
                    if self.title_row._checkbox.isVisible():
                        # Field differs - apply if checked
                        if self.title_checkbox.isChecked():
                            self.book.title = self.title_web_edit.text().strip()
                            applied_fields.append("Title")
                    else:
                        # DB field was empty - auto-apply web data
                        self.book.title = self.title_web_edit.text().strip()
                        applied_fields.append("Title")

                # Author
                if "author" in self.field_differences:
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
                                applied_fields.append("Author")
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
                            applied_fields.append("Author")

                # Year
                if "year" in self.field_differences:
                    if self.year_row._checkbox.isVisible():
                        # Field differs - apply if checked
                        if self.year_checkbox.isChecked():
                            year_text = self.year_web_edit.text().strip()
                            try:
                                self.book.year = int(year_text) if year_text else None
                                applied_fields.append("Year")
                            except ValueError:
                                self.book.year = None
                    else:
                        # DB field was empty - auto-apply web data
                        year_text = self.year_web_edit.text().strip()
                        try:
                            self.book.year = int(year_text) if year_text else None
                            applied_fields.append("Year")
                        except ValueError:
                            self.book.year = None

                # Series
                if "series" in self.field_differences:
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
                                    series = self.series_queries.get_by_name(
                                        series_name
                                    )
                                    if not series:
                                        series_id = self.series_queries.insert(
                                            series_name
                                        )
                                    else:
                                        series_id = series.series_id
                            self.book.series_id = series_id
                            self.book.series_number = series_number
                            applied_fields.append("Series")
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
                        applied_fields.append("Series")

                # Genre
                if "genre" in self.field_differences:
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
                                applied_fields.append("Genre")
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
                            applied_fields.append("Genre")

                # Plot (save only the actual plot content, rating and publisher are handled separately)
                if "plot" in self.field_differences:
                    # Save the combined rating+plot string (from field_differences) to comments
                    plot_text_for_db = self.field_differences["plot"].strip("\n")
                    if plot_text_for_db:
                        self.book.comments = plot_text_for_db
                        applied_fields.append("Plot")

                # Rating (save to database if available)
                rating_text = self.rating_edit.text().strip()
                if rating_text:
                    # Extract just the rating number (e.g., "4.5" from "4.5 (1,234 ratings)")
                    import re

                    rating_match = re.match(r"([0-9.]+)", rating_text)
                    if rating_match:
                        try:
                            rating_val = float(rating_match.group(1))
                            # Note: You'll need to add a rating field to your book database table
                            # self.book.rating = rating_val
                            # applied_fields.append('Rating')
                            pass  # Rating field not yet implemented in database
                        except ValueError:
                            pass

                # Publisher field removed - too much inconsistent data from web sources

                # Source is NOT saved to database (display only for legal safety)

                # Validate foreign keys before save (prevent IntegrityError)
                if self.book.author_id and self.author_queries:
                    author = self.author_queries.get_by_id(self.book.author_id)
                    if not author:
                        self.book.author_id = None
                if self.book.series_id and self.series_queries:
                    series = self.series_queries.get_by_id(self.book.series_id)
                    if not series:
                        self.book.series_id = None
                if self.book.genre_id and self.genre_queries:
                    genre = self.genre_queries.get_by_id(self.book.genre_id)
                    if not genre:
                        self.book.genre_id = None
                if self.book.collection_id and self.collection_queries:
                    collection = self.collection_queries.get_by_id(self.book.collection_id)
                    if not collection:
                        self.book.collection_id = None

                # Save to database
                try:
                    self.book_queries.update(self.book)
                except Exception as e:
                    raise

                # Emit signal to notify main window of data save
                self.data_saved.emit()

                # Call refresh callback to update parent window
                if self.refresh_callback:
                    self.refresh_callback()
                    # Clear dirty flag in parent window since data was just saved
                    if hasattr(self.parent(), "_clear_dirty"):
                        self.parent()._clear_dirty()

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
            super().accept()  # Use accept instead of reject for consistency


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
        genre_name="Test Genre",
    )

    window = WebMetadataWindow(
        db=None,
        book=book,
        scaler=scaler,
        theme_manager=theme_manager,
        refresh_callback=None,  # No callback needed for test
    )
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(test_web_metadata())
