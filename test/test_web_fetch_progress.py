"""Tests for web fetch progress dialog and message numbering."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication

from src.ui.web_fetch_progress import WebFetchProgressDialog
from src.web.web_book_api import _source_progress_message


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


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
