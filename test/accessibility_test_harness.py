"""
PySide6 Accessibility Test Harness
Simple app to test accessibility features, layouts, and screen reader compatibility.
Tests problematic patterns we've encountered in AbCS development.
"""

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QLineEdit, QPushButton, QStatusBar,
    QGroupBox, QSizePolicy
)
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QFont
import sys


class AccessibilityTestWindow(QMainWindow):
    """Test window for PySide6 accessibility features."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Accessibility Test Harness - AbCS")
        self.resize(900, 700)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Test sections
        self.create_label_alignment_test(main_layout)
        self.create_combo_width_test(main_layout)
        self.create_status_bar_test(main_layout)
        self.create_jaws_keyboard_test(main_layout)

        main_layout.addStretch()

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Test each section with JAWS/NVDA")

    def create_label_alignment_test(self, parent_layout):
        """Test label alignment with different methods."""
        group = QGroupBox("Label Alignment Test")
        group.setAccessibleName("Label alignment test")
        layout = QVBoxLayout(group)

        info = QLabel("Testing right-aligned labels next to controls:")
        info.setWordWrap(True)
        layout.addWidget(info)

        # Test 1: Using setAlignment only
        test1_layout = QHBoxLayout()
        test1_layout.setSpacing(10)
        label1 = QLabel("Method 1 (setAlignment):")
        label1.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        label1.setMinimumWidth(150)
        combo1 = QComboBox()
        combo1.addItems(["Option A", "Option B", "Option C"])
        label1.setBuddy(combo1)
        combo1.setAccessibleName("Method 1 options")
        combo1.setAccessibleDescription(
            "Combo box for method 1 label alignment")
        test1_layout.addWidget(label1)
        test1_layout.addWidget(combo1)
        test1_layout.addStretch()
        layout.addLayout(test1_layout)

        # Test 2: Using stylesheet
        test2_layout = QHBoxLayout()
        test2_layout.setSpacing(10)
        label2 = QLabel("Method 2 (stylesheet):")
        label2.setStyleSheet("QLabel { min-width: 150px; text-align: right; }")
        label2.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        combo2 = QComboBox()
        combo2.addItems(["Option A", "Option B", "Option C"])
        label2.setBuddy(combo2)
        combo2.setAccessibleName("Method 2 options")
        combo2.setAccessibleDescription(
            "Combo box for method 2 label alignment")
        test2_layout.addWidget(label2)
        test2_layout.addWidget(combo2)
        test2_layout.addStretch()
        layout.addLayout(test2_layout)

        # Test 3: Using setFixedWidth
        test3_layout = QHBoxLayout()
        test3_layout.setSpacing(10)
        label3 = QLabel("Method 3 (setFixedWidth):")
        label3.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        label3.setFixedWidth(150)
        combo3 = QComboBox()
        combo3.addItems(["Option A", "Option B", "Option C"])
        label3.setBuddy(combo3)
        combo3.setAccessibleName("Method 3 options")
        combo3.setAccessibleDescription(
            "Combo box for method 3 label alignment")
        test3_layout.addWidget(label3)
        test3_layout.addWidget(combo3)
        test3_layout.addStretch()
        layout.addLayout(test3_layout)

        # Test 4: Using size policy
        test4_layout = QHBoxLayout()
        test4_layout.setSpacing(10)
        label4 = QLabel("Method 4 (size policy):")
        label4.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        label4.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        label4.setFixedWidth(150)
        combo4 = QComboBox()
        combo4.addItems(["Option A", "Option B", "Option C"])
        label4.setBuddy(combo4)
        combo4.setAccessibleName("Method 4 options")
        combo4.setAccessibleDescription(
            "Combo box for method 4 label alignment")
        test4_layout.addWidget(label4)
        test4_layout.addWidget(combo4)
        test4_layout.addStretch()
        layout.addLayout(test4_layout)

        parent_layout.addWidget(group)

    def create_combo_width_test(self, parent_layout):
        """Test combo box width control methods."""
        group = QGroupBox("Combo Box Width Test")
        group.setAccessibleName("Combo box width test")
        layout = QVBoxLayout(group)

        info = QLabel(
            "Testing methods to control combo box width (target: 200px):")
        info.setWordWrap(True)
        layout.addWidget(info)

        # Test 1: setMinimumWidth only
        test1_layout = QHBoxLayout()
        test1_layout.setSpacing(10)
        label1 = QLabel("setMinimumWidth(200):")
        test1_layout.addWidget(label1)
        combo1 = QComboBox()
        combo1.addItems(["Short", "Medium Text", "Very Long Text Here"])
        combo1.setMinimumWidth(200)
        label1.setBuddy(combo1)
        combo1.setAccessibleName("Minimum width 200")
        test1_layout.addWidget(combo1, 0)
        test1_layout.addStretch()
        layout.addLayout(test1_layout)

        # Test 2: setFixedWidth
        test2_layout = QHBoxLayout()
        test2_layout.setSpacing(10)
        label2 = QLabel("setFixedWidth(200):")
        test2_layout.addWidget(label2)
        combo2 = QComboBox()
        combo2.addItems(["Short", "Medium Text", "Very Long Text Here"])
        combo2.setFixedWidth(200)
        label2.setBuddy(combo2)
        combo2.setAccessibleName("Fixed width 200")
        test2_layout.addWidget(combo2, 0)
        test2_layout.addStretch()
        layout.addLayout(test2_layout)

        # Test 3: Stylesheet width
        test3_layout = QHBoxLayout()
        test3_layout.setSpacing(10)
        label3 = QLabel("Stylesheet width:")
        test3_layout.addWidget(label3)
        combo3 = QComboBox()
        combo3.addItems(["Short", "Medium Text", "Very Long Text Here"])
        combo3.setStyleSheet("QComboBox { width: 200px; }")
        label3.setBuddy(combo3)
        combo3.setAccessibleName("Stylesheet width 200")
        test3_layout.addWidget(combo3, 0)
        test3_layout.addStretch()
        layout.addLayout(test3_layout)

        # Test 4: Stylesheet min-width + max-width
        test4_layout = QHBoxLayout()
        test4_layout.setSpacing(10)
        label4 = QLabel("Stylesheet min/max-width:")
        test4_layout.addWidget(label4)
        combo4 = QComboBox()
        combo4.addItems(["Short", "Medium Text", "Very Long Text Here"])
        combo4.setStyleSheet(
            "QComboBox { min-width: 200px; max-width: 200px; }")
        label4.setBuddy(combo4)
        combo4.setAccessibleName("Stylesheet min and max width 200")
        test4_layout.addWidget(combo4, 0)
        test4_layout.addStretch()
        layout.addLayout(test4_layout)

        # Test 5: Size policy Fixed + setFixedWidth
        test5_layout = QHBoxLayout()
        test5_layout.setSpacing(10)
        label5 = QLabel("Fixed policy + setFixedWidth:")
        test5_layout.addWidget(label5)
        combo5 = QComboBox()
        combo5.addItems(["Short", "Medium Text", "Very Long Text Here"])
        combo5.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        combo5.setFixedWidth(200)
        label5.setBuddy(combo5)
        combo5.setAccessibleName("Fixed policy and fixed width 200")
        test5_layout.addWidget(combo5, 0)
        test5_layout.addStretch()
        layout.addLayout(test5_layout)

        parent_layout.addWidget(group)

    def create_status_bar_test(self, parent_layout):
        """Test status bar announcement methods."""
        group = QGroupBox("Status Bar Announcement Test")
        group.setAccessibleName("Status bar announcement test")
        layout = QVBoxLayout(group)

        info = QLabel("Test different status bar update methods with JAWS:")
        info.setWordWrap(True)
        layout.addWidget(info)

        btn_layout = QHBoxLayout()

        btn1 = QPushButton("showMessage()")
        btn1.setAccessibleName("Show status message")
        btn1.clicked.connect(lambda: self.status_bar.showMessage(
            "Method 1: showMessage() called"))
        btn_layout.addWidget(btn1)

        btn2 = QPushButton("setStatusTip()")
        btn2.setAccessibleName("Set status tip")
        btn2.setStatusTip("Method 2: Status tip set on button hover")
        btn_layout.addWidget(btn2)

        btn3 = QPushButton("Clear Status")
        btn3.setAccessibleName("Clear status bar")
        btn3.clicked.connect(lambda: self.status_bar.clearMessage())
        btn_layout.addWidget(btn3)

        btn4 = QPushButton("Move Focus to Status")
        btn4.setAccessibleName("Focus status bar")
        btn4.clicked.connect(self.focus_status_bar)
        btn_layout.addWidget(btn4)

        layout.addLayout(btn_layout)

        # Add text to announce
        announce_layout = QHBoxLayout()
        label = QLabel("Custom message:")
        announce_layout.addWidget(label)
        self.status_text = QLineEdit()
        self.status_text.setPlaceholderText("Type message and press Announce")
        self.status_text.setAccessibleName("Custom status message")
        label.setBuddy(self.status_text)
        announce_layout.addWidget(self.status_text)
        btn_announce = QPushButton("Announce")
        btn_announce.setAccessibleName("Announce custom status message")
        btn_announce.clicked.connect(
            lambda: self.status_bar.showMessage(self.status_text.text()))
        announce_layout.addWidget(btn_announce)
        layout.addLayout(announce_layout)

        parent_layout.addWidget(group)

    def create_jaws_keyboard_test(self, parent_layout):
        """Test JAWS keyboard compatibility (backspace, delete)."""
        group = QGroupBox("JAWS Keyboard Test")
        group.setAccessibleName("JAWS keyboard test")
        layout = QVBoxLayout(group)

        info = QLabel("Test backspace and delete keys with JAWS running:")
        info.setWordWrap(True)
        layout.addWidget(info)

        # Standard QLineEdit
        test1_layout = QHBoxLayout()
        label1 = QLabel("Standard QLineEdit:")
        test1_layout.addWidget(label1)
        edit1 = QLineEdit()
        edit1.setPlaceholderText("Type and try backspace/delete")
        edit1.setAccessibleName("Standard line edit")
        label1.setBuddy(edit1)
        test1_layout.addWidget(edit1)
        layout.addLayout(test1_layout)

        # QLineEdit with event filter
        test2_layout = QHBoxLayout()
        label2 = QLabel("With event filter:")
        test2_layout.addWidget(label2)
        edit2 = QLineEdit()
        edit2.setPlaceholderText("Type and try backspace/delete")
        edit2.installEventFilter(self)
        edit2.setAccessibleName("Line edit with event filter")
        label2.setBuddy(edit2)
        test2_layout.addWidget(edit2)
        layout.addLayout(test2_layout)

        # Custom subclass with keyPressEvent override
        test3_layout = QHBoxLayout()
        label3 = QLabel("Custom keyPressEvent:")
        test3_layout.addWidget(label3)
        edit3 = JAWSCompatibleLineEdit()
        edit3.setPlaceholderText("Type and try backspace/delete")
        edit3.setAccessibleName("Line edit with custom keyPressEvent")
        label3.setBuddy(edit3)
        test3_layout.addWidget(edit3)
        layout.addLayout(test3_layout)

        parent_layout.addWidget(group)

    def focus_status_bar(self):
        """Move focus to status bar."""
        self.status_bar.setFocusPolicy(Qt.StrongFocus)
        self.status_bar.setFocus()
        self.status_bar.showMessage(
            "Status bar has focus - JAWS should read this")

    def eventFilter(self, source, event):
        """Event filter for keyboard test."""
        if isinstance(source, QLineEdit) and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Backspace, Qt.Key_Delete):
                self.status_bar.showMessage(
                    f"Event filter detected key: {event.key()}")
                return False
        return super().eventFilter(source, event)


class JAWSCompatibleLineEdit(QLineEdit):
    """Custom QLineEdit with keyPressEvent override for JAWS testing."""

    def keyPressEvent(self, event):
        """Override to test JAWS keyboard handling."""
        if event.key() in (Qt.Key_Backspace, Qt.Key_Delete):
            super().keyPressEvent(event)
            window = self.window()
            if hasattr(window, 'status_bar'):
                window.status_bar.showMessage(
                    f"Custom keyPressEvent handled: {event.key()}")
            return

        super().keyPressEvent(event)


def main():
    """Run the test harness."""
    app = QApplication(sys.argv)

    # CRITICAL: Enable accessibility BEFORE creating widgets
    from PySide6.QtGui import QAccessible
    QAccessible.setActive(True)
    QAccessible.setRootObject(app)

    # Print diagnostic info
    print("\n" + "="*70)
    print("PySide6 ACCESSIBILITY TEST HARNESS - JAWS/NVDA Testing")
    print("="*70)
    print(f"QAccessible.isActive(): {QAccessible.isActive()}")
    print("\nIMPORTANT: Qt apps don't support JAWS Virtual Cursor like web browsers.")
    print("Instead, use these JAWS commands:")
    print("  Insert+T        - Read window title")
    print("  Tab             - Navigate between controls")
    print("  Insert+Tab      - Read current control")
    print("  Insert+Up       - Say line")
    print("  Insert+Down     - Say all from cursor")
    print("  Insert+Ctrl+F1  - Window technical info (check class name)")
    print("\nIf window class shows 'Qt6101QWindowIcon', accessibility is broken.")
    print("If it shows proper widget classes, accessibility is working.")
    print("="*70 + "\n")

    # Set application font to 14pt like AbCS
    font = QFont()
    font.setPointSize(14)
    app.setFont(font)

    window = AccessibilityTestWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
