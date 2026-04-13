"""
Styled Dialogs Helper
Provides accessible styled message boxes for standalone applications
"""

from PySide6.QtWidgets import QMessageBox, QDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


def show_styled_message_box(parent, icon, title, text, buttons=QMessageBox.Ok, default_button=QMessageBox.Ok):
    """
    Show a styled, accessible message box.
    
    Args:
        parent: Parent widget
        icon: QMessageBox icon (Information, Warning, Question, Critical)
        title: Dialog title
        text: Dialog text
        buttons: Button combination
        default_button: Default button
    
    Returns:
        Button pressed
    """
    msg_box = QMessageBox(parent)
    msg_box.setIcon(icon)
    msg_box.setWindowTitle(title)
    msg_box.setText(text)
    msg_box.setStandardButtons(buttons)
    msg_box.setDefaultButton(default_button)
    
    # Apply accessible styling
    font = QFont()
    font.setPointSize(10)
    msg_box.setFont(font)
    
    # Ensure dialog is accessible
    msg_box.setAccessibleName(title)
    msg_box.setAccessibleDescription(text)
    
    # Make dialog modal for proper focus management
    msg_box.setModal(True)
    
    return msg_box.exec()


class StyledDialog(QDialog):
    """Base class for styled accessible dialogs."""
    
    def __init__(self, parent=None, title="Dialog"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setAccessibleName(title)
        
        # Apply accessible styling
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)
