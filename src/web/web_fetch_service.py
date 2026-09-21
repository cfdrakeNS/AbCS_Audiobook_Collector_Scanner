"""Shared orchestration for web metadata fetch from UI call sites.

Fetch runs on a QThread worker. The progress dialog's ``exec()`` keeps the
caller blocked while the GUI stays responsive, then returns ``WebFetchResult``
as before.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any, Optional

from PySide6.QtCore import QObject, QThread, Qt, Signal, Slot

from src.ui.web_fetch_progress import WebFetchProgressDialog
from src.web.web_book_api import (
    clean_web_data,
    format_web_fetch_dialog_text,
    format_web_fetch_status_message,
    get_web_api,
)


@dataclass
class WebFetchResult:
    """Outcome of a single web metadata fetch attempt."""

    raw_data: Optional[dict] = None
    cleaned_data: Optional[dict] = None
    errors: list[str] = field(default_factory=list)
    canceled: bool = False
    last_error: Optional[str] = None
    status_message: str = ""
    dialog_text: str = ""

    @property
    def has_usable_data(self) -> bool:
        return bool(self.cleaned_data) and not self.canceled


class _WebFetchWorker(QObject):
    """Runs ``get_book_metadata`` off the GUI thread."""

    progress = Signal(str)
    finished = Signal(object)  # raw dict | None
    failed = Signal(str)

    def __init__(
        self,
        *,
        title: str,
        author: str,
        year: Optional[str],
        refresh: int,
        narrator: str,
        path: str,
        source: str,
        comments: str,
        bypass_cache: bool,
        cancel_event: threading.Event,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._title = title
        self._author = author
        self._year = year
        self._refresh = refresh
        self._narrator = narrator
        self._path = path
        self._source = source
        self._comments = comments
        self._bypass_cache = bypass_cache
        self._cancel_event = cancel_event

    @Slot()
    def run(self) -> None:
        try:
            api = get_web_api()

            def _progress(message: str) -> None:
                self.progress.emit(message or "")

            def _should_cancel() -> bool:
                return self._cancel_event.is_set()

            raw = api.get_book_metadata(
                self._title,
                self._author,
                self._year,
                refresh=self._refresh,
                narrator=self._narrator,
                path=self._path,
                source=self._source,
                comments=self._comments,
                progress_callback=_progress,
                should_cancel=_should_cancel,
                bypass_cache=self._bypass_cache,
            )
            self.finished.emit(raw)
        except Exception as exc:
            self.failed.emit(str(exc))


class _WebFetchUiBridge(QObject):
    """Receives worker signals on the GUI thread (plain callables do not)."""

    def __init__(self, popup: WebFetchProgressDialog, holder: dict[str, Any]) -> None:
        super().__init__()
        self._popup = popup
        self._holder = holder

    @Slot(str)
    def on_progress(self, message: str) -> None:
        self._popup.update_message(message)

    @Slot(object)
    def on_finished(self, raw: object) -> None:
        self._holder["raw"] = raw
        self._popup.accept()

    @Slot(str)
    def on_failed(self, message: str) -> None:
        self._holder["error"] = message
        self._popup.accept()


def _build_result_from_raw(
    raw: Optional[dict], *, last_error: Optional[str] = None, user_canceled: bool = False
) -> WebFetchResult:
    result = WebFetchResult(last_error=last_error)

    if user_canceled or (raw and raw.get("_canceled")):
        result.canceled = True
        result.status_message = "Web fetch canceled."
        result.dialog_text = "Web fetch was canceled."
        return result

    result.raw_data = raw
    result.errors = list((raw or {}).get("_fetch_errors", []) or [])

    if raw and not raw.get("_no_result"):
        result.cleaned_data = clean_web_data(raw)
    else:
        result.cleaned_data = None

    if result.errors:
        result.status_message = format_web_fetch_status_message(result.errors)
        result.dialog_text = format_web_fetch_dialog_text(result.errors)
    elif result.cleaned_data:
        result.status_message = "Web data found."
        result.dialog_text = ""
    else:
        result.status_message = "No web data found for this book."
        result.dialog_text = "No information found for this book in any web source."
        if result.last_error:
            result.dialog_text = (
                f"{result.dialog_text}\n\nLast error: {result.last_error}"
            )
    return result


def _shutdown_thread(thread: QThread, timeout_ms: int = 15000) -> None:
    if thread.isRunning():
        thread.quit()
        if not thread.wait(timeout_ms):
            thread.terminate()
            thread.wait(2000)


def fetch_web_metadata_for_book(
    book: Any,
    *,
    parent=None,
    refresh: int = 0,
    bypass_cache: bool = False,
    show_progress: bool = True,
    cancel_event: threading.Event | None = None,
    progress_callback=None,
) -> WebFetchResult:
    """Run web metadata fetch with progress dialog, cancel, and cleaning.

    When ``show_progress`` is True, work runs on a ``QThread`` while
    ``WebFetchProgressDialog.exec()`` keeps the caller blocked and the UI
    responsive. When False (tests), the fetch runs synchronously on the
    calling thread.
    """
    title = getattr(book, "title", "") or ""
    author = getattr(book, "author_name", "") or ""
    year = None
    if getattr(book, "year", None):
        year = str(book.year)
    narrator = getattr(book, "reader", "") or ""
    path = getattr(book, "path", "") or ""
    source = getattr(book, "source", "") or ""
    comments = getattr(book, "comments", "") or ""

    if not show_progress:
        cancel_event = cancel_event or threading.Event()
        try:
            api = get_web_api()
            raw = api.get_book_metadata(
                title,
                author,
                year,
                refresh=refresh,
                narrator=narrator,
                path=path,
                source=source,
                comments=comments,
                progress_callback=progress_callback,
                should_cancel=lambda: cancel_event.is_set(),
                bypass_cache=bypass_cache,
            )
            return _build_result_from_raw(raw)
        except Exception as exc:
            return _build_result_from_raw(None, last_error=str(exc))

    popup = WebFetchProgressDialog(parent)
    thread = QThread()
    worker = _WebFetchWorker(
        title=title,
        author=author,
        year=year,
        refresh=refresh,
        narrator=narrator,
        path=path,
        source=source,
        comments=comments,
        bypass_cache=bypass_cache,
        cancel_event=popup.cancel_event,
    )
    worker.moveToThread(thread)

    holder: dict[str, Any] = {"raw": None, "error": None}
    bridge = _WebFetchUiBridge(popup, holder)

    worker.progress.connect(bridge.on_progress, Qt.ConnectionType.QueuedConnection)
    worker.finished.connect(bridge.on_finished, Qt.ConnectionType.QueuedConnection)
    worker.failed.connect(bridge.on_failed, Qt.ConnectionType.QueuedConnection)
    thread.started.connect(worker.run)

    thread.start()
    try:
        popup.exec()
    finally:
        user_canceled = popup.cancel_requested
        popup.cancel_event.set()
        _shutdown_thread(thread)
        worker.deleteLater()
        bridge.deleteLater()
        thread.deleteLater()
        popup.close()

    return _build_result_from_raw(
        holder["raw"], last_error=holder["error"], user_canceled=user_canceled
    )
