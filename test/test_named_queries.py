"""SeriesQueries, GenreQueries, and StatisticsQueries coverage."""

from __future__ import annotations

from datetime import date

from src.database.models import Book
from src.database.queries import (
    AuthorQueries,
    BookQueries,
    GenreQueries,
    SeriesQueries,
    StatisticsQueries,
)


class TestSeriesQueries:
    def test_insert_get_and_get_or_create(self, temp_db):
        series_q = SeriesQueries(temp_db)
        series_id = series_q.insert("NQ Series Alpha")
        found = series_q.get_by_id(series_id)
        assert found is not None
        assert found.name == "NQ Series Alpha"

        by_name = series_q.get_by_name("nq series alpha")
        assert by_name is not None
        assert by_name.series_id == series_id

        same_id = series_q.get_or_create("NQ Series Alpha")
        assert same_id == series_id

        names = {item.name for item in series_q.get_all()}
        assert "NQ Series Alpha" in names

    def test_update_and_delete_unused(self, temp_db):
        series_q = SeriesQueries(temp_db)
        series_id = series_q.insert("NQ Series Temp")
        series_q.update(series_id, "NQ Series Renamed")
        assert series_q.get_by_id(series_id).name == "NQ Series Renamed"

        series_q.delete(series_id)
        assert series_q.get_by_id(series_id) is None


class TestGenreQueries:
    def test_insert_get_and_list(self, temp_db):
        genre_q = GenreQueries(temp_db)
        genre_id = genre_q.insert("NQ Genre Mystery")
        found = genre_q.get_by_name("nq genre mystery")
        assert found is not None
        assert found.genre_id == genre_id

        assert genre_q.get_or_create("NQ Genre Mystery") == genre_id
        names = {item.name for item in genre_q.get_all()}
        assert "NQ Genre Mystery" in names

    def test_cleanup_unused_removes_orphan(self, temp_db):
        genre_q = GenreQueries(temp_db)
        genre_id = genre_q.insert("NQ Genre Orphan")
        genre_q.cleanup_unused()
        assert genre_q.get_by_id(genre_id) is None


class TestStatisticsQueries:
    def test_get_statistics_reflects_inserted_rows(self, temp_db):
        before = StatisticsQueries(temp_db).get_statistics()

        author_id = AuthorQueries(temp_db).insert("NQ Stats Author")
        series_id = SeriesQueries(temp_db).insert("NQ Stats Series")
        genre_id = GenreQueries(temp_db).insert("NQ Stats Genre")
        BookQueries(temp_db).insert(
            Book(
                title="NQ Stats Read Book",
                author_id=author_id,
                series_id=series_id,
                genre_id=genre_id,
                read_date=date(2093, 5, 1),
                time_hours=3,
                time_minutes=0,
            )
        )
        BookQueries(temp_db).insert(
            Book(
                title="NQ Stats Unread Book",
                author_id=author_id,
                time_hours=1,
                time_minutes=0,
            )
        )

        after = StatisticsQueries(temp_db).get_statistics()
        assert after.total_books == before.total_books + 2
        assert after.total_authors >= before.total_authors + 1
        assert after.total_series >= before.total_series + 1
        assert after.total_genres >= before.total_genres + 1
        assert after.books_read == before.books_read + 1
        assert after.books_unread == before.books_unread + 1
        assert after.total_hours_read >= before.total_hours_read + 3
