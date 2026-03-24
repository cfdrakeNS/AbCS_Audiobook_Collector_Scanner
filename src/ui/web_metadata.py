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
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QShortcut, QKeySequence, QAccessible

from src.accessibility.scaling import UIScaler
from src.accessibility.theme_manager import ThemeManager
from src.accessibility.accessible_events import announce_dialog_opened, announce_dialog_closed
from src.database import DatabaseManager, Book


class WebMetadataWindow(QDialog):
    """
    Web metadata window with PROVEN accessibility foundation.
    
    F1, Alt+/, and Escape work out of box.
    Built incrementally from accessible skeleton.
    """
    
    def __init__(self, db: DatabaseManager, book: Book, scaler: UIScaler, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Web Details")
        self.setAccessibleName("Web Details Window")
        self.setAttribute(Qt.WA_NativeWindow, True)
        
        # Basic setup - PROVEN pattern
        self.scaler = scaler
        self.theme_manager = theme_manager
        self._default_status_message = "Ready"
        
        # Database objects
        self.db = db
        self.book = book
        
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
        
        # Title field
        title_label = QLabel("&Title:")
        self.title_edit = QLineEdit()
        self.title_edit.setAccessibleName("Book title")
        title_label.setBuddy(self.title_edit)
        form.addRow(title_label, self.title_edit)
        
        # Author field  
        author_label = QLabel("&Author:")
        self.author_edit = QLineEdit()
        self.author_edit.setAccessibleName("Author")
        author_label.setBuddy(self.author_edit)
        form.addRow(author_label, self.author_edit)
        
        # Plot field
        plot_label = QLabel("&Plot:")
        self.plot_edit = QTextEdit()
        self.plot_edit.setAccessibleName("Plot")
        self.plot_edit.setTabChangesFocus(True)
        self.plot_edit.setMinimumHeight(40)
        plot_label.setBuddy(self.plot_edit)
        form.addRow(plot_label, self.plot_edit)
        
        # Year field
        year_label = QLabel("&Year:")
        self.year_spin = QSpinBox()
        self.year_spin.setRange(0, 2100)
        self.year_spin.setValue(0)
        self.year_spin.setAccessibleName("Publication year")
        self.year_spin.setSpecialValueText("")
        self.year_spin.setFixedWidth(110)
        year_label.setBuddy(self.year_spin)
        form.addRow(year_label, self.year_spin)
        
        # Series field
        series_label = QLabel("Ser&ies:")
        self.series_edit = QLineEdit()
        self.series_edit.setAccessibleName("Book series")
        series_label.setBuddy(self.series_edit)
        form.addRow(series_label, self.series_edit)
        
        # Genre field
        genre_label = QLabel("&Genre:")
        self.genre_edit = QLineEdit()
        self.genre_edit.setAccessibleName("Genre")
        genre_label.setBuddy(self.genre_edit)
        form.addRow(genre_label, self.genre_edit)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Launch Tag button
        self.launch_tag_button = QPushButton("Launch Tag")
        self.launch_tag_button.setAccessibleName("Launch Tag")
        self.launch_tag_button.setAccessibleDescription("Open current item in external tag editor - Alt+L")
        self.launch_tag_button.setFocusPolicy(Qt.StrongFocus)
        self.launch_tag_button.clicked.connect(self.on_launch_tag_editor)
        button_layout.addWidget(self.launch_tag_button)
        
        # Save button
        self.save_button = QPushButton("Save")
        self.save_button.setAccessibleName("Save")
        self.save_button.setAccessibleDescription("Save web metadata changes - Alt+S")
        self.save_button.setFocusPolicy(Qt.StrongFocus)
        self.save_button.clicked.connect(self.accept)
        button_layout.addWidget(self.save_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
    
    def load_book_data(self):
        """Load book data into fields."""
        if self.book:
            self.title_edit.setText(self.book.title or "")
            self.author_edit.setText(self.book.author_name or "")
            self.plot_edit.setPlainText(self.book.comments or "")
            self.year_spin.setValue(self.book.year or 0)
            self.series_edit.setText(self.book.series_name or "")
            self.genre_edit.setText(self.book.genre_name or "")
    
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
        
        self.launch_tag_shortcut = QShortcut(QKeySequence("Alt+L"), self)
        self.launch_tag_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.launch_tag_shortcut.activated.connect(lambda: self.launch_tag_button.click())
    
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
            ("Alt+L", "Launch Tag"),
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
    
    def on_launch_tag_editor(self):
        """Launch tag editor."""
        self.set_status("Launch tag functionality not implemented yet")
    
    def set_status(self, message: str, announce: bool = False):
        """Set status message."""
        self._default_status_message = message
        self.status_bar.showMessage(message)
        
        if announce:
            from src.accessibility.accessible_events import announce_status_message
            announce_status_message(self.status_bar, message, move_focus=True)
    
    def accept(self):
        """Save and accept."""
        self.set_status("Saving web metadata...")
        announce_dialog_closed(self)
        super().accept()
    
    def reject(self):
        """Handle close."""
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
        theme_manager=theme_manager
    )
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(test_web_metadata())
