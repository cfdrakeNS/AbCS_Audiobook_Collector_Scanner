"""Progress dialog for batch web metadata fetch (N of M)."""

from __future__ import annotations

import threading

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QLabel, QProgressBar, QVBoxLayout

from src.accessibility.accessible_events import (
    announce_dialog_opened,
    configure_status_bar_accessibility,
)
from src.ui.accessible_dialog import AccessibleDialog
from PySide6.QtWidgets import QStatusBar


class BatchWebFetchProgressDialog(AccessibleDialog):
    """Modal progress for multi-book web fetch with cancel."""

    def __init__(self, total: int, parent=None):
        super().__init__(parent)
        from src.accessibility.icon_helper import get_app_icon

        self.setWindowIcon(get_app_icon())
        self.total = max(1, total)
        self.cancel_event = threading.Event()
        self.setWindowTitle("Batch web fetch")
        self.setModal(True)
        self.setAccessibleName("Batch web fetch progress")
        self.setAccessibleDescription(
            f"Fetching web metadata for {self.total} books. "
            "Press Escape or Alt+C to cancel."
        )

        layout = QVBoxLayout(self)
        self.status_label = QLabel("Starting…")
        self.status_label.setWordWrap(True)
        self.status_label.setFocusPolicy(Qt.StrongFocus)
        layout.addWidget(self.status_label)

        self.bar = QProgressBar()
        self.bar.setRange(0, self.total)
        self.bar.setValue(0)
        self.bar.setAccessibleName("Batch fetch progress")
        layout.addWidget(self.bar)

        self.status_bar = QStatusBar()
        configure_status_bar_accessibility(self.status_bar)
        layout.addWidget(self.status_bar)

        QShortcut(QKeySequence(Qt.Key_Escape), self, activated=self.request_cancel)
        QShortcut(QKeySequence("Alt+C"), self, activated=self.request_cancel)
        self.resize(440, 140)

    def request_cancel(self) -> None:
        if self.cancel_event.is_set():
            return
        self.cancel_event.set()
        self.update_progress(self.bar.value(), "Canceling…")

    def update_progress(self, current: int, title: str) -> None:
        self.bar.setValue(min(current, self.total))
        text = f"Book {current} of {self.total}: {title}"
        self.status_label.setText(text)
        self.status_label.setAccessibleName(text)
        self.setAccessibleDescription(text)
        self.status_bar.showMessage(text)

    def showEvent(self, event):
        super().showEvent(event)
        self.raise_()
        self.activateWindow()
        announce_dialog_opened(self, "Batch web fetch progress")
