"""
Main Window - Audio Book Window
Primary interface for browsing and managing audiobook collection.
"""

import time

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableView,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QLineEdit,
    QPushButton,
    QLabel,
    QStatusBar,
    QMessageBox,
    QHeaderView,
    QCheckBox,
    QAbstractItemView,
    QDialog,
    QTextEdit,
)
from src.ui.license_dialogue import LicenseDialog
from PySide6.QtCore import (
    Qt,
    QTimer,
    QItemSelectionModel,
    QEvent,
    QSettings,
    QAbstractTableModel,
    QModelIndex,
)
from PySide6.QtGui import (
    QKeyEvent,
    QAction,
    QActionGroup,
    QShortcut,
    QKeySequence,
    QAccessible,
)
from PySide6.QtWidgets import QApplication

from src.database import (
    DatabaseManager,
    BookQueries,
    AuthorQueries,
    SeriesQueries,
    GenreQueries,
    CollectionQueries,
    SearchFilter,
    Book,
    StatisticsQueries,
)
from src.ui.statistics_dialog import StatisticsDialog
from src.accessibility.scaling import UIScaler
from src.accessibility.accessible_events import announce_status_message
from src.accessibility.style_helpers import (
    exec_styled_message_box,
    build_accessible_button_style,
)
from src.accessibility.theme_manager import ThemeManager
from src.accessibility.shortcuts import get_shortcut_manager, ShortcutContext
from src.accessibility.key_filters import is_unmapped_alt_letter
from src.ui.book_details import BookDetailsWindow
from src.ui.update_window import UpdateWindow
from src.ui.preferences_window import PreferencesWindow
from src.ui.import_window import ImportWindow
from src.ui.collection_window import CollectionWindow
from src.ui.name_list_window import NameListWindow
from src.ui.backup_restore_window import BackupRestoreWindow

from src.ui.web_metadata import WebMetadataWindow

# Import version from main module


def get_app_version():
    """Get app version from build_config."""
    try:
        from src.build_config import APP_VERSION

        return f"v{APP_VERSION}"
    except ImportError:
        return "v?.?.?"


class BookTableView(QTableView):
    """QTableView with QTableWidget-like convenience helpers."""

    def rowCount(self) -> int:
        model = self.model()
        return model.rowCount() if model else 0

    def columnCount(self) -> int:
        model = self.model()
        return model.columnCount() if model else 0

    def currentRow(self) -> int:
        return self.currentIndex().row()

    def currentColumn(self) -> int:
        return self.currentIndex().column()

    def setCurrentCell(self, row: int, column: int):
        model = self.model()
        if model is None:
            return
        index = model.index(row, column)
        self.setCurrentIndex(index)


class BookTableModel(QAbstractTableModel):
    """Model-backed view for large book lists."""

    HEADERS = [
        "Author",
        "Title",
        "Year",
        "Series",
        "Genre",
        "Time",
        "Read",
    ]

    def __init__(self, books: list[Book] | None = None, parent=None):
        super().__init__(parent)
        self._books = books or []

    def set_books(self, books: list[Book]):
        self.beginResetModel()
        self._books = books
        self.endResetModel()

    def rowCount(self, parent: QModelIndex | None = None) -> int:
        return len(self._books)

    def columnCount(self, parent: QModelIndex | None = None) -> int:
        return len(self.HEADERS)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()
        if row < 0 or row >= len(self._books):
            return None

        book = self._books[row]

        if role in (Qt.DisplayRole, Qt.AccessibleTextRole):
            if col == 0:
                return book.author_name or ""
            if col == 1:
                return book.title or ""
            if col == 2:
                return str(book.year) if book.year else ""
            if col == 3:
                return book.series_name or ""
            if col == 4:
                return book.genre_name or ""
            if col == 5:
                return book.time_display or ""
            if col == 6:
                if book.read_date:
                    return (
                        book.read_date
                        if isinstance(book.read_date, str)
                        else str(book.read_date)
                    )
                return ""

        if role == Qt.TextAlignmentRole:
            if col == 2:  # Year column
                return Qt.AlignCenter | Qt.AlignVCenter
            if col == 5:  # Time (length) column
                return Qt.AlignRight | Qt.AlignVCenter
            if col == 6:
                return Qt.AlignCenter | Qt.AlignVCenter

        return None

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole
    ):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            if 0 <= section < len(self.HEADERS):
                return self.HEADERS[section]
            return None
        # Empty vertical headers to avoid row number announcements
        return ""


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from src.accessibility.icon_helper import get_app_icon
        import os

        # Debug: print resolved icon path and existence
        from src.accessibility import icon_helper

        print(
            "[DEBUG] ICON_PATH:",
            os.path.abspath(icon_helper.ICON_PATH),
            "Exists:",
            os.path.exists(icon_helper.ICON_PATH),
        )
        # Set the window icon using centralized icon helper
        self.setWindowIcon(get_app_icon())

    def _selection_shortcuts_text(self) -> str:
        """Return selection shortcut text for status bar (accessibility, no Alt+key noise)."""
        # Only show Escape to cancel selection for accessibility
        return "Escape to cancel selection"

    def show_read_date_dialog(self, row: int):
        """Show a dialog to set the read date for the selected book (accessible version)."""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QDateEdit
        from PySide6.QtCore import QDate
        from src.accessibility.icon_helper import get_app_icon

        class ReadDateDialog(QDialog):
            """Scoped Enter handling for the read-date dialog without global shortcuts."""

            def __init__(self, parent=None):
                super().__init__(parent)
                self.date_field = None
                self.setWindowIcon(get_app_icon())

            def keyPressEvent(self, event):
                if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                    if self.date_field is not None:
                        self.date_field.setFocus()
                    QTimer.singleShot(0, self.accept)
                    event.accept()
                    return
                super().keyPressEvent(event)

        book = self.books[row]
        dlg = ReadDateDialog(self)
        dlg.setWindowTitle(f"Set Read Date for '{book.title}'")
        dlg.setModal(True)
        layout = QVBoxLayout(dlg)

        # Use simple QDateEdit with calendar popup
        date_field = QDateEdit()
        date_field.setCalendarPopup(True)
        date_field.setDisplayFormat("yyyy-MM-dd")
        date_field.setAccessibleName("Date read")
        date_field.setMinimumDate(QDate(1, 1, 1))
        date_field.setSpecialValueText("")

        # Set initial date
        if book.read_date:
            if isinstance(book.read_date, str):
                d = QDate.fromString(book.read_date, "yyyy-MM-dd")
            else:
                d = QDate(book.read_date.year, book.read_date.month, book.read_date.day)
            if d.isValid():
                date_field.setDate(d)
            else:
                date_field.setDate(QDate.currentDate())
        else:
            # Default to today's date for new entries
            date_field.setDate(QDate.currentDate())

        # Set font size
        font = date_field.font()
        font.setPointSize(self.scaler.get_scaled_size(14))
        date_field.setFont(font)

        layout.addWidget(date_field)
        date_field.setFocus()
        dlg.date_field = date_field

        # Add Alt+Down shortcut to open calendar (though it may not work)
        from PySide6.QtGui import QShortcut, QKeySequence

        alt_down_shortcut = QShortcut(QKeySequence("Alt+Down"), dlg)
        alt_down_shortcut.activated.connect(date_field.calendarPopup)

        dlg.setLayout(layout)
        # Auto-size dialog width so title is always fully visible
        from PySide6.QtGui import QFontMetrics

        title_text = dlg.windowTitle()
        font_metrics = QFontMetrics(dlg.font())
        title_width = (
            font_metrics.horizontalAdvance(title_text) + 80
        )  # padding for window controls
        min_width = 400
        content_width = dlg.sizeHint().width() + 120
        final_width = max(title_width, content_width, min_width)
        dlg.resize(final_width, dlg.sizeHint().height())
        # Center the dialog in the main window
        parent_geom = self.geometry()
        dlg_geom = dlg.frameGeometry()
        center_point = parent_geom.center() - dlg_geom.center()
        dlg.move(center_point)

        if dlg.exec() == QDialog.Accepted:
            # Check if date is being changed (not just cleared)
            if date_field.date() == date_field.minimumDate():
                # Clear the date - no confirmation needed for clearing
                book.read_date = ""
                self.book_queries.update(book)
                self.refresh_books()
                self.set_status(f"Read date cleared for {book.title}", announce=True)
            else:
                new_date = date_field.date().toString("yyyy-MM-dd")
                # Check if date is actually changing
                if book.read_date == new_date:
                    # No change - don't ask for confirmation
                    self.set_status(
                        f"Read date unchanged for {book.title}", announce=True
                    )
                else:
                    # Date is changing - ask for confirmation
                    from PySide6.QtWidgets import QMessageBox

                    reply = QMessageBox.question(
                        self,
                        "Confirm Read Date",
                        f"Mark '{book.title}' as read on {new_date}?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No,
                    )
                    if reply == QMessageBox.Yes:
                        book.read_date = new_date
                        self.book_queries.update(book)
                        self.refresh_books()
                        self.set_status(
                            f"Read date set for {book.title}", announce=True
                        )
                    else:
                        # User cancelled - don't update
                        self.set_status(
                            f"Read date update cancelled for {book.title}",
                            announce=True,
                        )
            # Move focus back to the same cell (QTableView)
            index = self.book_model.index(row, 6)
            self.table.setCurrentIndex(index)
            self.table.setFocus()

    """
    Main application window - Audio Book Window.
    Displays list of books with filtering and search.
    """

    FIND_ALLOWED_ALT_LETTERS = {"I", "T", "X"}

    DUPLICATE_MATCH_OPTIONS = [
        ("Title + Author + Collection", "title_author"),
        ("Title + Author + Year", "title_author_year"),
        ("Title + Author + Year + Collection", "title_author_year_collection"),
    ]

    _SETTINGS_ORG = "AbCS"
    _SETTINGS_APP = "AudioBookCollector"
    _SETTINGS_KEY_COLLECTION_FILTER_ID = "main/collection_filter_id"

    def _set_sort_label(self, order_by=None, direction=None):
        """Set the sort label with custom message for Author, Genre, Series."""
        key = order_by or self.current_filter.order_by
        if key == "Author":
            msg = "Author, Year, Title"
        elif key == "Series":
            msg = "Series, Year, Title"
        elif key == "Genre":
            msg = "Genre, Title"
        else:
            msg = key
        if direction:
            self.sort_label.setText(f"Sorted: {msg} ({direction})")
        else:
            self.sort_label.setText(f"Sorted: {msg}")

    def __init__(
        self, db: DatabaseManager, scaler: UIScaler, theme_manager: ThemeManager
    ):
        """
        Initialize main window.
        """
        super().__init__()

        # Store UI managers
        self.scaler = scaler
        self.theme_manager = theme_manager

        # Database and queries
        self.db = db
        self.book_queries = BookQueries(db)
        self.author_queries = AuthorQueries(db)
        self.series_queries = SeriesQueries(db)
        self.genre_queries = GenreQueries(db)
        self.collection_queries = CollectionQueries(db)

        # UI components
        self.table = QTableWidget()
        self.books = []
        self.current_filter = SearchFilter()
        self._collection_filter_items = [("All Collections", None)]
        self._read_filter_options = ["All", "Read", "Unread"]
        self._primary_sort_options = ["Title", "Author", "Genre", "Series", "Read Date"]

        # Selected books (for bulk operations)
        self.selected_book_ids = set()

        # Duplicate check mode state
        self.duplicate_mode_active = False
        self.duplicate_mode_match_mode = ""
        self.duplicate_mode_book_ids = set()
        self._duplicate_saved_filter = None

        # Anchor row for shift selection
        self.selection_anchor_row = None

        # Guard for selection indicator updates
        self._updating_selection_ui = False

        # Track last focused book in table (for ESC from search to restore focus)
        self._last_table_book_id = None
        self._last_table_column = 1

        # Status message clear timer
        self.status_clear_timer = QTimer()
        self.status_clear_timer.setSingleShot(True)
        self.status_clear_timer.timeout.connect(self.clear_status_message)

        # De-duplicate rapid repeated announcements of the same status text.
        self._last_announced_message = ""
        self._last_announce_monotonic = 0.0

        # Header sort state for non-primary columns
        self._last_header_sort_column = -1
        self._last_header_sort_order = Qt.AscendingOrder
        self._active_sort_key = "Title"

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
        self._load_saved_collection_filter()
        self.refresh_books()

        # Window settings
        version_str = get_app_version()
        self.setWindowTitle(f"AbCS - Audio Book Collector Scanner {version_str}")
        # Larger default size for better column visibility
        self.resize(1400, 800)
        # mw#22: Minimum size to prevent columns from being cut off
        self.setMinimumSize(900, 400)

        # Show SetupDialog if database is empty
        stats_queries = StatisticsQueries(self.db)
        stats = stats_queries.get_statistics()
        if stats.total_books == 0:
            self.on_show_splash()

        # Set focus to first title in book list on startup.
        if self.table.model() and self.table.model().rowCount() > 0:
            self.table.setCurrentCell(0, 1)  # Column 1 is Title
            self.table.setFocus()
        else:
            self.table.setFocus()

        # Maximize window on open (accessibility requirement)
        self.showMaximized()

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

        # Status bar (no Alt+key shortcut hints for accessibility)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Menu bar
        self.create_menu_bar()

    def create_header(self) -> QHBoxLayout:
        """Create header with filters and search."""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Remove layout margins
        layout.setSpacing(0)

        return layout

    def on_scale_changed(self, scale_percentage: int):
        """Update header control heights when zoom level changes."""
        # Scale the height proportionally: base is 20px at 100% scale
        base_height = 20
        scaled_height = int(base_height * (scale_percentage / 100.0))

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

        # Keep table fixed-content columns scaled without expensive content-size scans.
        if hasattr(self, "table"):
            self._apply_fixed_content_column_widths()
            self.update_stretch_columns()

    def apply_control_styles(self):
        """Re-apply dynamic styles for controls and table after theme/scale changes."""
        self.on_scale_changed(self.scaler.current_scale)
        table_header = self.table.horizontalHeader()
        table_vertical_header = self.table.verticalHeader()

        widgets_to_repolish = [
            self.update_button,
            self.delete_button,
            self.table,
            self.table.viewport(),
            table_header,
            table_header.viewport(),
            table_vertical_header,
            table_vertical_header.viewport(),
        ]

        # Optional controls can vary by build/window mode.
        if hasattr(self, "get_web_info_button"):
            widgets_to_repolish.append(self.get_web_info_button)

        for widget in widgets_to_repolish:
            style = widget.style()
            style.unpolish(widget)
            style.polish(widget)
            if hasattr(widget, "viewport") and callable(getattr(widget, "viewport")):
                try:
                    viewport = widget.viewport()
                    if viewport is not None:
                        viewport.update()
                        continue
                except Exception:
                    pass
            widget.repaint()

        table_header.updateGeometry()
        table_header.viewport().update()
        table_header.repaint()

    def on_theme_changed(self, _theme_name: str):
        """Refresh main window controls/table when application theme changes."""
        self.apply_control_styles()

    def create_table(self):
        """Create books table."""
        self.table = BookTableView()
        self.table.setAccessibleName("Audio books")
        self.table.setAccessibleDescription("List of audiobooks in collection")

        # Columns: Author, Title, Year, Series, Genre, Time, Read
        self.table.setColumnHidden(0, True)  # Author
        self.table.setColumnHidden(3, True)  # Series
        self.table.setColumnHidden(5, True)  # Time
        self.book_model = BookTableModel([])
        self.table.setModel(self.book_model)
        # Selection column removed; only text highlighting used

        # Table settings - SelectItems for cell-level focus, row selection handled manually
        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setVisible(False)
        # mw#22: Enable horizontal scrollbar so columns don't get cut off
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setWordWrap(False)

        # Disable hover highlighting for low-vision comfort
        self.table.setMouseTracking(False)
        self.table.viewport().setMouseTracking(False)
        self.table.setAttribute(Qt.WA_Hover, False)
        self.table.viewport().setAttribute(Qt.WA_Hover, False)
        # Apply centralized F1 popup style to table only
        self.table.setStyleSheet("""
            QTableView::item:hover {
                background-color: palette(base);
                color: palette(text);
            }
            QTableView::item:selected {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }
            QTableView::item:selected:focus {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }
            """)

        # Resize columns - mw#22: Author, Title, Series, Genre stretch proportionally
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setMinimumSectionSize(60)  # Prevent columns from disappearing

        # mw#22: Store stretch column proportions (relative weights)
        # Title reduced by 20%, half of that added to Series and Genre
        # New: Author 2.5, Title 2.8, Series 1.85, Genre 1.85
        self._stretch_columns = {
            0: 2.5,  # Author
            1: 2.8,  # Title (reduced)
            3: 1.85,  # Series (increased)
            4: 1.85,  # Genre (increased)
        }

        # Fixed content columns - use fixed/scaled widths for large dataset performance
        self._apply_fixed_content_column_widths()

        # Stretch columns use Interactive mode - we control sizing in resizeEvent
        header.setSectionResizeMode(0, QHeaderView.Interactive)  # Author
        header.setSectionResizeMode(1, QHeaderView.Interactive)  # Title
        header.setSectionResizeMode(3, QHeaderView.Interactive)  # Series
        header.setSectionResizeMode(4, QHeaderView.Interactive)  # Genre
        header.setSortIndicatorShown(True)
        header.setSortIndicator(1, Qt.AscendingOrder)
        header.sectionClicked.connect(self.on_table_header_clicked)

        # Double-click to open details
        self.table.doubleClicked.connect(self.on_table_double_clicked)

        # Selection change handler
        self.table.selectionModel().selectionChanged.connect(
            self.on_table_selection_changed
        )

        # Current cell change handler (screen reader announcements)
        self.table.selectionModel().currentChanged.connect(self.on_current_cell_changed)

        # Install event filter for custom mouse handling
        self.table.viewport().installEventFilter(self)

        # Custom mouse and key handlers
        self.table.mousePressEvent = self.table_mouse_press
        self.table.mouseDoubleClickEvent = self.table_mouse_double_click  # mw#18
        self.table.keyPressEvent = self.accessible_table_key_press

    def accessible_table_key_press(self, event):
        """Custom key handler: Tab/Shift+Tab move focus out of table for accessibility."""
        if event.key() == Qt.Key_Tab and not event.modifiers() & Qt.ControlModifier:
            # Move focus to next widget outside the table
            self.focusNextChild()
            event.accept()
            return
        elif event.key() == Qt.Key_Backtab:
            # Move focus to previous widget outside the table
            self.focusPreviousChild()
            event.accept()
            return
        # Otherwise, default table navigation
        self.table_key_press(event)

    def _apply_fixed_content_column_widths(self):
        """Set fixed/scaled widths for non-stretch content columns.

        Using fixed widths avoids expensive ResizeToContents recalculation on each
        refresh, which can be very slow on 30k+ row datasets.
        """
        if not hasattr(self, "table"):
            return

        header = self.table.horizontalHeader()
        scale = max(getattr(self.scaler, "current_scale", 100), 50) / 100.0

        # Base widths at 100% scale (pixels)
        base_widths = {
            2: 72,  # Year
            5: 82,  # Time
            6: 116,  # Read (was 7)
        }

        for col, base_width in base_widths.items():
            header.setSectionResizeMode(col, QHeaderView.Fixed)
            self.table.setColumnWidth(col, max(int(base_width * scale), 48))

    def create_footer(self) -> QHBoxLayout:
        """Create footer with action buttons and info."""
        layout = QHBoxLayout()

        # Update button (hidden initially)

        self.update_button = QPushButton("Update")
        self.update_button.setAccessibleName("Update selected books")
        self.update_button.setAccessibleDescription("Update selected books - Alt+U")
        self.update_button.setFocusPolicy(Qt.StrongFocus)
        self.update_button.setAutoDefault(True)
        self.update_button.setDefault(True)
        self.update_button.clicked.connect(self.on_update_clicked)
        self.update_button.setVisible(False)
        layout.addWidget(self.update_button)

        # Delete button (hidden initially)

        self.delete_button = QPushButton("Delete")
        self.delete_button.setAccessibleName("Delete selected books")
        self.delete_button.setAccessibleDescription("Delete selected books - Alt+D")
        self.delete_button.setFocusPolicy(Qt.StrongFocus)
        self.delete_button.setAutoDefault(True)
        self.delete_button.setDefault(True)
        self.delete_button.clicked.connect(self.on_delete_clicked)
        self.delete_button.setVisible(False)
        layout.addWidget(self.delete_button)

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

        # Book List Import
        book_list_import_action = QAction("Import Book &List", self)
        book_list_import_action.setShortcut("Ctrl+Shift+I")
        book_list_import_action.setShortcutContext(Qt.ApplicationShortcut)
        book_list_import_action.triggered.connect(self.on_book_list_import)
        file_menu.addAction(book_list_import_action)

        file_menu.addSeparator()

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Edit menu
        self.edit_menu = menubar.addMenu("&Edit")

        # Delete action (same as delete button)
        self.delete_action = QAction("&Delete\tDel", self)
        self.delete_action.setShortcut(QKeySequence("Del"))
        self.delete_action.triggered.connect(self.on_delete_clicked)
        self.delete_action.setEnabled(False)  # Disabled until item selected
        self.edit_menu.addAction(self.delete_action)

        # Update action (same as update button)
        self.update_action = QAction("&Update\tCtrl+U", self)
        self.update_action.setShortcut("Ctrl+U")
        self.update_action.triggered.connect(self.on_update_clicked)
        self.update_action.setEnabled(False)  # Disabled until item selected
        self.edit_menu.addAction(self.update_action)

        # Fetch Web Info action (for Alt+E then W shortcut)
        self.get_web_info_action = QAction("Fetch &Web Info", self)
        self.get_web_info_action.triggered.connect(self.on_get_web_info_clicked)
        self.edit_menu.addAction(self.get_web_info_action)

        # View menu
        self.view_menu = menubar.addMenu("&View")

        # mw#17: Context-sensitive open at top of View menu
        book_details_action = QAction("&Open Focused Item\tEnter", self)
        book_details_action.triggered.connect(self.on_open_book_details)
        self.view_menu.addAction(book_details_action)

        find_action = QAction("&Find...\tCtrl+F", self)
        find_action.setShortcuts([QKeySequence("Ctrl+F")])
        find_action.triggered.connect(self.on_find)
        self.view_menu.addAction(find_action)

        self.view_menu.addSeparator()

        # Phase 2: collection filter moved from header combo to View menu.
        self.view_collections_menu = self.view_menu.addMenu("&Collections")
        self.collection_filter_group = QActionGroup(self)
        self.collection_filter_group.setExclusive(True)

        # Phase 3: read filter moved from header combo to View menu.
        self.view_read_menu = self.view_menu.addMenu("&Read")
        self.read_filter_group = QActionGroup(self)
        self.read_filter_group.setExclusive(True)
        self._rebuild_read_filter_menu()

        # Phase 2: Reading History (accessed via menu Alt+V then H)
        reading_history_action = QAction("Reading &History", self)
        reading_history_action.triggered.connect(self.on_reading_history)
        self.view_menu.addAction(reading_history_action)

        # Separator after reading history, before zoom controls
        self.view_menu.addSeparator()

        # mw#16: Zoom actions with shortcut keys displayed
        zoom_in_action = QAction("Zoom &In\tCtrl++", self)
        zoom_in_action.triggered.connect(self.on_zoom_in)
        self.view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom &Out\tCtrl+-", self)
        zoom_out_action.triggered.connect(self.on_zoom_out)
        self.view_menu.addAction(zoom_out_action)

        zoom_reset_action = QAction("&Reset Zoom\tCtrl+0", self)
        zoom_reset_action.triggered.connect(self.on_zoom_reset)
        self.view_menu.addAction(zoom_reset_action)

        self.view_menu.addSeparator()

        # Phase 4: sorting moved from header combo to dedicated Sort menu.
        self.sort_menu = menubar.addMenu("&Sort")
        self.sort_action_group = QActionGroup(self)
        self.sort_action_group.setExclusive(True)
        self._rebuild_sort_menu()

        # manage menu
        view_menu = menubar.addMenu("&Manage")

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

        view_menu.addSeparator()

        duplicate_action = QAction("&Duplicate Check...", self)
        duplicate_action.triggered.connect(self.on_duplicate_check)
        view_menu.addAction(duplicate_action)

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

        license_action = QAction("&License...", self)
        license_action.triggered.connect(self.on_show_license)
        help_menu.addAction(license_action)

        shortcuts_action = QAction("&Keyboard Shortcuts", self)
        shortcuts_action.triggered.connect(self.on_show_shortcuts)
        help_menu.addAction(shortcuts_action)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        shortcut_mgr = get_shortcut_manager()

        # Alt+Key shortcuts (centralized)
        callback_map = {
            "update_button": self.on_update_clicked,  # Alt+U
            "delete_button": self.on_delete_clicked,  # Alt+D
        }
        shortcut_mgr.register_alt_shortcuts(
            self, ShortcutContext.MAIN_WINDOW, callback_map
        )

        # Zoom shortcuts - register as proper QShortcut objects
        # Store references to prevent garbage collection
        # Register both keyboard and numpad versions
        # Zoom In: Ctrl++ (keyboard) and Ctrl+Plus (numpad)
        self.zoom_in_shortcut = QShortcut(QKeySequence("Ctrl++"), self)
        self.zoom_in_shortcut.activated.connect(self.on_zoom_in)

        self.zoom_in_numpad_shortcut = QShortcut(QKeySequence("Ctrl+Num++"), self)
        self.zoom_in_numpad_shortcut.activated.connect(self.on_zoom_in)

        # Zoom Out: Ctrl+- (keyboard) and Ctrl+Minus (numpad)
        self.zoom_out_shortcut = QShortcut(QKeySequence("Ctrl+-"), self)
        self.zoom_out_shortcut.activated.connect(self.on_zoom_out)

        self.zoom_out_numpad_shortcut = QShortcut(QKeySequence("Ctrl+Num+-"), self)
        self.zoom_out_numpad_shortcut.activated.connect(self.on_zoom_out)

        # Zoom Reset: Ctrl+0 — ApplicationShortcut so it works from any dialog too
        self.zoom_reset_shortcut = QShortcut(QKeySequence("Ctrl+0"), self)
        self.zoom_reset_shortcut.setContext(Qt.ApplicationShortcut)
        self.zoom_reset_shortcut.activated.connect(self.on_zoom_reset)

        # Help shortcut: F1 opens keyboard shortcuts help
        self.help_shortcut = QShortcut(QKeySequence("F1"), self)
        self.help_shortcut.activated.connect(self.on_show_shortcuts)

        # mw#15: Ctrl+N for new book
        self.new_book_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        self.new_book_shortcut.activated.connect(self.on_new_book)

        # mw#19: Enter handled by menu action and table_key_press
        # (No separate QShortcut to avoid ambiguous shortcut error)

        # mw#24: Alt+/ reads status bar aloud
        self.status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.status_shortcut.activated.connect(self.on_read_status_bar)

        # ESC shortcut at window level - clears selection or search
        self.escape_shortcut = QShortcut(QKeySequence("Escape"), self)
        self.escape_shortcut.activated.connect(self.on_escape_pressed)

        # mw#23: Alt+1 through Alt+8 to jump to table columns
        # Columns: 0=Author, 1=Title, 2=Year, 3=Series, 4=Genre, 5=Time, 6=Read
        self.column_shortcuts = []
        for i in range(7):
            shortcut = QShortcut(QKeySequence(f"Alt+{i + 1}"), self)  # Alt+1..7
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
            shortcuts = self._selection_shortcuts_text()

            # Include title of currently focused book (same as announce_selection)
            current_row = self.table.currentRow()
            if 0 <= current_row < len(self.books):
                title = self.books[current_row].title or "Unknown"
                if count == 1:
                    return f"{title} - selected. {shortcuts}"
                else:
                    return f"{title} - {count} selected. {shortcuts}"
            return f"{count} selected. {shortcuts}"

        # Priority 2: Duplicate mode active
        if self.duplicate_mode_active:
            return (
                f"Duplicate mode: {len(self.books)} books shown. "
                "Use normal selection. Alt+D Delete, Escape Cancel Dup Mode"
            )

        # Priority 3: Show search results if search is active
        if self.current_filter.search_text:
            search_text = self.current_filter.search_text
            if search_text.startswith("?"):
                search_text = search_text[1:]
            count = len(self.books)
            order_by = self._active_sort_key or "Title"
            if count == 0:
                return f"No {order_by.lower()}s found matching '{search_text}'. Esc to exit search"
            elif count == 1:
                return f"Found 1 {order_by.lower()}: {search_text}. Esc to exit search"
            else:
                return f"Found {count} {order_by.lower()}s matching '{search_text}'. Esc to exit search"

        # Priority 4: Show filtered book count with all active filters
        parts = [f"Showing {len(self.books)} books"]

        # mw#12: Show current sort order (especially Series/Genre)
        # Remove 'BY xxx' and only show 'Showing XX books'

        # Read filter
        if self.current_filter.read_filter == "Read":
            parts.append("Read")
        elif self.current_filter.read_filter == "Unread":
            parts.append("Unread")

        # Collection filter
        if self.current_filter.collection_id is not None:
            parts.append(self._current_collection_label())

        return " • ".join(parts)

    # Removed status shortcut hint text for accessibility

    def _normalize_duplicate_mode(self, mode: str) -> str:
        """Normalize duplicate mode values (supports legacy aliases)."""
        normalized = (mode or "").strip()
        if normalized == "with_collection":
            return "title_author_year_collection"
        if normalized == "ignore_collection":
            return "title_author_year"
        if normalized == "title_author_year_ignore_collection":
            return "title_author_year"
        if normalized == "title_author_ignore_collection":
            return "title_author_year"
        valid_modes = {option[1] for option in self.DUPLICATE_MATCH_OPTIONS}
        if normalized in valid_modes:
            return normalized
        return "title_author_year_collection"

    def _duplicate_mode_label(self, mode: str) -> str:
        """Get display label for duplicate mode key."""
        normalized = self._normalize_duplicate_mode(mode)
        for label, data in self.DUPLICATE_MATCH_OPTIONS:
            if data == normalized:
                return label
        return "Title + Author + Year + Collection"

    def _apply_current_filter_to_controls(self):
        """Apply current filter state into header controls without triggering refresh."""
        valid_collection_ids = {
            item[1] for item in self._collection_filter_items if item[1] is not None
        }
        if self.current_filter.collection_id not in valid_collection_ids:
            self.current_filter.collection_id = None

        if self.current_filter.read_filter not in self._read_filter_options:
            self.current_filter.read_filter = "All"

        if self.current_filter.order_by not in self._primary_sort_options:
            self.current_filter.order_by = "Title"

        self._active_sort_key = self.current_filter.order_by
        self._set_sort_label()

        self._sync_collection_menu_selection()
        self._sync_read_menu_selection()
        self._sync_sort_menu_selection(self.current_filter.order_by)

    def _current_collection_label(self) -> str:
        """Return the active collection filter label for status messages."""
        for label, collection_id in self._collection_filter_items:
            if collection_id == self.current_filter.collection_id:
                return label
        return "All Collections"

    def _duplicate_key_for_book(self, book: Book, mode: str):
        """Build duplicate comparison key for a book based on mode."""
        normalized_mode = self._normalize_duplicate_mode(mode)
        title_key = (book.title or "").strip().casefold()
        author_key = book.author_id or 0
        year_key = book.year or 0
        collection_key = book.collection_id or 0

        if normalized_mode == "title_author":
            return (title_key, author_key)
        if normalized_mode == "title_author_year":
            return (title_key, author_key, year_key)
        return (title_key, author_key, year_key, collection_key)

    def _collect_duplicate_book_ids(self, books: list[Book], mode: str) -> set[int]:
        """Return IDs of books that belong to duplicate groups for selected mode."""
        grouped: dict[tuple, list[int]] = {}
        for book in books:
            key = self._duplicate_key_for_book(book, mode)
            grouped.setdefault(key, []).append(book.book_id)

        duplicate_ids: set[int] = set()
        for ids in grouped.values():
            if len(ids) > 1:
                duplicate_ids.update(ids)
        return duplicate_ids

    def _apply_row_selection_by_book_ids(self, book_ids: set[int]):
        """Programmatically select full rows that match book IDs."""
        self._updating_selection_ui = True
        try:
            model = self.table.selectionModel()
            if model is None:
                return
            model.clearSelection()

            col_count = self.table.columnCount()
            for row, book in enumerate(self.books):
                if book.book_id not in book_ids:
                    continue
                for col in range(col_count):
                    idx = self.table.model().index(row, col)
                    model.select(idx, QItemSelectionModel.Select)
        finally:
            self._updating_selection_ui = False

    def _refresh_duplicate_mode_after_data_change(self):
        """Recompute duplicate-mode rows after database changes (e.g., delete)."""
        if not self.duplicate_mode_active:
            return

        all_books = self.book_queries.get_all(
            SearchFilter(order_by=self.current_filter.order_by)
        )
        self.duplicate_mode_book_ids = self._collect_duplicate_book_ids(
            all_books,
            self.duplicate_mode_match_mode,
        )

        if not self.duplicate_mode_book_ids:
            self.exit_duplicate_mode(
                message="Duplicate mode complete. No remaining duplicates found.",
                announce=True,
            )
            return

        self.refresh_books()
        self.selected_book_ids = {
            book.book_id
            for book in self.books
            if book.book_id in self.duplicate_mode_book_ids
        }
        self._apply_row_selection_by_book_ids(self.selected_book_ids)
        self.update_selection_ui()
        # Do not set a duplicate mode status here to avoid overlapping/jumbled messages

    def exit_duplicate_mode(
        self, message: str = "Duplicate mode canceled", announce: bool = False
    ):
        """Exit duplicate mode and restore previous filter/view."""
        if not self.duplicate_mode_active:
            return

        saved_filter = self._duplicate_saved_filter
        self.duplicate_mode_active = False
        self.duplicate_mode_match_mode = ""
        self.duplicate_mode_book_ids.clear()
        self._duplicate_saved_filter = None

        self.selected_book_ids.clear()
        self.selection_anchor_row = None

        if saved_filter is not None:
            self.current_filter = SearchFilter(
                collection_id=saved_filter.collection_id,
                read_filter=saved_filter.read_filter,
                order_by=saved_filter.order_by,
                search_text=saved_filter.search_text,
                is_keyword_search=saved_filter.is_keyword_search,
            )

        self._apply_current_filter_to_controls()
        self.refresh_books()
        self.update_selection_ui()
        self.set_status(message, timeout_ms=3000, announce=announce)

    def on_duplicate_check(self):
        """Start duplicate mode by prompting for duplicate match type."""
        settings = QSettings("AbCS", "AbCS")
        preferred_mode = self._normalize_duplicate_mode(
            settings.value(
                "import/rules/duplicate/match_mode",
                "title_author_year_collection",
                type=str,
            )
        )

        dialog = QDialog(self)
        dialog.setWindowTitle("Duplicate Check")
        """Start duplicate mode by prompting for duplicate match type."""
        dialog.setAccessibleDescription(
            "Select duplicate match mode and start duplicate checking"
        )

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        prompt = QLabel("Select duplicate match type:")
        layout.addWidget(prompt)

        mode_combo = QComboBox()
        mode_combo.setAccessibleName("Duplicate match type")
        mode_combo.setAccessibleDescription(
            "Same duplicate matching options as Preferences"
        )
        combo_height = max(self.scaler.get_scaled_size(24), 18)
        mode_combo.setStyleSheet(f"""
            QComboBox {{
                min-height: {combo_height}px;
                max-height: {combo_height}px;
                padding: 2px 6px;
                border: 1px solid palette(dark);
                border-radius: 3px;
            }}
            QComboBox:focus {{
                border: 2px solid palette(highlight);
                outline: none;
            }}
            QComboBox QAbstractItemView {{
                outline: none;
                border: 1px solid palette(dark);
            }}
            """)
        for label, data in self.DUPLICATE_MATCH_OPTIONS:
            mode_combo.addItem(label, data)
        preferred_index = mode_combo.findData(preferred_mode)
        mode_combo.setCurrentIndex(0 if preferred_index < 0 else preferred_index)
        layout.addWidget(mode_combo)

        buttons_layout = QHBoxLayout()
        # Restore original button text
        start_button = QPushButton("Start")
        start_button.setAccessibleName("Start duplicate check")
        start_button.setAccessibleDescription("Start duplicate check")
        cancel_button = QPushButton("Cancel")
        cancel_button.setAccessibleName("Cancel duplicate check")
        cancel_button.setAccessibleDescription("Cancel duplicate check")
        button_style = build_accessible_button_style(self.scaler.get_scaled_size(20))
        start_button.setStyleSheet(button_style)
        cancel_button.setStyleSheet(button_style)
        start_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        # Centralized Alt+letter shortcuts for Duplicate Check dialog
        from src.accessibility.shortcuts import get_shortcut_manager, ShortcutContext

        shortcut_mgr = get_shortcut_manager()

        def focus_mode_combo():
            mode_combo.setFocus()
            mode_combo.showPopup()

        callback_map = {
            "start_button": start_button.click,
            "cancel_button": cancel_button.click,
            "mode_combo": focus_mode_combo,
        }
        shortcut_mgr.register_alt_shortcuts(
            dialog, ShortcutContext.DUPLICATE_DIALOG, callback_map
        )
        buttons_layout.addStretch()
        buttons_layout.addWidget(start_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)

        if dialog.exec() != QDialog.Accepted:
            self.set_status("Duplicate check canceled", timeout_ms=2000, announce=False)
            return

        selected_mode = self._normalize_duplicate_mode(mode_combo.currentData())

        all_books = self.book_queries.get_all(
            SearchFilter(order_by=self.current_filter.order_by)
        )
        duplicate_ids = self._collect_duplicate_book_ids(all_books, selected_mode)
        if not duplicate_ids:
            msg = f"No duplicates found for mode: {self._duplicate_mode_label(selected_mode)}"
            self.set_status(msg, timeout_ms=3000)
            from src.accessibility.icon_helper import get_app_icon

            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Information,
                title="Duplicate Check Result",
                text=msg,
                window_icon=get_app_icon(),
            )
            return

        if not self.duplicate_mode_active:
            self._duplicate_saved_filter = SearchFilter(
                collection_id=self.current_filter.collection_id,
                read_filter=self.current_filter.read_filter,
                order_by=self.current_filter.order_by,
                search_text=self.current_filter.search_text,
                is_keyword_search=self.current_filter.is_keyword_search,
            )

        self.duplicate_mode_active = True
        self.duplicate_mode_match_mode = selected_mode
        self.duplicate_mode_book_ids = set(duplicate_ids)

        self.current_filter.collection_id = None
        self.current_filter.read_filter = "All"
        self.current_filter.search_text = ""
        self.current_filter.is_keyword_search = False
        self._apply_current_filter_to_controls()

        self.refresh_books()

        self.selected_book_ids = set()
        self._apply_row_selection_by_book_ids(self.selected_book_ids)
        self.selection_anchor_row = None
        self.update_selection_ui()

        dup_count = len(self.duplicate_mode_book_ids)
        status_msg = f"{dup_count} duplicate books found ({self._duplicate_mode_label(selected_mode)})"
        self.set_status(status_msg, timeout_ms=0)
        popup_msg = f"Duplicate check complete: {dup_count} duplicate books found using mode: {self._duplicate_mode_label(selected_mode)}."
        from src.accessibility.icon_helper import get_app_icon

        exec_styled_message_box(
            self,
            self.scaler.get_scaled_size(20),
            icon=QMessageBox.Information,
            title="Duplicate Check Result",
            text=popup_msg,
            window_icon=get_app_icon(),
        )
        # Set focus to the first title in the table for accessibility
        if self.table.model() and self.table.model().rowCount() > 0:
            self.table.setCurrentCell(0, 1)  # Column 1 is Title
            self.table.setFocus()

    def set_status(self, message: str, timeout_ms: int = 0, announce: bool = False):
        """
        Set status bar message with optional screen reader announcement.

        Args:
            message: Message to display
            timeout_ms: If > 0, message will clear to default after this delay.
                       If 0, message stays until manually changed.
            announce: If True, briefly move focus to status bar so the screen reader reads it
        """
        if announce and message == self._last_announced_message:
            if (time.monotonic() - self._last_announce_monotonic) < 0.6:
                announce = False

        announce_status_message(self.status_bar, message, move_focus=announce)

        if announce:
            self._last_announced_message = message
            self._last_announce_monotonic = time.monotonic()

        if timeout_ms > 0:
            self.status_clear_timer.stop()
            self.status_clear_timer.start(timeout_ms)

    def set_default_status(self, announce: bool = False):
        """
        Set status bar to the default message for current state.

        Args:
            announce: If True, announce to screen readers (default False for passive updates)
        """
        self.set_status(self.get_default_status(), timeout_ms=0, announce=announce)

    def on_read_status_bar(self):
        """mw#24: Alt+/ reads status bar. Do nothing if no screen reader active."""
        if QAccessible.isActive():
            # Announce status bar to screen reader
            self.set_status(self.get_default_status(), timeout_ms=0, announce=True)
        # else: do nothing (no popup)

    def on_open_book_details(self):
        """mw#17,19: Open book details for current book (Enter)."""
        if self.selected_book_ids:
            # If items are selected, don't open details
            return

        # Ensure table has focus and get current row
        row = self.table.currentRow()
        if row < 0 and self.table.rowCount() > 0:
            row = 0  # Default to first row if none selected

        if 0 <= row < len(self.books):
            column = self.table.currentColumn()
            if column < 0:
                column = 1
            # Author, Series, Genre columns open their manager dialogs
            if column in (0, 3, 4):
                self._handle_book_table_double_click(row, column)
            # Read column opens date picker
            elif column == 7:
                self.show_read_date_dialog(row)
            # Title column opens Book Details
            elif column == 1:
                self._handle_book_table_double_click(row, column)
            # All other columns: do nothing, show status
            else:
                self.set_status(
                    "Enter only opens details for Author, Title, Series, Genre, or Read columns.",
                    timeout_ms=2500,
                    announce=True,
                )

    # ========== End Status Bar Helpers ==========

    def refresh_collections(self):
        """Refresh collection filter data and rebuild View > Collections menu."""
        selected_collection_id = self.current_filter.collection_id
        self._collection_filter_items = [("All Collections", None)]

        collections = self.collection_queries.get_all(active_only=True)
        for coll in collections:
            self._collection_filter_items.append((coll.name, coll.collection_id))

        valid_ids = {
            collection_id
            for _label, collection_id in self._collection_filter_items
            if collection_id is not None
        }
        if selected_collection_id not in valid_ids:
            self.current_filter.collection_id = None

        self._rebuild_collection_filter_menu()

    def clear_all_filters(self):
        """Clear all filters and search, reset to show all books."""
        self.current_filter.search_text = ""
        self.current_filter.is_keyword_search = False
        self.current_filter.collection_id = None
        self.current_filter.read_filter = "All"
        self._apply_current_filter_to_controls()

        self._sync_collection_menu_selection()
        self._sync_read_menu_selection()

    def _rebuild_read_filter_menu(self):
        """Populate View > Read submenu from read filter options."""
        if not hasattr(self, "view_read_menu"):
            return

        self.view_read_menu.clear()
        self.read_filter_group = QActionGroup(self)
        self.read_filter_group.setExclusive(True)

        for label in self._read_filter_options:
            action = QAction(label, self)
            action.setCheckable(True)
            action.setData(label)
            action.triggered.connect(
                lambda _checked=False, value=label: self.on_read_menu_selected(value)
            )
            self.read_filter_group.addAction(action)
            self.view_read_menu.addAction(action)

        self._sync_read_menu_selection()

    def _sync_read_menu_selection(self):
        """Keep View > Read checked item synced with current filter."""
        if not hasattr(self, "read_filter_group"):
            return

        current_value = self.current_filter.read_filter or "All"
        for action in self.read_filter_group.actions():
            action.blockSignals(True)
            action.setChecked(action.data() == current_value)
            action.blockSignals(False)

    def on_read_menu_selected(self, read_filter: str):
        """Handle View > Read menu selection."""
        target = read_filter if read_filter in {"All", "Read", "Unread"} else "All"
        self.on_read_filter_changed(target)

    def _rebuild_sort_menu(self):
        """Populate Sort menu with supported sort fields."""
        if not hasattr(self, "sort_menu"):
            return

        self.sort_menu.clear()
        self.sort_action_group = QActionGroup(self)
        self.sort_action_group.setExclusive(True)

        self._sort_menu_options = [
            ("Author", "&Author", 0, True),
            ("Title", "&Title", 1, True),
            ("Year", "&Year", 2, False),
            ("Series", "&Series", 3, True),
            ("Genre", "&Genre", 4, True),
            ("Length", "&Length", 5, False),
            ("Read Date", "Read &Date", 6, False),
        ]

        self._sort_actions_by_key = {}

        for key, menu_text, column, is_primary in self._sort_menu_options:
            action = QAction(menu_text, self)
            action.setCheckable(True)
            action.triggered.connect(
                lambda _checked=False, key=key, col=column, primary=is_primary: self.on_sort_menu_selected(
                    key, col, primary
                )
            )
            self.sort_action_group.addAction(action)
            self.sort_menu.addAction(action)
            self._sort_actions_by_key[key] = action

        self._sync_sort_menu_selection(self.current_filter.order_by)

    def _sort_key_for_column(self, column: int) -> str:
        """Return Sort menu key for a table column index."""
        mapping = {
            0: "Author",
            1: "Title",
            2: "Year",
            3: "Series",
            4: "Genre",
            5: "Length",
            6: "Read Date",
        }
        return mapping.get(column, "Title")

    def _sync_sort_menu_selection(self, key: str):
        """Keep Sort menu checked item synced with current active sort."""
        if not hasattr(self, "_sort_actions_by_key"):
            return

        target_key = key if key in self._sort_actions_by_key else "Title"

        for action_key, action in self._sort_actions_by_key.items():
            action.blockSignals(True)
            action.setChecked(action_key == target_key)
            action.blockSignals(False)

    def on_sort_menu_selected(self, key: str, column: int, is_primary: bool):
        """Handle Sort menu selection."""
        # Always use backend SQL for Read Date (and primary sorts)
        if is_primary or key == "Read Date":
            self.on_order_changed(key)
            return

        # For custom sorts (Year, Length, Tracks), toggle order like header clicks
        if self._last_header_sort_column == column:
            next_order = (
                Qt.DescendingOrder
                if self._last_header_sort_order == Qt.AscendingOrder
                else Qt.AscendingOrder
            )
        else:
            next_order = Qt.AscendingOrder

        self._last_header_sort_column = column
        self._last_header_sort_order = next_order
        self._active_sort_key = key
        self._sort_books_in_memory(column, next_order)
        self.table.horizontalHeader().setSortIndicator(column, next_order)

        # Update sort label with direction
        direction = "Descending" if next_order == Qt.DescendingOrder else "Ascending"
        self._set_sort_label(order_by=key, direction=direction)
        self._sync_sort_menu_selection(key)

    def _rebuild_collection_filter_menu(self):
        """Populate View > Collections submenu from current collection list."""
        if not hasattr(self, "view_collections_menu"):
            return

        self.view_collections_menu.clear()
        self.collection_filter_group = QActionGroup(self)
        self.collection_filter_group.setExclusive(True)

        for label, collection_id in self._collection_filter_items:

            action = QAction(label, self)
            action.setCheckable(True)
            action.setData(collection_id)
            action.triggered.connect(
                lambda _checked=False, cid=collection_id: self.on_collection_menu_selected(
                    cid
                )
            )
            self.collection_filter_group.addAction(action)
            self.view_collections_menu.addAction(action)

        self._sync_collection_menu_selection()

    def _save_collection_filter_setting(self):
        """Persist the current collection filter selection for next app launch."""
        settings = QSettings(self._SETTINGS_ORG, self._SETTINGS_APP)
        collection_id = self.current_filter.collection_id
        settings.setValue(
            self._SETTINGS_KEY_COLLECTION_FILTER_ID,
            int(collection_id) if collection_id is not None else -1,
        )

    def _load_saved_collection_filter(self):
        """Restore the last saved collection filter if it is still available."""
        settings = QSettings(self._SETTINGS_ORG, self._SETTINGS_APP)
        saved_collection_id = settings.value(
            self._SETTINGS_KEY_COLLECTION_FILTER_ID, -1, type=int
        )

        if saved_collection_id is None or int(saved_collection_id) < 0:
            self.current_filter.collection_id = None
            self._sync_collection_menu_selection()
            return

        valid_ids = {
            collection_id
            for _label, collection_id in self._collection_filter_items
            if collection_id is not None
        }
        self.current_filter.collection_id = (
            int(saved_collection_id) if int(saved_collection_id) in valid_ids else None
        )
        self._sync_collection_menu_selection()

    def _sync_collection_menu_selection(self):
        """Keep View > Collections checked item synced with current filter."""
        if not hasattr(self, "collection_filter_group"):
            return

        for action in self.collection_filter_group.actions():
            action.blockSignals(True)
            action.setChecked(action.data() == self.current_filter.collection_id)
            action.blockSignals(False)

    def on_collection_menu_selected(self, collection_id):
        """Handle View > Collections menu selection."""
        valid_ids = {
            collection_id_value
            for _label, collection_id_value in self._collection_filter_items
        }
        self.current_filter.collection_id = (
            collection_id if collection_id in valid_ids else None
        )
        self._save_collection_filter_setting()
        self._sync_collection_menu_selection()
        self.refresh_books()

    def has_active_filters(self) -> bool:
        """Check if any filters or search are active."""
        return bool(
            self.current_filter.search_text
            or self.current_filter.collection_id is not None
            or self.current_filter.read_filter != "All"
        )

    def refresh_books(self):
        """Refresh books table based on current filter."""
        # BLOCK ALL EVENTS - This is critical!
        self.table.blockSignals(True)

        try:
            # Get books from database
            self.books = self.book_queries.get_all(self.current_filter)

            # Duplicate mode only shows duplicate candidates for selected matching rule
            if self.duplicate_mode_active:
                self.books = [
                    book
                    for book in self.books
                    if book.book_id in self.duplicate_mode_book_ids
                ]

            # DISABLE UPDATES WHILE RESETTING MODEL
            self.table.setUpdatesEnabled(False)
            self.table.setSortingEnabled(False)

            focus_ctx = self._capture_table_focus_context()
            self.book_model.set_books(self.books)
            self._restore_table_focus_context(focus_ctx)

            # RE-ENABLE UPDATES
            self.table.setUpdatesEnabled(True)

            self.set_default_status(announce=False)

        except Exception as e:
            self.table.setUpdatesEnabled(True)
            self.set_status(f"Error loading books: {e}", timeout_ms=3000)

        finally:
            # ALWAYS UNBLOCK SIGNALS - even on error
            self.table.blockSignals(False)
            # Keep Qt auto-sorting disabled; header clicks are handled explicitly
            self.table.setSortingEnabled(False)
            # Allow Qt to process pending UI events.
            QApplication.instance().processEvents()

    # Event handlers

    def on_collection_changed(self, collection_id=None):
        """Handle collection filter change."""
        valid_ids = {
            item_collection_id
            for _label, item_collection_id in self._collection_filter_items
            if item_collection_id is not None
        }
        coll_id = collection_id if collection_id in valid_ids else None
        self.current_filter.collection_id = coll_id
        self._save_collection_filter_setting()
        self._sync_collection_menu_selection()
        self.refresh_books()

    def on_read_filter_changed(self, text: str):
        """Handle read filter change."""
        self.current_filter.read_filter = (
            text if text in self._read_filter_options else "All"
        )
        self._sync_read_menu_selection()
        self.refresh_books()

    def on_order_changed(self, text: str):
        """Handle sort order change."""
        target = text if text in self._primary_sort_options else "Title"
        self.current_filter.order_by = target
        self._active_sort_key = target
        self._set_sort_label(order_by=target)
        self._set_primary_sort_indicator(target)
        self._sync_sort_menu_selection(target)
        self.refresh_books()

    def on_table_header_clicked(self, column: int):
        """Handle table header clicks with combo-aligned sorting for key columns."""
        # Custom sort for Author and Series columns
        if column == 0:  # Author
            self.on_order_changed("Author")
            return
        elif column == 3:  # Series
            self.on_order_changed("Series")
            return
        # Title and Genre use default logic

        if self._last_header_sort_column == column:
            next_order = (
                Qt.DescendingOrder
                if self._last_header_sort_order == Qt.AscendingOrder
                else Qt.AscendingOrder
            )
        else:
            next_order = Qt.AscendingOrder

        self._last_header_sort_column = column
        self._last_header_sort_order = next_order

        self._sort_books_in_memory(column, next_order)
        self.table.horizontalHeader().setSortIndicator(column, next_order)

        header_text = (
            self.book_model.headerData(column, Qt.Horizontal, Qt.DisplayRole) or "Field"
        )
        direction = "Descending" if next_order == Qt.DescendingOrder else "Ascending"
        self._active_sort_key = self._sort_key_for_column(column)
        self._set_sort_label(order_by=header_text, direction=direction)
        self._sync_sort_menu_selection(self._active_sort_key)

    def _sort_books_in_memory(self, column: int, order: Qt.SortOrder):
        """Sort books list for non-primary columns without SQL roundtrip."""
        if not self.books:
            return

        focus_ctx = self._capture_table_focus_context()

        def sort_key(book: Book):
            if column == 2:  # Year
                return (book.year is None, book.year or 0)
            if column == 5:  # Length
                return (book.time_hours or 0) * 60 + (book.time_minutes or 0)
            if column == 6:  # Read Date
                return book.read_date or ""
            return ""

        self.books.sort(key=sort_key, reverse=(order == Qt.DescendingOrder))
        self.book_model.set_books(self.books)
        self._restore_table_focus_context(focus_ctx)

    def _set_primary_sort_indicator(self, order_by: str):
        """Keep sort indicator aligned with Order By combo for primary columns."""
        order_to_column = {
            "Author": 0,
            "Title": 1,
            "Series": 3,
            "Genre": 4,
        }
        column = order_to_column.get(order_by)
        if column is None:
            return

        self._last_header_sort_column = column
        self._last_header_sort_order = Qt.AscendingOrder
        self.table.horizontalHeader().setSortIndicator(column, Qt.AscendingOrder)

    def on_find(self):
        """Open popup Find dialog (Ctrl+F)."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Find")
        dialog.setAccessibleName("Find")
        dialog.setAccessibleDescription(
            "Find books by field. Enter text and press Enter to find."
        )
        dialog.resize(500, 180)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        field_row = QHBoxLayout()
        field_label = QLabel("Find &in:")
        field_combo = QComboBox()
        field_combo.addItems(["Author", "Title", "Series", "Genre"])
        field_combo.setAccessibleName("Find field")
        combo_height = max(int(20 * (self.scaler.current_scale / 100.0)), 18)
        field_combo.setStyleSheet(
            f"QComboBox {{ min-height: {combo_height}px; max-height: {combo_height}px; }}"
        )
        field_label.setBuddy(field_combo)
        field_row.addWidget(field_label)
        field_row.addWidget(field_combo, 1)

        exact_check = QCheckBox("E&xact match")
        exact_check.setAccessibleName("Exact match")
        exact_check.setChecked(False)
        field_row.addSpacing(12)
        field_row.addWidget(exact_check)
        layout.addLayout(field_row)

        text_row = QHBoxLayout()
        # Set initial label to match the default field
        initial_field = field_combo.currentText()
        text_label = QLabel(
            f"Find &{initial_field.lower()}:" if initial_field else "Find &text:"
        )
        text_edit = QLineEdit()
        text_edit.setAccessibleName("Find text")
        text_label.setBuddy(text_edit)
        text_row.addWidget(text_label)
        text_row.addWidget(text_edit, 1)
        layout.addLayout(text_row)

        def update_text_label(index):
            field = field_combo.currentText()
            # Use ampersand for Alt+T shortcut only on 'Title', else just 'Find xxx:'
            if field == "Title":
                text_label.setText("Find &title:")
                text_edit.setAccessibleName("Find title")
            elif field == "Author":
                text_label.setText("Find author:")
                text_edit.setAccessibleName("Find author")
            elif field == "Series":
                text_label.setText("Find series:")
                text_edit.setAccessibleName("Find series")
            elif field == "Genre":
                text_label.setText("Find genre:")
                text_edit.setAccessibleName("Find genre")
            else:
                text_label.setText(f"Find {field.lower()}:")
                text_edit.setAccessibleName(f"Find {field.lower()}")

        field_combo.currentIndexChanged.connect(update_text_label)

        dialog_status = QStatusBar(dialog)
        dialog_status.setSizeGripEnabled(False)
        dialog_status.showMessage(
            "Enter text and press Enter to find. Alt+I field, Alt+T text, Alt+X exact, Alt+/ read status"
        )
        layout.addWidget(dialog_status)

        field_to_column = {
            "Author": 0,
            "Title": 1,
            "Series": 3,
            "Genre": 4,
        }

        # Use search_field if present, else order_by
        current_field = getattr(
            self.current_filter, "search_field", self.current_filter.order_by
        )
        if current_field in field_to_column:
            field_combo.setCurrentText(current_field)
        else:
            field_combo.setCurrentText("Title")

        if self.current_filter.search_text:
            text_edit.setText(self.current_filter.search_text)
        # Only override with filter if user changed during session
        # settings = QSettings('AbCS', 'AudioBookCollector')
        # Always start unchecked; do not override with previous session
        # Persist Exact Match setting on change

        def update_exact_match_setting():
            settings = QSettings("AbCS", "AudioBookCollector")
            settings.setValue("find/exact_match", exact_check.isChecked())

        exact_check.stateChanged.connect(update_exact_match_setting)

        self._find_filter_widgets = {dialog, field_combo, text_edit, exact_check}
        for widget in self._find_filter_widgets:
            widget.installEventFilter(self)

        find_status_shortcut = QShortcut(QKeySequence("Alt+/"), dialog)

        def read_find_status():
            status_text = dialog_status.currentMessage() or "Find dialog ready"
            announce_status_message(dialog_status, status_text, move_focus=True)

        find_status_shortcut.activated.connect(read_find_status)

        def run_find():
            query = text_edit.text().strip()
            if not query:
                QApplication.beep()
                dialog_status.showMessage(
                    "Enter text to find. Alt+I field, Alt+T text, Alt+X exact, Alt+/ read status"
                )
                return

            selected_field = field_combo.currentText()
            selected_column = field_to_column.get(selected_field, 1)

            # Always keep order_by as user selected, but search_field is what to search
            self.current_filter.search_field = selected_field
            self.current_filter.search_text = query
            self.current_filter.is_keyword_search = not exact_check.isChecked()
            self.refresh_books()

            if not self.books:
                message = f"No match found for {selected_field.lower()}: {query}"
                QApplication.beep()
                dialog_status.showMessage(message)
                self.set_status(message, timeout_ms=3000, announce=True)
                # Popup for screen reader users
                from src.accessibility.icon_helper import get_app_icon

                exec_styled_message_box(
                    self,
                    self.scaler.get_scaled_size(20),
                    icon=QMessageBox.Information,
                    title="No Match Found",
                    text=message,
                    window_icon=get_app_icon(),
                )
                # Clear filter so new search works
                self.current_filter.search_text = ""
                self.refresh_books()

                # Return keyboard focus to the main table after the no-match popup.
                dialog.reject()

                def restore_table_focus_after_no_match():
                    if self.table.rowCount() > 0:
                        row = self.table.currentRow()
                        if row < 0:
                            row = 0
                        target_col = selected_column
                        if target_col < 0 or target_col >= self.table.columnCount():
                            target_col = 1
                        self.table.setCurrentCell(row, target_col)
                    self.table.setFocus(Qt.TabFocusReason)

                QTimer.singleShot(0, restore_table_focus_after_no_match)
                return

            found_book = self.books[0]
            dialog.accept()
            self.focus_book_by_id(found_book.book_id, selected_column)

        text_edit.returnPressed.connect(run_find)
        field_combo.activated.connect(lambda _index: text_edit.setFocus())
        QTimer.singleShot(0, lambda: text_edit.setFocus(Qt.TabFocusReason))

        result = dialog.exec()

        # If dialog closed and no match was found, clear filter
        if not self.books or (
            result != QDialog.Accepted and self.current_filter.search_text
        ):
            self.current_filter.search_text = ""
            self.refresh_books()

        for widget in self._find_filter_widgets:
            widget.removeEventFilter(self)
        self._find_filter_widgets = set()

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

    def _capture_table_focus_context(
        self, row: int | None = None, column: int | None = None
    ) -> dict:
        """Capture current table row/column and book ID so focus can be restored."""
        if row is None:
            row = self.table.currentRow()
        if column is None:
            column = self.table.currentColumn()

        if column is None or column < 0:
            column = 1

        book_id = None
        if row is not None and 0 <= row < len(self.books):
            book_id = self.books[row].book_id

        return {
            "row": row,
            "column": column,
            "book_id": book_id,
        }

    def _restore_table_focus_context(self, focus_ctx: dict | None):
        """Restore focus to the same book/cell when possible after refresh."""
        if not focus_ctx or self.table.rowCount() <= 0:
            return

        column = focus_ctx.get("column", 1)
        if column < 0 or column >= self.table.columnCount():
            column = 1

        book_id = focus_ctx.get("book_id")
        if book_id is not None and self.focus_book_by_id(book_id, column):
            return

        row = focus_ctx.get("row", 0)
        if row is None or row < 0:
            row = 0
        row = min(row, self.table.rowCount() - 1)

        index = self.table.model().index(row, column)
        self.table.scrollTo(index, QAbstractItemView.PositionAtCenter)
        self.table.setCurrentCell(row, column)
        self.table.setCurrentIndex(index)
        self.table.setFocus(Qt.TabFocusReason)

    def on_book_double_click(self, row: int, column: int):
        """Handle double-click on book."""
        if 0 <= row < len(self.books):
            self._handle_book_table_double_click(row, column)

    def on_table_double_clicked(self, index: QModelIndex):
        """Handle double-click signal from the table view."""
        if not index.isValid():
            return
        self.on_book_double_click(index.row(), index.column())

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
        """Filter events for find-dialog Alt-key handling and table mouse behavior."""
        if (
            event.type() == QEvent.KeyPress
            and hasattr(self, "_find_filter_widgets")
            and source in self._find_filter_widgets
        ):
            if is_unmapped_alt_letter(event, self.FIND_ALLOWED_ALT_LETTERS):
                event.accept()
                return True

        if (
            hasattr(self, "table")
            and source is self.table.viewport()
            and event.type() == QEvent.MouseButtonPress
        ):
            # Let mouse press be handled by our custom handler
            return False
        return super().eventFilter(source, event)

    # Checkbox selection logic removed; only text highlighting used

    def table_mouse_press(self, event):
        """Handle mouse press - Explorer-like selection behavior."""
        if event.button() == Qt.LeftButton:
            index = self.table.indexAt(event.position().toPoint())
            if not index.isValid():
                QTableView.mousePressEvent(self.table, event)
                return

            modifiers = event.modifiers()
            row = index.row()

            # Shift+Click: Range select from anchor to clicked row
            if modifiers & Qt.ShiftModifier:
                # Shift+Arrow: Start selection OR extend selection (Windows standard)
                if self.selection_anchor_row is None:
                    # No anchor set - start selection at current row (like original Shift+Space)
                    self._updating_selection_ui = True
                    self.selection_anchor_row = row
                    # Select all cells in this row (for SelectItems mode)
                    self.table.selectionModel().clearSelection()
                    for col in range(self.table.columnCount()):
                        index = self.table.model().index(row, col)
                        self.table.selectionModel().select(
                            index, QItemSelectionModel.Select
                        )
                    self._updating_selection_ui = False
                    # Manually sync selection (like original Shift+Space)
                    self.selected_book_ids.clear()
                    self.selected_book_ids.add(self.books[row].book_id)
                    self.update_selection_ui()
                    self.announce_selection()
                else:
                    # Anchor exists - extend selection
                    start_row = min(self.selection_anchor_row, row)
                    end_row = max(self.selection_anchor_row, row)

                    self._updating_selection_ui = True
                    self.table.selectionModel().clearSelection()

                    # Select all cells in each row
                    col_count = self.table.columnCount()
                    for r in range(start_row, end_row + 1):
                        for c in range(col_count):
                            idx = self.table.model().index(r, c)
                            self.table.selectionModel().select(
                                idx, QItemSelectionModel.Select
                            )

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

        QTableView.mousePressEvent(self.table, event)

    def table_mouse_double_click(self, event):
        """Handle mouse double-click from table viewport."""
        if event.button() == Qt.LeftButton:
            index = self.table.indexAt(event.position().toPoint())
            if index.isValid():
                row = index.row()
                column = index.column()
                if 0 <= row < len(self.books):
                    self._handle_book_table_double_click(row, column)
                    event.accept()
                    return
        QTableView.mouseDoubleClickEvent(self.table, event)

    def _handle_book_table_double_click(self, row: int, column: int):
        """Route double-click based on focused column - matches Enter behavior."""
        # Author column (0): Open author manager
        if column == 0:
            focus_ctx = self._capture_table_focus_context(row, column)
            dialog = NameListWindow(
                self.db,
                self.scaler,
                self.theme_manager,
                "author",
                initial_name=self.books[row].author_name,
                parent=self,
            )
            dialog.exec()
            self.refresh_books()
            self._restore_table_focus_context(focus_ctx)
            return

        # Title column (1): Open book details
        if column == 1:
            self.open_book_details(self.books[row])
            return

        # Series column (3): Open series manager
        if column == 3:
            focus_ctx = self._capture_table_focus_context(row, column)
            dialog = NameListWindow(
                self.db,
                self.scaler,
                self.theme_manager,
                "series",
                initial_name=(self.books[row].series_name or "").strip() or None,
                parent=self,
            )
            dialog.exec()
            self.refresh_books()
            self._restore_table_focus_context(focus_ctx)
            return

        # Genre column (4): Open genre manager
        if column == 4:
            focus_ctx = self._capture_table_focus_context(row, column)
            dialog = NameListWindow(
                self.db,
                self.scaler,
                self.theme_manager,
                "genre",
                initial_name=(self.books[row].genre_name or "").strip() or None,
                parent=self,
            )
            dialog.exec()
            self.refresh_books()
            self._restore_table_focus_context(focus_ctx)
            return

        # Read Date column (6): Open date dialog
        if column == 6:
            self.show_read_date_dialog(row)
            return

        # All other columns: do nothing (match Enter behavior)

    def table_key_press(self, event: QKeyEvent):
        """Handle key press in table."""
        # Allow default Select All (Ctrl+A) behavior
        if event.matches(QKeySequence.SelectAll):
            QTableView.keyPressEvent(self.table, event)
            return

        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            row = self.table.currentRow()
            col = self.table.currentColumn()
            if 0 <= row < len(self.books):
                if col == 6:  # Read Date column
                    self.show_read_date_dialog(row)
                    event.accept()
                    return
                elif col in (0, 3, 4):
                    self._handle_book_table_double_click(row, col)
                    event.accept()
                    return
                elif col == 1:
                    self._handle_book_table_double_click(row, col)
                    event.accept()
                    return
                else:
                    self.set_status(
                        "No action available for this column", timeout_ms=2000
                    )
                    event.accept()
                    return

            # Check for Shift+Arrow keys for selection
        if event.key() in (
            Qt.Key_Up,
            Qt.Key_Down,
            Qt.Key_PageUp,
            Qt.Key_PageDown,
            Qt.Key_Home,
            Qt.Key_End,
        ):
            modifiers = event.modifiers()
            if modifiers & Qt.ShiftModifier:
                # Shift+Arrow: Start selection OR extend selection (Windows standard)
                row = self.table.currentRow()
                if 0 <= row < len(self.books):
                    if self.selection_anchor_row is None:
                        # No anchor set - start selection at current row (like original Shift+Space)
                        self._updating_selection_ui = True
                        self.selection_anchor_row = row
                        # Select all cells in this row (for SelectItems mode)
                        self.table.selectionModel().clearSelection()
                        for col in range(self.table.columnCount()):
                            index = self.table.model().index(row, col)
                            self.table.selectionModel().select(
                                index, QItemSelectionModel.Select
                            )
                        self._updating_selection_ui = False
                        # Manually sync selection (like original Shift+Space)
                        self.selected_book_ids.clear()
                        self.selected_book_ids.add(self.books[row].book_id)
                        self.update_selection_ui()
                        self.announce_selection()
                    else:
                        # Anchor exists - extend selection
                        self.extend_selection_with_arrow(event.key())
                event.accept()
                return

            # Ctrl+Arrow: just move (Qt default)
            if modifiers & Qt.ControlModifier:
                QTableView.keyPressEvent(self.table, event)
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
        # Skip Space key handling - no longer used for selection
        elif event.key() == Qt.Key_Space:
            event.accept()
            return
        elif event.key() == Qt.Key_Escape:
            # ESC handling is done at window level (on_escape_pressed)
            # Let the window-level shortcut handle it
            event.ignore()
            return
        else:
            # Call original key press handler
            QTableView.keyPressEvent(self.table, event)

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
        """Extend selection with Shift+Arrow from anchor (set by Shift+Down/Up)."""
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
                self.table.selectionModel().select(index, QItemSelectionModel.Select)

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

    def on_current_cell_changed(self, current: QModelIndex, _previous: QModelIndex):
        """Handle current cell changes - track last focused book for search ESC restore."""
        current_row = current.row()
        current_col = current.column()
        # Track the last focused book in the table for ESC from search restore
        if 0 <= current_row < len(self.books):
            self._last_table_book_id = self.books[current_row].book_id
            self._last_table_column = current_col if current_col >= 0 else 1

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

        shortcuts_text = self._selection_shortcuts_text()
        announcement = f"{announcement}. {shortcuts_text}"

        # Keep until selection changes
        self.set_status(announcement, timeout_ms=0, announce=True)

    def update_selection_ui(self):
        """Update UI based on selection."""
        count = len(self.selected_book_ids)

        # Only show buttons if we have an actual selection
        # (not just the current row from navigation)
        has_selection = count > 0
        in_duplicate_mode = self.duplicate_mode_active
        show_action_buttons = has_selection or in_duplicate_mode

        self.update_button.setVisible(has_selection and not in_duplicate_mode)
        self.delete_button.setVisible(show_action_buttons)
        # status_hint_label removed for accessibility; no longer updated
        # Removed status shortcut hint text update for accessibility

        self.sort_label.setVisible(not show_action_buttons)

        # Enable/disable Edit menu items based on selection
        if hasattr(self, "delete_action"):
            self.delete_action.setEnabled(has_selection)
        if hasattr(self, "update_action"):
            self.update_action.setEnabled(has_selection and not in_duplicate_mode)
        if hasattr(self, "get_web_info_action"):
            # Fetch Web Info should always be enabled except in duplicate mode
            # It will use the currently focused book if no specific selection
            should_enable = not in_duplicate_mode
            self.get_web_info_action.setEnabled(should_enable)

        self.sync_selection_indicators()

        # Avoid status churn while items are selected.
        # Selection speech/status is handled by explicit announce_selection() calls.
        if has_selection:
            return

        self.set_default_status(announce=False)

    def sync_selection_indicators(self):
        # Selection highlight handled by the view; no custom indicator logic needed.
        pass

    def on_update_clicked(self):
        """Handle Update button click."""
        if self.duplicate_mode_active:
            self.set_status(
                "Selection cleared in duplicate mode. Escape to exit duplicate mode. Use Delete or Cancel Dup Mode.",
                timeout_ms=3000,
            )
            return

        if self.selected_book_ids:
            # Track the first selected row to return focus after update
            first_selected_row = None
            for row in range(self.table.rowCount()):
                if (
                    row < len(self.books)
                    and self.books[row].book_id in self.selected_book_ids
                ):
                    first_selected_row = row
                    break

            dialog = UpdateWindow(
                db=self.db,
                scaler=self.scaler,
                selected_book_ids=self.selected_book_ids,
                parent=self,
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
                        f"Updated {updated_count} books - filters cleared (no matching records)",
                        announce=True,
                    )
                else:
                    self.set_status(f"Updated {updated_count} books")

            # Return focus to the first selected row (or same position)
            if first_selected_row is not None:
                target_row = min(first_selected_row, self.table.rowCount() - 1)
                if target_row >= 0:
                    self.table.setCurrentCell(target_row, 1)  # Title column
                    self.table.setFocus()

    def on_delete_clicked(self):
        """Handle Delete button click."""
        if not self.selected_book_ids:
            if self.duplicate_mode_active:
                self.set_status(
                    "Duplicate mode active. Select books to delete, or Cancel Dup Mode.",
                    timeout_ms=3000,
                )
            return

        if self.selected_book_ids:
            count = len(self.selected_book_ids)

            # mw#25: Track the first selected row to return focus after delete
            first_selected_row = None
            for row in range(self.table.rowCount()):
                if (
                    row < len(self.books)
                    and self.books[row].book_id in self.selected_book_ids
                ):
                    first_selected_row = row
                    break

            from src.accessibility.icon_helper import get_app_icon

            reply = exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Question,
                title="Confirm Delete",
                text=f"Are you sure you want to delete {count} selected book(s)?",
                buttons=QMessageBox.Yes | QMessageBox.No,
                default_button=QMessageBox.No,
                window_icon=get_app_icon(),
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

                if self.duplicate_mode_active:
                    self._refresh_duplicate_mode_after_data_change()
                    return

                # Check if filters resulted in 0 books - clear filters to prevent freeze
                if self.table.rowCount() == 0 and self.has_active_filters():
                    self.clear_all_filters()
                    self.refresh_books()
                    self.set_status(
                        f"{deleted_count} book(s) deleted - filters cleared (no matching records)",
                        announce=True,
                    )
                    return  # Skip focus logic since table was refreshed

                # mw#25: Focus the row before the deleted selection
                if first_selected_row is not None:
                    target_row = max(0, first_selected_row - 1)
                    if target_row < self.table.rowCount():
                        self.table.setCurrentCell(target_row, 1)  # Title column
                        self.table.setFocus()

                # Show deletion message
                self.set_status(f"{deleted_count} book(s) deleted", timeout_ms=2000)

    def on_get_web_info_clicked(self, from_button=False):
        """Handle Fetch Web Info - opens web metadata window for focused/selected book."""
        # Reject button calls since we removed the button
        if from_button:
            return

        # Handle focused book (no selection) first
        row = self.table.currentRow()
        if row >= 0 and row < len(self.books):
            # We have a focused book, proceed with web fetch
            pass
        elif self.selected_book_ids:
            # Multi-book selection - ignore
            return
        else:
            # No book available
            self.set_status("No book available for web info fetch", announce=True)
            return

        book = self.books[row]

        # Show auto-closing popup dialog while fetching web info
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel
        from PySide6.QtCore import QTimer

        popup = QDialog(self)
        popup.setWindowTitle("Please wait")
        popup.setModal(True)
        popup.setWindowFlags(popup.windowFlags() | Qt.WindowStaysOnTopHint)
        layout = QVBoxLayout(popup)
        label = QLabel("Fetching book info from web, please wait...")
        layout.addWidget(label)
        popup.setLayout(layout)
        popup.resize(400, 100)

        # Auto-close after 1.8 seconds (same as book details)
        QTimer.singleShot(1800, popup.accept)
        popup.show()
        QApplication.processEvents()

        # Check web data first before opening window
        from src.ui.web_metadata import WebMetadataWindow

        # Get book data for search
        title = book.title
        author = book.author_name
        year = str(book.year) if book.year else None

        # Try to fetch web data
        web_data = None
        try:
            from src.web.web_book_api import WebBookAPI
            from PySide6.QtCore import QSettings

            # Read user preferences
            settings = QSettings("AbCS", "AudioBookCollector")
            if not settings.contains("import/flip_author_name"):
                legacy_settings = QSettings("AbCS", "AbCS")
                flip_author = legacy_settings.value(
                    "import/flip_author_name", False, type=bool
                )
            else:
                flip_author = settings.value(
                    "import/flip_author_name", False, type=bool
                )

            if not settings.contains("import/autocorrect/move_leading_the_title"):
                legacy_settings = QSettings("AbCS", "AbCS")
                move_articles = legacy_settings.value(
                    "import/autocorrect/move_leading_the_title", False, type=bool
                )
            else:
                move_articles = settings.value(
                    "import/autocorrect/move_leading_the_title", False, type=bool
                )

            # Try to fetch web data once. WebBookAPI already cascades through
            # Google Books -> Open Library -> WikiData for refresh=0.
            api = WebBookAPI()
            last_error = None

            try:
                web_data = api.get_book_metadata(
                    title,
                    author,
                    year,
                    refresh=0,
                    move_articles=move_articles,
                    flip_author=flip_author,
                )
            except Exception as e:
                last_error = str(e)

        except Exception:
            pass  # Silently fail if web fetch fails

        # Close the popup after web search is complete
        popup.close()

        # Check if we got real data (not just empty placeholders)
        is_real_match = False
        if web_data:
            # Check if any field has meaningful content
            meaningful_fields = [
                web_data.get("description"),
                web_data.get("publisher"),
                web_data.get("published_year"),
                web_data.get("isbn"),
                web_data.get("pages"),
                web_data.get("language"),
            ]
            is_real_match = any(
                field
                and str(field).strip()
                and str(field) not in ["Unknown", "N/A", "None", ""]
                for field in meaningful_fields
            )

            if is_real_match:
                # Only open window if real data found
                focus_ctx = self._capture_table_focus_context(
                    row, 1
                )  # Focus title column
                dialog = WebMetadataWindow(
                    self.db,
                    book,
                    self.scaler,
                    self.theme_manager,
                    parent=self,
                    refresh_callback=self.refresh_books,
                    web_data=web_data,
                )
                dialog.exec()
                self._restore_table_focus_context(focus_ctx)
                return

        # If no real data found, show popup and status, then return.
        no_data_text = "No information found for this book in any web source."
        if last_error:
            no_data_text = f"{no_data_text}\n\nLast error: {last_error}"

        exec_styled_message_box(
            self,
            self.scaler.get_scaled_size(20),
            icon=QMessageBox.Information,
            title="No Web Data Found",
            text=no_data_text,
        )

        self.set_status(
            "No additional web information found for this book.", timeout_ms=3000
        )
        # Restore focus even when no web data is found
        self.table.setFocus()

    def on_cancel_clicked(self):
        """Handle Cancel button click. mw#25: Focus returns to table. mw#26: Leaves focus on current cell."""
        if self.duplicate_mode_active:
            self.exit_duplicate_mode(message="Duplicate mode canceled", announce=False)
            QTimer.singleShot(0, self.table.setFocus)
            return

        self.table.clearSelection()
        self.selected_book_ids.clear()
        self.selection_anchor_row = None  # Reset anchor for keyboard selection
        self.update_selection_ui()
        # mw#13: Revert status bar to default after clearing selection
        self.set_default_status(announce=False)
        # mw#25: Return focus to table (use timer to ensure button hiding completes)
        QTimer.singleShot(0, self.table.setFocus)

    def on_escape_pressed(self):
        """Handle ESC key at window level - clears selection, shows confirmation for duplicate mode exit, then clears search/read filter."""
        # If in duplicate mode, ESC should ask to exit duplicate mode
        if self.duplicate_mode_active:
            if self.selected_book_ids or self.selection_anchor_row is not None:
                # Clear selection without confirmation (status bar shows action)
                self.selected_book_ids.clear()
                self.selection_anchor_row = None
                self._apply_row_selection_by_book_ids(set())
                self.update_selection_ui()
                self.set_status(
                    "Selection cleared in duplicate mode. Escape to exit duplicate mode."
                )
                return
            else:
                # No selection - ask to exit duplicate mode
                from src.accessibility.style_helpers import exec_styled_message_box

                reply = exec_styled_message_box(
                    self,
                    self.scaler.get_scaled_size(20),
                    icon=QMessageBox.Question,
                    title="Exit Duplicate Mode",
                    text="Exit duplicate mode and return to normal view?",
                    buttons=QMessageBox.Yes | QMessageBox.No,
                    default_button=QMessageBox.Yes,
                )
                if reply == QMessageBox.Yes:
                    self.exit_duplicate_mode(announce=True)
                return

        # First priority: clear selection mode/selected books (normal mode)
        if self.selected_book_ids or self.selection_anchor_row is not None:
            self.on_cancel_clicked()
            return
        # Second priority: clear search - use book_id to restore position (mw#29)
        if self.current_filter.has_search:
            # Use tracked book ID (set by on_current_cell_changed)
            restore_book_id = self._last_table_book_id
            restore_column = (
                self._last_table_column if self._last_table_column >= 0 else 1
            )

            # Clear filter and refresh
            self.current_filter.search_text = ""
            self.current_filter.is_keyword_search = False
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
            return
        # Third priority: clear read/unread filter
        if self.current_filter.read_filter in ("Read", "Unread"):
            # Clear read filter and refresh
            self.current_filter.read_filter = "All"
            self._sync_read_menu_selection()
            self.refresh_books()
            self.set_status("Read/Unread filter cleared", timeout_ms=2000)
            return

    def clear_status_message(self):
        """Clear temporary status message and restore default status."""
        self.set_default_status(announce=False)

    # Status bar is accessible via Qt; no manual focus logic needed.

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

    def on_reading_history(self):
        """Handle Alt+H - Show reading history window."""
        from src.ui.reading_history_window import ReadingHistoryWindow

        # Create reading history window
        reading_window = ReadingHistoryWindow(
            self.db, self.scaler, self.theme_manager, parent=self
        )

        # Show window
        reading_window.show()
        reading_window.raise_()
        reading_window.activateWindow()

    def on_new_book(self):
        """Open book details for new book."""
        # bd#8: Pass current sort order to show in header
        sort_order = self.current_filter.order_by
        details = BookDetailsWindow(
            self.db,
            self.scaler,
            sort_order=sort_order,
            parent=self,
            current_collection_id=self.current_filter.collection_id,
        )
        details.exec()

        # bd#7: If a new book was saved, get its book_id to focus on it
        new_book_id = details.book.book_id if details.book else None

        self.refresh_books()

        # bd#7: Focus the table on the newly created book (if saved)
        if new_book_id:
            self.focus_book_by_id(new_book_id)

    def on_book_list_import(self):
        """Open book list import window."""
        from src.ui.book_list_import_window import BookListImportWindow

        dialog = BookListImportWindow(
            self.db, self.scaler, self.theme_manager, parent=self
        )
        dialog.exec()
        # Refresh collections and books to show any imported items and new collections
        self.refresh_collections()
        self.refresh_books()

    def on_import(self):
        """Open import window."""
        dialog = ImportWindow(self.db, self.scaler, self.theme_manager, parent=self)
        dialog.exec()
        imported_count = getattr(dialog, "total_imported", 0)
        self.refresh_books()

        if imported_count > 0 and len(self.books) == 0:
            db_total_books = 0
            try:
                db_total_books = self.book_queries.get_statistics().total_books
            except Exception:
                db_total_books = 0

            self.current_filter = SearchFilter(order_by="Title")
            self.clear_all_filters()
            self.on_order_changed("Title")
            self.refresh_collections()
            self.current_filter.collection_id = None
            self.current_filter.read_filter = "All"
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

        self.focus_first_title_after_import_close()

    def focus_first_title_after_import_close(self):
        """Return focus to Main Window and place cursor on first Title cell."""
        self.raise_()
        self.activateWindow()

        if self.table.rowCount() <= 0:
            self.table.setFocus(Qt.TabFocusReason)
            return

        title_col = 1
        self.table.setCurrentCell(0, title_col)
        index = self.table.model().index(0, title_col)
        self.table.selectionModel().setCurrentIndex(index, QItemSelectionModel.NoUpdate)
        self.table.scrollTo(index)
        self.table.setFocus(Qt.TabFocusReason)

    def restore_main_focus_after_modal(self):
        """Ensure Main Window regains focus on a sensible table cell after modal dialogs."""
        self.raise_()
        self.activateWindow()

        if self.table.rowCount() <= 0:
            self.table.setFocus(Qt.TabFocusReason)
            return

        row = self.table.currentRow()
        if row < 0 or row >= self.table.rowCount():
            row = 0
        title_col = 1
        self.table.setCurrentCell(row, title_col)
        index = self.table.model().index(row, title_col)
        self.table.selectionModel().setCurrentIndex(index, QItemSelectionModel.NoUpdate)
        self.table.scrollTo(index)
        self.table.setFocus(Qt.TabFocusReason)

    def open_book_details(self, book: Book):
        """Open book details window."""
        # bd#8: Pass current sort order to show in header
        sort_order = self.current_filter.order_by

        # bd#4: Find current book's index in the list for Prev/Next navigation
        current_index = 0
        for i, b in enumerate(self.books):
            if b.book_id == book.book_id:
                current_index = i
                break

        details = BookDetailsWindow(
            self.db,
            self.scaler,
            book=book,
            sort_order=sort_order,
            books_list=self.books,
            current_index=current_index,
            parent=self,
        )
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
        focus_ctx = self._capture_table_focus_context()
        dialog = PreferencesWindow(self.scaler, self.theme_manager, parent=self)
        dialog.exec()
        self._restore_table_focus_context(focus_ctx)
        self.restore_main_focus_after_modal()

    def on_show_splash(self):
        """Show library statistics or setup dialog if empty DB."""
        stats_queries = StatisticsQueries(self.db)
        stats = stats_queries.get_statistics()

        if stats.total_books == 0:
            # Show accessible SetupDialog for empty DB
            from src.ui.setup_dialogue import SetupDialog

            focus_ctx = self._capture_table_focus_context()
            dlg = SetupDialog(self.scaler, parent=self)
            dlg.exec()
            self._restore_table_focus_context(focus_ctx)
            self.restore_main_focus_after_modal()
        else:
            focus_ctx = self._capture_table_focus_context()
            dlg = StatisticsDialog(stats, self.scaler, parent=self)
            dlg.exec()
            self._restore_table_focus_context(focus_ctx)
            self.restore_main_focus_after_modal()

    def on_show_authors(self):
        """Open Author window."""
        focus_ctx = self._capture_table_focus_context()
        dialog = NameListWindow(
            self.db,
            self.scaler,
            self.theme_manager,
            "author",
            parent=self,
        )
        dialog.exec()
        self.refresh_books()
        self._restore_table_focus_context(focus_ctx)

    def on_show_collection(self):
        """Open collection window."""
        previous_collection_id = self.current_filter.collection_id
        focus_ctx = self._capture_table_focus_context()

        dialog = CollectionWindow(
            self.db,
            self.scaler,
            self.theme_manager,
            parent=self,
        )
        dialog.exec()

        self.refresh_collections()

        valid_ids = {
            collection_id
            for _label, collection_id in self._collection_filter_items
            if collection_id is not None
        }
        if previous_collection_id is not None and previous_collection_id in valid_ids:
            self.current_filter.collection_id = previous_collection_id
        else:
            self.current_filter.collection_id = None

        self.refresh_books()
        self._restore_table_focus_context(focus_ctx)

    def on_show_Genre(self):
        """Open Genre( window."""
        focus_ctx = self._capture_table_focus_context()
        dialog = NameListWindow(
            self.db,
            self.scaler,
            self.theme_manager,
            "genre",
            parent=self,
        )
        dialog.exec()
        self.refresh_books()
        self._restore_table_focus_context(focus_ctx)

    def on_show_Series(self):
        """Open Series window."""
        focus_ctx = self._capture_table_focus_context()
        dialog = NameListWindow(
            self.db,
            self.scaler,
            self.theme_manager,
            "series",
            parent=self,
        )
        dialog.exec()
        self.refresh_books()
        self._restore_table_focus_context(focus_ctx)

    def on_backup_restore(self):
        """Open backup_restore window."""
        focus_ctx = self._capture_table_focus_context()
        dialog = BackupRestoreWindow(
            self.db,
            self.scaler,
            self.theme_manager,
            parent=self,
        )
        dialog.exec()
        if dialog.data_changed:
            # Re-initialize all query objects to ensure new DB connection is used
            self.book_queries = BookQueries(self.db)
            self.author_queries = AuthorQueries(self.db)
            self.series_queries = SeriesQueries(self.db)
            self.genre_queries = GenreQueries(self.db)
            self.collection_queries = CollectionQueries(self.db)
            self.refresh_collections()
            self.current_filter.collection_id = None  # Reset to All Collections
            self._sync_collection_menu_selection()
            self.refresh_books()
            self.set_status(
                "Database updated from backup/restore operation. Showing All Collections."
            )
        self._restore_table_focus_context(focus_ctx)

    def on_about(self):
        # TEST: Use AboutDialog from about_dialogue.py instead of internal popup
        from src.ui.about_dialogue import AboutDialog

        dlg = AboutDialog(self.scaler, self)
        dlg.exec()
        self.set_status("About dialog opened (external AboutDialog test)")
        self.restore_main_focus_after_modal()
        # --- Internal implementation commented out for test ---
        # ...existing code...

    def on_show_license(self):
        """Show the new accessible license dialog."""
        dlg = LicenseDialog(self.scaler, self)
        dlg.exec()
        self.set_status("License dialog opened. Press Tab to move to OK button.")
        self.restore_main_focus_after_modal()

    def on_show_shortcuts(self):
        """Show keyboard shortcuts help in a table for screen reader accessibility."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Keyboard Shortcuts - Main Window")
        dlg.setAccessibleName("")
        dlg.setAccessibleDescription("")
        dlg.resize(500, 600)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        shortcuts = [
            ("Alt+1", "Jump to Author"),
            ("Alt+2", "Jump to Title"),
            ("Alt+3", "Jump to Year"),
            ("Alt+4", "Jump to Series"),
            ("Alt+5", "Jump to Genre"),
            ("Alt+6", "Jump to Time"),
            ("Alt+7", "Jump to Read Date"),
            ("Shift+Down/Up", "Start selection or extend selection"),
            ("Alt+U", "Update selected"),
            ("Alt+D", "Delete selected"),
            ("Ctrl+F", "Find"),
            ("Ctrl+I", "Import"),
            ("Ctrl+N", "New book"),
            (
                "Enter",
                "Open focused item (Title=details; Author/Series/Genre=manager; Read Date=set date)",
            ),
            ("Escape", "Clear selection/search/read filter"),
            ("Ctrl+Plus", "Zoom in"),
            ("Ctrl+Minus", "Zoom out"),
            ("Ctrl+0", "Reset zoom"),
            ("Alt+/", "Read status bar"),
            ("F1", "Show keyboard shortcuts"),
        ]
        # Centralize Alt+/ visibility and order
        from src.accessibility.shortcut_helpers import (
            get_accessible_shortcuts_list,
            build_accessible_f1_popup_style,
        )

        shortcuts = get_accessible_shortcuts_list(shortcuts)

        # Create table with 1 column
        table = QTableWidget()
        table.setAccessibleName("")
        table.setAccessibleDescription("")
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels([""])
        table.setRowCount(len(shortcuts))
        table.setVerticalHeaderLabels([""] * len(shortcuts))
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.NoSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setTabKeyNavigation(False)
        table.setAlternatingRowColors(False)
        table.verticalHeader().setVisible(False)
        # Disable mouse hover and highlight
        table.setMouseTracking(False)
        table.viewport().setMouseTracking(False)
        table.setAttribute(Qt.WA_Hover, False)
        table.viewport().setAttribute(Qt.WA_Hover, False)
        # Apply centralized F1 popup style
        table.setStyleSheet(build_accessible_f1_popup_style())
        table.horizontalHeader().setVisible(False)
        table.setShowGrid(False)

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

        QTimer.singleShot(0, lambda: table.setFocus(Qt.TabFocusReason))
        focus_ctx = self._capture_table_focus_context()
        dlg.exec()
        self._restore_table_focus_context(focus_ctx)
        self.restore_main_focus_after_modal()

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
        if not hasattr(self, "_stretch_columns") or not hasattr(self, "table"):
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
