"""
Book Details Window
Form for viewing and editing individual book information.
"""

import re
from src.database import (
    DatabaseManager,
    Book,
    BookQueries,
    AuthorQueries,
    SeriesQueries,
    GenreQueries,
    CollectionQueries,
)
from src.accessibility.icon_helper import apply_decorative_action_icon
from src.accessibility.theme_manager import ThemeManager
from src.accessibility.scaling import UIScaler
from src.accessibility.style_helpers import (
    apply_status_bar_tooltip,
    apply_visual_tooltip_map,
    build_accessible_message_box_style,
    build_modern_button_style,
    exec_styled_message_box,
    MESSAGE_BOX_DELETE_CONFIRM_ICONS,
    MESSAGE_BOX_UNSAVED_THREE_ICONS,
    MESSAGE_BOX_UNSAVED_TWO_ICONS,
)
from src.accessibility.accessible_events import (
    announce_status_message,
    announce_dialog_closed,
    configure_status_bar_accessibility,
    read_status_bar_message,
)
from src.accessibility.key_filters import is_unmapped_alt_letter
from src.accessibility.read_only_text import (
    PlotLineList,
    format_plot_text_for_navigation,
    set_navigable_plain_text,
)
import getpass

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLineEdit,
    QComboBox,
    QTextEdit,
    QStackedWidget,
    QPushButton,
    QLabel,
    QDateEdit,
    QSpinBox,
    QMessageBox,
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QApplication,
    QStatusBar,
    QSizePolicy,
    QStackedWidget,
)
from PySide6.QtCore import Qt, QDate, QEvent, QTimer, QSettings, QObject
from PySide6.QtGui import QAccessible, QTextCursor, QShortcut, QKeySequence
from datetime import datetime
from typing import List, Dict, Any
from src.ui.accessible_dialog import AccessibleDialog

class BookDetailsWindow(AccessibleDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from src.accessibility.icon_helper import get_app_icon

        self.setWindowIcon(get_app_icon())

    # List of allowed Alt+key shortcuts for Book Details
    ALLOWED_ALT_KEYS = {
        "N",
        "D",
        "S",
        "U",
        "W",
        "T",
        "A",
        "P",
        "Y",
        "M",
        "R",
        "E",
        "I",
        "G",
        "C",
        "F",
        "B",
        "Z",
        "O",  # Alt+O for Format
        "H",
        "/",
        "F1",
    }

    def set_status(self, message: str, announce: bool = False):
        """Set status bar message with optional screen reader announcement. No Alt+key shortcut hints."""
        self._default_status_message = message
        announce_status_message(self.status_bar, message, move_focus=announce)

    def on_read_status_bar(self, *, announce_text: str | None = None):
        """Read current status bar message (Alt+/)."""
        fallback = announce_text or self._idle_status_message()
        read_status_bar_message(
            self.status_bar,
            fallback=fallback,
            announce_text=announce_text,
        )

    def on_cancel_edit(self):
        """
        Handle Cancel (Escape) action: show save dialog if dirty, then close.
        Restores combo focus if Escape pressed while a combo is focused.
        """
        focused_widget = self.focusWidget()
        combo_to_restore = None
        if isinstance(focused_widget, QComboBox):
            combo_to_restore = focused_widget
        elif hasattr(focused_widget, "parentWidget") and isinstance(
            focused_widget.parentWidget(), QComboBox
        ):
            combo_to_restore = focused_widget.parentWidget()

        if self._dirty:
            from src.accessibility.icon_helper import get_app_icon

            book_title = getattr(self, "title_edit", None)
            book_author = getattr(self, "author_combo", None)
            title_val = book_title.text().strip() if book_title else "(Untitled)"
            author_val = (
                book_author.currentText().strip() if book_author else "(Unknown author)"
            )
            msg_text = (
                f"You have unsaved changes for '{title_val}' by {author_val}.\n\n"
                "Yes = Save and close\n"
                "No = Continue editing\n"
                "Cancel = Revert and close"
            )
            reply = exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Question,
                title="Unsaved Changes",
                text=msg_text,
                buttons=QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                default_button=QMessageBox.Cancel,
                button_texts={
                    QMessageBox.Yes: "&Yes",
                    QMessageBox.No: "&No",
                    QMessageBox.Cancel: "&Cancel",
                },
                window_icon=get_app_icon(),
                button_icon_roles=MESSAGE_BOX_UNSAVED_THREE_ICONS,
            )

            if reply == QMessageBox.Yes:
                # Save and close
                self.on_save()
                announce_dialog_closed(self)
                self.reject()
            elif reply == QMessageBox.No:
                # Continue editing
                if combo_to_restore:
                    QTimer.singleShot(0, combo_to_restore.setFocus)
                return
            else:  # Cancel - revert and close
                self._revert_changes()
                self.set_status("Changes discarded.", announce=True)
                announce_dialog_closed(self)
                self.reject()
        else:
            # No changes, just close
            announce_dialog_closed(self)
            self.reject()
        if combo_to_restore:
            QTimer.singleShot(0, combo_to_restore.setFocus)

    @staticmethod
    def _normalize_time_text(raw_text: str) -> str:
        """Normalize time text to HH:MM from HHMM or HH:MM input."""
        digits = "".join(ch for ch in (raw_text or "") if ch.isdigit())
        if len(digits) != 4:
            return ""
        hours = int(digits[:2])
        minutes = int(digits[2:])
        if minutes > 59:
            return ""
        return f"{hours:02d}:{minutes:02d}"

    def _normalize_time_on_focus_out(self):
        """Normalize time field quietly when focus leaves the control."""
        normalized = self._normalize_time_text(self.time_edit.text())
        if normalized and normalized != self.time_edit.text():
            self.time_edit.setText(normalized)

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
            r"(\bO')([a-z])", lambda m: m.group(1) + m.group(2).upper(), value
        )
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

    def __init__(
        self,
        db: DatabaseManager,
        scaler: UIScaler,
        book: Book = None,
        sort_order: str = "Title",
        books_list: list = None,
        current_index: int = 0,
        theme_manager: ThemeManager = None,
        parent=None,
        current_collection_id=None,
    ):
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
            current_collection_id: Current collection ID (if provided and new book)
        """
        # Initialize book details window
        super().__init__(parent)
        self.setAttribute(Qt.WA_NativeWindow, True)
        self.setWindowModality(Qt.ApplicationModal)
        self.winId()

        self.db = db
        self.scaler = scaler
        self.theme_manager = theme_manager or ThemeManager(
            QApplication.instance()
        )  # Store theme manager
        self.book = book or Book()
        self.is_new = book is None
        self.sort_order = sort_order  # bd#8: Store for header display
        self._dirty = False  # bd#6: Track if form has unsaved changes
        self._data_was_changed = False  # True after save/delete/web apply; gates list refresh
        self._in_edit_mode = False  # Track whether Book Details is currently in edit mode
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

        # Store current collection id for new book defaulting
        self.current_collection_id = current_collection_id

        # Query objects
        self.book_queries = BookQueries(db)
        self.author_queries = AuthorQueries(db)
        self.series_queries = SeriesQueries(db)
        self.genre_queries = GenreQueries(db)
        self.collection_queries = CollectionQueries(db)

        # Setup UI
        self.setup_ui()
        self.apply_visual_tooltips()
        self.apply_control_styles()  # bd#1: Uniform control heights
        self.disable_hover_highlight()
        self.install_focus_filters()  # bd#2: Prevent text auto-select on focus

        # PHASE 2 OPTIMIZATION: View/Edit mode - skip combo loading for existing books
        # New books: load combos immediately (user will edit)
        # Existing books: show labels, load combos on demand via Edit button
        if self.is_new:
            # New book: load combos and show them immediately
            self.load_combos()
            self._hide_view_labels()
        else:
            # Existing book: view mode - hide combos, show labels (fast!)
            self._show_view_labels()

        # Load book data (view mode uses labels, edit mode uses combos)
        if not self.is_new:
            self.load_book_data()
        else:
            self._reset_new_fields()

        # bd#6: Setup dirty tracking and initial save button visibility
        self._setup_dirty_tracking()
        self._update_save_button_visibility()

        # Window settings (title bar only; no accessible name/description noise for SR)
        title = "New Book" if self.is_new else "Book Details"
        self.setWindowTitle(title)
        self.setAccessibleName("")
        self.setAccessibleDescription("")
        self.resize(850, 650)
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

        # Also filter plot editor
        for widget in self.findChildren(QTextEdit):
            widget.installEventFilter(self)

        # Filter QComboBox and QSpinBox - they select text AFTER their internal lineEdit gets focus
        for widget in self.findChildren(QComboBox):
            widget.installEventFilter(self)
        for widget in self.findChildren(QSpinBox):
            widget.installEventFilter(self)

        # Filter QPushButton for Enter key handling when focused
        for widget in self.findChildren(QPushButton):
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

            # Handle Enter key on focused buttons
            if key == Qt.Key_Return or key == Qt.Key_Enter:
                if isinstance(source, QPushButton) and source.hasFocus():
                    source.click()
                    return True

            # Block unused Alt+letter keys everywhere
            if is_unmapped_alt_letter(event, self.ALLOWED_ALT_KEYS):
                QApplication.beep()
                return True

        if event.type() == QEvent.FocusIn:
            # Schedule deselection AFTER Qt finishes its default focus handling
            # QTimer.singleShot(0, ...) runs on the next event loop iteration
            # Use default argument (w=source) to capture the widget value NOW,
            # not when the lambda executes later
            if isinstance(source, QLineEdit):
                QTimer.singleShot(0, lambda w=source: w.deselect())
            elif isinstance(source, QTextEdit):
                if source is not self.comments_edit:
                    QTimer.singleShot(0, lambda w=source: w.moveCursor(QTextCursor.Start))
            elif isinstance(source, QComboBox):
                # QComboBox selects text in its internal lineEdit - deselect it
                if source.lineEdit():
                    QTimer.singleShot(
                        0,
                        lambda w=source: (
                            w.lineEdit().deselect() if w.lineEdit() else None
                        ),
                    )
            elif isinstance(source, QSpinBox):
                # QSpinBox also has an internal lineEdit
                QTimer.singleShot(0, lambda w=source: w.lineEdit().deselect())

        # Check for FocusOut on relevant fields to sanitize input silently
        # Only sanitize if field has been modified (is dirty) - prevents unwanted prompts for save
        if event.type() == QEvent.FocusOut:
            from src.core.validator import ImportValidator

            validator = ImportValidator()
            dirty_widget = self._resolve_dirty_source(source)
            is_dirty = dirty_widget is not None

            # Title - only sanitize if dirty
            if source == self.title_edit and is_dirty:
                val = self.title_edit.text()
                temp = {"title": val}
                validator.sanitize_metadata(temp)
                if temp["title"] != val:
                    self.title_edit.setText(temp["title"])
            # Author - only sanitize if dirty
            elif source == self.author_combo and is_dirty:
                val = self.author_combo.currentText()
                temp = {"author": val}
                validator.sanitize_metadata(temp)
                if temp["author"] != val:
                    self.author_combo.setEditText(temp["author"])
                self._check_combo_change(
                    "Author",
                    self.author_combo,
                    self._original_author,
                    self.author_queries,
                )
            # Series - only sanitize if dirty
            elif source == self.series_combo and is_dirty:
                val = self.series_combo.currentText()
                temp = {"series": val}
                validator.sanitize_metadata(temp)
                if temp["series"] != val:
                    self.series_combo.setEditText(temp["series"])
                self._check_combo_change(
                    "Series",
                    self.series_combo,
                    self._original_series,
                    self.series_queries,
                )
            # Genre - only sanitize if dirty
            elif source == self.genre_combo and is_dirty:
                val = self.genre_combo.currentText()
                temp = {"genre": val}
                validator.sanitize_metadata(temp)
                if temp["genre"] != val:
                    self.genre_combo.setEditText(temp["genre"])
                self._check_combo_change(
                    "Genre", self.genre_combo, self._original_genre, self.genre_queries
                )
            # Reader - only sanitize if dirty
            elif source == self.reader_edit and is_dirty:
                val = self.reader_edit.text()
                temp = {"reader": val}
                validator.sanitize_metadata(temp)
                if temp["reader"] != val:
                    self.reader_edit.setText(temp["reader"])

            # The combo _check_combo_change calls still need to happen for non-dirty fields
            # to handle auto-creation of new entries, but sanitization is skipped
            elif source == self.author_combo:
                self._check_combo_change(
                    "Author",
                    self.author_combo,
                    self._original_author,
                    self.author_queries,
                )
            elif source == self.series_combo:
                self._check_combo_change(
                    "Series",
                    self.series_combo,
                    self._original_series,
                    self.series_queries,
                )
            elif source == self.genre_combo:
                self._check_combo_change(
                    "Genre", self.genre_combo, self._original_genre, self.genre_queries
                )

            dirty_widget = self._resolve_dirty_source(source)
            if dirty_widget is not None:
                field_name = self._get_dirty_field_name(dirty_widget)
                # Only announce if value actually changed (existing logic)
                last_status = getattr(self, "_last_status_message", None)
                new_status = f"{field_name} changed."
                if last_status != new_status:
                    self.set_status(new_status, announce=True)
                    self._last_status_message = new_status
                self._pending_dirty_widgets.discard(dirty_widget)

        # Block plain Up/Down arrow keys on combo boxes - require Alt+Up/Down
        # This prevents silent value changes that the screen reader doesn't announce
        if event.type() == QEvent.KeyPress:
            if isinstance(source, QComboBox):
                key = event.key()
                modifiers = event.modifiers()
                if key in (Qt.Key_Up, Qt.Key_Down):
                    # Only allow with Alt modifier (opens dropdown, screen reader announces)
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

        # Stylesheet for QPushButton - compact height, visible border, inverted focus
        button_style = build_modern_button_style(scaled_height)

        # Stylesheet for QLabel - bold text for form labels
        label_style = """
            QLabel {
                font-weight: bold;
            }
        """

        self.save_button.setObjectName("primaryActionButton")
        self.delete_button.setObjectName("destructiveActionButton")
        self.edit_button.setObjectName("")
        self.new_button.setObjectName("")

        # Apply styles to widgets that need local styling
        # Text boxes, combo boxes, spin boxes, and date edits use theme manager styling - don't override
        for widget in self.findChildren(QComboBox):
            widget.setStyleSheet("")
        for widget in self.findChildren(QPushButton):
            widget.setStyleSheet(button_style)
        for widget in self.findChildren(QLabel):
            widget.setStyleSheet(label_style)
        self._apply_action_button_icons()

    def _apply_action_button_icons(self):
        """Decorative icons beside action button text."""
        apply_decorative_action_icon(self.new_button, "new", self.scaler)
        apply_decorative_action_icon(self.edit_button, "update", self.scaler)
        apply_decorative_action_icon(self.save_button, "save", self.scaler)
        apply_decorative_action_icon(self.delete_button, "delete", self.scaler)
        apply_decorative_action_icon(
            self.get_web_details_button, "search_web", self.scaler
        )

    def _configure_field_combo(self, combo: QComboBox) -> None:
        """Keep combo fields within the form column, not the longest list item."""
        combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        combo.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )
        combo.setMinimumContentsLength(12)

    def _make_view_edit_stack(
        self, view_widget: QWidget, edit_widget: QWidget
    ) -> QStackedWidget:
        """Stack view and edit widgets so only one sizes the grid cell."""
        stack = QStackedWidget()
        stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        stack.addWidget(view_widget)
        stack.addWidget(edit_widget)
        stack.setCurrentWidget(view_widget)
        return stack

    def setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # bd#8: Header section showing sort order
        header_layout = QHBoxLayout()
        self.sort_order_label = QLabel(f"Sorted by: {self.sort_order}")
        self.sort_order_label.setAccessibleName("")
        self.sort_order_label.setAccessibleDescription("")
        self.sort_order_label.setFocusPolicy(Qt.NoFocus)
        if QAccessible.isActive():
            self.sort_order_label.hide()
        header_layout.addWidget(self.sort_order_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Two-column grid layout — stable label column, expanding field column
        grid = QGridLayout()
        grid.setColumnStretch(1, 1)
        grid.setColumnMinimumWidth(0, self.scaler.get_scaled_size(90))
        grid.setVerticalSpacing(10)
        grid.setHorizontalSpacing(8)

        label_align = Qt.AlignRight | Qt.AlignVCenter

        ROW_TITLE = 0
        ROW_AUTHOR = 1
        ROW_PLOT = 2
        ROW_YEAR_TIME = 3
        ROW_READER_READ = 4
        ROW_SERIES = 5
        ROW_GENRE = 6
        ROW_COLLECTION = 7
        ROW_FILES = 8
        ROW_FORMAT = 9
        ROW_PATH = 10

        # Title
        title_label = QLabel("Title:")
        self.title_edit = QLineEdit()
        self.title_edit.setAccessibleName("")
        self.title_edit.setAccessibleDescription("")
        title_label.setBuddy(self.title_edit)
        grid.addWidget(title_label, ROW_TITLE, 0, label_align)
        grid.addWidget(self.title_edit, ROW_TITLE, 1)

        # Author — view label and combo share the same grid cell
        author_label = QLabel("Author:")
        self.author_label_display = QLineEdit()
        self.author_label_display.setReadOnly(True)
        self.author_label_display.setAccessibleName("Author")
        self.author_label_display.setAccessibleDescription(
            "Author name - press Alt+A to focus, Alt+U to edit"
        )
        self.author_label_display.setFocusPolicy(Qt.StrongFocus)
        self.author_combo = QComboBox()
        self.author_combo.setEditable(True)
        self.author_combo.setAccessibleName("Author")
        self._configure_field_combo(self.author_combo)
        self.author_field_stack = self._make_view_edit_stack(
            self.author_label_display, self.author_combo
        )
        author_label.setBuddy(self.author_label_display)
        grid.addWidget(author_label, ROW_AUTHOR, 0, label_align)
        grid.addWidget(self.author_field_stack, ROW_AUTHOR, 1)

        # Plot — line list for review, text edit for editing
        self.comments_label = QLabel("Plot:")
        self.plot_review = PlotLineList()
        self.plot_review.setAccessibleName("Plot")
        self.comments_edit = QTextEdit()
        self.comments_edit.setAccessibleName("Plot editor")
        self.comments_edit.setAccessibleDescription("Plot summary for editing.")
        self.comments_edit.setTabChangesFocus(True)
        self.comments_edit.setFocusPolicy(Qt.StrongFocus)
        self.plot_stack = QStackedWidget()
        self.plot_stack.addWidget(self.plot_review)
        self.plot_stack.addWidget(self.comments_edit)
        self.plot_stack.setFocusPolicy(Qt.StrongFocus)
        self.plot_stack.setCurrentWidget(self.plot_review)
        self.plot_stack.setFocusProxy(self.plot_review)
        self.comments_edit.setMinimumHeight(120)
        self.comments_edit.setMaximumHeight(200)
        self.plot_review.setMinimumHeight(120)
        self.plot_review.setMaximumHeight(200)
        self.comments_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.plot_review.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.comments_label.setBuddy(self.plot_stack)
        grid.addWidget(self.comments_label, ROW_PLOT, 0, label_align)
        grid.addWidget(self.plot_stack, ROW_PLOT, 1)

        # Year + Time
        self.year_spin = QSpinBox()
        self.year_spin.setRange(0, 2100)
        self.year_spin.setSpecialValueText("")
        self.year_spin.setValue(self.year_spin.minimum())
        self.year_spin.setAccessibleName("Publication year")
        self.year_spin.setMaximumWidth(110)

        time_label = QLabel("Time:")
        time_label.setAlignment(label_align)
        self.time_edit = QLineEdit()
        self.time_edit.setInputMask("99:99;_")
        self.time_edit.setPlaceholderText("HH:MM")
        self.time_edit.setAccessibleName("Time")
        self.time_edit.setMaximumWidth(100)
        time_label.setBuddy(self.time_edit)

        year_time_layout = QHBoxLayout()
        year_time_layout.setContentsMargins(0, 0, 0, 0)
        year_time_layout.addWidget(self.year_spin)
        year_time_layout.addWidget(time_label)
        year_time_layout.addWidget(self.time_edit)
        year_time_layout.addStretch()
        year_time_widget = QWidget()
        year_time_widget.setLayout(year_time_layout)

        year_label = QLabel("Year:")
        year_label.setBuddy(self.year_spin)
        grid.addWidget(year_label, ROW_YEAR_TIME, 0, label_align)
        grid.addWidget(year_time_widget, ROW_YEAR_TIME, 1)

        # Reader + Read date
        reader_label = QLabel("Reader:")
        reader_label.setAlignment(label_align)
        self.reader_edit = QLineEdit()
        self.reader_edit.setAccessibleName("Reader/Narrator")
        reader_label.setBuddy(self.reader_edit)

        read_label = QLabel("Read:")
        read_label.setAlignment(label_align)
        self.read_date = QDateEdit()
        self._null_read_date = QDate(2000, 1, 1)
        self.read_date.setCalendarPopup(True)
        self.read_date.setDisplayFormat("yyyy-MM-dd")
        self.read_date.setAccessibleName("Date read")
        self.read_date.setMinimumDate(QDate(1752, 9, 14))
        self.read_date.setSpecialValueText("")
        self.read_date.setMaximumWidth(150)
        self.read_date.setDate(self._null_read_date)

        from PySide6.QtWidgets import QCalendarWidget

        class CustomCalendar(QCalendarWidget):
            def __init__(self, parent, date_edit, null_date):
                super().__init__(parent)
                self.date_edit = date_edit
                self._null_date = null_date

                if hasattr(parent, "scaler"):
                    scaler = parent.scaler
                    calendar_style = f"""
                    QCalendarWidget {{
                        font-size: {scaler.get_scaled_size(12)}pt;
                    }}
                    QCalendarWidget QToolButton {{
                        font-size: {scaler.get_scaled_size(12)}pt;
                        min-height: {scaler.get_scaled_size(24)}px;
                        min-width: {scaler.get_scaled_size(24)}px;
                    }}
                    QCalendarWidget QAbstractItemView:enabled {{
                        font-size: {scaler.get_scaled_size(12)}pt;
                        selection-background-color: palette(highlight);
                        selection-color: palette(highlighted-text);
                    }}
                    QCalendarWidget QAbstractItemView:disabled {{
                        font-size: {scaler.get_scaled_size(12)}pt;
                        color: palette(text);
                        background-color: palette(base);
                    }}
                    """
                    self.setStyleSheet(calendar_style)

            def showEvent(self, event):
                if self.date_edit.date() == self._null_date:
                    today = QDate.currentDate()
                    self.date_edit.setDate(today)
                    self.setSelectedDate(today)
                super().showEvent(event)

        calendar = CustomCalendar(self, self.read_date, self._null_read_date)
        self.read_date.setCalendarWidget(calendar)
        read_label.setBuddy(self.read_date)

        reader_read_layout = QHBoxLayout()
        reader_read_layout.setContentsMargins(0, 0, 0, 0)
        reader_read_layout.addWidget(self.reader_edit, 1)
        reader_read_layout.addWidget(read_label)
        reader_read_layout.addWidget(self.read_date)
        reader_read_layout.addStretch()
        reader_read_widget = QWidget()
        reader_read_widget.setLayout(reader_read_layout)

        grid.addWidget(reader_label, ROW_READER_READ, 0, label_align)
        grid.addWidget(reader_read_widget, ROW_READER_READ, 1)

        # Series — view label and combo share the same grid cell
        series_label = QLabel("Series:")
        self.series_label_display = QLineEdit()
        self.series_label_display.setReadOnly(True)
        self.series_label_display.setAccessibleName("Book series")
        self.series_label_display.setAccessibleDescription(
            "Series name - press Alt+I to focus, Alt+U to edit"
        )
        self.series_label_display.setFocusPolicy(Qt.StrongFocus)
        self.series_combo = QComboBox()
        self.series_combo.setEditable(True)
        self.series_combo.setAccessibleName("Book series")
        self._configure_field_combo(self.series_combo)
        self.series_field_stack = self._make_view_edit_stack(
            self.series_label_display, self.series_combo
        )
        series_label.setBuddy(self.series_label_display)
        grid.addWidget(series_label, ROW_SERIES, 0, label_align)
        grid.addWidget(self.series_field_stack, ROW_SERIES, 1)

        # Genre — view label and combo share the same grid cell
        genre_label = QLabel("Genre:")
        self.genre_label_display = QLineEdit()
        self.genre_label_display.setReadOnly(True)
        self.genre_label_display.setAccessibleName("Genre")
        self.genre_label_display.setAccessibleDescription(
            "Genre - press Alt+G to focus, Alt+U to edit"
        )
        self.genre_label_display.setFocusPolicy(Qt.StrongFocus)
        self.genre_combo = QComboBox()
        self.genre_combo.setEditable(True)
        self.genre_combo.setAccessibleName("Genre")
        self._configure_field_combo(self.genre_combo)
        self.genre_field_stack = self._make_view_edit_stack(
            self.genre_label_display, self.genre_combo
        )
        genre_label.setBuddy(self.genre_label_display)
        grid.addWidget(genre_label, ROW_GENRE, 0, label_align)
        grid.addWidget(self.genre_field_stack, ROW_GENRE, 1)

        # Collection — view label and combo share the same grid cell
        collection_label = QLabel("Collection:")
        self.collection_label_display = QLineEdit()
        self.collection_label_display.setReadOnly(True)
        self.collection_label_display.setAccessibleName("Collection")
        self.collection_label_display.setAccessibleDescription(
            "Collection - press Alt+C to focus, Alt+U to edit"
        )
        self.collection_label_display.setFocusPolicy(Qt.StrongFocus)
        self.collection_combo = QComboBox()
        self.collection_combo.setAccessibleName("Collection")
        self._configure_field_combo(self.collection_combo)
        self.collection_field_stack = self._make_view_edit_stack(
            self.collection_label_display, self.collection_combo
        )
        collection_label.setBuddy(self.collection_label_display)
        grid.addWidget(collection_label, ROW_COLLECTION, 0, label_align)
        grid.addWidget(self.collection_field_stack, ROW_COLLECTION, 1)

        # Files + Bitrate + Size
        files_label = QLabel("Files:")
        self.files_edit = QLineEdit()
        self.files_edit.setReadOnly(False)
        self.files_edit.setAccessibleName("Number of files")
        files_label.setBuddy(self.files_edit)

        bitrate_label = QLabel("Bitrate:")
        bitrate_label.setAlignment(label_align)
        self.bitrate_edit = QLineEdit()
        self.bitrate_edit.setReadOnly(False)
        self.bitrate_edit.setAccessibleName("Bitrate in kbps")
        bitrate_label.setBuddy(self.bitrate_edit)

        size_label = QLabel("Size:")
        size_label.setAlignment(label_align)
        self.size_edit = QLineEdit()
        self.size_edit.setReadOnly(False)
        self.size_edit.setAccessibleName("File size in megabytes")
        size_label.setBuddy(self.size_edit)

        files_layout = QHBoxLayout()
        files_layout.setContentsMargins(0, 0, 0, 0)
        files_layout.addWidget(self.files_edit)
        files_layout.addWidget(bitrate_label)
        files_layout.addWidget(self.bitrate_edit)
        files_layout.addWidget(size_label)
        files_layout.addWidget(self.size_edit)
        files_layout.addStretch()
        files_widget = QWidget()
        files_widget.setLayout(files_layout)
        grid.addWidget(files_label, ROW_FILES, 0, label_align)
        grid.addWidget(files_widget, ROW_FILES, 1)

        # Format + Source
        format_label = QLabel("Format:")
        self.format_combo = QComboBox()
        self.format_combo.setAccessibleName("File format")
        self._configure_field_combo(self.format_combo)
        self.format_combo.setMaximumWidth(120)
        format_label.setBuddy(self.format_combo)
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

        source_label = QLabel("Source:")
        source_label.setAlignment(label_align)
        self.source_edit = QLineEdit()
        self.source_edit.setReadOnly(False)
        self.source_edit.setAccessibleName("Import source")

        format_layout = QHBoxLayout()
        format_layout.setContentsMargins(0, 0, 0, 0)
        format_layout.addWidget(self.format_combo)
        format_layout.addWidget(source_label)
        format_layout.addWidget(self.source_edit, 1)
        format_layout.addStretch()
        format_widget = QWidget()
        format_widget.setLayout(format_layout)
        grid.addWidget(format_label, ROW_FORMAT, 0, label_align)
        grid.addWidget(format_widget, ROW_FORMAT, 1)

        # Path + Added date
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(False)
        self.path_edit.setAccessibleName("File path")

        added_label = QLabel("Added:")
        added_label.setAlignment(label_align)
        self.added_edit = QLineEdit()
        self.added_edit.setReadOnly(True)
        self.added_edit.setAccessibleName("Date added to collection")
        self.added_edit.setMaximumWidth(150)

        path_layout = QHBoxLayout()
        path_layout.setContentsMargins(0, 0, 0, 0)
        path_layout.addWidget(self.path_edit, 1)
        path_layout.addWidget(added_label)
        path_layout.addWidget(self.added_edit)
        path_widget = QWidget()
        path_widget.setLayout(path_layout)

        path_label = QLabel("Path:")
        path_label.setBuddy(self.path_edit)
        grid.addWidget(path_label, ROW_PATH, 0, label_align)
        grid.addWidget(path_widget, ROW_PATH, 1)

        layout.addLayout(grid)

        # bd#4: Action buttons - New, Save, Delete (Prev/Next via Page Up/Down)
        button_layout = QHBoxLayout()

        # Stretch first to push buttons to the right
        button_layout.addStretch()

        # New button (Alt+N) - clears form for new entry
        self.new_button = QPushButton("New")
        self.new_button.setAccessibleName("New book")
        self.new_button.setAccessibleDescription("Clear form for new book entry")
        self.new_button.setFocusPolicy(Qt.StrongFocus)
        self.new_button.clicked.connect(self.on_new)
        self.new_button.setDefault(False)
        self.new_button.setAutoDefault(
            False
        )  # Restored to prevent global Enter trigger
        button_layout.addWidget(self.new_button)

        # Update button (Alt+U via shortcut) - toggles view/edit mode for combos
        self.edit_button = QPushButton("Update")
        self.edit_button.setAccessibleName("Update book")
        self.edit_button.setAccessibleDescription("Enable editing of book details")
        self.edit_button.setFocusPolicy(Qt.StrongFocus)
        self.edit_button.clicked.connect(self.on_edit_mode)
        self.edit_button.setDefault(False)
        self.edit_button.setAutoDefault(False)
        button_layout.addWidget(self.edit_button)

        # Save button (Alt+S)
        self.save_button = QPushButton("Save")
        self.save_button.setAccessibleName("Save book")
        self.save_button.setAccessibleDescription("Save changes")
        self.save_button.setFocusPolicy(Qt.StrongFocus)
        self.save_button.clicked.connect(self.on_save)
        self.save_button.setDefault(False)
        self.save_button.setAutoDefault(
            False
        )  # Restored to prevent global Enter trigger
        button_layout.addWidget(self.save_button)

        # Delete button (Alt+D)
        self.delete_button = QPushButton("Delete")
        self.delete_button.setAccessibleName("Delete book")
        self.delete_button.setAccessibleDescription("Delete this book")
        self.delete_button.setFocusPolicy(Qt.StrongFocus)
        self.delete_button.clicked.connect(self.on_delete)
        # Hide delete for new books (nothing to delete yet)
        self.delete_button.setVisible(not self.is_new)
        self.delete_button.setDefault(False)
        self.delete_button.setAutoDefault(
            False
        )  # Restored to prevent global Enter trigger
        button_layout.addWidget(self.delete_button)

        # Get web info button (Alt+W)
        self.get_web_details_button = QPushButton("Fetch Web Info")
        self.get_web_details_button.setAccessibleName("Get web info")
        self.get_web_details_button.setAccessibleDescription("Fetch book info from web")
        self.get_web_details_button.setFocusPolicy(Qt.StrongFocus)
        self.get_web_details_button.clicked.connect(self.on_get_web_details)
        self.get_web_details_button.setDefault(False)
        self.get_web_details_button.setAutoDefault(
            False
        )  # Restored to prevent global Enter trigger
        button_layout.addWidget(self.get_web_details_button)

        layout.addLayout(button_layout)

        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        configure_status_bar_accessibility(self.status_bar)
        layout.addWidget(self.status_bar)

        # Set explicit tab order for predictable screen reader navigation
        # bd#7: Include view labels in tab order for accessibility
        self.setTabOrder(self.title_edit, self.author_label_display)
        self.setTabOrder(self.author_label_display, self.author_combo)
        self.setTabOrder(self.author_combo, self.plot_stack)
        self.setTabOrder(self.plot_stack, self.year_spin)
        self.setTabOrder(self.year_spin, self.time_edit)
        self.setTabOrder(self.time_edit, self.reader_edit)
        self.setTabOrder(self.reader_edit, self.read_date)
        self.setTabOrder(self.read_date, self.series_label_display)
        self.setTabOrder(self.series_label_display, self.series_combo)
        self.setTabOrder(self.series_combo, self.genre_label_display)
        self.setTabOrder(self.genre_label_display, self.genre_combo)
        self.setTabOrder(self.genre_combo, self.collection_label_display)
        self.setTabOrder(self.collection_label_display, self.collection_combo)
        self.setTabOrder(self.collection_combo, self.files_edit)
        self.setTabOrder(self.files_edit, self.bitrate_edit)
        self.setTabOrder(self.bitrate_edit, self.size_edit)
        self.setTabOrder(self.size_edit, self.format_combo)
        self.setTabOrder(self.format_combo, self.source_edit)
        self.setTabOrder(self.source_edit, self.path_edit)
        self.setTabOrder(self.path_edit, self.added_edit)
        self.setTabOrder(self.added_edit, self.new_button)
        self.setTabOrder(self.new_button, self.edit_button)
        self.setTabOrder(self.edit_button, self.save_button)
        self.setTabOrder(self.save_button, self.delete_button)
        self.setTabOrder(self.delete_button, self.get_web_details_button)

        # bd#4: Setup keyboard shortcuts
        self.setup_shortcuts()

    def apply_visual_tooltips(self):
        """Short sighted-user tooltips paired with screen reader descriptions."""
        apply_visual_tooltip_map(
            {
                self.title_edit: (
                    "Book title",
                    "",
                ),
                self.author_combo: (
                    "Author name",
                    "Author of the audiobook",
                ),
                self.author_label_display: (
                    "Author name",
                    "Author name - press Alt+A to focus, Alt+U to edit",
                ),
                self.comments_edit: (
                    "Plot or comments",
                    "Plot summary or comments for this book",
                ),
                self.year_spin: (
                    "Publication year",
                    "Publication year of the audiobook",
                ),
                self.time_edit: (
                    "Audiobook length",
                    "Length in hours and minutes",
                ),
                self.reader_edit: (
                    "Narrator or reader",
                    "Narrator or reader name",
                ),
                self.read_date: (
                    "Date read",
                    "Date this book was marked as read",
                ),
                self.series_combo: (
                    "Series name",
                    "Series this book belongs to",
                ),
                self.series_label_display: (
                    "Series name",
                    "Series name - press Alt+I to focus, Alt+U to edit",
                ),
                self.genre_combo: (
                    "Genre",
                    "Genre classification for this book",
                ),
                self.genre_label_display: (
                    "Genre",
                    "Genre - press Alt+G to focus, Alt+U to edit",
                ),
                self.collection_combo: (
                    "Collection",
                    "Collection that owns this book",
                ),
                self.collection_label_display: (
                    "Collection",
                    "Collection - press Alt+C to focus, Alt+U to edit",
                ),
                self.files_edit: (
                    "Number of audio files",
                    "Number of files in this audiobook",
                ),
                self.bitrate_edit: (
                    "Audio bitrate",
                    "Bitrate in kilobits per second",
                ),
                self.size_edit: (
                    "Total file size",
                    "Combined file size in megabytes",
                ),
                self.format_combo: (
                    "Audio file format",
                    "Primary audio file format",
                ),
                self.source_edit: (
                    "Import source",
                    "How this book was added to the library",
                ),
                self.path_edit: (
                    "Folder or file path",
                    "Location of audiobook files on disk",
                ),
                self.added_edit: (
                    "Date added",
                    "Date this book was added to the collection",
                ),
                self.new_button: (
                    "Start a new book entry",
                    "Clear form for new book entry",
                ),
                self.edit_button: (
                    "Edit book details",
                    "Enable editing of book details",
                ),
                self.save_button: (
                    "Save changes",
                    "Save changes to this book",
                ),
                self.delete_button: (
                    "Delete this book",
                    "Delete this book from the collection",
                ),
                self.get_web_details_button: (
                    "Fetch metadata from the web",
                    "Fetch book info from web",
                ),
            }
        )
        apply_status_bar_tooltip(self.status_bar, "")

    def _idle_status_message(self) -> str:
        """Default status text when the form is idle (view or new-book mode)."""
        if self.is_new:
            return "New book entry."
        title = (getattr(self, "title_edit", None) and self.title_edit.text() or "").strip()
        if not title:
            title = (getattr(self.book, "title", None) or "").strip()
        title = title or "(Untitled)"
        author = (
            getattr(self, "author_label_display", None)
            and self.author_label_display.text()
            or ""
        ).strip()
        if not author:
            author = (getattr(self.book, "author_name", None) or "").strip()
        author = author or "(Unknown author)"
        return f"{title} by {author}."

    def _blur_title_before_navigation_load(self):
        """Move focus off title so setText during load does not trigger SR."""
        for widget in (self.edit_button, self.save_button, self.new_button, self.delete_button):
            if widget.isVisible():
                widget.setFocus(Qt.OtherFocusReason)
                return

    def _focus_title_after_navigation(self):
        """Speak title only after Page Up/Down (same pattern as import detail)."""
        was_read_only = self.title_edit.isReadOnly()
        in_edit_mode = self._in_edit_mode

        def focus_title():
            if was_read_only and not in_edit_mode:
                self.title_edit.setReadOnly(False)
            self.title_edit.setAccessibleName("")
            self.title_edit.setAccessibleDescription("")
            self.title_edit.setFocus(Qt.OtherFocusReason)

            def restore_read_only():
                if was_read_only and not in_edit_mode:
                    self.title_edit.setReadOnly(True)

            from src.accessibility.screen_reader import get_screen_reader_focus_delay_ms

            delay = max(get_screen_reader_focus_delay_ms(), 400)
            QTimer.singleShot(delay, restore_read_only)

        QTimer.singleShot(0, focus_title)

    def setup_shortcuts(self):
        """bd#4: Setup keyboard shortcuts for buttons."""
        # Use centralized shortcuts for fields, local shortcuts for buttons (like import_detail)
        from src.accessibility.shortcuts import get_shortcut_manager, ShortcutContext

        mgr = get_shortcut_manager()

        # Field shortcuts (centralized)
        # Build callback map from centralized shortcut mapping to avoid duplicates
        from src.accessibility.shortcuts import BOOK_DETAILS_SHORTCUTS

        callback_map = {}
        for key, (desc, attr) in BOOK_DETAILS_SHORTCUTS.items():
            if attr == "show_help":
                callback_map[attr] = self.on_show_shortcuts
            elif hasattr(self, attr):
                widget = getattr(self, attr)
                # Only connect focus for widgets that support setFocus
                if hasattr(widget, "setFocus"):
                    callback_map[attr] = lambda w=widget: w.setFocus()
        # Add button callbacks that trigger actions (not just focus)
        callback_map["get_web_details_button"] = self.on_get_web_details
        callback_map["edit_button"] = self.on_edit_mode
        # Add focus routing for view labels (route to combos when labels are hidden in edit mode)
        callback_map["author_label_display"] = self._focus_author
        callback_map["series_label_display"] = self._focus_series
        callback_map["genre_label_display"] = self._focus_genre
        callback_map["collection_label_display"] = self._focus_collection
        callback_map["comments_edit"] = self._focus_plot
        mgr.register_alt_shortcuts(self, ShortcutContext.BOOK_DETAILS, callback_map)

        # Button shortcuts (local like import_detail)
        self.new_shortcut = QShortcut(QKeySequence("Alt+N"), self)
        self.new_shortcut.activated.connect(
            lambda: self.on_new() if self.new_button.isVisible() else None
        )
        self.delete_shortcut = QShortcut(QKeySequence("Alt+D"), self)
        self.delete_shortcut.activated.connect(
            lambda: self.on_delete() if self.delete_button.isVisible() else None
        )
        self.save_shortcut = QShortcut(QKeySequence("Alt+S"), self)
        self.save_shortcut.activated.connect(
            lambda: self.on_save() if self.save_button.isVisible() else None
        )

        # Update/Edit button shortcut (Alt+U) - triggers action like delete button
        self.edit_shortcut = QShortcut(QKeySequence("Alt+U"), self)
        self.edit_shortcut.activated.connect(
            lambda: self.on_edit_mode() if self.edit_button.isVisible() else None
        )

        # Escape key for cancel functionality
        self.escape_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.escape_shortcut.activated.connect(self.on_cancel_edit)

        # Alt+/ remains local for status bar read
        self.status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.status_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.status_shortcut.activated.connect(self.on_read_status_bar)

        # PageUp/PageDown for navigation (like import_detail_window)
        self.prev_shortcut = QShortcut(QKeySequence(Qt.Key_PageUp), self)
        self.prev_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.prev_shortcut.activated.connect(self.on_prev)

        self.next_shortcut = QShortcut(QKeySequence(Qt.Key_PageDown), self)
        self.next_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.next_shortcut.activated.connect(self.on_next)

    def reject(self):
        """
        Override reject to close dialog directly.
        Escape key handles save changes dialog.
        """
        # PHASE 2 OPTIMIZATION: Clean up event filters to prevent accumulation
        self._cleanup_event_filters()

        announce_dialog_closed(self)

        super().reject()

    def _cleanup_event_filters(self):
        """Remove event filters from all child widgets to prevent accumulation."""
        for widget in self.findChildren(QObject):
            try:
                widget.removeEventFilter(self)
            except:
                pass  # Some widgets may not have our filter

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
            self.time_edit: "Time",
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
        self.title_edit.textChanged.connect(lambda: self._mark_dirty(self.title_edit))
        self.reader_edit.textChanged.connect(lambda: self._mark_dirty(self.reader_edit))
        self.time_edit.textChanged.connect(lambda: self._mark_dirty(self.time_edit))
        self.comments_edit.textChanged.connect(
            lambda: self._mark_dirty(self.comments_edit)
        )
        self.files_edit.textChanged.connect(lambda: self._mark_dirty(self.files_edit))
        self.bitrate_edit.textChanged.connect(
            lambda: self._mark_dirty(self.bitrate_edit)
        )
        self.size_edit.textChanged.connect(lambda: self._mark_dirty(self.size_edit))
        self.format_combo.currentIndexChanged.connect(
            lambda: self._mark_dirty(self.format_combo)
        )
        self.path_edit.textChanged.connect(lambda: self._mark_dirty(self.path_edit))

        # Combos
        self.author_combo.currentIndexChanged.connect(
            lambda: self._mark_dirty(self.author_combo)
        )
        self.author_combo.editTextChanged.connect(
            lambda: self._mark_dirty(self.author_combo)
        )
        self.series_combo.currentIndexChanged.connect(
            lambda: self._mark_dirty(self.series_combo)
        )
        self.series_combo.editTextChanged.connect(
            lambda: self._mark_dirty(self.series_combo)
        )
        self.genre_combo.currentIndexChanged.connect(
            lambda: self._mark_dirty(self.genre_combo)
        )
        self.genre_combo.editTextChanged.connect(
            lambda: self._mark_dirty(self.genre_combo)
        )
        self.collection_combo.currentIndexChanged.connect(
            lambda: self._mark_dirty(self.collection_combo)
        )

        # Spinbox and date
        self.year_spin.valueChanged.connect(lambda: self._mark_dirty(self.year_spin))
        self.read_date.dateChanged.connect(lambda: self._mark_dirty(self.read_date))

    def _mark_dirty(self, widget=None):
        """bd#6: Mark form as having unsaved changes."""
        if getattr(self, "_loading_fields", False):
            return
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

        for combo in [
            self.author_combo,
            self.series_combo,
            self.genre_combo,
            self.collection_combo,
        ]:
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
        self.set_status(self._idle_status_message(), announce=announce)

    def _update_save_button_visibility(self):
        """
        bd#6: Show save button only when there are unsaved changes.
        For new books, always show save button, hide Update button.
        For existing books in view mode, show Update button.
        In edit mode, hide Update button.
        """
        if self._in_edit_mode:
            self.new_button.setVisible(False)
            self.delete_button.setVisible(False)
            self.save_button.setVisible(True)
            self.edit_button.setVisible(False)
            self.get_web_details_button.setVisible(False)
            return

        save_active = self._dirty or self.is_new
        self.new_button.setVisible(not save_active)
        self.delete_button.setVisible((not self.is_new) and (not save_active))
        self.save_button.setVisible(save_active)
        # Get Web Info: show for existing books, hide for new books and in edit mode
        self.get_web_details_button.setVisible(not self.is_new and not save_active)
        # Update button: hide for new books, hide in edit mode, show in view mode for existing
        self.edit_button.setVisible(not self.is_new and not save_active)

    def on_show_shortcuts(self):
        """Show keyboard shortcuts help dialog."""
        from src.accessibility.shortcuts import BOOK_DETAILS_SHORTCUTS
        from src.accessibility.shortcut_helpers import (
            get_accessible_shortcuts_list,
            build_accessible_f1_popup_style,
        )

        dlg = AccessibleDialog(self)
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
        table.setStyleSheet(build_accessible_f1_popup_style())
        # Build shortcut list from centralized mapping
        shortcut_keys = [
            ("Alt+" + k, desc)
            for k, (desc, _) in BOOK_DETAILS_SHORTCUTS.items()
            if k != "F1"
        ]
        # Add local button shortcuts and status read (not in centralized mapping)
        shortcut_keys.extend(
            [
                ("Alt+N", "New book"),
                ("Alt+D", "Delete book"),
                ("Alt+/", "Read status bar"),
            ]
        )
        shortcut_keys.append(("F1", "Show keyboard shortcuts"))
        shortcut_keys = get_accessible_shortcuts_list(shortcut_keys)
        table.setRowCount(len(shortcut_keys))
        table.setVerticalHeaderLabels([""] * len(shortcut_keys))
        for row, (key, desc) in enumerate(shortcut_keys):
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
        """Load combo box data and build lookup indexes for fast access."""
        # PHASE 2 OPTIMIZATION: Build id->index lookup dicts to avoid slow findData()
        self._author_index_map: Dict[int, int] = {}
        self._series_index_map: Dict[int, int] = {}
        self._genre_index_map: Dict[int, int] = {}
        self._collection_index_map: Dict[int, int] = {}

        # Authors
        self.author_combo.blockSignals(True)
        self.author_combo.clear()
        authors = self.author_queries.get_all()
        for idx, author in enumerate(authors):
            self.author_combo.addItem(author.name, author.author_id)
            self._author_index_map[author.author_id] = idx
        self.author_combo.setMaxVisibleItems(20)  # Limit dropdown size
        self.author_combo.blockSignals(False)

        # Series
        self.series_combo.blockSignals(True)
        self.series_combo.clear()
        series_list = self.series_queries.get_all()
        for idx, series in enumerate(series_list):
            self.series_combo.addItem(series.name, series.series_id)
            self._series_index_map[series.series_id] = idx
        self.series_combo.setMaxVisibleItems(20)
        self.series_combo.blockSignals(False)

        # Genres
        self.genre_combo.blockSignals(True)
        self.genre_combo.clear()
        genres = self.genre_queries.get_all()
        for idx, genre in enumerate(genres):
            self.genre_combo.addItem(genre.name, genre.genre_id)
            self._genre_index_map[genre.genre_id] = idx
        self.genre_combo.setMaxVisibleItems(20)
        self.genre_combo.blockSignals(False)

        # Collections
        self.collection_combo.blockSignals(True)
        self.collection_combo.clear()
        collections = self.collection_queries.get_all()
        for idx, coll in enumerate(collections):
            self.collection_combo.addItem(coll.name, coll.collection_id)
            self._collection_index_map[coll.collection_id] = idx
        self.collection_combo.setMaxVisibleItems(20)
        self.collection_combo.blockSignals(False)

    def load_book_data(self):
        """Load book data into form, suppressing dirty tracking."""
        self._loading_fields = True
        try:
            self.title_edit.setText(self.book.title)
            # View mode: set label text instead of loading combos (fast!)
            self.author_label_display.setText(self.book.author_name or "")
            if self.book.year:
                self.year_spin.setValue(self.book.year)
            else:
                self.year_spin.setValue(self.year_spin.minimum())
            # View mode: set label text instead of loading combos
            self.series_label_display.setText(self.book.series_name or "")
            self.genre_label_display.setText(self.book.genre_name or "")
            self.reader_edit.setText(self.book.reader or "")
            if self.is_new:
                if self.current_collection_id is not None:
                    coll_name = self.collection_queries.get_by_id(self.current_collection_id)
                    self.collection_label_display.setText(coll_name.name if coll_name else "")
                else:
                    self.collection_label_display.setText("")
            else:
                self.collection_label_display.setText(self.book.collection_name or "")
            self.time_edit.setText(self.book.time_display)
            self.files_edit.setText(str(self.book.tracks) if self.book.tracks else "")
            self.size_edit.setText(self.book.size_display if self.book.size_mb else "")
            self.bitrate_edit.setText(
                str(self.book.bitrate) if self.book.bitrate else ""
            )
            format_value = (self.book.file_format or "").lower()
            if format_value:
                idx = self.format_combo.findData(format_value)
                if idx >= 0:
                    self.format_combo.setCurrentIndex(idx)
                else:
                    self.format_combo.setCurrentIndex(-1)
            else:
                self.format_combo.setCurrentIndex(-1)
            self.path_edit.setText(self.book.path or "")
            self.source_edit.setText(self.book.source or "")
            if self.book.date_added:
                if isinstance(self.book.date_added, str):
                    self.added_edit.setText(self.book.date_added[:10])
                else:
                    self.added_edit.setText(self.book.date_added.strftime("%Y-%m-%d"))
            else:
                self.added_edit.setText("")
            set_navigable_plain_text(self.comments_edit, self.book.comments or "")
            self.plot_review.set_plot_text(self.book.comments or "")
            if self.book.read_date:
                read_date_value = self.book.read_date
                if isinstance(read_date_value, str):
                    try:
                        read_date_value = datetime.strptime(
                            read_date_value, "%Y-%m-%d"
                        ).date()
                    except ValueError:
                        read_date_value = None
                if read_date_value:
                    qdate = QDate(
                        read_date_value.year, read_date_value.month, read_date_value.day
                    )
                    self.read_date.setDate(qdate)
                else:
                    self.read_date.setDate(self._null_read_date)
            else:
                self.read_date.setDate(self._null_read_date)
            # Store original values from book for change tracking
            self._original_author = self.book.author_name or ""
            self._original_series = self.book.series_name or ""
            self._original_genre = self.book.genre_name or ""
        finally:
            self._loading_fields = False

    def _check_combo_change(
        self, field_name: str, combo: QComboBox, original_value: str, query_obj
    ):
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
        msg = (
            f"'{current_text}' is a new {field_name}.\n\nCreate this new {field_name}?"
        )
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
        """Save book data with mandatory sanitization (title, author, genre, series, reader)."""
        if self.time_edit.hasFocus():
            self._normalize_time_on_focus_out()

        from src.core.validator import ImportValidator

        validator = ImportValidator()
        # Collect all editable fields to sanitize
        book_dict = {
            "title": self.title_edit.text(),
            "author": self.author_combo.currentText(),
            "series": self.series_combo.currentText(),
            "genre": self.genre_combo.currentText(),
            "reader": self.reader_edit.text(),
        }
        # Sanitize all fields (ignore C: flags, silent correction)
        for field in ["title", "author", "series", "genre", "reader"]:
            temp = {field: book_dict[field]}
            validator.sanitize_metadata(temp)
            book_dict[field] = temp[field]
        # Ensure author field is sanitized even if user did not leave the field
        temp = {"author": book_dict["author"]}
        validator.sanitize_metadata(temp)
        book_dict["author"] = temp["author"]
        # Update UI fields with sanitized values
        self._loading_fields = True
        try:
            self.title_edit.setText(book_dict["title"])
            self.author_combo.setEditText(book_dict["author"])
            self.series_combo.setEditText(book_dict["series"])
            self.genre_combo.setEditText(book_dict["genre"])
            self.reader_edit.setText(book_dict["reader"])
        finally:
            self._loading_fields = False

        # Validate
        if not book_dict["title"]:
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
        if not book_dict["author"]:
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
        author_id = self.author_queries.get_or_create(book_dict["author"])
        # Get or create series
        series_id = None
        if book_dict["series"]:
            series_id = self.series_queries.get_or_create(book_dict["series"])
        # Get or create genre
        genre_id = None
        if book_dict["genre"]:
            genre_id = self.genre_queries.get_or_create(book_dict["genre"])
        reader_text = book_dict["reader"]
        # Get collection
        collection_id = self.collection_combo.currentData()
        if collection_id is None:
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(14),
                icon=QMessageBox.Warning,
                title="Missing Collection",
                text="Please select a collection before saving.",
            )
            self.collection_combo.setFocus()
            return
        self.book.collection_id = collection_id

        # Parse time with normalization
        time_text = self.time_edit.text().strip()
        time_hours = 0
        time_minutes = 0
        if time_text:
            normalized_time = self._normalize_time_text(time_text)
            if normalized_time:
                try:
                    parts = normalized_time.split(":")
                    time_hours = int(parts[0])
                    time_minutes = int(parts[1])
                except (ValueError, IndexError):
                    pass

        # Get read date
        read_date = None
        if self.read_date.date() != self._null_read_date:
            qdate = self.read_date.date()
            read_date = datetime(qdate.year(), qdate.month(), qdate.day()).date()

        year_value = self.year_spin.value()
        year_value = None if year_value == self.year_spin.minimum() else year_value

        # Removed legacy normalization methods (_to_proper_case, _is_proper_case_enabled, _normalize_name_field)
        self.book.year = year_value
        self.book.title = book_dict["title"]
        self.book.author_name = book_dict["author"]
        self.book.author_id = author_id
        self.book.series_id = series_id
        self.book.genre_id = genre_id
        self.book.collection_id = collection_id
        self.book.reader = reader_text
        self.book.time_hours = time_hours
        self.book.time_minutes = time_minutes
        # The following assignments must come after tracks, size_mb, bitrate, file_format, source_text, path_text are defined
        # (moved below after those variables are set)

        # Parse files, bitrate, size, format, source, path
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

            self._data_was_changed = True

            # Clear dirty and update original values (don't close window)
            self._clear_dirty(preserve_status=True)
            self._original_author = self.author_combo.currentText()
            self._original_series = self.series_combo.currentText()
            self._original_genre = self.genre_combo.currentText()
            self.setWindowTitle("Book Details")

            # Switch back to view mode (hide combos, show labels)
            self._show_view_labels()
            # Update labels with saved values
            self.author_label_display.setText(self.author_combo.currentText())
            self.series_label_display.setText(self.series_combo.currentText())
            self.genre_label_display.setText(self.genre_combo.currentText())
            self.collection_label_display.setText(self.collection_combo.currentText())
            # Show edit button, hide save button
            self._clear_dirty()  # Clears dirty state and updates button visibility

            QTimer.singleShot(0, self.title_edit.setFocus)

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
        """Delete book, with confirmation dialog using standardized message box."""
        if not self.book or not self.book.book_id:
            return

        # Prepare accessible title/author for dialogs
        book_title = self.book.title or "(Untitled)"
        # Prefer denormalized author_name, fallback to author_id if needed
        author_name = getattr(self.book, "author_name", None) or ""
        if not author_name and hasattr(self, "author_combo"):
            author_name = self.author_combo.currentText().strip() or "(Unknown author)"
        if not author_name:
            author_name = "(Unknown author)"

        # Confirm delete using standardized message box
        confirm_text = (
            f"Are you sure you want to delete this book?\n\n"
            f"Title: {book_title}\nAuthor: {author_name}"
        )
        reply = exec_styled_message_box(
            self,
            self.scaler.get_scaled_size(20),
            icon=QMessageBox.Question,
            title="Confirm Delete",
            text=confirm_text,
            buttons=QMessageBox.Yes | QMessageBox.No,
            default_button=QMessageBox.No,
            button_icon_roles=MESSAGE_BOX_DELETE_CONFIRM_ICONS,
        )
        if reply != QMessageBox.Yes:
            self.set_status("Delete canceled.")
            return
        try:
            deleted_index = self.current_index
            self.book_queries.delete(self.book.book_id)
            self._data_was_changed = True

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
                        text=f"Book deleted. No more books.\n\nTitle: {book_title}\nAuthor: {author_name}",
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
                exec_styled_message_box(
                    self,
                    self.scaler.get_scaled_size(20),
                    icon=QMessageBox.Information,
                    title="Success",
                    text=f"Book deleted successfully!\n\nTitle: {book_title}\nAuthor: {author_name}",
                )
                self.set_status("Book deleted successfully")
                QTimer.singleShot(0, self.title_edit.setFocus)
            else:
                exec_styled_message_box(
                    self,
                    self.scaler.get_scaled_size(20),
                    icon=QMessageBox.Information,
                    title="Success",
                    text=f"Book deleted successfully!\n\nTitle: {book_title}\nAuthor: {author_name}",
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

        # Load combos and switch to edit mode (show combos, hide labels)
        self.load_combos()
        self._hide_view_labels()

        # Clear form fields
        self._reset_new_fields()

        # Update window title
        self.setWindowTitle("New Book")

        # Update button states
        self.delete_button.setVisible(False)
        self._update_save_button_visibility()  # bd#6: Show save for new book

        # Focus title field
        self.title_edit.setFocus()
        self.set_status("")

    def on_edit_mode(self):
        """
        Switch from view mode to edit mode.
        Loads combo boxes and shows them for editing.
        """
        # Load combo data (this is the slow part - only done when needed)
        self.load_combos()

        # Switch from labels to combos and unlock all fields
        self._in_edit_mode = True
        self._hide_view_labels()

        # Now set combo values using the fast index maps
        # PHASE 2 OPTIMIZATION: Block signals to prevent slow event cascades
        self._loading_fields = True
        try:
            self.author_combo.blockSignals(True)
            idx = self._author_index_map.get(self.book.author_id, -1)
            if idx >= 0:
                self.author_combo.setCurrentIndex(idx)
            self.author_combo.blockSignals(False)

            self.series_combo.blockSignals(True)
            if self.book.series_id:
                idx = self._series_index_map.get(self.book.series_id, -1)
                if idx >= 0:
                    self.series_combo.setCurrentIndex(idx)
            else:
                self.series_combo.setCurrentIndex(-1)
                self.series_combo.clearEditText()
            self.series_combo.blockSignals(False)

            self.genre_combo.blockSignals(True)
            if self.book.genre_id:
                idx = self._genre_index_map.get(self.book.genre_id, -1)
                if idx >= 0:
                    self.genre_combo.setCurrentIndex(idx)
            else:
                self.genre_combo.setCurrentIndex(-1)
                self.genre_combo.clearEditText()
            self.genre_combo.blockSignals(False)

            self.collection_combo.blockSignals(True)
            if self.book.collection_id:
                idx = self._collection_index_map.get(self.book.collection_id, -1)
                if idx >= 0:
                    self.collection_combo.setCurrentIndex(idx)
            else:
                self.collection_combo.setCurrentIndex(-1)
            self.collection_combo.blockSignals(False)
        finally:
            self._loading_fields = False

        # Hide edit button in edit mode, show save instead
        self.new_button.setVisible(False)
        self.delete_button.setVisible(False)
        self.edit_button.setVisible(False)
        self.save_button.setVisible(True)
        self.get_web_details_button.setVisible(False)

        # Focus the title field (most logical starting point for editing)
        self.title_edit.setFocus()

    def _show_view_labels(self):
        """Show view labels and hide combos for fast display mode."""
        self.author_field_stack.setCurrentWidget(self.author_label_display)
        self.series_field_stack.setCurrentWidget(self.series_label_display)
        self.genre_field_stack.setCurrentWidget(self.genre_label_display)
        self.collection_field_stack.setCurrentWidget(self.collection_label_display)
        self._in_edit_mode = False
        # Make other fields read-only in view mode
        self._set_fields_read_only(True)

    def _hide_view_labels(self):
        """Hide view labels and show combos for edit mode."""
        self.author_field_stack.setCurrentWidget(self.author_combo)
        self.series_field_stack.setCurrentWidget(self.series_combo)
        self.genre_field_stack.setCurrentWidget(self.genre_combo)
        self.collection_field_stack.setCurrentWidget(self.collection_combo)
        # Make other fields editable in edit mode
        self._set_fields_read_only(False)

    def _set_fields_read_only(self, read_only: bool):
        """Set all non-combo fields to read-only or editable."""
        # Title
        self.title_edit.setReadOnly(read_only)
        # Plot/Comments
        self.comments_edit.setReadOnly(read_only)
        if read_only:
            restored_plot = format_plot_text_for_navigation(self.comments_edit.toPlainText())
            self.comments_edit.setPlainText(restored_plot)
            self.plot_review.set_plot_text(restored_plot)
            self.plot_stack.setCurrentWidget(self.plot_review)
            self.plot_stack.setFocusProxy(self.plot_review)
        else:
            self.plot_stack.setCurrentWidget(self.comments_edit)
            self.plot_stack.setFocusProxy(self.comments_edit)
        # Year
        self.year_spin.setReadOnly(read_only)
        # Time
        self.time_edit.setReadOnly(read_only)
        # Reader
        self.reader_edit.setReadOnly(read_only)
        # Read date
        self.read_date.setReadOnly(read_only)
        # Files
        self.files_edit.setReadOnly(read_only)
        # Bitrate
        self.bitrate_edit.setReadOnly(read_only)
        # Size
        self.size_edit.setReadOnly(read_only)
        # Format
        self.format_combo.setEnabled(True)
        # Path
        self.path_edit.setReadOnly(read_only)
        # Source
        self.source_edit.setReadOnly(read_only)
        # Added date
        self.added_edit.setReadOnly(read_only)

    def _focus_plot(self):
        """Focus plot line list in view mode or editor in edit mode."""
        if self.plot_stack.currentWidget() is self.plot_review:
            self.plot_review.setFocus()
        else:
            self.comments_edit.setFocus()

    def _focus_author(self):
        """Focus author - view label in view mode, combo in edit mode."""
        if self.author_label_display.isVisible():
            self.author_label_display.setFocus()
        else:
            self.author_combo.setFocus()

    def _focus_series(self):
        """Focus series - view label in view mode, combo in edit mode."""
        if self.series_label_display.isVisible():
            self.series_label_display.setFocus()
        else:
            self.series_combo.setFocus()

    def _focus_genre(self):
        """Focus genre - view label in view mode, combo in edit mode."""
        if self.genre_label_display.isVisible():
            self.genre_label_display.setFocus()
        else:
            self.genre_combo.setFocus()

    def _focus_collection(self):
        """Focus collection - view label in view mode, combo in edit mode."""
        if self.collection_label_display.isVisible():
            self.collection_label_display.setFocus()
        else:
            self.collection_combo.setFocus()

    def _apply_new_defaults(self):
        """Apply defaults for new entries without auto-selecting choices."""
        # Only set source field here; collection logic moved to _reset_new_fields
        if not self.source_edit.text().strip():
            self.source_edit.setText(getpass.getuser())

    def _reset_new_fields(self):
        """Reset all editable fields for a new book without prepopulation, suppressing dirty tracking."""
        self._loading_fields = True
        try:
            self.title_edit.clear()
            # Clear view labels (QLineEdit widgets)
            self.author_label_display.clear()
            self.series_label_display.clear()
            self.genre_label_display.clear()
            self.collection_label_display.clear()
            # Clear combos
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
            self.plot_review.clear()
            self.read_date.setDate(self._null_read_date)
            if self.current_collection_id is not None:
                idx = self.collection_combo.findData(self.current_collection_id)
                if idx >= 0:
                    self.collection_combo.setCurrentIndex(idx)
                else:
                    self.collection_combo.setCurrentIndex(-1)
            else:
                if self.collection_combo.count() == 1:
                    self.collection_combo.setCurrentIndex(0)
                else:
                    self.collection_combo.setCurrentIndex(-1)
            self._apply_new_defaults()
            self.reader_edit.setText("")
        finally:
            self._loading_fields = False

    def on_get_web_details(self):
        """Open web book details window to fetch and review web metadata."""
        from PySide6.QtCore import QTimer
        from src.ui.web_fetch_progress import WebFetchProgressDialog

        popup = WebFetchProgressDialog(self)
        popup.show()
        QApplication.processEvents()
        if not self.book:
            popup.close()
            self.set_status("No book selected for web lookup")
            return
        try:
            from src.ui.web_metadata import WebMetadataWindow
            from src.web.web_book_api import WebBookAPI
            from PySide6.QtCore import QSettings

            # Get book data for search
            title = self.book.title
            author = self.book.author_name
            year = str(self.book.year) if self.book.year else None

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

            # Try to fetch web data once. WebBookAPI cascades Open Library ->
            # Google Books -> WikiData for refresh=0.
            api = WebBookAPI()
            web_data = None
            last_error = None

            try:
                web_data = api.get_book_metadata(
                    title,
                    author,
                    year,
                    refresh=0,
                    move_articles=move_articles,
                    flip_author=flip_author,
                    narrator=self.book.reader or "",
                    path=self.book.path or "",
                    source=self.book.source or "",
                    comments=self.book.comments or "",
                    progress_callback=popup.update_message,
                )
            except Exception as e:
                last_error = str(e)
            finally:
                popup.close()

            from src.web.web_book_api import clean_web_data

            cleaned_web_data = (
                clean_web_data(web_data, move_articles, flip_author)
                if web_data and not web_data.get("_no_result")
                else None
            )
            if cleaned_web_data and WebMetadataWindow.web_data_offers_changes(
                self.book, cleaned_web_data
            ):
                web_window = WebMetadataWindow(
                    self.db,
                    self.book,
                    self.scaler,
                    self.theme_manager,
                    self,
                    refresh_callback=self.load_book_data,
                    web_data=web_data,
                )
                result = web_window.exec()
                if result == QDialog.Accepted:
                    self._data_was_changed = True
                    self.set_status(
                        "Web details applied successfully", announce=True
                    )
                    QTimer.singleShot(0, self._focus_plot)
            else:
                fetch_errors = (web_data or {}).get("_fetch_errors", [])
                if fetch_errors:
                    status_msg = "Web fetch failed: unable to reach web sources."
                    if fetch_errors:
                        status_msg = f"{status_msg} {fetch_errors[0]}"
                    no_web_text = (
                        "Unable to reach one or more web sources.\n\n"
                        + "\n".join(f"  \u2022 {e}" for e in fetch_errors[:3])
                    )
                elif cleaned_web_data:
                    status_msg = "No new web information found for this book."
                    no_web_text = (
                        "Web sources were searched but no new information was found "
                        "for this book. Existing metadata is already up to date."
                    )
                elif last_error:
                    status_msg = f"No web data found for this book. {last_error}"
                    no_web_text = (
                        f"No information found for this book in any web source.\n\n"
                        f"Last error: {last_error}"
                    )
                else:
                    status_msg = "No web data found for this book."
                    no_web_text = (
                        "No information found for this book in any web source."
                    )
                self.set_status(status_msg, announce=True)
                exec_styled_message_box(
                    self,
                    self.scaler.get_scaled_size(20),
                    icon=QMessageBox.Information,
                    title="No Web Data Found",
                    text=no_web_text,
                )
                QTimer.singleShot(0, self.title_edit.setFocus)
        except Exception as e:
            import traceback

            traceback.print_exc()
            self.set_status(f"Error opening web details: {str(e)}")

    def _focus_first_dirty_field(self):
        """Focus the first dirty field if any, else title_edit."""
        if self._first_dirty_widget:
            self._first_dirty_widget.setFocus()
        else:
            self.title_edit.setFocus()

    def _confirm_save_or_cancel(self, nav_callback):
        """Show unsaved changes popup for navigation. If Yes, save and navigate; if No, stay and focus dirty field."""
        from src.accessibility.icon_helper import get_app_icon

        msg_text = (
            "You have unsaved changes.\n\n"
            "Yes = Save and continue\n"
            "No = Stay and continue editing"
        )
        reply = exec_styled_message_box(
            self,
            self.scaler.get_scaled_size(20),
            icon=QMessageBox.Question,
            title="Unsaved Changes",
            text=msg_text,
            buttons=QMessageBox.Yes | QMessageBox.No,
            default_button=QMessageBox.No,
            button_texts={QMessageBox.Yes: "&Yes", QMessageBox.No: "&No"},
            window_icon=get_app_icon(),
            button_icon_roles=MESSAGE_BOX_UNSAVED_TWO_ICONS,
        )
        if reply == QMessageBox.Yes:
            self.on_save()
            nav_callback()
        else:
            self._focus_first_dirty_field()

    def on_prev(self):
        """Navigate to previous book in the list, with dirty check and popup."""

        def do_nav():
            if self.books_list and self.current_index > 0:
                self._blur_title_before_navigation_load()
                self.current_index -= 1
                self.book = self.books_list[self.current_index]
                self.is_new = False
                self.load_book_data()
                self._clear_dirty(preserve_status=True)
                self.update_navigation_state()
                self._focus_title_after_navigation()

        if self._dirty:
            self._confirm_save_or_cancel(do_nav)
        else:
            do_nav()

    def on_next(self):
        """Navigate to next book in the list, with dirty check and popup."""

        def do_nav():
            if self.books_list and self.current_index < len(self.books_list) - 1:
                self._blur_title_before_navigation_load()
                self.current_index += 1
                self.book = self.books_list[self.current_index]
                self.is_new = False
                self.load_book_data()
                self._clear_dirty(preserve_status=True)
                self.update_navigation_state()
                self._focus_title_after_navigation()

        if self._dirty:
            self._confirm_save_or_cancel(do_nav)
        else:
            do_nav()

    def update_navigation_state(self):
        """Update button states based on current position."""
        self.delete_button.setVisible(not self.is_new)
