"""
Import Detail Window
Form for viewing and editing scanned audiobook details before import.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QLabel,
    QSpinBox, QMessageBox, QApplication, QTextEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QStatusBar
)
from PySide6.QtCore import Qt, QEvent, QTimer
from PySide6.QtGui import QShortcut, QKeySequence, QAccessible

from database import (
    DatabaseManager, AuthorQueries, SeriesQueries, GenreQueries, CollectionQueries
)
from accessibility.scaling import UIScaler
from accessibility.theme_manager import ThemeManager
from accessibility.key_filters import is_unmapped_alt_letter
from accessibility.accessible_events import (
    announce_status_message, announce_dialog_opened, announce_dialog_closed
)


class ImportDetailWindow(QDialog):
    """
    Import detail dialog for viewing and editing scanned audiobook metadata.
    """

    RESULT_PREV = 2
    RESULT_NEXT = 3
    ALLOWED_ALT_LETTERS = {
        'A', 'B', 'C', 'E', 'F', 'G', 'H', 'I', 'L', 'M', 'O', 'R', 'T', 'Y', 'Z'
    }

    def __init__(self, db: DatabaseManager, scaler: UIScaler,
                 theme_manager: ThemeManager, book_data: dict = None,
                 errors: list = None, current_index: int = 0,
                 total_count: int = 0, parent=None):
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

        self.db = db
        self.scaler = scaler
        self.theme_manager = theme_manager
        self.book_data = book_data or {}
        self.errors = errors or []
        self.current_index = current_index
        self.total_count = total_count
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
        self.apply_control_styles()
        self.install_focus_filters()
        self.load_combos()
        self.load_book_data()
        self._setup_dirty_tracking()

        # Window settings
        title = "Import Detail - " + self.book_data.get("title", "Untitled")
        self.setWindowTitle(title)
        self.setAccessibleName(title)
        self.setAccessibleDescription(
            "Form for viewing and editing scanned audiobook details")
        self.resize(850, 500)

        announce_dialog_opened(self, title)
        self.set_status("Ready")

    def set_status(self, message: str, announce: bool = False):
        """Set status message on this dialog and mirror to parent import window."""
        self._default_status_message = message

        if hasattr(self, "status_bar") and self.status_bar is not None:
            announce_status_message(
                self.status_bar, message, move_focus=announce)

        parent = self.parent()
        if parent and hasattr(parent, "set_status"):
            parent.set_status(message, announce=False)
        elif parent and hasattr(parent, "status_bar"):
            announce_status_message(
                parent.status_bar, message, move_focus=False)

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

    def on_read_status_bar(self):
        """Read current status (Alt+/)."""
        status_text = self.get_status_summary()
        if QAccessible.isActive():
            self.set_status(status_text, announce=True)
        else:
            QMessageBox.information(
                self,
                "Status",
                f"No screen reader active.\n\nStatus: {status_text}")

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
        if is_unmapped_alt_letter(event, self.ALLOWED_ALT_LETTERS):
            event.accept()
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
            dirty_widget = self._resolve_dirty_source(source)
            if dirty_widget is not None:
                field_name = self._get_dirty_field_name(dirty_widget)
                self.set_status(
                    f"{field_name} changed. Press Alt+I Save or Alt+C Cancel",
                    announce=True
                )
                self._pending_dirty_widgets.discard(dirty_widget)

        return super().eventFilter(source, event)

    def _mark_dirty(self, widget=None):
        """Mark form as having unsaved changes."""
        if widget is not None:
            self._pending_dirty_widgets.add(widget)

        if not self._dirty:
            self._dirty = True
            if widget and not self._first_dirty_widget:
                self._first_dirty_widget = widget
            self.import_button.setEnabled(True)

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
        }
        return mapping.get(widget, "Import details")

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
        """Clear dirty flag."""
        self._dirty = False
        self._first_dirty_widget = None
        self._pending_dirty_widgets.clear()

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
        """Format imported time fields as HH:MM."""
        hours = int(self.book_data.get("time_hours") or 0)
        minutes = int(self.book_data.get("time_minutes") or 0)
        if hours == 0 and minutes == 0:
            return ""
        return f"{hours:02d}:{minutes:02d}"

    def load_book_data(self):
        """Load scanned book data into form fields."""
        self.title_edit.setText(self.book_data.get("title", ""))
        self.author_combo.setCurrentText(self.book_data.get("author", ""))
        self.comments_edit.setPlainText(self.book_data.get("comment", ""))

        year = self.book_data.get("year")
        if year:
            try:
                self.year_spin.setValue(int(year))
            except (ValueError, TypeError):
                self.year_spin.setValue(0)

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
            error_text = "; ".join(self.errors)
            self.errors_edit.setText(error_text)
        else:
            self.errors_edit.setText("")

        self._clear_dirty()

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

        for widget in self.findChildren(QLineEdit):
            widget.setStyleSheet(lineedit_style)
        for widget in self.findChildren(QComboBox):
            widget.setStyleSheet(combo_style)
        for widget in self.findChildren(QSpinBox):
            widget.setStyleSheet(spinbox_style)
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
        row1_layout.addWidget(self.title_edit, 2)

        author_label = QLabel("&Author:")
        self.author_combo = QComboBox()
        self.author_combo.setEditable(True)
        self.author_combo.setAccessibleName("Author")
        author_label.setBuddy(self.author_combo)
        row1_layout.addWidget(author_label)
        row1_layout.addWidget(self.author_combo, 1)

        title_label = QLabel("&Title:")
        title_label.setBuddy(self.title_edit)
        form.addRow(title_label, row1_layout)

        # Row 2: Comments
        self.comments_label = QLabel("C&omments:")
        self.comments_edit = QTextEdit()
        self.comments_edit.setAccessibleName("Comments")
        self.comments_edit.setTabChangesFocus(True)
        self.comments_edit.setMinimumHeight(40)
        self.comments_label.setBuddy(self.comments_edit)
        form.addRow(self.comments_label, self.comments_edit)

        # Row 3: Year + Time + Reader
        row3_layout = QHBoxLayout()

        self.year_spin = QSpinBox()
        self.year_spin.setRange(1900, 2100)
        self.year_spin.setValue(0)
        self.year_spin.setAccessibleName("Publication year")
        self.year_spin.setSpecialValueText("Unknown")
        row3_layout.addWidget(self.year_spin)

        time_label = QLabel("Ti&me:")
        self.time_edit = QLineEdit()
        self.time_edit.setPlaceholderText("HH:MM")
        self.time_edit.setAccessibleName("Duration")
        time_label.setBuddy(self.time_edit)
        row3_layout.addWidget(time_label)
        row3_layout.addWidget(self.time_edit)

        reader_label = QLabel("&Reader:")
        self.reader_edit = QLineEdit()
        self.reader_edit.setAccessibleName("Reader/Narrator")
        reader_label.setBuddy(self.reader_edit)
        row3_layout.addWidget(reader_label)
        row3_layout.addWidget(self.reader_edit)

        year_label = QLabel("&Year:")
        year_label.setBuddy(self.year_spin)
        form.addRow(year_label, row3_layout)

        # Row 4: Series + Genre + Collection
        row4_layout = QHBoxLayout()

        self.series_combo = QComboBox()
        self.series_combo.setEditable(True)
        self.series_combo.setAccessibleName("Book series")
        row4_layout.addWidget(self.series_combo, 1)

        genre_label = QLabel("&Genre:")
        self.genre_combo = QComboBox()
        self.genre_combo.setEditable(True)
        self.genre_combo.setAccessibleName("Genre")
        genre_label.setBuddy(self.genre_combo)
        row4_layout.addWidget(genre_label)
        row4_layout.addWidget(self.genre_combo, 1)

        collection_label = QLabel("Co&llection:")
        self.collection_combo = QComboBox()
        self.collection_combo.setAccessibleName("Collection")
        collection_label.setBuddy(self.collection_combo)
        row4_layout.addWidget(collection_label)
        row4_layout.addWidget(self.collection_combo, 1)

        series_label = QLabel("&Series:")
        series_label.setBuddy(self.series_combo)
        form.addRow(series_label, row4_layout)

        # Row 5: Files + Bitrate + Size + Format + Source
        row5_layout = QHBoxLayout()

        files_label = QLabel("&Files:")
        self.files_edit = QLineEdit()
        self.files_edit.setReadOnly(True)
        self.files_edit.setAccessibleName("Number of files")
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
        size_label.setBuddy(self.size_edit)
        row5_layout.addWidget(size_label)
        row5_layout.addWidget(self.size_edit)

        format_label = QLabel("Format:")
        self.format_edit = QLineEdit()
        self.format_edit.setReadOnly(True)
        self.format_edit.setAccessibleName("File format")
        row5_layout.addWidget(format_label)
        row5_layout.addWidget(self.format_edit)

        source_label = QLabel("Source:")
        self.source_edit = QLineEdit()
        self.source_edit.setReadOnly(True)
        self.source_edit.setAccessibleName("Import source")
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
            "QTextEdit { background-color: palette(base); color: red; }")
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

        # Buttons
        button_layout = QHBoxLayout()

        self.import_button = QPushButton("&Import")
        self.import_button.setAccessibleName("Import book")
        self.import_button.setAccessibleDescription(
            "Import this book with entered details - Alt+I")
        self.import_button.setFocusPolicy(Qt.StrongFocus)
        self.import_button.clicked.connect(self.accept)
        button_layout.addWidget(self.import_button)

        button_layout.addStretch()

        self.cancel_button = QPushButton("&Cancel")
        self.cancel_button.setAccessibleName("Cancel import")
        self.cancel_button.setAccessibleDescription(
            "Cancel import for this book - Alt+C or Escape")
        self.cancel_button.setFocusPolicy(Qt.StrongFocus)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.setup_shortcuts()

    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        self.help_shortcut = QShortcut(QKeySequence("F1"), self)
        self.help_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.help_shortcut.activated.connect(self.on_show_shortcuts)

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
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setStyleSheet(
            "QTableWidget:focus { border: none; outline: none; }"
            "QTableWidget::item:selected { border: none; outline: none; }"
        )

        shortcuts = [
            ("Alt+/", "Read status bar"),
            ("Alt+T", "Title"),
            ("Alt+A", "Author"),
            ("Alt+O", "Comments"),
            ("Alt+Y", "Year"),
            ("Alt+M", "Time"),
            ("Alt+R", "Reader"),
            ("Alt+I", "Series"),
            ("Alt+G", "Genre"),
            ("Alt+L", "Collection"),
            ("Alt+F", "Files"),
            ("Alt+B", "Bitrate"),
            ("Alt+Z", "Size"),
            ("Alt+H", "Path"),
            ("Alt+I", "Import"),
            ("Alt+C or Escape", "Cancel"),
            ("Page Up", "Previous item"),
            ("Page Down", "Next item"),
            ("F1", "Show keyboard shortcuts"),
        ]

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

        close_button = QPushButton("Close")
        close_button.setAccessibleName("Close")
        close_button.clicked.connect(dlg.accept)
        btn_font = close_button.font()
        btn_font.setPointSize(self.scaler.get_scaled_size(11))
        close_button.setFont(btn_font)
        layout.addWidget(close_button)

        dlg.setTabOrder(table, close_button)

        dlg.exec()

    def _collect_form_data(self):
        """Collect edited values back into book_data."""
        self.book_data["title"] = self.title_edit.text().strip()
        self.book_data["author"] = self.author_combo.currentText().strip()
        self.book_data["year"] = self.year_spin.value(
        ) if self.year_spin.value() > 0 else None
        self.book_data["comment"] = self.comments_edit.toPlainText().strip()
        self.book_data["narrator"] = self.reader_edit.text().strip()
        self.book_data["series"] = self.series_combo.currentText().strip()
        self.book_data["genre"] = self.genre_combo.currentText().strip()
        self.book_data["collection"] = self.collection_combo.currentText().strip()

    def on_prev(self):
        """Save edits and request previous import item."""
        if self.current_index <= 0:
            QApplication.beep()
            return
        self._collect_form_data()
        self.done(self.RESULT_PREV)

    def on_next(self):
        """Save edits and request next import item."""
        if self.total_count and self.current_index >= self.total_count - 1:
            QApplication.beep()
            return
        self._collect_form_data()
        self.done(self.RESULT_NEXT)

    def accept(self):
        """Return edited data when accepting."""
        self._collect_form_data()

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
            msg.setText(
                "Import details changed.\n\n"
                "Save = apply edits and close\n"
                "Cancel = continue editing"
            )
            save_button = msg.addButton("&Save", QMessageBox.AcceptRole)
            msg.addButton("&Cancel", QMessageBox.RejectRole)
            msg.exec()

            if msg.clickedButton() == save_button:
                self.accept()
            else:
                self.set_status("Close canceled")
            return

        self._closing_via_handler = True
        try:
            announce_dialog_closed(self)
            super().reject()
        finally:
            self._closing_via_handler = False
