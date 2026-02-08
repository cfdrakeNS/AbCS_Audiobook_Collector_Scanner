"""
Test with native window flags - forces Qt to create a proper Windows window.

The Qt6102QWindowIcon class suggests Qt is creating a frameless or tool window
instead of a proper application window. This forces creation of a native window.

HOW TO TEST:
1. Start JAWS FIRST
2. Run: python test\test_jaws_native_window.py
3. Check Insert+Ctrl+F1 - Window class should change
4. Try Tab navigation
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

    # Force native windows (critical for accessibility)
    app.setAttribute(Qt.AA_NativeWindows, True)
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings, False)

    # CRITICAL: Enable accessibility BEFORE creating any widgets
    QAccessible.setActive(True)
    QAccessible.setRootObject(app)

    print("\n" + "="*60)
    print("JAWS TEST - NATIVE WINDOW MODE")
    print("="*60)
    print(f"AA_NativeWindows: True")
    print(f"QAccessible.isActive(): {QAccessible.isActive()}")
    print("\nCheck Insert+Ctrl+F1 - window class should be different")
    print("="*60 + "\n")

    # Create main window with explicit window flags
    window = QMainWindow()
    window.setWindowTitle("JAWS Native Window Test")
    window.resize(600, 400)

    # Force this to be a native window
    window.setAttribute(Qt.WA_NativeWindow, True)
    window.setAttribute(Qt.WA_DontCreateNativeAncestors, False)

    # Central widget
    central = QWidget()
    # Make central widget native too
    central.setAttribute(Qt.WA_NativeWindow, True)
    window.setCentralWidget(central)
    layout = QVBoxLayout(central)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(20)

    # Large font
    font = QFont()
    font.setPointSize(16)
    app.setFont(font)

    # Simple label
    label = QLabel(
        "Native window test. Check window class with Insert+Ctrl+F1.")
    label.setAccessibleName("Test label")
    label.setAccessibleDescription("This label tests native window mode")
    label.setWordWrap(True)
    layout.addWidget(label)

    # Simple button
    button = QPushButton("Click Me")
    button.setAccessibleName("Click Me")
    button.setAccessibleDescription("Test button")
    layout.addWidget(button)

    # Status bar
    status_bar = QStatusBar()
    window.setStatusBar(status_bar)
    status_bar.showMessage("Native window mode enabled")

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

    # Force processing to ensure native window creation
    app.processEvents()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
