"""Accessible summary dialog after a batch web metadata fetch."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)

from src.accessibility.accessible_events import announce_dialog_opened
from src.ui.accessible_dialog import AccessibleDialog
from src.web.batch_web_fetch import BatchFetchOutcome


class BatchWebFetchSummaryDialog(AccessibleDialog):
    """Modal summary: Apply all / Review each / Cancel."""

    APPLY_ALL = 1
    REVIEW_EACH = 2
    CANCEL = 0

    def __init__(self, outcome: BatchFetchOutcome, parent=None):
        super().__init__(parent)
        from src.accessibility.icon_helper import get_app_icon

        self.setWindowIcon(get_app_icon())
        self._choice = self.CANCEL
        self.outcome = outcome

        total = len(outcome.results)
        with_changes = len(outcome.with_changes)
        no_match = len(outcome.no_match)
        errored = len(outcome.errored)

        summary = (
            f"Batch web fetch finished. "
            f"{total} book{'s' if total != 1 else ''} processed. "
            f"{with_changes} with new information. "
            f"{no_match} with no match. "
            f"{errored} with errors."
        )
        self.setWindowTitle("Batch web fetch")
        self.setAccessibleName("Batch web fetch summary")
        self.setAccessibleDescription(summary)
        self.setModal(True)

        layout = QVBoxLayout(self)
        label = QLabel(summary)
        label.setWordWrap(True)
        label.setFocusPolicy(Qt.StrongFocus)
        label.setAccessibleName("Batch fetch summary")
        layout.addWidget(label)

        self.miss_list = QListWidget()
        self.miss_list.setAccessibleName("Books with no match or errors")
        for item in outcome.no_match + outcome.errored:
            book = item.book
            title = getattr(book, "title", "") or "Untitled"
            author = getattr(book, "author_name", "") or ""
            reason = "error" if (item.error or item.fetch.last_error) else "no match"
            text = f"{title} — {author} ({reason})" if author else f"{title} ({reason})"
            self.miss_list.addItem(QListWidgetItem(text))
        if self.miss_list.count() == 0:
            self.miss_list.addItem(QListWidgetItem("All books returned usable changes."))
            self.miss_list.setEnabled(False)
        layout.addWidget(self.miss_list)

        buttons = QHBoxLayout()
        self.apply_btn = QPushButton("Apply all")
        self.apply_btn.setAccessibleName("Apply all")
        self.apply_btn.setAccessibleDescription(
            "Apply new web fields to all books that have changes"
        )
        self.apply_btn.setDefault(True)
        self.apply_btn.clicked.connect(self._on_apply)
        self.apply_btn.setEnabled(with_changes > 0)

        self.review_btn = QPushButton("Review each")
        self.review_btn.setAccessibleName("Review each")
        self.review_btn.setAccessibleDescription(
            "Open the web metadata window for each book with changes"
        )
        self.review_btn.clicked.connect(self._on_review)
        self.review_btn.setEnabled(with_changes > 0)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setAccessibleName("Cancel")
        self.cancel_btn.setAccessibleDescription("Discard fetched results")
        self.cancel_btn.clicked.connect(self._on_cancel)

        buttons.addWidget(self.apply_btn)
        buttons.addWidget(self.review_btn)
        buttons.addWidget(self.cancel_btn)
        layout.addLayout(buttons)

        self.resize(520, 360)
        QShortcut(QKeySequence(Qt.Key_Escape), self, activated=self._on_cancel)

    def _on_apply(self) -> None:
        self._choice = self.APPLY_ALL
        self.accept()

    def _on_review(self) -> None:
        self._choice = self.REVIEW_EACH
        self.accept()

    def _on_cancel(self) -> None:
        self._choice = self.CANCEL
        self.reject()

    @property
    def choice(self) -> int:
        return self._choice

    def showEvent(self, event):
        super().showEvent(event)
        self.raise_()
        self.activateWindow()
        announce_dialog_opened(self, "Batch web fetch summary")
        self.apply_btn.setFocus(Qt.OtherFocusReason) if self.apply_btn.isEnabled() else self.cancel_btn.setFocus(
            Qt.OtherFocusReason
        )
