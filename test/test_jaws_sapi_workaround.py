"""
Workaround test - uses Windows SAPI for announcements if Qt accessibility fails.

This bypasses Qt's accessibility bridge entirely and speaks directly to Windows
using SAPI (Speech API). This will make JAWS hear announcements even if Qt's
UIA/MSAA bridge is broken.

HOW TO TEST:
1. Start JAWS FIRST
2. Run: python test\test_jaws_sapi_workaround.py
3. Try Tab navigation
4. Click button

This should announce through SAPI even if Qt accessibility is broken.
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QPushButton, QStatusBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAccessible, QFont


def speak_sapi(text):
    """Speak text using Windows SAPI, bypassing Qt accessibility."""
    try:
        import win32com.client
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        speaker.Speak(text, 1)  # 1 = async, doesn't block
        print(f"  -> SAPI speaking: {text}")
        return True
    except ImportError:
        print("  -> pywin32 not installed, cannot use SAPI")
        print("  -> Install with: pip install pywin32")
        return False
    except Exception as e:
        print(f"  -> SAPI error: {e}")
        return False


def main():
    # Create application
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_NativeWindows, True)

    # Enable Qt accessibility
    QAccessible.setActive(True)
    QAccessible.setRootObject(app)

    print("\n" + "="*60)
    print("JAWS TEST - SAPI WORKAROUND")
    print("="*60)
    print(f"QAccessible.isActive(): {QAccessible.isActive()}")
    print("\nThis test uses Windows SAPI for announcements.")
    print("It should work even if Qt accessibility is broken.")
    print("\nTesting SAPI...")

    # Test SAPI
    if speak_sapi("SAPI test"):
        print("✓ SAPI working! You should have heard 'SAPI test'")
    else:
        print("× SAPI not available - install pywin32:")
        print("  pip install pywin32")
        print("\nContinuing with Qt accessibility only...")

    print("="*60 + "\n")

    # Create main window
    window = QMainWindow()
    window.setWindowTitle("JAWS SAPI Workaround Test")
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
    label = QLabel("SAPI workaround test. Tab should announce via SAPI.")
    label.setAccessibleName("Test label")
    label.setWordWrap(True)
    label.setFocusPolicy(Qt.StrongFocus)

    # Override focus to announce via SAPI
    original_label_focus = label.focusInEvent

    def label_focus(event):
        original_label_focus(event)
        speak_sapi("Test label")
    label.focusInEvent = label_focus

    layout.addWidget(label)

    # Button
    button = QPushButton("Click Me")
    button.setAccessibleName("Click Me")

    # Override focus to announce via SAPI
    original_button_focus = button.focusInEvent

    def button_focus(event):
        original_button_focus(event)
        speak_sapi("Click Me button")
    button.focusInEvent = button_focus

    layout.addWidget(button)

    # Status bar
    status_bar = QStatusBar()
    window.setStatusBar(status_bar)
    status_bar.showMessage("SAPI workaround enabled - Try Tab navigation")

    # Button click handler
    click_count = [0]

    def on_click():
        click_count[0] += 1
        msg = f"Button clicked {click_count[0]} times"
        status_bar.showMessage(msg)
        speak_sapi(msg)
        print(f"  -> {msg}")

    button.clicked.connect(on_click)

    # Announce window opening
    speak_sapi("SAPI workaround test window opened")

    # Show window
    window.show()
    app.processEvents()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
