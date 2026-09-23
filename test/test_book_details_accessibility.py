"""Book details accessibility: status readback and idle status text."""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt

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

def test_idle_status_includes_title_and_author(temp_db, ui_scaler, theme_manager):
    books = _ensure_sample_books(temp_db, count=1)

    window = BookDetailsWindow(
        temp_db,
        ui_scaler,
        book=books[0],
        parent=None,
        theme_manager=theme_manager,
    )
    message = window._idle_status_message()
    assert message.endswith(".")
    assert " by " in message
    assert window.status_bar.currentMessage() == message
    window.close()

def test_status_bar_has_no_sighted_tooltip(temp_db, ui_scaler, theme_manager):
    books = _ensure_sample_books(temp_db, count=1)

    window = BookDetailsWindow(
        temp_db,
        ui_scaler,
        book=books[0],
        parent=None,
        theme_manager=theme_manager,
    )
    assert window.status_bar.toolTip() == ""
    window.close()

def test_display_stores_blank_series_number_from_title(
    temp_db, ui_scaler, theme_manager
):
    author_id = AuthorQueries(temp_db).insert("Series Display Author")
    books = BookQueries(temp_db)
    blank_id = books.insert(
        Book(title="Busted - 6.5", author_id=author_id, series_number=None)
    )
    kept_id = books.insert(
        Book(title="Other - 9", author_id=author_id, series_number=2)
    )
    year_id = books.insert(
        Book(title="Some Title, 1999", author_id=author_id, series_number=None)
    )

    window = BookDetailsWindow(
        temp_db,
        ui_scaler,
        book=books.get_by_id(blank_id),
        parent=None,
        theme_manager=theme_manager,
    )
    assert window.series_number_edit.text() == "6.5"
    assert window.book.series_number == 6.5
    assert window.book.title == "Busted - 6.5"
    assert window._dirty is False
    assert books.get_by_id(blank_id).series_number == 6.5
    window.close()

    kept = BookDetailsWindow(
        temp_db,
        ui_scaler,
        book=books.get_by_id(kept_id),
        parent=None,
        theme_manager=theme_manager,
    )
    assert kept.series_number_edit.text() == "2"
    assert books.get_by_id(kept_id).series_number == 2
    assert books.get_by_id(kept_id).title == "Other - 9"
    kept.close()

    year = BookDetailsWindow(
        temp_db,
        ui_scaler,
        book=books.get_by_id(year_id),
        parent=None,
        theme_manager=theme_manager,
    )
    assert year.series_number_edit.text() == ""
    assert books.get_by_id(year_id).series_number is None
    assert books.get_by_id(year_id).title == "Some Title, 1999"
    year.close()


def test_page_navigation_focuses_title(temp_db, ui_scaler, theme_manager, monkeypatch):
    books = _ensure_sample_books(temp_db, count=2)

    window = BookDetailsWindow(
        temp_db,
        ui_scaler,
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
