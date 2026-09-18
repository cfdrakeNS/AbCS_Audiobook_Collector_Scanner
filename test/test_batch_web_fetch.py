"""Tests for batch web fetch helpers."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from src.ui.web_metadata import WebMetadataWindow
from src.web.batch_web_fetch import BatchBookResult, BatchFetchOutcome
from src.web.web_fetch_service import WebFetchResult


def test_batch_outcome_counts():
    book_a = SimpleNamespace(title="A", author_name="Auth")
    book_b = SimpleNamespace(title="B", author_name="Auth")
    book_c = SimpleNamespace(title="C", author_name="Auth")
    outcome = BatchFetchOutcome(
        results=[
            BatchBookResult(
                book=book_a,
                fetch=WebFetchResult(cleaned_data={"title": "A"}),
                has_changes=True,
            ),
            BatchBookResult(
                book=book_b,
                fetch=WebFetchResult(cleaned_data=None),
                has_changes=False,
            ),
            BatchBookResult(
                book=book_c,
                fetch=WebFetchResult(last_error="boom"),
                has_changes=False,
                error="boom",
            ),
        ]
    )
    assert len(outcome.with_changes) == 1
    assert len(outcome.no_match) == 1
    assert len(outcome.errored) == 1


def test_web_data_offers_changes_used_by_batch():
    book = SimpleNamespace(
        title="Old",
        author_name="Author",
        year=None,
        genre_name="",
        comments="",
    )
    web = {"title": "New Title", "author": "Author", "plot": "A" * 100}
    assert WebMetadataWindow.web_data_offers_changes(book, web)
