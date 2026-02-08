"""
Book Details Window
Form for viewing and editing individual book information.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QTextEdit, QPushButton,
    QLabel, QDateEdit, QSpinBox, QMessageBox, QWidget
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QAccessible
from datetime import datetime

from database import DatabaseManager, Book, BookQueries, AuthorQueries, SeriesQueries, GenreQueries, CollectionQueries
from accessibility.scaling import UIScaler
from accessibility.accessible_events import announce_status_message, announce_form_field, announce_dialog_opened, announce_dialog_closed


class BookDetailsWindow(QDialog):
    """
    Book details dialog for viewing/editing book information.
    """

    def __init__(self, db: DatabaseManager, scaler: UIScaler, book: Book = None, parent=None):
        """
        Initialize book details window.

        Args:
            db: Database manager
            scaler: UI scaler
            book: Book to edit (None for new book)
            parent: Parent widget
        """
        super().__init__(parent)

        self.db = db
        self.scaler = scaler
        self.book = book or Book()
        self.is_new = (book is None)

        # Query objects
        self.book_queries = BookQueries(db)
        self.author_queries = AuthorQueries(db)
        self.series_queries = SeriesQueries(db)
        self.genre_queries = GenreQueries(db)
        self.collection_queries = CollectionQueries(db)

        # Setup UI
        self.setup_ui()
        self.disable_hover_highlight()
        self.load_combos()

        if not self.is_new:
            self.load_book_data()

        # Window settings
        title = "New Book" if self.is_new else f"Book Details - {self.book.title}"
        self.setWindowTitle(title)
        self.setAccessibleName(title)
        self.setAccessibleDescription(
            "Form for viewing and editing book information")
        self.resize(700, 500)

    def disable_hover_highlight(self):
        """Disable hover highlighting for low-vision comfort."""
        self.setMouseTracking(False)
        self.setAttribute(Qt.WA_Hover, False)
        for child in self.findChildren(QWidget):
            child.setMouseTracking(False)
            child.setAttribute(Qt.WA_Hover, False)

    def setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Form layout
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setSpacing(10)

        # Title
        self.title_edit = QLineEdit()
        self.title_edit.setAccessibleName("Book title")
        form.addRow("&Title:", self.title_edit)

        # Author
        self.author_combo = QComboBox()
        self.author_combo.setEditable(True)
        self.author_combo.setAccessibleName("Author")
        form.addRow("&Author:", self.author_combo)

        # Year and Files (side by side)
        year_files_layout = QHBoxLayout()
        self.year_spin = QSpinBox()
        self.year_spin.setRange(1900, 2100)
        self.year_spin.setValue(datetime.now().year)
        self.year_spin.setAccessibleName("Publication year")
        year_files_layout.addWidget(self.year_spin)

        year_files_layout.addWidget(QLabel("Files:"))
        self.files_edit = QLineEdit()
        self.files_edit.setReadOnly(True)
        self.files_edit.setAccessibleName("Number of files")
        year_files_layout.addWidget(self.files_edit)
        form.addRow("&Year:", year_files_layout)

        # Series and Genre (side by side)
        series_genre_layout = QHBoxLayout()
        self.series_combo = QComboBox()
        self.series_combo.setEditable(True)
        self.series_combo.setAccessibleName("Book series")
        series_genre_layout.addWidget(self.series_combo, 1)

        series_genre_layout.addWidget(QLabel("Genre:"))
        self.genre_combo = QComboBox()
        self.genre_combo.setEditable(True)
        self.genre_combo.setAccessibleName("Genre")
        series_genre_layout.addWidget(self.genre_combo, 1)
        form.addRow("Ser&ies:", series_genre_layout)

        # Reader
        self.reader_edit = QLineEdit()
        self.reader_edit.setAccessibleName("Reader/Narrator")
        form.addRow("&Reader:", self.reader_edit)

        # Collection
        self.collection_combo = QComboBox()
        self.collection_combo.setAccessibleName("Collection")
        form.addRow("Co&llection:", self.collection_combo)

        # Time and Size (side by side)
        time_size_layout = QHBoxLayout()
        self.time_edit = QLineEdit()
        self.time_edit.setPlaceholderText("HH:MM")
        self.time_edit.setAccessibleName("Duration")
        time_size_layout.addWidget(self.time_edit)

        time_size_layout.addWidget(QLabel("Size (MB):"))
        self.size_edit = QLineEdit()
        self.size_edit.setReadOnly(True)
        self.size_edit.setAccessibleName("File size in megabytes")
        time_size_layout.addWidget(self.size_edit)
        form.addRow("Ti&me:", time_size_layout)

        # Bitrate and Format (side by side)
        bitrate_format_layout = QHBoxLayout()
        self.bitrate_edit = QLineEdit()
        self.bitrate_edit.setReadOnly(True)
        self.bitrate_edit.setAccessibleName("Bitrate in kbps")
        bitrate_format_layout.addWidget(self.bitrate_edit)

        bitrate_format_layout.addWidget(QLabel("Format:"))
        self.format_edit = QLineEdit()
        self.format_edit.setReadOnly(True)
        self.format_edit.setAccessibleName("File format")
        bitrate_format_layout.addWidget(self.format_edit)
        form.addRow("&Bitrate:", bitrate_format_layout)

        # Path
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        self.path_edit.setAccessibleName("File path")
        form.addRow("Pat&h:", self.path_edit)

        # Comments
        self.comments_edit = QTextEdit()
        self.comments_edit.setAccessibleName("Comments")
        self.comments_edit.setMaximumHeight(100)
        form.addRow("C&omments:", self.comments_edit)

        # Read date
        self.read_date = QDateEdit()
        self.read_date.setCalendarPopup(True)
        self.read_date.setDisplayFormat("yyyy-MM-dd")
        self.read_date.setAccessibleName("Date read")
        self.read_date.setSpecialValueText("Not read")
        form.addRow("Read Date:", self.read_date)

        layout.addLayout(form)

        # Buttons
        button_layout = QHBoxLayout()

        self.save_button = QPushButton("&Save")
        self.save_button.setAccessibleName("Save book")
        self.save_button.clicked.connect(self.on_save)
        button_layout.addWidget(self.save_button)

        if not self.is_new:
            self.delete_button = QPushButton("&Delete")
            self.delete_button.setAccessibleName("Delete book")
            self.delete_button.clicked.connect(self.on_delete)
            button_layout.addWidget(self.delete_button)

        button_layout.addStretch()

        self.close_button = QPushButton("&Close")
        self.close_button.setAccessibleName("Close window")
        self.close_button.clicked.connect(self.reject)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def load_combos(self):
        """Load combo box data."""
        # Authors
        self.author_combo.clear()
        authors = self.author_queries.get_all()
        for author in authors:
            self.author_combo.addItem(author.name, author.author_id)

        # Series
        self.series_combo.clear()
        self.series_combo.addItem("", None)  # Empty option
        series_list = self.series_queries.get_all()
        for series in series_list:
            self.series_combo.addItem(series.name, series.series_id)

        # Genres
        self.genre_combo.clear()
        self.genre_combo.addItem("", None)  # Empty option
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

        # Files
        self.files_edit.setText(str(self.book.tracks))

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

        # Size
        self.size_edit.setText(self.book.size_display)

        # Bitrate
        self.bitrate_edit.setText(str(self.book.bitrate))

        # Format
        self.format_edit.setText(self.book.file_format)

        # Path
        self.path_edit.setText(self.book.path)

        # Comments
        self.comments_edit.setPlainText(self.book.comments)

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

    def on_save(self):
        """Save book data."""
        # Validate
        if not self.title_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Title is required.")
            self.title_edit.setFocus()
            return

        # Get author ID (create if new)
        author_text = self.author_combo.currentText().strip()
        if not author_text:
            QMessageBox.warning(self, "Validation Error",
                                "Author is required.")
            self.author_combo.setFocus()
            return

        author_id = self.author_queries.get_or_create(author_text)

        # Get or create series
        series_text = self.series_combo.currentText().strip()
        series_id = None
        if series_text:
            series_id = self.series_queries.get_or_create(series_text)

        # Get or create genre
        genre_text = self.genre_combo.currentText().strip()
        genre_id = None
        if genre_text:
            genre_id = self.genre_queries.get_or_create(genre_text)

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
        self.book.title = self.title_edit.text().strip()
        self.book.author_id = author_id
        self.book.year = self.year_spin.value()
        self.book.series_id = series_id
        self.book.genre_id = genre_id
        self.book.collection_id = collection_id
        self.book.reader = self.reader_edit.text().strip()
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
                QMessageBox.information(
                    self, "Success", "Book added successfully!")
            else:
                self.book_queries.update(self.book)
                QMessageBox.information(
                    self, "Success", "Book updated successfully!")

            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving book: {str(e)}")

    def on_delete(self):
        """Delete book."""
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{self.book.title}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.book_queries.delete(self.book.book_id)
                QMessageBox.information(
                    self, "Success", "Book deleted successfully!")
                self.accept()
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Error deleting book: {str(e)}")
