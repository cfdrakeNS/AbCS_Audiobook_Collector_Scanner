#!/usr/bin/env python3
"""
JAWS Accessibility Test Script
This script creates a minimal Qt application to test JAWS accessibility.
Run this with JAWS active to verify accessibility is working.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QAccessible
from PySide6.QtWidgets import QApplication, QMainWindow, QStatusBar, QLabel, QVBoxLayout, QWidget, QPushButton
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))


def print_accessibility_info():
    """Print detailed accessibility information."""
    print("\n" + "="*70)
    print("JAWS ACCESSIBILITY DIAGNOSTIC TEST")
    print("="*70)

    # Check if QAccessible is active
    is_active = QAccessible.isActive()
    print(f"\n1. QAccessible.isActive(): {is_active}")
    if not is_active:
        print("   ⚠ WARNING: No screen reader detected!")
        print("   → Start JAWS FIRST, then run this script")
    else:
        print("   ✓ Screen reader detected")

    # Check QApplication
    app = QApplication.instance()
    if app:
        print(f"\n2. QApplication exists: True")
        print(f"   Application name: {app.applicationName()}")

        # Query accessible interface
        iface = QAccessible.queryAccessibleInterface(app)
        if iface:
            print(f"   ✓ Has accessible interface")
            print(f"   Role: {iface.role()}")
            print(f"   Name: {iface.text(QAccessible.Text.Name)}")
        else:
            print(f"   ✗ No accessible interface!")

    print("\n" + "="*70)
    print("INSTRUCTIONS FOR TESTING WITH JAWS:")
    print("="*70)
    print("1. Use Insert+T to read window title")
    print("   → Should say 'JAWS Accessibility Test'")
    print("\n2. Use Insert+F5 to list form fields")
    print("   → Should show button and status bar")
    print("\n3. Use JAWS cursor (Numpad Plus) to read screen")
    print("   → Should read 'Test message in status bar'")
    print("\n4. Press Tab to move to button")
    print("   → Should say 'Test Button'")
    print("\n5. Press Enter on button")
    print("   → Should update status bar to 'Button clicked!'")
    print("="*70 + "\n")


class TestWindow(QMainWindow):
    """Minimal test window for JAWS accessibility."""

    def __init__(self):
        super().__init__()

        # Window properties
        self.setWindowTitle("JAWS Accessibility Test")
        self.setAccessibleName("JAWS Test Window")
        self.setAccessibleDescription(
            "Test window for verifying JAWS screen reader accessibility")
        self.resize(800, 600)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Label
        label = QLabel("JAWS Accessibility Test Window")
        label.setAccessibleName("Test Label")
        label.setAccessibleDescription("Main test label")
        layout.addWidget(label)

        # Button
        button = QPushButton("Test Button")
        button.setAccessibleName("Test Button")
        button.setAccessibleDescription(
            "Click this button to test accessibility")
        button.clicked.connect(self.on_button_clicked)
        layout.addWidget(button)

        # Status bar
        self.status = QStatusBar()
        self.status.setAccessibleName("Status Bar")
        self.status.setAccessibleDescription("Test status messages")
        self.status.setObjectName("TestStatusBar")
        self.setStatusBar(self.status)
        self.status.showMessage("Test message in status bar")

        # Set accessible name on status bar message
        self.status.setAccessibleName("Test message in status bar")

    def on_button_clicked(self):
        """Handle button click."""
        self.status.showMessage("Button clicked!")
        self.status.setAccessibleName("Button clicked!")
        print("Button clicked - status bar updated")


def main():
    """Run the test application."""
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("JAWS Test")

    # Enable accessibility
    QAccessible.setActive(True)
    QAccessible.setRootObject(app)

    # Print diagnostics
    print_accessibility_info()

    # Create and show window
    window = TestWindow()
    window.show()

    # Print window info
    print("\nWindow created and shown.")
    print("Use JAWS to test the window (see instructions above).")
    print("\nClose the window to exit.\n")

    # Check if window has accessible interface
    window_iface = QAccessible.queryAccessibleInterface(window)
    if window_iface:
        print(f"✓ Main window has accessible interface")
        print(f"  Role: {window_iface.role()}")
        print(f"  Name: {window_iface.text(QAccessible.Text.Name)}")
    else:
        print(f"✗ Main window does NOT have accessible interface!")

    # Run event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
