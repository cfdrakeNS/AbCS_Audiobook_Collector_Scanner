"""
Simple web metadata window - build incrementally from working base
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


class SimpleWebMetadataWindow(QDialog):
    """Simple web metadata window - build from working base."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Web Metadata - Simple")
        self.setAccessibleName("Web Metadata Window")
        self.setAttribute(Qt.WA_NativeWindow, True)
        
        # Basic setup
        app = QApplication.instance()
        self.scaler = UIScaler(app)
        self.theme_manager = ThemeManager(app)
        self._default_status_message = "Ready"
        
        # Simple UI
        layout = QVBoxLayout(self)
        
        # Status bar (like working test)
        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        layout.addWidget(self.status_bar)
        
        # Basic shortcuts that work
        self.setup_shortcuts()
        
        # Set initial status
        self.set_status("Ready")
        announce_dialog_opened(self, "Web Metadata Simple")
    
    def setup_shortcuts(self):
        """Setup shortcuts - exact working pattern."""
        # F1 - local shortcut (works in test)
        self.help_shortcut = QShortcut(QKeySequence("F1"), self)
        self.help_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.help_shortcut.activated.connect(self.on_show_shortcuts)
        
        # Escape - local shortcut (works in test)
        self.close_shortcut = QShortcut(QKeySequence("Escape"), self)
        self.close_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.close_shortcut.activated.connect(self.reject)
        
        # Alt+/ - local shortcut (works in test)
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
            text="F1 shortcut working! Web metadata simple window."
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


def test_simple_window():
    """Test simple web metadata window."""
    app = QApplication(sys.argv)
    
    print("=== Simple Web Metadata Test ===")
    print("Step 1: Test F1 (should show help)")
    print("Step 2: Test Alt+/ (should read status)")
    print("Step 3: Test Escape (should close)")
    print("==================================")
    
    window = SimpleWebMetadataWindow()
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(test_simple_window())
