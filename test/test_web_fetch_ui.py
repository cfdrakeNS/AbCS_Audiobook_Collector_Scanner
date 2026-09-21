"""Web fetch progress dialog and fetch-service UI wiring tests."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from src.ui.web_fetch_progress import WebFetchProgressDialog
from src.web.web_book_api import _source_progress_message
from src.web.web_fetch_service import fetch_web_metadata_for_book


@pytest.fixture
def api(web_api):
    return web_api


def test_source_progress_message_fixed_numbers():
    assert _source_progress_message("open_library") == "Trying source 1: Open Library…"
    assert _source_progress_message("google_books") == "Trying source 2: Google Books…"
    assert _source_progress_message("wikidata") == "Trying source 3: WikiData…"
    assert (
        _source_progress_message("open_library", phase="broadened")
        == "Broadened search, Open Library…"
    )
    assert (
        _source_progress_message("google_books", phase="title_only")
        == "Title-only search, Google Books…"
    )

def test_progress_dialog_update_message_replaces_label(qapp):
    popup = WebFetchProgressDialog()
    try:
        popup.update_message("Trying source 1: Open Library…")
        assert popup._message_label.text() == "Trying source 1: Open Library…"
        assert popup._message_label.accessibleName() == "Trying source 1: Open Library…"
        popup.update_message("Trying source 2: Google Books…")
        assert popup._message_label.text() == "Trying source 2: Google Books…"
        assert popup._message_label.accessibleName() == "Trying source 2: Google Books…"
        assert popup.status_bar.currentMessage() == "Trying source 2: Google Books…"
    finally:
        popup.close()

def test_progress_dialog_request_cancel_sets_flag(qapp):
    popup = WebFetchProgressDialog()
    try:
        assert popup.cancel_requested is False
        popup.request_cancel()
        assert popup.cancel_requested is True
        assert popup.cancel_event.is_set() is True
        assert "Cancel" in popup._message_label.text()
        # Second cancel is a no-op
        popup.request_cancel()
        assert popup.cancel_requested is True
    finally:
        popup.close()


def test_fetch_service_canceled(qapp, api, monkeypatch):
    class Book:
        title = "Test"
        author_name = "Author"
        year = None
        reader = ""
        path = ""
        source = ""
        comments = ""

    def fake_get(*_a, **_k):
        return {"_canceled": True}

    monkeypatch.setattr("src.web.web_fetch_service.get_web_api", lambda: api)
    monkeypatch.setattr(api, "get_book_metadata", fake_get)
    result = fetch_web_metadata_for_book(Book(), show_progress=False)
    assert result.canceled
    assert "canceled" in result.status_message.lower()

def test_fetch_service_cleans_success(qapp, api, monkeypatch):
    class Book:
        title = "Pride and Prejudice"
        author_name = "Jane Austen"
        year = None
        reader = ""
        path = ""
        source = ""
        comments = ""

    raw = {
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "plot": "A" * 100,
        "source": "open_library",
    }

    monkeypatch.setattr("src.web.web_fetch_service.get_web_api", lambda: api)
    monkeypatch.setattr(api, "get_book_metadata", lambda *a, **k: raw)
    result = fetch_web_metadata_for_book(Book(), show_progress=False)
    assert result.has_usable_data
    assert result.cleaned_data["title"] == "Pride and Prejudice"


def test_fetch_service_runs_on_worker_thread(qapp, api, monkeypatch):
    """Worker ``run`` executes get_book_metadata off the GUI thread."""
    import threading

    from PySide6.QtCore import QThread, Qt

    from src.web.web_fetch_service import _WebFetchWorker

    caller_ident = threading.get_ident()
    seen = {"worker_ident": None}
    cancel_event = threading.Event()

    def fake_get(*_a, **_k):
        seen["worker_ident"] = threading.get_ident()
        return {
            "title": "Pride and Prejudice",
            "author": "Jane Austen",
            "plot": "A" * 100,
            "source": "open_library",
        }

    monkeypatch.setattr("src.web.web_fetch_service.get_web_api", lambda: api)
    monkeypatch.setattr(api, "get_book_metadata", fake_get)

    thread = QThread()
    worker = _WebFetchWorker(
        title="Pride and Prejudice",
        author="Jane Austen",
        year=None,
        refresh=0,
        narrator="",
        path="",
        source="",
        comments="",
        bypass_cache=False,
        cancel_event=cancel_event,
    )
    worker.moveToThread(thread)
    holder = {"raw": None}

    def _on_finished(raw):
        holder["raw"] = raw
        thread.quit()

    worker.finished.connect(_on_finished, Qt.ConnectionType.QueuedConnection)
    thread.started.connect(worker.run)
    thread.start()
    assert thread.wait(10000)
    worker.deleteLater()
    thread.deleteLater()

    assert holder["raw"] is not None
    assert seen["worker_ident"] is not None
    assert seen["worker_ident"] != caller_ident

