"""Batch write APIs and book-list import DB integration tests."""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock

import pytest

pd = pytest.importorskip("pandas")

from src.database.models import Book, SearchFilter
from src.database.queries import (
    AuthorQueries,
    BookQueries,
    CollectionQueries,
    GenreQueries,
    SeriesQueries,
)
from src.ui.book_list_import_window import BookListImportWindow


@pytest.fixture
def empty_temp_db(tmp_path):
    """Fresh empty database (not a copy of the large local library)."""
    from src.database.connection import DatabaseManager

    db = DatabaseManager(str(tmp_path / "book_list_batch.db"))
    db.initialize_database()
    try:
        yield db
    finally:
        db.close()


class TestBookBatchWrites:
    def test_insert_many_inserts_all_rows(self, empty_temp_db):
        authors = AuthorQueries(empty_temp_db)
        books = BookQueries(empty_temp_db)
        author_id = authors.insert("Batch Author")

        count = books.insert_many(
            [
                Book(title="Batch One", author_id=author_id, year=2001),
                Book(title="Batch Two", author_id=author_id, year=2002),
                Book(title="Batch Three", author_id=author_id, year=2003),
            ],
            commit=True,
        )
        assert count == 3
        rows = empty_temp_db.fetch_all(
            "SELECT title FROM books WHERE author_id = ? ORDER BY year",
            (author_id,),
        )
        assert [r[0] for r in rows] == ["Batch One", "Batch Two", "Batch Three"]

    def test_insert_many_empty_is_noop(self, empty_temp_db):
        books = BookQueries(empty_temp_db)
        assert books.insert_many([], commit=True) == 0

    def test_update_many_sets_read_dates(self, empty_temp_db):
        authors = AuthorQueries(empty_temp_db)
        books = BookQueries(empty_temp_db)
        author_id = authors.insert("Update Author")
        id1 = books.insert(Book(title="Update One", author_id=author_id))
        id2 = books.insert(Book(title="Update Two", author_id=author_id))

        updated = books.update_many(
            [
                (id1, date(2024, 1, 15)),
                (id2, date(2024, 2, 20)),
            ],
            commit=True,
        )
        assert updated == 2
        b1 = books.get_by_id(id1)
        b2 = books.get_by_id(id2)
        assert b1.read_date == date(2024, 1, 15)
        assert b2.read_date == date(2024, 2, 20)

    def test_author_ensure_names_creates_missing(self, empty_temp_db):
        authors = AuthorQueries(empty_temp_db)
        authors.insert("Existing Author")
        cache = authors.ensure_names(
            ["Existing Author", "New Author A", "New Author B", "new author a"],
            commit=True,
        )
        assert "existing author" in cache
        assert "new author a" in cache
        assert "new author b" in cache
        # Case-variant of already-ensured name should map to same id
        assert cache["new author a"] == authors.get_by_name("New Author A").author_id


def _set_mapping(window: BookListImportWindow, mapping: dict[str, int | None]) -> None:
    """Set field mapping combos: column index 0 → combo index 1 (after None)."""
    for field, col_index in mapping.items():
        combo = window.field_mappings[field]
        if col_index is None:
            combo.setCurrentIndex(0)
        else:
            # Ensure enough column letters exist
            while combo.count() <= col_index + 1:
                letter = window._excel_column_label(combo.count() - 1)
                combo.addItem(letter)
            combo.setCurrentIndex(col_index + 1)


def _prepare_window(window: BookListImportWindow, frame, mapping: dict) -> int:
    """Load DataFrame, map fields, select first collection; return collection_id."""
    window.file_data = frame
    window.column_count = len(frame.columns)
    window.update_column_combos()
    _set_mapping(window, mapping)
    if window.collection_combo.count() == 0:
        pytest.fail("No collections available for book list import test")
    window.collection_combo.setCurrentIndex(0)
    return window.collection_combo.currentData()


class TestBookListImportDb:
    def test_import_new_books_batches_insert_and_single_commit(
        self, empty_temp_db, ui_scaler, theme_manager, qtbot, monkeypatch
    ):
        window = BookListImportWindow(empty_temp_db, ui_scaler, theme_manager)
        qtbot.addWidget(window)

        frame = pd.DataFrame(
            {
                "Title": [f"BL Book {i}" for i in range(5)],
                "Author": ["BL Author"] * 5,
                "Year": [2000 + i for i in range(5)],
            }
        )
        collection_id = _prepare_window(
            window,
            frame,
            {"title": 0, "author": 1, "year": 2},
        )

        insert_many = MagicMock(wraps=window.book_queries.insert_many)
        monkeypatch.setattr(window.book_queries, "insert_many", insert_many)

        success, errors, duplicates, skipped = window.import_new_books()

        assert (success, errors, duplicates, skipped) == (5, 0, 0, 0)
        assert insert_many.call_count == 1
        assert insert_many.call_args.kwargs.get("commit") is False
        rows = empty_temp_db.fetch_all(
            "SELECT COUNT(*) FROM books WHERE collection_id = ?",
            (collection_id,),
        )
        assert rows[0][0] == 5

        # Second pass: all duplicates, no additional inserts
        insert_many.reset_mock()
        success2, errors2, duplicates2, skipped2 = window.import_new_books()
        assert success2 == 0
        assert duplicates2 == 5
        assert insert_many.call_count == 0

    def test_update_read_dates_batches_and_single_commit(
        self, empty_temp_db, ui_scaler, theme_manager, qtbot, monkeypatch
    ):
        authors = AuthorQueries(empty_temp_db)
        books = BookQueries(empty_temp_db)
        collections = CollectionQueries(empty_temp_db)
        collection_id = collections.get_all()[0].collection_id
        author_id = authors.insert("RD Author")
        book_id = books.insert(
            Book(
                title="RD Title",
                author_id=author_id,
                collection_id=collection_id,
            )
        )

        window = BookListImportWindow(empty_temp_db, ui_scaler, theme_manager)
        qtbot.addWidget(window)
        window.import_mode = "read_date"

        frame = pd.DataFrame(
            {
                "Title": ["RD Title"],
                "Author": ["RD Author"],
                "ReadDate": ["2024-06-15"],
            }
        )
        _prepare_window(
            window,
            frame,
            {"title": 0, "author": 1, "read_date": 2},
        )
        # Select the same collection we seeded
        for i in range(window.collection_combo.count()):
            if window.collection_combo.itemData(i) == collection_id:
                window.collection_combo.setCurrentIndex(i)
                break

        update_many = MagicMock(wraps=window.book_queries.update_many)
        monkeypatch.setattr(window.book_queries, "update_many", update_many)

        success, errors, duplicates, skipped = window.update_read_dates()

        assert (success, errors, duplicates, skipped) == (1, 0, 0, 0)
        assert update_many.call_count == 1
        assert update_many.call_args.kwargs.get("commit") is False
        updated = books.get_by_id(book_id)
        assert updated.read_date == date(2024, 6, 15)

    def test_import_stores_series_number_without_title_suffix(
        self, empty_temp_db, ui_scaler, theme_manager, qtbot
    ):
        window = BookListImportWindow(empty_temp_db, ui_scaler, theme_manager)
        qtbot.addWidget(window)
        frame = pd.DataFrame(
            {
                "Title": ["Rules of Prey"],
                "Author": ["John Sandford"],
                "Series": ["Lucas Davenport"],
                "SeriesNo": ["3"],
            }
        )
        _prepare_window(
            window,
            frame,
            {"title": 0, "author": 1, "series": 2, "series_no": 3},
        )

        success, errors, duplicates, skipped = window.import_new_books()
        assert (success, errors, duplicates, skipped) == (1, 0, 0, 0)
        saved = BookQueries(empty_temp_db).get_all(SearchFilter())
        match = [book for book in saved if book.series_number == 3]
        assert len(match) == 1
        assert match[0].title == "Rules Of Prey"
        assert match[0].series_name == "Lucas Davenport"
