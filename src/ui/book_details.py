"""
Book Details Window
Form for viewing and editing individual book information.
"""

import re

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

from database import DatabaseManager, Book, BookQueries, AuthorQueries, SeriesQueries, GenreQueries, CollectionQueries
from accessibility.scaling import UIScaler
from accessibility.style_helpers import build_accessible_message_box_style, exec_styled_message_box
from accessibility.accessible_events import announce_status_message, announce_form_field, announce_dialog_opened, announce_dialog_closed


class BookDetailsWindow(QDialog):
    """
    Book details dialog for viewing/editing book information.
    """

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

    def __init__(self, db: DatabaseManager, scaler: UIScaler, book: Book = None,
                 sort_order: str = "Title", books_list: list = None,
                 current_index: int = 0, parent=None):
        """
        Initialize book details window.

        Args:
            db: Database manager
            scaler: UI scaler
            book: Book to edit (None for new book)
            sort_order: Current sort order from main window (for header display)
            books_list: List of Book objects for Prev/Next navigation
            current_index: Index of current book in books_list
            parent: Parent widget
        """
        super().__init__(parent)
        self.setAttribute(Qt.WA_NativeWindow, True)
        self.setWindowModality(Qt.ApplicationModal)
        self.winId()

        self.db = db
        self.scaler = scaler
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

        # Setup UI
        self.setup_ui()
        self.apply_control_styles()  # bd#1: Uniform control heights
        self.disable_hover_highlight()
        self.install_focus_filters()  # bd#2: Prevent text auto-select on focus
        self.load_combos()

        if not self.is_new:
            self.load_book_data()

        # bd#6: Setup dirty tracking and initial save button visibility
        self._setup_dirty_tracking()
        self._update_save_button_visibility()

        # Window settings
        title = "New Book" if self.is_new else f"Book Details - {self.book.title}"
        self.setWindowTitle(title)
        self.setAccessibleName(title)
        self.setAccessibleDescription(
            "Form for viewing and editing book information")
        self.resize(850, 500)
        announce_dialog_opened(self, title)
        self.set_status("Ready")
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

        # Apply styles to all matching widgets
        for widget in self.findChildren(QLineEdit):
            widget.setStyleSheet(lineedit_style)
        for widget in self.findChildren(QComboBox):
            widget.setStyleSheet(combo_style)
        for widget in self.findChildren(QSpinBox):
            widget.setStyleSheet(spinbox_style)
        for widget in self.findChildren(QDateEdit):
            widget.setStyleSheet(dateedit_style)
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

        # bd#3 Row 2: Comments (expand to fit, hide when empty)
        self.comments_label = QLabel("C&omments:")
        self.comments_edit = QTextEdit()
        self.comments_edit.setAccessibleName("Comments")
        # Tab navigates instead of inserting tabs
        self.comments_edit.setTabChangesFocus(True)
        # Dynamic height: start small, grow with content
        self.comments_edit.setMinimumHeight(40)
        self.comments_edit.textChanged.connect(self._adjust_comments_height)
        self.comments_label.setBuddy(self.comments_edit)
        form.addRow(self.comments_label, self.comments_edit)

        # bd#3 Row 3: Year + Time + Reader + Read date
        row3_layout = QHBoxLayout()

        self.year_spin = QSpinBox()
        self.year_spin.setRange(1900, 2100)
        self.year_spin.setValue(datetime.now().year)
        self.year_spin.setAccessibleName("Publication year")
        self.year_spin.setMaximumWidth(95)
        row3_layout.addWidget(self.year_spin)

        time_label = QLabel("Ti&me:")
        self.time_edit = QLineEdit()
        self.time_edit.setPlaceholderText("HH:MM")
        self.time_edit.setAccessibleName("Duration")
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
        self.read_date.setSpecialValueText("Not read")
        self.read_date.setMaximumWidth(150)
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

        collection_label = QLabel("Collection (&K):")
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
        self.files_edit.setReadOnly(True)
        self.files_edit.setAccessibleName("Number of files")
        self.files_edit.setMaximumWidth(70)
        files_label.setBuddy(self.files_edit)
        row5_layout.addWidget(self.files_edit)

        bitrate_label = QLabel("&Bitrate:")
        self.bitrate_edit = QLineEdit()
        self.bitrate_edit.setReadOnly(True)
        self.bitrate_edit.setAccessibleName("Bitrate in kbps")
        self.bitrate_edit.setMaximumWidth(95)
        bitrate_label.setBuddy(self.bitrate_edit)
        row5_layout.addWidget(bitrate_label)
        row5_layout.addWidget(self.bitrate_edit)

        size_label = QLabel("Si&ze:")
        self.size_edit = QLineEdit()
        self.size_edit.setReadOnly(True)
        self.size_edit.setAccessibleName("File size in megabytes")
        self.size_edit.setMaximumWidth(100)
        size_label.setBuddy(self.size_edit)
        row5_layout.addWidget(size_label)
        row5_layout.addWidget(self.size_edit)

        format_label = QLabel("Format:")
        self.format_edit = QLineEdit()
        self.format_edit.setReadOnly(True)
        self.format_edit.setAccessibleName("File format")
        self.format_edit.setMaximumWidth(90)
        row5_layout.addWidget(format_label)
        row5_layout.addWidget(self.format_edit)

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
        self.path_edit.setReadOnly(True)
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

        # bd#4: Four buttons - New, Save, Delete, Close (Prev/Next via Page Up/Down)
        button_layout = QHBoxLayout()

        # New button (Alt+N) - clears form for new entry
        self.new_button = QPushButton("&New")
        self.new_button.setAccessibleName("New book")
        self.new_button.setAccessibleDescription(
            "Clear form for new book entry - Alt+N or Ctrl+Enter")
        self.new_button.setFocusPolicy(Qt.StrongFocus)
        self.new_button.clicked.connect(self.on_new)
        button_layout.addWidget(self.new_button)

        # Save button (Alt+S)
        self.save_button = QPushButton("&Save")
        self.save_button.setAccessibleName("Save book")
        self.save_button.setAccessibleDescription("Save changes - Alt+S")
        self.save_button.setFocusPolicy(Qt.StrongFocus)
        self.save_button.clicked.connect(self.on_save)
        button_layout.addWidget(self.save_button)

        # Delete button (Alt+D)
        self.delete_button = QPushButton("&Delete")
        self.delete_button.setAccessibleName("Delete book")
        self.delete_button.setAccessibleDescription(
            "Delete this book - Alt+D or Delete key")
        self.delete_button.setFocusPolicy(Qt.StrongFocus)
        self.delete_button.clicked.connect(self.on_delete)
        # Hide delete for new books (nothing to delete yet)
        self.delete_button.setVisible(not self.is_new)
        button_layout.addWidget(self.delete_button)

        # Cancel button (Alt+L) - visible only when save/new is active
        self.cancel_button = QPushButton("Cance&l")
        self.cancel_button.setAccessibleName("Cancel")
        self.cancel_button.setAccessibleDescription("Cancel editing - Alt+L")
        self.cancel_button.setFocusPolicy(Qt.StrongFocus)
        self.cancel_button.clicked.connect(self.on_cancel_edit)
        self.cancel_button.setVisible(False)
        button_layout.addWidget(self.cancel_button)

        button_layout.addStretch()

        # Close button (Alt+C)
        self.close_button = QPushButton("&Close")
        self.close_button.setAccessibleName("Close window")
        self.close_button.setAccessibleDescription(
            "Close window - Alt+C or Escape")
        self.close_button.setFocusPolicy(Qt.StrongFocus)
        self.close_button.clicked.connect(self.reject)
        button_layout.addWidget(self.close_button)

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
            msg.button(QMessageBox.Yes).setText("&Yes - Save")
            msg.button(QMessageBox.No).setText("&No - Continue editing")
            msg.button(QMessageBox.Cancel).setText(
                "Cance&l - Revert and close")
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
        self._clear_dirty()

    def setup_shortcuts(self):
        """bd#4: Setup keyboard shortcuts for buttons."""
        # Ctrl+Enter for New (consistent with other windows)
        self.new_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        self.new_shortcut.activated.connect(self.on_new)

        # Delete key for Delete
        self.delete_shortcut = QShortcut(QKeySequence(Qt.Key_Delete), self)
        self.delete_shortcut.activated.connect(self.on_delete)

        # Page Up for Prev
        self.pageup_shortcut = QShortcut(QKeySequence(Qt.Key_PageUp), self)
        self.pageup_shortcut.activated.connect(self.on_prev)

        # Page Down for Next
        self.pagedown_shortcut = QShortcut(QKeySequence(Qt.Key_PageDown), self)
        self.pagedown_shortcut.activated.connect(self.on_next)

        # Escape for Close
        self.escape_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.escape_shortcut.activated.connect(self.reject)

        # F1 for Help
        self.help_shortcut = QShortcut(QKeySequence("F1"), self)
        self.help_shortcut.activated.connect(self.on_show_shortcuts)

        # Alt+/ reads status bar
        self.status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.status_shortcut.activated.connect(self.on_read_status_bar)

        # Alt+L cancel when cancel button is active
        self.cancel_shortcut = QShortcut(QKeySequence("Alt+L"), self)
        self.cancel_shortcut.activated.connect(self.on_cancel_shortcut)

    def on_cancel_shortcut(self):
        """Handle Alt+L when Cancel is available."""
        if self.cancel_button.isVisible():
            self.on_cancel_edit()

    def on_cancel_edit(self):
        """Cancel edits and revert to standard browsing mode without closing."""
        if self.is_new:
            if self.books_list and 0 <= self.current_index < len(self.books_list):
                self.book = self.books_list[self.current_index]
                self.is_new = False
                self.load_book_data()
                self.update_navigation_state()
                self.setWindowTitle(f"Book Details - {self.book.title}")
                self.setAccessibleName(f"Book Details - {self.book.title}")
            else:
                super().reject()
                return
        else:
            self.load_book_data()

        self._clear_dirty()
        self.set_status("Changes canceled")

    def set_status(self, message: str, timeout_ms: int = 0, announce: bool = True):
        """Set status bar message with optional screen reader announcement."""
        self._default_status_message = message
        self.status_bar.showMessage(message)

        if announce and QAccessible.isActive():
            previous_focus = QApplication.instance().focusWidget()
            self.status_bar.setFocusPolicy(Qt.StrongFocus)
            self.status_bar.setFocus()

            def restore_focus():
                if previous_focus:
                    previous_focus.setFocus()
                self.status_bar.setFocusPolicy(Qt.NoFocus)

            QTimer.singleShot(100, restore_focus)

        if timeout_ms > 0:
            QTimer.singleShot(
                timeout_ms,
                lambda: self.status_bar.showMessage(
                    self._default_status_message)
            )

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
            self.time_edit: "Time",
            self.comments_edit: "Comments",
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

    def _clear_dirty(self):
        """bd#6: Clear dirty flag after save or load."""
        self._dirty = False
        self._first_dirty_widget = None
        self._pending_dirty_widgets.clear()
        self._update_save_button_visibility()

    def _update_save_button_visibility(self):
        """
        bd#6: Show save button only when there are unsaved changes.
        For new books, always show save button.
        """
        save_active = self.is_new or self._dirty
        self.save_button.setVisible(save_active)

        # bd#16: Hide New and Delete when Save is active
        self.new_button.setVisible(not save_active)
        self.delete_button.setVisible((not self.is_new) and (not save_active))
        self.cancel_button.setVisible(save_active)
        self.close_button.setVisible(not save_active)

    def on_show_shortcuts(self):
        """Show keyboard shortcuts help dialog."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Keyboard Shortcuts - Book Details")
        dlg.setAccessibleName("Keyboard Shortcuts")
        dlg.resize(450, 500)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Shortcuts list
        shortcuts = [
            ("Alt+/", "Read status bar"),
            ("Alt+T", "Title"),
            ("Alt+A", "Author"),
            ("Alt+O", "Comments"),
            ("Alt+Y", "Year"),
            ("Alt+M", "Time"),
            ("Alt+R", "Reader"),
            ("Alt+E", "Read date"),
            ("Alt+I", "Series"),
            ("Alt+G", "Genre"),
            ("Alt+K", "Collection"),
            ("Alt+F", "Files"),
            ("Alt+B", "Bitrate"),
            ("Alt+Z", "Size"),
            ("Alt+H", "Path"),
            ("Alt+N", "New book"),
            ("Alt+S", "Save"),
            ("Alt+D", "Delete"),
            ("Alt+L", "Cancel"),
            ("Alt+C", "Close window"),
            ("Page Up", "Previous book"),
            ("Page Down", "Next book"),
            ("Escape", "Close window"),
            ("F1", "Show this help"),
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

        # Populate table
        for row, (key, description) in enumerate(shortcuts):
            if key:
                combined_text = f"{description} - {key}"
            else:
                combined_text = ""
            item = QTableWidgetItem(combined_text)
            item.setData(Qt.AccessibleTextRole,
                         f"{description}: {key}" if key else "")
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

    def load_combos(self):
        """Load combo box data."""
        # Authors
        self.author_combo.clear()
        authors = self.author_queries.get_all()
        for author in authors:
            self.author_combo.addItem(author.name, author.author_id)

        # Series
        self.series_combo.clear()
        self.series_combo.addItem("None", None)  # Clear option
        series_list = self.series_queries.get_all()
        for series in series_list:
            self.series_combo.addItem(series.name, series.series_id)

        # Genres
        self.genre_combo.clear()
        self.genre_combo.addItem("None", None)  # Clear option
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

        # Series
        if self.book.series_id:
            idx = self.series_combo.findData(self.book.series_id)
            if idx >= 0:
                self.series_combo.setCurrentIndex(idx)

        # Genre
        if self.book.genre_id:
            idx = self.genre_combo.findData(self.book.genre_id)
            if idx >= 0:
                self.genre_combo.setCurrentIndex(idx)

        # Reader
        self.reader_edit.setText(self.book.reader)

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
        self.size_edit.setText(self.book.size_display)

        # Bitrate
        self.bitrate_edit.setText(str(self.book.bitrate))

        # Format
        self.format_edit.setText(self.book.file_format)

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
        if not current_text or current_text == original_value or current_text == "None":
            return

        # Check if this value exists in the database
        existing = query_obj.get_by_name(current_text)
        if existing:
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
                text="Title is required.",
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
                text="Author is required.",
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
        if series_text and series_text != "None":
            series_id = self.series_queries.get_or_create(series_text)

        # Get or create genre (confirmation already done on focusOut)
        genre_text = self._normalize_name_field(self.genre_combo.currentText())
        genre_id = None
        if genre_text and genre_text != "None":
            genre_id = self.genre_queries.get_or_create(genre_text)

        reader_text = self._normalize_name_field(self.reader_edit.text())

        # Get collection
        collection_id = self.collection_combo.currentData()
        if collection_id is None and self.collection_combo.count() > 0:
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

        # Update book object
        self.book.title = title_text
        self.book.author_id = author_id
        self.book.year = self.year_spin.value()
        self.book.series_id = series_id
        self.book.genre_id = genre_id
        self.book.collection_id = collection_id
        self.book.reader = reader_text
        self.book.time_hours = time_hours
        self.book.time_minutes = time_minutes
        self.book.comments = self.comments_edit.toPlainText()
        self.book.read_date = read_date

        # Save to database
        try:
            if self.is_new:
                self.book.date_added = datetime.now()
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
            self._clear_dirty()
            self._original_author = self.author_combo.currentText()
            self._original_series = self.series_combo.currentText()
            self._original_genre = self.genre_combo.currentText()
            self.setWindowTitle(f"Book Details - {self.book.title}")

        except Exception as e:
            self.set_status("Error saving book")
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Critical,
                title="Error",
                text=f"Error saving book: {str(e)}",
            )

    def on_delete(self):
        """Delete book."""
        # Don't allow delete for new books
        if self.is_new:
            return

        reply = exec_styled_message_box(
            self,
            self.scaler.get_scaled_size(20),
            icon=QMessageBox.Question,
            title="Confirm Delete",
            text=f"Are you sure you want to delete '{self.book.title}'?",
            buttons=QMessageBox.Yes | QMessageBox.No,
            default_button=QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
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
                            text="Book deleted. No more books.",
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
                    self.setWindowTitle(f"Book Details - {self.book.title}")
                    exec_styled_message_box(
                        self,
                        self.scaler.get_scaled_size(20),
                        icon=QMessageBox.Information,
                        title="Success",
                        text="Book deleted successfully!",
                    )
                    self.set_status("Book deleted successfully")
                else:
                    exec_styled_message_box(
                        self,
                        self.scaler.get_scaled_size(20),
                        icon=QMessageBox.Information,
                        title="Success",
                        text="Book deleted successfully!",
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
                    text=f"Error deleting book: {str(e)}",
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
        self.title_edit.clear()
        self.author_combo.setCurrentIndex(-1)
        self.author_combo.clearEditText()
        self.year_spin.setValue(datetime.now().year)
        self.series_combo.setCurrentIndex(0)  # Empty option
        self.genre_combo.setCurrentIndex(0)   # Empty option
        # Keep current collection as default
        self.reader_edit.clear()
        self.time_edit.clear()
        self.files_edit.clear()
        self.size_edit.clear()
        self.bitrate_edit.clear()
        self.format_edit.clear()
        self.path_edit.clear()
        self.source_edit.clear()
        self.added_edit.setText(datetime.now().strftime("%Y-%m-%d"))
        self.comments_edit.clear()
        self.read_date.setDate(self.read_date.minimumDate())

        # Update window title
        self.setWindowTitle("New Book")
        self.setAccessibleName("New Book")

        # Update button states
        self.delete_button.setVisible(False)
        self._update_save_button_visibility()  # bd#6: Show save for new book

        # Focus title field
        self.title_edit.setFocus()
        self.set_status("New book entry. Press Alt+S Save or Alt+L Cancel")

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
        self.setWindowTitle(f"Book Details - {self.book.title}")
        self.setAccessibleName(f"Book Details - {self.book.title}")

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
        self.setWindowTitle(f"Book Details - {self.book.title}")
        self.setAccessibleName(f"Book Details - {self.book.title}")

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
