"""
Standalone Accessible Sample Application
Demonstrates complete accessibility patterns without AbCS dependencies
"""

import sys
import os

# Add current directory to Python path for standalone operation
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QApplication, QStatusBar, 
    QLineEdit, QTextEdit, QSpinBox, QFormLayout, QHBoxLayout, QComboBox,
    QTableWidget, QTableWidgetItem, QMessageBox
)
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QShortcut, QKeySequence, QAccessible

from accessibility_patterns import AccessibilityMixin
from styled_dialogs import show_styled_message_box


class AccessibleSampleWindow(QDialog, AccessibilityMixin):
    """
    Complete accessible window demonstrating all patterns.
    
    This is a TRUE standalone sample - no AbCS dependencies.
    All accessibility patterns are self-contained.
    """
    
    def __init__(self, parent=None, window_title="Accessible Sample"):
        super().__init__(parent)
        self.setWindowTitle(window_title)
        self.setAccessibleName(f"{window_title} Window")
        self.setAttribute(Qt.WA_NativeWindow, True)
        
        # Initialize accessibility patterns
        self.init_accessibility()
        
        # Setup UI
        layout = QVBoxLayout(self)
        self.setup_ui(layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        layout.addWidget(self.status_bar)
        
        # Setup shortcuts
        self.setup_shortcuts()
        
        # Set initial status
        self.set_status("Ready - All accessibility patterns working")
        self.announce_dialog_opened(window_title)
    
    def setup_ui(self, layout):
        """Complete accessible UI with all patterns demonstrated."""
        form = QFormLayout()
        
        # Text field with accessibility
        title_label = QLabel("&Title:")
        self.title_edit = QLineEdit()
        self.title_edit.setAccessibleName("Title field")
        self.title_edit.setAccessibleDescription("Enter the title here")
        title_label.setBuddy(self.title_edit)
        form.addRow(title_label, self.title_edit)
        
        # Combo box with anti-noise pattern
        category_label = QLabel("&Category:")
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.addItems(["Fiction", "Non-Fiction", "Technical"])
        self.category_combo.setAccessibleName("Category field")
        self.category_combo.setAccessibleDescription("Select or type a category")
        category_label.setBuddy(self.category_combo)
        form.addRow(category_label, self.category_combo)
        
        # Spin box with accessibility
        year_label = QLabel("&Year:")
        self.year_spin = QSpinBox()
        self.year_spin.setRange(1900, 2030)
        self.year_spin.setValue(2026)
        self.year_spin.setAccessibleName("Year field")
        self.year_spin.setAccessibleDescription("Publication year")
        year_label.setBuddy(self.year_spin)
        form.addRow(year_label, self.year_spin)
        
        layout.addLayout(form)
        
        # Table with row number suppression
        table_label = QLabel("Items:")
        self.items_table = QTableWidget(3, 2)
        self.items_table.setHorizontalHeaderLabels(["Name", "Value"])
        
        # Hide row numbers for JAWS compatibility
        self.items_table.verticalHeader().setVisible(False)
        self.items_table.setVerticalHeaderLabels([""] * 3)
        
        # Add meaningful accessible text
        self.items_table.setItem(0, 0, QTableWidgetItem("Item 1"))
        self.items_table.item(0, 0).setData(Qt.AccessibleTextRole, "First item name")
        self.items_table.setItem(0, 1, QTableWidgetItem("100"))
        self.items_table.item(0, 1).setData(Qt.AccessibleTextRole, "First item value: 100")
        
        self.items_table.setAccessibleName("Items table")
        self.items_table.setAccessibleDescription("Table showing item names and values")
        layout.addWidget(table_label)
        layout.addWidget(self.items_table)
        
        # Screen reader-optimized buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save")
        self.save_button.setAccessibleName("Save button")
        self.save_button.setAccessibleDescription("Save the current data")
        self.save_button.clicked.connect(self.on_save)
        button_layout.addWidget(self.save_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.setAccessibleName("Delete button")
        self.delete_button.setAccessibleDescription("Delete selected item")
        self.delete_button.clicked.connect(self.on_delete)
        button_layout.addWidget(self.delete_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Set explicit tab order
        self.setTabOrder(self.title_edit, self.category_combo)
        self.setTabOrder(self.category_combo, self.year_spin)
        self.setTabOrder(self.year_spin, self.items_table)
        self.setTabOrder(self.items_table, self.save_button)
        self.setTabOrder(self.save_button, self.delete_button)
        
        # Install combo box anti-noise event filter
        self.category_combo.installEventFilter(self)
    
    def on_save(self):
        """Screen reader-optimized save with validation feedback."""
        title = self.title_edit.text().strip()
        if not title:
            show_styled_message_box(
                self,
                icon=QMessageBox.Warning,
                title="Validation Error",
                text="Please enter a title before saving."
            )
            self.title_edit.setFocus()
            self.set_status("Save canceled: title is required", announce=True)
            return
        
        self.set_status("Data saved successfully", announce=True)
        self.title_edit.setFocus()
    
    def on_delete(self):
        """Screen reader-optimized delete with selection feedback."""
        if self.items_table.currentRow() == -1:
            show_styled_message_box(
                self,
                icon=QMessageBox.Warning,
                title="No Selection",
                text="Select an item in the table to delete."
            )
            self.set_status("Delete canceled: no item selected", announce=True)
            self.items_table.setFocus()
            return
        
        row = self.items_table.currentRow()
        self.items_table.removeRow(row)
        self.set_status("Item deleted successfully", announce=True)
        if self.items_table.rowCount() > 0:
            self.items_table.setCurrentCell(0, 0)
        self.items_table.setFocus()
    
    def setup_shortcuts(self):
        """All shortcuts implemented locally - no external dependencies."""
        # F1 - Help
        self.help_shortcut = QShortcut(QKeySequence("F1"), self)
        self.help_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.help_shortcut.activated.connect(self.on_show_shortcuts)
        
        # Escape - Close with confirmation
        self.close_shortcut = QShortcut(QKeySequence("Escape"), self)
        self.close_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.close_shortcut.activated.connect(self.on_escape)
        
        # Alt+/ - Read status
        self.read_status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.read_status_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.read_status_shortcut.activated.connect(self.on_read_status)
        
        # Field shortcuts - all local QShortcut objects
        self.title_shortcut = QShortcut(QKeySequence("Alt+T"), self)
        self.title_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.title_shortcut.activated.connect(lambda: self.title_edit.setFocus())
        
        self.category_shortcut = QShortcut(QKeySequence("Alt+C"), self)
        self.category_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.category_shortcut.activated.connect(lambda: self.category_combo.setFocus())
        
        self.year_shortcut = QShortcut(QKeySequence("Alt+Y"), self)
        self.year_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.year_shortcut.activated.connect(lambda: self.year_spin.setFocus())
        
        self.table_shortcut = QShortcut(QKeySequence("Alt+I"), self)
        self.table_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.table_shortcut.activated.connect(lambda: self.items_table.setFocus())
        
        self.table_alt_l_shortcut = QShortcut(QKeySequence("Alt+L"), self)
        self.table_alt_l_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.table_alt_l_shortcut.activated.connect(lambda: self.items_table.setFocus())
        
        self.save_shortcut = QShortcut(QKeySequence("Alt+S"), self)
        self.save_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.save_shortcut.activated.connect(lambda: self.save_button.setFocus())
        
        self.delete_shortcut = QShortcut(QKeySequence("Alt+D"), self)
        self.delete_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.delete_shortcut.activated.connect(lambda: self.delete_button.setFocus())
    
    def on_show_shortcuts(self):
        """F1 - Show complete accessibility help."""
        help_text = """
STANDALONE ACCESSIBLE SAMPLE - All Patterns Working

BASIC SHORTCUTS:
• F1 - Show this help
• Alt+/ - Read status message
• Escape - Close with confirmation

FIELD SHORTCUTS (All Working):
• Alt+T - Focus Title field
• Alt+C - Focus Category field
• Alt+Y - Focus Year field
• Alt+I - Focus Items table
• Alt+L - Focus Items table
• Alt+S - Focus Save button
• Alt+D - Focus Delete button

ACCESSIBILITY PATTERNS:
✓ Status bar with Alt+/ readback
✓ Alt+letter hygiene (blocks unmapped keys)
✓ Combo box anti-noise (blocks plain arrows)
✓ Table row suppression for JAWS
✓ Screen reader-optimized buttons
✓ Focus management after operations
✓ Explicit tab order
✓ Modal message boxes with styling
✓ Global Enter avoidance (uses keyPressEvent)

COMBO BOX BEHAVIOR:
• Alt+Down - Open dropdown
• Enter - Commit and move focus
• Plain Up/Down - Blocked (beeps)

BUTTON BEHAVIOR:
• All buttons always enabled
• Enter key activates focused button
• No Cancel/Close buttons

TESTING:
• Test with JAWS screen reader
• All shortcuts work immediately
• No external dependencies required
        """
        
        show_styled_message_box(
            self,
            icon=QMessageBox.Information,
            title="Accessibility Patterns - All Working",
            text=help_text
        )
    
    def on_read_status(self):
        """Alt+/ - Read current status."""
        status_text = self.status_bar.currentMessage() or "Ready"
        self.set_status(status_text, announce=True)
    
    def on_escape(self):
        """Escape - Show confirmation dialog."""
        reply = show_styled_message_box(
            self,
            icon=QMessageBox.Question,
            title="Close Window",
            text="Are you sure you want to close this window?",
            buttons=QMessageBox.Yes | QMessageBox.No,
            default_button=QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.announce_dialog_closed()
            super().reject()


def main():
    """Run the standalone accessible sample."""
    app = QApplication(sys.argv)
    
    print("=== Standalone Accessible Sample ===")
    print("All accessibility patterns working - no dependencies!")
    print("Test with JAWS screen reader")
    print("=====================================")
    
    window = AccessibleSampleWindow(window_title="Standalone Accessible Sample")
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
