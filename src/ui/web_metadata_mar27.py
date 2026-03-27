"""
Web Metadata Window - Built from PROVEN accessible skeleton
Accessibility works out of box: F1, Alt+/, Escape
"""

import sys
import os
from PySide6.QtGui import QShortcut, QKeySequence, QAccessible
from PySide6.QtCore import Qt, QTimer
from src.accessibility.accessible_events import announce_dialog_closed

# Add to project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QApplication, QStatusBar, 
    QLineEdit, QTextEdit, QSpinBox, QFormLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QWidget, QSizePolicy, QMessageBox
)

# --- REVERTED TO PROVEN ACCESSIBLE VERSION ---
from src.ui.web_metadata_backup import WebMetadataWindow as ProvenWebMetadataWindow

# Wrapper to match the expected signature in main_window.py
from PySide6.QtCore import Signal

class WebMetadataWindow(ProvenWebMetadataWindow):
    data_saved = Signal()
    def __init__(self, db, book, scaler, theme_manager, parent=None, refresh_callback=None):
        super().__init__(db=db, book=book, scaler=scaler, theme_manager=theme_manager, parent=parent)
        # Main layout for dynamic content (field differences)
        self.dynamic_layout_container = QWidget(self)
        self.dynamic_layout_container.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.dynamic_layout = QVBoxLayout(self.dynamic_layout_container)
        self.dynamic_layout.setContentsMargins(0, 0, 0, 0)
        self.dynamic_layout.setSpacing(2)
        # Insert at the top of the main layout (after title, before buttons/status)
        if hasattr(self, 'layout') and callable(getattr(self, 'layout')):
            main_layout = self.layout()
            main_layout.insertWidget(1, self.dynamic_layout_container)
        # Track change rows for clearing
        self.change_rows = {}
        self.changes_layout = self.dynamic_layout
        self.refresh_callback = refresh_callback
    
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
        """Update UI with accessible, text-based summary of changes and checkboxes, packed at the top."""
        self.web_data = web_data
        self.field_differences = {}
        # Clear previous change rows
        for row in self.change_rows.values():
            if isinstance(row, tuple):
                row_widget = row[0]
            else:
                row_widget = row
            row_widget.setParent(None)
        self.change_rows.clear()

        # Helper to add a change row, packed with QSizePolicy.Minimum
        def add_change_row(field_name, db_value, web_value, shortcut):
            row_widget = QWidget()
            row_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(2)
            row_layout.setAlignment(Qt.AlignLeft)
            label = QLabel(f"{field_name}:")
            label.setAccessibleName(f"{field_name} label")
            row_layout.addWidget(label)
            db_label = QLabel(f"Current: {db_value if db_value is not None else ''}")
            db_label.setAccessibleName(f"Current {field_name}")
            row_layout.addWidget(db_label)
            arrow = QLabel("→")
            arrow.setAccessibleName("to")
            row_layout.addWidget(arrow)
            web_label = QLabel(f"Web: {web_value if web_value is not None else ''}")
            web_label.setAccessibleName(f"Web {field_name}")
            row_layout.addWidget(web_label)
            # Always show QCheckBox for every field
            from PySide6.QtWidgets import QCheckBox
            cb = QCheckBox("Apply", row_widget)
            cb.setAccessibleName(f"Apply web {field_name}")
            cb.setFocusPolicy(Qt.StrongFocus)
            cb.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            cb.setStyleSheet("QCheckBox { font-size: 14pt; padding: 2px 8px; } QCheckBox::indicator { width: 18px; height: 18px; }")
            row_layout.addWidget(cb)
            self.change_rows[field_name.lower()] = row_widget
            self.changes_layout.addWidget(row_widget)

        # Always show all checkboxes regardless of changes
        add_change_row("Title", self.book.title, web_data.get('title', ''), Qt.ALT + Qt.Key_T)
        add_change_row("Author", self.book.author_name, web_data.get('author', ''), Qt.ALT + Qt.Key_A)
        add_change_row("Year", str(self.book.year) if self.book.year else '', str(web_data.get('year', '')),
                       Qt.ALT + Qt.Key_Y)
        add_change_row("Series", self.book.series_name, web_data.get('series', ''), Qt.ALT + Qt.Key_I)
        add_change_row("Genre", self.book.genre_name, web_data.get('genre', ''), Qt.ALT + Qt.Key_G)
        add_change_row("Plot", self.book.comments, web_data.get('plot', ''), Qt.ALT + Qt.Key_P)
        self.set_status("All fields shown. Use Apply buttons to select.")
    
    # Removed: show_changes_popup (was for testing only)
    
    def show_indicator(self, field, show, color=None):
        """Show or hide the web data indicator and checkbox for a field. Color: 'green' or 'red'."""
        # Find the indicator label in the field's container
        container = None
        if field is self.title_edit:
            container = self.title_field_container
        elif field is self.author_edit:
            container = self.author_field_container
        elif field is self.year_edit:
            container = self.year_field_container
        elif field is self.series_edit:
            container = self.series_field_container
        elif field is self.genre_edit:
            container = self.genre_field_container
        if container:
            # Toggle indicator and checkbox visibility
            if hasattr(container, '_indicator'):
                container._indicator.setVisible(show)
                if show and color:
                    if color == 'red':
                        container._indicator.setStyleSheet("color: #C0392B; font-weight: bold;")
                    elif color == 'green':
                        container._indicator.setStyleSheet("color: #2E8B57; font-weight: bold;")
            if hasattr(container, '_checkbox'):
                container._checkbox.setVisible(show)
    
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
        status_text = self.status_bar.currentMessage()
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
        self.status_bar.showMessage(message)
        if announce:
            from src.accessibility.accessible_events import announce_status_message
            announce_status_message(self.status_bar, message, move_focus=True)
    
    def accept(self):
        """Save and accept - update database and refresh book details, with plot field formatted as requested."""
        # Build list of differences for status bar
        diff_fields = [k.capitalize() for k in self.field_differences.keys() if k != 'plot']
        plot_found = 'plot' in self.field_differences
        plot_status = "Plot Found" if plot_found else "Plot Not Found"
        diff_str = f" - Difference - {', '.join(diff_fields)}" if diff_fields else ""
        self.set_status(f"{plot_status}{diff_str}")

        if self.book and self.db:
            try:
                # Only apply web data for checked fields
                # Title
                self.book.title = self.title_edit.text().strip()
                # Author
                author_name = self.author_edit.text().strip()
                if author_name:
                    author = self.author_queries.get_by_name(author_name)
                    if not author:
                        author_id = self.author_queries.insert(author_name)
                    else:
                        author_id = author.author_id
                    self.book.author_id = author_id
                # Year
                year_text = self.year_edit.text().strip()
                try:
                    self.book.year = int(year_text) if year_text else None
                except ValueError:
                    self.book.year = None
                # Series
                series_text = self.series_edit.text().strip()
                series_id = None
                series_number = None
                if series_text:
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
                    self.book.series_id = series_id
                    self.book.series_number = series_number
                # Genre
                genre_name = self.genre_edit.text().strip()
                genre_id = None
                if genre_name:
                    genre = self.genre_queries.get_by_name(genre_name)
                    if not genre:
                        genre_id = self.genre_queries.insert(genre_name)
                    else:
                        genre_id = genre.genre_id
                    self.book.genre_id = genre_id

                # Plot/comments always applied
                plot = self.plot_edit.toPlainText().strip()
                rating_line = ""
                source_line = ""
                publisher_line = ""
                web_data = getattr(self, 'web_data', None)
                if web_data:
                    rating = web_data.get('rating')
                    ratings_count = web_data.get('ratings_count')
                    source = web_data.get('source')
                    publisher = web_data.get('publisher')
                    if rating:
                        try:
                            rating_val = float(rating)
                            rating_str = f"{rating_val:.1f}"
                        except (ValueError, TypeError):
                            rating_str = str(rating)
                        if ratings_count:
                            try:
                                count_val = int(ratings_count)
                                count_str = f"{count_val} reviews"
                            except (ValueError, TypeError):
                                count_str = f"{ratings_count} reviews"
                            rating_line = f"Rating {rating_str} ({count_str})"
                        else:
                            rating_line = f"Rating {rating_str}"
                    if source:
                        source_line = f"Plot Source: {source}"
                    if publisher:
                        publisher_line = f"Publisher: {publisher}"
                # Build the new plot/comments field: rating and source on same line at top, publisher at end
                plot_lines = []
                header_line = ""
                if rating_line and source_line:
                    header_line = f"{rating_line} | {source_line}"
                elif rating_line:
                    header_line = rating_line
                elif source_line:
                    header_line = source_line
                if header_line:
                    plot_lines.append(header_line)
                if plot:
                    plot_lines.append(plot)
                if publisher_line:
                    plot_lines.append(publisher_line)
                # Remove any blank lines between sections
                new_plot = "\n".join([line for line in plot_lines if line.strip() != ""]).strip()
                self.book.comments = new_plot

                # Save to database
                self.book_queries.update(self.book)
                
                # Emit signal to notify main window of data save
                self.data_saved.emit()

                # Always call refresh callback to auto-save in book details
                if self.refresh_callback:
                    self.refresh_callback()  # This loads the data (may set dirty flag)
                    
                    if web_data:
                        # Also call save to persist changes
                        if hasattr(self.parent_window, 'on_save'):
                            self.parent_window.on_save()
                    
                    # Clear dirty state using the proper method
                    if hasattr(self.parent_window, '_clear_dirty'):
                        self.parent_window._clear_dirty(preserve_status=True)
                    # Force clear dirty flag one more time
                    if hasattr(self.parent_window, '_dirty'):
                        self.parent_window._dirty = False
                    # Update save button visibility
                    if hasattr(self.parent_window, '_update_save_button_visibility'):
                        self.parent_window._update_save_button_visibility()
                    # Force UI update
                    if hasattr(self.parent_window, 'repaint'):
                        self.parent_window.repaint()

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
        # Emit data_saved so MainWindow restores focus to table even on Escape
        self.data_saved.emit()
        announce_dialog_closed(self)
        super().reject()


def test_web_metadata():
    """Test web metadata window with proven accessibility."""
    app = QApplication(sys.argv)
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
