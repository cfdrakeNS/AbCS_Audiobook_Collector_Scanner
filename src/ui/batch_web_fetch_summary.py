"""Accessible summary dialog after a batch web metadata fetch."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from src.accessibility.accessible_events import (
    announce_dialog_opened,
    announce_status_message,
    configure_status_bar_accessibility,
    read_status_bar_message,
)
from src.accessibility.shortcut_helpers import exec_f1_shortcuts_dialog
from src.accessibility.style_helpers import (
    apply_tooltip_accessibility,
    build_accessible_button_style,
    build_table_polish_style,
    exec_styled_message_box,
)
from src.ui.accessible_dialog import AccessibleDialog
from src.web.batch_web_fetch import (
    BatchBookResult,
    BatchFetchOutcome,
    _match_lacks_plot,
)


def _result_reason(item: BatchBookResult) -> str:
    if item.fetch.canceled:
        return "canceled"
    if item.error or item.fetch.last_error:
        return "error"
    if item.has_changes:
        return "new information"
    if item.fetch.cleaned_data:
        if _match_lacks_plot(item):
            return "no plot"
        return "up to date"
    return "no match"


def _issue_text(item: BatchBookResult) -> str:
    reason = _result_reason(item)
    if reason == "new information":
        return "new information"
    if reason == "no match":
        return "No match was found in web sources."
    if reason == "no plot":
        return "A match was found but no usable plot was available to save."
    if reason == "up to date":
        return "Stored fields are already up to date."
    if reason == "canceled":
        return "Not fetched because the queue was canceled."
    return item.error or item.fetch.last_error or "The fetch reported an error."


def _row_status_message(item: BatchBookResult) -> str:
    if _result_reason(item) == "new information":
        return "Save. Review."
    return _issue_text(item)


class BatchWebFetchSummaryDialog(AccessibleDialog):
    """Modal summary: Apply all / Review each. Escape discards."""

    help_doc_override = "07_web_metadata.md"

    APPLY_ALL = 1
    REVIEW_EACH = 2
    CANCEL = 0

    def __init__(self, outcome: BatchFetchOutcome, parent=None):
        super().__init__(parent)
        from src.accessibility.icon_helper import get_app_icon

        self.setWindowIcon(get_app_icon())
        self._choice = self.CANCEL
        self.outcome = outcome
        self._row_items: list[BatchBookResult] = list(outcome.results) or []
        self._total = len(outcome.results)
        self._with_changes = len(outcome.with_changes)
        self._no_match = len(outcome.no_match)
        self._unchanged = len(outcome.unchanged)
        self._no_plot = len(outcome.no_plot)
        self._errored = len(outcome.errored)

        total = len(outcome.results)
        with_changes = len(outcome.with_changes)
        no_match = len(outcome.no_match)
        unchanged = len(outcome.unchanged)
        no_plot = len(outcome.no_plot)
        errored = len(outcome.errored)
        canceled_note = (
            " Fetch was canceled before all books finished." if outcome.canceled else ""
        )

        summary = (
            f"Batch web fetch finished. "
            f"{total} book{'s' if total != 1 else ''} processed. "
            f"{with_changes} with new information. "
            f"{no_match} with no match. "
            f"{unchanged} already up to date. "
            f"{no_plot} with no plot. "
            f"{errored} with errors.{canceled_note}"
        )
        self.setWindowTitle("Batch web fetch")
        self.setAccessibleName("Batch web fetch summary")
        self.setAccessibleDescription(summary)
        self.setModal(True)

        layout = QVBoxLayout(self)
        self.summary_label = QLabel(summary)
        self.summary_label.setWordWrap(True)
        self.summary_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.summary_label.setObjectName("batchWebFetchSummaryDescription")
        self.summary_label.setFocusPolicy(Qt.TabFocus)
        self.summary_label.setAccessibleName(summary)
        self.summary_label.setAccessibleDescription("Batch web fetch instructions")
        self.summary_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.summary_label.setStyleSheet(
            "QLabel#batchWebFetchSummaryDescription {"
            "  background-color: palette(base);"
            "  border: 1px solid palette(mid);"
            "  padding: 5px;"
            "}"
        )
        layout.addWidget(self.summary_label)

        self.books_table = QTableWidget()
        self.books_table.setAccessibleName("Books list")
        self.books_table.setAccessibleDescription(
            "Fetched books and their results. Use Up and Down arrows to move. "
            "Enter opens details for the highlighted book. Alt+L to jump here."
        )
        self.books_table.setColumnCount(2)
        self.books_table.setHorizontalHeaderLabels(["Title", "Issue"])
        self.books_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.books_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.books_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.books_table.setTabKeyNavigation(False)
        self.books_table.setFocusPolicy(Qt.StrongFocus)
        self.books_table.setAlternatingRowColors(False)
        self.books_table.setShowGrid(False)
        self.books_table.setMouseTracking(False)
        self.books_table.viewport().setMouseTracking(False)
        self.books_table.setAttribute(Qt.WA_Hover, False)
        self.books_table.viewport().setAttribute(Qt.WA_Hover, False)
        vh = self.books_table.verticalHeader()
        vh.setVisible(False)
        vh.setHighlightSections(False)
        header = self.books_table.horizontalHeader()
        header.setHighlightSections(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.books_table.setStyleSheet(build_table_polish_style())
        apply_tooltip_accessibility(
            self.books_table,
            "Fetched books and issues",
            "Title and fetch issue for each book",
        )

        rows = self._row_items
        self.books_table.setRowCount(max(len(rows), 1))
        if not rows:
            empty = QTableWidgetItem("No books were processed.")
            empty.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.books_table.setItem(0, 0, empty)
        for row, item in enumerate(rows):
            book = item.book
            title = getattr(book, "title", "") or "Untitled"
            reason = _result_reason(item)
            title_item = QTableWidgetItem(title)
            issue_item = QTableWidgetItem(reason)
            accessible = f"{title}: {reason}"
            title_item.setData(Qt.AccessibleTextRole, accessible)
            issue_item.setData(Qt.AccessibleTextRole, accessible)
            for cell in (title_item, issue_item):
                cell.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.books_table.setItem(row, 0, title_item)
            self.books_table.setItem(row, 1, issue_item)
        if rows:
            self.books_table.selectRow(0)
            self.books_table.setCurrentCell(0, 0)
        self.books_table.cellActivated.connect(self._on_row_activated)
        self.books_table.currentCellChanged.connect(self._on_table_current_changed)
        layout.addWidget(self.books_table)

        scaler = getattr(parent, "scaler", None)
        if scaler is not None:
            scaled_height = scaler.get_scaled_size(20)
        else:
            from src.accessibility.scaling import UIScaler

            scaled_height = UIScaler(QApplication.instance()).get_scaled_size(20)
        self._scaled_height = scaled_height
        button_style = build_accessible_button_style(scaled_height)

        buttons = QHBoxLayout()
        self.apply_btn = QPushButton("Apply all")
        self.apply_btn.setAccessibleName("Apply all")
        self.apply_btn.setAccessibleDescription(
            "Apply new web fields to all books that have changes - Alt+A"
        )
        self.apply_btn.setDefault(True)
        self.apply_btn.setStyleSheet(button_style)
        self.apply_btn.clicked.connect(self._on_apply)
        self.apply_btn.setEnabled(with_changes > 0)

        self.review_btn = QPushButton("Review each")
        self.review_btn.setAccessibleName("Review each")
        self.review_btn.setAccessibleDescription(
            "Open the web metadata window for each book with changes - Alt+R"
        )
        if with_changes == 1:
            self.review_btn.setText("Review")
            self.review_btn.setAccessibleName("Review")
            self.review_btn.setAccessibleDescription(
                "Open the web metadata window for the one book with new information - Alt+R"
            )
        self.review_btn.setStyleSheet(button_style)
        self.review_btn.clicked.connect(self._on_review)
        self.review_btn.setEnabled(with_changes > 0)

        buttons.addWidget(self.apply_btn)
        buttons.addWidget(self.review_btn)
        layout.addLayout(buttons)

        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        configure_status_bar_accessibility(self.status_bar)
        layout.addWidget(self.status_bar)

        self.resize(560, 420)
        QShortcut(QKeySequence(Qt.Key_Escape), self, activated=self._on_escape)
        QShortcut(QKeySequence("Alt+A"), self, activated=self.apply_btn.click)
        QShortcut(QKeySequence("Alt+R"), self, activated=self.review_btn.click)
        self._list_shortcut = QShortcut(QKeySequence("Alt+L"), self)
        self._list_shortcut.setContext(Qt.WindowShortcut)
        self._list_shortcut.activated.connect(self._focus_book_list)
        self._f1_shortcut = QShortcut(QKeySequence("F1"), self)
        self._f1_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self._f1_shortcut.activated.connect(self._show_shortcuts)
        self._status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self._status_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self._status_shortcut.activated.connect(
            lambda: read_status_bar_message(self.status_bar)
        )

        from src.ui.help_router import install_shift_f1_help

        self.context_help_shortcut = install_shift_f1_help(
            self, shortcut_context=Qt.WidgetWithChildrenShortcut
        )

    def _idle_status_message(self) -> str:
        parts = [
            f"{self._total} processed.",
            f"{self._with_changes} with new information.",
            f"{self._no_match} with no match.",
            f"{self._unchanged} already up to date.",
            f"{self._no_plot} with no plot.",
            f"{self._errored} with errors.",
        ]
        if self._with_changes == 1:
            parts.append("Apply all.")
            parts.append("Review.")
        elif self._with_changes > 1:
            parts.append("Apply all.")
            parts.append("Review each.")
        parts.append("Escape to close.")
        return " ".join(parts)

    def _set_status(self, message: str, *, announce: bool = True) -> None:
        announce_status_message(
            self.status_bar,
            message,
            move_focus=announce,
            restore_focus=True,
            update_visible=True,
        )

    def _focus_book_list(self) -> None:
        if self.books_table.rowCount() > 0 and self.books_table.currentRow() < 0:
            self.books_table.selectRow(0)
            self.books_table.setCurrentCell(0, 0)
        self.books_table.setFocus(Qt.ShortcutFocusReason)
        self._announce_row_status()

    def _refresh_counts_from_rows(self) -> None:
        self._with_changes = sum(
            1 for item in self._row_items if item.has_changes and not item.fetch.canceled
        )
        self._no_match = sum(
            1
            for item in self._row_items
            if _result_reason(item) == "no match"
        )
        self._unchanged = sum(
            1 for item in self._row_items if _result_reason(item) == "up to date"
        )
        self._no_plot = sum(
            1 for item in self._row_items if _result_reason(item) == "no plot"
        )
        self._errored = sum(
            1 for item in self._row_items if _result_reason(item) == "error"
        )
        self.apply_btn.setEnabled(self._with_changes > 0)
        self.review_btn.setEnabled(self._with_changes > 0)
        if self._with_changes == 1:
            self.review_btn.setText("Review")
            self.review_btn.setAccessibleName("Review")
        if self._with_changes > 1:
            self.review_btn.setText("Review each")
            self.review_btn.setAccessibleName("Review each")

    def _announce_row_status(self) -> None:
        row = self.books_table.currentRow()
        if 0 <= row < len(self._row_items):
            self._set_status(_row_status_message(self._row_items[row]), announce=False)
            return
        self._set_status(self._idle_status_message(), announce=False)

    def _on_table_current_changed(
        self, row: int, _col: int, _prev_row: int, _prev_col: int
    ) -> None:
        if 0 <= row < len(self._row_items):
            self._set_status(_row_status_message(self._row_items[row]), announce=False)

    def _fit_summary_label_height(self) -> None:
        text = self.summary_label.text() or " "
        width = max(self.summary_label.width(), self.width() - 40, 280)
        metrics = self.summary_label.fontMetrics()
        rect = metrics.boundingRect(0, 0, width, 2000, Qt.TextWordWrap, text)
        padding = 16
        target = max(48, min(rect.height() + padding, 220))
        self.summary_label.setMinimumHeight(target)
        self.summary_label.setMaximumHeight(target)

    def _on_row_activated(self, row: int, _column: int) -> None:
        if row < 0 or row >= len(self._row_items):
            return
        item = self._row_items[row]
        reason = _result_reason(item)
        book = item.book
        title = getattr(book, "title", "") or "Untitled"
        if reason == "new information":
            choice = self._exec_save_or_review_dialog(title)
            if choice == "save":
                self._save_row(row, item)
            elif choice == "review":
                self._review_row(item)
            return
        from src.accessibility.icon_helper import get_app_icon

        exec_styled_message_box(
            self,
            self._scaled_height,
            icon=QMessageBox.Information,
            title="Web fetch result",
            text=_issue_text(item),
            window_icon=get_app_icon(),
        )

    def _exec_save_or_review_dialog(self, title: str) -> str:
        dlg = AccessibleDialog(self)
        dlg.setWindowTitle("Web fetch result")
        dlg.setAccessibleName("Web fetch result")
        dlg.setAccessibleDescription(
            f"New information for {title}. Save, Review, or Escape to close."
        )
        dlg.setModal(True)
        layout = QVBoxLayout(dlg)
        label = QLabel(f"New information was found for {title}.")
        label.setWordWrap(True)
        label.setFocusPolicy(Qt.StrongFocus)
        layout.addWidget(label)
        buttons = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setAccessibleName("Save")
        save_btn.setAccessibleDescription("Apply the new web fields to this book")
        save_btn.setStyleSheet(build_accessible_button_style(self._scaled_height))
        review_btn = QPushButton("Review")
        review_btn.setAccessibleName("Review")
        review_btn.setAccessibleDescription("Open the web metadata window for this book")
        review_btn.setDefault(True)
        review_btn.setStyleSheet(build_accessible_button_style(self._scaled_height))
        buttons.addWidget(save_btn)
        buttons.addWidget(review_btn)
        layout.addLayout(buttons)
        choice = {"value": "dismiss"}

        def _save():
            choice["value"] = "save"
            dlg.accept()

        def _review():
            choice["value"] = "review"
            dlg.accept()

        save_btn.clicked.connect(_save)
        review_btn.clicked.connect(_review)
        QShortcut(QKeySequence(Qt.Key_Escape), dlg, activated=dlg.reject)
        dlg.show()
        review_btn.setFocus(Qt.OtherFocusReason)
        dlg.exec()
        return choice["value"]

    def _save_row(self, row: int, item: BatchBookResult) -> None:
        parent = self.owner_widget
        db = getattr(parent, "db", None)
        if db is None or not item.fetch.cleaned_data:
            return
        from src.web.batch_web_fetch import apply_web_changes_to_book

        apply_web_changes_to_book(db, item.book, item.fetch.cleaned_data)
        item.has_changes = False
        result_item = self.books_table.item(row, 1)
        if result_item is not None:
            result_item.setText("saved")
            title_item = self.books_table.item(row, 0)
            title_text = title_item.text() if title_item else "Untitled"
            accessible = f"{title_text}: saved"
            result_item.setData(Qt.AccessibleTextRole, accessible)
            if title_item is not None:
                title_item.setData(Qt.AccessibleTextRole, accessible)
        self._refresh_counts_from_rows()
        self._announce_row_status()

    def _review_row(self, item: BatchBookResult) -> None:
        parent = self.owner_widget
        scaler = getattr(parent, "scaler", None)
        theme_manager = getattr(parent, "theme_manager", None)
        db = getattr(parent, "db", None)
        if scaler is None or theme_manager is None:
            return
        from src.ui.web_metadata import WebMetadataWindow

        dialog = WebMetadataWindow(
            db,
            item.book,
            scaler,
            theme_manager,
            parent=parent,
            refresh_callback=None,
            web_data=item.fetch.raw_data or item.fetch.cleaned_data,
        )
        dialog.raise_()
        dialog.activateWindow()
        dialog.exec()

    def _show_shortcuts(self) -> None:
        exec_f1_shortcuts_dialog(
            self,
            "Keyboard Shortcuts - Batch web fetch",
            [
                ("Enter", "Open the highlighted book"),
                ("Alt+L", "Books list"),
                ("Alt+A", "Apply all"),
                ("Alt+R", "Review each"),
                ("Escape", "Close and discard results"),
                ("Alt+/", "Read status bar"),
                ("F1", "Show keyboard shortcuts"),
            ],
        )

    def _on_apply(self) -> None:
        if not self.apply_btn.isEnabled():
            return
        self._choice = self.APPLY_ALL
        self.accept()

    def _on_review(self) -> None:
        if not self.review_btn.isEnabled():
            return
        self._choice = self.REVIEW_EACH
        self.accept()

    def _on_escape(self) -> None:
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
        self._fit_summary_label_height()
        self._set_status(self._idle_status_message(), announce=False)
        QTimer.singleShot(0, self._focus_book_list)
