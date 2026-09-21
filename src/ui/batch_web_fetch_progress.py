"""Progress dialog for batch web metadata fetch (N of M)."""

from __future__ import annotations

import threading

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAccessible, QAccessibleEvent, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QProgressBar,
    QSizePolicy,
    QStatusBar,
    QVBoxLayout,
)

from src.accessibility.accessible_events import (
    announce_dialog_opened,
    configure_status_bar_accessibility,
)
from src.accessibility.screen_reader import (
    get_screen_reader_focus_delay_ms,
    is_screen_reader_active,
)
from src.ui.accessible_dialog import AccessibleDialog
from src.ui.web_fetch_progress import FetchStatusLabel


class BatchWebFetchProgressDialog(AccessibleDialog):
    """Modal progress for multi-book web fetch. Escape cancels the queue."""

    help_doc_override = "07_web_metadata.md"

    def __init__(self, total: int, parent=None):
        super().__init__(parent)
        from src.accessibility.icon_helper import get_app_icon

        self.setWindowIcon(get_app_icon())
        self.total = max(1, total)
        self.cancel_event = threading.Event()
        self._user_canceled = False
        self._open_announced = False
        self.setWindowTitle("Batch web fetch")
        self.setModal(True)
        self.setAccessibleName("Batch web fetch progress")
        self.setAccessibleDescription(
            f"Fetching web metadata for {self.total} books. Escape to cancel."
        )

        layout = QVBoxLayout(self)
        self.status_label = FetchStatusLabel("Escape to cancel.")
        self.status_label.setWordWrap(True)
        self.status_label.setFocusPolicy(Qt.NoFocus)
        self.status_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        layout.addWidget(self.status_label)

        self.bar = QProgressBar()
        self.bar.setRange(0, self.total)
        self.bar.setValue(0)
        self.bar.setAccessibleName("Batch fetch progress")
        self.bar.setFixedHeight(22)
        self.bar.setStyleSheet(
            "QProgressBar {"
            "  min-height: 22px;"
            "  max-height: 22px;"
            "  border: 1px solid palette(dark);"
            "  border-radius: 3px;"
            "  text-align: center;"
            "  background-color: palette(base);"
            "}"
            "QProgressBar::chunk {"
            "  background-color: palette(highlight);"
            "}"
        )
        layout.addWidget(self.bar)

        self.status_bar = QStatusBar()
        configure_status_bar_accessibility(self.status_bar)
        layout.addWidget(self.status_bar)

        self._escape_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self._escape_shortcut.setContext(Qt.WindowShortcut)
        self._escape_shortcut.activated.connect(self.request_cancel)
        self.setMinimumWidth(587)
        self.resize(587, 160)

        from src.ui.help_router import install_shift_f1_help

        self.context_help_shortcut = install_shift_f1_help(
            self, shortcut_context=Qt.WidgetWithChildrenShortcut
        )
        self.status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.status_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.status_shortcut.activated.connect(self._read_status)
        self._f1_shortcut = QShortcut(QKeySequence("F1"), self)
        self._f1_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self._f1_shortcut.activated.connect(self._show_shortcuts)

    def _read_status(self) -> None:
        from src.accessibility.accessible_events import read_status_bar_message

        read_status_bar_message(self.status_bar)

    def _show_shortcuts(self) -> None:
        from src.accessibility.shortcut_helpers import exec_f1_shortcuts_dialog

        exec_f1_shortcuts_dialog(
            self,
            "Keyboard Shortcuts - Batch web fetch",
            [
                ("Escape", "Cancel the remaining queue"),
                ("Alt+/", "Read status bar"),
                ("F1", "Show keyboard shortcuts"),
            ],
        )

    @property
    def cancel_requested(self) -> bool:
        return self._user_canceled

    def request_cancel(self) -> None:
        if self._user_canceled:
            return
        self._user_canceled = True
        self.cancel_event.set()
        self.update_progress(self.bar.value(), "Canceling…")

    def update_progress(self, current: int, title: str) -> None:
        self.bar.setValue(min(current, self.total))
        if title == "Canceling…":
            text = "Canceling…"
        else:
            text = f"Book {current} of {self.total}: {title}. Escape to cancel."
        self.status_label.set_status_text(text)
        self.setAccessibleDescription(text)
        self.status_bar.showMessage(text)
        self._speak_status(text)

    def _speak_status(self, text: str) -> None:
        text = (text or "").strip()
        if not text:
            return
        if not (QAccessible.isActive() or is_screen_reader_active()):
            return
        self.status_label.setFocusPolicy(Qt.StrongFocus)
        self.status_label.setFocus(Qt.OtherFocusReason)
        QApplication.processEvents()
        if QAccessible.isActive():
            QAccessible.updateAccessibility(
                QAccessibleEvent(self.status_label, QAccessible.Event.Focus)
            )
        self.setFocus(Qt.OtherFocusReason)
        self.status_label.setFocusPolicy(Qt.NoFocus)
        QApplication.processEvents()

    def showEvent(self, event):
        super().showEvent(event)
        self.raise_()
        self.activateWindow()
        if not self._open_announced:
            self._open_announced = True
            announce_dialog_opened(
                self, "Batch web fetch progress. Escape to cancel."
            )
            delay = max(300, get_screen_reader_focus_delay_ms())
            QTimer.singleShot(delay, lambda: self._speak_status(self.status_label.text()))
