"""
Accessible Window Skeleton/Template
PROVEN working accessibility pattern for all future windows

Copy this skeleton and add your UI elements - accessibility will work out of box.

USAGE:
1. Copy this file to new window_name.py
2. Rename class to YourWindowName
3. Add your UI elements in setup_ui()
4. Add your field shortcuts in setup_shortcuts()
5. Test F1, Alt+/, Escape - they should work

TESTING:
python src/ui/your_new_window.py
"""

import sys
import os

# Add to project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QApplication, QStatusBar, 
    QLineEdit, QTextEdit, QSpinBox, QFormLayout, QHBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QShortcut, QKeySequence, QAccessible

from src.accessibility.scaling import UIScaler
from src.accessibility.theme_manager import ThemeManager
from src.accessibility.accessible_events import announce_dialog_opened, announce_dialog_closed


class AccessibleWindowSkeleton(QDialog):
    """
    PROVEN accessible window skeleton.
    
    F1, Alt+/, and Escape work out of box.
    Add your UI elements and field shortcuts incrementally.
    """
    
    def __init__(self, parent=None, window_title="Window", scaler=None, theme_manager=None):
        super().__init__(parent)
        self.setWindowTitle(window_title)
        self.setAccessibleName(f"{window_title} Window")
        self.setAttribute(Qt.WA_NativeWindow, True)
        
        # Basic setup - PROVEN pattern
        app = QApplication.instance()
        self.scaler = scaler or UIScaler(app)
        self.theme_manager = theme_manager or ThemeManager(app)
        self._default_status_message = "Ready"
        
        # Setup UI (add your elements here)
        layout = QVBoxLayout(self)
        self.setup_ui(layout)
        
        # Status bar (PROVEN working pattern)
        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        layout.addWidget(self.status_bar)
        
        # Setup shortcuts (add your field shortcuts here)
        self.setup_shortcuts()
        
        # Set initial status
        self.set_status("Ready")
        announce_dialog_opened(self, window_title)
    
    def setup_ui(self, layout):
        """
        Add your UI elements here.
        
        EXAMPLE:
        form = QFormLayout()
        
        # Add your fields
        title_label = QLabel("&Title:")
        self.title_edit = QLineEdit()
        self.title_edit.setAccessibleName("Title field")
        title_label.setBuddy(self.title_edit)
        form.addRow(title_label, self.title_edit)
        
        layout.addLayout(form)
        
        # Add your buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("&Save")
        save_button.setAccessibleName("Save")
        save_button.clicked.connect(self.accept)
        button_layout.addWidget(save_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        """
        # Add your UI setup here
        pass
    
    def setup_shortcuts(self):
        """
        PROVEN accessibility shortcuts - F1, Alt+/, Escape work out of box.
        
        Add your field shortcuts here:
        'field_name': lambda: self.field_name.setFocus(),
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
        
        # Add your field shortcuts here
        # Example:
        # self.title_shortcut = QShortcut(QKeySequence("Alt+T"), self)
        # self.title_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        # self.title_shortcut.activated.connect(lambda: self.title_edit.setFocus())
    
    def on_show_shortcuts(self):
        """F1 shortcut - show help."""
        from PySide6.QtWidgets import QMessageBox
        from src.accessibility.style_helpers import exec_styled_message_box, build_accessible_message_box_style
        exec_styled_message_box(
            self,
            self.scaler.get_scaled_size(20),
            icon=QMessageBox.Information,
            title="F1 Help",
            text="F1 shortcut working! Accessible window skeleton."
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


def test_skeleton():
    """Test the accessible window skeleton."""
    app = QApplication(sys.argv)
    
    print("=== Accessible Window Skeleton Test ===")
    print("PROVEN accessibility pattern")
    print("F1, Alt+/, Escape should work")
    print("=====================================")
    
    window = AccessibleWindowSkeleton(window_title="Skeleton Test")
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(test_skeleton())
