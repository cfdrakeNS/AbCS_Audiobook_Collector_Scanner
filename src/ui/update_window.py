from src.accessibility.style_helpers import exec_styled_message_box
from src.accessibility.scaling import UIScaler
from src.accessibility.accessible_events import announce_status_message
from src.database import (
    DatabaseManager,
    Book,
    BookQueries,
    SeriesQueries,
    GenreQueries,
    CollectionQueries,
)
import time
from typing import Set, List
from PySide6.QtGui import QShortcut, QKeySequence, QAccessible
from PySide6.QtCore import Qt, QEvent, QTimer, QSettings
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QPushButton,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QStatusBar,
    QMessageBox,
    QApplication,
)
import re

"""
Update Window - Bulk update for selected books.
Allows mass updating or removing of Series, Genre, and Collection for selected books.
Updates occur immediately when a selection is made.
"""


# Special marker for "None" option to clear a field
NONE_MARKER = "__NONE__"


class UpdateWindow(QDialog):
    """
    Update dialog for bulk updating Series, Genre, and Collection.
    Updates occur immediately when a combo selection is made.
    Select "None" to clear/remove a field value from selected books.
    """

    def __init__(
        self, db: DatabaseManager, scaler: UIScaler, selected_book_ids: set, parent=None
    ):
        super().__init__(parent)
        from src.accessibility.icon_helper import get_app_icon

        self.setWindowIcon(get_app_icon())

    @staticmethod
    def _to_proper_case(text: str) -> str:
        value = text.strip().lower()
        if not value:
            return ""
        return re.sub(
            r"(^|[\s\-'])([a-z])",
            lambda match: f"{match.group(1)}{match.group(2).upper()}",
            value,
        )

    @staticmethod
    def _is_proper_case_enabled() -> bool:
        settings = QSettings("AbCS", "AbCS")
        return settings.value("import/autocorrect/proper_case", False, type=bool)

    @classmethod
    def _normalize_name_field(cls, text: str) -> str:
        value = text.strip()
        if not value:
            return ""
        if cls._is_proper_case_enabled():
            return cls._to_proper_case(value)
        return value

    def __init__(
        self,
        db: DatabaseManager,
        scaler: UIScaler,
        selected_book_ids: Set[int],
        parent=None,
    ):
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
        self.selected_book_ids = set(selected_book_ids)  # Copy to avoid mutation
        self.changes_applied = False
        self._default_status_message = "Ready"
        self._last_series_action_at = 0.0
        self._last_genre_action_at = 0.0
        self._last_series_action_text = ""
        self._last_genre_action_text = ""
        self._processing_series_input = False
        self._processing_genre_input = False
        self._skip_series_focus_out_once = False
        self._skip_genre_focus_out_once = False

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
            "Updates occur immediately when a selection is made."
        )
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
        self.series_combo.setSizeAdjustPolicy(
            QComboBox.AdjustToMinimumContentsLengthWithIcon
        )
        self.series_combo.setMinimumContentsLength(20)
        self.series_combo.setAccessibleName("Series")
        self.series_combo.setAccessibleDescription(
            "Select series to apply, enter new, or select None to clear - Alt+S"
        )
        series_label.setBuddy(self.series_combo)
        header_layout.addWidget(series_label)
        header_layout.addWidget(self.series_combo, 1)

        # Genre combo (Alt+G)
        genre_label = QLabel("&Genre:")
        self.genre_combo = QComboBox()
        self.genre_combo.setEditable(True)
        self.genre_combo.setSizeAdjustPolicy(
            QComboBox.AdjustToMinimumContentsLengthWithIcon
        )
        self.genre_combo.setMinimumContentsLength(20)
        self.genre_combo.setAccessibleName("Genre")
        self.genre_combo.setAccessibleDescription(
            "Select genre to apply, enter new, or select None to clear - Alt+G"
        )
        genre_label.setBuddy(self.genre_combo)
        header_layout.addWidget(genre_label)
        header_layout.addWidget(self.genre_combo, 1)

        # Collection combo (Alt+C) - only if multiple collections exist
        self.collection_label = QLabel("&Collection:")
        self.collection_combo = QComboBox()
        self.collection_combo.setAccessibleName("Collection")
        self.collection_combo.setAccessibleDescription(
            "Select collection to apply - Alt+C"
        )
        self.collection_label.setBuddy(self.collection_combo)
        header_layout.addWidget(self.collection_label)
        header_layout.addWidget(self.collection_combo, 1)

        # Hide collection if only one collection exists
        if not self.has_multiple_collections:
            self.collection_label.setVisible(False)
            self.collection_combo.setVisible(False)

        self._apply_header_combo_widths()

        layout.addLayout(header_layout)

        # === Detail Section: Book list table ===
        self.table = QTableWidget()
        self.table.setAccessibleName("Selected books list")
        self.table.setAccessibleDescription(
            "List of books being updated with Title, Year, Series, Genre, Collection"
        )

        # Columns: Title, Year, Series, Genre, Collection
        columns = ["Title", "Year", "Series", "Genre", "Collection"]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)

        # Table settings
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(False)
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
        self.table.setColumnWidth(1, 80)  # Year - wider to show 4 digits
        self.table.setColumnWidth(2, 200)  # Series
        self.table.setColumnWidth(3, 180)  # Genre
        self.table.setColumnWidth(4, 200)  # Collection

        layout.addWidget(self.table, 1)  # stretch=1 to fill space

        # === Footer Section: Status bar ===
        footer_layout = QHBoxLayout()

        # Status bar for messages
        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        footer_layout.addWidget(self.status_bar, 1)

        layout.addLayout(footer_layout)

        # Explicit tab order to keep header navigation predictable
        self.setTabOrder(self.series_combo, self.genre_combo)
        if self.has_multiple_collections:
            self.setTabOrder(self.genre_combo, self.collection_combo)
            self.setTabOrder(self.collection_combo, self.table)
        else:
            self.setTabOrder(self.genre_combo, self.table)
        self.table.setFocusPolicy(Qt.StrongFocus)

    def install_event_filters(self):
        """Install event filters on combo boxes to block plain arrow keys and handle FocusOut."""
        self.series_combo.installEventFilter(self)
        self.genre_combo.installEventFilter(self)
        self.collection_combo.installEventFilter(self)

        # Store lineEdit references for comparison in eventFilter
        self._series_line_edit = self.series_combo.lineEdit()
        self._genre_line_edit = self.genre_combo.lineEdit()

        # For editable combos, also filter the internal lineEdit for key and focus handling
        if self._series_line_edit:
            self._series_line_edit.installEventFilter(self)
        if self._genre_line_edit:
            self._genre_line_edit.installEventFilter(self)

    def eventFilter(self, source, event):
        """
        Event filter to:
        1. Block plain Up/Down arrow keys on combo boxes (require Alt+Down to open dropdown)
        2. Handle Enter on header combos to apply updates and move focus forward
        3. Handle FocusOut to detect and apply typed Series/Genre entries
        """
        if event.type() == QEvent.KeyPress:
            key = event.key()

            # Prevent unused Alt+letter combinations from being echoed into editable combos
            if source in (
                self.series_combo,
                self._series_line_edit,
                self.genre_combo,
                self._genre_line_edit,
            ):
                modifiers = event.modifiers()
                if modifiers & Qt.AltModifier:
                    allowed_alt_keys = {
                        Qt.Key_S,
                        Qt.Key_G,
                        Qt.Key_L,
                        Qt.Key_Slash,
                        Qt.Key_Question,
                        Qt.Key_Up,
                        Qt.Key_Down,
                    }
                    # Block Alt+/ from typing through
                    if key == Qt.Key_Slash:
                        return True
                    if Qt.Key_A <= key <= Qt.Key_Z and key not in allowed_alt_keys:
                        return True

            if key in (Qt.Key_Return, Qt.Key_Enter):
                if source == self.series_combo or source == self._series_line_edit:
                    self._skip_series_focus_out_once = True
                    should_move = self.on_series_entered()
                    if should_move:
                        QTimer.singleShot(
                            0, lambda s=source: self._focus_next_header_control(s)
                        )
                    else:
                        QTimer.singleShot(0, lambda: self.series_combo.setFocus())
                    return True

                if source == self.genre_combo or source == self._genre_line_edit:
                    self._skip_genre_focus_out_once = True
                    should_move = self.on_genre_entered()
                    if should_move:
                        QTimer.singleShot(
                            0, lambda s=source: self._focus_next_header_control(s)
                        )
                    else:
                        QTimer.singleShot(0, lambda: self.genre_combo.setFocus())
                    return True

                if source == self.collection_combo:
                    self.on_collection_changed(self.collection_combo.currentIndex())
                    QTimer.singleShot(
                        0, lambda s=source: self._focus_next_header_control(s)
                    )
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

        # Handle FocusOut to detect/apply values typed into editable combos
        if event.type() == QEvent.FocusOut:
            # Handle both combo and lineEdit; processing code dedupes safely
            if source == self.series_combo or source == self._series_line_edit:
                if self._skip_series_focus_out_once:
                    self._skip_series_focus_out_once = False
                    return super().eventFilter(source, event)
                self._handle_series_focus_out()
            elif source == self.genre_combo or source == self._genre_line_edit:
                if self._skip_genre_focus_out_once:
                    self._skip_genre_focus_out_once = False
                    return super().eventFilter(source, event)
                self._handle_genre_focus_out()

        return super().eventFilter(source, event)

    def _focus_next_header_control(self, source):
        """Move focus to next logical control from header fields."""
        if source == self.series_combo or source == self._series_line_edit:
            self.genre_combo.setFocus()
            return

        if source == self.genre_combo or source == self._genre_line_edit:
            if self.has_multiple_collections and self.collection_combo.isVisible():
                self.collection_combo.setFocus()
            else:
                self.table.setFocus()
            return

        if source == self.collection_combo:
            self.table.setFocus()

    def _find_existing_combo_data(self, combo: QComboBox, text: str):
        """Find existing item data by case-insensitive text match (excluding blank/None)."""
        lookup = text.strip().casefold()
        if not lookup:
            return None

        for index in range(combo.count()):
            item_text = combo.itemText(index).strip().casefold()
            if item_text != lookup:
                continue

            data = combo.itemData(index)
            if data is None or data == NONE_MARKER:
                return None
            return data

        return None

    def _handle_series_focus_out(self):
        """Handle focus leaving Series combo - check for new entry."""
        self._process_series_input(keep_focus=False)

    def _handle_genre_focus_out(self):
        """Handle focus leaving Genre combo - check for new entry."""
        self._process_genre_input(keep_focus=False)

    def _is_recent_series_action(self, text: str) -> bool:
        return (
            self._last_series_action_text == text.casefold()
            and (time.monotonic() - self._last_series_action_at) < 0.5
        )

    def _is_recent_genre_action(self, text: str) -> bool:
        return (
            self._last_genre_action_text == text.casefold()
            and (time.monotonic() - self._last_genre_action_at) < 0.5
        )

    def _mark_series_action(self, text: str):
        self._last_series_action_text = text.casefold()
        self._last_series_action_at = time.monotonic()

    def _mark_genre_action(self, text: str):
        self._last_genre_action_text = text.casefold()
        self._last_genre_action_at = time.monotonic()

    def _process_series_input(self, keep_focus: bool) -> bool:
        if self._processing_series_input:
            return False

        self._processing_series_input = True
        try:
            text = self._normalize_name_field(self.series_combo.currentText())
            normalized_text = text.casefold()
            if not text:
                if keep_focus:
                    QTimer.singleShot(0, lambda: self.series_combo.setFocus())
                return True

            if normalized_text == "none":
                book_ids = list(self.selected_book_ids)
                count = len(book_ids)
                self.book_queries.bulk_update_series(book_ids, None)
                self._mark_series_action(text)
                self.changes_applied = True
                self.show_status(
                    f"Series cleared from {count} book{'s' if count != 1 else ''}"
                )
                self.series_combo.setCurrentIndex(0)
                self.refresh_books_table()
                if keep_focus:
                    QTimer.singleShot(0, lambda: self.series_combo.setFocus())
                return True

            if self._is_recent_series_action(text):
                if keep_focus:
                    QTimer.singleShot(0, lambda: self.series_combo.setFocus())
                return True

            existing_data = self._find_existing_combo_data(self.series_combo, text)
            existing = (
                self.series_queries.get_by_name(text) if existing_data is None else None
            )
            existing_series_id = (
                existing_data
                if existing_data is not None
                else (existing.series_id if existing else None)
            )

            if existing_series_id is not None:
                book_ids = list(self.selected_book_ids)
                count = len(book_ids)
                self.book_queries.bulk_update_series(book_ids, existing_series_id)
                self._mark_series_action(text)
                self.changes_applied = True
                self.show_status(
                    f"Series: {text} added to {count} book{'s' if count != 1 else ''}"
                )
                self.series_combo.setCurrentIndex(0)
                self.load_combos()
                self.refresh_books_table()
                if keep_focus:
                    QTimer.singleShot(0, lambda: self.series_combo.setFocus())
                return True

            if not self._confirm_new_entry("Series", text):
                self._mark_series_action(text)
                QTimer.singleShot(0, lambda: self.series_combo.setFocus())
                return False

            new_id = self.series_queries.get_or_create(text)
            book_ids = list(self.selected_book_ids)
            count = len(book_ids)
            self.book_queries.bulk_update_series(book_ids, new_id)
            self._mark_series_action(text)
            self.changes_applied = True
            self.show_status(
                f"Series: {text} added to {count} book{'s' if count != 1 else ''}"
            )
            self.load_combos()
            self.refresh_books_table()
            if keep_focus:
                QTimer.singleShot(0, lambda: self.series_combo.setFocus())
            return True
        finally:
            self._processing_series_input = False

    def _process_genre_input(self, keep_focus: bool) -> bool:
        if self._processing_genre_input:
            return False

        self._processing_genre_input = True
        try:
            text = self._normalize_name_field(self.genre_combo.currentText())
            normalized_text = text.casefold()
            if not text:
                if keep_focus:
                    QTimer.singleShot(0, lambda: self.genre_combo.setFocus())
                return True

            if normalized_text == "none":
                book_ids = list(self.selected_book_ids)
                count = len(book_ids)
                self.book_queries.bulk_update_genre(book_ids, None)
                self._mark_genre_action(text)
                self.changes_applied = True
                self.show_status(
                    f"Genre cleared from {count} book{'s' if count != 1 else ''}"
                )
                self.genre_combo.setCurrentIndex(0)
                self.refresh_books_table()
                if keep_focus:
                    QTimer.singleShot(0, lambda: self.genre_combo.setFocus())
                return True

            if self._is_recent_genre_action(text):
                if keep_focus:
                    QTimer.singleShot(0, lambda: self.genre_combo.setFocus())
                return True

            existing_data = self._find_existing_combo_data(self.genre_combo, text)
            existing = (
                self.genre_queries.get_by_name(text) if existing_data is None else None
            )
            existing_genre_id = (
                existing_data
                if existing_data is not None
                else (existing.genre_id if existing else None)
            )

            if existing_genre_id is not None:
                book_ids = list(self.selected_book_ids)
                count = len(book_ids)
                self.book_queries.bulk_update_genre(book_ids, existing_genre_id)
                self._mark_genre_action(text)
                self.changes_applied = True
                self.show_status(
                    f"Genre: {text} added to {count} book{'s' if count != 1 else ''}"
                )
                self.genre_combo.setCurrentIndex(0)
                self.load_combos()
                self.refresh_books_table()
                if keep_focus:
                    QTimer.singleShot(0, lambda: self.genre_combo.setFocus())
                return True

            if not self._confirm_new_entry("Genre", text):
                self._mark_genre_action(text)
                QTimer.singleShot(0, lambda: self.genre_combo.setFocus())
                return False

            new_id = self.genre_queries.get_or_create(text)
            book_ids = list(self.selected_book_ids)
            count = len(book_ids)
            self.book_queries.bulk_update_genre(book_ids, new_id)
            self._mark_genre_action(text)
            self.changes_applied = True
            self.show_status(
                f"Genre: {text} added to {count} book{'s' if count != 1 else ''}"
            )
            self.load_combos()
            self.refresh_books_table()
            if keep_focus:
                QTimer.singleShot(0, lambda: self.genre_combo.setFocus())
            return True
        finally:
            self._processing_genre_input = False

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

        table_style = """
            QTableWidget:focus {
                border: none;
                outline: none;
            }
            QTableWidget::item:focus {
                border: none;
                outline: none;
            }
        """

        # Apply styles
        # Combo boxes use theme manager styling - don't override
        for widget in self.findChildren(QPushButton):
            widget.setStyleSheet(button_style)
        for widget in self.findChildren(QLabel):
            widget.setStyleSheet(label_style)
        self.table.setStyleSheet(table_style)
        self._apply_header_combo_widths()

    def _apply_header_combo_widths(self):
        """Keep Series and Genre combos visually aligned with same width."""
        min_width = max(self.scaler.get_scaled_size(220), 180)
        self.series_combo.setMinimumWidth(min_width)
        self.genre_combo.setMinimumWidth(min_width)

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
            self.collection_combo.addItem(collection.name, collection.collection_id)

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
        from src.accessibility.shortcuts import get_shortcut_manager, ShortcutContext

        mgr = get_shortcut_manager()
        callback_map = {
            "series_combo": self.series_combo.setFocus,
            "genre_combo": self.genre_combo.setFocus,
            "collection_combo": self.collection_combo.setFocus,
            "book_list": self.focus_book_list,
        }
        mgr.register_alt_shortcuts(self, ShortcutContext.UPDATE_WINDOW, callback_map)

        # Escape to close
        escape_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        escape_shortcut.activated.connect(self.accept)

        # F1 for keyboard shortcuts help
        help_shortcut = QShortcut(QKeySequence("F1"), self)
        help_shortcut.activated.connect(self.on_show_shortcuts)

        # Alt+/ reads status bar message (local only)
        alt_slash_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        alt_slash_shortcut.activated.connect(self.on_read_status_bar)

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

        # Handle Enter key in editable combos for typed entries
        if self._series_line_edit:
            self._series_line_edit.returnPressed.connect(self.on_series_entered)
        if self._genre_line_edit:
            self._genre_line_edit.returnPressed.connect(self.on_genre_entered)

    def show_status(self, message: str, announce: bool = True):
        """Show message in status bar and announce to screen readers."""
        self._default_status_message = message
        announce_status_message(self.status_bar, message, move_focus=announce)

    def on_read_status_bar(self):
        """Read current status bar message (Alt+/)."""
        status_text = self.status_bar.currentMessage() or self._default_status_message
        if QAccessible.isActive():
            self.show_status(status_text, announce=True)
        # else: do nothing (no popup)

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
        from src.accessibility.icon_helper import get_app_icon

        reply = exec_styled_message_box(
            self,
            self.scaler.get_scaled_size(20),
            icon=QMessageBox.Question,
            title=f"New {field_name}",
            text=msg,
            buttons=QMessageBox.Yes | QMessageBox.No,
            default_button=QMessageBox.No,
            window_icon=get_app_icon(),
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
                f"Series cleared from {count} book{'s' if count != 1 else ''}"
            )
        elif data is not None:
            # Apply selected series
            self.book_queries.bulk_update_series(book_ids, data)
            self.changes_applied = True
            self.show_status(
                f"Series: {series_name} added to {count} book{'s' if count != 1 else ''}"
            )

        # Reset combo to blank and refresh table
        self.series_combo.setCurrentIndex(0)
        self.refresh_books_table()
        QTimer.singleShot(0, lambda: self.series_combo.setFocus())

    def on_series_entered(self) -> bool:
        """Handle Enter key in series combo for new series."""
        return self._process_series_input(keep_focus=False)

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
                f"Genre cleared from {count} book{'s' if count != 1 else ''}"
            )
        elif data is not None:
            # Apply selected genre
            self.book_queries.bulk_update_genre(book_ids, data)
            self.changes_applied = True
            self.show_status(
                f"Genre: {genre_name} added to {count} book{'s' if count != 1 else ''}"
            )

        # Reset combo to blank and refresh table
        self.genre_combo.setCurrentIndex(0)
        self.refresh_books_table()
        QTimer.singleShot(0, lambda: self.genre_combo.setFocus())

    def on_genre_entered(self) -> bool:
        """Handle Enter key in genre combo for new genre."""
        return self._process_genre_input(keep_focus=False)

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
            f"Collection: {collection_name} set for {count} book{'s' if count != 1 else ''}"
        )

        # Reset combo to blank and refresh table
        self.collection_combo.setCurrentIndex(0)
        self.refresh_books_table()
        QTimer.singleShot(0, lambda: self.collection_combo.setFocus())

    def on_show_shortcuts(self):
        """Show keyboard shortcuts help dialog (accessible, centralized)."""
        from src.accessibility.shortcut_helpers import (
            get_accessible_shortcuts_list,
            build_accessible_f1_popup_style,
        )

        shortcuts = [
            ("Alt+S", "Series"),
            ("Alt+G", "Genre"),
            ("Alt+C", "Collection"),
            ("Alt+Down", "Open combo dropdown"),
            ("Alt+L", "Book list"),
            ("Escape", "Close window"),
            ("Alt+/", "Read status bar"),
            ("F1", "Show keyboard shortcuts"),
        ]
        filtered_shortcuts = get_accessible_shortcuts_list(shortcuts)

        dlg = QDialog(self)
        dlg.setWindowTitle("Keyboard Shortcuts - Update Window")
        dlg.setAccessibleName("Keyboard Shortcuts")
        dlg.resize(450, 400)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        table = QTableWidget()
        table.setAccessibleName("Shortcuts list")
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels([""])
        table.setRowCount(len(filtered_shortcuts))
        table.setVerticalHeaderLabels([""] * len(filtered_shortcuts))
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setTabKeyNavigation(False)
        table.setAlternatingRowColors(False)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        table.setShowGrid(False)

        # Disable hover highlighting for low-vision comfort
        table.setMouseTracking(False)
        table.viewport().setMouseTracking(False)
        table.setAttribute(Qt.WA_Hover, False)
        table.viewport().setAttribute(Qt.WA_Hover, False)

        table.setStyleSheet(build_accessible_f1_popup_style())

        # Populate table - description on left, key on right
        for row, (key, description) in enumerate(filtered_shortcuts):
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

        dlg.exec()
