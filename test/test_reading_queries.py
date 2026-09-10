"""ReadingQueries coverage for Reading History stats/history methods."""

from __future__ import annotations

from datetime import date

from src.database.models import Book
from src.database.queries import AuthorQueries, BookQueries
from src.database.reading_queries import ReadingQueries


def _insert_read_book(
    db,
    *,
    title: str,
    read_date: date,
    hours: int = 5,
    minutes: int = 0,
) -> int:
    author_id = AuthorQueries(db).insert(f"RQ Author {title}")
    return BookQueries(db).insert(
        Book(
            title=title,
            author_id=author_id,
            read_date=read_date,
            time_hours=hours,
            time_minutes=minutes,
        )
    )


def test_get_reading_statistics_shape_and_counts(temp_db):
    start = date(2090, 1, 1)
    end = date(2090, 12, 31)
    _insert_read_book(temp_db, title="RQ Stats A", read_date=date(2090, 3, 10), hours=4)
    _insert_read_book(temp_db, title="RQ Stats B", read_date=date(2090, 3, 20), hours=6)
    _insert_read_book(temp_db, title="RQ Stats C", read_date=date(2090, 7, 1), hours=2)

    queries = ReadingQueries(temp_db)
    stats = queries.get_reading_statistics(start_date=start, end_date=end)

    assert stats["total_books"] == 3
    assert stats["total_hours"] == 12.0
    assert stats["avg_hours_per_book"] == 4.0
    assert stats["books_per_month"] > 0
    assert isinstance(stats["yearly_breakdown"], list)
    assert isinstance(stats["monthly_breakdown"], list)
    assert len(stats["yearly_breakdown"]) >= 1
    assert stats["yearly_breakdown"][0]["year"] == 2090
    assert stats["yearly_breakdown"][0]["book_count"] == 3

    months = {row["month_key"]: row["book_count"] for row in stats["monthly_breakdown"]}
    assert months.get("2090-03") == 2
    assert months.get("2090-07") == 1

    productive = stats["most_productive_month"]
    assert productive is not None
    assert productive["book_count"] == 2
    assert productive["year"] == 2090


def test_get_reading_history_returns_books_in_range(temp_db):
    _insert_read_book(temp_db, title="RQ Hist In", read_date=date(2091, 2, 15))
    _insert_read_book(temp_db, title="RQ Hist Out", read_date=date(2080, 1, 1))

    queries = ReadingQueries(temp_db)
    books = queries.get_reading_history(
        start_date=date(2091, 1, 1),
        end_date=date(2091, 12, 31),
        order_by="read_date DESC",
    )
    titles = {book.title for book in books}
    assert "RQ Hist In" in titles
    assert "RQ Hist Out" not in titles
    matched = next(book for book in books if book.title == "RQ Hist In")
    assert matched.read_date == date(2091, 2, 15)
    assert matched.author_name


def test_get_reading_history_respects_limit(temp_db):
    for index in range(3):
        _insert_read_book(
            temp_db,
            title=f"RQ Limit {index}",
            read_date=date(2092, 1, index + 1),
        )

    queries = ReadingQueries(temp_db)
    books = queries.get_reading_history(
        start_date=date(2092, 1, 1),
        end_date=date(2092, 12, 31),
        limit=2,
    )
    assert len(books) == 2


def test_empty_range_returns_zero_stats(temp_db):
    queries = ReadingQueries(temp_db)
    stats = queries.get_reading_statistics(
        start_date=date(1900, 1, 1),
        end_date=date(1900, 1, 31),
    )
    assert stats["total_books"] == 0
    assert stats["total_hours"] == 0.0
    assert stats["yearly_breakdown"] == []
    assert stats["monthly_breakdown"] == []
    assert stats["most_productive_month"] is None
