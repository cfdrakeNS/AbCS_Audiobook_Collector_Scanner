"""Accessible summary dialog after a batch web metadata fetch."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
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
from src.accessibility.screen_reader import is_screen_reader_active
from src.accessibility.shortcut_helpers import exec_f1_shortcuts_dialog
from src.accessibility.style_helpers import (
    apply_tooltip_accessibility,
    build_modern_button_style,
    build_table_polish_style,
)
from src.ui.accessible_dialog import AccessibleDialog
from src.ui.web_metadata import WebMetadataWindow
from src.web.batch_web_fetch import (
    BatchBookResult,
    BatchFetchOutcome,
    _match_lacks_plot,
)


def _error_fragments(item: BatchBookResult) -> list[str]:
    fragments: list[str] = []
    if item.error:
        fragments.extend(part.strip() for part in item.error.split(";") if part.strip())
    if item.fetch.last_error:
        fragments.append(item.fetch.last_error.strip())
    fragments.extend(
        str(err).strip() for err in (item.fetch.errors or []) if str(err).strip()
    )
    return fragments


def _fragment_is_google_skip(fragment: str) -> bool:
    low = fragment.lower()
    if "google" not in low:
        return False
    return (
        "paused" in low
        or "429" in low
        or "too many requests" in low
        or "rate limit" in low
    )


def _google_skip_only(item: BatchBookResult) -> bool:
    """True when the row failed only because Google Books was not searched."""
    if item.fetch.cleaned_data or item.has_changes:
        return False
    fragments = _error_fragments(item)
    if not fragments:
        return False
    return all(_fragment_is_google_skip(fragment) for fragment in fragments)


def _batch_google_not_searched(items: list[BatchBookResult]) -> bool:
    from src.web.web_http import _is_source_cooling_down

    if _is_source_cooling_down("google_books"):
        return True
    return any(_fragment_is_google_skip(part) for item in items for part in _error_fragments(item))


def _google_limit_note() -> str:
    """Top-summary sentence with the minutes left on the Google Books pause."""
    from src.web.web_http import (
        RATE_LIMIT_COOLDOWN_DEFAULTS,
        _seconds_until_cooldown_clears,
    )

    remaining = _seconds_until_cooldown_clears("google_books")
    if remaining <= 0:
        remaining = float(RATE_LIMIT_COOLDOWN_DEFAULTS["google_books"])
    minutes = max(1, int(round(remaining / 60.0)))
    unit = "minute" if minutes == 1 else "minutes"
    return f" Google Books limit hit. Try in {minutes} {unit}."


def _result_reason(item: BatchBookResult) -> str:
    if item.fetch.canceled:
        return "canceled"
    if item.error or item.fetch.last_error:
        if _google_skip_only(item):
            return "no match"
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
        return _change_issue_label(item)
    if reason == "no match":
        return "No match found"
    if reason == "no plot":
        return "Match found. No plot was found."
    if reason == "up to date":
        return "Plot and metadata up to date."
    if reason == "canceled":
        return "Not fetched because the queue was canceled."
    return _error_issue_text(item)


def _error_issue_text(item: BatchBookResult) -> str:
    """Row text for a real fetch error. Google skip notes stay on the window summary."""
    kept = [
        fragment
        for fragment in _error_fragments(item)
        if not _fragment_is_google_skip(fragment)
    ]
    # item.error may already join several sources; prefer the non-Google pieces.
    if kept:
        return "; ".join(dict.fromkeys(kept))
    return "The fetch reported an error."


def _change_issue_label(item: BatchBookResult) -> str:
    """Match stand-alone fetch wording: Plot found and/or Metadata found."""
    web = item.fetch.cleaned_data or item.fetch.raw_data or {}
    plot = str(web.get("plot") or "").strip()
    diffs: dict = {}
    if web:
        try:
            diffs = WebMetadataWindow.compute_field_differences(item.book, web)
        except Exception:
            diffs = {
                key: value
                for key, value in web.items()
                if key != "plot" and value
            }
    parts: list[str] = []
    if plot:
        parts.append("Plot found")
    if any(key != "plot" for key in diffs):
        parts.append("Metadata found")
    if not parts:
        parts.append("Metadata found")
    return ". ".join(parts)


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
        self._saved_any = False
        self._silent_reshow = False
        self._announce_focus_on_show = True
        self.outcome = outcome
        self._row_items: list[BatchBookResult] = list(outcome.results) or []
        self._total = len(outcome.results)
        self._google_not_searched = _batch_google_not_searched(self._row_items)
        self._with_changes = sum(
            1 for item in self._row_items if _result_reason(item) == "new information"
        )
        self._no_match = sum(
            1 for item in self._row_items if _result_reason(item) == "no match"
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

        total = self._total
        with_changes = self._with_changes
        no_match = self._no_match
        unchanged = self._unchanged
        no_plot = self._no_plot
        errored = self._errored
        canceled_note = (
            " Fetch was canceled before all books finished." if outcome.canceled else ""
        )
        google_note = _google_limit_note() if self._google_not_searched else ""

        summary = (
            f"Batch web fetch finished. "
            f"{total} book{'s' if total != 1 else ''} processed. "
            f"{with_changes} with new information. "
            f"{no_match} with no match. "
            f"{unchanged} already up to date. "
            f"{no_plot} with no plot. "
            f"{errored} with errors.{canceled_note}{google_note}"
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
            "Alt+L to jump here. Alt+R to review books with changes."
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
        header.setMinimumSectionSize(160)
        header.setStretchLastSection(False)
        self.books_table.setTextElideMode(Qt.ElideRight)
        self.books_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.books_table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
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
            issue = _issue_text(item)
            title_item = QTableWidgetItem(title)
            issue_item = QTableWidgetItem(issue)
            accessible = f"{title}: {issue}"
            title_item.setData(Qt.AccessibleTextRole, accessible)
            issue_item.setData(Qt.AccessibleTextRole, accessible)
            for cell in (title_item, issue_item):
                cell.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.books_table.setItem(row, 0, title_item)
            self.books_table.setItem(row, 1, issue_item)
        if rows:
            self.books_table.selectRow(0)
            self.books_table.setCurrentCell(0, 0)
        self._size_summary_columns()
        layout.addWidget(self.books_table)

        scaler = getattr(parent, "scaler", None)
        if scaler is None:
            from src.accessibility.scaling import UIScaler

            scaler = UIScaler(QApplication.instance())
        scaled_height = scaler.get_scaled_size(20)
        self._scaled_height = scaled_height
        button_style = build_modern_button_style(scaled_height)
        from src.accessibility.icon_helper import apply_decorative_action_icon
        buttons = QHBoxLayout()
        self.apply_btn = QPushButton("Apply all")
        self.apply_btn.setAccessibleName("Apply all")
        self.apply_btn.setAccessibleDescription(
            "Apply new web fields to all books that have changes - Alt+A"
        )
        self.apply_btn.setDefault(False)
        self.apply_btn.setAutoDefault(False)
        self.apply_btn.setStyleSheet(button_style)
        apply_decorative_action_icon(self.apply_btn, "save", scaler)
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
        apply_decorative_action_icon(self.review_btn, "edit", scaler)
        self.review_btn.setDefault(False)
        self.review_btn.setAutoDefault(False)
        self.review_btn.clicked.connect(self._on_review)
        self.review_btn.setEnabled(with_changes > 0)

        buttons.addWidget(self.apply_btn)
        buttons.addWidget(self.review_btn)
        layout.addLayout(buttons)

        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        configure_status_bar_accessibility(self.status_bar)
        layout.addWidget(self.status_bar)

        self.resize(760, 420)
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
        if is_screen_reader_active():
            parts: list[str] = []
            if self._with_changes:
                parts.append("Alt+A Apply all")
                if self._with_changes == 1:
                    parts.append("Alt+R Review")
                else:
                    parts.append("Alt+R Review each")
            parts.append("Escape to close")
            return ". ".join(parts) + "."
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

    def _size_summary_columns(self) -> None:
        """Title and Issue both grow when the summary window is widened."""
        header = self.books_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

    def _fit_summary_label_height(self) -> None:
        text = self.summary_label.text() or " "
        width = max(self.summary_label.width(), self.width() - 40, 280)
        metrics = self.summary_label.fontMetrics()
        rect = metrics.boundingRect(0, 0, width, 2000, Qt.TextWordWrap, text)
        padding = 16
        target = max(48, min(rect.height() + padding, 220))
        self.summary_label.setMinimumHeight(target)
        self.summary_label.setMaximumHeight(target)

    def _mark_row_saved(self, row: int, item: BatchBookResult) -> None:
        item.has_changes = False
        self._saved_any = True
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
        if self.isVisible():
            self._set_status(self._idle_status_message(), announce=False)

    def _review_row(
        self,
        item: BatchBookResult,
        *,
        queue_index: int | None = None,
        queue_total: int | None = None,
    ) -> int:
        parent = self.owner_widget
        scaler = getattr(parent, "scaler", None)
        theme_manager = getattr(parent, "theme_manager", None)
        db = getattr(parent, "db", None)
        from src.ui.web_metadata import WebMetadataWindow

        dialog = WebMetadataWindow(
            db,
            item.book,
            scaler,
            theme_manager,
            parent=self,
            refresh_callback=None,
            web_data=item.fetch.raw_data or item.fetch.cleaned_data,
            queue_index=queue_index,
            queue_total=queue_total,
        )
        dialog.raise_()
        dialog.activateWindow()
        result = dialog.exec()
        return int(result)

    def _show_shortcuts(self) -> None:
        exec_f1_shortcuts_dialog(
            self,
            "Keyboard Shortcuts - Batch web fetch",
            [
                ("Alt+L", "Books list"),
                ("Alt+A", "Apply all"),
                ("Alt+R", "Review each"),
                ("Escape", "Close"),
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
        pending = [
            item
            for item in self._row_items
            if item.has_changes and not item.fetch.canceled
        ]
        total = len(pending)
        self._silent_reshow = True
        self._announce_focus_on_show = False
        self.status_bar.clearMessage()
        self.hide()
        try:
            for index, item in enumerate(pending, start=1):
                row = self._row_items.index(item)
                result = self._review_row(
                    item, queue_index=index, queue_total=total
                )
                if result == QDialog.Accepted:
                    self._mark_row_saved(row, item)
        finally:
            self.show()
            self.raise_()
            self.activateWindow()
            self._silent_reshow = False
            self._announce_focus_on_show = True
            self._focus_book_list()
            self._set_status(self._idle_status_message(), announce=False)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            focused = self.focusWidget()
            if isinstance(focused, QPushButton) and focused.isEnabled():
                focused.click()
                event.accept()
                return
            event.accept()
            return
        super().keyPressEvent(event)

    def _on_escape(self) -> None:
        self._choice = self.CANCEL
        self.reject()

    @property
    def saved_any(self) -> bool:
        return self._saved_any

    @property
    def choice(self) -> int:
        return self._choice

    def showEvent(self, event):
        super().showEvent(event)
        self.raise_()
        self.activateWindow()
        self._fit_summary_label_height()
        if self._silent_reshow:
            return
        announce_dialog_opened(self, "Batch web fetch summary")
        self._set_status(self._idle_status_message(), announce=False)
        QTimer.singleShot(0, self._focus_book_list)
