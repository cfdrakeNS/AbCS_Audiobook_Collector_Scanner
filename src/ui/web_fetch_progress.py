"""Accessible modal dialog shown while fetching web book metadata."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QDialog, QLabel, QStatusBar, QVBoxLayout

from src.accessibility.accessible_events import (
    announce_dialog_opened,
    announce_status_message,
    configure_status_bar_accessibility,
)
from src.accessibility.screen_reader import get_screen_reader_focus_delay_ms


class WebFetchProgressDialog(QDialog):
    """Modal wait dialog with live status text for web metadata fetch."""

    def __init__(self, parent=None):
        super().__init__(parent)
        from src.accessibility.icon_helper import get_app_icon

        self.setWindowIcon(get_app_icon())
        self.setWindowTitle("Please wait")
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setAccessibleName("Fetching web book information")
        self.setAccessibleDescription(
            "Searching online sources for book metadata. Please wait."
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 6)
        layout.setSpacing(8)

        self._message_label = QLabel("Preparing web search…")
        self._message_label.setAccessibleName("Web fetch status")
        self._message_label.setAccessibleDescription(self._message_label.text())
        self._message_label.setWordWrap(True)
        self._message_label.setFocusPolicy(Qt.NoFocus)
        layout.addWidget(self._message_label)

        self.status_bar = QStatusBar()
        configure_status_bar_accessibility(self.status_bar)
        self.status_bar.setFixedHeight(22)
        layout.addWidget(self.status_bar)

        self.resize(400, 110)
        self._initial_announced = False
        self.setFocusPolicy(Qt.StrongFocus)

    def _blur_status_focus(self) -> None:
        """Move focus off the status bar so the next announce triggers a focus-in."""
        app = QApplication.instance()
        if not app or app.focusWidget() != self.status_bar:
            return
        self.setFocus(Qt.OtherFocusReason)
        QApplication.processEvents()

    def show(self):
        super().show()
        self.raise_()
        self.activateWindow()
        QApplication.processEvents()
        announce_dialog_opened(self, "Fetching web book information")
        delay = max(300, get_screen_reader_focus_delay_ms())
        QTimer.singleShot(delay, self._announce_initial)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._ensure_foreground)

    def _ensure_foreground(self):
        """Keep the wait dialog active so JAWS associates speech with this window."""
        self.raise_()
        self.activateWindow()

    def _announce_initial(self):
        if self._initial_announced:
            return
        self._initial_announced = True
        text = (
            f"Fetching web book information. {self._message_label.text().strip()}"
        )
        self._speak_status(text, force=True)

    def update_message(self, text: str) -> None:
        """Update visible status and announce via focus-based readback for JAWS/NVDA."""
        text = (text or "").strip()
        if not text:
            return
        self._message_label.setText(text)
        self._message_label.setAccessibleDescription(text)
        self.setAccessibleDescription(text)
        self._initial_announced = True
        QApplication.processEvents()
        QTimer.singleShot(0, lambda t=text: self._speak_status(t, force=True))

    def _speak_status(self, text: str, *, force: bool = False) -> None:
        """Use focus-based readback; blur first so JAWS re-reads each new message."""
        self._blur_status_focus()
        announce_status_message(
            self.status_bar,
            text,
            move_focus=True,
            force_focus_announce=force,
            restore_focus=False,
            update_visible=True,
        )
