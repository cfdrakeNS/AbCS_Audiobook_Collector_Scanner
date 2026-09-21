"""Batch web metadata fetch queue and apply helpers."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any, Callable

from PySide6.QtCore import QObject, QThread, Qt, Signal, Slot
from PySide6.QtWidgets import QApplication

from src.ui.batch_web_fetch_progress import BatchWebFetchProgressDialog
from src.ui.web_metadata import WebMetadataWindow
from src.web.web_book_api import PLOT_MIN_LENGTH
from src.web.web_fetch_service import WebFetchResult, fetch_web_metadata_for_book


def _has_usable_plot(text: str) -> bool:
    return len((text or "").strip()) >= PLOT_MIN_LENGTH


def _match_lacks_plot(result: "BatchBookResult") -> bool:
    """True when a web match exists but neither side has a usable plot."""
    web = result.fetch.cleaned_data or {}
    web_plot = str(web.get("plot") or "").strip()
    book_plot = str(getattr(result.book, "comments", None) or "").strip()
    return not _has_usable_plot(web_plot) and not _has_usable_plot(book_plot)


@dataclass
class BatchBookResult:
    book: Any
    fetch: WebFetchResult
    has_changes: bool = False
    error: str = ""


@dataclass
class BatchFetchOutcome:
    results: list[BatchBookResult] = field(default_factory=list)
    canceled: bool = False

    @property
    def with_changes(self) -> list[BatchBookResult]:
        return [r for r in self.results if r.has_changes and not r.fetch.canceled]

    @property
    def no_match(self) -> list[BatchBookResult]:
        return [
            r
            for r in self.results
            if not r.fetch.canceled
            and not r.has_changes
            and not r.error
            and not r.fetch.last_error
            and not r.fetch.cleaned_data
        ]

    @property
    def unchanged(self) -> list[BatchBookResult]:
        return [
            r
            for r in self.results
            if not r.fetch.canceled
            and not r.has_changes
            and not r.error
            and not r.fetch.last_error
            and r.fetch.cleaned_data
            and not _match_lacks_plot(r)
        ]

    @property
    def no_plot(self) -> list[BatchBookResult]:
        return [
            r
            for r in self.results
            if not r.fetch.canceled
            and not r.has_changes
            and not r.error
            and not r.fetch.last_error
            and r.fetch.cleaned_data
            and _match_lacks_plot(r)
        ]

    @property
    def errored(self) -> list[BatchBookResult]:
        return [
            r
            for r in self.results
            if not r.fetch.canceled and (r.error or r.fetch.last_error)
        ]


def collect_batch_results(
    books: list[Any],
    cancel_event: threading.Event,
    on_progress: Callable[[int, int, str], None] | None = None,
) -> BatchFetchOutcome:
    """Fetch each book (no GUI wait dialog). Cooperative cancel via ``cancel_event``."""
    outcome = BatchFetchOutcome()
    total = len(books)
    for index, book in enumerate(books, start=1):
        if cancel_event.is_set():
            outcome.canceled = True
            break
        title = getattr(book, "title", "") or "Untitled"
        if on_progress:
            on_progress(index, total, title)
        fetch = fetch_web_metadata_for_book(
            book,
            parent=None,
            refresh=0,
            show_progress=False,
            cancel_event=cancel_event,
        )
        if fetch.canceled:
            outcome.canceled = True
            outcome.results.append(BatchBookResult(book=book, fetch=fetch))
            break
        has_changes = WebMetadataWindow.web_data_offers_changes(
            book, fetch.cleaned_data
        )
        err = fetch.last_error or ""
        if fetch.errors and not fetch.cleaned_data:
            err = err or "; ".join(fetch.errors[:2])
        outcome.results.append(
            BatchBookResult(
                book=book,
                fetch=fetch,
                has_changes=has_changes,
                error=err,
            )
        )
        if cancel_event.is_set():
            outcome.canceled = True
            break
    return outcome


class _BatchFetchWorker(QObject):
    progress = Signal(int, int, str)
    finished = Signal(object)

    def __init__(self, books: list[Any], cancel_event: threading.Event):
        super().__init__()
        self._books = books
        self._cancel_event = cancel_event

    @Slot()
    def run(self) -> None:
        def _progress(current: int, total: int, title: str) -> None:
            self.progress.emit(current, total, title)

        outcome = collect_batch_results(
            self._books, self._cancel_event, on_progress=_progress
        )
        self.finished.emit(outcome)


class _BatchFetchUiBridge(QObject):
    """Receives batch worker signals on the GUI thread."""

    def __init__(
        self, popup: BatchWebFetchProgressDialog, holder: dict[str, Any]
    ) -> None:
        super().__init__()
        self._popup = popup
        self._holder = holder

    @Slot(int, int, str)
    def on_progress(self, current: int, total: int, title: str) -> None:
        self._popup.update_progress(current, title)

    @Slot(object)
    def on_finished(self, outcome: object) -> None:
        self._holder["outcome"] = outcome
        self._popup.accept()


def run_batch_web_fetch_with_progress(
    books: list[Any], *, parent=None
) -> BatchFetchOutcome:
    """Run batch fetch on a worker thread with an N/M progress dialog."""
    if not books:
        return BatchFetchOutcome()

    popup = BatchWebFetchProgressDialog(len(books), parent)
    thread = QThread()
    worker = _BatchFetchWorker(list(books), popup.cancel_event)
    worker.moveToThread(thread)
    holder: dict[str, Any] = {"outcome": BatchFetchOutcome()}
    bridge = _BatchFetchUiBridge(popup, holder)

    worker.progress.connect(bridge.on_progress, Qt.ConnectionType.QueuedConnection)
    worker.finished.connect(bridge.on_finished, Qt.ConnectionType.QueuedConnection)
    thread.started.connect(worker.run)
    thread.start()
    try:
        popup.exec()
    finally:
        popup.cancel_event.set()
        thread.quit()
        thread.wait(60000)
        worker.deleteLater()
        bridge.deleteLater()
        thread.deleteLater()
        popup.close()
        QApplication.processEvents()

    return holder["outcome"]


def apply_web_changes_to_book(db, book, web_data: dict) -> list[str]:
    """Apply all field differences from cleaned web_data; return applied labels."""
    from src.database.queries import AuthorQueries, BookQueries, GenreQueries

    differences = WebMetadataWindow.compute_field_differences(book, web_data)
    if not differences:
        return []

    author_queries = AuthorQueries(db)
    genre_queries = GenreQueries(db)
    book_queries = BookQueries(db)
    applied: list[str] = []

    if "title" in differences:
        book.title = differences["title"].strip()
        applied.append("Title")

    if "author" in differences:
        author_name = differences["author"].strip()
        if author_name:
            existing = author_queries.get_by_name(author_name)
            if existing:
                book.author_id = existing.author_id
            else:
                book.author_id = author_queries.insert(author_name)
            applied.append("Author")

    if "year" in differences:
        year_text = str(differences["year"]).strip()
        try:
            book.year = int(year_text) if year_text else None
            applied.append("Year")
        except ValueError:
            book.year = None

    if "genre" in differences:
        genre_name = differences["genre"].strip()
        if genre_name:
            existing = genre_queries.get_by_name(genre_name)
            if existing:
                book.genre_id = existing.genre_id
            else:
                book.genre_id = genre_queries.insert(genre_name)
            applied.append("Genre")

    if "plot" in differences:
        plot_text = differences["plot"].strip("\n")
        if plot_text:
            book.comments = plot_text
            applied.append("Plot")

    if book.author_id:
        author = author_queries.get_by_id(book.author_id)
        book.author_name = author.name if author else ""
    if book.genre_id:
        genre = genre_queries.get_by_id(book.genre_id)
        book.genre_name = genre.name if genre else ""

    book_queries.update(book)
    return applied


def review_batch_results(
    outcome: BatchFetchOutcome,
    *,
    db,
    scaler,
    theme_manager,
    parent=None,
    refresh_callback=None,
) -> None:
    """Open Web Metadata for each book with changes; Save or Skip advances."""
    items = outcome.with_changes
    total = len(items)
    for index, item in enumerate(items, start=1):
        dialog = WebMetadataWindow(
            db,
            item.book,
            scaler,
            theme_manager,
            parent=parent,
            refresh_callback=None,
            web_data=item.fetch.raw_data or item.fetch.cleaned_data,
            queue_index=index,
            queue_total=total,
        )
        dialog.raise_()
        dialog.activateWindow()
        dialog.exec()
    if refresh_callback:
        refresh_callback()
