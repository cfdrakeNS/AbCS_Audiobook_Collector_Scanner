"""
Test with NVDA to determine if this is JAWS-specific.

If NVDA Tab navigation works but JAWS doesn't, it's a JAWS configuration issue.
If NVDA also doesn't work, it's a Windows/Qt system issue.

INSTALL NVDA:
1. Download: https://www.nvaccess.org/download/
2. Run installer
3. Start NVDA

HOW TO TEST:
1. Close JAWS
2. Start NVDA
3. Run: python test\test_nvda_comparison.py
4. Try Tab navigation
5. Listen for announcements

NVDA COMMANDS:
- NVDA+T: Read title
- Tab: Navigate (should announce)
- Insert+Up: Say line
- Insert+Down: Say all
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QPushButton, QStatusBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAccessible, QFont


def main():
    # Create application
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_NativeWindows, True)

    # Enable accessibility
    QAccessible.setActive(True)
    QAccessible.setRootObject(app)

    print("\n" + "="*60)
    print("NVDA COMPARISON TEST")
    print("="*60)
    print("Make sure:")
    print("  1. JAWS is CLOSED")
    print("  2. NVDA is RUNNING")
    print("")
    print(f"QAccessible.isActive(): {QAccessible.isActive()}")
    print("")
    print("With NVDA running, try:")
    print("  Tab             - Navigate (should announce)")
    print("  NVDA+T          - Read title")
    print("  Insert+Up       - Say line")
    print("  Space           - Click button")
    print("="*60 + "\n")

    # Create main window
    window = QMainWindow()
    window.setWindowTitle("NVDA Comparison Test")
    window.resize(600, 400)

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

    # Label
    label = QLabel("NVDA test. Does Tab announce widgets with NVDA?")
    label.setAccessibleName("Test label")
    label.setAccessibleDescription("This tests NVDA compatibility")
    label.setWordWrap(True)
    label.setFocusPolicy(Qt.StrongFocus)
    layout.addWidget(label)

    # Button
    button = QPushButton("Click Me")
    button.setAccessibleName("Click Me button")
    button.setAccessibleDescription("Test button for NVDA")
    layout.addWidget(button)

    # Status bar
    status_bar = QStatusBar()
    window.setStatusBar(status_bar)
    status_bar.showMessage("NVDA test - Try Tab navigation")

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

    print("="*60)
    print("WHAT TO CHECK:")
    print("  - Does NVDA announce widgets when you press Tab?")
    print("  - Does NVDA announce status bar changes?")
    print("  - Compare with JAWS behavior")
    print("")
    print("If NVDA works but JAWS doesn't:")
    print("  -> JAWS configuration issue")
    print("")
    print("If NVDA also doesn't work:")
    print("  -> Qt/Windows accessibility issue")
    print("="*60 + "\n")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
