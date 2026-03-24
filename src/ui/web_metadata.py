"""
Web Metadata Window - Built from PROVEN accessible skeleton
Accessibility works out of box: F1, Alt+/, Escape
"""

import sys
import os

# Add to project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QApplication, QStatusBar, 
    QLineEdit, QTextEdit, QSpinBox, QFormLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QCheckBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QShortcut, QKeySequence, QAccessible

from src.accessibility.scaling import UIScaler
from src.accessibility.theme_manager import ThemeManager
from src.accessibility.accessible_events import announce_dialog_opened, announce_dialog_closed
from src.database import DatabaseManager, Book
from src.database.queries import BookQueries, AuthorQueries, SeriesQueries, GenreQueries


class WebMetadataWindow(QDialog):
    """
    Web metadata window with PROVEN accessibility foundation.
    
    F1, Alt+/, and Escape work out of box.
    Built incrementally from accessible skeleton.
    """
    
    def __init__(self, db: DatabaseManager, book: Book, scaler: UIScaler, theme_manager: ThemeManager, parent=None, refresh_callback=None):
        super().__init__(parent)
        self.setWindowTitle("Web Details")
        self.setAccessibleName("Web Details Window")
        self.setAttribute(Qt.WA_NativeWindow, True)
        self.resize(600, 400)  # Make window wider for title/author fields
        
        # Basic setup - PROVEN pattern
        self.scaler = scaler
        self.theme_manager = theme_manager
        self._default_status_message = "Ready"
        self.refresh_callback = refresh_callback  # Callback to refresh book details
        
        # Database objects
        self.db = db
        self.book = book
        
        # Initialize query objects
        self.book_queries = BookQueries(db)
        self.author_queries = AuthorQueries(db)
        self.series_queries = SeriesQueries(db)
        self.genre_queries = GenreQueries(db)
        
        # Setup UI
        layout = QVBoxLayout(self)
        self.setup_ui(layout)
        
        # Status bar (PROVEN working pattern)
        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        layout.addWidget(self.status_bar)
        
        # Setup shortcuts (add field shortcuts here)
        self.setup_shortcuts()
        
        # Load data and set status
        self.load_book_data()
        self.set_status("Ready")
        announce_dialog_opened(self, "Web Details")
    
    def setup_ui(self, layout):
        """
        Web metadata UI - built incrementally.
        """
        # Form layout
        form = QFormLayout()
        
        # Title field with checkbox
        title_row = QHBoxLayout()
        title_label = QLabel("&Title:")
        self.title_edit = QLineEdit()
        self.title_edit.setAccessibleName("Book title")
        title_label.setBuddy(self.title_edit)
        title_row.addWidget(title_label)
        title_row.addWidget(self.title_edit, 1)  # Give title edit more space
        
        # Web data checkbox for title
        self.title_checkbox = QCheckBox()
        self.title_checkbox.setAccessibleName("Title web data indicator")
        self.title_checkbox.setEnabled(False)  # Read-only indicator
        title_row.addWidget(self.title_checkbox)
        
        form.addRow(title_row)
        
        # Author field with checkbox
        author_row = QHBoxLayout()
        author_label = QLabel("&Author:")
        self.author_edit = QLineEdit()
        self.author_edit.setAccessibleName("Author")
        author_label.setBuddy(self.author_edit)
        author_row.addWidget(author_label)
        author_row.addWidget(self.author_edit, 1)  # Give author edit more space
        
        # Web data checkbox for author
        self.author_checkbox = QCheckBox()
        self.author_checkbox.setAccessibleName("Author web data indicator")
        self.author_checkbox.setEnabled(False)  # Read-only indicator
        author_row.addWidget(self.author_checkbox)
        
        form.addRow(author_row)
        
        # Plot field (no checkbox as requested)
        plot_label = QLabel("&Plot:")
        self.plot_edit = QTextEdit()
        self.plot_edit.setAccessibleName("Plot")
        self.plot_edit.setTabChangesFocus(True)
        self.plot_edit.setMinimumHeight(40)
        plot_label.setBuddy(self.plot_edit)
        form.addRow(plot_label, self.plot_edit)
        
        # Year field with checkbox
        year_row = QHBoxLayout()
        year_label = QLabel("&Year:")
        self.year_spin = QSpinBox()
        self.year_spin.setRange(0, 2100)
        self.year_spin.setValue(0)
        self.year_spin.setAccessibleName("Publication year")
        self.year_spin.setSpecialValueText("")
        self.year_spin.setFixedWidth(110)
        year_label.setBuddy(self.year_spin)
        year_row.addWidget(year_label)
        year_row.addWidget(self.year_spin)
        
        # Web data checkbox for year
        self.year_checkbox = QCheckBox()
        self.year_checkbox.setAccessibleName("Year web data indicator")
        self.year_checkbox.setEnabled(False)  # Read-only indicator
        year_row.addWidget(self.year_checkbox)
        
        form.addRow(year_row)
        
        # Series field with checkbox
        series_row = QHBoxLayout()
        series_label = QLabel("Ser&ies:")
        self.series_edit = QLineEdit()
        self.series_edit.setAccessibleName("Book series")
        series_label.setBuddy(self.series_edit)
        series_row.addWidget(series_label)
        series_row.addWidget(self.series_edit, 1)  # Give series edit more space
        
        # Web data checkbox for series
        self.series_checkbox = QCheckBox()
        self.series_checkbox.setAccessibleName("Series web data indicator")
        self.series_checkbox.setEnabled(False)  # Read-only indicator
        series_row.addWidget(self.series_checkbox)
        
        form.addRow(series_row)
        
        # Genre field with checkbox
        genre_row = QHBoxLayout()
        genre_label = QLabel("&Genre:")
        self.genre_edit = QLineEdit()
        self.genre_edit.setAccessibleName("Genre")
        genre_label.setBuddy(self.genre_edit)
        genre_row.addWidget(genre_label)
        genre_row.addWidget(self.genre_edit, 1)  # Give genre edit more space
        
        # Web data checkbox for genre
        self.genre_checkbox = QCheckBox()
        self.genre_checkbox.setAccessibleName("Genre web data indicator")
        self.genre_checkbox.setEnabled(False)  # Read-only indicator
        genre_row.addWidget(self.genre_checkbox)
        
        form.addRow(genre_row)
        
        layout.addLayout(form)
        
        # Buttons - match book_details styling
        button_layout = QHBoxLayout()
        
        # Save button only - match book_details style
        self.save_button = QPushButton("Save")
        self.save_button.setAccessibleName("Save")
        self.save_button.setAccessibleDescription("Save web metadata changes - Alt+S")
        self.save_button.setFocusPolicy(Qt.StrongFocus)
        self.save_button.clicked.connect(self.accept)
        button_layout.addWidget(self.save_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Apply book_details button styling
        scaled_height = self.scaler.get_scaled_size(22)
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
            QPushButton:hover {{
                background-color: palette(alternate-base);
            }}
        """
        self.save_button.setStyleSheet(button_style)
    
    def load_book_data(self):
        """Load book data into fields and fetch web data."""
        if self.book:
            self.title_edit.setText(self.book.title or "")
            self.author_edit.setText(self.book.author_name or "")
            self.plot_edit.setPlainText(self.book.comments or "")
            self.year_spin.setValue(self.book.year or 0)
            self.series_edit.setText(self.book.series_name or "")
            self.genre_edit.setText(self.book.genre_name or "")
        
        # Auto-fetch web data when window opens
        self.fetch_web_data()
    
    def fetch_web_data(self):
        """Fetch book data from web sources."""
        self.set_status("Fetching web data...")
        
        # Get search terms from current book
        title = self.book.title if self.book else ""
        author = self.book.author_name if self.book else ""
        
        if not title and not author:
            self.set_status("No title or author available for web search")
            return
        
        # Simulate web fetching (for now - will implement real API later)
        # This is where we'd integrate with Open Library, Google Books, etc.
        web_data = self.simulate_web_fetch(title, author)
        
        if web_data:
            self.update_fields_with_web_data(web_data)
            self.show_changes_popup(web_data)
            self.set_status("Web data fetched successfully")
        else:
            self.set_status("No web data found")
            # Clear all checkboxes to indicate no web data
            self.clear_web_indicators()
    
    def simulate_web_fetch(self, title, author):
        """Simulate web data fetching (placeholder for real API)."""
        # This should only return data that's actually different and better
        # Not garbage test data that replaces everything
        
        if title and author:
            # Only return data if it's actually an improvement
            # For now, return None to simulate "no web data found"
            # In real implementation, this would call actual APIs
            return None
        
        return None
    
    def update_fields_with_web_data(self, web_data):
        """Update fields with web data and set indicators."""
        changes_made = False
        
        # Update title and set indicator
        if web_data.get('title') and web_data['title'] != self.title_edit.text():
            self.title_edit.setText(web_data['title'])
            self.title_checkbox.setChecked(True)
            changes_made = True
        
        # Update author and set indicator
        if web_data.get('author') and web_data['author'] != self.author_edit.text():
            self.author_edit.setText(web_data['author'])
            self.author_checkbox.setChecked(True)
            changes_made = True
        
        # Update year and set indicator
        if web_data.get('year') and web_data['year'] != self.year_spin.value():
            self.year_spin.setValue(web_data['year'])
            self.year_checkbox.setChecked(True)
            changes_made = True
        
        # Update series with series number and set indicator
        series_text = web_data.get('series', '')
        if web_data.get('series_number'):
            series_text = f"{series_text} - {web_data['series_number']}"
        
        if series_text and series_text != self.series_edit.text():
            self.series_edit.setText(series_text)
            self.series_checkbox.setChecked(True)
            changes_made = True
        
        # Update genre and set indicator
        if web_data.get('genre') and web_data['genre'] != self.genre_edit.text():
            self.genre_edit.setText(web_data['genre'])
            self.genre_checkbox.setChecked(True)
            changes_made = True
        
        # Update plot (no checkbox for plot)
        if web_data.get('plot') and web_data['plot'] != self.plot_edit.toPlainText():
            self.plot_edit.setPlainText(web_data['plot'])
            changes_made = True
        
        return changes_made
    
    def clear_web_indicators(self):
        """Clear all web data indicators."""
        self.title_checkbox.setChecked(False)
        self.author_checkbox.setChecked(False)
        self.year_checkbox.setChecked(False)
        self.series_checkbox.setChecked(False)
        self.genre_checkbox.setChecked(False)
    
    def show_changes_popup(self, web_data):
        """Show popup with only the fields that changed."""
        changes = []
        
        if web_data.get('title') and web_data['title'] != self.book.title:
            changes.append(f"Title: {web_data['title']}")
        
        if web_data.get('author') and web_data['author'] != self.book.author_name:
            changes.append(f"Author: {web_data['author']}")
        
        if web_data.get('year') and web_data['year'] != self.book.year:
            changes.append(f"Year: {web_data['year']}")
        
        if web_data.get('series') or web_data.get('series_number'):
            series_text = web_data.get('series', '')
            if web_data.get('series_number'):
                series_text = f"{series_text} - {web_data['series_number']}"
            changes.append(f"Series: {series_text}")
        
        if web_data.get('genre') and web_data['genre'] != self.book.genre_name:
            changes.append(f"Genre: {web_data['genre']}")
        
        # For plot, just show "Found" or "Not found" as requested
        if web_data.get('plot'):
            changes.append("Plot: Found")
        
        if changes:
            from PySide6.QtWidgets import QMessageBox
            from src.accessibility.style_helpers import exec_styled_message_box, build_accessible_message_box_style
            changes_text = "\n".join(changes)
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Information,
                title="Web Data Updates",
                text=f"The following fields were updated from web data:\n\n{changes_text}"
            )
    
    def setup_shortcuts(self):
        """
        PROVEN accessibility shortcuts + field shortcuts.
        F1, Alt+/, Escape work out of box.
        """
        # F1 - local shortcut (PROVEN working)
        self.help_shortcut = QShortcut(QKeySequence("F1"), self)
        self.help_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.help_shortcut.activated.connect(self.on_show_shortcuts)
        
        # Escape - local shortcut (PROVEN working)
        self.close_shortcut = QShortcut(QKeySequence("Escape"), self)
        self.close_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.close_shortcut.activated.connect(self.reject)
        
        # Alt+/ - local shortcut (PROVEN working)
        self.read_status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.read_status_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.read_status_shortcut.activated.connect(self.on_read_status_bar)
        
        # Field shortcuts
        self.title_shortcut = QShortcut(QKeySequence("Alt+T"), self)
        self.title_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.title_shortcut.activated.connect(lambda: self.title_edit.setFocus())
        
        self.author_shortcut = QShortcut(QKeySequence("Alt+A"), self)
        self.author_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.author_shortcut.activated.connect(lambda: self.author_edit.setFocus())
        
        self.plot_shortcut = QShortcut(QKeySequence("Alt+P"), self)
        self.plot_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.plot_shortcut.activated.connect(lambda: self.plot_edit.setFocus())
        
        self.year_shortcut = QShortcut(QKeySequence("Alt+Y"), self)
        self.year_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.year_shortcut.activated.connect(lambda: self.year_spin.setFocus())
        
        self.series_shortcut = QShortcut(QKeySequence("Alt+I"), self)
        self.series_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.series_shortcut.activated.connect(lambda: self.series_edit.setFocus())
        
        self.genre_shortcut = QShortcut(QKeySequence("Alt+G"), self)
        self.genre_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.genre_shortcut.activated.connect(lambda: self.genre_edit.setFocus())
        
        self.save_shortcut = QShortcut(QKeySequence("Alt+S"), self)
        self.save_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.save_shortcut.activated.connect(lambda: self.save_button.click())
    
    def on_show_shortcuts(self):
        """F1 shortcut - show help with standard table format."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Keyboard Shortcuts - Web Details")
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
            ("Alt+I", "Series"),
            ("Alt+G", "Genre"),
            ("Alt+S", "Save"),
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

        QTimer.singleShot(0, lambda: table.setFocus(Qt.TabFocusReason))
        dlg.exec()
    
    def on_read_status_bar(self):
        """Alt+/ shortcut - read status."""
        status_text = self.status_bar.currentMessage() or self._default_status_message
        from src.accessibility.style_helpers import exec_styled_message_box, build_accessible_message_box_style
        if QAccessible.isActive():
            self.set_status(status_text, announce=True)
        else:
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Information,
                title="Alt+/ Test",
                text=f"Alt+/ working! Status: {status_text}"
            )
    
    def set_status(self, message: str, announce: bool = False):
        """Set status message."""
        self._default_status_message = message
        self.status_bar.showMessage(message)
        
        if announce:
            from src.accessibility.accessible_events import announce_status_message
            announce_status_message(self.status_bar, message, move_focus=True)
    
    def accept(self):
        """Save and accept - update database and refresh book details."""
        self.set_status("Saving web metadata...")
        
        if self.book and self.db:
            try:
                # Handle author - get or create author ID
                author_name = self.author_edit.text().strip()
                if author_name:
                    author = self.author_queries.get_by_name(author_name)
                    if not author:
                        author_id = self.author_queries.insert(author_name)
                    else:
                        author_id = author.author_id
                else:
                    author_id = None
                
                # Handle series - get or create series ID
                series_text = self.series_edit.text().strip()
                series_id = None
                series_number = None
                if series_text:
                    # Extract series name and number
                    if " - " in series_text:
                        parts = series_text.split(" - ")
                        series_name = parts[0].strip()
                        try:
                            series_number = int(parts[1].strip())
                        except ValueError:
                            series_number = None
                    else:
                        series_name = series_text
                    
                    if series_name:
                        series = self.series_queries.get_by_name(series_name)
                        if not series:
                            series_id = self.series_queries.insert(series_name)
                        else:
                            series_id = series.series_id
                
                # Handle genre - get or create genre ID
                genre_name = self.genre_edit.text().strip()
                if genre_name:
                    genre = self.genre_queries.get_by_name(genre_name)
                    if not genre:
                        genre_id = self.genre_queries.insert(genre_name)
                    else:
                        genre_id = genre.genre_id
                else:
                    genre_id = None
                
                # Update book object with web metadata (filtered)
                title_text = self.title_edit.text().strip()
                author_text = self.author_edit.text().strip()
                
                # Filter out test artifacts
                title_text = title_text.replace(" - WEB EDITION", "").strip()
                author_text = author_text.replace(" (Web Verified)", "").strip()
                
                self.book.title = title_text
                self.book.author_id = author_id
                self.book.comments = self.plot_edit.toPlainText().strip()
                self.book.year = self.year_spin.value()
                self.book.series_id = series_id
                self.book.genre_id = genre_id
                
                # Save to database using BookQueries
                self.book_queries.update(self.book)
                
                # Set status and close
                self.set_status("Web metadata saved successfully")
                
                # Call refresh callback if provided
                if self.refresh_callback:
                    self.refresh_callback()
                
                announce_dialog_closed(self)
                super().accept()
                
            except Exception as e:
                self.set_status(f"Error saving: {str(e)}")
                # Don't close on error
                return
        else:
            # No book or database - just close
            announce_dialog_closed(self)
            super().accept()
    
    def reject(self):
        """Handle close - discard changes as requested."""
        announce_dialog_closed(self)
        super().reject()


def test_web_metadata():
    """Test web metadata window with proven accessibility."""
    app = QApplication(sys.argv)
    
    print("=== Web Metadata Window Test ===")
    print("Built from PROVEN accessible skeleton")
    print("F1, Alt+/, Escape should work")
    print("All field shortcuts should work")
    print("=====================================")
    
    # Create dummy objects for testing
    from src.accessibility.scaling import UIScaler
    from src.accessibility.theme_manager import ThemeManager
    app_instance = QApplication.instance()
    scaler = UIScaler(app_instance)
    theme_manager = ThemeManager(app_instance)
    
    # Create dummy book
    from src.database import Book
    book = Book(
        title="Test Book Title",
        author_name="Test Author Name",
        comments="Test plot description here",
        year=2023,
        series_name="Test Series",
        genre_name="Test Genre"
    )
    
    window = WebMetadataWindow(
        db=None, 
        book=book, 
        scaler=scaler, 
        theme_manager=theme_manager,
        refresh_callback=None  # No callback needed for test
    )
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(test_web_metadata())
