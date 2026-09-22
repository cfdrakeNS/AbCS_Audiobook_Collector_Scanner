"""Keep the focused book as current after sort and filter."""

from __future__ import annotations

from datetime import date

from src.database.models import Book
from src.database.queries import AuthorQueries, BookQueries


def _current_book_id(window):
    row = window.table.currentRow()
    if 0 <= row < len(window.books):
        return window.books[row].book_id
    return None


def _insert_focus_books(window):
    authors = AuthorQueries(window.db)
    books = BookQueries(window.db)
    zebra = authors.insert("Zebra Author")
    alpha = authors.insert("Alpha Author")
    middle = authors.insert("Middle Author")
    id_middle = books.insert(
        Book(title="Middle Book", author_id=zebra, year=2000, tracks=1, path="/m")
    )
    id_alpha = books.insert(
        Book(
            title="Alpha Book",
            author_id=alpha,
            year=1990,
            tracks=1,
            path="/a",
            read_date=date(2020, 1, 1),
        )
    )
    id_zulu = books.insert(
        Book(title="Zulu Book", author_id=middle, year=2010, tracks=1, path="/z")
    )
    window.refresh_books()
    window.on_order_changed("Title")
    return id_middle, id_alpha, id_zulu


def test_author_sort_keeps_focused_book(main_window, qapp, qtbot):
    window = main_window
    id_middle, _id_alpha, _id_zulu = _insert_focus_books(window)
    window.focus_book_by_id(id_middle, 1)
    assert _current_book_id(window) == id_middle

    window.on_order_changed("Author")
    qapp.processEvents()
    qtbot.wait(20)

    assert _current_book_id(window) == id_middle
    assert window.books[window.table.currentRow()].title == "Middle Book"


def test_year_sort_keeps_focused_book(main_window, qapp, qtbot):
    window = main_window
    _id_middle, _id_alpha, id_zulu = _insert_focus_books(window)
    window.focus_book_by_id(id_zulu, 1)
    assert _current_book_id(window) == id_zulu

    window._sort_actions_by_key["Year"].trigger()
    qapp.processEvents()
    qtbot.wait(20)

    assert _current_book_id(window) == id_zulu
    years = [book.year or 0 for book in window.books]
    assert years == sorted(years)


def test_unread_filter_keeps_unread_book(main_window, qapp, qtbot):
    window = main_window
    id_middle, _id_alpha, _id_zulu = _insert_focus_books(window)
    window.focus_book_by_id(id_middle, 1)
    window.on_read_filter_changed("Unread")
    qapp.processEvents()
    qtbot.wait(20)

    assert _current_book_id(window) == id_middle


def test_read_filter_moves_when_book_excluded(main_window, qapp, qtbot):
    window = main_window
    id_middle, id_alpha, _id_zulu = _insert_focus_books(window)
    window.focus_book_by_id(id_middle, 1)
    window.on_read_filter_changed("Read")
    qapp.processEvents()
    qtbot.wait(20)

    assert _current_book_id(window) == id_alpha
