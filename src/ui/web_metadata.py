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
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QCheckBox,
    QWidget, QSizePolicy
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
        self.setWindowTitle("Web Book Details")
        self.setAccessibleName("Web Book Details Window")
        self.setAccessibleDescription("Window for reviewing and accepting web-fetched book metadata")
        self.setMinimumSize(800, 500)  # Wider for title/author, same height
        self.resize(900, 600)  # Wider window - was 700x600
        
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
        layout.setContentsMargins(20, 20, 20, 20)  # Match backup
        layout.setSpacing(15)  # Match backup spacing
        self.setup_ui(layout)
        
        # Status bar (add after layout like book_details)
        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        layout.addWidget(self.status_bar)
        
        # Setup shortcuts (add field shortcuts here)
        self.setup_shortcuts()
        
        # Apply field styling like backup window
        self.apply_field_styling()
        
        # Load data and set status
        self.load_book_data()
        self.set_status("Ready")
        announce_dialog_opened(self, "Web Details")
    
    def setup_ui(self, layout):
        """
        Web metadata UI - match book_details layout exactly.
        """
        # Form layout for book details - EXACT backup match
        form_layout = QFormLayout()
        form_layout.setSpacing(3)  # EXACT backup spacing
        form_layout.setContentsMargins(20, 20, 20, 20)  # EXACT backup margins
        
        # Set proper alignment for labels and fields - EXACT backup values
        form_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # EXACT backup
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)  # EXACT backup
        
        # Title field - add directly like backup
        self.title_edit = QLineEdit()
        self.title_edit.setAccessibleName("Title")
        self.title_edit.setAccessibleDescription("Book title from web source")
        self.title_edit.setMaximumWidth(600)
        title_label = QLabel("&Title:")
        title_label.setBuddy(self.title_edit)
        form_layout.addRow(title_label, self.title_edit)
        
        # Author field - add directly like backup
        self.author_edit = QLineEdit()
        self.author_edit.setAccessibleName("Author")
        self.author_edit.setAccessibleDescription("Author name from web source")
        self.author_edit.setMaximumWidth(400)
        author_label = QLabel("&Author:")
        author_label.setBuddy(self.author_edit)
        form_layout.addRow(author_label, self.author_edit)
        
        # Year field - add directly like backup
        self.year_edit = QLineEdit()
        self.year_edit.setAccessibleName("Publication year")
        self.year_edit.setAccessibleDescription("Publication year from web source")
        self.year_edit.setMaximumWidth(80)
        self.year_edit.setPlaceholderText("YYYY")
        year_label = QLabel("&Year:")
        year_label.setBuddy(self.year_edit)
        form_layout.addRow(year_label, self.year_edit)
        
        # Series field - add directly like backup
        self.series_edit = QLineEdit()
        self.series_edit.setAccessibleName("Series")
        self.series_edit.setAccessibleDescription("Series name from web source")
        self.series_edit.setMaximumWidth(300)
        series_label = QLabel("Ser&ies:")
        series_label.setBuddy(self.series_edit)
        form_layout.addRow(series_label, self.series_edit)
        
        # Genre field - add directly like backup
        self.genre_edit = QLineEdit()
        self.genre_edit.setAccessibleName("Genre")
        self.genre_edit.setAccessibleDescription("Genre from web source")
        self.genre_edit.setMaximumWidth(200)
        genre_label = QLabel("&Genre:")
        genre_label.setBuddy(self.genre_edit)
        form_layout.addRow(genre_label, self.genre_edit)
        
        # Plot field (no indicator as requested)
        self.plot_edit = QTextEdit()
        self.plot_edit.setAccessibleName("Plot Summary")
        self.plot_edit.setAccessibleDescription("Plot summary from web source")
        self.plot_edit.setTabChangesFocus(True)
        self.plot_edit.setMaximumHeight(120)  # Match backup window
        plot_label = QLabel("&Plot:")
        plot_label.setBuddy(self.plot_edit)
        form_layout.addRow(plot_label, self.plot_edit)
        
        layout.addLayout(form_layout)
        
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
    
    def apply_field_styling(self):
        """Apply field styling like backup window."""
        # Apply F1 popup style to fields
        from src.accessibility.shortcut_helpers import build_accessible_f1_popup_style
        field_style = build_accessible_f1_popup_style()
        
        for field in self.findChildren(QLineEdit):
            field.setStyleSheet(field_style)
        
        for field in self.findChildren(QTextEdit):
            field.setStyleSheet(field_style)
    
    def _create_field_with_indicator(self, field):
        """Create a field with web data difference indicator."""
        from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
        
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)  # Reduced spacing to prevent excessive gaps
        
        # Set container to match field height - EXACT backup values
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # The actual field
        layout.addWidget(field)
        
        # Difference indicator (check mark for web data)
        indicator = QLabel("✓")
        indicator.setAccessibleName("Web data indicator")
        indicator.setAccessibleDescription("This field contains web-fetched data")
        indicator.setStyleSheet("color: #2E8B57; font-weight: bold;")  # Sea green
        indicator.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        indicator.setAlignment(Qt.AlignCenter)
        layout.addWidget(indicator)
        
        return container
    
    def load_book_data(self):
        """Load book data into fields and fetch web data."""
        if self.book:
            self.title_edit.setText(self.book.title or "")
            self.author_edit.setText(self.book.author_name or "")
            self.plot_edit.setPlainText(self.book.comments or "")
            self.year_edit.setText(str(self.book.year) if self.book.year else "")
            self.series_edit.setText(self.book.series_name or "")
            self.genre_edit.setText(self.book.genre_name or "")
        
        # Auto-fetch web data when window opens
        self.fetch_web_data()
    
    def fetch_web_data(self):
        """Fetch web data from API with status updates."""
        self.set_status("Fetching web data...")
        
        # Get current book info
        title = self.book.title
        author = self.book.author_name
        
        # Fetch web data
        web_data = self.simulate_web_fetch(title, author)
        
        if web_data:
            self.update_fields_with_web_data(web_data)
            self.show_changes_popup(web_data)
            self.set_status("Web data fetched successfully")
        else:
            self.set_status("No web data found - book not matched")
            # Clear all indicators to indicate no web data
            self.clear_web_indicators()
    
    def simulate_web_fetch(self, title, author):
        """Fetch real web data from Google Books API."""
        try:
            import requests
        except ImportError:
            # requests not available, return None
            print("requests module not available - web fetching disabled")
            return None
        
        import json
        
        if not title or not author:
            return None
            
        try:
            # Build Google Books API query
            query = f"{title} {author}"
            url = f"https://www.googleapis.com/books/v1/volumes?q={requests.utils.quote(query)}&maxResults=1"
            
            # Make API request
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                if data.get('items') and len(data['items']) > 0:
                    book = data['items'][0]['volumeInfo']
                    
                    # Validate that this is a good match
                    api_title = book.get('title', '').lower()
                    api_author = book.get('authors', [])
                    api_author_str = ', '.join(api_author).lower() if api_author else ''
                    
                    title_lower = title.lower()
                    author_lower = author.lower()
                    
                    # Check for basic title similarity (at least 50% match)
                    import difflib
                    title_similarity = difflib.SequenceMatcher(None, title_lower, api_title).ratio()
                    
                    # Check if author name appears in API authors
                    author_match = any(author_lower in auth.lower() for auth in api_author) if api_author else False
                    
                    # Only accept if we have reasonable title match AND author match
                    if title_similarity > 0.5 and author_match:
                        # Extract relevant data
                        result = {
                            'title': book.get('title', ''),
                            'author': ', '.join(book.get('authors', [])),
                            'year': None,
                            'series': None,
                            'genre': None,
                            'plot': book.get('description', '')
                        }
                        
                        # Extract year from publication date
                        pub_date = book.get('publishedDate', '')
                        if pub_date:
                            import re
                            year_match = re.search(r'(\d{4})', pub_date)
                            if year_match:
                                try:
                                    result['year'] = int(year_match.group(1))
                                except ValueError:
                                    pass
                        
                        # Extract genre from categories
                        if 'categories' in book and book['categories']:
                            result['genre'] = book['categories'][0]
                        
                        # Extract series from title (common pattern: "Series Name, Book #")
                        title_text = book.get('title', '')
                        if ', ' in title_text:
                            parts = title_text.split(', ')
                            if len(parts) >= 2 and 'book' in parts[1].lower():
                                result['series'] = parts[0]
                        
                        return result
                    else:
                        print(f"Poor match: title similarity {title_similarity:.2f}, author match {author_match}")
                        return None
                    
        except Exception as e:
            print(f"Web fetch error: {e}")
            
        return None
    
    def generate_realistic_plot(self, title):
        """Generate a more realistic plot based on title keywords."""
        title_lower = title.lower()
        
        if 'bones' in title_lower:
            return "A chilling discovery of skeletal remains leads detective Charlie Parker on a journey into the past, uncovering secrets that were meant to stay buried forever."
        elif 'mystery' in title_lower:
            return "When a mysterious stranger arrives in town, long-buried secrets begin to surface, threatening to destroy the peaceful community."
        elif 'thriller' in title_lower:
            return "A fast-paced thriller that keeps readers on the edge of their seats as the protagonist races against time to prevent a catastrophic event."
        elif 'detective' in title_lower:
            return "A brilliant detective must use all their skills to solve a seemingly impossible case that has stumped everyone else."
        elif 'murder' in title_lower:
            return "A brutal murder rocks a small town, revealing dark secrets that everyone thought were long forgotten."
        else:
            return "A compelling story that explores the depths of human nature and the choices we make when faced with impossible situations."
    
    def update_fields_with_web_data(self, web_data):
        """Update UI fields with web data and track differences."""
        changes_made = False
        
        # Track differences for popup
        self.field_differences = {}
        
        # Compare and update title
        if web_data.get('title') and web_data['title'] != self.book.title:
            self.title_edit.setText(web_data['title'])
            self.field_differences['title'] = web_data['title']
            changes_made = True
        
        # Compare and update author
        if web_data.get('author') and web_data['author'] != self.book.author_name:
            self.author_edit.setText(web_data['author'])
            self.field_differences['author'] = web_data['author']
            changes_made = True
        
        # Compare and update year
        if web_data.get('year') and str(web_data['year']) != self.year_edit.text():
            self.year_edit.setText(str(web_data['year']))
            self.field_differences['year'] = str(web_data['year'])
            changes_made = True
        
        # Compare and update series
        if web_data.get('series') and web_data['series'] != self.book.series_name:
            self.series_edit.setText(web_data['series'])
            self.field_differences['series'] = web_data['series']
            changes_made = True
        
        # Compare and update genre
        if web_data.get('genre') and web_data['genre'] != self.book.genre_name:
            self.genre_edit.setText(web_data['genre'])
            self.field_differences['genre'] = web_data['genre']
            changes_made = True
        
        # Compare and update plot (show found/not found)
        if web_data.get('plot'):
            if web_data['plot'] != self.book.comments:
                self.plot_edit.setPlainText(web_data['plot'])
                self.field_differences['plot'] = 'found'
                changes_made = True
        
        return changes_made
    
    def show_changes_popup(self, web_data):
        """Show popup with only fields that changed."""
        if not hasattr(self, 'field_differences') or not self.field_differences:
            return
            
        # Build changes message
        message_lines = ["Web Data Changes Found:"]
        for field, value in self.field_differences.items():
            if field == 'plot':
                field_name = 'Plot'
                display_value = 'found' if value == 'found' else 'not found'
            elif field == 'series':
                field_name = 'Series'
                display_value = value
            elif field == 'genre':
                field_name = 'Genre'
                display_value = value
            elif field == 'author':
                field_name = 'Author'
                display_value = value
            elif field == 'year':
                field_name = 'Year'
                display_value = value
            elif field == 'title':
                field_name = 'Title'
                display_value = value
            else:
                field_name = field.capitalize()
                display_value = value
            
            message_lines.append(f"{field_name} - {display_value}")
        
        # Show popup
        from PySide6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("Web Data Changes")
        msg.setText("\n".join(message_lines))
        msg.setIcon(QMessageBox.Information)
        msg.exec()
    
    def show_indicator(self, field, show):
        """Show or hide the web data indicator for a field."""
        # Find the container widget that holds the field and indicator
        parent = field.parent()
        if parent and isinstance(parent, QWidget):
            # Find the indicator label (should be the last child)
            for child in parent.children():
                if isinstance(child, QLabel) and child.text() == "✓":
                    child.setVisible(show)
                    break
    
    def clear_web_indicators(self):
        """Clear all web data indicators."""
        self.show_indicator(self.title_edit, False)
        self.show_indicator(self.author_edit, False)
        self.show_indicator(self.year_edit, False)
        self.show_indicator(self.series_edit, False)
        self.show_indicator(self.genre_edit, False)
    
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
                
                # Always call refresh callback to auto-save in book details
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
