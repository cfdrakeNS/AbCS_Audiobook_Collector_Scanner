"""
Test app to determine what breaks JAWS window virtualization (Insert+Alt+W).

This creates 3 test windows to compare:
1. Basic Qt window (no accessibility changes)
2. Qt window with QAccessible.setActive(True) 
3. Qt window with QAccessible.setActive(True) + setRootObject()

Instructions:
1. Start JAWS first
2. Run: python test_virtualization.py
3. Test each window with Insert+Alt+W to see which ones virtualize
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QStatusBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAccessible


class TestWindow(QMainWindow):
    """Base test window with common UI elements."""

    def __init__(self, title, description):
        super().__init__()
        self.setWindowTitle(title)
        self.resize(600, 400)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Description label
        desc = QLabel(description)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Sample table (like AbCS main window)
        table = QTableWidget(5, 3)
        table.setHorizontalHeaderLabels(["Author", "Title", "Year"])
        for row in range(5):
            table.setItem(row, 0, QTableWidgetItem(f"Author {row+1}"))
            table.setItem(row, 1, QTableWidgetItem(f"Book Title {row+1}"))
            table.setItem(row, 2, QTableWidgetItem(f"202{row}"))
        layout.addWidget(table)

        # Buttons
        btn_layout = QVBoxLayout()
        btn1 = QPushButton("Test Button 1")
        btn2 = QPushButton("Test Button 2")
        btn_layout.addWidget(btn1)
        btn_layout.addWidget(btn2)
        layout.addLayout(btn_layout)

        # Status bar
        status = QStatusBar()
        status.showMessage(
            "Test status message - try Insert+Alt+W to virtualize")
        self.setStatusBar(status)


class BasicWindow(TestWindow):
    """Window 1: Basic Qt with NO accessibility changes."""

    def __init__(self):
        super().__init__(
            "Test 1: Basic Qt (NO accessibility)",
            "This window has NO QAccessible changes. "
            "It should virtualize normally in JAWS (Insert+Alt+W)."
        )


class AccessibleActiveWindow(TestWindow):
    """Window 2: With QAccessible.setActive(True)."""

    def __init__(self):
        super().__init__(
            "Test 2: QAccessible.setActive(True)",
            "This window called QAccessible.setActive(True). "
            "Does it still virtualize with Insert+Alt+W?"
        )


class AccessibleRootWindow(TestWindow):
    """Window 3: With setActive + setRootObject."""

    def __init__(self):
        super().__init__(
            "Test 3: setActive + setRootObject",
            "This window called setActive(True) AND setRootObject(app). "
            "Does it still virtualize with Insert+Alt+W?"
        )


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("JAWS Virtualization Test")

    print("\n" + "="*70)
    print("JAWS WINDOW VIRTUALIZATION TEST")
    print("="*70)
    print("\nThis test will open 3 windows to determine what breaks virtualization.")
    print("\nInstructions:")
    print("1. Make sure JAWS is running")
    print("2. Click each window and try Insert+Alt+W to virtualize")
    print("3. Note which windows virtualize and which don't")
    print("\nTest Windows:")
    print("  1. Basic Qt (no accessibility changes)")
    print("  2. QAccessible.setActive(True)")
    print("  3. setActive(True) + setRootObject(app)")
    print("="*70 + "\n")

    # Create test 1: Basic window (no changes)
    window1 = BasicWindow()
    window1.move(100, 100)
    window1.show()

    # Create test 2: setActive(True)
    QAccessible.setActive(True)
    window2 = AccessibleActiveWindow()
    window2.move(750, 100)
    window2.show()

    # Create test 3: setActive + setRootObject
    QAccessible.setRootObject(app)
    window3 = AccessibleRootWindow()
    window3.move(100, 550)
    window3.show()

    print("\nAll windows opened. Test Insert+Alt+W in each window.")
    print("Close all windows when done testing.\n")

    # Check accessibility status
    print(f"QAccessible.isActive(): {QAccessible.isActive()}")
    print("(setRootObject was called for window 3)")

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
