"""
Accessibility Patterns Mixin
Provides all accessibility patterns for standalone applications
"""

from PySide6.QtCore import Qt, QEvent, QTimer
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QAccessible


class AccessibilityMixin:
    """
    Mixin providing complete accessibility patterns.
    
    This mixin can be added to any QDialog to make it fully accessible.
    All patterns are self-contained - no external dependencies.
    """
    
    # Alt+letter allowlist - blocks unmapped Alt+keys for JAWS
    ALLOWED_ALT_LETTERS = {'/', '?', 'T', 'C', 'Y', 'I', 'L', 'S', 'D', 'F1'}
    
    def init_accessibility(self):
        """Initialize accessibility patterns."""
        self._default_status_message = "Ready"
        self.installEventFilter(self)
    
    def eventFilter(self, source, event):
        """Complete event filter with Alt+key hygiene and combo anti-noise."""
        # Alt+letter hygiene
        if event.type() in (QEvent.ShortcutOverride, QEvent.KeyPress) and bool(event.modifiers() & Qt.AltModifier):
            key_text = event.text().upper()
            if key_text and key_text.isalpha() and key_text not in self.ALLOWED_ALT_LETTERS:
                QApplication.beep()  # User feedback
                return True  # Block unmapped Alt+letters
        
        # Combo box anti-noise pattern
        if hasattr(source, '__class__') and source.__class__.__name__ == 'QComboBox' and hasattr(source, 'isEditable') and source.isEditable():
            if event.type() == QEvent.KeyPress:
                if event.key() in (Qt.Key_Up, Qt.Key_Down):
                    if bool(event.modifiers() & Qt.AltModifier):
                        # Allow Alt+Down to open dropdown
                        return super().eventFilter(source, event) if hasattr(super(), 'eventFilter') else False
                    else:
                        # Block plain arrow keys
                        QApplication.beep()
                        return True
                elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
                    # Enter commits typed value and moves focus
                    if hasattr(source, 'lineEdit'):
                        source.lineEdit().returnPressed.emit()
                    self.focusNextChild()
                    return True
        
        return super().eventFilter(source, event) if hasattr(super(), 'eventFilter') else False
    
    def keyPressEvent(self, event):
        """Handle Enter key for buttons (avoid global shortcuts)."""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            focused_widget = self.focusWidget()
            if hasattr(focused_widget, '__class__') and focused_widget.__class__.__name__ == 'QPushButton':
                focused_widget.click()
                event.accept()
                return
        super().keyPressEvent(event)
    
    def set_status(self, message: str, announce: bool = False):
        """Set status message with optional screen reader announcement."""
        self._default_status_message = message
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage(message)
        
        if announce and QAccessible.isActive():
            # Simple announcement for screen readers
            QTimer.singleShot(100, lambda: self._announce_to_screen_reader(message))
    
    def _announce_to_screen_reader(self, message: str):
        """Announce message to screen reader."""
        # Simple screen reader announcement
        if hasattr(self, 'status_bar') and self.status_bar:
            self.status_bar.showMessage(message)
            # Force screen reader to read
            self.status_bar.setFocus()
            QTimer.singleShot(50, lambda: self.clear_focus())
    
    def clear_focus(self):
        """Clear focus from status bar."""
        if hasattr(self, 'title_edit'):
            self.title_edit.setFocus()
    
    def announce_dialog_opened(self, title: str):
        """Announce dialog opened."""
        if QAccessible.isActive():
            self.set_status(f"{title} window opened", announce=True)
    
    def announce_dialog_closed(self):
        """Announce dialog closed."""
        if QAccessible.isActive():
            # Dialog closing announcement handled by system
            pass
