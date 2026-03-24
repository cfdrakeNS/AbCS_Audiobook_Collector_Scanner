"""
Book Details Window
Form for viewing and editing individual book information.
"""

import re
from src.database import DatabaseManager, Book, BookQueries, AuthorQueries, SeriesQueries, GenreQueries, CollectionQueries
from src.accessibility.theme_manager import ThemeManager
from src.accessibility.scaling import UIScaler
from src.accessibility.shortcuts import ShortcutManager, ShortcutContext
from src.accessibility.style_helpers import build_accessible_message_box_style, exec_styled_message_box
from src.accessibility.accessible_events import announce_status_message, announce_form_field, announce_dialog_opened, announce_dialog_closed
import getpass

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QTextEdit, QPushButton,
    QLabel, QDateEdit, QSpinBox, QMessageBox, QWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QApplication, QStatusBar
)
from PySide6.QtCore import Qt, QDate, QEvent, QTimer, QSettings
from PySide6.QtGui import QAccessible, QTextCursor, QShortcut, QKeySequence
from datetime import datetime

from src.database import DatabaseManager, Book, BookQueries, AuthorQueries, SeriesQueries, GenreQueries, CollectionQueries
from src.accessibility.scaling import UIScaler
from src.accessibility.style_helpers import build_accessible_message_box_style, exec_styled_message_box
from src.accessibility.accessible_events import announce_status_message, announce_form_field, announce_dialog_opened, announce_dialog_closed


class BookDetailsWindow(QDialog):

    def set_status(self, message: str, announce: bool = False):
        """Set status bar message with optional screen reader announcement."""
        self._default_status_message = message
        announce_status_message(self.status_bar, message, move_focus=announce)

    def on_read_status_bar(self):
        """Read current status bar message (Alt+/)."""
        status_text = self.status_bar.currentMessage() or self._default_status_message
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

    def on_cancel_edit(self):
        """
        Handle Cancel (Alt+L) action: revert changes and close dialog if new, or revert edits if editing.
        """
        if self.is_new:
            # For new book, just close the dialog
            self._clear_dirty()
            self.set_status("New book entry cancelled.", announce=True)
            announce_dialog_closed(self)
            self.reject()  # Close dialog
        else:
            # For existing book, revert changes but keep dialog open
            self._revert_changes()
            self.set_status("Edits cancelled. Reverted to saved data.", announce=True)
            # Do not close dialog, just reset fields

    @staticmethod
    def _to_proper_case(text: str) -> str:
        value = text.strip().lower()
        if not value:
            return ""
        # Capitalize after space, hyphen, or apostrophe

        def capitalize_match(match):
            return match.group(1) + match.group(2).upper()
        # First, capitalize after space, hyphen, or apostrophe
        value = re.sub(r"(^|[\s\-'])([a-z])", capitalize_match, value)
        # Then, capitalize after apostrophe (for O'Connor)
        value = re.sub(
            r"(\bO')([a-z])", lambda m: m.group(1) + m.group(2).upper(), value)
        return value

    @staticmethod
    def _is_proper_case_enabled() -> bool:
        settings = QSettings("AbCS", "AudioBookCollector")
        if settings.contains("import/autocorrect/proper_case"):
            return settings.value("import/autocorrect/proper_case", False, type=bool)
        legacy_settings = QSettings("AbCS", "AbCS")
        return legacy_settings.value("import/autocorrect/proper_case", False, type=bool)

    @classmethod
    def _normalize_name_field(cls, text: str) -> str:
        value = text.strip()
        if not value:
            return ""
        if cls._is_proper_case_enabled():
            return cls._to_proper_case(value)
        return value

    def __init__(self, db: DatabaseManager, scaler: UIScaler, book: Book = None,
                 sort_order: str = "Title", books_list: list = None,
                 current_index: int = 0, theme_manager: ThemeManager = None, parent=None):
        """
        Initialize book details window.

        Args:
            db: Database manager
            scaler: UI scaler
            book: Book to edit (None for new book)
            sort_order: Current sort order from main window (for header display)
            books_list: List of Book objects for Prev/Next navigation
            current_index: Index of current book in books_list
            theme_manager: Theme manager for styling
            parent: Parent widget
        """
        super().__init__(parent)
        self.setAttribute(Qt.WA_NativeWindow, True)
        self.setWindowModality(Qt.ApplicationModal)
        self.winId()

        self.db = db
        self.scaler = scaler
        self.theme_manager = theme_manager or ThemeManager(scaler)  # Store theme manager
        self.book = book or Book()
        self.is_new = (book is None)
        self.sort_order = sort_order  # bd#8: Store for header display
        self._dirty = False  # bd#6: Track if form has unsaved changes
        self._first_dirty_widget = None  # Track first field that changed
        self._pending_dirty_widgets = set()
        self._default_status_message = "Ready"

        # Track original combo values for focusOut change detection
        self._original_author = ""
        self._original_series = ""
        self._original_genre = ""

        # bd#4: Store book list for Prev/Next navigation
        self.books_list = books_list or []
        self.current_index = current_index

        # Query objects
        self.book_queries = BookQueries(db)
        self.author_queries = AuthorQueries(db)
        self.series_queries = SeriesQueries(db)
        self.genre_queries = GenreQueries(db)
        self.collection_queries = CollectionQueries(db)
        # Accessibility: Shortcut manager
        self.shortcut_manager = ShortcutManager()

        # Setup UI
        self.setup_ui()
        self.apply_control_styles()  # bd#1: Uniform control heights
        self.disable_hover_highlight()
        self.install_focus_filters()  # bd#2: Prevent text auto-select on focus
        self.load_combos()

        if not self.is_new:
            self.load_book_data()
        else:
            self._reset_new_fields()

        # bd#6: Setup dirty tracking and initial save button visibility
        self._setup_dirty_tracking()
        self._update_save_button_visibility()

        # Window settings
        title = "New Book" if self.is_new else "Book Details"
        self.setWindowTitle(title)
        self.setAccessibleName(title)
        self.setAccessibleDescription(
            "Form for viewing and editing book information")
        self.resize(850, 500)
        announce_dialog_opened(self, title)
        self._show_idle_status(announce=False)
        QTimer.singleShot(0, self.title_edit.setFocus)

    def showEvent(self, event):
        """Ensure this dialog remains the active foreground window."""
        super().showEvent(event)
        QTimer.singleShot(0, self._ensure_foreground_window)

    def _ensure_foreground_window(self):
        """Raise and activate the dialog for reliable screen-reader title reading."""
        self.raise_()
        self.activateWindow()
        current_focus = self.focusWidget()
        if current_focus is None:
            self.title_edit.setFocus(Qt.TabFocusReason)

    def install_focus_filters(self):
        """
        bd#2: Install event filters on editable fields to prevent auto-select on focus.

        When a QLineEdit or editable QComboBox gains focus via Tab or Alt+key,
        Qt automatically selects all text. This is dangerous for blind/low-vision
        users because any keystroke would replace the content.

        We intercept FocusIn events and deselect text after Qt finishes its
        default focus handling.
        """
        # Find ALL QLineEdit widgets in the dialog (including those inside combos/spinboxes)
        for widget in self.findChildren(QLineEdit):
            widget.installEventFilter(self)

        # Also filter QTextEdit widgets
        for widget in self.findChildren(QTextEdit):
            widget.installEventFilter(self)

        # Filter QComboBox and QSpinBox - they select text AFTER their internal lineEdit gets focus
        for widget in self.findChildren(QComboBox):
            widget.installEventFilter(self)
        for widget in self.findChildren(QSpinBox):
            widget.installEventFilter(self)

    def eventFilter(self, source, event):
        """
        Event filter to handle focus events on form fields.

        bd#2: When a field gains focus, we deselect text so the user doesn't
        accidentally overwrite existing content by pressing a key.
        """
        if event.type() == QEvent.KeyPress:
            key = event.key()
            modifiers = event.modifiers()
            # Alt+ key tracking removed - was interfering with screen reader operation
        if event.type() == QEvent.FocusIn:
            # Schedule deselection AFTER Qt finishes its default focus handling
            # QTimer.singleShot(0, ...) runs on the next event loop iteration
            # Use default argument (w=source) to capture the widget value NOW,
            # not when the lambda executes later
            if isinstance(source, QLineEdit):
                QTimer.singleShot(0, lambda w=source: w.deselect())
            elif isinstance(source, QTextEdit):
                # QTextEdit uses QTextCursor.End to move cursor and clear selection
                QTimer.singleShot(
                    0, lambda w=source: w.moveCursor(QTextCursor.End))
            elif isinstance(source, QComboBox):
                # QComboBox selects text in its internal lineEdit - deselect it
                if source.lineEdit():
                    QTimer.singleShot(0, lambda w=source: w.lineEdit(
                    ).deselect() if w.lineEdit() else None)
            elif isinstance(source, QSpinBox):
                # QSpinBox also has an internal lineEdit
                QTimer.singleShot(0, lambda w=source: w.lineEdit().deselect())

        # Check for FocusOut on author/series/genre combos to detect new values
        if event.type() == QEvent.FocusOut:
            if source == self.author_combo:
                self._check_combo_change("Author", self.author_combo,
                                         self._original_author, self.author_queries)
            elif source == self.series_combo:
                self._check_combo_change("Series", self.series_combo,
                                         self._original_series, self.series_queries)
            elif source == self.genre_combo:
                self._check_combo_change("Genre", self.genre_combo,
                                         self._original_genre, self.genre_queries)

            dirty_widget = self._resolve_dirty_source(source)
            if dirty_widget is not None:
                field_name = self._get_dirty_field_name(dirty_widget)
                self.set_status(
                    f"{field_name} changed. Press Alt+S Save or Alt+L Cancel",
                    announce=True
                )
                self._pending_dirty_widgets.discard(dirty_widget)

        # Block plain Up/Down arrow keys on combo boxes - require Alt+Up/Down
        # This prevents silent value changes that JAWS doesn't announce
        if event.type() == QEvent.KeyPress:
            if isinstance(source, QComboBox):
                key = event.key()
                modifiers = event.modifiers()
                if key in (Qt.Key_Up, Qt.Key_Down):
                    # Only allow with Alt modifier (opens dropdown, JAWS announces)
                    if not (modifiers & Qt.AltModifier):
                        # Block plain arrow keys - beep to indicate blocked
                        QApplication.beep()
                        return True  # Consume the event

        # Return False to let the event continue to the widget
        return super().eventFilter(source, event)

    def disable_hover_highlight(self):
        """Disable hover highlighting for low-vision comfort."""
        self.setMouseTracking(False)
        self.setAttribute(Qt.WA_Hover, False)
        for child in self.findChildren(QWidget):
            child.setMouseTracking(False)
            child.setAttribute(Qt.WA_Hover, False)

    def apply_control_styles(self):
        """
        bd#1: Apply uniform control heights to all form widgets.

        Uses stylesheets to set consistent min/max heights based on the
        current zoom scale. This matches the approach used in MainWindow.
        """
        # Get base height and scale it
        base_height = 20
        scale_pct = self.scaler.current_scale
        scaled_height = int(base_height * (scale_pct / 100.0))

        # Stylesheet for QLineEdit controls
        lineedit_style = f"""
            QLineEdit {{
                min-height: {scaled_height}px;
                max-height: {scaled_height}px;
                padding: 2px 4px;
                border: 1px solid palette(dark);
                border-radius: 3px;
            }}
            QLineEdit:focus {{
                border: 2px solid palette(highlight);
                background-color: palette(light);
            }}
            QLineEdit:read-only {{
                background-color: palette(window);
            }}
        """

        # Stylesheet for QComboBox controls (scaled height)
        combo_style = f"""
            QComboBox {{
                min-height: {scaled_height}px;
                max-height: {scaled_height}px;
                padding: 2px 4px;
                border: 1px solid palette(dark);
                border-radius: 3px;
            }}
            QComboBox:focus {{
                border: 2px solid palette(highlight);
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
            }}
        """

        # Stylesheet for QSpinBox controls
        spinbox_style = f"""
            QSpinBox {{
                min-height: {scaled_height}px;
                max-height: {scaled_height}px;
                padding: 2px;
                border: 1px solid palette(dark);
                border-radius: 3px;
            }}
            QSpinBox:focus {{
                border: 2px solid palette(highlight);
                background-color: palette(light);
            }}
        """

        # Stylesheet for QDateEdit controls
        dateedit_style = f"""
            QDateEdit {{
                min-height: {scaled_height}px;
                max-height: {scaled_height}px;
                padding: 2px;
                border: 1px solid palette(dark);
                border-radius: 3px;
            }}
            QDateEdit:focus {{
                border: 2px solid palette(highlight);
                background-color: palette(light);
            }}
        """

        # Stylesheet for QPushButton - compact height, visible border, inverted focus
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

        # Stylesheet for QLabel - bold text for form labels
        label_style = """
            QLabel {
                font-weight: bold;
            }
        """

        # Apply styles to widgets that need local styling
        # Text boxes, combo boxes, spin boxes, and date edits use theme manager styling - don't override
        for widget in self.findChildren(QPushButton):
            widget.setStyleSheet(button_style)
        for widget in self.findChildren(QLabel):
            widget.setStyleSheet(label_style)

    def setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # bd#8: Header section showing sort order
        header_layout = QHBoxLayout()
        self.sort_order_label = QLabel(f"Sorted by: {self.sort_order}")
        self.sort_order_label.setAccessibleName(
            f"Books sorted by {self.sort_order}")
        header_layout.addWidget(self.sort_order_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Form layout
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setSpacing(10)

        # bd#3 Row 1: Title + Author (side by side)
        row1_layout = QHBoxLayout()
        self.title_edit = QLineEdit()
        self.title_edit.setAccessibleName("Book title")
        row1_layout.addWidget(self.title_edit, 2)  # stretch=2 (wider)

        author_label = QLabel("&Author:")
        self.author_combo = QComboBox()
        self.author_combo.setEditable(True)
        self.author_combo.setAccessibleName("Author")
        self.author_combo.setMaximumWidth(280)
        author_label.setBuddy(self.author_combo)
        row1_layout.addWidget(author_label)
        row1_layout.addWidget(self.author_combo, 1)  # stretch=1

        title_label = QLabel("&Title:")
        title_label.setBuddy(self.title_edit)
        form.addRow(title_label, row1_layout)

        # bd#3 Row 2: Plot (expand to fit, hide when empty)
        self.comments_label = QLabel("Pl&ot:")
        self.comments_edit = QTextEdit()
        self.comments_edit.setAccessibleName("Plot")
        # Tab navigates instead of inserting tabs
        self.comments_edit.setTabChangesFocus(True)
        # Dynamic height: start small, grow with content
        self.comments_edit.setMinimumHeight(40)
        self.comments_edit.textChanged.connect(self._adjust_comments_height)
        self.comments_label.setBuddy(self.comments_edit)
        form.addRow(self.comments_label, self.comments_edit)

        # bd#3 Row 3: Year + Length + Reader + Read date
        row3_layout = QHBoxLayout()

        self.year_spin = QSpinBox()
        self.year_spin.setRange(0, 2100)
        self.year_spin.setSpecialValueText("")
        self.year_spin.setValue(self.year_spin.minimum())
        self.year_spin.setAccessibleName("Publication year")
        self.year_spin.setMaximumWidth(110)
        row3_layout.addWidget(self.year_spin)

        time_label = QLabel("Length (&M):")
        self.time_edit = QLineEdit()
        self.time_edit.setPlaceholderText("HH:MM")
        self.time_edit.setAccessibleName("Length")
        self.time_edit.setMaximumWidth(100)
        time_label.setBuddy(self.time_edit)
        row3_layout.addWidget(time_label)
        row3_layout.addWidget(self.time_edit)

        reader_label = QLabel("&Reader:")
        self.reader_edit = QLineEdit()
        self.reader_edit.setAccessibleName("Reader/Narrator")
        self.reader_edit.setMaximumWidth(220)
        reader_label.setBuddy(self.reader_edit)
        row3_layout.addWidget(reader_label)
        row3_layout.addWidget(self.reader_edit)

        read_label = QLabel("R&ead:")
        self.read_date = QDateEdit()
        self.read_date.setCalendarPopup(True)
        self.read_date.setDisplayFormat("yyyy-MM-dd")
        self.read_date.setAccessibleName("Date read")
        self.read_date.setMinimumDate(QDate(1, 1, 1))
        self.read_date.setSpecialValueText("")
        self.read_date.setMaximumWidth(150)
        self.read_date.setDate(self.read_date.minimumDate())
        
        # Override calendar widget to show today's date when opening from minimum date
        from PySide6.QtWidgets import QCalendarWidget
        
        class CustomCalendar(QCalendarWidget):
            def __init__(self, parent, date_edit):
                super().__init__(parent)
                self.date_edit = date_edit
                
            def showEvent(self, event):
                # If date is minimum (null), set to today before showing
                if self.date_edit.date() == self.date_edit.minimumDate():
                    self.date_edit.setDate(QDate.currentDate())
                super().showEvent(event)
        
        # Replace the calendar widget with our custom one
        calendar = CustomCalendar(self.read_date, self.read_date)
        self.read_date.setCalendarWidget(calendar)
        
        read_label.setBuddy(self.read_date)
        row3_layout.addWidget(read_label)
        row3_layout.addWidget(self.read_date)

        year_label = QLabel("&Year:")
        year_label.setBuddy(self.year_spin)
        form.addRow(year_label, row3_layout)

        # bd#3 Row 4: Series + Genre + Collection
        row4_layout = QHBoxLayout()

        self.series_combo = QComboBox()
        self.series_combo.setEditable(True)
        self.series_combo.setAccessibleName("Book series")
        self.series_combo.setMaximumWidth(260)
        row4_layout.addWidget(self.series_combo, 1)

        genre_label = QLabel("&Genre:")
        self.genre_combo = QComboBox()
        self.genre_combo.setEditable(True)
        self.genre_combo.setAccessibleName("Genre")
        self.genre_combo.setMaximumWidth(220)
        genre_label.setBuddy(self.genre_combo)
        row4_layout.addWidget(genre_label)
        row4_layout.addWidget(self.genre_combo, 1)

        collection_label = QLabel("Collection:")
        self.collection_combo = QComboBox()
        self.collection_combo.setAccessibleName("Collection")
        self.collection_combo.setMaximumWidth(220)
        collection_label.setBuddy(self.collection_combo)
        row4_layout.addWidget(collection_label)
        row4_layout.addWidget(self.collection_combo, 1)

        series_label = QLabel("Ser&ies:")
        series_label.setBuddy(self.series_combo)
        form.addRow(series_label, row4_layout)

        # bd#3 Row 5: Files + Bitrate + Size + Format + Source
        row5_layout = QHBoxLayout()

        files_label = QLabel("&Files:")
        self.files_edit = QLineEdit()
        self.files_edit.setReadOnly(False)
        self.files_edit.setAccessibleName("Number of files")
        self.files_edit.setMaximumWidth(70)
        files_label.setBuddy(self.files_edit)
        row5_layout.addWidget(self.files_edit)

        bitrate_label = QLabel("&Bitrate:")
        self.bitrate_edit = QLineEdit()
        self.bitrate_edit.setReadOnly(False)
        self.bitrate_edit.setAccessibleName("Bitrate in kbps")
        self.bitrate_edit.setMaximumWidth(95)
        bitrate_label.setBuddy(self.bitrate_edit)
        row5_layout.addWidget(bitrate_label)
        row5_layout.addWidget(self.bitrate_edit)

        size_label = QLabel("Si&ze:")
        self.size_edit = QLineEdit()
        self.size_edit.setReadOnly(False)
        self.size_edit.setAccessibleName("File size in megabytes")
        self.size_edit.setMaximumWidth(100)
        size_label.setBuddy(self.size_edit)
        row5_layout.addWidget(size_label)
        row5_layout.addWidget(self.size_edit)

        format_label = QLabel("Format:")
        self.format_combo = QComboBox()
        self.format_combo.setAccessibleName("File format")
        self.format_combo.setMaximumWidth(110)
        format_items = [
            ("MP3", "mp3"),
            ("M4A", "m4a"),
            ("M4B", "m4b"),
            ("FLAC", "flac"),
            ("OGG", "ogg"),
            ("WAV", "wav"),
            ("WMA", "wma"),
        ]
        for label, value in format_items:
            self.format_combo.addItem(label, value)
        row5_layout.addWidget(format_label)
        row5_layout.addWidget(self.format_combo)

        source_label = QLabel("Source:")
        self.source_edit = QLineEdit()
        self.source_edit.setReadOnly(True)
        self.source_edit.setAccessibleName("Import source")
        self.source_edit.setMaximumWidth(110)
        row5_layout.addWidget(source_label)
        row5_layout.addWidget(self.source_edit)

        form.addRow(files_label, row5_layout)

        # bd#3 Row 6: Path + Added date
        row6_layout = QHBoxLayout()

        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(False)
        self.path_edit.setAccessibleName("File path")
        row6_layout.addWidget(self.path_edit, 3)  # stretch=3 (wider)

        added_label = QLabel("Added:")
        self.added_edit = QLineEdit()
        self.added_edit.setReadOnly(True)
        self.added_edit.setAccessibleName("Date added to collection")
        self.added_edit.setMaximumWidth(150)
        row6_layout.addWidget(added_label)
        row6_layout.addWidget(self.added_edit, 1)

        path_label = QLabel("Pat&h:")
        path_label.setBuddy(self.path_edit)
        form.addRow(path_label, row6_layout)

        layout.addLayout(form)

        # bd#4: Action buttons - New, Save, Delete (Prev/Next via Page Up/Down)
        button_layout = QHBoxLayout()

        # New button (Alt+N) - clears form for new entry
        self.new_button = QPushButton("New")
        self.new_button.setAccessibleName("New book")
        self.new_button.setAccessibleDescription(
            "Clear form for new book entry - Alt+N or Ctrl+Enter")
        self.new_button.setFocusPolicy(Qt.StrongFocus)
        # self.new_button.setShortcut(QKeySequence("Alt+N"))  # Commented out for accessibility
        self.new_button.clicked.connect(self.on_new)
        self.new_button.setDefault(False)
        self.new_button.setAutoDefault(False)
        button_layout.addWidget(self.new_button)

        # Save button (Alt+S)
        self.save_button = QPushButton("Save")
        self.save_button.setAccessibleName("Save book")
        self.save_button.setAccessibleDescription("Save changes - Alt+S")
        self.save_button.setFocusPolicy(Qt.StrongFocus)
        # self.save_button.setShortcut(QKeySequence("Alt+S"))  # Commented out for accessibility
        self.save_button.clicked.connect(self.on_save)
        self.save_button.setDefault(False)
        self.save_button.setAutoDefault(False)
        button_layout.addWidget(self.save_button)

        # Delete button (Alt+D)
        self.delete_button = QPushButton("Delete")
        self.delete_button.setAccessibleName("Delete book")
        self.delete_button.setAccessibleDescription(
            "Delete this book - Alt+D or Delete key")
        self.delete_button.setFocusPolicy(Qt.StrongFocus)
        # self.delete_button.setShortcut(QKeySequence("Alt+D"))  # Commented out for accessibility
        self.delete_button.clicked.connect(self.on_delete)
        # Hide delete for new books (nothing to delete yet)
        self.delete_button.setVisible(not self.is_new)
        self.delete_button.setDefault(False)
        self.delete_button.setAutoDefault(False)
        button_layout.addWidget(self.delete_button)

        # Cancel button (Alt+L) - visible only when save/new is active
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setAccessibleName("Cancel")
        self.cancel_button.setAccessibleDescription("Cancel editing - Alt+L")
        self.cancel_button.setFocusPolicy(Qt.StrongFocus)
        # self.cancel_button.setShortcut(QKeySequence("Alt+L"))  # Commented out for accessibility
        self.cancel_button.clicked.connect(self.on_cancel_edit)
        self.cancel_button.setVisible(False)
        self.cancel_button.setDefault(False)
        self.cancel_button.setAutoDefault(False)
        button_layout.addWidget(self.cancel_button)

        # Update Metadata button (Alt+U)
        self.get_web_details_button = QPushButton("&Update Metadata")
        self.get_web_details_button.setAccessibleName("Update metadata")
        self.get_web_details_button.setAccessibleDescription("Fetch book metadata from web sources - Alt+U")
        self.get_web_details_button.setFocusPolicy(Qt.StrongFocus)
        self.get_web_details_button.clicked.connect(self.on_get_web_details)
        self.get_web_details_button.setDefault(False)
        self.get_web_details_button.setAutoDefault(False)
        button_layout.addWidget(self.get_web_details_button)

        button_layout.addStretch()

        layout.addLayout(button_layout)

        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        layout.addWidget(self.status_bar)

        # bd#4: Setup keyboard shortcuts
        self.setup_shortcuts()

    def reject(self):
        """
        Override reject to check for unsaved changes before closing.
        Yes = Save and stay on book, No = Continue editing, Cancel = Revert and close.
        """
        if self._dirty:
            msg = QMessageBox(self)
            msg.setWindowTitle("Unsaved Changes")
            msg.setStyleSheet(
                build_accessible_message_box_style(
                    self.scaler.get_scaled_size(20))
            )
            msg.setText(
                "You have unsaved changes.\n\n"
                "Yes = Save and stay\n"
                "No = Continue editing\n"
                "Cancel = Revert and close"
            )
            msg.setStandardButtons(
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            msg.button(QMessageBox.Yes).setText("&Yes")
            msg.button(QMessageBox.No).setText("&No")
            msg.button(QMessageBox.Cancel).setText("&Cancel")
            reply = msg.exec()

            if reply == QMessageBox.Yes:
                self.on_save()  # Save and stay (on_save doesn't close anymore)
            elif reply == QMessageBox.No:
                return  # Continue editing, keep dialog open
            else:  # Cancel - revert all fields and close
                self._revert_changes()
                announce_dialog_closed(self)
                super().reject()
        else:
            announce_dialog_closed(self)
            super().reject()  # No changes, just close

    def _revert_changes(self):
        """
        Revert all fields to their original values by reloading the book data.
        For new books, clear the form.
        """
        if self.is_new:
            # For new book, just clear the form
            self.on_new()
        else:
            # Reload original data
            self.load_book_data()

    def _get_dirty_field_name(self, widget) -> str:
        """Return a user-friendly field name for a dirty widget."""
        mapping = {
            self.title_edit: "Title",
            self.author_combo: "Author",
            self.year_spin: "Year",
            self.series_combo: "Series",
            self.genre_combo: "Genre",
            self.collection_combo: "Collection",
            self.reader_edit: "Reader",
            self.time_edit: "Length",
            self.files_edit: "Files",
            self.bitrate_edit: "Bitrate",
            self.size_edit: "Size",
            self.format_combo: "Format",
            self.source_edit: "Source",
            self.path_edit: "Path",
            self.comments_edit: "Plot",
            self.read_date: "Read date",
        }
        return mapping.get(widget, "Book details")

    def _setup_dirty_tracking(self):
        """
        bd#6: Connect all editable field signals to track changes.
        Save button is hidden until user makes changes (for existing books).
        """
        # Text fields - use lambda to track which field changed
        self.title_edit.textChanged.connect(
            lambda: self._mark_dirty(self.title_edit))
        self.reader_edit.textChanged.connect(
            lambda: self._mark_dirty(self.reader_edit))
        self.time_edit.textChanged.connect(
            lambda: self._mark_dirty(self.time_edit))
        self.comments_edit.textChanged.connect(
            lambda: self._mark_dirty(self.comments_edit))
        self.files_edit.textChanged.connect(
            lambda: self._mark_dirty(self.files_edit))
        self.bitrate_edit.textChanged.connect(
            lambda: self._mark_dirty(self.bitrate_edit))
        self.size_edit.textChanged.connect(
            lambda: self._mark_dirty(self.size_edit))
        self.format_combo.currentIndexChanged.connect(
            lambda: self._mark_dirty(self.format_combo))
        self.path_edit.textChanged.connect(
            lambda: self._mark_dirty(self.path_edit))

        # Combos
        self.author_combo.currentIndexChanged.connect(
            lambda: self._mark_dirty(self.author_combo))
        self.author_combo.editTextChanged.connect(
            lambda: self._mark_dirty(self.author_combo))
        self.series_combo.currentIndexChanged.connect(
            lambda: self._mark_dirty(self.series_combo))
        self.series_combo.editTextChanged.connect(
            lambda: self._mark_dirty(self.series_combo))
        self.genre_combo.currentIndexChanged.connect(
            lambda: self._mark_dirty(self.genre_combo))
        self.genre_combo.editTextChanged.connect(
            lambda: self._mark_dirty(self.genre_combo))
        self.collection_combo.currentIndexChanged.connect(
            lambda: self._mark_dirty(self.collection_combo))

        # Spinbox and date
        self.year_spin.valueChanged.connect(
            lambda: self._mark_dirty(self.year_spin))
        self.read_date.dateChanged.connect(
            lambda: self._mark_dirty(self.read_date))

    def _mark_dirty(self, widget=None):
        """bd#6: Mark form as having unsaved changes."""
        if widget is not None:
            self._pending_dirty_widgets.add(widget)

        if not self._dirty:
            self._dirty = True
            self._first_dirty_widget = widget
            self._update_save_button_visibility()

    def _resolve_dirty_source(self, source):
        """Resolve focus-out source widget to tracked dirty control."""
        if source in self._pending_dirty_widgets:
            return source

        for combo in [self.author_combo, self.series_combo, self.genre_combo, self.collection_combo]:
            if combo in self._pending_dirty_widgets and source == combo.lineEdit():
                return combo

        parent = source.parentWidget() if hasattr(source, "parentWidget") else None
        if parent in self._pending_dirty_widgets:
            return parent

        return None

    def _clear_dirty(self, preserve_status: bool = False):
        """bd#6: Clear dirty flag after save or load."""
        self._dirty = False
        self._first_dirty_widget = None
        self._pending_dirty_widgets.clear()
        self._update_save_button_visibility()
        if not preserve_status:
            self._show_idle_status(announce=False)

    def _show_idle_status(self, announce: bool = False):
        """Show default status when form is not in edit/save mode."""
        if self.is_new:
            self.set_status(
                "New book entry. Press Alt+S Save, Alt+L Cancel, Alt+U Update Metadata", announce=announce)
        else:
            self.set_status(
                "Alt+N New, Alt+D Delete, Alt+U Update Metadata, Escape Close", announce=announce)

    def _update_save_button_visibility(self):
        """
        bd#6: Show save button only when there are unsaved changes.
        For new books, always show save button.
        """
        save_active = self.is_new or self._dirty
        self.save_button.setVisible(save_active)

        # bd#16: Show/hide buttons based on save state
        # For new books: show New, hide Delete, show Save, hide Cancel, show Update Metadata
        # For existing books: show New/Delete when not saving, show Save/Cancel when saving
        self.new_button.setVisible(self.is_new and not save_active)
        self.delete_button.setVisible(
            (not self.is_new) and (not save_active))
        self.save_button.setVisible(save_active)
        self.cancel_button.setVisible(save_active)
        # Update Metadata: show for existing books, hide for new books
        self.get_web_details_button.setVisible(not self.is_new)

    def on_show_shortcuts(self):
        """Show keyboard shortcuts help dialog."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Keyboard Shortcuts - Book Details")
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
            ("Alt+M", "Length"),
            ("Alt+R", "Reader"),
            ("Alt+E", "Read date"),
            ("Alt+I", "Series"),
            ("Alt+G", "Genre"),
            ("Alt+C", "Collection"),
            ("Alt+F", "Files"),
            ("Alt+B", "Bitrate"),
            ("Alt+Z", "Size"),
            ("Alt+H", "Path"),
            ("Alt+U", "Update Metadata"),
            ("Alt+N", "New book"),
            ("Alt+S", "Save"),
            ("Alt+D", "Delete"),
            ("Alt+L", "Cancel"),
            ("Page Up", "Previous book"),
            ("Page Down", "Next book"),
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

        dlg.exec()

    def load_combos(self):
        """Load combo box data."""
        # Authors
        self.author_combo.clear()
        authors = self.author_queries.get_all()
        for author in authors:
            self.author_combo.addItem(author.name, author.author_id)

        # Series
        self.series_combo.clear()
        series_list = self.series_queries.get_all()
        for series in series_list:
            self.series_combo.addItem(series.name, series.series_id)

        # Genres
        self.genre_combo.clear()
        genres = self.genre_queries.get_all()
        for genre in genres:
            self.genre_combo.addItem(genre.name, genre.genre_id)

        # Collections
        self.collection_combo.clear()
        collections = self.collection_queries.get_all()
        for coll in collections:
            self.collection_combo.addItem(coll.name, coll.collection_id)

    def load_book_data(self):
        """Load book data into form."""
        self.title_edit.setText(self.book.title)

        # Set author combo
        idx = self.author_combo.findData(self.book.author_id)
        if idx >= 0:
            self.author_combo.setCurrentIndex(idx)

        # Year
        if self.book.year:
            self.year_spin.setValue(self.book.year)
        else:
            self.year_spin.setValue(self.year_spin.minimum())

        # Series
        if self.book.series_id:
            idx = self.series_combo.findData(self.book.series_id)
            if idx >= 0:
                self.series_combo.setCurrentIndex(idx)
        else:
            self.series_combo.setCurrentIndex(-1)
            self.series_combo.clearEditText()

        # Genre
        if self.book.genre_id:
            idx = self.genre_combo.findData(self.book.genre_id)
            if idx >= 0:
                self.genre_combo.setCurrentIndex(idx)
        else:
            self.genre_combo.setCurrentIndex(-1)
            self.genre_combo.clearEditText()

        # Reader
        self.reader_edit.setText(self.book.reader or "")

        # Collection
        if self.book.collection_id:
            idx = self.collection_combo.findData(self.book.collection_id)
            if idx >= 0:
                self.collection_combo.setCurrentIndex(idx)

        # Time
        self.time_edit.setText(self.book.time_display)

        # Files
        self.files_edit.setText(str(self.book.tracks)
                                if self.book.tracks else "")

        # Size
        self.size_edit.setText(self.book.size_display
                               if self.book.size_mb else "")

        # Bitrate
        self.bitrate_edit.setText(str(self.book.bitrate)
                                  if self.book.bitrate else "")

        # Format
        format_value = (self.book.file_format or "").lower()
        if format_value:
            idx = self.format_combo.findData(format_value)
            if idx >= 0:
                self.format_combo.setCurrentIndex(idx)
            else:
                self.format_combo.setCurrentIndex(-1)
        else:
            self.format_combo.setCurrentIndex(-1)

        # Path
        self.path_edit.setText(self.book.path or "")

        # Source
        self.source_edit.setText(self.book.source or "")

        # Date Added
        if self.book.date_added:
            if isinstance(self.book.date_added, str):
                self.added_edit.setText(self.book.date_added[:10])
            else:
                self.added_edit.setText(
                    self.book.date_added.strftime("%Y-%m-%d"))
        else:
            self.added_edit.setText("")

        # Comments - hide row if empty
        self.comments_edit.setPlainText(self.book.comments or "")
        # Delay height adjustment until widget is laid out
        QTimer.singleShot(0, self._adjust_comments_height)

        # Read date
        if self.book.read_date:
            read_date_value = self.book.read_date
            if isinstance(read_date_value, str):
                # Expect YYYY-MM-DD from SQLite; ignore invalid strings
                try:
                    read_date_value = datetime.strptime(
                        read_date_value, "%Y-%m-%d").date()
                except ValueError:
                    read_date_value = None

            if read_date_value:
                qdate = QDate(read_date_value.year,
                              read_date_value.month,
                              read_date_value.day)
                self.read_date.setDate(qdate)
            else:
                self.read_date.setDate(self.read_date.minimumDate())
        else:
            self.read_date.setDate(self.read_date.minimumDate())

        # Store original combo values for focusOut change detection
        self._original_author = self.author_combo.currentText()
        self._original_series = self.series_combo.currentText()
        self._original_genre = self.genre_combo.currentText()

    def _check_combo_change(self, field_name: str, combo: QComboBox,
                            original_value: str, query_obj):
        """
        Check if a combo box value changed to a new (non-existing) value.
        Called on focusOut for author, series, genre combos.
        Shows Yes/No dialog - if No, reverts to original value.
        """
        current_text = combo.currentText().strip()

        # Skip if empty, unchanged, or "None" (clear option)
        if not current_text or current_text == original_value:
            return

        # Check if this value exists in the database
        existing = query_obj.get_by_name(current_text)
        if existing:
            self._set_original_combo_value(field_name, current_text)
            return  # Value exists, no warning needed

        # Value is new - ask Yes/No
        msg = f"'{current_text}' is a new {field_name}.\n\nCreate this new {field_name}?"
        reply = exec_styled_message_box(
            self,
            self.scaler.get_scaled_size(20),
            icon=QMessageBox.Question,
            title=f"New {field_name}",
            text=msg,
            buttons=QMessageBox.Yes | QMessageBox.No,
            default_button=QMessageBox.No,
        )

        if reply != QMessageBox.Yes:
            # Revert to original value
            combo.setEditText(original_value)
            return

        self._set_original_combo_value(field_name, current_text)

    def _set_original_combo_value(self, field_name: str, value: str):
        """Update original text snapshot to avoid repeated 'new value' prompts."""
        if field_name == "Author":
            self._original_author = value
        elif field_name == "Series":
            self._original_series = value
        elif field_name == "Genre":
            self._original_genre = value

    def on_save(self):
        """Save book data."""
        title_text = self._normalize_name_field(self.title_edit.text())

        # Validate
        if not title_text:
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Warning,
                title="Validation Error",
                text="Title is required."
            )
            self.title_edit.setFocus()
            self.set_status("Title is required")
            return

        # Get author - confirm if creating new
        author_text = self._normalize_name_field(
            self.author_combo.currentText())
        if not author_text:
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Warning,
                title="Validation Error",
                text="Author is required."
            )
            self.author_combo.setFocus()
            self.set_status("Author is required")
            return

        # Get or create author (confirmation already done on focusOut)
        author_id = self.author_queries.get_or_create(author_text)

        # Get or create series (confirmation already done on focusOut)
        series_text = self._normalize_name_field(
            self.series_combo.currentText())
        series_id = None
        if series_text:
            series_id = self.series_queries.get_or_create(series_text)

        # Get or create genre (confirmation already done on focusOut)
        genre_text = self._normalize_name_field(self.genre_combo.currentText())
        genre_id = None
        if genre_text:
            genre_id = self.genre_queries.get_or_create(genre_text)

        reader_text = self._normalize_name_field(self.reader_edit.text())

        # Get collection
        collection_id = self.collection_combo.currentData()
        if collection_id is None and self.collection_combo.count() == 1:
            collection_id = self.collection_combo.itemData(0)

        # Parse time
        time_text = self.time_edit.text().strip()
        time_hours = 0
        time_minutes = 0
        if time_text and ':' in time_text:
            try:
                parts = time_text.split(':')
                time_hours = int(parts[0])
                time_minutes = int(parts[1])
            except (ValueError, IndexError):
                pass

        # Get read date
        read_date = None
        if self.read_date.date() != self.read_date.minimumDate():
            qdate = self.read_date.date()
            read_date = datetime(
                qdate.year(), qdate.month(), qdate.day()).date()

        year_value = self.year_spin.value()
        year_value = None if year_value == self.year_spin.minimum() else year_value

        tracks = 0
        files_text = self.files_edit.text().strip()
        if files_text:
            try:
                tracks = int(files_text)
            except ValueError:
                tracks = 0

        bitrate = 0
        bitrate_text = self.bitrate_edit.text().strip()
        if bitrate_text:
            try:
                bitrate = int(bitrate_text)
            except ValueError:
                bitrate = 0

        size_mb = 0.0
        size_text = self.size_edit.text().strip()
        if size_text:
            try:
                size_mb = float(size_text)
            except ValueError:
                size_mb = 0.0

        file_format = ""
        if self.format_combo.currentIndex() >= 0:
            file_format = self.format_combo.currentData() or ""
        source_text = self.source_edit.text().strip()
        path_text = self.path_edit.text().strip()

        # Update book object
        self.book.title = title_text
        self.book.author_id = author_id
        self.book.year = year_value
        self.book.series_id = series_id
        self.book.genre_id = genre_id
        self.book.collection_id = collection_id
        self.book.reader = reader_text
        self.book.time_hours = time_hours
        self.book.time_minutes = time_minutes
        self.book.tracks = tracks
        self.book.size_mb = size_mb
        self.book.bitrate = bitrate
        self.book.file_format = file_format
        self.book.source = source_text
        self.book.path = path_text
        self.book.comments = self.comments_edit.toPlainText()
        self.book.read_date = read_date

        # Save to database
        try:
            if self.is_new:
                self.book.date_added = datetime.now()
                if not self.book.source:
                    self.book.source = "Manual Entry"
                book_id = self.book_queries.insert(self.book)
                self.book.book_id = book_id
                self.is_new = False
                self.set_status("Book added successfully")
            else:
                self.book_queries.update(self.book)
                # Update the book in books_list
                if self.books_list and 0 <= self.current_index < len(self.books_list):
                    self.books_list[self.current_index] = self.book
                self.set_status("Book updated successfully")

            # Clear dirty and update original values (don't close window)
            self._clear_dirty(preserve_status=True)
            self._original_author = self.author_combo.currentText()
            self._original_series = self.series_combo.currentText()
            self._original_genre = self.genre_combo.currentText()
            self.setWindowTitle("Book Details")
            self.setAccessibleName("Book Details")

        except Exception as e:
            self.set_status("Error saving book")
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Critical,
                title="Error",
                text=f"Error saving book: {str(e)}"
            )

    def on_delete(self):
        """Delete book, with confirmation dialog."""
        if not self.book or not self.book.book_id:
            return
        # Confirm delete
        msg = QMessageBox(self)
        msg.setWindowTitle("Confirm Delete")
        msg.setStyleSheet(build_accessible_message_box_style(self.scaler.get_scaled_size(20)))
        msg.setText(f"Are you sure you want to delete this book?\n\nTitle: {self.book.title}")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.button(QMessageBox.Yes).setText("&Yes - Delete")
        msg.button(QMessageBox.No).setText("&No - Cancel")
        reply = msg.exec()
        if reply != QMessageBox.Yes:
            self.set_status("Delete canceled.")
            return
        try:
            deleted_index = self.current_index
            self.book_queries.delete(self.book.book_id)

            # Remove from books_list and navigate
            if self.books_list:
                self.books_list.pop(deleted_index)

                if len(self.books_list) == 0:
                    # No more books - close the window
                    exec_styled_message_box(
                        self,
                        self.scaler.get_scaled_size(20),
                        icon=QMessageBox.Information,
                        title="Success",
                        text="Book deleted. No more books."
                    )
                    self.set_status("Book deleted. No more books")
                    super().reject()
                    return
                elif deleted_index >= len(self.books_list):
                    # Was last book, move back one
                    self.current_index = len(self.books_list) - 1
                # else: stay at same index (now points to next book)

                self.book = self.books_list[self.current_index]
                self.is_new = False
                self.load_book_data()
                self._clear_dirty()
                self.update_navigation_state()
                self.setWindowTitle("Book Details")
                self.setAccessibleName("Book Details")
                exec_styled_message_box(
                    self,
                    self.scaler.get_scaled_size(20),
                    icon=QMessageBox.Information,
                    title="Success",
                    text="Book deleted successfully!"
                )
                self.set_status("Book deleted successfully")
            else:
                exec_styled_message_box(
                    self,
                    self.scaler.get_scaled_size(20),
                    icon=QMessageBox.Information,
                    title="Success",
                    text="Book deleted successfully!"
                )
                self.set_status("Book deleted successfully")
                super().reject()
        except Exception as e:
            self.set_status("Error deleting book")
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Critical,
                title="Error",
                text=f"Error deleting book: {str(e)}"
            )

    def on_new(self):
        """
        bd#4: Clear form for new book entry.
        Resets all fields and switches to 'new book' mode.
        """
        # Reset book object
        self.book = Book()
        self.is_new = True

        # Clear form fields
        self._reset_new_fields()

        # Update window title
        self.setWindowTitle("New Book")
        self.setAccessibleName("New Book")

        # Update button states
        self.delete_button.setVisible(False)
        self._update_save_button_visibility()  # bd#6: Show save for new book

        # Focus title field
        self.title_edit.setFocus()
        self.set_status("New book entry. Press Alt+S Save or Alt+L Cancel")

    def _apply_new_defaults(self):
        """Apply defaults for new entries without auto-selecting choices."""
        if self.collection_combo.count() == 1:
            self.collection_combo.setCurrentIndex(0)
        else:
            self.collection_combo.setCurrentIndex(-1)
        if not self.source_edit.text().strip():
            self.source_edit.setText(getpass.getuser())

    def _reset_new_fields(self):
        """Reset all editable fields for a new book without prepopulation."""
        self.title_edit.clear()
        self.author_combo.setCurrentIndex(-1)
        self.author_combo.clearEditText()
        self.year_spin.setValue(self.year_spin.minimum())
        self.series_combo.setCurrentIndex(-1)
        self.series_combo.clearEditText()
        self.genre_combo.setCurrentIndex(-1)
        self.genre_combo.clearEditText()
        self.reader_edit.clear()
        self.time_edit.clear()
        self.files_edit.clear()
        self.size_edit.clear()
        self.bitrate_edit.clear()
        self.format_combo.setCurrentIndex(-1)
        self.path_edit.clear()
        self.source_edit.clear()
        self.added_edit.setText("")
        self.comments_edit.clear()
        self.read_date.setDate(self.read_date.minimumDate())
        self._apply_new_defaults()
        self.reader_edit.setText("")

    def on_get_web_details(self):
        """Open web book details window to fetch and review web metadata."""
        if not self.book:
            self.set_status("No book selected for web lookup")
            return
        
        try:
            from src.ui.web_book_details_window import WebBookDetailsWindow
            
            # Create web details window
            web_window = WebBookDetailsWindow(self.db, self.book, self.scaler, self.theme_manager, self)
            
            # Show window modally
            result = web_window.exec()
            
            if result == QDialog.Accepted:
                # User accepted changes - would implement actual update here
                self.set_status("Web details applied successfully", announce=True)
                # For now, just reload book data
                self.load_book_data()
            else:
                self.set_status("Web details cancelled", announce=True)
                
        except Exception as e:
            print(f"DEBUG: Exception in on_get_web_details: {e}")
            import traceback
            traceback.print_exc()
            self.set_status(f"Error opening web details: {str(e)}")

    def on_prev(self):
        """
        bd#4: Navigate to previous book in the list.
        Blocked with beep if there are unsaved changes.
        """
        # Block navigation if dirty
        if self._dirty:
            QApplication.beep()
            self.set_status(
                "Unsaved changes. Press Alt+S Save or Alt+L Cancel")
            return

        if not self.books_list or self.current_index <= 0:
            return

        self.current_index -= 1
        self.book = self.books_list[self.current_index]
        self.is_new = False
        self.load_book_data()
        self._clear_dirty()  # bd#6: Reset dirty after loading new book
        self.update_navigation_state()

        # Update window title
        self.setWindowTitle("Book Details")
        self.setAccessibleName("Book Details")

    def on_next(self):
        """
        bd#4: Navigate to next book in the list.
        Blocked with beep if there are unsaved changes.
        """
        # Block navigation if dirty
        if self._dirty:
            QApplication.beep()
            self.set_status(
                "Unsaved changes. Press Alt+S Save or Alt+L Cancel")
            return

        if not self.books_list or self.current_index >= len(self.books_list) - 1:
            return

        self.current_index += 1
        self.book = self.books_list[self.current_index]
        self.is_new = False
        self.load_book_data()
        self._clear_dirty()  # bd#6: Reset dirty after loading new book
        self.update_navigation_state()

        # Update window title
        self.setWindowTitle("Book Details")
        self.setAccessibleName("Book Details")

    def _adjust_comments_height(self):
        """Adjust comments QTextEdit height to fit content."""
        text = self.comments_edit.toPlainText().strip()
        if not text:
            # Empty: collapse to single line height
            self.comments_edit.setFixedHeight(25)
            return

        doc = self.comments_edit.document()
        # Set document width to viewport width so it calculates wrapped height
        doc.setTextWidth(self.comments_edit.viewport().width())
        # Calculate height needed for content plus margins
        doc_height = doc.size().height()
        margins = self.comments_edit.contentsMargins()
        frame_width = self.comments_edit.frameWidth() * 2
        needed_height = int(doc_height + margins.top() +
                            margins.bottom() + frame_width + 5)
        # Clamp between min 40 and max 200
        new_height = max(40, min(200, needed_height))
        self.comments_edit.setFixedHeight(new_height)

    def update_navigation_state(self):
        """Update button states based on current position."""
        self.delete_button.setVisible(not self.is_new)
