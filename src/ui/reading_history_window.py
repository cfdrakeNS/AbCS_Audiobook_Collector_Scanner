"""
Reading History Window - Audio Book Collection
Shows reading statistics and history with full accessibility support.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QLabel, QPushButton,
    QDateEdit, QComboBox, QLineEdit, QGroupBox,
    QHeaderView, QAbstractItemView, QStatusBar, QMessageBox,
    QTabWidget
)
from PySide6.QtCore import (
    Qt, QDate, QSettings, QTimer, QItemSelection, QItemSelectionModel
)
from PySide6.QtGui import QAction, QShortcut, QKeySequence, QAccessible

from src.database import BookQueries, ReadingQueries, SearchFilter
from src.accessibility.scaling import UIScaler
from src.accessibility.accessible_events import announce_status_message
from src.accessibility.style_helpers import exec_styled_message_box, build_accessible_button_style
from src.accessibility.theme_manager import ThemeManager
from src.accessibility.shortcuts import get_shortcut_manager, ShortcutContext
from src.accessibility.key_filters import is_unmapped_alt_letter
from src.accessibility.shortcut_helpers import build_accessible_f1_popup_style


class ReadingHistoryWindow(QMainWindow):
    """Reading History window with statistics and history table."""

    def __init__(self, db, scaler: UIScaler, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self.db = db
        self.scaler = scaler
        self.theme_manager = theme_manager
        self.book_queries = BookQueries(db)
        self.reading_queries = ReadingQueries(db)
        self._default_status_message = "Ready"
        self._loading = False
        
        # Window setup
        self.setWindowTitle("Reading History")
        self.setMinimumSize(800, 600)
        self.resize(1200, 800)
        
        self.setup_ui()
        self.setup_shortcuts()
        self.load_reading_data()

    def setup_ui(self):
        """Setup user interface with tabs."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setAccessibleName("Reading history tabs")
        
        # Create tabs
        self.create_general_tab()
        self.create_year_tab()
        self.create_month_tab()
        self.create_date_range_tab()
        
        main_layout.addWidget(self.tab_widget)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setAccessibleName("Status bar")
        
        # Connect signals
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # Apply theme
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
        self.on_theme_changed()

    def create_general_tab(self):
        """Create General tab with overall statistics."""
        general_widget = QWidget()
        general_layout = QVBoxLayout(general_widget)
        
        # Statistics section
        stats_group = QGroupBox("Overall Reading Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        # Statistics labels
        self.total_books_label = QLabel("Total Books Read: 0")
        self.total_books_label.setAccessibleName("Total books read")
        
        self.total_hours_label = QLabel("Total Hours Read: 0.0")
        self.total_hours_label.setAccessibleName("Total hours read")
        
        self.avg_hours_label = QLabel("Average Hours per Book: 0.0")
        self.avg_hours_label.setAccessibleName("Average hours per book")
        
        stats_layout.addWidget(self.total_books_label)
        stats_layout.addWidget(self.total_hours_label)
        stats_layout.addWidget(self.avg_hours_label)
        stats_layout.addStretch()
        
        general_layout.addWidget(stats_group)
        general_layout.addStretch()
        
        self.tab_widget.addTab(general_widget, "&General")

    def create_year_tab(self):
        """Create Year tab with yearly breakdown."""
        year_widget = QWidget()
        year_layout = QVBoxLayout(year_widget)
        
        # Year table
        self.year_table = QTableWidget()
        self.year_table.setAccessibleName("Yearly reading statistics table")
        self.year_table.setAccessibleDescription("Table showing books read per year")
        
        # Setup table columns
        year_headers = ["Year", "Books Read", "Total Hours"]
        self.year_table.setColumnCount(len(year_headers))
        self.year_table.setHorizontalHeaderLabels(year_headers)
        
        # Table configuration
        self.year_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.year_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.year_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.year_table.setAlternatingRowColors(False)
        self.year_table.verticalHeader().setVisible(False)
        self.year_table.verticalHeader().setSectionsClickable(False)
        self.year_table.verticalHeader().setHighlightSections(False)
        self.year_table.verticalHeader().setAccessibleName("")
        
        # Configure header
        header = self.year_table.horizontalHeader()
        header.setSectionsClickable(True)
        header.setSortIndicatorShown(True)
        header.setSortIndicator(0, Qt.DescendingOrder)
        header.setMinimumSectionSize(100)
        header.setStretchLastSection(True)
        
        year_layout.addWidget(self.year_table)
        self.tab_widget.addTab(year_widget, "&Year")

    def create_month_tab(self):
        """Create Month tab with monthly breakdown."""
        month_widget = QWidget()
        month_layout = QVBoxLayout(month_widget)
        
        # Month table
        self.month_table = QTableWidget()
        self.month_table.setAccessibleName("Monthly reading statistics table")
        self.month_table.setAccessibleDescription("Table showing books read per month")
        
        # Setup table columns
        month_headers = ["Month", "Year", "Books Read", "Total Hours"]
        self.month_table.setColumnCount(len(month_headers))
        self.month_table.setHorizontalHeaderLabels(month_headers)
        
        # Table configuration
        self.month_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.month_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.month_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.month_table.setAlternatingRowColors(False)
        self.month_table.verticalHeader().setVisible(False)
        self.month_table.verticalHeader().setSectionsClickable(False)
        self.month_table.verticalHeader().setHighlightSections(False)
        self.month_table.verticalHeader().setAccessibleName("")
        
        # Configure header
        header = self.month_table.horizontalHeader()
        header.setSectionsClickable(True)
        header.setSortIndicatorShown(True)
        header.setSortIndicator(0, Qt.DescendingOrder)
        header.setMinimumSectionSize(100)
        header.setStretchLastSection(True)
        
        month_layout.addWidget(self.month_table)
        self.tab_widget.addTab(month_widget, "&Month")

    def create_date_range_tab(self):
        """Create Date Range tab with filtering."""
        range_widget = QWidget()
        range_layout = QVBoxLayout(range_widget)
        
        # Controls section
        controls_group = QGroupBox("Date Range & Filters")
        controls_layout = QVBoxLayout(controls_group)
        
        # Date range controls
        date_layout = QHBoxLayout()
        
        # Start date
        start_date_label = QLabel("From:")
        start_date_label.setAccessibleName("Start date")
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setAccessibleName("Start date")
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addMonths(-12))
        
        # End date
        end_date_label = QLabel("To:")
        end_date_label.setAccessibleName("End date")
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setAccessibleName("End date")
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        
        date_layout.addWidget(start_date_label)
        date_layout.addWidget(self.start_date_edit)
        date_layout.addWidget(end_date_label)
        date_layout.addWidget(self.end_date_edit)
        date_layout.addStretch()
        
        controls_layout.addLayout(date_layout)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        # Collection filter
        collection_label = QLabel("Collection:")
        collection_label.setAccessibleName("Collection filter")
        self.collection_combo = QComboBox()
        self.collection_combo.setAccessibleName("Collection filter")
        self.collection_combo.setAccessibleDescription("Filter reading history by collection")
        
        # Refresh button
        self.refresh_button = QPushButton("&Refresh")
        self.refresh_button.setAccessibleName("Refresh")
        self.refresh_button.setAccessibleDescription("Refresh reading history data - Alt+R")
        
        filter_layout.addWidget(collection_label)
        filter_layout.addWidget(self.collection_combo)
        filter_layout.addWidget(self.refresh_button)
        filter_layout.addStretch()
        
        controls_layout.addLayout(filter_layout)
        
        # Period statistics
        period_stats_layout = QHBoxLayout()
        
        self.period_books_label = QLabel("Books in Period: 0")
        self.period_books_label.setAccessibleName("Books in period")
        
        self.period_hours_label = QLabel("Hours in Period: 0.0")
        self.period_hours_label.setAccessibleName("Hours in period")
        
        period_stats_layout.addWidget(self.period_books_label)
        period_stats_layout.addWidget(self.period_hours_label)
        period_stats_layout.addStretch()
        
        controls_layout.addLayout(period_stats_layout)
        range_layout.addWidget(controls_group)
        
        # History table
        self.range_table = QTableWidget()
        self.range_table.setAccessibleName("Date range reading history table")
        self.range_table.setAccessibleDescription("Table showing reading history with date, title, author, and length")
        
        # Setup table columns
        range_headers = ["Date", "Title", "Author", "Length", "Hours"]
        self.range_table.setColumnCount(len(range_headers))
        self.range_table.setHorizontalHeaderLabels(range_headers)
        
        # Table configuration
        self.range_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.range_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.range_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.range_table.setAlternatingRowColors(False)
        self.range_table.verticalHeader().setVisible(False)
        self.range_table.verticalHeader().setSectionsClickable(False)
        self.range_table.verticalHeader().setHighlightSections(False)
        self.range_table.verticalHeader().setAccessibleName("")
        
        # Configure header
        header = self.range_table.horizontalHeader()
        header.setSectionsClickable(True)
        header.setSortIndicatorShown(True)
        header.setSortIndicator(0, Qt.DescendingOrder)
        header.setMinimumSectionSize(100)
        header.setStretchLastSection(True)
        
        range_layout.addWidget(self.range_table)
        
        self.tab_widget.addTab(range_widget, "Date &Range")

    def setup_shortcuts(self):
        """Setup keyboard shortcuts using ShortcutManager."""
        mgr = get_shortcut_manager()
        callback_map = {
            'refresh_button': lambda: self.refresh_button.click(),
        }
        mgr.register_alt_shortcuts(
            self, ShortcutContext.READING_HISTORY_WINDOW, callback_map)

        # F1 for help
        self.help_shortcut = QShortcut(QKeySequence("F1"), self)
        self.help_shortcut.activated.connect(self.on_show_shortcuts)

        # Alt+/ for status bar read
        self.read_status_bar_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.read_status_bar_shortcut.activated.connect(self.on_read_status_bar)

    def apply_accessible_styling(self):
        """Apply accessible styling following import window pattern."""
        # Button styling
        button_style = build_accessible_button_style(self.scaler.get_scaled_size(20))
        
        for widget in self.findChildren(QPushButton):
            widget.setStyleSheet(button_style)
        
        # Table styling - use centralized F1 popup style
        from src.accessibility.shortcut_helpers import build_accessible_f1_popup_style
        table_style = build_accessible_f1_popup_style()
        
        for table in [self.year_table, self.month_table, self.range_table]:
            if table:
                table.setStyleSheet(table_style)
        
        # Date edit and combo box styling - let theme manager handle it
        for widget in self.findChildren(QDateEdit):
            widget.setStyleSheet("")
        for widget in self.findChildren(QComboBox):
            widget.setStyleSheet("")

    def load_reading_data(self):
        """Load reading history data based on current filters."""
        if self._loading:
            return
            
        self._loading = True
        try:
            # Get overall statistics
            stats = self.reading_queries.get_reading_statistics()
            self.update_general_stats(stats)
            
            # Get yearly breakdown
            yearly_data = stats.get('yearly_breakdown', [])
            self.populate_year_table(yearly_data)
            
            # Get monthly breakdown
            monthly_data = stats.get('monthly_breakdown', [])
            self.populate_month_table(monthly_data)
            
            # Load date range data
            self.load_date_range_data()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load reading history: {str(e)}")
        finally:
            self._loading = False

    def update_general_stats(self, stats):
        """Update general statistics labels."""
        self.total_books_label.setText(f"Total Books Read: {stats['total_books']}")
        self.total_hours_label.setText(f"Total Hours Read: {stats['total_hours']:.1f}")
        self.avg_hours_label.setText(f"Average Hours per Book: {stats['avg_hours_per_book']:.1f}")

    def populate_year_table(self, yearly_data):
        """Populate year table with yearly breakdown."""
        self.year_table.setRowCount(0)
        
        for row, year_data in enumerate(yearly_data):
            self.year_table.insertRow(row)
            
            # Year
            year_item = QTableWidgetItem(str(year_data['year']))
            year_item.setAccessibleName(f"Year: {year_item.text()}")
            self.year_table.setItem(row, 0, year_item)
            
            # Books read
            books_item = QTableWidgetItem(str(year_data['book_count']))
            books_item.setAccessibleName(f"Books read: {books_item.text()}")
            self.year_table.setItem(row, 1, books_item)
            
            # Total hours
            hours_item = QTableWidgetItem(f"{year_data['total_hours']:.1f}")
            hours_item.setAccessibleName(f"Total hours: {hours_item.text()}")
            self.year_table.setItem(row, 2, hours_item)

    def populate_month_table(self, monthly_data):
        """Populate month table with monthly breakdown."""
        self.month_table.setRowCount(0)
        
        for row, month_data in enumerate(monthly_data):
            self.month_table.insertRow(row)
            
            # Month name
            month_item = QTableWidgetItem(month_data['month_name'])
            month_item.setAccessibleName(f"Month: {month_item.text()}")
            self.month_table.setItem(row, 0, month_item)
            
            # Year
            year_item = QTableWidgetItem(str(month_data['year']))
            year_item.setAccessibleName(f"Year: {year_item.text()}")
            self.month_table.setItem(row, 1, year_item)
            
            # Books read
            books_item = QTableWidgetItem(str(month_data['book_count']))
            books_item.setAccessibleName(f"Books read: {books_item.text()}")
            self.month_table.setItem(row, 2, books_item)
            
            # Total hours
            hours_item = QTableWidgetItem(f"{month_data['total_hours']:.1f}")
            hours_item.setAccessibleName(f"Total hours: {hours_item.text()}")
            self.month_table.setItem(row, 3, hours_item)

    def load_date_range_data(self):
        """Load data for date range tab."""
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        collection_id = self.collection_combo.currentData()
        
        # Query books with read dates
        filter_criteria = SearchFilter(
            collection_id=collection_id,
            read_filter="Read"  # Only read books
        )
        
        books = self.book_queries.get_all(filter_criteria)
        
        # Filter by date range
        filtered_books = []
        for book in books:
            if book.read_date:
                book_date = book.read_date.toString("yyyy-MM-dd")
                if start_date <= book_date <= end_date:
                    filtered_books.append(book)
        
        # Update period statistics
        total_books = len(filtered_books)
        total_hours = sum(book.time_hours or 0 for book in filtered_books)
        
        self.period_books_label.setText(f"Books in Period: {total_books}")
        self.period_hours_label.setText(f"Hours in Period: {total_hours:.1f}")
        
        # Populate table
        self.populate_range_table(filtered_books)
        
        self.set_status(f"Showing {total_books} books in date range")

    def populate_range_table(self, books):
        """Populate date range table with reading history data."""
        self.range_table.setRowCount(0)
        
        for row, book in enumerate(books):
            self.range_table.insertRow(row)
            
            # Date
            date_item = QTableWidgetItem(book.read_date.toString("yyyy-MM-dd") if book.read_date else "")
            date_item.setAccessibleName(f"Read date: {date_item.text()}")
            self.range_table.setItem(row, 0, date_item)
            
            # Title
            title_item = QTableWidgetItem(book.title or "")
            title_item.setAccessibleName(f"Title: {title_item.text()}")
            self.range_table.setItem(row, 1, title_item)
            
            # Author
            author_item = QTableWidgetItem(book.author_name or "")
            author_item.setAccessibleName(f"Author: {author_item.text()}")
            self.range_table.setItem(row, 2, author_item)
            
            # Length (tracks)
            length_item = QTableWidgetItem(str(book.tracks or 0))
            length_item.setAccessibleName(f"Length: {length_item.text()}")
            self.range_table.setItem(row, 3, length_item)
            
            # Hours
            hours_item = QTableWidgetItem(str(book.time_hours or 0))
            hours_item.setAccessibleName(f"Hours: {hours_item.text()}")
            self.range_table.setItem(row, 4, hours_item)

    def on_tab_changed(self, index):
        """Handle tab change."""
        tab_names = ["General", "Year", "Month", "Date Range"]
        if index < len(tab_names):
            self.set_status(f"Viewing {tab_names[index]} statistics", announce=True)

    def on_theme_changed(self):
        """Handle theme change."""
        self.apply_accessible_styling()

    def on_show_shortcuts(self):
        """Show keyboard shortcuts help dialog."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Keyboard Shortcuts - Reading History")
        dlg.setAccessibleName("Keyboard Shortcuts")
        dlg.resize(560, 420)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        table = QTableWidget()
        table.setAccessibleName("Shortcuts list")
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels([""])

        shortcuts = [
            ("Alt+G", "General tab"),
            ("Alt+Y", "Year tab"),
            ("Alt+M", "Month tab"),
            ("Alt+R", "Date Range tab"),
            ("Enter", "Open selected book details"),
            ("Alt+/", "Read status bar"),
            ("F1", "Show this help"),
            ("Escape", "Close window"),
        ]

        table.setRowCount(len(shortcuts))
        table.setVerticalHeaderLabels([""] * len(shortcuts))
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectItems)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setTabKeyNavigation(False)
        table.setAlternatingRowColors(False)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setMouseTracking(False)
        table.viewport().setMouseTracking(False)
        table.setAttribute(Qt.WA_Hover, False)
        table.viewport().setAttribute(Qt.WA_Hover, False)
        
        # Apply centralized F1 popup style
        from src.accessibility.shortcut_helpers import get_accessible_shortcuts_list, build_accessible_f1_popup_style
        # Centralize Alt+/ visibility and order for screen readers
        shortcuts = get_accessible_shortcuts_list(shortcuts)
        table.setStyleSheet(build_accessible_f1_popup_style())

        for row, (key, desc) in enumerate(shortcuts):
            item = QTableWidgetItem(f"{desc} - {key}")
            item.setData(Qt.AccessibleTextRole, f"{desc}: {key}")
            table.setItem(row, 0, item)

        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        font = table.font()
        font.setPointSize(self.scaler.get_scaled_size(11))
        table.setFont(font)

        layout.addWidget(table)
        dlg.setLayout(layout)
        dlg.exec()

    def on_read_status_bar(self):
        """Read current status bar message (Alt+/)."""
        status_text = self._default_status_message
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

    def set_status(self, message: str, announce: bool = False):
        """Set status bar message with optional screen reader announcement."""
        self._default_status_message = message
        announce_status_message(self.status_bar, message, move_focus=announce)

    def showEvent(self, event):
        """Handle window show event."""
        super().showEvent(event)
        # Load collections when window is shown
        if not hasattr(self, '_collections_loaded'):
            self.load_collections()
            self._collections_loaded = True

    def load_collections(self):
        """Load collections into combo box."""
        from src.database import CollectionQueries
        collection_queries = CollectionQueries(self.db)
        collections = collection_queries.get_all()
        self.collection_combo.clear()
        self.collection_combo.addItem("All Collections", None)
        
        for collection in collections:
            self.collection_combo.addItem(collection.name, collection.collection_id)

    def keyPressEvent(self, event):
        """Handle key press events."""
        # Escape key closes window
        if event.key() == Qt.Key_Escape:
            self.close()
            event.accept()
            return
        
        # Prevent Enter from closing dialog
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            event.ignore()
            return
        super().keyPressEvent(event)

    def closeEvent(self, event):
        """Handle window close event."""
        # No cleanup needed - shortcuts are automatically managed
        super().closeEvent(event)
