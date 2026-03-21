"""
Reading History Window - Audio Book Collection
Shows reading statistics and history with full accessibility support.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QLabel, QPushButton,
    QDateEdit, QComboBox, QLineEdit, QGroupBox,
    QHeaderView, QAbstractItemView, QStatusBar, QMessageBox
)
from PySide6.QtCore import (
    Qt, QDate, QSettings, QTimer, QItemSelection, QItemSelectionModel
)
from PySide6.QtGui import QAction, QShortcut, QKeySequence, QAccessible

from src.database import BookQueries, ReadingQueries
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
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
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
        controls_layout.addLayout(filter_layout)
        
        main_layout.addWidget(controls_group)
        
        # Statistics section
        stats_group = QGroupBox("Reading Statistics")
        stats_layout = QHBoxLayout(stats_group)
        
        # Statistics labels
        self.total_books_label = QLabel("Total Books Read: 0")
        self.total_books_label.setAccessibleName("Total books read")
        
        self.total_hours_label = QLabel("Total Hours: 0.0")
        self.total_hours_label.setAccessibleName("Total hours")
        
        self.avg_books_per_month_label = QLabel("Avg Books/Month: 0.0")
        self.avg_books_per_month_label.setAccessibleName("Average books per month")
        
        stats_layout.addWidget(self.total_books_label)
        stats_layout.addWidget(self.total_hours_label)
        stats_layout.addWidget(self.avg_books_per_month_label)
        stats_layout.addStretch()
        
        main_layout.addWidget(stats_group)
        
        # History table
        self.table = QTableWidget()
        self.table.setAccessibleName("Reading history table")
        self.table.setAccessibleDescription("Table showing reading history with date, title, author, and hours")
        
        # Setup table columns
        headers = ["Date", "Title", "Author", "Hours", "Collection"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        
        # Table configuration
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setSectionsClickable(False)
        self.table.verticalHeader().setHighlightSections(False)
        self.table.verticalHeader().setAccessibleName("")
        
        # Configure header
        header = self.table.horizontalHeader()
        header.setSectionsClickable(True)
        header.setSortIndicatorShown(True)
        header.setSortIndicator(0, Qt.DescendingOrder)  # Sort by date descending
        header.setMinimumSectionSize(100)
        header.setStretchLastSection(True)
        
        # Apply accessible styling
        self.apply_accessible_styling()
        
        main_layout.addWidget(self.table)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setAccessibleName("Status bar")
        
        # Connect signals
        self.refresh_button.clicked.connect(self.load_reading_data)
        self.start_date_edit.dateChanged.connect(self.load_reading_data)
        self.end_date_edit.dateChanged.connect(self.load_reading_data)
        self.collection_combo.currentIndexChanged.connect(self.load_reading_data)
        header.sectionClicked.connect(self.on_table_header_clicked)
        
        # Apply theme
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
        self.on_theme_changed()

    def setup_shortcuts(self):
        """Setup keyboard shortcuts using ShortcutManager."""
        mgr = get_shortcut_manager()
        callback_map = {
            'refresh_button': lambda: self.refresh_button.click(),
            'date_start': lambda: self.start_date_edit.setFocus(),
            'date_end': lambda: self.end_date_edit.setFocus(),
            'collection_filter': lambda: self.collection_combo.setFocus(),
            'history_table': lambda: self.table.setFocus(),
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
        self.table.setStyleSheet(build_accessible_f1_popup_style())
        
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
            # Get filter criteria
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
            
            # Update statistics
            self.update_statistics(filtered_books)
            
            # Populate table
            self.populate_table(filtered_books)
            
            self.set_status(f"Showing {len(filtered_books)} books in reading history")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load reading history: {str(e)}")
        finally:
            self._loading = False

    def update_statistics(self, books):
        """Update statistics labels."""
        total_books = len(books)
        total_hours = sum(book.time_hours or 0 for book in books)
        
        # Calculate average books per month
        if total_books > 0:
            # Get date range in months
            start_date = self.start_date_edit.date()
            end_date = self.end_date_edit.date()
            months = max(1, start_date.daysTo(end_date) // 30)
            avg_per_month = total_books / months
        else:
            avg_per_month = 0.0
        
        self.total_books_label.setText(f"Total Books Read: {total_books}")
        self.total_hours_label.setText(f"Total Hours: {total_hours:.1f}")
        self.avg_books_per_month_label.setText(f"Avg Books/Month: {avg_per_month:.1f}")

    def populate_table(self, books):
        """Populate table with reading history data."""
        self.table.setRowCount(0)
        
        for row, book in enumerate(books):
            self.table.insertRow(row)
            
            # Date
            date_item = QTableWidgetItem(book.read_date.toString("yyyy-MM-dd") if book.read_date else "")
            date_item.setAccessibleName(f"Read date: {date_item.text()}")
            self.table.setItem(row, 0, date_item)
            
            # Title
            title_item = QTableWidgetItem(book.title or "")
            title_item.setAccessibleName(f"Title: {title_item.text()}")
            self.table.setItem(row, 1, title_item)
            
            # Author
            author_item = QTableWidgetItem(book.author_name or "")
            author_item.setAccessibleName(f"Author: {author_item.text()}")
            self.table.setItem(row, 2, author_item)
            
            # Hours
            hours_item = QTableWidgetItem(str(book.time_hours or 0))
            hours_item.setAccessibleName(f"Hours: {hours_item.text()}")
            self.table.setItem(row, 3, hours_item)
            
            # Collection
            collection_item = QTableWidgetItem(book.collection_name or "")
            collection_item.setAccessibleName(f"Collection: {collection_item.text()}")
            self.table.setItem(row, 4, collection_item)

    def on_table_header_clicked(self, column: int):
        """Handle table header clicks for sorting."""
        if self.table.rowCount() == 0:
            return
        
        # Toggle sort order if same column, otherwise use ascending
        if hasattr(self, '_last_sort_column') and self._last_sort_column == column:
            next_order = Qt.DescendingOrder if hasattr(self, '_last_sort_order') and self._last_sort_order == Qt.AscendingOrder else Qt.AscendingOrder
        else:
            next_order = Qt.AscendingOrder
        
        self._last_sort_column = column
        self._last_sort_order = next_order
        
        self.table.horizontalHeader().setSortIndicator(column, next_order)
        self.sort_table(column, next_order)
        
        # Announce sort for accessibility
        headers = ["Date", "Title", "Author", "Hours", "Collection"]
        header_text = headers[column] if column < len(headers) else "Column"
        direction = "descending" if next_order == Qt.DescendingOrder else "ascending"
        self.set_status(f"Sorted by {header_text} ({direction})", announce=True)

    def sort_table(self, column: int, order: Qt.SortOrder):
        """Sort table by column."""
        # Get current data
        data = []
        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        
        # Sort data
        reverse = order == Qt.DescendingOrder
        data.sort(key=lambda row: row[column].lower(), reverse=reverse)
        
        # Repopulate table
        for row, row_data in enumerate(data):
            for col, text in enumerate(row_data):
                item = QTableWidgetItem(text)
                item.setAccessibleName(f"Row {row+1}, Column {col+1}: {text}")
                self.table.setItem(row, col, item)

    def load_collections(self):
        """Load collections into combo box."""
        from src.database import CollectionQueries
        collection_queries = CollectionQueries(self.db)
        collections = collection_queries.get_all()
        self.collection_combo.clear()
        self.collection_combo.addItem("All Collections", None)
        
        for collection in collections:
            self.collection_combo.addItem(collection.name, collection.collection_id)

    def on_theme_changed(self):
        """Handle theme change."""
        self.apply_accessible_styling()

    def on_show_shortcuts(self):
        """Show keyboard shortcuts help."""
        shortcuts = [
            ("Alt+R", "Refresh data"),
            ("Alt+1", "Focus start date"),
            ("Alt+2", "Focus end date"),
            ("Alt+3", "Focus collection filter"),
            ("Alt+4", "Focus history table"),
            ("Enter", "Open selected book details"),
            ("Alt+/", "Read status bar"),
            ("F1", "Show this help"),
            ("Escape", "Close window"),
        ]
        
        # Create help dialog
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QTableWidget
        help_dialog = QDialog(self)
        help_dialog.setWindowTitle("Reading History Shortcuts")
        help_dialog.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(help_dialog)
        
        # Create shortcuts table
        table = QTableWidget()
        table.setRowCount(len(shortcuts))
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Shortcut", "Action"])
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectItems)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setAlternatingRowColors(False)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setMouseTracking(False)
        table.viewport().setMouseTracking(False)
        table.setAttribute(Qt.WA_Hover, False)
        table.viewport().setAttribute(Qt.WA_Hover, False)
        
        # Apply F1 popup style
        from src.accessibility.shortcut_helpers import build_accessible_f1_popup_style
        table.setStyleSheet(build_accessible_f1_popup_style())
        
        # Populate shortcuts
        for row, (key, desc) in enumerate(shortcuts):
            table.setItem(row, 0, QTableWidgetItem(key))
            table.setItem(row, 1, QTableWidgetItem(desc))
        
        layout.addWidget(table)
        help_dialog.setLayout(layout)
        help_dialog.exec()

    def on_read_status_bar(self):
        """Read current status bar message (Alt+/)."""
        status_text = self._default_status_message
        if QAccessible.isActive():
            self.set_status(status_text, announce=True)
        else:
            exec_styled_message_box(
                self,
                "Status Bar",
                status_text
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

    def keyPressEvent(self, event):
        """Handle key press events."""
        # Prevent Enter from closing dialog
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            event.ignore()
            return
        super().keyPressEvent(event)

    def closeEvent(self, event):
        """Handle window close event."""
        # No cleanup needed - shortcuts are automatically managed
        super().closeEvent(event)
