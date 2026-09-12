"""Shared orchestration for web metadata fetch from UI call sites."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from PySide6.QtWidgets import QApplication

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


def fetch_web_metadata_for_book(
    book: Any,
    *,
    parent=None,
    refresh: int = 0,
    bypass_cache: bool = False,
    show_progress: bool = True,
) -> WebFetchResult:
    """Run web metadata fetch with progress dialog, cancel, and cleaning.

    Args:
        book: Book-like object with title, author_name, year, reader, path, etc.
        parent: Qt parent for the progress dialog.
        refresh: Passed to WebBookAPI (0=all sources, 1=skip Open Library, …).
        bypass_cache: True for Re-fetch (Alt+F).
        show_progress: When False, skip the progress dialog (tests).
    """
    result = WebFetchResult()
    popup: WebFetchProgressDialog | None = None

    title = getattr(book, "title", "") or ""
    author = getattr(book, "author_name", "") or ""
    year = None
    if getattr(book, "year", None):
        year = str(book.year)

    try:
        if show_progress:
            popup = WebFetchProgressDialog(parent)
            popup.show()
            QApplication.processEvents()

        api = get_web_api()

        def _should_cancel() -> bool:
            return bool(popup and popup.cancel_requested)

        progress_cb = popup.update_message if popup else None

        try:
            raw = api.get_book_metadata(
                title,
                author,
                year,
                refresh=refresh,
                narrator=getattr(book, "reader", "") or "",
                path=getattr(book, "path", "") or "",
                source=getattr(book, "source", "") or "",
                comments=getattr(book, "comments", "") or "",
                progress_callback=progress_cb,
                should_cancel=_should_cancel if popup else None,
                bypass_cache=bypass_cache,
            )
        except Exception as exc:
            result.last_error = str(exc)
            raw = None

        if raw and raw.get("_canceled"):
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
            result.dialog_text = (
                "No information found for this book in any web source."
            )
            if result.last_error:
                result.dialog_text = (
                    f"{result.dialog_text}\n\nLast error: {result.last_error}"
                )

        return result
    finally:
        if popup is not None:
            popup.close()
