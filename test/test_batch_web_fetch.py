"""Tests for batch web fetch helpers."""

from __future__ import annotations

import os
import threading
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from src.ui.web_metadata import WebMetadataWindow
from src.web.batch_web_fetch import (
    BatchBookResult,
    BatchFetchOutcome,
    apply_web_changes_to_book,
    collect_batch_results,
)
from src.web.web_fetch_service import WebFetchResult


def test_batch_outcome_counts():
    book_a = SimpleNamespace(title="A", author_name="Auth")
    book_b = SimpleNamespace(title="B", author_name="Auth")
    book_c = SimpleNamespace(title="C", author_name="Auth")
    book_d = SimpleNamespace(title="D", author_name="Auth")
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
            BatchBookResult(
                book=book_d,
                fetch=WebFetchResult(cleaned_data={"title": "D", "plot": "P" * 90}),
                has_changes=False,
            ),
            BatchBookResult(
                book=SimpleNamespace(title="E", author_name="Auth", comments=""),
                fetch=WebFetchResult(cleaned_data={"title": "E"}),
                has_changes=False,
            ),
        ]
    )
    assert len(outcome.with_changes) == 1
    assert len(outcome.no_match) == 1
    assert len(outcome.errored) == 1
    assert len(outcome.unchanged) == 1
    assert len(outcome.no_plot) == 1


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


def test_collect_batch_cancel_stops_queue():
    books = [
        SimpleNamespace(title="A", author_name="Auth"),
        SimpleNamespace(title="B", author_name="Auth"),
    ]
    cancel = threading.Event()
    cancel.set()
    outcome = collect_batch_results(books, cancel)
    assert outcome.canceled
    assert outcome.results == []


def test_collect_batch_cancel_after_first(monkeypatch):
    books = [
        SimpleNamespace(title="A", author_name="Auth"),
        SimpleNamespace(title="B", author_name="Auth"),
    ]
    cancel = threading.Event()
    calls = {"n": 0}

    def fake_fetch(book, **_kwargs):
        calls["n"] += 1
        cancel.set()
        return WebFetchResult(
            cleaned_data={"title": book.title, "author": "Auth", "plot": "P" * 90},
            raw_data={"title": book.title},
        )

    monkeypatch.setattr(
        "src.web.batch_web_fetch.fetch_web_metadata_for_book", fake_fetch
    )
    monkeypatch.setattr(
        WebMetadataWindow,
        "web_data_offers_changes",
        staticmethod(lambda *_a, **_k: True),
    )
    outcome = collect_batch_results(books, cancel)
    assert calls["n"] == 1
    assert outcome.canceled
    assert len(outcome.results) == 1


def test_collect_batch_uses_fetch_per_book(monkeypatch):
    books = [
        SimpleNamespace(title="A", author_name="Auth"),
        SimpleNamespace(title="B", author_name="Auth"),
    ]
    seen = []

    def fake_fetch(book, **kwargs):
        seen.append(book.title)
        assert kwargs.get("show_progress") is False
        return WebFetchResult(cleaned_data={"title": book.title})

    monkeypatch.setattr(
        "src.web.batch_web_fetch.fetch_web_metadata_for_book", fake_fetch
    )
    monkeypatch.setattr(
        WebMetadataWindow,
        "web_data_offers_changes",
        staticmethod(lambda *_a, **_k: False),
    )
    outcome = collect_batch_results(books, threading.Event())
    assert seen == ["A", "B"]
    assert not outcome.canceled
    assert len(outcome.results) == 2


def test_apply_web_changes_to_book_title_only():
    book = SimpleNamespace(
        title="Old",
        author_name="Author",
        year=None,
        genre_name="",
        comments="",
        author_id=1,
        genre_id=None,
    )
    web = {"title": "New Title From Web Lookup That Differs"}
    author = SimpleNamespace(name="Author")
    with patch("src.database.queries.AuthorQueries") as aq_cls, patch(
        "src.database.queries.GenreQueries"
    ) as gq_cls, patch("src.database.queries.BookQueries") as bq_cls:
        aq = aq_cls.return_value
        aq.get_by_id.return_value = author
        gq_cls.return_value.get_by_id.return_value = None
        applied = apply_web_changes_to_book(MagicMock(), book, web)
    assert "Title" in applied
    assert book.title == "New Title From Web Lookup That Differs"
    bq_cls.return_value.update.assert_called_once()


def test_summary_dialog_focus_default_apply(qapp):
    from src.ui.batch_web_fetch_summary import BatchWebFetchSummaryDialog

    book = SimpleNamespace(title="A", author_name="Auth")
    outcome = BatchFetchOutcome(
        results=[
            BatchBookResult(
                book=book,
                fetch=WebFetchResult(cleaned_data={"title": "A"}),
                has_changes=True,
            )
        ]
    )
    dlg = BatchWebFetchSummaryDialog(outcome)
    try:
        dlg.show()
        qapp.processEvents()
        assert not dlg.apply_btn.isDefault()
        assert not dlg.apply_btn.autoDefault()
        assert not dlg.review_btn.isDefault()
        assert not dlg.review_btn.autoDefault()
        assert dlg.apply_btn.isEnabled()
        assert not hasattr(dlg, "cancel_btn")
        assert "1 with new information" in dlg.accessibleDescription()
        assert dlg.books_table.columnCount() == 2
        assert dlg.books_table.horizontalHeaderItem(1).text() == "Issue"
        assert dlg.review_btn.text() == "Review"
        assert dlg.books_table.currentRow() == 0
        assert dlg.books_table.hasFocus()
        issue = dlg.books_table.item(0, 1).text()
        assert issue == "Metadata found"
        assert dlg.books_table.columnWidth(0) >= 140
        assert dlg.books_table.columnWidth(1) <= 220
        assert "Apply all" in dlg.status_bar.currentMessage()
        assert "Review" in dlg.status_bar.currentMessage()
        assert "Escape to close" in dlg.status_bar.currentMessage()
    finally:
        dlg.close()


def test_enter_in_summary_list_does_not_apply_all(qapp):
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from src.ui.batch_web_fetch_summary import BatchWebFetchSummaryDialog

    book = SimpleNamespace(title="A", author_name="Auth")
    outcome = BatchFetchOutcome(
        results=[
            BatchBookResult(
                book=book,
                fetch=WebFetchResult(cleaned_data={"title": "A"}),
                has_changes=True,
            )
        ]
    )
    dlg = BatchWebFetchSummaryDialog(outcome)
    try:
        dlg.show()
        qapp.processEvents()
        dlg.books_table.setFocus()
        QTest.keyClick(dlg.books_table, Qt.Key_Return)
        qapp.processEvents()
        assert dlg.isVisible()
        assert dlg.choice == BatchWebFetchSummaryDialog.CANCEL
        assert dlg.saved_any is False
        assert dlg.books_table.item(0, 1).text() == "Metadata found"
    finally:
        dlg.close()


def test_change_issue_label_plot_or_metadata():
    from src.ui.batch_web_fetch_summary import _change_issue_label

    book = SimpleNamespace(
        title="A",
        author_name="Auth",
        year=None,
        genre_name=None,
        comments="",
    )
    plot_only = BatchBookResult(
        book=book,
        fetch=WebFetchResult(
            cleaned_data={"title": "A", "author": "Auth", "plot": "A full plot from the web."}
        ),
        has_changes=True,
    )
    meta_only = BatchBookResult(
        book=book,
        fetch=WebFetchResult(cleaned_data={"title": "Changed Title From Web"}),
        has_changes=True,
    )
    both = BatchBookResult(
        book=book,
        fetch=WebFetchResult(
            cleaned_data={
                "title": "Changed Title From Web",
                "plot": "A full plot from the web.",
            }
        ),
        has_changes=True,
    )
    assert _change_issue_label(plot_only) == "Plot found"
    assert _change_issue_label(meta_only) == "Metadata found"
    assert _change_issue_label(both) == "Plot found. Metadata found"


def test_summary_status_alt_shortcuts_when_screen_reader(qapp, monkeypatch):
    from src.ui.batch_web_fetch_summary import BatchWebFetchSummaryDialog

    monkeypatch.setattr(
        "src.ui.batch_web_fetch_summary.is_screen_reader_active",
        lambda: True,
    )
    book = SimpleNamespace(title="A", author_name="Auth")
    outcome = BatchFetchOutcome(
        results=[
            BatchBookResult(
                book=book,
                fetch=WebFetchResult(cleaned_data={"title": "A"}),
                has_changes=True,
            )
        ]
    )
    dlg = BatchWebFetchSummaryDialog(outcome)
    try:
        dlg.show()
        qapp.processEvents()
        assert (
            dlg.status_bar.currentMessage()
            == "Alt+A Apply all. Alt+R Review. Escape to close."
        )
    finally:
        dlg.close()


def test_review_button_keeps_summary_open_after_save(qapp, monkeypatch):
    from PySide6.QtWidgets import QDialog
    from src.ui.batch_web_fetch_summary import BatchWebFetchSummaryDialog

    visible_during_review = []

    class FakeMeta:
        def __init__(self, *args, **kwargs):
            return None

        def raise_(self):
            return None

        def activateWindow(self):
            return None

        def exec(self):
            visible_during_review.append(dlg.isVisible())
            return QDialog.Accepted

    monkeypatch.setattr("src.ui.web_metadata.WebMetadataWindow", FakeMeta)
    book = SimpleNamespace(title="A", author_name="Auth")
    outcome = BatchFetchOutcome(
        results=[
            BatchBookResult(
                book=book,
                fetch=WebFetchResult(cleaned_data={"title": "A"}),
                has_changes=True,
            )
        ]
    )
    dlg = BatchWebFetchSummaryDialog(outcome)
    try:
        dlg.show()
        qapp.processEvents()
        dlg._on_review()
        qapp.processEvents()
        assert visible_during_review == [False]
        assert dlg.isVisible()
        assert dlg.choice == BatchWebFetchSummaryDialog.CANCEL
        assert dlg.saved_any is True
        assert dlg.books_table.item(0, 1).text() == "saved"
        assert not dlg.review_btn.isEnabled()
        assert not hasattr(dlg, "_on_row_activated")
        assert not hasattr(dlg, "_exec_save_or_review_dialog")
    finally:
        dlg.close()


def test_progress_dialog_says_escape_to_cancel(qapp):
    from src.ui.batch_web_fetch_progress import BatchWebFetchProgressDialog

    dlg = BatchWebFetchProgressDialog(3)
    try:
        assert "Escape to cancel" in dlg.accessibleDescription()
        dlg.update_progress(1, "Dune")
        assert "Escape to cancel" in dlg.status_label.text()
        assert "Book 1 of 3" in dlg.status_label.text()
    finally:
        dlg.close()


def test_review_batch_opens_each_book_then_refreshes(monkeypatch):
    from src.web.batch_web_fetch import review_batch_results

    created = []

    class FakeDlg:
        def __init__(self, *args, **kwargs):
            created.append(kwargs)

        def raise_(self):
            return None

        def activateWindow(self):
            return None

        def exec(self):
            return 1

    monkeypatch.setattr("src.web.batch_web_fetch.WebMetadataWindow", FakeDlg)
    refresh = MagicMock()
    book_a = SimpleNamespace(title="A")
    book_b = SimpleNamespace(title="B")
    outcome = BatchFetchOutcome(
        results=[
            BatchBookResult(
                book=book_a,
                fetch=WebFetchResult(cleaned_data={"title": "A"}),
                has_changes=True,
            ),
            BatchBookResult(
                book=book_b,
                fetch=WebFetchResult(cleaned_data={"title": "B"}),
                has_changes=True,
            ),
        ]
    )
    review_batch_results(
        outcome,
        db=None,
        scaler=None,
        theme_manager=None,
        refresh_callback=refresh,
    )
    assert len(created) == 2
    assert created[0]["queue_index"] == 1
    assert created[1]["queue_index"] == 2
    assert all(item["refresh_callback"] is None for item in created)
    refresh.assert_called_once()


def test_result_reason_no_plot_vs_up_to_date():
    from src.ui.batch_web_fetch_summary import _result_reason

    empty = SimpleNamespace(title="E", comments="")
    stub = SimpleNamespace(title="S", comments="A L Fraine")
    filled = SimpleNamespace(title="F", comments="Existing plot text here. " * 8)
    no_plot = BatchBookResult(
        book=empty,
        fetch=WebFetchResult(cleaned_data={"title": "E", "author": "A"}),
        has_changes=False,
    )
    stub_plot = BatchBookResult(
        book=stub,
        fetch=WebFetchResult(cleaned_data={"title": "S", "author": "A"}),
        has_changes=False,
    )
    up_to_date = BatchBookResult(
        book=filled,
        fetch=WebFetchResult(cleaned_data={"title": "F", "author": "A"}),
        has_changes=False,
    )
    assert _result_reason(no_plot) == "no plot"
    assert _result_reason(stub_plot) == "no plot"
    assert _result_reason(up_to_date) == "up to date"
