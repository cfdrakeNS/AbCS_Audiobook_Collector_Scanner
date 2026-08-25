"""Book details accessibility: status readback and idle status text."""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt

from src.accessibility.scaling import UIScaler
from src.accessibility.theme_manager import ThemeManager
from src.database.connection import DatabaseManager
from src.database.models import Book
from src.database.queries import AuthorQueries, BookQueries
from src.ui.book_details import BookDetailsWindow


def _ensure_sample_books(db: DatabaseManager, count: int = 2) -> list[Book]:
    books = BookQueries(db).get_all()
    while len(books) < count:
        index = len(books)
        author_id = AuthorQueries(db).insert(f"Accessibility Author {index}")
        BookQueries(db).insert(
            Book(title=f"Accessibility Book {index}", author_id=author_id)
        )
        books = BookQueries(db).get_all()
    return books


def test_idle_status_includes_title_and_author(qapp, temp_db):
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    books = _ensure_sample_books(temp_db, count=1)

    window = BookDetailsWindow(
        temp_db,
        scaler,
        book=books[0],
        parent=None,
        theme_manager=theme_manager,
    )
    message = window._idle_status_message()
    assert message.endswith(".")
    assert " by " in message
    assert window.status_bar.currentMessage() == message
    window.close()


def test_status_bar_has_no_sighted_tooltip(qapp, temp_db):
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    books = _ensure_sample_books(temp_db, count=1)

    window = BookDetailsWindow(
        temp_db,
        scaler,
        book=books[0],
        parent=None,
        theme_manager=theme_manager,
    )
    assert window.status_bar.toolTip() == ""
    window.close()


def test_page_navigation_focuses_title(qapp, temp_db, monkeypatch):
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    books = _ensure_sample_books(temp_db, count=2)

    window = BookDetailsWindow(
        temp_db,
        scaler,
        book=books[0],
        books_list=books,
        current_index=0,
        parent=None,
        theme_manager=theme_manager,
    )
    focus_calls = []

    def track_focus(reason=Qt.OtherFocusReason):
        focus_calls.append(reason)

    monkeypatch.setattr(window.title_edit, "setFocus", track_focus)
    monkeypatch.setattr(
        "src.ui.book_details.QTimer.singleShot",
        lambda _ms, fn: fn(),
    )

    window.on_next()
    assert focus_calls
    assert window.title_edit.text() == books[1].title
    window.close()
