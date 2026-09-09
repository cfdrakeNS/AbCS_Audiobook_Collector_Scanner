"""Accessible modal dialog shown while fetching web book metadata."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAccessible, QAccessibleEvent, QKeySequence, QShortcut
from PySide6.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout

from src.accessibility.accessible_events import (
    announce_dialog_opened,
    configure_status_bar_accessibility,
)
from src.ui.accessible_dialog import AccessibleDialog
from src.accessibility.screen_reader import (
    get_screen_reader_focus_delay_ms,
    is_screen_reader_active,
)


class FetchStatusLabel(QLabel):
    """Status line that announces text changes to screen readers."""

    def set_status_text(self, text: str) -> None:
        text = (text or "").strip()
        if not text:
            return
        self.setText(text)
        self.setAccessibleName(text)
        self.setAccessibleDescription(text)
        if QAccessible.isActive():
            QAccessible.updateAccessibility(
                QAccessibleEvent(self, QAccessible.Event.NameChanged)
            )
            QAccessible.updateAccessibility(
                QAccessibleEvent(self, QAccessible.Event.DescriptionChanged)
            )


class WebFetchProgressDialog(AccessibleDialog):
    """Modal wait dialog with live status text for web metadata fetch.

    Cooperative cancel: Escape or Alt+C sets ``cancel_requested``. The fetch
    loop checks the flag between requests (after ``update_message`` pumps events).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        from src.accessibility.icon_helper import get_app_icon
        from PySide6.QtWidgets import QStatusBar

        self.setWindowIcon(get_app_icon())
        self.setWindowTitle("Please wait")
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setAccessibleName("Fetching web book information")
        self.setAccessibleDescription(
            "Searching online sources for book metadata. "
            "Press Escape or Alt+C to cancel."
        )

        self._cancel_requested = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 6)
        layout.setSpacing(8)

        self._message_label = FetchStatusLabel("Preparing web search…")
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
        self._last_spoken = ""
        self._initial_timer = QTimer(self)
        self._initial_timer.setSingleShot(True)
        self._initial_timer.timeout.connect(self._announce_initial)
        self.setFocusPolicy(Qt.StrongFocus)

        self._escape_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self._escape_shortcut.setContext(Qt.WindowShortcut)
        self._escape_shortcut.activated.connect(self.request_cancel)

        self._cancel_shortcut = QShortcut(QKeySequence("Alt+C"), self)
        self._cancel_shortcut.setContext(Qt.WindowShortcut)
        self._cancel_shortcut.activated.connect(self.request_cancel)

    @property
    def cancel_requested(self) -> bool:
        return self._cancel_requested

    def request_cancel(self) -> None:
        """Mark the fetch as canceled; checked between network requests."""
        if self._cancel_requested:
            return
        self._cancel_requested = True
        self.update_message("Canceling web fetch…")

    def show(self):
        super().show()
        self.raise_()
        self.activateWindow()
        QApplication.processEvents()
        announce_dialog_opened(self, "Fetching web book information")
        delay = max(300, get_screen_reader_focus_delay_ms())
        self._initial_timer.start(delay)

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
        self._speak_status(self._message_label.text(), force=True)

    def update_message(self, text: str) -> None:
        """Update visible status and announce for JAWS/NVDA."""
        text = (text or "").strip()
        if not text:
            return
        if self._initial_timer.isActive():
            self._initial_timer.stop()
        self._message_label.set_status_text(text)
        self.setAccessibleDescription(text)
        self.status_bar.showMessage(text)
        self._initial_announced = True
        self._message_label.update()
        self.repaint()
        QApplication.processEvents()
        self._speak_status(text, force=True)

    def _speak_status(self, text: str, *, force: bool = False) -> None:
        """Announce via the status label; each source change gets a focus pulse."""
        text = (text or "").strip()
        if not text:
            return
        if not force and text == self._last_spoken:
            return
        if not (QAccessible.isActive() or is_screen_reader_active()):
            self._last_spoken = text
            return

        self._last_spoken = text
        self._message_label.setFocusPolicy(Qt.StrongFocus)
        self._message_label.setFocus(Qt.OtherFocusReason)
        QApplication.processEvents()
        if QAccessible.isActive():
            QAccessible.updateAccessibility(
                QAccessibleEvent(self._message_label, QAccessible.Event.Focus)
            )
        self.setFocus(Qt.OtherFocusReason)
        self._message_label.setFocusPolicy(Qt.NoFocus)
        QApplication.processEvents()
