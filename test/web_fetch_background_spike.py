"""
Throwaway JAWS spike for background web-fetch accessibility.

Not collected by pytest. Run:
    python test/web_fetch_background_spike.py

Verify with JAWS (NVDA optional) before any production QThread fetch:

1. Progress spoken while the fake worker runs.
2. Tab / arrows work during the wait (work is off the GUI thread).
3. Completion in foreground: title and default button announced.
4. Start again, Alt+Tab away before finish, then back — completion still announced.
5. Start again, Escape — cancel announced; focus returns here.

Only after 1–5 pass should Phase 1 production thread work start.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PySide6.QtCore import QObject, QThread, Qt, Signal, Slot, QTimer
from PySide6.QtWidgets import QApplication, QLabel, QMessageBox, QPushButton, QVBoxLayout

from src.accessibility.icon_helper import get_app_icon
from src.accessibility.style_helpers import (
    build_accessible_button_style,
    exec_styled_message_box,
)
from src.ui.accessible_dialog import AccessibleDialog
from src.ui.web_fetch_progress import WebFetchProgressDialog


class _FakeWorker(QObject):
    progress = Signal(str)
    finished = Signal()

    def __init__(self, cancel_event, parent=None):
        super().__init__(parent)
        self._cancel = cancel_event

    @Slot()
    def run(self) -> None:
        steps = [
            "Trying source 1: Open Library…",
            "Trying source 2: Google Books…",
            "Looking up plot…",
            "Finishing…",
        ]
        for message in steps:
            if self._cancel.is_set():
                self.progress.emit("Canceling web fetch…")
                self.finished.emit()
                return
            self.progress.emit(message)
            time.sleep(1.2)
        self.finished.emit()


class _SpikeUiBridge(QObject):
    """Receives worker signals on the GUI thread (plain callables do not)."""

    def __init__(self, popup: WebFetchProgressDialog):
        super().__init__()
        self._popup = popup

    @Slot(str)
    def on_progress(self, message: str) -> None:
        self._popup.update_message(message)

    @Slot()
    def on_finished(self) -> None:
        self._popup.accept()


class SpikeWindow(AccessibleDialog):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(get_app_icon())
        self.setWindowTitle("Background fetch spike")
        self.setAccessibleName("Background fetch spike")
        self.setAccessibleDescription(
            "Manual JAWS harness for background web fetch. "
            "Press Start fake fetch, then check progress speech, Tab, "
            "completion, Alt+Tab away, and Escape cancel."
        )
        button_style = build_accessible_button_style(20)

        layout = QVBoxLayout(self)
        instructions = QLabel(
            "The wait dialog is modal. You cannot use this window until it closes.\n"
            "Stay on Please wait. Press Escape to cancel.\n\n"
            "1. Start fake fetch — progress should speak.\n"
            "2. Escape should still work while progress speaks.\n"
            "3. Let it finish (do not press Escape) — completion should announce.\n"
            "4. Start again, Alt+Tab away before finish — completion should still announce.\n"
            "5. Start again, press Escape — cancel should announce."
        )
        instructions.setWordWrap(True)
        instructions.setFocusPolicy(Qt.StrongFocus)
        layout.addWidget(instructions)

        start = QPushButton("Start fake fetch")
        start.setAccessibleName("Start fake fetch")
        start.setAccessibleDescription(
            "Run a fake background fetch using the real progress dialog"
        )
        start.setStyleSheet(button_style)
        start.setDefault(True)
        start.clicked.connect(self.run_fake_fetch)
        layout.addWidget(start)

        close_btn = QPushButton("Close")
        close_btn.setAccessibleName("Close")
        close_btn.setAccessibleDescription("Close the spike window")
        close_btn.setStyleSheet(button_style)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        self.resize(520, 300)
        start.setFocus(Qt.OtherFocusReason)

    def run_fake_fetch(self) -> None:
        popup = WebFetchProgressDialog(self)
        thread = QThread()
        worker = _FakeWorker(popup.cancel_event)
        worker.moveToThread(thread)
        bridge = _SpikeUiBridge(popup)
        worker.progress.connect(bridge.on_progress, Qt.ConnectionType.QueuedConnection)
        worker.finished.connect(bridge.on_finished, Qt.ConnectionType.QueuedConnection)
        thread.started.connect(worker.run)
        thread.start()
        popup.exec()
        canceled = popup.cancel_requested
        popup.cancel_event.set()
        thread.quit()
        thread.wait(5000)
        worker.deleteLater()
        bridge.deleteLater()
        thread.deleteLater()
        popup.close()

        title = "Canceled" if canceled else "Web fetch complete"
        text = (
            "Fake fetch was canceled."
            if canceled
            else (
                "Fake fetch finished. If JAWS read this dialog title and the "
                "default button, scenario 3 (or 4 after Alt+Tab) passed."
            )
        )
        exec_styled_message_box(
            self,
            20,
            icon=QMessageBox.Information,
            title=title,
            text=text,
            window_icon=get_app_icon(),
        )
        self.raise_()
        self.activateWindow()


def main() -> int:
    app = QApplication(sys.argv)
    win = SpikeWindow()
    win.show()
    QTimer.singleShot(0, win.raise_)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
