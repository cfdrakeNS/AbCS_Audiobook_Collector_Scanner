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
    collection_id = window.current_filter.collection_id
    zebra = authors.insert("Zebra Author")
    alpha = authors.insert("Alpha Author")
    middle = authors.insert("Middle Author")
    id_middle = books.insert(
        Book(
            title="Middle Book",
            author_id=zebra,
            year=2000,
            tracks=1,
            path="/m",
            collection_id=collection_id,
        )
    )
    id_alpha = books.insert(
        Book(
            title="Alpha Book",
            author_id=alpha,
            year=1990,
            tracks=1,
            path="/a",
            read_date=date(2020, 1, 1),
            collection_id=collection_id,
        )
    )
    id_zulu = books.insert(
        Book(
            title="Zulu Book",
            author_id=middle,
            year=2010,
            tracks=1,
            path="/z",
            collection_id=collection_id,
        )
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
    year_keys = [(book.year is None, book.year or 0) for book in window.books]
    assert year_keys == sorted(year_keys)


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

    remaining_ids = {book.book_id for book in window.books}
    assert id_middle not in remaining_ids
    assert id_alpha in remaining_ids
    current_id = _current_book_id(window)
    assert current_id in remaining_ids
    current = next(book for book in window.books if book.book_id == current_id)
    assert current.read_date


def test_update_returns_focus_to_first_selected_book(
    main_window, qapp, qtbot, monkeypatch
):
    window = main_window
    assert len(window.books) >= 2
    first_id = window.books[0].book_id
    second_id = window.books[1].book_id
    window.focus_book_by_id(second_id, 1)
    window.selected_book_ids = {first_id, second_id}
    window.update_selection_ui()
    assert _current_book_id(window) == second_id

    class _FakeUpdate:
        def __init__(self, *args, **kwargs):
            self.changes_applied = True
            self.selected_book_ids = {first_id, second_id}

        def exec(self):
            return 1

    monkeypatch.setattr("src.ui.main_window.UpdateWindow", _FakeUpdate)
    window.on_update_clicked()
    qapp.processEvents()
    qtbot.wait(20)

    assert _current_book_id(window) == first_id
    assert window.selected_book_ids == set()
    assert window.table.hasFocus()
