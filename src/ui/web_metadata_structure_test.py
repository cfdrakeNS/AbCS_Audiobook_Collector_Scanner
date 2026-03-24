"""
Test window with same structure as web_metadata but minimal
"""

import sys
import os

# Add the project root to Python path
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


class WebMetadataTestWindow(QDialog):
    """Test window with web_metadata structure but minimal content."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_NativeWindow, True)
        # No modality - like test window
        
        # Setup like web_metadata
        app = QApplication.instance()
        self.scaler = UIScaler(app)
        self.theme_manager = ThemeManager(app)
        self._default_status_message = "Ready"
        
        # Simple UI like web_metadata
        layout = QVBoxLayout(self)
        
        # Form like web_metadata
        form = QFormLayout()
        
        # Title field
        title_label = QLabel("&Title:")
        self.title_edit = QLineEdit()
        title_label.setBuddy(self.title_edit)
        form.addRow(title_label, self.title_edit)
        
        # Author field  
        author_label = QLabel("&Author:")
        self.author_edit = QLineEdit()
        author_label.setBuddy(self.author_edit)
        form.addRow(author_label, self.author_edit)
        
        layout.addLayout(form)
        
        # Buttons like web_metadata
        button_layout = QHBoxLayout()
        save_button = QPushButton("&Save")
        button_layout.addWidget(save_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Status bar like web_metadata
        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        layout.addWidget(self.status_bar)
        
        # Setup shortcuts - exact copy from working test
        self.setup_shortcuts()
        
        # Set status
        self.set_status("Ready")
        announce_dialog_opened(self, "Web Metadata Test")
    
    def setup_shortcuts(self):
        """Setup shortcuts - exact copy from working test window."""
        # F1 - local shortcut
        self.help_shortcut = QShortcut(QKeySequence("F1"), self)
        self.help_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.help_shortcut.activated.connect(self.on_show_shortcuts)
        
        # Escape - local shortcut
        self.close_shortcut = QShortcut(QKeySequence("Escape"), self)
        self.close_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.close_shortcut.activated.connect(self.reject)
        
        # Alt+/ - local shortcut
        self.read_status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.read_status_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.read_status_shortcut.activated.connect(self.on_read_status_bar)
    
    def on_show_shortcuts(self):
        """F1 shortcut test."""
        from PySide6.QtWidgets import QMessageBox
        from src.accessibility.style_helpers import exec_styled_message_box, build_accessible_message_box_style
        exec_styled_message_box(
            self,
            self.scaler.get_scaled_size(20),
            icon=QMessageBox.Information,
            title="F1 Test",
            text="F1 shortcut is working in web_metadata structure!"
        )
    
    def on_read_status_bar(self):
        """Alt+/ shortcut test."""
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


def test_web_metadata_structure():
    """Test web_metadata structure with working shortcuts."""
    app = QApplication(sys.argv)
    
    print("=== Web Metadata Structure Test ===")
    print("Test F1: Should show message box")
    print("Test Alt+/: Should read status")
    print("Test Escape: Should close window")
    print("================================")
    
    window = WebMetadataTestWindow()
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(test_web_metadata_structure())
