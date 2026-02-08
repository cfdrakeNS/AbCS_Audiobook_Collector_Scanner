"""
Test with explicit accessibility roles - tells JAWS exactly what each widget is.

This explicitly sets the role for each widget using Qt's accessibility API.

HOW TO TEST:
1. Start JAWS FIRST
2. Run: python test\test_jaws_with_roles.py
3. Try Tab navigation - JAWS should announce roles
4. Check Insert+Ctrl+F1
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QPushButton, QStatusBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAccessible, QFont


class AccessibleLabel(QLabel):
    """Label with explicit accessibility role."""

    def accessibleRole(self):
        return QAccessible.StaticText


class AccessibleButton(QPushButton):
    """Button with explicit accessibility role."""

    def accessibleRole(self):
        return QAccessible.Button


def main():
    # Create application FIRST
    app = QApplication(sys.argv)

    # Force native windows
    app.setAttribute(Qt.AA_NativeWindows, True)

    # CRITICAL: Enable accessibility BEFORE creating any widgets
    QAccessible.setActive(True)
    QAccessible.setRootObject(app)

    print("\n" + "="*60)
    print("JAWS TEST - EXPLICIT ACCESSIBILITY ROLES")
    print("="*60)
    print(f"QAccessible.isActive(): {QAccessible.isActive()}")
    print("\nWidgets have explicit accessibility roles set")
    print("Try Tab navigation - should announce widget types")
    print("="*60 + "\n")

    # Create main window
    window = QMainWindow()
    window.setWindowTitle("JAWS Explicit Roles Test")
    window.resize(600, 400)
    window.setAttribute(Qt.WA_NativeWindow, True)

    # Central widget
    central = QWidget()
    window.setCentralWidget(central)
    layout = QVBoxLayout(central)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(20)

    # Large font
    font = QFont()
    font.setPointSize(16)
    app.setFont(font)

    # Label with explicit role
    label = AccessibleLabel(
        "Test with explicit accessibility roles. Try Tab navigation.")
    label.setAccessibleName("Test label")
    label.setAccessibleDescription("Label with explicit StaticText role")
    label.setWordWrap(True)
    label.setFocusPolicy(Qt.StrongFocus)  # Make label focusable
    layout.addWidget(label)

    # Button with explicit role
    button = AccessibleButton("Click Me")
    button.setAccessibleName("Click Me")
    button.setAccessibleDescription("Button with explicit Button role")
    layout.addWidget(button)

    # Status bar
    status_bar = QStatusBar()
    window.setStatusBar(status_bar)
    status_bar.showMessage("Explicit roles enabled - Try Tab navigation")

    # Button click handler
    click_count = [0]

    def on_click():
        click_count[0] += 1
        msg = f"Button clicked {click_count[0]} times"
        status_bar.showMessage(msg)
        print(f"  -> {msg}")

    button.clicked.connect(on_click)

    # Show window
    window.show()
    app.processEvents()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
