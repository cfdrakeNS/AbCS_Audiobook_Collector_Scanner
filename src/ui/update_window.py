"""
Update Window - Bulk update for selected books.
Allows mass updating or removing of Series, Genre, and Collection for selected books.
Updates occur immediately when a selection is made.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QComboBox, QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QStatusBar, QMessageBox, QApplication,
    QLineEdit, QWidget
)
from PySide6.QtCore import Qt, QEvent, QTimer
from PySide6.QtGui import QShortcut, QKeySequence, QAccessible
from typing import Set, List

from database import (
    DatabaseManager, Book, BookQueries, SeriesQueries,
    GenreQueries, CollectionQueries
)
from accessibility.scaling import UIScaler


# Special marker for "None" option to clear a field
NONE_MARKER = "__NONE__"


class UpdateWindow(QDialog):
    """
    Update dialog for bulk updating Series, Genre, and Collection.
    Updates occur immediately when a combo selection is made.
    Select "None" to clear/remove a field value from selected books.
    """

    def __init__(self, db: DatabaseManager, scaler: UIScaler,
                 selected_book_ids: Set[int], parent=None):
        """
        Initialize update window.

        Args:
            db: Database manager
            scaler: UI scaler
            selected_book_ids: Set of book IDs to update
            parent: Parent widget
        """
        super().__init__(parent)

        self.db = db
        self.scaler = scaler
        self.selected_book_ids = set(
            selected_book_ids)  # Copy to avoid mutation
        self.changes_applied = False

        # Query objects
        self.book_queries = BookQueries(db)
        self.series_queries = SeriesQueries(db)
        self.genre_queries = GenreQueries(db)
        self.collection_queries = CollectionQueries(db)

        # Load selected books data
        self.books: List[Book] = self._load_selected_books()

        # Check if multiple collections exist
        self.collections = self.collection_queries.get_all()
        self.has_multiple_collections = len(self.collections) > 1

        # Setup UI
        self.setup_ui()
        self.apply_control_styles()
        self.load_combos()
        self.load_books_table()
        self.setup_shortcuts()
        # Must come before connect_signals to set up lineEdit refs
        self.install_event_filters()
        self.connect_signals()

        # Window settings
        count = len(self.selected_book_ids)
        title = f"Update {count} Book{'s' if count != 1 else ''}"
        self.setWindowTitle(title)
        self.setAccessibleName(title)
        self.setAccessibleDescription(
            "Bulk update Series, Genre, and Collection for selected books. "
            "Updates occur immediately when a selection is made.")
        self.resize(1200, 500)  # Wider window for larger columns
        self.setMinimumWidth(900)  # Ensure minimum width

    def _load_selected_books(self) -> List[Book]:
        """Load Book objects for all selected book IDs."""
        books = []
        for book_id in self.selected_book_ids:
            book = self.book_queries.get_by_id(book_id)
            if book:
                books.append(book)
        return books

    def setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # === Header Section: Combo boxes ===
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)

        # Series combo (Alt+S)
        series_label = QLabel("&Series:")
        self.series_combo = QComboBox()
        self.series_combo.setEditable(True)
        self.series_combo.setAccessibleName("Series")
        self.series_combo.setAccessibleDescription(
            "Select series to apply, enter new, or select None to clear - Alt+S")
        series_label.setBuddy(self.series_combo)
        header_layout.addWidget(series_label)
        header_layout.addWidget(self.series_combo, 1)

        # Genre combo (Alt+G)
        genre_label = QLabel("&Genre:")
        self.genre_combo = QComboBox()
        self.genre_combo.setEditable(True)
        self.genre_combo.setAccessibleName("Genre")
        self.genre_combo.setAccessibleDescription(
            "Select genre to apply, enter new, or select None to clear - Alt+G")
        genre_label.setBuddy(self.genre_combo)
        header_layout.addWidget(genre_label)
        header_layout.addWidget(self.genre_combo, 1)

        # Collection combo (Alt+L) - only if multiple collections exist
        self.collection_label = QLabel("Co&llection:")
        self.collection_combo = QComboBox()
        self.collection_combo.setAccessibleName("Collection")
        self.collection_combo.setAccessibleDescription(
            "Select collection to apply - Alt+L")
        self.collection_label.setBuddy(self.collection_combo)
        header_layout.addWidget(self.collection_label)
        header_layout.addWidget(self.collection_combo, 1)

        # Hide collection if only one collection exists
        if not self.has_multiple_collections:
            self.collection_label.setVisible(False)
            self.collection_combo.setVisible(False)

        layout.addLayout(header_layout)

        # === Detail Section: Book list table ===
        self.table = QTableWidget()
        self.table.setAccessibleName("Selected books list")
        self.table.setAccessibleDescription(
            "List of books being updated with Title, Year, Series, Genre, Collection")

        # Columns: Title, Year, Series, Genre, Collection
        columns = ["Title", "Year", "Series", "Genre", "Collection"]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)

        # Table settings
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)

        # Column sizing - use fixed minimum widths for Series and Collection
        header = self.table.horizontalHeader()
        header.setMinimumSectionSize(50)  # Ensure minimum size for all columns
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Title stretches
        # Year - auto-size to content
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        # Series - user can resize
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        # Genre - user can resize
        header.setSectionResizeMode(3, QHeaderView.Interactive)
        # Collection - user can resize
        header.setSectionResizeMode(4, QHeaderView.Interactive)

        # Set column widths (Interactive mode allows these to be set)
        self.table.setColumnWidth(1, 80)   # Year - wider to show 4 digits
        self.table.setColumnWidth(2, 200)  # Series
        self.table.setColumnWidth(3, 180)  # Genre
        self.table.setColumnWidth(4, 200)  # Collection

        layout.addWidget(self.table, 1)  # stretch=1 to fill space

        # === Footer Section: Status bar and Close button ===
        footer_layout = QHBoxLayout()

        # Status bar for messages
        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        footer_layout.addWidget(self.status_bar, 1)

        # Close button (Alt+C)
        self.close_button = QPushButton("&Close")
        self.close_button.setAccessibleName("Close")
        self.close_button.setAccessibleDescription(
            "Close window - Alt+C or Escape")
        self.close_button.setFocusPolicy(Qt.StrongFocus)
        self.close_button.setDefault(False)  # Don't trigger on Enter
        self.close_button.setAutoDefault(False)  # Don't auto-trigger on Enter
        self.close_button.clicked.connect(self.accept)
        footer_layout.addWidget(self.close_button)

        layout.addLayout(footer_layout)

    def install_event_filters(self):
        """Install event filters on combo boxes to block plain arrow keys and handle FocusOut."""
        self.series_combo.installEventFilter(self)
        self.genre_combo.installEventFilter(self)
        self.collection_combo.installEventFilter(self)

        # Store lineEdit references for comparison in eventFilter
        self._series_line_edit = self.series_combo.lineEdit()
        self._genre_line_edit = self.genre_combo.lineEdit()

        # For editable combos, also filter the internal lineEdit for FocusOut and Enter detection
        if self._series_line_edit:
            self._series_line_edit.installEventFilter(self)
        if self._genre_line_edit:
            self._genre_line_edit.installEventFilter(self)

    def eventFilter(self, source, event):
        """
        Event filter to:
        1. Block plain Up/Down arrow keys on combo boxes (require Alt+Down to open dropdown)
        2. Handle FocusOut to detect and apply new entries
        """
        # Handle Enter key on collection combo (not editable, no returnPressed signal)
        if event.type() == QEvent.KeyPress:
            key = event.key()
            if key in (Qt.Key_Return, Qt.Key_Enter):
                if source == self.collection_combo:
                    # Collection is the last combo, just stay put
                    return True  # Consume the event to prevent dialog close

            # Block plain Up/Down arrow keys on combo boxes
            if isinstance(source, QComboBox):
                modifiers = event.modifiers()
                if key in (Qt.Key_Up, Qt.Key_Down):
                    # Only allow with Alt modifier (opens dropdown)
                    if not (modifiers & Qt.AltModifier):
                        # Block plain arrow keys - beep to indicate blocked
                        QApplication.beep()
                        return True  # Consume the event

        # Handle FocusOut to detect new entries typed into combos
        # Check both the combo and its internal lineEdit
        if event.type() == QEvent.FocusOut:
            # Series combo or its lineEdit
            if source == self.series_combo or source == self._series_line_edit:
                self._handle_series_focus_out()
            # Genre combo or its lineEdit
            elif source == self.genre_combo or source == self._genre_line_edit:
                self._handle_genre_focus_out()

        return super().eventFilter(source, event)

    def _handle_series_focus_out(self):
        """Handle focus leaving Series combo - check for new entry."""
        text = self.series_combo.currentText().strip()
        if not text or text == "None":
            return

        # Check if it matches an existing item in the combo
        index = self.series_combo.findText(text, Qt.MatchFixedString)
        if index >= 0:
            # It's an existing item - apply it if not blank
            if index > 0:  # Not the blank item
                # Set the combo to this index so currentData() works correctly
                self.series_combo.setCurrentIndex(index)
                self.on_series_changed(index)
            return

        # It's a new value - confirm and apply
        if self._confirm_new_entry("Series", text):
            new_id = self.series_queries.get_or_create(text)
            book_ids = list(self.selected_book_ids)
            count = len(book_ids)
            self.book_queries.bulk_update_series(book_ids, new_id)
            self.changes_applied = True
            self.show_status(
                f"Series: {text} added to {count} book{'s' if count != 1 else ''}")
            self.load_combos()
            self.refresh_books_table()
        else:
            # User said No - keep text but restore focus to this combo
            QTimer.singleShot(0, lambda: self.series_combo.setFocus())

    def _handle_genre_focus_out(self):
        """Handle focus leaving Genre combo - check for new entry."""
        text = self.genre_combo.currentText().strip()
        if not text or text == "None":
            return

        # Check if it matches an existing item in the combo
        index = self.genre_combo.findText(text, Qt.MatchFixedString)
        if index >= 0:
            # It's an existing item - apply it if not blank
            if index > 0:  # Not the blank item
                # Set the combo to this index so currentData() works correctly
                self.genre_combo.setCurrentIndex(index)
                self.on_genre_changed(index)
            return

        # It's a new value - confirm and apply
        if self._confirm_new_entry("Genre", text):
            new_id = self.genre_queries.get_or_create(text)
            book_ids = list(self.selected_book_ids)
            count = len(book_ids)
            self.book_queries.bulk_update_genre(book_ids, new_id)
            self.changes_applied = True
            self.show_status(
                f"Genre: {text} added to {count} book{'s' if count != 1 else ''}")
            self.load_combos()
            self.refresh_books_table()
        else:
            # User said No - keep text but restore focus to this combo
            QTimer.singleShot(0, lambda: self.genre_combo.setFocus())

    def apply_control_styles(self):
        """Apply consistent styling to all controls."""
        # Get scale percentage and calculate scaled values
        scale_pct = self.scaler.current_scale
        base_height = 20
        scaled_height = int(base_height * (scale_pct / 100.0))
        base_font_size = int(9 * (scale_pct / 100.0))

        # Apply font to all widgets
        font = self.font()
        font.setPointSize(base_font_size)
        self.setFont(font)

        # Stylesheet for QComboBox controls
        combo_style = f"""
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
        """

        # Stylesheet for QPushButton
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
        """

        # Stylesheet for QLabel in header - bold
        label_style = """
            QLabel {
                font-weight: bold;
            }
        """

        # Apply styles
        for widget in self.findChildren(QComboBox):
            widget.setStyleSheet(combo_style)
        for widget in self.findChildren(QPushButton):
            widget.setStyleSheet(button_style)
        for widget in self.findChildren(QLabel):
            widget.setStyleSheet(label_style)

    def load_combos(self):
        """Load combo box items from database."""
        # Series - blank first, then "None" to clear, then existing series
        self.series_combo.clear()
        self.series_combo.addItem("", None)  # Blank = no action
        self.series_combo.addItem("None", NONE_MARKER)  # Clear the field
        for series in self.series_queries.get_all():
            self.series_combo.addItem(series.name, series.series_id)

        # Genre - blank first, then "None" to clear, then existing genres
        self.genre_combo.clear()
        self.genre_combo.addItem("", None)  # Blank = no action
        self.genre_combo.addItem("None", NONE_MARKER)  # Clear the field
        for genre in self.genre_queries.get_all():
            self.genre_combo.addItem(genre.name, genre.genre_id)

        # Collection - blank first, then existing collections (no "None" - books must have collection)
        self.collection_combo.clear()
        self.collection_combo.addItem("", None)  # Blank = no action
        for collection in self.collections:
            self.collection_combo.addItem(
                collection.name, collection.collection_id)

    def load_books_table(self):
        """Load selected books into the table."""
        self.table.setRowCount(len(self.books))

        for row, book in enumerate(self.books):
            # Title
            title_item = QTableWidgetItem(book.title or "")
            self.table.setItem(row, 0, title_item)

            # Year
            year_text = str(book.year) if book.year else ""
            year_item = QTableWidgetItem(year_text)
            self.table.setItem(row, 1, year_item)

            # Series
            series_item = QTableWidgetItem(book.series_name or "")
            self.table.setItem(row, 2, series_item)

            # Genre
            genre_item = QTableWidgetItem(book.genre_name or "")
            self.table.setItem(row, 3, genre_item)

            # Collection
            collection_item = QTableWidgetItem(book.collection_name or "")
            self.table.setItem(row, 4, collection_item)

    def refresh_books_table(self):
        """Refresh book data and table after an update."""
        self.books = self._load_selected_books()
        self.load_books_table()

    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Escape to close
        escape_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        escape_shortcut.activated.connect(self.accept)

        # Alt+B to focus book list
        book_list_shortcut = QShortcut(QKeySequence("Alt+B"), self)
        book_list_shortcut.activated.connect(self.focus_book_list)

        # F1 for keyboard shortcuts help
        help_shortcut = QShortcut(QKeySequence("F1"), self)
        help_shortcut.activated.connect(self.on_show_shortcuts)

    def focus_book_list(self):
        """Move focus to the book list table."""
        self.table.setFocus()
        if self.table.rowCount() > 0:
            self.table.setCurrentCell(0, 0)

    def connect_signals(self):
        """Connect combo box signals for immediate updates."""
        # Use activated signal (fires on user selection, not programmatic changes)
        self.series_combo.activated.connect(self.on_series_changed)
        self.genre_combo.activated.connect(self.on_genre_changed)
        self.collection_combo.activated.connect(self.on_collection_changed)

        # Handle Enter key in editable combos for new entries
        self._series_line_edit.returnPressed.connect(self.on_series_entered)
        self._genre_line_edit.returnPressed.connect(self.on_genre_entered)

    def show_status(self, message: str, announce: bool = True):
        """Show message in status bar and announce to screen readers."""
        self.status_bar.showMessage(message)
        # Announce to screen readers (JAWS/NVDA) using focus trick
        if announce and QAccessible.isActive():
            previous_focus = QApplication.instance().focusWidget()
            self.status_bar.setFocusPolicy(Qt.StrongFocus)
            self.status_bar.setFocus()

            def restore_focus():
                if previous_focus:
                    previous_focus.setFocus()
                self.status_bar.setFocusPolicy(Qt.NoFocus)
            QTimer.singleShot(100, restore_focus)

    def keyPressEvent(self, event):
        """Override to prevent Enter from closing the dialog."""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            # Don't close dialog on Enter - let combos handle it
            event.ignore()
            return
        super().keyPressEvent(event)

    def _confirm_new_entry(self, field_name: str, value: str) -> bool:
        """
        Ask user to confirm creating a new entry.
        Returns True if confirmed, False if cancelled.
        """
        msg = f"'{value}' is a new {field_name}.\n\nCreate this new {field_name}?"
        reply = QMessageBox.question(
            self, f"New {field_name}", msg,
            QMessageBox.Yes | QMessageBox.No
        )
        return reply == QMessageBox.Yes

    def on_series_changed(self, index: int):
        """Handle series combo selection change - update immediately."""
        if index == 0:  # Blank selected - no action
            return

        data = self.series_combo.currentData()
        book_ids = list(self.selected_book_ids)
        count = len(book_ids)

        series_name = self.series_combo.currentText()
        if data == NONE_MARKER or series_name == "None":
            # Clear series from all selected books
            self.book_queries.bulk_update_series(book_ids, None)
            self.changes_applied = True
            self.show_status(
                f"Series cleared from {count} book{'s' if count != 1 else ''}")
        elif data is not None:
            # Apply selected series
            self.book_queries.bulk_update_series(book_ids, data)
            self.changes_applied = True
            self.show_status(
                f"Series: {series_name} added to {count} book{'s' if count != 1 else ''}")

        # Reset combo to blank and refresh table
        self.series_combo.setCurrentIndex(0)
        self.refresh_books_table()

    def on_series_entered(self):
        """Handle Enter key in series combo for new series."""
        text = self.series_combo.currentText().strip()
        if not text or text == "None":  # Blank or None item
            return

        # Check if it's an existing series
        existing = self.series_queries.get_by_name(text)
        if existing:
            # Existing series - just apply it
            book_ids = list(self.selected_book_ids)
            count = len(book_ids)
            self.book_queries.bulk_update_series(book_ids, existing.series_id)
            self.changes_applied = True
            self.show_status(
                f"Series: {text} added to {count} book{'s' if count != 1 else ''}")
            self.series_combo.setCurrentIndex(0)
            self.load_combos()
            self.refresh_books_table()
            return

        # New series - confirm with user
        if not self._confirm_new_entry("Series", text):
            self.series_combo.setCurrentIndex(0)
            return

        # Create new series and apply
        new_id = self.series_queries.get_or_create(text)
        book_ids = list(self.selected_book_ids)
        count = len(book_ids)
        self.book_queries.bulk_update_series(book_ids, new_id)
        self.changes_applied = True
        self.show_status(
            f"Series: {text} added to {count} book{'s' if count != 1 else ''}")

        # Reload combos to include new series, reset, and refresh table
        self.load_combos()
        self.refresh_books_table()

    def on_genre_changed(self, index: int):
        """Handle genre combo selection change - update immediately."""
        if index == 0:  # Blank selected - no action
            return

        data = self.genre_combo.currentData()
        book_ids = list(self.selected_book_ids)
        count = len(book_ids)

        genre_name = self.genre_combo.currentText()
        if data == NONE_MARKER or genre_name == "None":
            # Clear genre from all selected books
            self.book_queries.bulk_update_genre(book_ids, None)
            self.changes_applied = True
            self.show_status(
                f"Genre cleared from {count} book{'s' if count != 1 else ''}")
        elif data is not None:
            # Apply selected genre
            self.book_queries.bulk_update_genre(book_ids, data)
            self.changes_applied = True
            self.show_status(
                f"Genre: {genre_name} added to {count} book{'s' if count != 1 else ''}")

        # Reset combo to blank and refresh table
        self.genre_combo.setCurrentIndex(0)
        self.refresh_books_table()

    def on_genre_entered(self):
        """Handle Enter key in genre combo for new genre."""
        text = self.genre_combo.currentText().strip()
        if not text or text == "None":  # Blank or None item
            return

        # Check if it's an existing genre
        existing = self.genre_queries.get_by_name(text)
        if existing:
            # Existing genre - just apply it
            book_ids = list(self.selected_book_ids)
            count = len(book_ids)
            self.book_queries.bulk_update_genre(book_ids, existing.genre_id)
            self.changes_applied = True
            self.show_status(
                f"Genre: {text} added to {count} book{'s' if count != 1 else ''}")
            self.genre_combo.setCurrentIndex(0)
            self.load_combos()
            self.refresh_books_table()
            return

        # New genre - confirm with user
        if not self._confirm_new_entry("Genre", text):
            self.genre_combo.setCurrentIndex(0)
            return

        # Create new genre and apply
        new_id = self.genre_queries.get_or_create(text)
        book_ids = list(self.selected_book_ids)
        count = len(book_ids)
        self.book_queries.bulk_update_genre(book_ids, new_id)
        self.changes_applied = True
        self.show_status(
            f"Genre: {text} added to {count} book{'s' if count != 1 else ''}")

        # Reload combos to include new genre, reset, and refresh table
        self.load_combos()
        self.refresh_books_table()

    def on_collection_changed(self, index: int):
        """Handle collection combo selection change - update immediately."""
        if index == 0:  # Blank selected - no action
            return

        data = self.collection_combo.currentData()
        if data is None:
            return

        # Apply selected collection
        collection_name = self.collection_combo.currentText()
        book_ids = list(self.selected_book_ids)
        count = len(book_ids)
        self.book_queries.bulk_update_collection(book_ids, data)
        self.changes_applied = True
        self.show_status(
            f"Collection: {collection_name} set for {count} book{'s' if count != 1 else ''}")

        # Reset combo to blank and refresh table
        self.collection_combo.setCurrentIndex(0)
        self.refresh_books_table()

    def on_show_shortcuts(self):
        """Show keyboard shortcuts help dialog."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Keyboard Shortcuts - Update Window")
        dlg.setAccessibleName("Keyboard Shortcuts")
        dlg.resize(450, 400)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Shortcuts list - description on left, key on right
        shortcuts = [
            ("Alt+S", "Series"),
            ("Alt+G", "Genre"),
            ("Alt+L", "Collection"),
            ("Alt+Down", "Open combo dropdown"),
            ("Alt+B", "Book list"),
            ("Alt+C", "Close window"),
            ("Escape", "Close window"),
            ("F1", "Show keyboard shortcuts"),
        ]

        # Create table
        table = QTableWidget()
        table.setAccessibleName("Shortcuts list")
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

        # Populate table - description on left, key on right
        for row, (key, description) in enumerate(shortcuts):
            combined_text = f"{description} - {key}"
            item = QTableWidgetItem(combined_text)
            item.setData(Qt.AccessibleTextRole, f"{description}: {key}")
            table.setItem(row, 0, item)

        # Resize column to stretch
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)

        # Set font size
        scale_pct = self.scaler.current_scale
        base_font_size = int(11 * (scale_pct / 100.0))
        font = table.font()
        font.setPointSize(base_font_size)
        table.setFont(font)

        layout.addWidget(table)

        close_btn = QPushButton("Close")
        close_btn.setAccessibleName("Close")
        close_btn.clicked.connect(dlg.accept)
        btn_font = close_btn.font()
        btn_font.setPointSize(base_font_size)
        close_btn.setFont(btn_font)
        layout.addWidget(close_btn)

        dlg.setTabOrder(table, close_btn)

        dlg.exec()
