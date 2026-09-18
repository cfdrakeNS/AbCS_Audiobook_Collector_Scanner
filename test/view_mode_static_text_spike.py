"""
Throwaway JAWS/NVDA spike for view-mode field announcements.

Run:
    python test/view_mode_static_text_spike.py

Compare Tab through:
  1) focusable QLabel (shipped approach)
  2) read-only QLineEdit (old noise: "read only")
  3) editable QLineEdit (says "edit")

Accept the control that speaks name + value with neither "edit" nor "read only".
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.accessibility.view_fields import create_view_value_label, set_view_value


class ViewModeSpikeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("View-mode static text spike")
        self.setAccessibleName("View-mode static text spike")
        self.setAccessibleDescription(
            "Compare QLabel versus read-only and editable line edits for JAWS announcements."
        )

        layout = QVBoxLayout(self)
        intro = QLabel(
            "Tab through each row. Prefer the control that speaks the field name "
            "and value without saying edit or read only."
        )
        intro.setWordWrap(True)
        intro.setFocusPolicy(Qt.StrongFocus)
        layout.addWidget(intro)

        self.label_value = create_view_value_label("Author (QLabel)")
        set_view_value(self.label_value, "John Connelly", "Author (QLabel)")
        layout.addWidget(QLabel("1. Focusable QLabel (candidate):"))
        layout.addWidget(self.label_value)

        self.readonly_edit = QLineEdit("John Connelly")
        self.readonly_edit.setReadOnly(True)
        self.readonly_edit.setAccessibleName("Author (read-only line edit)")
        layout.addWidget(QLabel("2. Read-only QLineEdit (old behavior):"))
        layout.addWidget(self.readonly_edit)

        self.editable_edit = QLineEdit("John Connelly")
        self.editable_edit.setReadOnly(False)
        self.editable_edit.setAccessibleName("Author (editable line edit)")
        layout.addWidget(QLabel("3. Editable QLineEdit:"))
        layout.addWidget(self.editable_edit)

        buttons = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.setAccessibleName("Close")
        close_btn.clicked.connect(self.close)
        buttons.addWidget(close_btn)
        layout.addLayout(buttons)
        self.resize(520, 360)
        self.label_value.setFocus(Qt.OtherFocusReason)


def main() -> int:
    app = QApplication(sys.argv)
    win = ViewModeSpikeWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
