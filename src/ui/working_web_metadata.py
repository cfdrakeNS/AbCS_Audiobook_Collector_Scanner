"""
Web metadata window - start from PROVEN working accessibility base
Copy exact working accessibility_test_window.py and add web metadata fields
"""

import sys
import os

# Add to project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QApplication, QStatusBar, QLineEdit, QTextEdit, QSpinBox, QFormLayout, QHBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QShortcut, QKeySequence, QAccessible

from src.accessibility.scaling import UIScaler
from src.accessibility.theme_manager import ThemeManager
from src.accessibility.accessible_events import announce_dialog_opened, announce_dialog_closed
from src.database import DatabaseManager, Book


class WorkingWebMetadataWindow(QDialog):
    """Web metadata window - start from PROVEN working base."""
    
    def __init__(self, db: DatabaseManager, book: Book, scaler: UIScaler, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Web Details: Simple")
        self.setAccessibleName("Web Details Window")
        self.setAttribute(Qt.WA_NativeWindow, True)
        
        # Basic setup - EXACT copy from working test
        self.scaler = scaler
        self.theme_manager = theme_manager
        self._default_status_message = "Ready"
        
        # Database objects
        self.db = db
        self.book = book
        
        # Simple UI with web metadata fields
        layout = QVBoxLayout(self)
        
        # Form for fields
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
        
        layout.addLayout(form)
        
        # Save button
        button_layout = QHBoxLayout()
        save_button = QPushButton("&Save")
        save_button.setAccessibleName("Save")
        save_button.setAccessibleDescription("Save web metadata changes - Alt+S")
        save_button.clicked.connect(self.accept)
        button_layout.addWidget(save_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Status bar (exact copy from working test)
        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        layout.addWidget(self.status_bar)
        
        # Setup shortcuts - EXACT copy from working test
        self.setup_shortcuts()
        
        # Load data and set status
        self.load_data()
        self.set_status("Ready")
        announce_dialog_opened(self, "Web Details")
    
    def load_data(self):
        """Load book data into fields."""
        if self.book:
            self.title_edit.setText(self.book.title or "")
            self.author_edit.setText(self.book.author_name or "")
            self.plot_edit.setPlainText(self.book.comments or "")
            self.year_spin.setValue(self.book.year or 0)
    
    def setup_shortcuts(self):
        """Setup shortcuts - EXACT copy from working test window."""
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
    
    def on_show_shortcuts(self):
        """F1 shortcut - show help."""
        from PySide6.QtWidgets import QMessageBox
        from src.accessibility.style_helpers import exec_styled_message_box, build_accessible_message_box_style
        exec_styled_message_box(
            self,
            self.scaler.get_scaled_size(20),
            icon=QMessageBox.Information,
            title="F1 Help",
            text="F1 shortcut working! Web metadata with proven accessibility base."
        )
    
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
    
    def reject(self):
        """Handle close."""
        announce_dialog_closed(self)
        super().reject()


def test_working_web_metadata():
    """Test web metadata window with proven accessibility base."""
    app = QApplication(sys.argv)
    
    print("=== Working Web Metadata Test ===")
    print("Base: PROVEN accessibility test window")
    print("Added: Web metadata fields")
    print("Test F1, Alt+/, Escape")
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
        title="Test Book",
        author_name="Test Author",
        comments="Test plot",
        year=2023
    )
    
    window = WorkingWebMetadataWindow(
        db=None, 
        book=book, 
        scaler=scaler, 
        theme_manager=theme_manager
    )
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(test_working_web_metadata())
