"""
Minimal accessibility test window
Just test F1 and Alt+/ to see if basic shortcuts work
"""

import sys
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QApplication, QStatusBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QShortcut, QKeySequence, QAccessible

from src.accessibility.scaling import UIScaler
from src.accessibility.theme_manager import ThemeManager
from src.accessibility.accessible_events import announce_dialog_opened, announce_dialog_closed


class MinimalTestWindow(QDialog):
    """Minimal test window for accessibility shortcuts."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Accessibility Test Window")
        self.setAccessibleName("Accessibility Test Window")
        
        # Basic setup - need app instance for UIScaler
        app = QApplication.instance()
        self.scaler = UIScaler(app)
        self.theme_manager = ThemeManager(app)
        self._default_status_message = "Ready"
        
        # Simple UI
        layout = QVBoxLayout(self)
        
        label = QLabel("Test Window")
        label.setAccessibleName("Test Label")
        layout.addWidget(label)
        
        button = QPushButton("Test Button")
        button.setAccessibleName("Test Button")
        layout.addWidget(button)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        layout.addWidget(self.status_bar)
        
        # Setup shortcuts - EXACT copy from import_detail
        self.setup_shortcuts()
        
        # Set initial status
        self.set_status("Ready")
        announce_dialog_opened(self, "Accessibility Test Window")
    
    def setup_shortcuts(self):
        """Setup shortcuts - exact copy from import_detail."""
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
            text="F1 shortcut is working!"
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
                icon=None,
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MinimalTestWindow()
    window.show()
    sys.exit(app.exec())
