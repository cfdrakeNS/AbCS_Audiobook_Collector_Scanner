from PySide6.QtWidgets import QDialog, QVBoxLayout, QStatusBar, QApplication, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
import sys

class MinimalWebMetadataTest(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minimal Web Metadata Test")
        self.resize(400, 200)
        layout = QVBoxLayout(self)
        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar)
        self.status_bar.showMessage("Ready")
        self.label = QLabel("Press F1 or Alt+/ to test shortcuts.")
        layout.addWidget(self.label)
        # F1 shortcut
        self.f1_shortcut = QShortcut(QKeySequence("F1"), self)
        self.f1_shortcut.activated.connect(self.on_f1)
        # Alt+/ shortcut
        self.alt_slash_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.alt_slash_shortcut.activated.connect(self.on_alt_slash)
    def on_f1(self):
        self.status_bar.showMessage("F1 pressed!")
        print("[DEBUG] F1 shortcut activated", file=sys.stderr)
    def on_alt_slash(self):
        self.status_bar.showMessage("Alt+/ pressed!")
        print("[DEBUG] Alt+/ shortcut activated", file=sys.stderr)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dlg = MinimalWebMetadataTest()
    dlg.show()
    sys.exit(app.exec())
