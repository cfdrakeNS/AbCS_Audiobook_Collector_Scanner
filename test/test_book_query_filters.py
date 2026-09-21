"""Pure DB / model filter tests (plot, date-added, title accessible text)."""

from __future__ import annotations

from datetime import date, datetime

import pytest
from PySide6.QtCore import Qt

from src.database.connection import DatabaseManager
from src.database.models import Book, SearchFilter, book_has_plot, PLOT_MIN_LENGTH
from src.database.queries import AuthorQueries, BookQueries
from src.ui.main_window import BookTableModel


def _insert_book(db: DatabaseManager, title: str, comments: str = "") -> int:
    author_id = AuthorQueries(db).insert(f"Plot Author {title}")
    return BookQueries(db).insert(
        Book(title=title, author_id=author_id, comments=comments)
    )


def _insert_book_with_date(db, title: str, date_added: datetime) -> int:
    author_id = AuthorQueries(db).insert(f"DateAdded Author {title}")
    return BookQueries(db).insert(
        Book(title=title, author_id=author_id, date_added=date_added)
    )


def test_title_accessible_text_includes_plot_suffix():
    model = BookTableModel(
        [
            Book(title="With Plot", comments="p" * PLOT_MIN_LENGTH),
            Book(title="No Plot", comments="Reader: Bob"),
        ]
    )

    with_plot = model.data(model.index(0, 1), Qt.DisplayRole)
    without_plot = model.data(model.index(1, 1), Qt.DisplayRole)
    with_plot_sr = model.data(model.index(0, 1), Qt.AccessibleTextRole)
    without_plot_sr = model.data(model.index(1, 1), Qt.AccessibleTextRole)

    assert with_plot == "With Plot"
    assert without_plot == "No Plot"
    assert with_plot_sr == "With Plot, plot"
    assert without_plot_sr == "No Plot"


def test_title_accessible_text_includes_selection_suffix():
    model = BookTableModel(
        [
            Book(book_id=1, title="First", comments="p" * PLOT_MIN_LENGTH),
            Book(book_id=2, title="Second"),
        ]
    )
    model.set_selection_book_ids({1, 2})

    first_sr = model.data(model.index(0, 1), Qt.AccessibleTextRole)
    second_sr = model.data(model.index(1, 1), Qt.AccessibleTextRole)
    second_display = model.data(model.index(1, 1), Qt.DisplayRole)

    assert first_sr == "First, plot - 2 selected. Escape to cancel selection"
    assert second_sr == "Second - 2 selected. Escape to cancel selection"
    assert second_display == "Second"

    model.set_selection_book_ids({2})
    assert (
        model.data(model.index(1, 1), Qt.AccessibleTextRole)
        == "Second - selected. Escape to cancel selection"
    )
    assert model.data(model.index(0, 1), Qt.AccessibleTextRole) == "First, plot"


def test_book_has_plot_requires_minimum_length():
    short = "Reader: Jane Doe"
    long_plot = "x" * PLOT_MIN_LENGTH

    assert not book_has_plot("")
    assert not book_has_plot(short)
    assert book_has_plot(long_plot)
    assert book_has_plot(f"  {long_plot}  ")


@pytest.mark.parametrize(
    "plot_filter, expected_titles",
    [
        ("With Plot", {"PlotTest Has Plot"}),
        ("Without Plot", {"PlotTest Short Only", "PlotTest No Plot"}),
    ],
)
def test_plot_filter(temp_db, plot_filter, expected_titles):
    book_queries = BookQueries(temp_db)
    test_titles = {"PlotTest Has Plot", "PlotTest Short Only", "PlotTest No Plot"}
    _insert_book(temp_db, "PlotTest Has Plot", "p" * PLOT_MIN_LENGTH)
    _insert_book(temp_db, "PlotTest Short Only", "Reader: Bob")
    _insert_book(temp_db, "PlotTest No Plot", "")

    books = book_queries.get_all(SearchFilter(plot_filter=plot_filter))
    titles = {book.title for book in books if book.title in test_titles}

    assert titles == expected_titles


def test_date_added_filter_returns_books_on_or_after_cutoff(temp_db):
    book_queries = BookQueries(temp_db)
    test_titles = {"DateAdded Old Book", "DateAdded New Book", "DateAdded Same Day"}
    _insert_book_with_date(temp_db, "DateAdded Old Book", datetime(2024, 1, 15, 10, 0, 0))
    _insert_book_with_date(temp_db, "DateAdded New Book", datetime(2025, 12, 1, 10, 0, 0))
    _insert_book_with_date(
        temp_db, "DateAdded Same Day", datetime(2025, 6, 1, 8, 30, 0)
    )

    books = book_queries.get_all(SearchFilter(date_added_since=date(2025, 6, 1)))
    titles = {book.title for book in books if book.title in test_titles}

    assert titles == {"DateAdded New Book", "DateAdded Same Day"}


def test_date_added_filter_inactive_when_not_set(temp_db):
    book_queries = BookQueries(temp_db)
    title = "DateAdded Unfiltered Book"
    _insert_book_with_date(temp_db, title, datetime(2020, 1, 1, 0, 0, 0))

    books = book_queries.get_all(SearchFilter())
    titles = {book.title for book in books if book.title == title}

    assert titles == {title}
