"""
Throwaway JAWS spike for background web-fetch accessibility.

Not collected by pytest. Run:
    python test/web_fetch_background_spike.py

Verifies:
1. Progress spoken while a fake worker runs on a QThread
2. UI stays responsive (Tab) during the wait
3. Completion dialog announced in foreground
4. After Alt+Tab away, completion still raises/activates (manual check)
5. Escape / Alt+C cancel mid-fetch
"""

from __future__ import annotations

import sys
import time

from PySide6.QtCore import QObject, QThread, Qt, Signal, Slot, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
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


class SpikeWindow(AccessibleDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Background fetch spike")
        self.setAccessibleName("Background fetch spike")
        self.setAccessibleDescription(
            "Manual JAWS harness for background web fetch. "
            "Press Start fake fetch, then check progress speech, Tab, "
            "completion, Alt+Tab away, and Escape cancel."
        )
        layout = QVBoxLayout(self)
        instructions = QLabel(
            "1. Start fake fetch — progress should speak.\n"
            "2. Tab during fetch — app should stay responsive.\n"
            "3. Let it finish — completion dialog should announce.\n"
            "4. Start again, Alt+Tab away before finish — dialog should still announce.\n"
            "5. Start again, press Escape or Alt+C — cancel should announce."
        )
        instructions.setWordWrap(True)
        instructions.setFocusPolicy(Qt.StrongFocus)
        layout.addWidget(instructions)

        start = QPushButton("Start fake fetch")
        start.setAccessibleName("Start fake fetch")
        start.clicked.connect(self.run_fake_fetch)
        layout.addWidget(start)

        close_btn = QPushButton("Close")
        close_btn.setAccessibleName("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        self.resize(520, 280)

    def run_fake_fetch(self) -> None:
        popup = WebFetchProgressDialog(self)
        thread = QThread()
        worker = _FakeWorker(popup.cancel_event)
        worker.moveToThread(thread)
        worker.progress.connect(popup.update_message, Qt.ConnectionType.QueuedConnection)

        def _done() -> None:
            popup.accept()

        worker.finished.connect(_done, Qt.ConnectionType.QueuedConnection)
        thread.started.connect(worker.run)
        thread.start()
        popup.exec()
        popup.cancel_event.set()
        thread.quit()
        thread.wait(5000)
        worker.deleteLater()
        thread.deleteLater()
        popup.close()

        if popup.cancel_requested:
            QMessageBox.information(
                self,
                "Canceled",
                "Fake fetch was canceled.",
            )
        else:
            QMessageBox.information(
                self,
                "Web fetch complete",
                "Fake fetch finished. If JAWS read this dialog title and the "
                "default button, scenario 3 (or 4 after Alt+Tab) passed.",
            )


def main() -> int:
    app = QApplication(sys.argv)
    win = SpikeWindow()
    win.show()
    QTimer.singleShot(0, win.raise_)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
