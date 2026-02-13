"""
Import Window
Main interface for scanning folders and importing audiobooks.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QStatusBar,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QFileDialog, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, QSettings, QTimer
from PySide6.QtGui import QShortcut, QKeySequence, QAccessible
from datetime import datetime

from database import (
    DatabaseManager, BookQueries, AuthorQueries,
    GenreQueries, CollectionQueries, Book, Collection
)
from core import BookScanner, ImportValidator
from accessibility.scaling import UIScaler
from accessibility.theme_manager import ThemeManager
from accessibility.accessible_events import (
    announce_status_message, announce_dialog_opened, announce_dialog_closed
)
from ui.import_detail_window import ImportDetailWindow


class ImportWindow(QDialog):
    """
    Import dialog for scanning folders and importing metadata.
    """

    def __init__(self, db: DatabaseManager, scaler: UIScaler,
                 theme_manager: ThemeManager, parent=None):
        super().__init__(parent)

        self.db = db
        self.scaler = scaler
        self.theme_manager = theme_manager
        self.settings = QSettings('AbCS', 'AudioBookCollector')

        self.book_queries = BookQueries(self.db)
        self.author_queries = AuthorQueries(self.db)
        self.genre_queries = GenreQueries(self.db)
        self.collection_queries = CollectionQueries(self.db)
        self.scanner = BookScanner()
        self.validator = ImportValidator()

        self._loading = False
        self.scanned_items = []
        self.allowed_extensions = None
        self.include_subfolders = True
        self.default_collection_id = None
        self._default_status_message = "Ready"

        self.setup_ui()
        self.apply_control_styles()
        self.load_preferences()
        self.connect_signals()
        self.setup_shortcuts()
        self.scaler.scale_changed.connect(self.on_scale_changed)

        title = "Import Audiobooks"
        self.setWindowTitle(title)
        self.setAccessibleName(title)
        self.setAccessibleDescription(
            "Scan folders for audiobooks and import metadata")
        self.resize(1100, 600)
        self.setMinimumWidth(900)

        announce_dialog_opened(self, title)
        self.update_summary()

    def _get_default_collection_id(self) -> int:
        """Get a default collection ID for imports."""
        if self.default_collection_id is not None:
            return self.default_collection_id

        collections = self.collection_queries.get_all()
        if collections:
            self.default_collection_id = collections[0].collection_id
            return self.default_collection_id

        default_collection = Collection(name="Default", active=True)
        self.default_collection_id = self.collection_queries.insert(
            default_collection)
        return self.default_collection_id

    @staticmethod
    def _normalize_year(value):
        """Normalize year to int or None."""
        if value is None:
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            value = value.strip()
            if value.isdigit():
                return int(value)
        return None

    def _build_book_from_scan(self, data: dict) -> Book:
        """Create a Book object from scanned data."""
        title = (data.get("title") or "").strip()
        author_text = (data.get("author") or "").strip()
        genre_text = (data.get("genre") or "").strip()
        reader_text = (data.get("narrator") or "").strip()

        author_id = self.author_queries.get_or_create(author_text)
        genre_id = None
        if genre_text:
            genre_id = self.genre_queries.get_or_create(genre_text)

        return Book(
            title=title,
            author_id=author_id,
            year=self._normalize_year(data.get("year")),
            series_id=None,
            genre_id=genre_id,
            collection_id=self._get_default_collection_id(),
            reader=reader_text,
            time_hours=int(data.get("time_hours") or 0),
            time_minutes=int(data.get("time_minutes") or 0),
            tracks=int(data.get("tracks") or 0),
            size_mb=float(data.get("size_mb") or 0.0),
            bitrate=int(data.get("bitrate") or 0),
            file_format=str(data.get("format") or ""),
            path=str(data.get("folder") or ""),
            comments=str(data.get("comment") or ""),
            date_added=datetime.now(),
            source="Import",
        )

    def setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Header section
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        folder_label = QLabel("&Folder:")
        self.folder_edit = QLineEdit()
        self.folder_edit.setReadOnly(True)
        self.folder_edit.setAccessibleName("Folder path")
        self.folder_edit.setAccessibleDescription(
            "Folder to scan for imports - Alt+F")
        folder_label.setBuddy(self.folder_edit)
        header_layout.addWidget(folder_label)
        header_layout.addWidget(self.folder_edit, 1)

        self.browse_button = QPushButton("Bro&wse")
        self.browse_button.setAccessibleName("Browse")
        self.browse_button.setAccessibleDescription(
            "Browse for a folder to scan - Alt+W")
        header_layout.addWidget(self.browse_button)

        formats_label = QLabel("F&ormats:")
        self.formats_edit = QLineEdit()
        self.formats_edit.setReadOnly(True)
        self.formats_edit.setAccessibleName("Formats")
        self.formats_edit.setAccessibleDescription(
            "File formats to scan - Alt+O")
        formats_label.setBuddy(self.formats_edit)
        header_layout.addWidget(formats_label)
        header_layout.addWidget(self.formats_edit, 1)

        self.scan_button = QPushButton("&Scan")
        self.scan_button.setAccessibleName("Scan")
        self.scan_button.setAccessibleDescription(
            "Scan the selected folder for audio files - Alt+S")
        header_layout.addWidget(self.scan_button)

        layout.addLayout(header_layout)

        # Detail section: import list table
        self.table = QTableWidget()
        self.table.setAccessibleName("Import list")
        self.table.setAccessibleDescription(
            "List of scanned files with validation results")

        columns = [
            "Author",
            "Title",
            "Year",
            "Error Type",
            "File/Folder",
        ]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)

        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)

        layout.addWidget(self.table, 1)

        # Footer section
        footer_layout = QHBoxLayout()

        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        footer_layout.addWidget(self.status_bar, 1)

        self.import_selected_button = QPushButton("&Import Selected")
        self.import_selected_button.setAccessibleName("Import Selected")
        self.import_selected_button.setAccessibleDescription(
            "Import selected valid items - Alt+I")
        self.import_selected_button.setDefault(False)
        self.import_selected_button.setAutoDefault(False)
        footer_layout.addWidget(self.import_selected_button)

        self.import_all_button = QPushButton("Import &All Valid")
        self.import_all_button.setAccessibleName("Import All Valid")
        self.import_all_button.setAccessibleDescription(
            "Import all valid items - Alt+A")
        self.import_all_button.setDefault(False)
        self.import_all_button.setAutoDefault(False)
        footer_layout.addWidget(self.import_all_button)

        self.cancel_button = QPushButton("&Cancel")
        self.cancel_button.setAccessibleName("Cancel")
        self.cancel_button.setAccessibleDescription(
            "Close import window - Alt+C or F4")
        self.cancel_button.setDefault(False)
        self.cancel_button.setAutoDefault(False)
        footer_layout.addWidget(self.cancel_button)

        layout.addLayout(footer_layout)

    def apply_control_styles(self):
        """Apply consistent styling to inputs and buttons."""
        scale_pct = self.scaler.current_scale
        base_height = 20
        scaled_height = int(base_height * (scale_pct / 100.0))
        base_font_size = int(9 * (scale_pct / 100.0))

        font = self.font()
        font.setPointSize(base_font_size)
        self.setFont(font)

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
                background-color: palette(base);
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

        for widget in self.findChildren(QLineEdit):
            widget.setStyleSheet(lineedit_style)
        for widget in self.findChildren(QPushButton):
            widget.setStyleSheet(button_style)

        table_style = """
            QTableView::item:selected {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }
            QTableView::item:selected:!active {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }
            QTableView::item:focus {
                outline: none;
                border: none;
            }
            QTableView {
                outline: 0;
            }
        """
        self.table.setStyleSheet(table_style)

    def on_scale_changed(self, value: int):
        """Refresh control styles when zoom changes."""
        self.apply_control_styles()

    def load_preferences(self):
        """Load import preferences into header fields."""
        self._loading = True

        default_dir = self.settings.value(
            "import/default_directory", "", type=str)
        self.folder_edit.setText(default_dir)

        self.include_subfolders = self.settings.value(
            "import/include_subfolders", True, type=bool)

        formats = []
        allowed_extensions = set()
        for key, label in [
            ("mp3", "MP3"),
            ("m4a", "M4A"),
            ("m4b", "M4B"),
            ("flac", "FLAC"),
            ("ogg", "OGG"),
            ("wav", "WAV"),
            ("wma", "WMA"),
        ]:
            enabled = self.settings.value(
                f"import/formats/{key}", True, type=bool)
            if enabled:
                formats.append(label)
                allowed_extensions.add(f".{key}")

        self.allowed_extensions = allowed_extensions if allowed_extensions else None

        self.formats_edit.setText(", ".join(formats) if formats else "None")

        self._loading = False

    def connect_signals(self):
        """Connect signals to handlers."""
        self.browse_button.clicked.connect(self.on_browse)
        self.scan_button.clicked.connect(self.on_scan)
        self.import_selected_button.clicked.connect(self.on_import_selected)
        self.import_all_button.clicked.connect(self.on_import_all)
        self.cancel_button.clicked.connect(self.on_cancel)
        self.table.cellDoubleClicked.connect(self.on_open_detail)
        self.table.itemSelectionChanged.connect(
            self.on_table_selection_changed)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        close_shortcut = QShortcut(QKeySequence("F4"), self)
        close_shortcut.activated.connect(self.on_cancel)

        focus_list_shortcut = QShortcut(QKeySequence("Alt+B"), self)
        focus_list_shortcut.activated.connect(self.on_focus_list)

        open_detail_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        open_detail_shortcut.activated.connect(self.on_open_detail_selected)

        open_detail_shortcut_num = QShortcut(QKeySequence("Ctrl+Enter"), self)
        open_detail_shortcut_num.activated.connect(
            self.on_open_detail_selected)

        open_detail_f8_shortcut = QShortcut(QKeySequence("F8"), self)
        open_detail_f8_shortcut.activated.connect(self.on_open_detail_selected)

        read_status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        read_status_shortcut.activated.connect(self.on_read_status_bar)

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
            QMessageBox.information(
                self,
                "Status Bar",
                f"No screen reader active.\n\nStatus: {status_text}")

    def on_focus_list(self):
        """Move focus to import list table (Alt+B)."""
        self.table.setFocus()
        if self.table.rowCount() > 0 and self.table.currentRow() < 0:
            self.table.setCurrentCell(0, 0)
        self.set_status("Import list focused")

    def on_table_selection_changed(self):
        """Announce row selection count in status bar."""
        selected_rows = len(self.table.selectionModel().selectedRows())
        if selected_rows > 0:
            self.set_status(f"{selected_rows} selected")

    def update_summary(self, scanned: int = 0, valid: int = 0,
                       errors: int = 0, duplicates: int = 0):
        """Update status bar summary."""
        message = (
            f"Scanned: {scanned} | Valid: {valid} | "
            f"Errors: {errors} | Duplicates: {duplicates}")
        self.set_status(message)

    def on_browse(self):
        """Open folder browser for scan root."""
        current_dir = self.folder_edit.text().strip() or ""
        selected = QFileDialog.getExistingDirectory(
            self, "Select Import Folder", current_dir)
        if selected:
            self.folder_edit.setText(selected)
            self.set_status("Import folder selected")

    def on_scan(self):
        """Scan the selected folder for audiobooks."""
        folder_path = self.folder_edit.text().strip()
        if not folder_path:
            self.set_status("Select a folder before scanning")
            return

        books = self.scanner.scan_folder(
            folder_path,
            include_subfolders=self.include_subfolders,
            allowed_extensions=self.allowed_extensions)

        existing_books = self.book_queries.get_all()
        existing_list = [
            {
                "title": b.title,
                "author": b.author_name,
                "year": b.year
            }
            for b in existing_books
        ]

        self.scanned_items = []
        self.table.setRowCount(len(books))

        valid_count = 0
        error_count = 0
        duplicate_count = 0

        for row, book in enumerate(books):
            errors = list(book.get("errors", []))
            errors.extend(self.validator.validate_book(book))

            has_hard_error = any(
                self.validator.categorize_error(err) in ("read", "parse")
                for err in errors
            )
            has_warning = any(
                self.validator.categorize_error(err) == "warning"
                for err in errors
            )

            is_duplicate = self.validator.is_duplicate(book, existing_list)

            status = "OK"
            if has_hard_error:
                status = "Error"
                error_count += 1
            elif has_warning:
                status = "Warning"
                valid_count += 1
            elif is_duplicate:
                status = "Duplicate"
                duplicate_count += 1
            else:
                valid_count += 1

            error_summary = "; ".join(errors)
            if status == "Duplicate" and not error_summary:
                error_summary = "Duplicate"
            elif status == "Warning" and error_summary:
                error_summary = f"Warning: {error_summary}"
            elif status == "Error" and error_summary:
                error_summary = f"Error: {error_summary}"

            self.table.setItem(
                row, 0, QTableWidgetItem(book.get("author", "")))
            self.table.setItem(row, 1, QTableWidgetItem(book.get("title", "")))
            self.table.setItem(
                row, 2, QTableWidgetItem(str(book.get("year") or "")))
            self.table.setItem(row, 3, QTableWidgetItem(error_summary))
            self.table.setItem(
                row, 4, QTableWidgetItem(book.get("folder", "")))

            self.scanned_items.append({
                "book": book,
                "status": status,
                "errors": errors,
                "is_duplicate": is_duplicate
            })

        if not books:
            self.set_status("No audio files found")
            self.update_summary(0, 0, 0, 0)
            return

        self.update_summary(
            scanned=len(books),
            valid=valid_count,
            errors=error_count,
            duplicates=duplicate_count)

    def on_import_selected(self):
        """Import selected valid items."""
        if not self.scanned_items:
            self.set_status("No scanned items to import")
            return

        selected_rows = {index.row() for index in self.table.selectedIndexes()}
        if not selected_rows:
            self.set_status("Select one or more rows to import")
            return

        self._import_rows(sorted(selected_rows))

    def on_import_all(self):
        """Import all valid items."""
        if not self.scanned_items:
            self.set_status("No scanned items to import")
            return

        eligible_rows = []
        for idx, item in enumerate(self.scanned_items):
            if item["status"] in ("OK", "Warning") and not item["is_duplicate"]:
                eligible_rows.append(idx)

        if not eligible_rows:
            self.set_status("No valid items to import")
            return

        self._import_rows(eligible_rows)

    def _import_rows(self, row_indices):
        """Import rows by index from scanned_items."""
        imported = 0
        skipped = 0
        failed = 0

        for row in row_indices:
            if row < 0 or row >= len(self.scanned_items):
                continue

            item = self.scanned_items[row]
            status = item.get("status")
            if status not in ("OK", "Warning") or item.get("is_duplicate"):
                skipped += 1
                continue

            book_data = item.get("book", {})
            title = (book_data.get("title") or "").strip()
            author_text = (book_data.get("author") or "").strip()
            if not title or not author_text:
                skipped += 1
                continue

            try:
                book = self._build_book_from_scan(book_data)
                self.book_queries.insert(book)
                imported += 1
                item["status"] = "Imported"
                self.table.setItem(row, 3, QTableWidgetItem("Imported"))
            except Exception as exc:
                failed += 1
                item["status"] = "Failed"
                error_item = self.table.item(row, 3)
                error_text = error_item.text() if error_item else ""
                combined_error = (
                    error_text + "; " if error_text else "") + str(exc)
                self.table.setItem(row, 3, QTableWidgetItem(combined_error))

        self.set_status(
            f"Imported: {imported} | Skipped: {skipped} | Failed: {failed}")

    def _apply_detail_edits(self, row: int, detail_window: ImportDetailWindow):
        """Apply edits returned from ImportDetailWindow to scanned item + table."""
        item = self.scanned_items[row]
        for key in [
            "title", "author", "year", "narrator",
            "genre", "series", "collection", "comment"
        ]:
            if key in detail_window.book_data:
                item["book"][key] = detail_window.book_data[key]

        self.table.setItem(row, 1, QTableWidgetItem(
            detail_window.book_data.get("title", "")))
        self.table.setItem(row, 0, QTableWidgetItem(
            detail_window.book_data.get("author", "")))
        self.table.setItem(row, 2, QTableWidgetItem(
            str(detail_window.book_data.get("year") or "")))

    def on_open_detail(self, row: int = 0, col: int = 0):
        """Open import detail window to view/edit scanned metadata."""
        if self.table.rowCount() == 0:
            self.set_status("No items to view")
            return

        if row < 0 or row >= len(self.scanned_items):
            self.set_status("Select a valid row")
            return

        while 0 <= row < len(self.scanned_items):
            item = self.scanned_items[row]
            book_data = item.get("book", {})
            errors = item.get("errors", [])

            detail_window = ImportDetailWindow(
                self.db, self.scaler, self.theme_manager,
                book_data=book_data.copy(), errors=errors,
                current_index=row, total_count=len(self.scanned_items),
                parent=self)

            result = detail_window.exec()

            if result == QDialog.Accepted:
                self._apply_detail_edits(row, detail_window)
                self.set_status("Changes applied to import item")
                return

            if result == ImportDetailWindow.RESULT_PREV:
                self._apply_detail_edits(row, detail_window)
                if row > 0:
                    row -= 1
                else:
                    self.set_status("Already at first item")
                    return
                continue

            if result == ImportDetailWindow.RESULT_NEXT:
                self._apply_detail_edits(row, detail_window)
                if row < len(self.scanned_items) - 1:
                    row += 1
                else:
                    self.set_status("Already at last item")
                    return
                continue

            return

    def _get_selected_or_current_row(self) -> int:
        """Return selected row, current row, or -1 if unavailable."""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            return selected_rows[0].row()

        current_row = self.table.currentRow()
        if current_row >= 0:
            return current_row

        if self.table.rowCount() > 0:
            return 0

        return -1

    def on_open_detail_selected(self):
        """Open detail window for selected/current row."""
        row = self._get_selected_or_current_row()
        if row < 0:
            self.set_status("No items to view")
            return
        self.on_open_detail(row, self.table.currentColumn())

    def on_cancel(self):
        """Close dialog."""
        self.reject()

    def keyPressEvent(self, event):
        """Override to prevent Enter from closing the dialog."""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            event.ignore()
            return
        super().keyPressEvent(event)

    def accept(self):
        """Handle dialog accept."""
        announce_dialog_closed(self)
        super().accept()

    def reject(self):
        """Handle dialog reject."""
        announce_dialog_closed(self)
        super().reject()
