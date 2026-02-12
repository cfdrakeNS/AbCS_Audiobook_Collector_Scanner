"""
Import Detail Window
Form for viewing and editing scanned audiobook details before import.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QLabel,
    QSpinBox, QMessageBox, QApplication, QTextEdit
)
from PySide6.QtCore import Qt, QEvent, QTimer
from PySide6.QtGui import QShortcut, QKeySequence

from database import (
    DatabaseManager, AuthorQueries, GenreQueries
)
from accessibility.scaling import UIScaler
from accessibility.theme_manager import ThemeManager
from accessibility.accessible_events import (
    announce_status_message, announce_dialog_opened, announce_dialog_closed
)


class ImportDetailWindow(QDialog):
    """
    Import detail dialog for viewing and editing scanned audiobook metadata.
    """

    def __init__(self, db: DatabaseManager, scaler: UIScaler,
                 theme_manager: ThemeManager, book_data: dict = None,
                 errors: list = None, parent=None):
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
        self._dirty = False
        self._first_dirty_widget = None

        # Query objects
        self.author_queries = AuthorQueries(db)
        self.genre_queries = GenreQueries(db)

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
        if event.type() == QEvent.FocusIn:
            if isinstance(source, QLineEdit):
                QTimer.singleShot(0, lambda w=source: w.deselect())
            elif isinstance(source, QComboBox):
                if source.lineEdit():
                    QTimer.singleShot(0, lambda w=source: w.lineEdit(
                    ).deselect() if w.lineEdit() else None)
            elif isinstance(source, QSpinBox):
                QTimer.singleShot(0, lambda w=source: w.lineEdit().deselect())

        return super().eventFilter(source, event)

    def _mark_dirty(self, widget=None):
        """Mark form as having unsaved changes."""
        if not self._dirty:
            self._dirty = True
            if widget and not self._first_dirty_widget:
                self._first_dirty_widget = widget
            self.import_button.setEnabled(True)

    def _clear_dirty(self):
        """Clear dirty flag."""
        self._dirty = False
        self._first_dirty_widget = None

    def _setup_dirty_tracking(self):
        """Setup signals to track changes."""
        self.title_edit.textChanged.connect(
            lambda: self._mark_dirty(self.title_edit))
        self.author_combo.currentTextChanged.connect(
            lambda: self._mark_dirty(self.author_combo))
        self.year_spin.valueChanged.connect(
            lambda: self._mark_dirty(self.year_spin))
        self.narrator_edit.textChanged.connect(
            lambda: self._mark_dirty(self.narrator_edit))
        self.genre_combo.currentTextChanged.connect(
            lambda: self._mark_dirty(self.genre_combo))

    def load_combos(self):
        """Load author and genre combo boxes."""
        # Authors
        authors = self.author_queries.get_all()
        for author in authors:
            self.author_combo.addItem(author.name, author.author_id)

        # Genres
        genres = self.genre_queries.get_all()
        for genre in genres:
            self.genre_combo.addItem(genre.name, genre.genre_id)

    def load_book_data(self):
        """Load scanned book data into form fields."""
        self.title_edit.setText(self.book_data.get("title", ""))
        self.author_combo.setCurrentText(self.book_data.get("author", ""))

        year = self.book_data.get("year")
        if year:
            try:
                self.year_spin.setValue(int(year))
            except (ValueError, TypeError):
                self.year_spin.setValue(0)

        self.narrator_edit.setText(self.book_data.get("narrator", ""))
        self.genre_combo.setCurrentText(self.book_data.get("genre", ""))
        self.file_path_edit.setText(self.book_data.get("folder", ""))
        self.file_format_edit.setText(self.book_data.get("format", ""))

        size_mb = self.book_data.get("size_mb")
        if size_mb:
            self.file_size_edit.setText(f"{size_mb:.2f} MB")

        # Show errors if any
        if self.errors:
            error_text = "; ".join(self.errors)
            self.errors_edit.setText(error_text)
            self.errors_edit.setVisible(True)
            self.errors_label.setVisible(True)

        self._clear_dirty()

    def apply_control_styles(self):
        """Apply consistent control styling with scaling."""
        scaled_height = int(self.scaler.scale(28))

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

        # Header section
        header_layout = QHBoxLayout()
        self.errors_status = QLabel("Review scanned data")
        self.errors_status.setAccessibleName("Status")
        header_layout.addWidget(self.errors_status)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Form layout
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

        # Row 2: Year + Narrator + Genre
        row2_layout = QHBoxLayout()

        self.year_spin = QSpinBox()
        self.year_spin.setRange(1900, 2100)
        self.year_spin.setValue(0)
        self.year_spin.setAccessibleName("Publication year")
        self.year_spin.setSpecialValueText("Unknown")
        row2_layout.addWidget(self.year_spin)

        narrator_label = QLabel("N&arrator:")
        self.narrator_edit = QLineEdit()
        self.narrator_edit.setAccessibleName("Narrator/Reader")
        narrator_label.setBuddy(self.narrator_edit)
        row2_layout.addWidget(narrator_label)
        row2_layout.addWidget(self.narrator_edit)

        genre_label = QLabel("&Genre:")
        self.genre_combo = QComboBox()
        self.genre_combo.setEditable(True)
        self.genre_combo.setAccessibleName("Genre")
        genre_label.setBuddy(self.genre_combo)
        row2_layout.addWidget(genre_label)
        row2_layout.addWidget(self.genre_combo, 1)

        year_label = QLabel("&Year:")
        year_label.setBuddy(self.year_spin)
        form.addRow(year_label, row2_layout)

        # Row 3: File path + Format + Size (read-only reference)
        row3_layout = QHBoxLayout()

        self.file_path_edit = QLineEdit()
        self.file_path_edit.setReadOnly(True)
        self.file_path_edit.setAccessibleName("File path")
        row3_layout.addWidget(self.file_path_edit, 3)

        format_label = QLabel("Format:")
        self.file_format_edit = QLineEdit()
        self.file_format_edit.setReadOnly(True)
        self.file_format_edit.setAccessibleName("File format")
        row3_layout.addWidget(format_label)
        row3_layout.addWidget(self.file_format_edit)

        size_label = QLabel("Size:")
        self.file_size_edit = QLineEdit()
        self.file_size_edit.setReadOnly(True)
        self.file_size_edit.setAccessibleName("File size")
        row3_layout.addWidget(size_label)
        row3_layout.addWidget(self.file_size_edit)

        path_label = QLabel("Pat&h:")
        path_label.setBuddy(self.file_path_edit)
        form.addRow(path_label, row3_layout)

        # Row 4: Errors (if any) - highlighted
        self.errors_label = QLabel("E&rrors:")
        self.errors_edit = QTextEdit()
        self.errors_edit.setReadOnly(True)
        self.errors_edit.setAccessibleName("Validation errors")
        self.errors_edit.setMinimumHeight(60)
        self.errors_edit.setStyleSheet(
            "QTextEdit { background-color: palette(base); color: red; }")
        self.errors_label.setBuddy(self.errors_edit)
        form.addRow(self.errors_label, self.errors_edit)

        # Hide errors initially (shown only if there are errors)
        self.errors_label.setVisible(False)
        self.errors_edit.setVisible(False)

        layout.addLayout(form)

        # Footer: buttons
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
        close_shortcut = QShortcut(QKeySequence("Escape"), self)
        close_shortcut.activated.connect(self.reject)

    def accept(self):
        """Return edited data when accepting."""
        # Collect edited values back into book_data
        self.book_data["title"] = self.title_edit.text().strip()
        self.book_data["author"] = self.author_combo.currentText().strip()
        self.book_data["year"] = self.year_spin.value(
        ) if self.year_spin.value() > 0 else None
        self.book_data["narrator"] = self.narrator_edit.text().strip()
        self.book_data["genre"] = self.genre_combo.currentText().strip()

        announce_dialog_closed(self)
        super().accept()

    def reject(self):
        """Handle cancel."""
        announce_dialog_closed(self)
        super().reject()
