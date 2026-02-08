"""
Test with explicit accessibility events - manually notifies JAWS of changes.

This test manually fires accessibility update events to force JAWS to notice
widget focus changes and status bar updates.

### not working 

# HOW TO TEST:
1. Start JAWS FIRST
2. Run: python test\test_jaws_with_events.py
3. Try Tab navigation
4. Click button and listen for status announcement
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QPushButton, QStatusBar
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAccessible, QFont


def announce_to_screen_reader(widget, message):
    """Force an accessibility announcement."""
    # Try to fire an accessibility event
    try:
        # Update accessible name temporarily to trigger announcement
        old_name = widget.accessibleName()
        widget.setAccessibleName(message)
        QAccessible.updateAccessibility(
            QAccessible.Update(widget, QAccessible.NameChanged)
        )
        # Restore old name after a moment
        QTimer.singleShot(100, lambda: widget.setAccessibleName(old_name))
    except Exception as e:
        print(f"Failed to announce: {e}")


def main():
    # Create application FIRST
    app = QApplication(sys.argv)

    # Force native windows
    app.setAttribute(Qt.AA_NativeWindows, True)

    # CRITICAL: Enable accessibility BEFORE creating any widgets
    QAccessible.setActive(True)
    QAccessible.setRootObject(app)

    print("\n" + "="*60)
    print("JAWS TEST - EXPLICIT ACCESSIBILITY EVENTS")
    print("="*60)
    print(f"QAccessible.isActive(): {QAccessible.isActive()}")
    print("\nThis test manually fires accessibility events")
    print("to notify JAWS of focus changes and status updates.")
    print("="*60 + "\n")

    # Create main window
    window = QMainWindow()
    window.setWindowTitle("JAWS Accessibility Events Test")
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

    # Label
    label = QLabel(
        "Test with manual accessibility events. Try Tab navigation.")
    label.setAccessibleName("Test label")
    label.setAccessibleDescription("Label that fires focus events")
    label.setWordWrap(True)
    label.setFocusPolicy(Qt.StrongFocus)

    # Override focus event to announce
    original_label_focus_in = label.focusInEvent

    def label_focus_in(event):
        original_label_focus_in(event)
        print("  -> Label focused, firing accessibility event")
        QAccessible.updateAccessibility(
            QAccessible.Update(label, QAccessible.Focus)
        )

    label.focusInEvent = label_focus_in
    layout.addWidget(label)

    # Button
    button = QPushButton("Click Me")
    button.setAccessibleName("Click Me")
    button.setAccessibleDescription("Button that fires focus events")

    # Override focus event to announce
    original_button_focus_in = button.focusInEvent

    def button_focus_in(event):
        original_button_focus_in(event)
        print("  -> Button focused, firing accessibility event")
        QAccessible.updateAccessibility(
            QAccessible.Update(button, QAccessible.Focus)
        )

    button.focusInEvent = button_focus_in
    layout.addWidget(button)

    # Status bar
    status_bar = QStatusBar()
    window.setStatusBar(status_bar)
    status_bar.showMessage(
        "Explicit events enabled - Try Tab and click button")

    # Button click handler with explicit announcement
    click_count = [0]

    def on_click():
        click_count[0] += 1
        msg = f"Button clicked {click_count[0]} times"
        status_bar.showMessage(msg)
        print(f"  -> {msg}")

        # Fire accessibility event for status bar
        QAccessible.updateAccessibility(
            QAccessible.Update(status_bar, QAccessible.NameChanged)
        )

        # Also try to announce through the button itself
        announce_to_screen_reader(button, msg)

    button.clicked.connect(on_click)

    # Show window
    window.show()
    app.processEvents()

    # Fire initial focus event
    print("  -> Window shown, firing initial accessibility events")
    QAccessible.updateAccessibility(
        QAccessible.Update(window, QAccessible.ObjectShow)
    )

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
