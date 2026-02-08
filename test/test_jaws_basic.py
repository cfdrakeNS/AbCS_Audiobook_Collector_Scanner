"""
Minimal test for JAWS reading - tests if JAWS can read ANY PySide6 application.
This is simpler than the full test harness to isolate the issue.

HOW TO TEST:
1. Start JAWS FIRST
2. Run: python test/test_jaws_basic.py
3. Try these JAWS commands:
   - Insert+T: Read window title (should say "JAWS Basic Test")
   - Tab: Move to button (should say "Click Me button")
   - Insert+Tab: Read current control
   - Insert+Up Arrow: Say line
   - Space: Click button (should announce in status bar)
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QPushButton, QStatusBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAccessible, QFont


def main():
    # Create application FIRST
    app = QApplication(sys.argv)

    # CRITICAL: Enable accessibility BEFORE creating any widgets
    QAccessible.setActive(True)
    QAccessible.setRootObject(app)

    print("\n" + "="*60)
    print("JAWS BASIC ACCESSIBILITY TEST")
    print("="*60)
    print(f"QAccessible.isActive(): {QAccessible.isActive()}")
    print("\nWith JAWS running, try:")
    print("  Insert+T        - Read window title")
    print("  Tab             - Navigate to button")
    print("  Insert+Tab      - Read current control")
    print("  Space           - Click button")
    print("  Insert+Ctrl+F1  - Window technical info")
    print("="*60 + "\n")

    # Create main window
    window = QMainWindow()
    window.setWindowTitle("JAWS Basic Test")
    window.resize(600, 400)

    # Central widget
    central = QWidget()
    window.setCentralWidget(central)
    layout = QVBoxLayout(central)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(20)

    # Large font for visibility
    font = QFont()
    font.setPointSize(16)
    app.setFont(font)

    # Simple label
    label = QLabel("This is a test label. JAWS should read this.")
    label.setAccessibleName("Test label")
    label.setAccessibleDescription("This label tests if JAWS can read text")
    label.setWordWrap(True)
    layout.addWidget(label)

    # Simple button
    button = QPushButton("Click Me")
    button.setAccessibleName("Click Me")
    button.setAccessibleDescription("Test button that updates status bar")
    layout.addWidget(button)

    # Status bar for announcements
    status_bar = QStatusBar()
    window.setStatusBar(status_bar)
    status_bar.showMessage("Ready - Press Tab to navigate")

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

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
