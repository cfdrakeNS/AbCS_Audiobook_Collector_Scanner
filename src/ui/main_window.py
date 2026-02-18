"""
Main Window - Audio Book Window
Primary interface for browsing and managing audiobook collection.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QComboBox, QLineEdit,
    QPushButton, QLabel, QStatusBar, QMessageBox, QHeaderView,
    QAbstractItemView, QMenu, QDialog, QTextEdit, QSizePolicy
)
from PySide6.QtCore import (
    Qt, Signal, QTimer, QItemSelection, QItemSelectionModel, QEvent, QPoint
)
from PySide6.QtGui import QKeyEvent, QAction, QShortcut, QKeySequence, QColor, QPalette, QMouseEvent, QAccessible
from PySide6.QtWidgets import QApplication
import datetime

from database import (
    DatabaseManager, BookQueries, AuthorQueries, SeriesQueries,
    GenreQueries, CollectionQueries, SearchFilter, Book, StatisticsQueries
)
from accessibility.scaling import UIScaler
from accessibility.theme_manager import ThemeManager
from accessibility.shortcuts import get_shortcut_manager, ShortcutContext
from accessibility.key_filters import is_unmapped_alt_letter
from ui.book_details import BookDetailsWindow
from ui.update_window import UpdateWindow
from ui.preferences_window import PreferencesWindow
from ui.import_window import ImportWindow
from ui.collection_window import CollectionWindow

# Import version from main module


def get_app_version():
    """Get app version from main module."""
    try:
        from main import APP_VERSION, APP_BUILD_DATE
        return f"v{APP_VERSION} (build {APP_BUILD_DATE})"
    except ImportError:
        return "v?.?.?"


class JAWSCompatibleSearchBox(QLineEdit):
    """
    Custom QLineEdit for search box that works better with JAWS.
    Directly handles backspace and delete keys to bypass JAWS interception.
    """

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events, with special handling for backspace/delete with JAWS."""
        # Always allow backspace and delete to work normally
        if event.key() in (Qt.Key_Backspace, Qt.Key_Delete):
            # Let the default implementation handle it
            super().keyPressEvent(event)
            return

        # For all other keys, use default handling
        super().keyPressEvent(event)


class MainWindow(QMainWindow):
    """
    Main application window - Audio Book Window.
    Displays list of books with filtering and search.
    """

    ALLOWED_ALT_LETTERS = {
        'B', 'C', 'D', 'F', 'H', 'L', 'M', 'O', 'R', 'S', 'U', 'V'
    }

    def __init__(self, db: DatabaseManager, scaler: UIScaler, theme_manager: ThemeManager):
        """
        Initialize main window.

        Args:
            db: Database manager
            scaler: UI scaler
            theme_manager: Theme manager
        """
        super().__init__()

        self.db = db
        self.scaler = scaler
        self.theme_manager = theme_manager

        # Query objects
        self.book_queries = BookQueries(db)
        self.author_queries = AuthorQueries(db)
        self.series_queries = SeriesQueries(db)
        self.genre_queries = GenreQueries(db)
        self.collection_queries = CollectionQueries(db)

        # Current filter
        self.current_filter = SearchFilter()

        # Selected books (for bulk operations)
        self.selected_book_ids = set()

        # Anchor row for shift selection
        self.selection_anchor_row = None

        # Guard for selection indicator updates
        self._updating_selection_ui = False

        # Current books list
        self.books = []

        # Track last focused book in table (for ESC from search to restore focus)
        self._last_table_book_id = None
        self._last_table_column = 1

        # Search timer for debounced search
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.on_search_timeout)

        # Status message clear timer
        self.status_clear_timer = QTimer()
        self.status_clear_timer.setSingleShot(True)
        self.status_clear_timer.timeout.connect(self.clear_status_message)

        # Focus move timer (for moving focus after search completes)
        self.focus_move_timer = QTimer()
        self.focus_move_timer.setSingleShot(True)
        self.focus_move_timer.timeout.connect(self.on_focus_move_timeout)

        # Last search results count (for status messages)
        self.last_search_count = 0

        # Setup UI
        self.setup_ui()
        self.setup_shortcuts()

        # Connect to scaler changes to update header control heights
        self.scaler.scale_changed.connect(self.on_scale_changed)
        # Refresh control/table styling when theme changes
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
        # Apply initial button styling
        self.on_scale_changed(self.scaler.current_scale)

        # Load initial data
        self.refresh_collections()
        self.refresh_books()

        # Window settings
        version_str = get_app_version()
        self.setWindowTitle(
            f"AbCS - Audio Book Collector Scanner {version_str}")
        # Larger default size for better column visibility
        self.resize(1400, 800)
        # mw#22: Minimum size to prevent columns from being cut off
        self.setMinimumSize(900, 400)

        # Set focus to search field on startup for accessibility
        # Users can immediately search rather than navigate the full list
        self.search_box.setFocus()

    def setup_ui(self):
        """Setup user interface."""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Header section
        header_layout = self.create_header()
        # Wrap header layout in a widget with left alignment to prevent center stretching
        header_widget = QWidget()
        header_widget.setLayout(header_layout)
        layout.addWidget(header_widget, 0, Qt.AlignLeft | Qt.AlignTop)

        # Table for books
        self.create_table()
        layout.addWidget(self.table)

        # Footer section
        footer_layout = self.create_footer()
        layout.addLayout(footer_layout)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_hint_label = QLabel(
            "Alt+U Update, Alt+D Delete, Alt+L Cancel")
        self.status_hint_label.setVisible(False)
        self.status_hint_label.setAccessibleName("Selection shortcuts")
        self.status_hint_label.setAccessibleDescription(
            "Alt+U Update, Alt+D Delete, Alt+L Cancel"
        )
        self.status_hint_label.setFocusPolicy(Qt.StrongFocus)
        self.status_bar.insertWidget(0, self.status_hint_label, 1)
        self.status_bar.showMessage("Ready")

        # Menu bar
        self.create_menu_bar()

    def create_header(self) -> QHBoxLayout:
        """Create header with filters and search."""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Remove layout margins
        # Increased spacing between items to separate controls
        layout.setSpacing(0)

        # Set a uniform height for all controls using stylesheet
        # This is more reliable than setFixedHeight for combo boxes
        combo_stylesheet = """
            QComboBox {
                min-height: 20px;
                max-height: 20px;
                padding: 2px;
                border: 1px solid palette(dark);
                border-radius: 3px;
            }
            QComboBox:focus {
                border: 2px solid palette(highlight);
                background-color: palette(light);
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
            }
            QComboBox QAbstractItemView {
                min-height: 20px;
                outline: none;
            }
        """

        # Collection combo stylesheet with explicit width
        collection_combo_stylesheet = """
            QComboBox {
                min-height: 20px;
                max-height: 20px;
                width: 160px;
                padding: 2px;
                border: 1px solid palette(dark);
                border-radius: 3px;
            }
            QComboBox:focus {
                border: 2px solid palette(highlight);
                background-color: palette(light);
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
            }
            QComboBox QAbstractItemView {
                min-height: 20px;
                outline: none;
            }
        """

        search_stylesheet = """
            QLineEdit {
                min-height: 20px;
                max-height: 20px;
                width: 400px;
                padding: 2px 4px;
                border: 1px solid palette(dark);
                border-radius: 3px;
            }
            QLineEdit:focus {
                border: 2px solid palette(highlight);
                background-color: palette(light);
            }
        """

        # Collection filter
        self.coll_label = QLabel("Collection:")
        # mw#10: Use min-width to keep label text visible
        self.coll_label.setStyleSheet(
            "QLabel { min-width: 85px; padding-right: 5px; }")
        self.coll_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.coll_label, 0)
        layout.addSpacing(5)

        self.collection_combo = QComboBox()
        self.collection_combo.setAccessibleName("Collection filter")
        self.collection_combo.setStyleSheet(combo_stylesheet)
        # Increased width for collection names - use setFixedWidth for absolute control
        self.collection_combo.setFixedWidth(160)
        self.collection_combo.setSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.collection_combo.currentTextChanged.connect(
            self.on_collection_changed)
        layout.addWidget(self.collection_combo, 0)
        layout.addSpacing(40)

        # Read filter
        self.read_label = QLabel("Read?")
        # mw#10: Use min-width to keep label text visible
        self.read_label.setStyleSheet(
            "QLabel { min-width: 50px; }")
        self.read_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.read_label, 0)
        layout.addSpacing(5)

        self.read_combo = QComboBox()
        self.read_combo.setAccessibleName("Read filter")
        self.read_combo.addItems(["All", "Read", "Unread"])
        self.read_combo.setStyleSheet(combo_stylesheet)
        self.read_combo.setMinimumWidth(80)  # mw#10: Min width for "Unread"
        self.read_combo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.read_combo.currentTextChanged.connect(self.on_read_filter_changed)
        layout.addWidget(self.read_combo, 0)
        layout.addSpacing(40)

        # Order by
        self.order_label = QLabel("Order By:")
        # mw#10: Use min-width to keep label text visible
        self.order_label.setStyleSheet(
            "QLabel { min-width: 75px; }")
        self.order_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.order_label, 0)
        layout.addSpacing(5)

        self.order_combo = QComboBox()
        self.order_combo.setAccessibleName("Sort order")
        self.order_combo.addItems(["Title", "Author", "Genre", "Series"])
        self.order_combo.setStyleSheet(combo_stylesheet)
        self.order_combo.setMinimumWidth(90)  # mw#10: Min width for "Author"
        self.order_combo.setSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.order_combo.currentTextChanged.connect(self.on_order_changed)
        layout.addWidget(self.order_combo, 0)
        layout.addSpacing(40)

        # Search box
        self.search_label = QLabel("Search:")
        # mw#10: Use min-width to keep label text visible
        self.search_label.setStyleSheet(
            "QLabel { min-width: 60px; }")
        self.search_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.search_label, 0)
        layout.addSpacing(5)

        self.search_box = JAWSCompatibleSearchBox()
        self.search_box.setAccessibleName("Search")
        self.search_box.setPlaceholderText(
            "Type to search or ? for keyword search...")
        self.search_box.setStyleSheet(search_stylesheet)
        self.search_box.textChanged.connect(self.on_search_changed)
        self.search_box.installEventFilter(self)
        self.search_box.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.search_box, 1)  # Stretch to fill remaining space

        return layout

    def on_scale_changed(self, scale_percentage: int):
        """Update header control heights when zoom level changes."""
        # Scale the height proportionally: base is 20px at 100% scale
        base_height = 20
        scaled_height = int(base_height * (scale_percentage / 100.0))
        scaled_width = int(160 * (scale_percentage / 100.0))

        combo_stylesheet = f"""
            QComboBox {{
                min-height: {scaled_height}px;
                max-height: {scaled_height}px;
                padding: 2px;
                border: 1px solid palette(dark);
                border-radius: 3px;
            }}
            QComboBox:focus {{
                border: 2px solid palette(highlight);
                background-color: palette(light);
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
            }}
            QComboBox QAbstractItemView {{
                min-height: {scaled_height}px;
                outline: none;
            }}
        """

        collection_combo_stylesheet = f"""
            QComboBox {{
                min-height: {scaled_height}px;
                max-height: {scaled_height}px;
                width: {scaled_width}px;
                padding: 2px;
                border: 1px solid palette(dark);
                border-radius: 3px;
            }}
            QComboBox:focus {{
                border: 2px solid palette(highlight);
                background-color: palette(light);
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
            }}
            QComboBox QAbstractItemView {{
                min-height: {scaled_height}px;
                outline: none;
            }}
        """

        scaled_search_width = int(400 * (scale_percentage / 100.0))
        search_stylesheet = f"""
            QLineEdit {{
                min-height: {scaled_height}px;
                max-height: {scaled_height}px;
                width: {scaled_search_width}px;
                padding: 2px 4px;
                border: 1px solid palette(dark);
                border-radius: 3px;
            }}
            QLineEdit:focus {{
                border: 2px solid palette(highlight);
                background-color: palette(light);
            }}
        """

        # Update all combo boxes
        self.collection_combo.setStyleSheet(collection_combo_stylesheet)
        self.read_combo.setStyleSheet(combo_stylesheet)
        self.order_combo.setStyleSheet(combo_stylesheet)
        self.search_box.setStyleSheet(search_stylesheet)

        # Scale the collection combo width proportionally
        self.collection_combo.setFixedWidth(scaled_width)

        # Re-apply label widths and alignment with scaling via stylesheet
        self.coll_label.setStyleSheet(
            f"QLabel {{ min-width: {int(90 * (scale_percentage / 100.0))}px; text-align: right; }}")
        self.coll_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.read_label.setStyleSheet(
            f"QLabel {{ min-width: {int(60 * (scale_percentage / 100.0))}px; text-align: right; }}")
        self.read_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.order_label.setStyleSheet(
            f"QLabel {{ min-width: {int(80 * (scale_percentage / 100.0))}px; text-align: right; }}")
        self.order_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.search_label.setStyleSheet(
            f"QLabel {{ min-width: {int(70 * (scale_percentage / 100.0))}px; text-align: right; }}")
        self.search_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Button sizing - compact height
        button_stylesheet = f"""
            QPushButton {{
                padding: 4px 12px;
                min-height: {scaled_height}px;
                max-height: {scaled_height}px;
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
        self.update_button.setStyleSheet(button_stylesheet)
        self.delete_button.setStyleSheet(button_stylesheet)
        self.cancel_button.setStyleSheet(button_stylesheet)

    def apply_control_styles(self):
        """Re-apply dynamic styles for controls and table after theme/scale changes."""
        self.on_scale_changed(self.scaler.current_scale)
        table_header = self.table.horizontalHeader()
        table_vertical_header = self.table.verticalHeader()

        widgets_to_repolish = [
            self.collection_combo,
            self.read_combo,
            self.order_combo,
            self.search_box,
            self.coll_label,
            self.read_label,
            self.order_label,
            self.search_label,
            self.update_button,
            self.delete_button,
            self.cancel_button,
            self.table,
            self.table.viewport(),
            table_header,
            table_header.viewport(),
            table_vertical_header,
            table_vertical_header.viewport(),
        ]

        for widget in widgets_to_repolish:
            style = widget.style()
            style.unpolish(widget)
            style.polish(widget)
            widget.update()

        table_header.updateGeometry()
        table_header.viewport().update()
        table_header.repaint()

    def on_theme_changed(self, _theme_name: str):
        """Refresh main window controls/table when application theme changes."""
        self.apply_control_styles()

    def create_table(self):
        """Create books table."""
        self.table = QTableWidget()
        self.table.setAccessibleName("Audio books")
        self.table.setAccessibleDescription("List of audiobooks in collection")

        # Columns: Author, Title, Year, Plot, Series, Genre, Time, Tracks, Read, Date Added
        # mw#11: Selection checkbox column removed
        columns = ["Author", "Title", "Year", "Plot", "Series",
                   "Genre", "Time", "Tracks", "Read", "Added"]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.selection_column = -1  # No selection column

        # Table settings - SelectItems for cell-level focus, row selection handled manually
        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        # mw#22: Enable horizontal scrollbar so columns don't get cut off
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Disable hover highlighting for low-vision comfort
        self.table.setMouseTracking(False)
        self.table.viewport().setMouseTracking(False)
        self.table.setAttribute(Qt.WA_Hover, False)
        self.table.viewport().setAttribute(Qt.WA_Hover, False)
        self.table.setStyleSheet(
            """
            QTableView::item:hover { 
                background-color: palette(base); 
                color: palette(text); 
            }
            QTableView::item:focus {
                outline: none;
                border: none;
            }
            QTableView {
                outline: 0;
            }
            QTableView::item {
                padding-right: 8px;
            }
            """
        )

# Resize columns - mw#22: Author, Title, Series, Genre stretch proportionally
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setMinimumSectionSize(60)  # Prevent columns from disappearing

        # mw#22: Store stretch column proportions (relative weights)
        # Title gets 3.5x weight, Author 2.5x, Series and Genre 1.5x each
        self._stretch_columns = {
            0: 2.5,   # Author
            1: 3.5,   # Title (widest)
            4: 1.5,   # Series
            5: 1.5,   # Genre
        }

        # Fixed content columns - use ResizeToContents so they're always visible
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Year
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Plot
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Time
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Tracks
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Read
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)  # Added

        # Stretch columns use Interactive mode - we control sizing in resizeEvent
        header.setSectionResizeMode(0, QHeaderView.Interactive)  # Author
        header.setSectionResizeMode(1, QHeaderView.Interactive)  # Title
        header.setSectionResizeMode(4, QHeaderView.Interactive)  # Series
        header.setSectionResizeMode(5, QHeaderView.Interactive)  # Genre

        # Double-click to open details
        self.table.cellDoubleClicked.connect(self.on_book_double_click)

        # Selection change handler
        self.table.selectionModel().selectionChanged.connect(
            self.on_table_selection_changed)

        # Current cell change handler (screen reader announcements)
        self.table.currentCellChanged.connect(self.on_current_cell_changed)

        # Checkbox change handler
        self.table.itemChanged.connect(self.on_table_item_changed)

        # Install event filter for custom mouse handling
        self.table.viewport().installEventFilter(self)

        # Custom mouse and key handlers
        self.table.mousePressEvent = self.table_mouse_press
        self.table.mouseDoubleClickEvent = self.table_mouse_double_click  # mw#18
        self.table.keyPressEvent = self.table_key_press

    def create_footer(self) -> QHBoxLayout:
        """Create footer with action buttons and info."""
        layout = QHBoxLayout()

        # Update button (hidden initially)
        self.update_button = QPushButton("Update")
        self.update_button.setAccessibleName("Update selected books")
        self.update_button.setAccessibleDescription(
            "Update selected books - Alt+U")
        self.update_button.setFocusPolicy(Qt.StrongFocus)
        self.update_button.clicked.connect(self.on_update_clicked)
        self.update_button.setVisible(False)
        layout.addWidget(self.update_button)

        # Delete button (hidden initially)
        self.delete_button = QPushButton("Delete")
        self.delete_button.setAccessibleName("Delete selected books")
        self.delete_button.setAccessibleDescription(
            "Delete selected books - Alt+D")
        self.delete_button.setFocusPolicy(Qt.StrongFocus)
        self.delete_button.clicked.connect(self.on_delete_clicked)
        self.delete_button.setVisible(False)
        layout.addWidget(self.delete_button)

        # Cancel button (hidden initially)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setAccessibleName("Cancel selection")
        self.cancel_button.setAccessibleDescription("Cancel selection - Alt+L")
        self.cancel_button.setFocusPolicy(Qt.StrongFocus)
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        self.cancel_button.setVisible(False)
        layout.addWidget(self.cancel_button)

        # Spacer
        layout.addStretch()

        # Sort order label
        self.sort_label = QLabel("Sorted by: Title")
        layout.addWidget(self.sort_label)

        return layout

    def create_menu_bar(self):
        """Create menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        # Import is registered via setup_shortcuts

        # mw#15: New Book with Ctrl+N shortcut displayed
        new_action = QAction("&New Book\tCtrl+N", self)
        new_action.triggered.connect(self.on_new_book)
        file_menu.addAction(new_action)

        new_action = QAction("&Import", self)
        new_action.setShortcut("Ctrl+I")
        new_action.setShortcutContext(Qt.ApplicationShortcut)
        new_action.triggered.connect(self.on_import)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        # mw#17: Book Details at top of View menu
        book_details_action = QAction("&Book Details", self)
        book_details_action.setShortcut("Ctrl+Return")
        book_details_action.triggered.connect(self.on_open_book_details)
        view_menu.addAction(book_details_action)

        view_menu.addSeparator()

        prefs_action = QAction("&Authors", self)
        prefs_action.triggered.connect(self.on_show_authors)
        view_menu.addAction(prefs_action)

        prefs_action = QAction("&Collections", self)
        prefs_action.triggered.connect(self.on_show_collection)
        view_menu.addAction(prefs_action)

        prefs_action = QAction("&Genre", self)
        prefs_action.triggered.connect(self.on_show_Genre)
        view_menu.addAction(prefs_action)

        prefs_action = QAction("&Series", self)
        prefs_action.triggered.connect(self.on_show_Series)
        view_menu.addAction(prefs_action)

        file_menu.addSeparator()

        # mw#16: Zoom actions with shortcut keys displayed
        zoom_in_action = QAction("Zoom &In\tCtrl++", self)
        zoom_in_action.triggered.connect(self.on_zoom_in)
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom &Out\tCtrl+-", self)
        zoom_out_action.triggered.connect(self.on_zoom_out)
        view_menu.addAction(zoom_out_action)

        zoom_reset_action = QAction("&Reset Zoom\tCtrl+0", self)
        zoom_reset_action.triggered.connect(self.on_zoom_reset)
        view_menu.addAction(zoom_reset_action)

        # manage menu
        view_menu = menubar.addMenu("&Manage")

        prefs_action = QAction("&Preferences...", self)
        prefs_action.triggered.connect(self.on_preferences)
        view_menu.addAction(prefs_action)

        prefs_action = QAction("&Backup & Restore", self)
        prefs_action.triggered.connect(self.on_backup_restore)
        view_menu.addAction(prefs_action)

        splash_action = QAction("&Statistics...", self)
        splash_action.triggered.connect(self.on_show_splash)
        view_menu.addAction(splash_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About AbCS...", self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)

        shortcuts_action = QAction("&Keyboard Shortcuts", self)
        shortcuts_action.triggered.connect(self.on_show_shortcuts)
        help_menu.addAction(shortcuts_action)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        shortcut_mgr = get_shortcut_manager()

        # Alt+Key shortcuts
        callback_map = {
            'collection_combo': lambda: self.collection_combo.setFocus(),
            'read_combo': lambda: self.read_combo.setFocus(),
            'order_combo': lambda: self.order_combo.setFocus(),
            'search_box': lambda: (self.search_box.setFocus(), self.search_box.selectAll()),
            'menu_combo': lambda: self.menu_combo.setFocus(),
            'book_list': self.focus_book_title,
            'update_button': self.on_update_clicked,
            'delete_button': self.on_delete_clicked,
            'cancel_button': self.on_cancel_clicked,
        }
        shortcut_mgr.register_alt_shortcuts(
            self, ShortcutContext.MAIN_WINDOW, callback_map)

        # Zoom shortcuts - register as proper QShortcut objects
        # Store references to prevent garbage collection
        # Register both keyboard and numpad versions
        # Zoom In: Ctrl++ (keyboard) and Ctrl+Plus (numpad)
        self.zoom_in_shortcut = QShortcut(QKeySequence("Ctrl++"), self)
        self.zoom_in_shortcut.activated.connect(self.on_zoom_in)

        self.zoom_in_numpad_shortcut = QShortcut(
            QKeySequence("Ctrl+Num++"), self)
        self.zoom_in_numpad_shortcut.activated.connect(self.on_zoom_in)

        # Zoom Out: Ctrl+- (keyboard) and Ctrl+Minus (numpad)
        self.zoom_out_shortcut = QShortcut(QKeySequence("Ctrl+-"), self)
        self.zoom_out_shortcut.activated.connect(self.on_zoom_out)

        self.zoom_out_numpad_shortcut = QShortcut(
            QKeySequence("Ctrl+Num+-"), self)
        self.zoom_out_numpad_shortcut.activated.connect(self.on_zoom_out)

        # Zoom Reset: Ctrl+0 (both keyboard and numpad should work)
        self.zoom_reset_shortcut = QShortcut(QKeySequence("Ctrl+0"), self)
        self.zoom_reset_shortcut.activated.connect(self.on_zoom_reset)

        # Help shortcut: F1 opens keyboard shortcuts help
        self.help_shortcut = QShortcut(QKeySequence("F1"), self)
        self.help_shortcut.activated.connect(self.on_show_shortcuts)

        # mw#15: Ctrl+N for new book
        self.new_book_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        self.new_book_shortcut.activated.connect(self.on_new_book)

        # mw#19: Ctrl+Enter handled by menu action and table_key_press
        # (No separate QShortcut to avoid ambiguous shortcut error)

        # mw#24: Alt+/ reads status bar aloud
        self.status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.status_shortcut.activated.connect(self.on_read_status_bar)

        # ESC shortcut at window level - clears selection or search
        self.escape_shortcut = QShortcut(QKeySequence("Escape"), self)
        self.escape_shortcut.activated.connect(self.on_escape_pressed)

        # mw#23: Alt+1 through Alt+0 to jump to table columns
        # Columns: 0=Author, 1=Title, 2=Year, 3=Plot, 4=Series, 5=Genre, 6=Time, 7=Tracks, 8=Read, 9=Added
        self.column_shortcuts = []
        for i in range(10):
            shortcut = QShortcut(QKeySequence(
                f"Alt+{(i + 1) % 10}"), self)  # Alt+1..9, Alt+0
            shortcut.activated.connect(lambda col=i: self.jump_to_column(col))
            self.column_shortcuts.append(shortcut)

    def jump_to_column(self, column: int):
        """mw#23: Jump to specified column in the book table."""
        if self.table.rowCount() == 0:
            self.table.setFocus()
            return

        row = self.table.currentRow()
        if row < 0:
            row = 0

        if column >= self.table.columnCount():
            column = self.table.columnCount() - 1

        index = self.table.model().index(row, column)
        self.table.selectionModel().setCurrentIndex(index, QItemSelectionModel.NoUpdate)
        self.table.scrollTo(index)
        self.table.setFocus()

    # ========== Status Bar Helper Methods (Simplified) ==========
    def get_default_status(self) -> str:
        """Get the default status message based on current state."""
        # Priority 1: Show selection count if items are selected
        if self.selected_book_ids:
            count = len(self.selected_book_ids)
            shortcuts = "Alt+U Update, Alt+D Delete, Alt+L Cancel"

            # Include title of currently focused book (same as announce_selection)
            current_row = self.table.currentRow()
            if 0 <= current_row < len(self.books):
                title = self.books[current_row].title or "Unknown"
                if count == 1:
                    return f"{title} - selected. {shortcuts}"
                else:
                    return f"{title} - {count} selected. {shortcuts}"
            return f"{count} selected. {shortcuts}"

        # Priority 2: Show search results if search is active
        if self.current_filter.search_text:
            search_text = self.current_filter.search_text
            if search_text.startswith('?'):
                search_text = search_text[1:]
            count = len(self.books)
            order_by = self.current_filter.order_by
            if count == 0:
                return f"No {order_by.lower()}s found matching '{search_text}'. Esc to exit search"
            elif count == 1:
                return f"Found 1 {order_by.lower()}: {search_text}. Esc to exit search"
            else:
                return f"Found {count} {order_by.lower()}s matching '{search_text}'. Esc to exit search"

        # Priority 3: Show filtered book count with all active filters
        parts = [f"Showing {len(self.books)} books"]

        # mw#12: Show current sort order (especially Series/Genre)
        order_by = self.current_filter.order_by
        if order_by and order_by != "Title":  # Only show if not default
            parts.append(f"by {order_by}")

        # Read filter
        if self.current_filter.read_filter == "Read":
            parts.append("Read")
        elif self.current_filter.read_filter == "Unread":
            parts.append("Unread")

        # Collection filter
        if self.current_filter.collection_id is not None:
            parts.append(self.collection_combo.currentText())

        return " • ".join(parts)

    def set_status(self, message: str, timeout_ms: int = 0, announce: bool = True):
        """
        Set status bar message with optional screen reader announcement.

        Args:
            message: Message to display
            timeout_ms: If > 0, message will clear to default after this delay.
                       If 0, message stays until manually changed.
            announce: If True, briefly move focus to status bar so JAWS/NVDA read it
        """
        self.status_bar.showMessage(message)

        # Announce to screen readers by briefly moving focus (JAWS/NVDA workaround)
        if announce and QAccessible.isActive():
            previous_focus = QApplication.instance().focusWidget()

            # Temporarily make status bar focusable
            self.status_bar.setFocusPolicy(Qt.StrongFocus)
            self.status_bar.setFocus()

            # Restore focus after screen reader reads message
            def restore_focus():
                if previous_focus:
                    previous_focus.setFocus()
                self.status_bar.setFocusPolicy(Qt.NoFocus)

            QTimer.singleShot(100, restore_focus)

        if timeout_ms > 0:
            self.status_clear_timer.stop()
            self.status_clear_timer.start(timeout_ms)

    def set_default_status(self, announce: bool = False):
        """
        Set status bar to the default message for current state.

        Args:
            announce: If True, announce to screen readers (default False for passive updates)
        """
        self.set_status(self.get_default_status(),
                        timeout_ms=0, announce=announce)

    def on_read_status_bar(self):
        """mw#24: Alt+/ reads status bar. Shows message if no screen reader active."""
        if QAccessible.isActive():
            # Announce status bar to screen reader
            self.set_status(self.get_default_status(),
                            timeout_ms=0, announce=True)
        else:
            # No screen reader detected - show message box for testing
            QMessageBox.information(self, "Status Bar",
                                    f"No screen reader active.\n\nStatus: {self.get_default_status()}")

    def on_open_book_details(self):
        """mw#17,19: Open book details for current book (Ctrl+Enter)."""
        if self.selected_book_ids:
            # If items are selected, don't open details
            return

        # Ensure table has focus and get current row
        row = self.table.currentRow()
        if row < 0 and self.table.rowCount() > 0:
            row = 0  # Default to first row if none selected

        if 0 <= row < len(self.books):
            book = self.books[row]
            self.open_book_details(book)

    # ========== End Status Bar Helpers ==========

    def refresh_collections(self):
        """Refresh collection combo box."""
        self.collection_combo.clear()
        self.collection_combo.addItem("All Collections", None)

        collections = self.collection_queries.get_all(active_only=True)
        for coll in collections:
            self.collection_combo.addItem(coll.name, coll.collection_id)

    def clear_all_filters(self):
        """Clear all filters and search, reset to show all books."""
        # Block signals to prevent multiple refreshes
        self.search_box.blockSignals(True)
        self.collection_combo.blockSignals(True)
        self.read_combo.blockSignals(True)

        try:
            # Clear search box
            self.search_box.clear()

            # Reset combos to "All"
            self.collection_combo.setCurrentIndex(0)  # "All Collections"
            self.read_combo.setCurrentIndex(0)  # "All"

            # Reset filter object
            self.current_filter.search_text = ""
            self.current_filter.is_keyword_search = False
            self.current_filter.collection_id = None
            self.current_filter.read_filter = "All"
            # Keep order_by unchanged
        finally:
            self.search_box.blockSignals(False)
            self.collection_combo.blockSignals(False)
            self.read_combo.blockSignals(False)

    def has_active_filters(self) -> bool:
        """Check if any filters or search are active."""
        return bool(
            self.current_filter.search_text or
            self.current_filter.collection_id is not None or
            self.current_filter.read_filter != "All"
        )

    def refresh_books(self):
        """Refresh books table based on current filter."""
        # BLOCK ALL EVENTS - This is critical!
        self.table.blockSignals(True)

        try:
            # Get books from database
            self.books = self.book_queries.get_all(self.current_filter)

            # DISABLE UPDATES WHILE POPULATING TABLE
            self.table.setUpdatesEnabled(False)
            # CRITICAL: Disable sorting during population
            self.table.setSortingEnabled(False)

            # Clear table completely - setRowCount(0) is cleaner than clearContents
            # clearContents() leaves internal Qt structures that accumulate over time
            self.table.setRowCount(0)  # Complete reset, not just clearContents
            self.table.setRowCount(len(self.books))

            for row, book in enumerate(self.books):
                # Create new items - handle None values defensively
                # Set accessible text to suppress row number announcements in JAWS
                author_item = QTableWidgetItem(book.author_name or "")
                author_item.setData(Qt.AccessibleTextRole,
                                    book.author_name or "")
                self.table.setItem(row, 0, author_item)

                title_item = QTableWidgetItem(book.title or "")
                title_item.setData(Qt.AccessibleTextRole, book.title or "")
                self.table.setItem(row, 1, title_item)

                year_str = str(book.year) if book.year else ""
                year_item = QTableWidgetItem(year_str)
                year_item.setData(Qt.AccessibleTextRole, year_str)
                year_item.setData(
                    Qt.AccessibleDescriptionRole,
                    f"{book.title or ''} by {book.author_name or ''}".strip()
                )
                self.table.setItem(row, 2, year_item)

                # Plot (comments) indicator column - "Yes" if comments > 100 chars
                plot_text = "Yes" if book.has_substantial_comment else ""
                plot_item = QTableWidgetItem(plot_text)
                plot_item.setData(Qt.AccessibleTextRole, plot_text)
                plot_item.setData(
                    Qt.AccessibleDescriptionRole,
                    f"{book.title or ''} by {book.author_name or ''}".strip()
                )
                self.table.setItem(row, 3, plot_item)

                series_item = QTableWidgetItem(book.series_name or "")
                series_item.setData(Qt.AccessibleTextRole,
                                    book.series_name or "")
                series_item.setData(
                    Qt.AccessibleDescriptionRole,
                    f"{book.title or ''} by {book.author_name or ''}".strip()
                )
                self.table.setItem(row, 4, series_item)

                genre_item = QTableWidgetItem(book.genre_name or "")
                genre_item.setData(Qt.AccessibleTextRole,
                                   book.genre_name or "")
                genre_item.setData(
                    Qt.AccessibleDescriptionRole,
                    f"{book.title or ''} by {book.author_name or ''}".strip()
                )
                self.table.setItem(row, 5, genre_item)

                time_item = QTableWidgetItem(book.time_display or "")
                time_item.setData(Qt.AccessibleTextRole,
                                  book.time_display or "")
                time_item.setData(
                    Qt.AccessibleDescriptionRole,
                    f"{book.title or ''} by {book.author_name or ''}".strip()
                )
                self.table.setItem(row, 6, time_item)

                tracks_str = str(book.tracks or 0)
                tracks_item = QTableWidgetItem(tracks_str)
                tracks_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                tracks_item.setData(Qt.AccessibleTextRole, tracks_str)
                tracks_item.setData(
                    Qt.AccessibleDescriptionRole,
                    f"{book.title or ''} by {book.author_name or ''}".strip()
                )
                self.table.setItem(row, 7, tracks_item)

                # Read date column
                if book.read_date:
                    if isinstance(book.read_date, str):
                        read_date_str = book.read_date[:10]
                    else:
                        read_date_str = book.read_date.strftime("%Y-%m-%d")
                else:
                    read_date_str = ""
                read_item = QTableWidgetItem(read_date_str)
                read_item.setData(Qt.AccessibleTextRole, read_date_str)
                read_item.setData(
                    Qt.AccessibleDescriptionRole,
                    f"{book.title or ''} by {book.author_name or ''}".strip()
                )
                self.table.setItem(row, 8, read_item)

                # Date Added
                if book.date_added:
                    if isinstance(book.date_added, str):
                        date_str = book.date_added[:10]
                    else:
                        date_str = book.date_added.strftime("%Y-%m-%d")
                else:
                    date_str = ""
                added_item = QTableWidgetItem(date_str)
                added_item.setData(Qt.AccessibleTextRole, date_str)
                added_item.setData(
                    Qt.AccessibleDescriptionRole,
                    f"{book.title or ''} by {book.author_name or ''}".strip()
                )
                self.table.setItem(row, 9, added_item)

                # mw#11: Selection checkbox column removed - selection indicated by row highlight

            # RE-ENABLE UPDATES FIRST
            self.table.setUpdatesEnabled(True)

            # Sync selection indicators after repopulating
            self.sync_selection_indicators()

            # Set empty vertical header labels to prevent JAWS from reading row numbers
            # Even though header is hidden, JAWS still accesses it via accessibility API
            vertical_header_labels = [""] * len(self.books)
            self.table.setVerticalHeaderLabels(vertical_header_labels)

            # Update status bar with filter info
            filter_info = ""
            if self.current_filter.read_filter == "Read":
                filter_info = " • Read"
            elif self.current_filter.read_filter == "Unread":
                filter_info = " • Unread"

            collection_info = ""
            if self.current_filter.collection_id is not None:
                # Find collection name
                collection_item = self.collection_combo.currentData()
                if collection_item:
                    collection_info = f" • {self.collection_combo.currentText()}"

            self.set_default_status(announce=True)

        except Exception as e:
            self.table.setUpdatesEnabled(True)
            self.set_status(f"Error loading books: {e}", timeout_ms=3000)

        finally:
            # ALWAYS UNBLOCK SIGNALS - even on error
            self.table.blockSignals(False)
            # Re-enable sorting AFTER unblocking signals
            self.table.setSortingEnabled(True)
            # Allow Qt to process input events (search box keystrokes, etc.)
            QApplication.instance().processEvents()

    # Event handlers

    def on_collection_changed(self):
        """Handle collection filter change."""
        coll_id = self.collection_combo.currentData()
        self.current_filter.collection_id = coll_id
        self.refresh_books()

    def on_read_filter_changed(self, text: str):
        """Handle read filter change."""
        self.current_filter.read_filter = text
        self.refresh_books()

    def on_order_changed(self, text: str):
        """Handle sort order change."""
        # Update filter BEFORE calling refresh to ensure correct order is used
        self.current_filter.order_by = text
        self.sort_label.setText(f"Sorted by: {text}")
        # Only refresh books (no double refresh from combo signal)
        self.refresh_books()

    def on_search_changed(self, text: str):
        """Handle search text change."""
        self.current_filter.search_text = text
        self.current_filter.is_keyword_search = text.startswith('?')

        # Stop existing timer
        self.search_timer.stop()

        # If empty, clear search immediately (without status - eventFilter handles this)
        if not text:
            self.current_filter.search_text = ""
            # Only refresh if we were actually filtering (avoid redundant refresh)
            if self.current_filter.search_text or self.current_filter.read_filter or self.current_filter.collection_id:
                self.refresh_books()
            return

        # Keyword search (starts with ?) requires Enter key
        if text.startswith('?'):
            # Don't filter yet - wait for Enter
            return

        # Live filtering: filter as user types (with debounce)
        self.search_timer.start(300)  # 300ms debounce for responsiveness

    def on_search_enter(self):
        """Handle Enter key in search box."""
        # Stop any pending live search timer immediately
        self.search_timer.stop()

        search_text = self.search_box.text().strip()
        if not search_text:
            return

        # Determine if this is a keyword search (contains ?) and strip it
        is_keyword = search_text.startswith('?')
        if is_keyword:
            search_text = search_text[1:].strip()

        # Update filter with final search text
        self.current_filter.search_text = search_text
        self.current_filter.is_keyword_search = is_keyword

        # Perform search
        self.refresh_books()

        # Move focus to first search result using timer to ensure it happens after all events
        if len(self.books) > 0:
            def move_focus():
                # Focus the appropriate column based on order-by setting
                self.focus_search_result_cell(0)
                # Explicitly set focus to table AFTER setting cell (critical for keyboard nav)
                self.table.setFocus(Qt.TabFocusReason)
                # Announce search results
                self.set_status(self.get_default_status(),
                                timeout_ms=0, announce=False)

            # Use slightly longer delay to ensure refresh is complete
            QTimer.singleShot(150, move_focus)
        else:
            # No results - just show status
            self.set_status(self.get_default_status(),
                            timeout_ms=0, announce=False)

    def focus_search_result_cell(self, row: int):
        """Focus the result cell that matches the current order-by field."""
        order_column_map = {
            "Author": 0,
            "Title": 1,
            "Series": 4,
            "Genre": 5,
        }
        column = order_column_map.get(self.order_combo.currentText(), 1)
        if 0 <= row < self.table.rowCount():
            # Clear any existing selection
            self.table.clearSelection()
            # First scroll to ensure visibility
            index = self.table.model().index(row, column)
            self.table.scrollTo(index, QAbstractItemView.PositionAtCenter)
            # Set current cell - this highlights and focuses
            self.table.setCurrentCell(row, column)
            # Also select the cell to ensure visible highlight
            self.table.setCurrentIndex(index)

    def focus_book_by_id(self, book_id: int, column: int = 1):
        """Find a book by ID and focus its cell in the table."""
        found = False
        target_row = 0

        for row, book in enumerate(self.books):
            if book.book_id == book_id:
                target_row = row
                found = True
                break

        # Ensure valid column
        if column < 0 or column >= self.table.columnCount():
            column = 1  # Default to Title column

        # If not found, just focus row 0
        if not found and len(self.books) > 0:
            target_row = 0

        # Focus the cell (even if book not found, focus something)
        if self.table.rowCount() > 0:
            self.table.clearSelection()
            index = self.table.model().index(target_row, column)
            self.table.scrollTo(index, QAbstractItemView.PositionAtCenter)
            self.table.setCurrentCell(target_row, column)
            self.table.setCurrentIndex(index)

        # Always ensure table has focus for keyboard navigation
        self.table.setFocus(Qt.TabFocusReason)
        return found

    def on_search_timeout(self):
        """Handle search timer timeout for live filtering."""
        # This is called after user stops typing (300ms debounce)
        self.refresh_books()
        self.show_search_results_message()

    def on_book_double_click(self, row: int, column: int):
        """Handle double-click on book."""
        if 0 <= row < len(self.books):
            book = self.books[row]
            self.open_book_details(book)

    def on_table_selection_changed(self):
        """Handle table selection change and announce selection."""
        # Skip if we're programmatically updating selection
        if self._updating_selection_ui:
            return

        # With SelectItems mode, count cells per row to find fully selected rows
        model = self.table.selectionModel()
        selected_indexes = model.selectedIndexes()
        self.selected_book_ids.clear()

        # Count how many cells are selected per row
        row_cell_counts = {}
        for idx in selected_indexes:
            row = idx.row()
            row_cell_counts[row] = row_cell_counts.get(row, 0) + 1

        # A row is fully selected if all columns are selected
        col_count = self.table.columnCount()
        for row, count in row_cell_counts.items():
            if count == col_count and 0 <= row < len(self.books):
                self.selected_book_ids.add(self.books[row].book_id)

        self.update_selection_ui()

        # Announce selection for screen readers
        if len(self.selected_book_ids) > 0:
            self.announce_selection()

    def eventFilter(self, source, event):
        """Filter events to implement Explorer-like selection and handle search ESC and Enter."""
        if source is self.search_box and event.type() == QEvent.KeyPress:
            if is_unmapped_alt_letter(event, self.ALLOWED_ALT_LETTERS):
                event.accept()
                return True
            if event.key() == Qt.Key_Escape:
                # Use last table position (tracked by on_current_cell_changed)
                restore_book_id = self._last_table_book_id
                restore_column = self._last_table_column if self._last_table_column >= 0 else 1

                # Clear search box and filter efficiently
                # Disconnect signal temporarily to avoid double refresh
                self.search_box.textChanged.disconnect(self.on_search_changed)
                self.search_box.clear()
                self.search_box.textChanged.connect(self.on_search_changed)

                # Clear search filter and refresh once
                self.current_filter.search_text = ""
                self.search_timer.stop()
                self.refresh_books()

                # Always restore focus to table after clearing search
                def restore_focus():
                    if restore_book_id is not None:
                        self.focus_book_by_id(restore_book_id, restore_column)
                    else:
                        # No book to restore - just focus first row
                        if self.table.rowCount() > 0:
                            self.table.setCurrentCell(0, 1)
                        self.table.setFocus(Qt.TabFocusReason)
                QTimer.singleShot(150, restore_focus)

                self.set_status("Search cleared",
                                timeout_ms=2000, announce=False)
                return True
            elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
                # Handle Enter in search box - perform immediate search
                self.on_search_enter()
                return True  # Consume the event so search box doesn't process it
            # Let all other keys (including backspace) pass through normally
            return False
        if hasattr(self, 'table') and source is self.table.viewport() and event.type() == QEvent.MouseButtonPress:
            # Let mouse press be handled by our custom handler
            return False
        return super().eventFilter(source, event)

    def on_table_item_changed(self, item: QTableWidgetItem):
        """Handle checkbox changes in selection column."""
        if self._updating_selection_ui:
            return

        if item.column() != self.selection_column:
            return

        row = item.row()
        if row < 0 or row >= len(self.books):
            return

        book_id = self.books[row].book_id
        is_checked = item.checkState() == Qt.Checked

        model = self.table.selectionModel()
        index = self.table.model().index(row, 0)

        if is_checked:
            model.select(index, QItemSelectionModel.Select |
                         QItemSelectionModel.Rows)
            self.selected_book_ids.add(book_id)
            self.selection_anchor_row = row
        else:
            model.select(index, QItemSelectionModel.Deselect |
                         QItemSelectionModel.Rows)
            self.selected_book_ids.discard(book_id)
            if not self.selected_book_ids:
                self.selection_anchor_row = None

        self.update_selection_ui()

    def table_mouse_press(self, event):
        """Handle mouse press - Explorer-like selection behavior."""
        if event.button() == Qt.LeftButton:
            index = self.table.indexAt(event.position().toPoint())
            if not index.isValid():
                QTableWidget.mousePressEvent(self.table, event)
                return

            modifiers = event.modifiers()
            row = index.row()

            # Shift+Click: Range select from anchor to clicked row
            if modifiers & Qt.ShiftModifier:
                if self.selection_anchor_row is None:
                    self.selection_anchor_row = row

                start_row = min(self.selection_anchor_row, row)
                end_row = max(self.selection_anchor_row, row)

                self._updating_selection_ui = True
                self.table.selectionModel().clearSelection()

                # Select all cells in each row
                col_count = self.table.columnCount()
                for r in range(start_row, end_row + 1):
                    for c in range(col_count):
                        idx = self.table.model().index(r, c)
                        self.table.selectionModel().select(idx, QItemSelectionModel.Select)

                self.table.setCurrentCell(row, index.column())
                self._updating_selection_ui = False

                # Sync selection tracking
                self.selected_book_ids.clear()
                for r in range(start_row, end_row + 1):
                    if 0 <= r < len(self.books):
                        self.selected_book_ids.add(self.books[r].book_id)
                self.update_selection_ui()
                self.announce_selection()
                event.accept()
                return

            # Plain click: clear selection and move to clicked cell
            self.table.clearSelection()
            self.selected_book_ids.clear()
            self.selection_anchor_row = None  # Reset anchor for keyboard selection
            self.table.setCurrentCell(index.row(), index.column())
            self.update_selection_ui()
            event.accept()
            return

        QTableWidget.mousePressEvent(self.table, event)

    def table_mouse_double_click(self, event):
        """Handle mouse double-click - opens book details."""
        if event.button() == Qt.LeftButton:
            index = self.table.indexAt(event.position().toPoint())
            if index.isValid():
                row = index.row()
                if 0 <= row < len(self.books):
                    book = self.books[row]
                    self.open_book_details(book)
                    event.accept()
                    return
        QTableWidget.mouseDoubleClickEvent(self.table, event)

    def table_key_press(self, event: QKeyEvent):
        """Handle key press in table."""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            # mw#19: Only Ctrl+Enter opens book details
            if event.modifiers() & Qt.ControlModifier:
                if not self.selected_book_ids:
                    row = self.table.currentRow()
                    if 0 <= row < len(self.books):
                        book = self.books[row]
                        self.open_book_details(book)
            event.accept()
            return
        elif event.key() in (Qt.Key_Up, Qt.Key_Down, Qt.Key_PageUp, Qt.Key_PageDown, Qt.Key_Home, Qt.Key_End):
            modifiers = event.modifiers()

            # Shift+Arrow: Only extend selection if already in selection mode (anchor set via Shift+Space)
            if modifiers & Qt.ShiftModifier:
                if self.selection_anchor_row is not None:
                    # In selection mode - extend selection
                    self.extend_selection_with_arrow(event.key())
                    event.accept()
                    return
                # Not in selection mode - treat as plain arrow (move without selecting)
                self.move_current_without_selection(event.key())
                event.accept()
                return

            # Ctrl+Arrow: just move (Qt default)
            if modifiers & Qt.ControlModifier:
                QTableWidget.keyPressEvent(self.table, event)
                return

            # Plain arrow: move without selection
            self.move_current_without_selection(event.key())
            event.accept()
            return
        elif event.key() in (Qt.Key_Left, Qt.Key_Right):
            # Left/Right arrows: move between columns
            self.move_column_without_selection(event.key())
            event.accept()
            return
        elif event.key() == Qt.Key_Space:
            modifiers = event.modifiers()
            # Shift+Space: Enter selection mode - select current row and set anchor
            if modifiers & Qt.ShiftModifier:
                row = self.table.currentRow()
                if 0 <= row < len(self.books):
                    self._updating_selection_ui = True
                    self.selection_anchor_row = row
                    # Select all cells in this row (for SelectItems mode)
                    self.table.selectionModel().clearSelection()
                    for col in range(self.table.columnCount()):
                        index = self.table.model().index(row, col)
                        self.table.selectionModel().select(
                            index, QItemSelectionModel.Select)
                    self._updating_selection_ui = False
                    # Manually sync selection
                    self.selected_book_ids.clear()
                    self.selected_book_ids.add(self.books[row].book_id)
                    self.update_selection_ui()
                    self.announce_selection()
            # Plain space does nothing
            event.accept()
            return
        elif event.key() == Qt.Key_Escape:
            # ESC clears selection first, then clears search
            if self.selected_book_ids or self.selection_anchor_row is not None:
                # Clear selection (same as Cancel button)
                self.on_cancel_clicked()
                event.accept()
                return
            # ESC: Clear search if active (keep focus on table)
            if self.current_filter.has_search:
                # Use tracked book ID (set by on_current_cell_changed)
                restore_book_id = self._last_table_book_id
                restore_column = self._last_table_column if self._last_table_column >= 0 else 1

                # Disconnect to avoid double refresh
                self.search_box.textChanged.disconnect(self.on_search_changed)
                self.search_box.clear()
                self.search_box.textChanged.connect(self.on_search_changed)

                # Clear search filter and refresh
                self.current_filter.search_text = ""
                self.search_timer.stop()
                self.refresh_books()

                # Restore focus to the actual book that was selected
                def restore_focus():
                    if restore_book_id is not None:
                        self.focus_book_by_id(restore_book_id, restore_column)
                    else:
                        if self.table.rowCount() > 0:
                            self.table.setCurrentCell(0, 1)
                        self.table.setFocus(Qt.TabFocusReason)
                QTimer.singleShot(150, restore_focus)

                self.set_status("Search cleared", timeout_ms=2000)
                event.accept()
                return
        else:
            # Call original key press handler
            QTableWidget.keyPressEvent(self.table, event)

    def focus_book_title(self):
        """Focus book table and move to the Title column."""
        if self.table.rowCount() == 0:
            self.table.setFocus()
            return

        row = self.table.currentRow()
        if row < 0:
            row = 0

        title_col = 1
        index = self.table.model().index(row, title_col)
        self.table.selectionModel().setCurrentIndex(
            index, QItemSelectionModel.NoUpdate)
        self.table.scrollTo(index)
        self.table.setFocus()

    def move_current_without_selection(self, key: int):
        """Move current cell and clear selection when navigating with arrows."""
        row_count = self.table.rowCount()
        col_count = self.table.columnCount()
        if row_count == 0 or col_count == 0:
            return

        row = self.table.currentRow()
        col = self.table.currentColumn()
        if row < 0:
            row = 0
        if col < 0:
            col = 0

        page_step = max(self.table.verticalScrollBar().pageStep() - 1, 1)

        # Track if we're changing rows (not just columns)
        changing_rows = False

        if key == Qt.Key_Up:
            row = max(row - 1, 0)
            changing_rows = True
        elif key == Qt.Key_Down:
            row = min(row + 1, row_count - 1)
            changing_rows = True
        elif key == Qt.Key_Left:
            col = max(col - 1, 0)
        elif key == Qt.Key_Right:
            col = min(col + 1, col_count - 1)
        elif key == Qt.Key_PageUp:
            row = max(row - page_step, 0)
            changing_rows = True
        elif key == Qt.Key_PageDown:
            row = min(row + page_step, row_count - 1)
            changing_rows = True
        elif key == Qt.Key_Home:
            row = 0
            changing_rows = True
        elif key == Qt.Key_End:
            row = row_count - 1
            changing_rows = True

        # Only clear selection when changing rows, not for left/right
        if changing_rows:
            # Use flag to prevent selection change handler from triggering
            self._updating_selection_ui = True

            # Clear any existing selections when navigating up/down
            self.table.clearSelection()
            self.table.selectionModel().clearSelection()
            self.selected_book_ids.clear()
            self.selection_anchor_row = None

        # Set current cell - this properly sets both row selection and cell focus
        self.table.setCurrentCell(row, col)
        self.table.scrollTo(self.table.model().index(row, col))

        if changing_rows:
            self._updating_selection_ui = False

            # Update UI to clear selection display
            self.update_selection_ui()

            # Show book count message after clearing selection
            self.clear_status_message()

    def move_column_without_selection(self, key: int):
        """Move between columns without affecting selection or row focus."""
        col_count = self.table.columnCount()
        if col_count == 0:
            return

        col = self.table.currentColumn()
        if col < 0:
            col = 0

        if key == Qt.Key_Left:
            col = max(col - 1, 0)
        elif key == Qt.Key_Right:
            col = min(col + 1, col_count - 1)

        row = self.table.currentRow()
        if row < 0:
            row = 0

        # Use setCurrentCell for proper cell focus
        self.table.setCurrentCell(row, col)
        self.table.scrollTo(self.table.model().index(row, col))

    def extend_selection_with_arrow(self, key: int):
        """Extend selection with Shift+Arrow from anchor (set by Shift+Space)."""
        row_count = self.table.rowCount()
        if row_count == 0:
            return

        row = self.table.currentRow()
        col = self.table.currentColumn()
        if row < 0:
            row = 0
        if col < 0:
            col = 0

        page_step = max(self.table.verticalScrollBar().pageStep() - 1, 1)

        # Calculate target row
        target_row = row
        if key == Qt.Key_Up:
            target_row = max(row - 1, 0)
        elif key == Qt.Key_Down:
            target_row = min(row + 1, row_count - 1)
        elif key == Qt.Key_PageUp:
            target_row = max(row - page_step, 0)
        elif key == Qt.Key_PageDown:
            target_row = min(row + page_step, row_count - 1)
        elif key == Qt.Key_Home:
            target_row = 0
        elif key == Qt.Key_End:
            target_row = row_count - 1

        # Extend from anchor to target
        start_row = min(self.selection_anchor_row, target_row)
        end_row = max(self.selection_anchor_row, target_row)

        # Use flag to prevent selection change handler from interfering
        self._updating_selection_ui = True

        # Clear current selection first
        self.table.selectionModel().clearSelection()

        # Select all cells in each row (for SelectItems mode)
        col_count = self.table.columnCount()
        for r in range(start_row, end_row + 1):
            for c in range(col_count):
                index = self.table.model().index(r, c)
                self.table.selectionModel().select(
                    index, QItemSelectionModel.Select)

        self.table.setCurrentCell(target_row, col)
        self.table.scrollTo(self.table.model().index(target_row, col))

        self._updating_selection_ui = False

        # Now manually sync selection tracking
        self.selected_book_ids.clear()
        for r in range(start_row, end_row + 1):
            if 0 <= r < len(self.books):
                self.selected_book_ids.add(self.books[r].book_id)
        self.update_selection_ui()
        self.announce_selection()

    def move_cursor_to_row(self, row: int):
        """Scroll the specified row into view."""
        if 0 <= row < self.table.rowCount():
            # Use Title column (column 1) which always has content
            col = 1
            # Scroll to make the row visible
            index = self.table.model().index(row, col)
            self.table.scrollTo(index)

    def on_current_cell_changed(self, current_row: int, current_col: int, previous_row: int, previous_col: int):
        """Handle current cell changes - track last focused book for search ESC restore."""
        # Track the last focused book in the table for ESC from search restore
        if 0 <= current_row < len(self.books):
            self._last_table_book_id = self.books[current_row].book_id
            self._last_table_column = current_col if current_col >= 0 else 1

    def on_focus_move_timeout(self):
        """Move focus to first search result after delay."""
        if len(self.books) > 0:
            self.focus_search_result_cell(0)

    def announce_current_cell(self, force: bool = False):
        """Announce current cell value to the status bar for screen readers."""
        # Do not announce during selection operations (unless forced)
        if not force and hasattr(self, "selected_book_ids") and self.selected_book_ids:
            return

        row = self.table.currentRow()
        col = self.table.currentColumn()
        if row < 0 or col < 0:
            return

        if row >= len(self.books):
            return

        book = self.books[row]
        header_item = self.table.horizontalHeaderItem(col)
        header_text = header_item.text() if header_item else "Field"

        # Build announcement with book context
        value_text = ""
        if col == 0:  # Author
            value_text = book.author_name or "blank"
        elif col == 1:  # Title
            value_text = book.title or "blank"
        elif col == 2:  # Year
            value_text = str(book.year) if book.year else "blank"
        elif col == 3:  # Series
            value_text = book.series_name or "blank"
        elif col == 4:  # Genre
            value_text = book.genre_name or "blank"
        elif col == 5:  # Time
            value_text = book.time_display or "blank"
        elif col == 6:  # Tracks
            value_text = str(book.tracks or 0)
        elif col == 7:  # Read date
            if book.read_date:
                value_text = book.read_date if isinstance(
                    book.read_date, str) else str(book.read_date)
            else:
                value_text = "blank"
        elif col == 8:  # Date added
            if book.date_added:
                value_text = book.date_added if isinstance(
                    book.date_added, str) else str(book.date_added)
            else:
                value_text = "blank"
        else:
            value_text = "blank"

        announcement = f"{header_text}: {value_text}"
        self.set_status(announcement, timeout_ms=2000)

    def announce_selection(self):
        """Announce selected books to status bar - show last selected item."""
        if not self.selected_book_ids:
            return

        count = len(self.selected_book_ids)

        # Find the last selected book (the one with current focus)
        current_row = self.table.currentRow()
        if 0 <= current_row < len(self.books):
            last_book = self.books[current_row]
            title = last_book.title or "Unknown"

            if count == 1:
                announcement = f"{title} - selected"
            else:
                announcement = f"{title} - {count} selected"
        else:
            announcement = f"{count} selected"

        shortcuts_text = "Alt+U Update, Alt+D Delete, Alt+L Cancel"
        announcement = f"{announcement}. {shortcuts_text}"

        # Keep until selection changes
        self.set_status(announcement, timeout_ms=0)

    def toggle_current_row_selection(self):
        """Toggle selection for current row using Ctrl+Space."""
        row = self.table.currentRow()
        if row < 0 or row >= len(self.books):
            return

        model = self.table.selectionModel()
        index = self.table.model().index(row, 0)

        if model.isRowSelected(row, self.table.rootIndex()):
            model.select(index, QItemSelectionModel.Deselect |
                         QItemSelectionModel.Rows)
        else:
            model.select(index, QItemSelectionModel.Select |
                         QItemSelectionModel.Rows)
            self.selection_anchor_row = row

    def select_range_to_current_row(self):
        """Select a range from anchor to current row using Shift+Space."""
        row = self.table.currentRow()
        if row < 0 or row >= len(self.books):
            return

        if self.selection_anchor_row is None:
            self.selection_anchor_row = row

        start_row = min(self.selection_anchor_row, row)
        end_row = max(self.selection_anchor_row, row)

        start_index = self.table.model().index(start_row, 0)
        end_index = self.table.model().index(end_row, self.table.columnCount() - 1)
        selection = QItemSelection(start_index, end_index)

        self.table.selectionModel().select(
            selection, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows
        )

    def update_selection_ui(self):
        """Update UI based on selection."""
        count = len(self.selected_book_ids)

        # Only show buttons if we have an actual selection
        # (not just the current row from navigation)
        has_selection = count > 0
        self.update_button.setVisible(has_selection)
        self.delete_button.setVisible(has_selection)
        self.cancel_button.setVisible(has_selection)
        self.status_hint_label.setVisible(has_selection)

        self.sort_label.setVisible(not has_selection)

        self.sync_selection_indicators()

        # mw#12: Update status bar and announce to screen reader when selection changes
        self.set_default_status(announce=has_selection)

    def sync_selection_indicators(self):
        """Sync text color indicators with current selection.
        mw#11: Checkbox column removed, only using text color highlighting.
        """
        self._updating_selection_ui = True
        try:
            text_color_selected = self.palette().color(QPalette.Highlight)
            text_color_default = self.palette().color(QPalette.Text)

            for row in range(self.table.rowCount()):
                is_selected = False
                if 0 <= row < len(self.books):
                    is_selected = self.books[row].book_id in self.selected_book_ids

                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item is None:
                        continue
                    item.setForeground(
                        QColor(text_color_selected if is_selected else text_color_default))
        finally:
            self._updating_selection_ui = False

    def on_update_clicked(self):
        """Handle Update button click."""
        if self.selected_book_ids:
            # Track the first selected row to return focus after update
            first_selected_row = None
            for row in range(self.table.rowCount()):
                if row < len(self.books) and self.books[row].book_id in self.selected_book_ids:
                    first_selected_row = row
                    break

            dialog = UpdateWindow(
                db=self.db,
                scaler=self.scaler,
                selected_book_ids=self.selected_book_ids,
                parent=self
            )
            result = dialog.exec()

            # If changes were applied, refresh the book list and clear selection
            if dialog.changes_applied:
                updated_count = len(dialog.selected_book_ids)
                self.selected_book_ids.clear()
                self.update_selection_ui()
                self.refresh_books()

                # Check if filters resulted in 0 books - clear filters to prevent freeze
                if self.table.rowCount() == 0 and self.has_active_filters():
                    self.clear_all_filters()
                    self.refresh_books()
                    self.set_status(
                        f"Updated {updated_count} books - filters cleared (no matching records)", announce=True)
                else:
                    self.statusBar().showMessage(
                        f"Updated {updated_count} books")

            # Return focus to the first selected row (or same position)
            if first_selected_row is not None:
                target_row = min(first_selected_row, self.table.rowCount() - 1)
                if target_row >= 0:
                    self.table.setCurrentCell(target_row, 1)  # Title column
                    self.table.setFocus()

    def on_delete_clicked(self):
        """Handle Delete button click."""
        if self.selected_book_ids:
            count = len(self.selected_book_ids)

            # mw#25: Track the first selected row to return focus after delete
            first_selected_row = None
            for row in range(self.table.rowCount()):
                if row < len(self.books) and self.books[row].book_id in self.selected_book_ids:
                    first_selected_row = row
                    break

            reply = QMessageBox.question(
                self, "Confirm Delete",
                f"Are you sure you want to delete {count} selected book(s)?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.book_queries.delete_many(list(self.selected_book_ids))

                try:
                    self.author_queries.cleanup_unused()
                    self.series_queries.cleanup_unused()
                    self.genre_queries.cleanup_unused()
                    self.db.vacuum()
                except Exception:
                    pass

                deleted_count = len(self.selected_book_ids)
                self.selected_book_ids.clear()
                self.update_selection_ui()
                self.refresh_books()

                # Check if filters resulted in 0 books - clear filters to prevent freeze
                if self.table.rowCount() == 0 and self.has_active_filters():
                    self.clear_all_filters()
                    self.refresh_books()
                    self.set_status(
                        f"{deleted_count} book(s) deleted - filters cleared (no matching records)", announce=True)
                    return  # Skip focus logic since table was refreshed

                # mw#25: Focus the row before the deleted selection
                if first_selected_row is not None:
                    target_row = max(0, first_selected_row - 1)
                    if target_row < self.table.rowCount():
                        self.table.setCurrentCell(
                            target_row, 1)  # Title column
                        self.table.setFocus()

                # Show deletion message
                self.set_status(
                    f"{deleted_count} book(s) deleted", timeout_ms=2000)

    def on_cancel_clicked(self):
        """Handle Cancel button click. mw#25: Focus returns to table. mw#26: Leaves focus on current cell."""
        self.table.clearSelection()
        self.selected_book_ids.clear()
        self.selection_anchor_row = None  # Reset anchor for keyboard selection
        self.update_selection_ui()
        # mw#13: Revert status bar to default after clearing selection
        self.set_default_status(announce=False)
        # mw#25: Return focus to table (use timer to ensure button hiding completes)
        QTimer.singleShot(0, self.table.setFocus)

    def on_escape_pressed(self):
        """Handle ESC key at window level - clears selection first, then search."""
        # First priority: clear selection mode/selected books
        if self.selected_book_ids or self.selection_anchor_row is not None:
            self.on_cancel_clicked()
            return
        # Second priority: clear search - use book_id to restore position (mw#29)
        if self.current_filter.has_search:
            # Use tracked book ID (set by on_current_cell_changed)
            restore_book_id = self._last_table_book_id
            restore_column = self._last_table_column if self._last_table_column >= 0 else 1

            # Disconnect signal to prevent refresh during clear
            self.search_box.textChanged.disconnect(self.on_search_changed)
            self.search_box.clear()
            self.search_box.textChanged.connect(self.on_search_changed)

            # Clear filter and refresh
            self.current_filter.search_text = ""
            self.search_timer.stop()
            self.refresh_books()

            # Restore focus to the actual book that was selected
            def restore_focus():
                if restore_book_id is not None:
                    self.focus_book_by_id(restore_book_id, restore_column)
                else:
                    if self.table.rowCount() > 0:
                        self.table.setCurrentCell(0, 1)
                    self.table.setFocus(Qt.TabFocusReason)

            QTimer.singleShot(150, restore_focus)
            self.set_status("Search cleared", timeout_ms=2000)

    def clear_status_message(self):
        """Clear temporary status message and restore default status."""
        self.set_default_status(announce=False)

    def show_search_results_message(self):
        """Show search results in status bar without re-announcing (already announced in on_search_enter)."""
        self.set_default_status(announce=False)

    def on_status_bar_focus(self):
        """Status bar is already accessible - this is just for manual focus if needed."""
        # The status bar is already accessible to screen readers via Qt
        # This method is kept for F7 shortcut but doesn't need complex focus management
        pass

    def on_zoom_in(self):
        """Handle Ctrl++ zoom in."""
        new_scale = self.scaler.current_scale + self.scaler.SCALE_STEP
        if new_scale <= self.scaler.MAX_SCALE:
            self.scaler.increase_scale()

    def on_zoom_out(self):
        """Handle Ctrl+- zoom out."""
        new_scale = self.scaler.current_scale - self.scaler.SCALE_STEP
        if new_scale >= self.scaler.MIN_SCALE:
            self.scaler.decrease_scale()

    def on_zoom_reset(self):
        """Handle Ctrl+0 zoom reset - mw#21: Reset to default (150% ~14pt)."""
        self.scaler.reset_scale()

    def on_new_book(self):
        """Open book details for new book."""
        # bd#8: Pass current sort order to show in header
        sort_order = self.order_combo.currentText()
        details = BookDetailsWindow(
            self.db, self.scaler, sort_order=sort_order, parent=self)
        details.exec()

        # bd#7: If a new book was saved, get its book_id to focus on it
        new_book_id = details.book.book_id if details.book else None

        self.refresh_books()

        # bd#7: Focus the table on the newly created book (if saved)
        if new_book_id:
            self.focus_book_by_id(new_book_id)

    def on_import(self):
        """Open import window."""
        dialog = ImportWindow(self.db, self.scaler,
                              self.theme_manager, parent=self)
        dialog.exec()
        imported_count = getattr(dialog, "total_imported", 0)
        self.refresh_books()

        db_total_row = self.db.fetch_one("SELECT COUNT(*) FROM books")
        db_total_books = int(db_total_row[0]) if db_total_row else 0

        if imported_count > 0 and len(self.books) == 0:
            self.current_filter = SearchFilter(order_by="Title")
            self.clear_all_filters()
            self.order_combo.setCurrentText("Title")
            self.refresh_collections()
            self.collection_combo.setCurrentIndex(0)
            self.read_combo.setCurrentIndex(0)
            self.refresh_books()

            if len(self.books) > 0:
                self.set_status(
                    f"Imported {imported_count} books. View reset to show all books.",
                    timeout_ms=4000,
                )
            elif db_total_books > 0:
                self.set_status(
                    f"Imported {imported_count}. Database now has {db_total_books} books, but the table view is not rendering rows.",
                    timeout_ms=6000,
                )

    def open_book_details(self, book: Book):
        """Open book details window."""
        # bd#8: Pass current sort order to show in header
        sort_order = self.order_combo.currentText()

        # bd#4: Find current book's index in the list for Prev/Next navigation
        current_index = 0
        for i, b in enumerate(self.books):
            if b.book_id == book.book_id:
                current_index = i
                break

        details = BookDetailsWindow(
            self.db, self.scaler, book=book, sort_order=sort_order,
            books_list=self.books, current_index=current_index, parent=self)
        details.exec()

        # bd#7: After dialog closes, get the last viewed book_id
        # The dialog object still exists after exec() returns (just hidden),
        # so we can read its current book state before it's garbage collected
        last_book_id = details.book.book_id if details.book else None

        self.refresh_books()

        # bd#7: Focus the table on the book that was viewed in details window
        if last_book_id:
            self.focus_book_by_id(last_book_id)

    def on_preferences(self):
        """Open preferences dialog."""
        dialog = PreferencesWindow(
            self.scaler, self.theme_manager, parent=self)
        dialog.exec()

    def on_show_splash(self):
        """Show library statistics."""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QAbstractItemView, QTextEdit
        from PySide6.QtCore import Qt, QTimer

        # Get statistics from database
        stats_queries = StatisticsQueries(self.db)
        stats = stats_queries.get_statistics()

        # Create dialog
        dlg = QDialog(self)
        dlg.setWindowTitle("Library Statistics")
        dlg.setAccessibleName("")
        dlg.setAccessibleDescription("")
        dlg.resize(500, 500)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        if stats.total_books == 0:
            # First time use - welcome message
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            splash_text = """Welcome to AbCS - Audio Book Collector Scanner!

No audiobooks found in the database yet.

You can:
• Import audiobooks from your computer (scan folders)
• Manually add a new book

Use Ctrl+I to import or Alt+M for menu options."""
            text_edit.setPlainText(splash_text)
            font = text_edit.font()
            font.setPointSize(self.scaler.get_scaled_size(12))
            text_edit.setFont(font)
            layout.addWidget(text_edit)
        else:
            # Show statistics in a single-column table
            table = QTableWidget()
            table.setAccessibleName("")
            table.setAccessibleDescription("")
            table.setColumnCount(1)
            table.setHorizontalHeaderLabels([""])
            table.setSelectionBehavior(QAbstractItemView.SelectRows)
            table.setSelectionMode(QAbstractItemView.SingleSelection)
            table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            table.setAlternatingRowColors(True)
            table.verticalHeader().setVisible(False)
            table.horizontalHeader().setVisible(False)
            table.setShowGrid(False)
            table.setStyleSheet(
                "QTableWidget:focus { border: none; outline: none; }")

            # Data rows
            data = [
                ("Total Books", str(stats.total_books)),
                ("Total Authors", str(stats.total_authors)),
                ("Total Series", str(stats.total_series)),
                ("Total Genres", str(stats.total_genres)),
                ("Collections", str(stats.total_collections)),
                ("Books Read", str(stats.books_read)),
                ("Books Unread", str(stats.books_unread)),
                ("Total Listening Time", stats.total_time_display),
            ]

            table.setRowCount(len(data))

            for row, (label, value) in enumerate(data):
                combined_text = f"{label:<25} {value}"
                item = QTableWidgetItem(combined_text)
                item.setData(Qt.AccessibleTextRole, f"{label}: {value}")
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                table.setItem(row, 0, item)

            # Resize column to stretch
            header = table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.Stretch)

            # Set font
            font = table.font()
            font.setPointSize(self.scaler.get_scaled_size(11))
            font.setFamily("Courier New")
            table.setFont(font)

            layout.addWidget(table)

        ok_btn = QPushButton("Close")
        ok_btn.clicked.connect(dlg.close)
        layout.addWidget(ok_btn)

        dlg.exec()

    def on_import(self):
        """Open import window."""
        dialog = ImportWindow(self.db, self.scaler,
                              self.theme_manager, parent=self)
        dialog.exec()
        imported_count = getattr(dialog, "total_imported", 0)
        self.refresh_books()

        db_total_row = self.db.fetch_one("SELECT COUNT(*) FROM books")
        db_total_books = int(db_total_row[0]) if db_total_row else 0

        if imported_count > 0 and len(self.books) == 0:
            self.current_filter = SearchFilter(order_by="Title")
            self.clear_all_filters()
            self.order_combo.setCurrentText("Title")
            self.refresh_collections()
            self.collection_combo.setCurrentIndex(0)
            self.read_combo.setCurrentIndex(0)
            self.refresh_books()

            if len(self.books) > 0:
                self.set_status(
                    f"Imported {imported_count} books. View reset to show all books.",
                    timeout_ms=4000,
                )
            elif db_total_books > 0:
                self.set_status(
                    f"Imported {imported_count}. Database now has {db_total_books} books, but the table view is not rendering rows.",
                    timeout_ms=6000,
                )

    def on_show_authors(self):
        """Open Author window."""
        QMessageBox.information(self, "Coming Soon",
                                "show Author will be available soon!")

    def on_show_collection(self):
        """Open collection window."""
        previous_collection_id = self.current_filter.collection_id

        dialog = CollectionWindow(
            self.db,
            self.scaler,
            self.theme_manager,
            parent=self,
        )
        dialog.exec()

        self.refresh_collections()

        restored_index = self.collection_combo.findData(previous_collection_id)
        if previous_collection_id is not None and restored_index >= 0:
            self.collection_combo.setCurrentIndex(restored_index)
            self.current_filter.collection_id = previous_collection_id
        else:
            self.collection_combo.setCurrentIndex(0)
            self.current_filter.collection_id = None

        self.refresh_books()

    def on_show_Genre(self):
        """Open Genre( window."""
        QMessageBox.information(self, "Coming Soon",
                                "show Genre( will be available soon!")

    def on_show_Series(self):
        """Open Series window."""
        QMessageBox.information(self, "Coming Soon",
                                "show Series will be available soon!")

    def on_backup_restore(self):
        """Open backup_restore window."""
        QMessageBox.information(self, "Coming Soon",
                                "Backup & restore will be available soon!")

    def on_about(self):
        """Show about dialog."""
        dlg = QDialog(self)
        dlg.setWindowTitle("About AbCS")
        dlg.setAccessibleName("About AbCS")
        dlg.setAccessibleDescription(
            "Information about AbCS - Audio Book Collector Scanner")
        dlg.resize(600, 400)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setAccessibleName("About text")
        text_edit.setAccessibleDescription(
            "Information about AbCS application")

        screen_reader_text = "Screen reader is detected."
        if not QAccessible.isActive():
            screen_reader_text = (
                "No screen reader detected. "
                "For best accessibility, start JAWS or NVDA before launching AbCS."
            )

        about_text = f"""AbCS - Audio Book Collector Scanner

Version 1.0 (Python Edition)

A cross-platform audiobook collection manager with full accessibility support.

FEATURES:
• Audio Book Management with full metadata
• ID3 Tag Import from folders
• Advanced Search and Filtering
• Complete Keyboard Navigation
• Screen Reader Support
• Scalable UI (50%-200%+)
• High Contrast Themes

ACCESSIBILITY:
This application is designed to be fully accessible to users with low vision or who use screen readers. All features have keyboard shortcuts.

Screen Reader Status:
{screen_reader_text}

Press F1 or use Help → Keyboard Shortcuts to see all available shortcuts."""

        text_edit.setPlainText(about_text)
        font = text_edit.font()
        scaled_size = self.scaler.get_scaled_size(12)
        font.setPointSize(scaled_size)
        text_edit.setFont(font)
        layout.addWidget(text_edit)

        close_btn = QPushButton("Close")
        close_btn.setAccessibleName("Close")
        close_btn.clicked.connect(dlg.accept)
        btn_font = close_btn.font()
        btn_font.setPointSize(self.scaler.get_scaled_size(11))
        close_btn.setFont(btn_font)
        layout.addWidget(close_btn)

        dlg.exec()

    def on_show_shortcuts(self):
        """Show keyboard shortcuts help in a table for JAWS accessibility."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Keyboard Shortcuts - Main Window")
        dlg.setAccessibleName("")
        dlg.setAccessibleDescription("")
        dlg.resize(500, 600)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        shortcuts = [
            ("Alt+/", "Read status bar"),
            ("Alt+C", "Collection filter"),
            ("Alt+R", "Read filter"),
            ("Alt+O", "Order by"),
            ("Alt+S", "Search"),
            ("Alt+B", "Book list"),
            ("Alt+1", "Jump to Title column"),
            ("Alt+2", "Jump to Author column"),
            ("Alt+1..Alt+0", "Jump to other columns (see table order)"),
            ("Alt+U", "Update selected"),
            ("Alt+D", "Delete selected"),
            ("Alt+L", "Cancel selection"),
            ("Ctrl+I", "Import"),
            ("Ctrl+N", "New book"),
            ("Escape", "Clear selection/search"),
            ("Ctrl+Plus", "Zoom in"),
            ("Ctrl+Minus", "Zoom out"),
            ("Ctrl+0", "Reset zoom"),
            ("F1", "Show keyboard shortcuts"),
        ]

        # Create table with 1 column
        table = QTableWidget()
        table.setAccessibleName("")
        table.setAccessibleDescription("")
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels([""])
        table.setRowCount(len(shortcuts))
        table.setVerticalHeaderLabels([""] * len(shortcuts))
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setTabKeyNavigation(False)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setStyleSheet(
            "QTableWidget:focus { border: none; outline: none; }")

        # Populate table
        for row, (key, description) in enumerate(shortcuts):
            combined_text = f"{description} - {key}"
            item = QTableWidgetItem(combined_text)
            item.setData(Qt.AccessibleTextRole, f"{description}: {key}")
            table.setItem(row, 0, item)

        # Resize column to stretch
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)

        # Set font size
        font = table.font()
        font.setPointSize(self.scaler.get_scaled_size(11))
        table.setFont(font)

        layout.addWidget(table)

        close_btn = QPushButton("Close")
        close_btn.setAccessibleName("Close")
        close_btn.clicked.connect(dlg.accept)
        btn_font = close_btn.font()
        btn_font.setPointSize(self.scaler.get_scaled_size(11))
        close_btn.setFont(btn_font)
        layout.addWidget(close_btn)

        dlg.setTabOrder(table, close_btn)

        dlg.exec()

    def resizeEvent(self, event):
        """Handle window resize - recalculate proportional column widths."""
        super().resizeEvent(event)
        self.update_stretch_columns()

    def showEvent(self, event):
        """Handle window show - set initial column widths."""
        super().showEvent(event)
        # Delay column sizing to ensure table is fully laid out
        QTimer.singleShot(0, self.update_stretch_columns)

    def update_stretch_columns(self):
        """mw#22: Update stretch column widths proportionally."""
        if not hasattr(self, '_stretch_columns') or not hasattr(self, 'table'):
            return

        header = self.table.horizontalHeader()

        # Calculate total width used by fixed columns
        fixed_width = 0
        for col in range(self.table.columnCount()):
            if col not in self._stretch_columns:
                fixed_width += header.sectionSize(col)

        # Calculate available width for stretch columns
        available = self.table.viewport().width() - fixed_width
        if available < 100:
            return  # Not enough space

        # Calculate total weight
        total_weight = sum(self._stretch_columns.values())

        # Distribute available space proportionally
        for col, weight in self._stretch_columns.items():
            width = int(available * weight / total_weight)
            self.table.setColumnWidth(col, max(width, 60))
