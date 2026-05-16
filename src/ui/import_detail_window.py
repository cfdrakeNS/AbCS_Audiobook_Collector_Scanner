"""
Import Detail Window
Form for viewing and editing scanned audiobook details before import.
"""

import re
import os

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QPushButton,
    QLabel,
    QSpinBox,
    QMessageBox,
    QApplication,
    QTextEdit,
    QAbstractSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QStatusBar,
)
from PySide6.QtCore import Qt, QEvent, QTimer, QSettings
from PySide6.QtGui import QShortcut, QKeySequence, QAccessible

from src.core.validator import ImportValidator
from src.database import (
    DatabaseManager,
    AuthorQueries,
    SeriesQueries,
    GenreQueries,
    CollectionQueries,
)
from src.accessibility.scaling import UIScaler
from src.accessibility.style_helpers import (
    build_accessible_message_box_style,
    exec_styled_message_box,
)
from src.accessibility.theme_manager import ThemeManager
from src.accessibility.key_filters import is_unmapped_alt_letter
from src.accessibility.accessible_events import (
    announce_status_message,
    announce_dialog_opened,
    announce_dialog_closed,
)


class ImportDetailWindow(QDialog):
    def _focus_first_dirty_field(self):
        """Focus the first field that was changed (for accessibility)."""
        if self._first_dirty_widget:
            QTimer.singleShot(0, self._first_dirty_widget.setFocus)
        else:
            QTimer.singleShot(0, self.title_edit.setFocus)

    def _confirm_save_or_cancel(self, nav_callback):
        """Show unsaved changes popup for navigation. If Yes, save and navigate; if No, stay and focus dirty field."""
        from src.accessibility.icon_helper import get_app_icon

        book_title = getattr(self, "title_edit", None)
        book_author = getattr(self, "author_combo", None)
        title_val = book_title.text().strip() if book_title else "(Untitled)"
        author_val = (
            book_author.currentText().strip() if book_author else "(Unknown author)"
        )
        msg_text = (
            f"You have unsaved changes for '{title_val}' by {author_val}.\n\n"
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
        )
        if reply == QMessageBox.Yes:
            if self.on_save():
                nav_callback()
        else:
            self._focus_first_dirty_field()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from src.accessibility.icon_helper import get_app_icon

        self.setWindowIcon(get_app_icon())

    """
    Import detail dialog for viewing and editing scanned audiobook metadata.
    """

    RESULT_PREV = 2
    RESULT_NEXT = 3
    RESULT_SKIP = 4
    MIN_VALID_YEAR = 1900
    MAX_VALID_YEAR = 2100
    # Centralized Alt+letter shortcut mapping (parity with BookDetailsWindow)
    ALLOWED_ALT_LETTERS = {
        "A",  # Author
        "B",  # Bitrate
        "C",  # Collection
        "D",  # Discard (Skip)
        "E",  # Errors
        "F",  # Files
        "G",  # Genre
        "H",  # Path (Pat&h)
        "I",  # Series (Ser&ies)
        "M",  # Length (Length (&M))
        "O",  # Comments (C&omments)
        "R",  # Reader
        "S",  # Save
        "T",  # Title
        "Y",  # Year
        "Z",  # Size (Si&ze)
        # Add any additional used keys here
    }

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
        theme_manager: ThemeManager,
        book_data: dict = None,
        errors: list = None,
        current_index: int = 0,
        total_count: int = 0,
        is_duplicate: bool = False,
        parent=None,
    ):
        """
        Initialize import detail window.

        Args:
            db: Database manager
            scaler: UI scaler
            theme_manager: Theme manager
            book_data: Scanned book data dictionary
            errors: List of validation error messages
            parent: Parent widget
        """
        super().__init__(parent)
        self.setAttribute(Qt.WA_NativeWindow, True)
        self.setWindowModality(Qt.ApplicationModal)
        self.winId()

        self.db = db
        self.scaler = scaler
        self.theme_manager = theme_manager
        self.book_data = book_data or {}
        self.errors = errors or []
        self.current_index = current_index
        self.total_count = total_count
        self.is_duplicate_item = bool(is_duplicate)
        self._dirty = False
        self._first_dirty_widget = None
        self._pending_dirty_widgets = set()
        self._default_status_message = "Ready"
        self._closing_via_handler = False
        self._original_author = ""
        self._original_series = ""
        self._original_genre = ""

        # Query objects
        self.author_queries = AuthorQueries(db)
        self.series_queries = SeriesQueries(db)
        self.genre_queries = GenreQueries(db)
        self.collection_queries = CollectionQueries(db)

        # Setup UI
        self.setup_ui()
        self.apply_control_styles()
        self.install_focus_filters()
        self.load_combos()
        self.load_book_data()
        self._setup_dirty_tracking()
        self._apply_duplicate_read_only_state()

        # Window settings
        title = self._detail_window_title(self.book_data, self.errors)
        self.setWindowTitle(title)
        self.setAccessibleName(title)
        self.setAccessibleDescription(
            "Form for viewing and editing scanned audiobook details"
        )
        self.resize(880, 500)

        announce_dialog_opened(self, title)
        self.set_status("Ready")

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

    def set_status(self, message: str, announce: bool = False):
        """Set status message on this dialog and mirror to parent import window."""
        self._default_status_message = message

        if hasattr(self, "status_bar") and self.status_bar is not None:
            announce_status_message(self.status_bar, message, move_focus=announce)

        parent = self.parent()
        if parent and hasattr(parent, "set_status"):
            parent.set_status(message, announce=False)
        elif parent and hasattr(parent, "status_bar"):
            announce_status_message(parent.status_bar, message, move_focus=False)

    def get_status_summary(self) -> str:
        """Return a concise current-status summary for Alt+/ reading."""
        parent = self.parent()
        if parent and hasattr(parent, "status_bar"):
            parent_status = parent.status_bar.currentMessage().strip()
            if parent_status:
                return parent_status

        title = self.title_edit.text().strip() or "Untitled"
        author = self.author_combo.currentText().strip() or "Unknown author"
        errors_count = len(self.errors)
        if errors_count:
            return f"Import detail: {title} by {author}. {errors_count} errors."
        if self._default_status_message:
            return self._default_status_message
        return f"Import detail: {title} by {author}. No errors."

    def _get_import_list_valid_count(self) -> int:
        """Return current valid-books count from parent Import Window when available."""
        parent = self.parent()
        if parent and hasattr(parent, "_summary_counts"):
            summary = getattr(parent, "_summary_counts", {}) or {}
            try:
                summary_valid = int(summary.get("valid", 0))
                if summary_valid:
                    return summary_valid
            except (TypeError, ValueError):
                pass

        if parent and hasattr(parent, "scanned_items"):
            valid_count = 0
            for item in getattr(parent, "scanned_items", []) or []:
                status = str(item.get("status", "")).strip()
                if status in ("OK", "Warning"):
                    valid_count += 1
            return valid_count
        return 0

    def _build_exit_prompt_text(self) -> str:
        """Build close-confirmation message including import-list context."""
        valid_count = self._get_import_list_valid_count()
        parent = self.parent()
        parent_message = ""
        if parent and hasattr(parent, "_default_status_message"):
            parent_message = str(
                getattr(parent, "_default_status_message", "") or ""
            ).strip()

        current_message = parent_message or self.get_status_summary().strip() or "Ready"
        return (
            "Import details changed.\n\n"
            f"Valid books in Import list: {valid_count}\n"
            f"Current message: {current_message}\n\n"
            "Yes = Save and close\n"
            "No = Continue editing\n"
            "Cancel = Discard and close"
        )

    def on_read_status_bar(self):
        """Read current status (Alt+/)."""
        status_text = self.get_status_summary()
        if QAccessible.isActive():
            self.set_status(status_text, announce=True)
        # else: do nothing (no popup)

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
            # Show save changes dialog like book_details
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
                "Cancel = Discard and close"
            )
            msg = QMessageBox(self)
            msg.setWindowTitle("Unsaved Changes")
            msg.setStyleSheet(
                build_accessible_message_box_style(self.scaler.get_scaled_size(20))
            )
            msg.setText(msg_text)
            msg.setStandardButtons(
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            msg.button(QMessageBox.Yes).setText("&Yes")
            msg.button(QMessageBox.No).setText("&No")
            msg.button(QMessageBox.Cancel).setText("&Cancel")
            reply = msg.exec()

            if reply == QMessageBox.Yes:
                self.accept()
                return

            if reply == QMessageBox.No:
                self.set_status("Continue editing")
                if combo_to_restore:
                    QTimer.singleShot(0, combo_to_restore.setFocus)
                return

            if reply == QMessageBox.Cancel:
                self._clear_dirty()
                self.set_status("Canceled: changes discarded, window closed.")
                self.reject()
                return

            self.set_status("Continue editing")
            if combo_to_restore:
                QTimer.singleShot(0, combo_to_restore.setFocus)
            return

        self.reject()
        if combo_to_restore:
            QTimer.singleShot(0, combo_to_restore.setFocus)

    def install_focus_filters(self):
        """
        Install event filters on editable fields to prevent auto-select on focus.
        """
        for widget in self.findChildren(QLineEdit):
            widget.installEventFilter(self)
        for widget in self.findChildren(QTextEdit):
            widget.installEventFilter(self)
        for widget in self.findChildren(QComboBox):
            widget.installEventFilter(self)
        for widget in self.findChildren(QSpinBox):
            widget.installEventFilter(self)

    def eventFilter(self, source, event):
        """
        Event filter to handle focus events on form fields.
        """
        # Block unused Alt+letter keys everywhere
        if event.type() == QEvent.KeyPress:
            key = event.key()
            modifiers = event.modifiers()
            if is_unmapped_alt_letter(event, self.ALLOWED_ALT_LETTERS):
                QApplication.beep()
                return True

            # Prevent mapped Alt+letter shortcuts from typing characters into
            # focused text controls (e.g., Alt+S should save only, not insert "s").
            if modifiers & Qt.AltModifier:
                alt_char = (event.text() or "").upper()
                if alt_char and alt_char in self.ALLOWED_ALT_LETTERS:
                    return True

            # Block plain Up/Down arrow keys on combo boxes - require Alt+Up/Down
            if isinstance(source, QComboBox):
                if key in (Qt.Key_Up, Qt.Key_Down):
                    if not (modifiers & Qt.AltModifier):
                        QApplication.beep()
                        return True

        if event.type() == QEvent.FocusIn:
            if isinstance(source, QLineEdit):
                QTimer.singleShot(0, lambda w=source: w.deselect())
            elif isinstance(source, QComboBox):
                if source.lineEdit():
                    QTimer.singleShot(
                        0,
                        lambda w=source: (
                            w.lineEdit().deselect() if w.lineEdit() else None
                        ),
                    )
            elif isinstance(source, QSpinBox):
                QTimer.singleShot(0, lambda w=source: w.lineEdit().deselect())

        # Check for FocusOut on relevant fields to sanitize input silently
        # Only sanitize if field has been modified (is dirty) - prevents unwanted prompts for save
        if event.type() == QEvent.FocusOut:
            from src.core.validator import ImportValidator

            validator = ImportValidator()
            dirty_widget = self._resolve_dirty_source(source)
            is_dirty = dirty_widget is not None

            # Title - only sanitize if dirty
            if source == getattr(self, "title_edit", None) and is_dirty:
                val = self.title_edit.text()
                temp = {"title": val}
                validator.sanitize_metadata(temp)
                if temp["title"] != val:
                    self.title_edit.setText(temp["title"])
            # Author - only sanitize if dirty
            if source == getattr(self, "author_combo", None) and is_dirty:
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
            if source == getattr(self, "series_combo", None) and is_dirty:
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
            if source == getattr(self, "genre_combo", None) and is_dirty:
                val = self.genre_combo.currentText()
                temp = {"genre": val}
                validator.sanitize_metadata(temp)
                if temp["genre"] != val:
                    self.genre_combo.setEditText(temp["genre"])
                self._check_combo_change(
                    "Genre",
                    self.genre_combo,
                    self._original_genre,
                    self.genre_queries,
                )
            # Reader - only sanitize if dirty
            if source == getattr(self, "reader_edit", None) and is_dirty:
                val = self.reader_edit.text()
                temp = {"reader": val}
                validator.sanitize_metadata(temp)
                if temp["reader"] != val:
                    self.reader_edit.setText(temp["reader"])

            # The combo _check_combo_change calls still need to happen for non-dirty fields
            # to handle auto-creation of new entries, but sanitization is skipped
            elif source == getattr(self, "author_combo", None):
                self._check_combo_change(
                    "Author",
                    self.author_combo,
                    self._original_author,
                    self.author_queries,
                )
            elif source == getattr(self, "series_combo", None):
                self._check_combo_change(
                    "Series",
                    self.series_combo,
                    self._original_series,
                    self.series_queries,
                )
            elif source == getattr(self, "genre_combo", None):
                self._check_combo_change(
                    "Genre",
                    self.genre_combo,
                    self._original_genre,
                    self.genre_queries,
                )

            if dirty_widget is not None:
                field_name = self._get_dirty_field_name(dirty_widget)
                # Only announce if value actually changed (existing logic)
                last_status = getattr(self, "_last_status_message", None)
                new_status = f"{field_name} changed."
                if last_status != new_status:
                    self.set_status(new_status, announce=True)
                    self._last_status_message = new_status
                self._pending_dirty_widgets.discard(dirty_widget)

        return super().eventFilter(source, event)

    def _resolve_dirty_source(self, source):
        """Resolve the actual widget that should be marked as dirty."""
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

    def _get_dirty_field_name(self, widget):
        """Get the field name for status announcements."""
        mapping = {
            self.title_edit: "Title",
            self.author_combo: "Author",
            self.comments_edit: "Plot",
            self.year_spin: "Year",
            self.time_edit: "Time",
            self.reader_edit: "Reader",
            self.series_combo: "Series",
            self.genre_combo: "Genre",
            self.collection_combo: "Collection",
            self.files_edit: "Files",
            self.bitrate_edit: "Bitrate",
            self.size_edit: "Size",
            self.format_edit: "Format",
            self.source_edit: "Source",
            self.path_edit: "Path",
            self.errors_edit: "Errors",
        }
        return mapping.get(widget, "Field")

    def _mark_dirty(self, widget=None):
        """Mark form as having unsaved changes."""
        if widget is not None:
            self._pending_dirty_widgets.add(widget)

        if not self._dirty:
            self._dirty = True
            if widget and not self._first_dirty_widget:
                self._first_dirty_widget = widget
            self._update_save_button_visibility()

    def _clear_dirty(self):
        """Clear dirty flag."""
        self._dirty = False
        self._first_dirty_widget = None
        self._pending_dirty_widgets.clear()
        self._update_save_button_visibility()

    def _update_save_button_visibility(self):
        """Show Save button only when there are unsaved changes (dirty state)."""
        if hasattr(self, "save_return_button"):
            # Only show/enable when actually dirty (not just when a shortcut fires)
            if self._dirty:
                self.save_return_button.setEnabled(True)
                self.save_return_button.setVisible(True)
            else:
                self.save_return_button.setEnabled(False)
                self.save_return_button.setVisible(False)

    def _setup_dirty_tracking(self):
        """Setup signals to track changes."""
        self.title_edit.textChanged.connect(lambda: self._mark_dirty(self.title_edit))
        self.author_combo.currentTextChanged.connect(
            lambda: self._mark_dirty(self.author_combo)
        )
        self.comments_edit.textChanged.connect(
            lambda: self._mark_dirty(self.comments_edit)
        )
        self.year_spin.valueChanged.connect(lambda: self._mark_dirty(self.year_spin))
        self.time_edit.textChanged.connect(lambda: self._mark_dirty(self.time_edit))
        self.reader_edit.textChanged.connect(lambda: self._mark_dirty(self.reader_edit))
        self.series_combo.currentTextChanged.connect(
            lambda: self._mark_dirty(self.series_combo)
        )
        self.genre_combo.currentTextChanged.connect(
            lambda: self._mark_dirty(self.genre_combo)
        )
        self.collection_combo.currentIndexChanged.connect(
            lambda: self._mark_dirty(self.collection_combo)
        )

    def _apply_duplicate_read_only_state(self):
        """Keep duplicate entries editable (treated like other errors)."""
        if not self.is_duplicate_item:
            return
        self.set_status("Duplicate item loaded. Edit fields to resolve and save.")

    def load_combos(self):
        """Load author, series, genre, and collection combo boxes."""
        # Authors
        authors = self.author_queries.get_all()
        for author in authors:
            self.author_combo.addItem(author.name, author.author_id)

        # Series
        series_items = self.series_queries.get_all()
        for series in series_items:
            self.series_combo.addItem(series.name, series.series_id)

        # Genres
        genres = self.genre_queries.get_all()
        for genre in genres:
            self.genre_combo.addItem(genre.name, genre.genre_id)

        # Collections
        collections = self.collection_queries.get_all()
        for collection in collections:
            self.collection_combo.addItem(collection.name, collection.collection_id)

    def _format_duration(self) -> str:
        """Format imported time fields as HH:MM."""
        hours = int(self.book_data.get("time_hours") or 0)
        minutes = int(self.book_data.get("time_minutes") or 0)
        if hours == 0 and minutes == 0:
            return ""
        return f"{hours:02d}:{minutes:02d}"

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
        if normalized != self.time_edit.text():
            self.time_edit.setText(normalized)

    @classmethod
    def _normalize_year_value(cls, year_value) -> int:
        """Return valid year for spinner, otherwise 0 (blank)."""
        try:
            parsed_year = int(str(year_value).strip())
        except (TypeError, ValueError):
            return 0

        if cls.MIN_VALID_YEAR <= parsed_year <= cls.MAX_VALID_YEAR:
            return parsed_year
        return 0

    def load_book_data(self):
        """Load scanned book data into form fields."""
        self.title_edit.setText(self.book_data.get("title", ""))
        self.author_combo.setCurrentText(self.book_data.get("author", ""))
        self.comments_edit.setPlainText(self.book_data.get("comment", ""))

        self.year_spin.setValue(self._normalize_year_value(self.book_data.get("year")))

        self.time_edit.setText(self._format_duration())
        self.reader_edit.setText(self.book_data.get("narrator", ""))
        self.series_combo.setCurrentText(self.book_data.get("series", ""))
        self.genre_combo.setCurrentText(self.book_data.get("genre", ""))

        collection_name = self.book_data.get("collection", "")
        if collection_name:
            self.collection_combo.setCurrentText(collection_name)
        elif self.collection_combo.count() > 0:
            self.collection_combo.setCurrentIndex(0)

        tracks = self.book_data.get("tracks")
        if not tracks:
            files = self.book_data.get("files")
            if isinstance(files, list):
                tracks = len(files)
        self.files_edit.setText(str(tracks) if tracks else "")

        bitrate = self.book_data.get("bitrate")
        self.bitrate_edit.setText(f"{bitrate} kbps" if bitrate else "")

        size_mb = self.book_data.get("size_mb")
        self.size_edit.setText(f"{size_mb:.2f} MB" if size_mb else "")

        self.format_edit.setText(self.book_data.get("format", ""))
        self.source_edit.setText(self.book_data.get("source", "Import"))
        self.path_edit.setText(self.book_data.get("folder", ""))

        if self.errors:
            validator = ImportValidator()
            error_text = validator.format_error_summary(self.errors)
            self.errors_edit.setText(error_text)
        else:
            self.errors_edit.setText("")

        self._original_author = self.author_combo.currentText().strip()
        self._original_series = self.series_combo.currentText().strip()
        self._original_genre = self.genre_combo.currentText().strip()

        self._clear_dirty()

    def on_prev(self):
        """Navigate to previous import item, with dirty check and popup."""

        def do_nav():
            navigated = self._navigate_without_close(self.current_index - 1)
            QTimer.singleShot(0, self.title_edit.setFocus)
            if navigated:
                return
            QApplication.beep()
            self._collect_form_data()
            self.done(self.RESULT_PREV)

        if self._dirty:
            self._confirm_save_or_cancel(do_nav)
        else:
            do_nav()

    def on_next(self):
        """Navigate to next import item, with dirty check and popup."""

        def do_nav():
            navigated = self._navigate_without_close(self.current_index + 1)
            QTimer.singleShot(0, self.title_edit.setFocus)
            if navigated:
                return
            QApplication.beep()
            self._collect_form_data()
            self.done(self.RESULT_NEXT)

        if self._dirty:
            self._confirm_save_or_cancel(do_nav)
        else:
            do_nav()

    def _check_combo_change(
        self, field_name: str, combo: QComboBox, original_value: str, query_obj
    ):
        """
        Check whether combo changed to a new value and confirm create-on-save.
        """
        current_text = combo.currentText().strip()

        if not current_text or current_text == original_value:
            return

        existing = query_obj.get_by_name(current_text)
        if existing:
            self._set_original_combo_value(field_name, current_text)
            return

        reply = exec_styled_message_box(
            self,
            self.scaler.get_scaled_size(20),
            icon=QMessageBox.Question,
            title=f"New {field_name}",
            text=(
                f"'{current_text}' is a new {field_name}.\n\n"
                f"Create this new {field_name}?"
            ),
            buttons=QMessageBox.Yes | QMessageBox.No,
            default_button=QMessageBox.No,
        )

        if reply != QMessageBox.Yes:
            combo.setEditText(original_value)
            return

        self._set_original_combo_value(field_name, current_text)

    def _set_original_combo_value(self, field_name: str, value: str):
        """Update original combo snapshots to avoid repeat prompts."""
        if field_name == "Author":
            self._original_author = value
        elif field_name == "Series":
            self._original_series = value
        elif field_name == "Genre":
            self._original_genre = value

    @staticmethod
    def _detail_window_title(book_data: dict, errors: list | None = None) -> str:
        """Return a stable title for screen-reader clarity."""
        return "Import Detail"

    def _build_errors_for_row(self, row: int) -> list:
        """Build current error list for a row from parent scanned items."""
        parent = self.parent()
        if not parent or not hasattr(parent, "scanned_items"):
            return []
        if row < 0 or row >= len(parent.scanned_items):
            return []

        item = parent.scanned_items[row]
        errors = list(item.get("errors", []))
        if item.get("is_duplicate"):
            has_duplicate_error = any(
                str(err).strip().lower() == "duplicate" for err in errors
            )
            if not has_duplicate_error:
                errors.append("Duplicate")
        return errors

    def _navigate_without_close(self, target_index: int) -> bool:
        """Navigate to another scanned item in the same dialog instance."""
        parent = self.parent()
        if not parent or not hasattr(parent, "scanned_items"):
            return False

        resolved_index = self._resolve_target_index_from_filter(target_index)
        if resolved_index is None:
            return False

        self._collect_form_data()
        if hasattr(parent, "_apply_detail_edits"):
            parent._apply_detail_edits(self.current_index, self)

        next_item = parent.scanned_items[resolved_index]
        self.book_data = next_item.get("book", {}).copy()
        self.errors = self._build_errors_for_row(resolved_index)
        self.current_index = resolved_index
        self.total_count = len(parent.scanned_items)

        self.setWindowTitle(self._detail_window_title(self.book_data, self.errors))
        self.setAccessibleName(self.windowTitle())
        self.load_book_data()
        self.set_status(f"Viewing item {self.current_index + 1} of {self.total_count}")
        return True

    def _resolve_target_index_from_filter(self, requested_index: int) -> int | None:
        """Resolve navigation target to previous/next visible row when filter is active."""
        parent = self.parent()
        if not parent or not hasattr(parent, "scanned_items"):
            return None

        row_count = len(parent.scanned_items)
        if row_count == 0:
            return None

        if not hasattr(parent, "table") or parent.table is None:
            if 0 <= requested_index < row_count:
                return requested_index
            return None

        visible_rows = [
            row
            for row in range(row_count)
            if row < parent.table.rowCount() and not parent.table.isRowHidden(row)
        ]
        if not visible_rows:
            return None

        if requested_index == self.current_index:
            return (
                self.current_index
                if self.current_index in visible_rows
                else visible_rows[0]
            )

        direction = 1 if requested_index > self.current_index else -1
        if direction > 0:
            candidates = [row for row in visible_rows if row > self.current_index]
            return candidates[0] if candidates else None

        candidates = [row for row in visible_rows if row < self.current_index]
        return candidates[-1] if candidates else None

    def apply_control_styles(self):
        """Apply consistent control styling with scaling."""
        base_height = 20
        scale_pct = self.scaler.current_scale
        scaled_height = int(base_height * (scale_pct / 100.0))

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

        label_style = """
            QLabel {
                font-weight: bold;
            }
        """

        # Apply styles to widgets that need local styling
        # Text boxes, combo boxes, and spin boxes use theme manager styling - don't override
        for widget in self.findChildren(QPushButton):
            widget.setStyleSheet(button_style)
        for widget in self.findChildren(QLabel):
            widget.setStyleSheet(label_style)

    def setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Form layout (mirrors Book Details layout)
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setSpacing(10)

        # Row 1: Title + Author (side by side)
        row1_layout = QHBoxLayout()
        self.title_edit = QLineEdit()
        self.title_edit.setAccessibleName("Book title")
        self.title_edit.setReadOnly(False)
        row1_layout.addWidget(self.title_edit, 2)

        author_label = QLabel("&Author:")
        self.author_combo = QComboBox()
        self.author_combo.setEditable(True)
        self.author_combo.setAccessibleName("Author")
        self.author_combo.setMaximumWidth(280)
        author_label.setBuddy(self.author_combo)
        row1_layout.addWidget(author_label)
        row1_layout.addWidget(self.author_combo, 1)

        title_label = QLabel("&Title:")
        title_label.setBuddy(self.title_edit)
        form.addRow(title_label, row1_layout)

        # Row 2: Plot
        self.comments_label = QLabel("Pl&ot:")
        self.comments_edit = QTextEdit()
        self.comments_edit.setAccessibleName("Plot")
        self.comments_edit.setTabChangesFocus(True)
        self.comments_edit.setMinimumHeight(40)
        self.comments_edit.setReadOnly(False)
        self.comments_label.setBuddy(self.comments_edit)
        form.addRow(self.comments_label, self.comments_edit)

        # Row 3: Year + Length + Reader
        row3_layout = QHBoxLayout()

        self.year_spin = QSpinBox()
        self.year_spin.setRange(0, self.MAX_VALID_YEAR)
        self.year_spin.setValue(0)
        self.year_spin.setAccessibleName("Publication year")
        self.year_spin.setSpecialValueText("")
        self.year_spin.setFixedWidth(110)
        self.year_spin.setReadOnly(False)
        self.year_spin.setButtonSymbols(QAbstractSpinBox.NoButtons)
        row3_layout.addWidget(self.year_spin)
        row3_layout.addSpacing(40)

        time_label = QLabel("Ti&me:")
        self.time_edit = QLineEdit()
        self.time_edit.setPlaceholderText("HH:MM")
        self.time_edit.setInputMask("99:99;_")
        self.time_edit.setAccessibleName("Time")
        self.time_edit.setFixedWidth(100)
        self.time_edit.setReadOnly(False)
        time_label.setBuddy(self.time_edit)
        row3_layout.addWidget(time_label)
        row3_layout.addWidget(self.time_edit)
        row3_layout.addSpacing(40)

        reader_label = QLabel("&Reader:")
        self.reader_edit = QLineEdit()
        self.reader_edit.setAccessibleName("Reader/Narrator")
        self.reader_edit.setMaximumWidth(220)
        reader_label.setBuddy(self.reader_edit)
        row3_layout.addWidget(reader_label)
        row3_layout.addWidget(self.reader_edit)
        row3_layout.addStretch(1)

        year_label = QLabel("&Year:")
        year_label.setBuddy(self.year_spin)
        form.addRow(year_label, row3_layout)

        # Row 4: Series + Genre + Collection
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

        collection_label = QLabel("&Collection:")
        self.collection_combo = QComboBox()
        self.collection_combo.setAccessibleName("Collection")
        self.collection_combo.setMaximumWidth(220)
        self.collection_combo.setEditable(False)  # Make read-only, not editable
        self.collection_combo.setEnabled(True)  # Always enabled for focus
        collection_label.setBuddy(self.collection_combo)
        row4_layout.addWidget(collection_label)
        row4_layout.addWidget(self.collection_combo, 1)

        series_label = QLabel("Ser&ies:")
        series_label.setBuddy(self.series_combo)
        form.addRow(series_label, row4_layout)

        # Row 5: Files + Bitrate + Size + Format + Source
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

        # Row 6: Errors
        row6_layout = QHBoxLayout()

        self.errors_label = QLabel("&Errors:")
        self.errors_edit = QTextEdit()
        self.errors_edit.setReadOnly(True)
        self.errors_edit.setAccessibleName("Validation errors")
        self.errors_edit.setMinimumHeight(60)
        self.errors_edit.setStyleSheet(
            "QTextEdit { background-color: palette(base); color: red; }"
        )
        self.errors_label.setBuddy(self.errors_edit)
        row6_layout.addWidget(self.errors_edit)

        form.addRow(self.errors_label, row6_layout)

        # Row 7: Path
        row7_layout = QHBoxLayout()

        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        self.path_edit.setAccessibleName("File path")
        row7_layout.addWidget(self.path_edit, 1)

        path_label = QLabel("Pat&h:")
        path_label.setBuddy(self.path_edit)
        form.addRow(path_label, row7_layout)

        layout.addLayout(form)

        # Footer: status bar + buttons
        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        layout.addWidget(self.status_bar)

        # Row 5: Action buttons
        button_layout = QHBoxLayout()

        self.save_return_button = QPushButton("&Save")
        self.save_return_button.setAccessibleName("Save")
        self.save_return_button.setAccessibleDescription(
            "Save edits and continue editing - Alt+S"
        )
        # self.save_return_button.setShortcut(QKeySequence("Alt+S"))  # Managed by ShortcutManager
        self.save_return_button.setFocusPolicy(Qt.StrongFocus)
        self.save_return_button.clicked.connect(self.on_save)
        self.save_return_button.setEnabled(False)
        self.save_return_button.setVisible(False)
        button_layout.addWidget(self.save_return_button)

        self.skip_button = QPushButton("&Discard")
        self.skip_button.setAccessibleName("Discard")
        self.skip_button.setAccessibleDescription(
            "Discard this import item and advance to next available item - Alt+D"
        )
        # self.skip_button.setShortcut(QKeySequence("Alt+D"))  # Managed by ShortcutManager
        self.skip_button.setFocusPolicy(Qt.StrongFocus)
        self.skip_button.clicked.connect(self.on_skip_discard)
        button_layout.addWidget(self.skip_button)

        button_layout.addStretch()

        layout.addLayout(button_layout)

        # Set explicit tab order for predictable screen reader navigation
        self.setTabOrder(self.title_edit, self.author_combo)
        self.setTabOrder(self.author_combo, self.comments_edit)
        self.setTabOrder(self.comments_edit, self.year_spin)
        self.setTabOrder(self.year_spin, self.time_edit)
        self.setTabOrder(self.time_edit, self.reader_edit)
        self.setTabOrder(self.reader_edit, self.series_combo)
        self.setTabOrder(self.series_combo, self.genre_combo)
        self.setTabOrder(self.genre_combo, self.collection_combo)
        self.setTabOrder(self.collection_combo, self.files_edit)
        self.setTabOrder(self.files_edit, self.bitrate_edit)
        self.setTabOrder(self.bitrate_edit, self.size_edit)
        self.setTabOrder(self.size_edit, self.format_edit)
        self.setTabOrder(self.format_edit, self.source_edit)
        self.setTabOrder(self.source_edit, self.errors_edit)
        self.setTabOrder(self.errors_edit, self.path_edit)
        self.setTabOrder(self.path_edit, self.save_return_button)
        self.setTabOrder(self.save_return_button, self.skip_button)

        self.setup_shortcuts()

    def setup_shortcuts(self):
        """Centralized Alt+letter shortcut registration using ShortcutManager."""
        from src.accessibility.shortcuts import get_shortcut_manager, ShortcutContext

        mgr = get_shortcut_manager()
        callback_map = {
            "title_edit": lambda: self.title_edit.setFocus(),  # Alt+T
            "author_combo": lambda: self.author_combo.setFocus(),  # Alt+A
            "comments_edit": lambda: self.comments_edit.setFocus(),  # Alt+P (from Pl&ot label)
            "year_spin": lambda: self.year_spin.setFocus(),  # Alt+Y
            "time_edit": lambda: self.time_edit.setFocus(),  # Alt+M
            "reader_edit": lambda: self.reader_edit.setFocus(),  # Alt+R
            "series_combo": lambda: self.series_combo.setFocus(),  # Alt+I
            "genre_combo": lambda: self.genre_combo.setFocus(),  # Alt+G
            "collection_combo": lambda: self.collection_combo.setFocus(),  # Alt+C
            "files_edit": lambda: self.files_edit.setFocus(),  # Alt+F
            "bitrate_edit": lambda: self.bitrate_edit.setFocus(),  # Alt+B
            "size_edit": lambda: self.size_edit.setFocus(),  # Alt+Z
            "errors_edit": lambda: self.errors_edit.setFocus(),  # Alt+E
            "path_edit": lambda: self.path_edit.setFocus(),  # Alt+H
            "save_return_button": lambda: self.save_return_button.click(),  # Alt+S
            "skip_button": lambda: self.skip_button.click(),  # Alt+D
        }
        mgr.register_alt_shortcuts(self, ShortcutContext.BOOK_DETAILS, callback_map)

        # Local shortcuts (not centralized): Alt+/, F1, Escape, PageUp/PageDown
        self.help_shortcut = QShortcut(QKeySequence("F1"), self)
        self.help_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.help_shortcut.activated.connect(self.on_show_shortcuts)

        self.close_shortcut = QShortcut(QKeySequence("Escape"), self)
        self.close_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.close_shortcut.activated.connect(self.on_cancel_edit)

        self.prev_shortcut = QShortcut(QKeySequence(Qt.Key_PageUp), self)
        self.prev_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.prev_shortcut.activated.connect(self.on_prev)

        self.next_shortcut = QShortcut(QKeySequence(Qt.Key_PageDown), self)
        self.next_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.next_shortcut.activated.connect(self.on_next)

        self.read_status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.read_status_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.read_status_shortcut.activated.connect(self.on_read_status_bar)

    def on_show_shortcuts(self):
        """Show keyboard shortcuts help dialog."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Keyboard Shortcuts - Import Detail")
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
            ("Alt+M", "Time"),
            ("Alt+R", "Reader"),
            ("Alt+I", "Series"),
            ("Alt+G", "Genre"),
            ("Alt+C", "Collection"),
            ("Alt+F", "Files"),
            ("Alt+B", "Bitrate"),
            ("Alt+Z", "Size"),
            ("Alt+E", "Errors"),
            ("Alt+H", "Path"),
            ("Alt+S", "Save"),
            ("Alt+D", "Discard"),
            ("Page Up", "Previous item"),
            ("Page Down", "Next item"),
            ("Escape", "Close detail"),
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

    def _collect_form_data(self):
        """Collect edited values back into book_data."""
        self.book_data["title"] = self._normalize_name_field(self.title_edit.text())
        self.book_data["author"] = self._normalize_name_field(
            self.author_combo.currentText()
        )
        normalized_year = self._normalize_year_value(self.year_spin.value())
        self.book_data["year"] = normalized_year if normalized_year > 0 else None
        self.book_data["comment"] = self.comments_edit.toPlainText().strip()
        self.book_data["narrator"] = self._normalize_name_field(self.reader_edit.text())
        self.book_data["series"] = self._normalize_name_field(
            self.series_combo.currentText()
        )
        self.book_data["genre"] = self._normalize_name_field(
            self.genre_combo.currentText()
        )
        self.book_data["collection"] = self._normalize_name_field(
            self.collection_combo.currentText()
        )

        normalized_time = self._normalize_time_text(self.time_edit.text())
        if normalized_time:
            self.book_data["time_hours"] = int(normalized_time[:2])
            self.book_data["time_minutes"] = int(normalized_time[3:])
        else:
            self.book_data["time_hours"] = 0
            self.book_data["time_minutes"] = 0

    def on_skip_discard(self):
        """Discard this import item and return skip result to parent."""
        parent = self.parent()
        if (
            parent
            and hasattr(parent, "_discard_scanned_item")
            and hasattr(parent, "scanned_items")
        ):
            next_row = parent._discard_scanned_item(self.current_index)
            if next_row is not None and 0 <= next_row < len(parent.scanned_items):
                next_item = parent.scanned_items[next_row]
                self.book_data = next_item.get("book", {}).copy()
                self.errors = self._build_errors_for_row(next_row)
                self.current_index = next_row
                self.total_count = len(parent.scanned_items)
                title = self._detail_window_title(self.book_data, self.errors)
                self.setWindowTitle(title)
                self.setAccessibleName(title)
                self.load_book_data()
                self.set_status("Import item discarded")
                return

            if hasattr(parent, "table") and parent.table.rowCount() == 0:
                if hasattr(parent, "set_status"):
                    parent.set_status("Import item discarded. No items remain")
            elif hasattr(parent, "set_status"):
                parent.set_status(
                    "Import item discarded. No items remain in current filter"
                )

            self._closing_via_handler = True
            try:
                announce_dialog_closed(self)
                super().reject()
            finally:
                self._closing_via_handler = False
            return

        self._closing_via_handler = True
        try:
            announce_dialog_closed(self)
            self.done(self.RESULT_SKIP)
        finally:
            self._closing_via_handler = False

    def _save_to_parent(self, resolve_errors: bool):
        """Push current edits to parent import list and refresh local state."""
        self._collect_form_data()

        parent = self.parent()
        if parent and hasattr(parent, "_apply_detail_edits"):
            parent._apply_detail_edits(
                self.current_index,
                self,
                refresh_view=False,
            )

        if resolve_errors:
            self.errors = []
            self.errors_edit.setText("")

        title = self._detail_window_title(self.book_data, self.errors)
        self.setWindowTitle(title)
        self.setAccessibleName(title)
        self._clear_dirty()

    def on_save(self):
        """Save edits in-place and keep dialog open. Returns True if save succeeded, False if validation failed."""
        if not self._dirty:
            return True

        # Normalize time field before saving (in case user hasn't lost focus from time field)
        if self.time_edit.hasFocus():
            self._normalize_time_on_focus_out()

        # Validation logic (add your own as needed)
        if not self.title_edit.text().strip():
            self.set_status("Title is required.")
            self.title_edit.setFocus()
            return False
        # Add more validation as needed

        resolve_errors = bool(self.errors)
        self._save_to_parent(resolve_errors=resolve_errors)
        self.set_status("Changes saved")
        return True

    def accept(self):
        """Return edited data when accepting."""
        resolve_errors = bool(self._dirty and self.errors)
        self._save_to_parent(resolve_errors=resolve_errors)

        announce_dialog_closed(self)
        super().accept()

    def reject(self):
        """Handle cancel with dirty-check prompt before closing."""
        if self._closing_via_handler:
            announce_dialog_closed(self)
            super().reject()
            return

        if self._dirty:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Question)
            msg.setWindowTitle("Save Changes")
            msg.setStyleSheet(
                build_accessible_message_box_style(self.scaler.get_scaled_size(20))
            )
            msg.setText(self._build_exit_prompt_text())
            msg.setStandardButtons(
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            msg.button(QMessageBox.Yes).setText("&Yes - Save")
            msg.button(QMessageBox.No).setText("&No - Continue editing")
            msg.button(QMessageBox.Cancel).setText("Cance&l - Discard and close")
            reply = msg.exec()

            if reply == QMessageBox.Yes:
                self.accept()
                return

            if reply == QMessageBox.No:
                self.set_status("Close canceled")
                return

            if reply == QMessageBox.Cancel:
                self._clear_dirty()
                self._closing_via_handler = True
                try:
                    announce_dialog_closed(self)
                    super().reject()
                finally:
                    self._closing_via_handler = False
                return

            self.set_status("Close canceled")
            return

        self._closing_via_handler = True
        try:
            announce_dialog_closed(self)
            super().reject()
        finally:
            self._closing_via_handler = False
