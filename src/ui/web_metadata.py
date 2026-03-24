"""
Web Book Details Window
Shows web-fetched book data with comparison to local data.
Modeled from import_detail_window.py with modifications for web data display.
"""

import re
import os
import shutil
import subprocess

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QLabel,
    QSpinBox, QMessageBox, QApplication, QTextEdit, QAbstractSpinBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QStatusBar
)
from PySide6.QtCore import Qt, QEvent, QTimer, QSettings
from PySide6.QtGui import QShortcut, QKeySequence, QAccessible

from src.database import DatabaseManager, Book, AuthorQueries, SeriesQueries, GenreQueries, CollectionQueries
from src.accessibility.scaling import UIScaler
from src.accessibility.style_helpers import build_accessible_message_box_style, exec_styled_message_box
from src.accessibility.theme_manager import ThemeManager
from src.accessibility.key_filters import is_unmapped_alt_letter
from src.accessibility.accessible_events import (
    announce_status_message, announce_dialog_opened, announce_dialog_closed
)


class WebMetadataWindow(QDialog):
    """
    Web metadata dialog for viewing and accepting web-fetched book data.
    """

    RESULT_PREV = 2
    RESULT_NEXT = 3
    RESULT_SKIP = 4
    MIN_VALID_YEAR = 1900
    MAX_VALID_YEAR = 2100
    # Centralized Alt+letter shortcut mapping for web metadata
    ALLOWED_ALT_LETTERS = {
        'A',  # Author
        'G',  # Genre
        'I',  # Series (Ser&ies)
        'L',  # Launch Tag
        'P',  # Plot (Pl&ot)
        'S',  # Save
        'T',  # Title
        'Y',  # Year
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

    def __init__(self, db: DatabaseManager, book: Book, scaler: UIScaler,
                 theme_manager: ThemeManager, parent=None):
        """
        Initialize web metadata window.

        Args:
            db: Database manager
            book: Book object to compare with web data
            scaler: UI scaler
            theme_manager: Theme manager
            parent: Parent widget
        """
        super().__init__(parent)
        self.setAttribute(Qt.WA_NativeWindow, True)
        self.setWindowModality(Qt.ApplicationModal)
        self.winId()

        self.db = db
        self.scaler = scaler
        self.theme_manager = theme_manager
        self.book = book
        self._dirty = False
        self._first_dirty_widget = None
        self._pending_dirty_widgets = set()
        self._default_status_message = "Ready"
        self._closing_via_handler = False

        # Query objects
        self.author_queries = AuthorQueries(db)
        self.series_queries = SeriesQueries(db)
        self.genre_queries = GenreQueries(db)
        self.collection_queries = CollectionQueries(db)

        # Setup UI
        self.setup_ui()
        self.load_book_data()
        self.setup_shortcuts()

        # Window settings
        title = f"Web Details: {self.book.title}"
        self.setWindowTitle(title)
        self.setAccessibleName(title)
        self.setAccessibleDescription("Window for reviewing web-fetched book metadata")
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
        """Set status bar message with optional screen reader announcement."""
        self._default_status_message = message

        if hasattr(self, "status_bar") and self.status_bar is not None:
            announce_status_message(
                self.status_bar, message, move_focus=announce)

    def get_status_summary(self) -> str:
        """Return a concise current-status summary for Alt+/ reading."""
        title = self.title_edit.text().strip() or "Untitled"
        author = self.author_edit.text().strip() or "Unknown author"
        
        if self._default_status_message and self._default_status_message != "Ready":
            return self._default_status_message
        return f"Web metadata: {title} by {author}. Ready to review web data."

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
                getattr(parent, "_default_status_message", "") or "").strip()

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
        else:
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Information,
                title="Status",
                text=f"No screen reader active.\n\nStatus: {status_text}",
            )

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
                    QTimer.singleShot(0, lambda w=source: w.lineEdit(
                    ).deselect() if w.lineEdit() else None)
            elif isinstance(source, QSpinBox):
                QTimer.singleShot(0, lambda w=source: w.lineEdit().deselect())

        if event.type() == QEvent.FocusOut:
            # Web metadata doesn't use combo change checking
            # Removed: author_combo, series_combo, genre_combo references

            dirty_widget = self._resolve_dirty_source(source)
            if dirty_widget is not None:
                field_name = self._get_dirty_field_name(dirty_widget)
                self.set_status(
                    f"{field_name} changed.",
                    announce=True
                )
                self._pending_dirty_widgets.discard(dirty_widget)

        return super().eventFilter(source, event)

    def _resolve_dirty_source(self, source):
        """Resolve the actual widget that should be marked as dirty."""
        if source in self._pending_dirty_widgets:
            return source

        # Web metadata only has collection_combo
        if hasattr(self, 'collection_combo'):
            if self.collection_combo in self._pending_dirty_widgets and source == self.collection_combo.lineEdit():
                return self.collection_combo

        parent = source.parentWidget() if hasattr(source, "parentWidget") else None
        if parent in self._pending_dirty_widgets:
            return parent

        return None

    def _get_dirty_field_name(self, widget):
        """Get the field name for status announcements."""
        mapping = {
            self.title_edit: "Title",
            self.author_edit: "Author",
            self.comments_edit: "Plot",
            self.year_spin: "Year",
            self.series_edit: "Series",
            self.genre_edit: "Genre",
            self.collection_combo: "Collection",
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
            self.save_return_button.setEnabled(True)
            self.save_return_button.setVisible(True)

    def _clear_dirty(self):
        """Clear dirty flag."""
        self._dirty = False
        self._first_dirty_widget = None
        self._pending_dirty_widgets.clear()
        if hasattr(self, "save_return_button"):
            self.save_return_button.setEnabled(False)
            self.save_return_button.setVisible(False)

    def _setup_dirty_tracking(self):
        """Setup signals to track changes."""
        self.title_edit.textChanged.connect(
            lambda: self._mark_dirty(self.title_edit))
        self.author_combo.currentTextChanged.connect(
            lambda: self._mark_dirty(self.author_combo))
        self.comments_edit.textChanged.connect(
            lambda: self._mark_dirty(self.comments_edit))
        self.year_spin.valueChanged.connect(
            lambda: self._mark_dirty(self.year_spin))
        self.time_edit.textChanged.connect(
            lambda: self._mark_dirty(self.time_edit))
        self.reader_edit.textChanged.connect(
            lambda: self._mark_dirty(self.reader_edit))
        self.series_combo.currentTextChanged.connect(
            lambda: self._mark_dirty(self.series_combo))
        self.genre_combo.currentTextChanged.connect(
            lambda: self._mark_dirty(self.genre_combo))
        self.collection_combo.currentIndexChanged.connect(
            lambda: self._mark_dirty(self.collection_combo))

    def _apply_duplicate_read_only_state(self):
        """Keep duplicate entries editable (treated like other errors)."""
        if not self.is_duplicate_item:
            return
        self.set_status(
            "Duplicate item loaded. Edit fields to resolve and save.")

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
            self.collection_combo.addItem(
                collection.name, collection.collection_id)

    def _format_duration(self) -> str:
        """Format book duration as HH:MM."""
        # Web metadata doesn't have time fields yet
        return ""

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
        """Load current book data into form fields."""
        self.title_edit.setText(self.book.title or "")
        self.author_edit.setText(self.book.author_name or "")
        self.comments_edit.setPlainText(self.book.comments or "")
        self.year_spin.setValue(self.book.year or 0)
        self.series_edit.setText(self.book.series_name or "")
        self.genre_edit.setText(self.book.genre_name or "")

        # Collection field (web metadata may not use this yet)
        collection_name = self.book.collection_name or ""
        if collection_name and hasattr(self, 'collection_combo'):
            # Load collections into combo if needed
            pass

        # Web metadata doesn't use import-specific fields
        # Removed: files, bitrate, size, format, source, path, errors, time, reader

        self._original_author = self.author_edit.text().strip()
        self._original_series = self.series_edit.text().strip()
        self._original_genre = self.genre_edit.text().strip()

        self._clear_dirty()

    def _resolve_tag_target_path(self) -> str:
        """Return best file/folder path to open in external tag editor."""
        # Web metadata doesn't have file paths yet
        folder_path = self.book.path or ""
        if folder_path and os.path.exists(folder_path):
            return folder_path
        path_from_form = self.path_edit.text().strip() if hasattr(self, "path_edit") else ""
        if path_from_form and os.path.exists(path_from_form):
            return path_from_form

        return ""

    def _discover_tag_editor(self) -> tuple[str, str] | None:
        """Find supported external tag editor executable and return display name + path."""
        candidates = []

        for command_name in [
            "Mp3tag.exe",
            "Mp3tag",
            "TagScanner.exe",
            "TagScanner",
            "Tagscan.exe",
            "Tagscan",
        ]:
            command_path = shutil.which(command_name)
            if command_path:
                display_name = "Mp3tag" if "mp3tag" in command_name.lower() else "TagScanner"
                candidates.append((display_name, command_path))

        program_files_roots = [
            os.environ.get("ProgramFiles", ""),
            os.environ.get("ProgramFiles(x86)", ""),
            os.environ.get("LOCALAPPDATA", ""),
        ]
        known_relative_paths = [
            ("Mp3tag", os.path.join("Mp3tag", "Mp3tag.exe")),
            ("TagScanner", os.path.join("TagScanner", "Tagscan.exe")),
            ("TagScanner", os.path.join("TagScanner", "TagScanner.exe")),
        ]

        for root in program_files_roots:
            if not root:
                continue
            for display_name, relative_path in known_relative_paths:
                full_path = os.path.join(root, relative_path)
                if os.path.isfile(full_path):
                    candidates.append((display_name, full_path))

        seen = set()
        for display_name, executable_path in candidates:
            normalized = os.path.normcase(os.path.abspath(executable_path))
            if normalized in seen:
                continue
            seen.add(normalized)
            return display_name, executable_path

        return None

    def on_launch_tag_editor(self):
        """Launch Mp3tag/TagScanner for current item folder/file when available."""
        target_path = self._resolve_tag_target_path()
        if not target_path:
            self.set_status(
                "Edit Tag unavailable: no valid file or folder path", announce=True)
            return

        editor = self._discover_tag_editor()
        if not editor:
            self.set_status(
                "Edit Tag unavailable: install Mp3tag or TagScanner",
                announce=True,
            )
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Information,
                title="Edit Tag",
                text=(
                    "No supported tag editor was detected.\n\n"
                    "Install Mp3tag or TagScanner, then use Launch Tag again."
                ),
            )
            return

        editor_name, editor_path = editor
        try:
            subprocess.Popen([editor_path, target_path])
        except Exception as exc:
            self.set_status(f"Edit Tag failed: {str(exc)}", announce=True)
            return

        self.set_status(
            f"Opened {editor_name} for current import item", announce=True)

    def _check_combo_change(self, field_name: str, combo: QComboBox,
                            original_value: str, query_obj):
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
                str(err).strip().lower() == "duplicate"
                for err in errors
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

        self.setWindowTitle(self._detail_window_title(
            self.book_data, self.errors))
        self.setAccessibleName(self.windowTitle())
        self.load_book_data()
        self.set_status(
            f"Viewing item {self.current_index + 1} of {self.total_count}")
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
            row for row in range(row_count)
            if row < parent.table.rowCount() and not parent.table.isRowHidden(row)
        ]
        if not visible_rows:
            return None

        if requested_index == self.current_index:
            return self.current_index if self.current_index in visible_rows else visible_rows[0]

        direction = 1 if requested_index > self.current_index else -1
        if direction > 0:
            candidates = [
                row for row in visible_rows if row > self.current_index]
            return candidates[0] if candidates else None

        candidates = [row for row in visible_rows if row < self.current_index]
        return candidates[-1] if candidates else None

    def apply_control_styles(self):
        """Apply consistent control styling with scaling."""
        base_height = 20
        scale_pct = self.scaler.current_scale
        scaled_height = int(base_height * (scale_pct / 100.0))

        lineedit_style = f"""
            QLineEdit {{
                min-height: {scaled_height}px;
                max-height: {scaled_height}px;
                padding: 2px;
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

        # Row 1: Title (vertical layout)
        title_label = QLabel("&Title:")
        self.title_edit = QLineEdit()
        self.title_edit.setAccessibleName("Book title")
        self.title_edit.setReadOnly(False)
        title_label.setBuddy(self.title_edit)
        form.addRow(title_label, self.title_edit)

        # Row 2: Author (vertical layout)
        author_label = QLabel("&Author:")
        self.author_edit = QLineEdit()
        self.author_edit.setAccessibleName("Author")
        author_label.setBuddy(self.author_edit)
        form.addRow(author_label, self.author_edit)

        # Row 3: Plot
        self.comments_label = QLabel("Pl&ot:")
        self.comments_edit = QTextEdit()
        self.comments_edit.setAccessibleName("Plot")
        self.comments_edit.setTabChangesFocus(True)
        self.comments_edit.setMinimumHeight(40)
        self.comments_edit.setReadOnly(False)
        self.comments_label.setBuddy(self.comments_edit)
        form.addRow(self.comments_label, self.comments_edit)

        # Row 4: Year (vertical layout)
        year_label = QLabel("&Year:")
        self.year_spin = QSpinBox()
        self.year_spin.setRange(0, self.MAX_VALID_YEAR)
        self.year_spin.setValue(0)
        self.year_spin.setAccessibleName("Publication year")
        self.year_spin.setSpecialValueText("")
        self.year_spin.setFixedWidth(110)
        self.year_spin.setReadOnly(False)
        self.year_spin.setButtonSymbols(QAbstractSpinBox.NoButtons)
        year_label.setBuddy(self.year_spin)
        form.addRow(year_label, self.year_spin)

        # Row 4: Series (vertical layout)
        series_label = QLabel("Ser&ies:")
        self.series_edit = QLineEdit()
        self.series_edit.setAccessibleName("Book series")
        series_label.setBuddy(self.series_edit)
        form.addRow(series_label, self.series_edit)

        # Row 5: Genre (vertical layout)
        genre_label = QLabel("&Genre:")
        self.genre_edit = QLineEdit()
        self.genre_edit.setAccessibleName("Genre")
        genre_label.setBuddy(self.genre_edit)
        form.addRow(genre_label, self.genre_edit)

        # Row 5: Removed collection field - not needed for web metadata

        # Row 5: Removed import-specific fields (files, bitrate, size, format, source)
        # Web metadata doesn't need these fields

        # Row 6: Removed errors field - web metadata doesn't use validation errors

        # Row 7: Removed path field - web metadata doesn't show file paths

        layout.addLayout(form)

        # Buttons (added before status bar like book_details)
        button_layout = QHBoxLayout()

        self.save_return_button = QPushButton("&Save")
        self.save_return_button.setAccessibleName("Save")
        self.save_return_button.setAccessibleDescription(
            "Save edits and continue editing - Alt+S")
        self.save_return_button.setShortcut(QKeySequence("Alt+S"))
        self.save_return_button.setFocusPolicy(Qt.StrongFocus)
        self.save_return_button.clicked.connect(self.on_save)
        self.save_return_button.setEnabled(False)
        self.save_return_button.setVisible(False)
        button_layout.addWidget(self.save_return_button)

        self.launch_tag_button = QPushButton("&Launch Tag")
        self.launch_tag_button.setAccessibleName("Launch Tag")
        self.launch_tag_button.setAccessibleDescription(
            "Open current item in external tag editor - Alt+L")
        self.launch_tag_button.setFocusPolicy(Qt.StrongFocus)
        self.launch_tag_button.clicked.connect(self.on_launch_tag_editor)
        self.launch_tag_button.setEnabled(False)
        self.launch_tag_button.setVisible(False)
        button_layout.addWidget(self.launch_tag_button)

        self.save_button = QPushButton("&Save")
        self.save_button.setAccessibleName("Save")
        self.save_button.setAccessibleDescription(
            "Save web metadata changes - Alt+S")
        self.save_button.setShortcut(QKeySequence("Alt+S"))
        self.save_button.setFocusPolicy(Qt.StrongFocus)
        self.save_button.clicked.connect(self.accept)
        button_layout.addWidget(self.save_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Status bar (added after buttons like book_details)
        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        layout.addWidget(self.status_bar)

        self.setup_shortcuts()

    def setup_shortcuts(self):
        """Centralized Alt+letter shortcut registration using ShortcutManager."""
        from src.accessibility.shortcuts import get_shortcut_manager, ShortcutContext
        mgr = get_shortcut_manager()
        callback_map = {
            'title_edit': lambda: self.title_edit.setFocus(),      # Alt+T
            'author_edit': lambda: self.author_edit.setFocus(),  # Alt+A
            'comments_edit': lambda: self.comments_edit.setFocus(),  # Alt+P (from Pl&ot label)
            'year_spin': lambda: self.year_spin.setFocus(),        # Alt+Y
            'series_edit': lambda: self.series_edit.setFocus(),  # Alt+I
            'genre_edit': lambda: self.genre_edit.setFocus(),    # Alt+G
            'save_button': lambda: self.save_button.click(),      # Alt+S
            'launch_tag_button': lambda: self.launch_tag_button.click(),  # Alt+L
            'show_help': self.on_show_shortcuts,  # F1
        }
        mgr.register_alt_shortcuts(
            self, ShortcutContext.WEB_METADATA, callback_map)

        # Local shortcuts (not centralized): Alt+/, Escape, PageUp/PageDown
        self.read_status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.read_status_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.read_status_shortcut.activated.connect(self.on_read_status_bar)

        self.close_shortcut = QShortcut(QKeySequence("Escape"), self)
        self.close_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.close_shortcut.activated.connect(self.reject)

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
        from src.accessibility.shortcut_helpers import get_accessible_shortcuts_list, build_accessible_f1_popup_style
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
        """Collect edited values for saving web metadata."""
        # Web metadata will save to database, not to book_data dict
        # This method will be implemented when we add save functionality
        pass

    def on_prev(self):
        """Save edits and request previous import item."""
        if self._navigate_without_close(self.current_index - 1):
            return
        QApplication.beep()
        self._collect_form_data()
        self.done(self.RESULT_PREV)

    def on_next(self):
        """Save edits and request next import item."""
        if self._navigate_without_close(self.current_index + 1):
            return
        QApplication.beep()
        self._collect_form_data()
        self.done(self.RESULT_NEXT)

    def on_skip_discard(self):
        """Discard this import item and return skip result to parent."""
        parent = self.parent()
        if parent and hasattr(parent, "_discard_scanned_item") and hasattr(parent, "scanned_items"):
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
                resolve_errors=resolve_errors,
                refresh_view=False
            )

        if resolve_errors:
            self.errors = []
            self.errors_edit.setText("")

        title = self._detail_window_title(self.book_data, self.errors)
        self.setWindowTitle(title)
        self.setAccessibleName(title)
        self._clear_dirty()

    def on_save(self):
        """Save edits in-place and keep dialog open."""
        if not self._dirty:
            self.set_status("No changes to save")
            QApplication.beep()
            return

        resolve_errors = bool(self.errors)
        self._save_to_parent(resolve_errors=resolve_errors)
        self.set_status("Changes saved")

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
                build_accessible_message_box_style(
                    self.scaler.get_scaled_size(20))
            )
            msg.setText(self._build_exit_prompt_text())
            msg.setStandardButtons(
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            msg.button(QMessageBox.Yes).setText("&Yes - Save")
            msg.button(QMessageBox.No).setText("&No - Continue editing")
            msg.button(QMessageBox.Cancel).setText(
                "Cance&l - Discard and close")
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
