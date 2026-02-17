"""Regression tests for book ordering behavior in main list queries."""

from __future__ import annotations

import os
import shutil
from datetime import datetime

from database.connection import DatabaseManager
from database.models import Book, Collection, SearchFilter
from database.queries import AuthorQueries, BookQueries, CollectionQueries


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _temp_db(tmp_path):
    source_db = os.path.join(PROJECT_ROOT, "data", "abcs.db")
    target_db = tmp_path / "abcs_test.db"
    shutil.copy2(source_db, target_db)

    db = DatabaseManager(str(target_db))
    return db


def test_order_by_series_includes_books_without_series(tmp_path):
    db = _temp_db(tmp_path)
    try:
        book_queries = BookQueries(db)
        author_queries = AuthorQueries(db)
        collection_queries = CollectionQueries(db)

        active_collections = collection_queries.get_all(active_only=True)
        if not active_collections:
            collection_id = collection_queries.insert(
                Collection(name="Default", active=True)
            )
        else:
            collection_id = active_collections[0].collection_id

        author_id = author_queries.get_or_create("Ordering Regression Author")
        title = "Ordering Regression Book"

        inserted_book = Book(
            title=title,
            author_id=author_id,
            collection_id=collection_id,
            series_id=None,
            genre_id=None,
            date_added=datetime.now(),
            source="test",
        )
        inserted_id = book_queries.insert(inserted_book)

        filter_criteria = SearchFilter(order_by="Series")
        books = book_queries.get_all(filter_criteria)

        assert any(b.book_id == inserted_id for b in books), (
            "Books with no series must still appear when sorting by Series"
        )
    finally:
        db.close()
