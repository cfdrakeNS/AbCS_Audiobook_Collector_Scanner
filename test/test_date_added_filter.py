"""Tests for recently-added (date_added_since) filter behaviour."""

from datetime import date, datetime

from src.database.models import Book, SearchFilter
from src.database.queries import AuthorQueries, BookQueries


def _insert_book_with_date(db, title: str, date_added: datetime) -> int:
    author_id = AuthorQueries(db).insert(f"DateAdded Author {title}")
    return BookQueries(db).insert(
        Book(title=title, author_id=author_id, date_added=date_added)
    )


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
