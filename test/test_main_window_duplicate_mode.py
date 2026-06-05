"""Tests for main-window duplicate matching keys."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

import pytest

from src.accessibility.scaling import UIScaler
from src.accessibility.theme_manager import ThemeManager
from src.database.connection import DatabaseManager
from src.database.models import Book, SearchFilter
from src.ui.main_window import MainWindow

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def temp_db(tmp_path):
    data_dir = Path(PROJECT_ROOT) / "data"
    candidates = [data_dir / "abcs.db", data_dir / "wh abcs.db"]
    source_db = next((path for path in candidates if path.exists()), None)
    if source_db is None:
        pytest.skip("No test database available")
    target_db = tmp_path / "abcs_test.db"
    source_conn = sqlite3.connect(str(source_db))
    target_conn = sqlite3.connect(str(target_db))
    source_conn.backup(target_conn)
    source_conn.close()
    target_conn.close()
    db = DatabaseManager(str(target_db))
    try:
        yield db
    finally:
        db.close()


def test_title_author_collection_mode_scopes_by_collection(qapp, temp_db):
    """Title + Author + Collection should not flag cross-collection matches."""
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = MainWindow(temp_db, scaler, theme_manager)

    books = [
        Book(book_id=1, title="Shared Title", author_id=10, collection_id=1),
        Book(book_id=2, title="Shared Title", author_id=10, collection_id=2),
    ]
    assert window._collect_duplicate_book_ids(books, "title_author") == set()

    same_collection = [
        Book(book_id=3, title="Shared Title", author_id=10, collection_id=1),
        Book(book_id=4, title="Shared Title", author_id=10, collection_id=1),
    ]
    assert window._collect_duplicate_book_ids(same_collection, "title_author") == {3, 4}

    window.close()


def test_title_author_only_mode_ignores_year_and_collection(qapp, temp_db):
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = MainWindow(temp_db, scaler, theme_manager)

    books = [
        Book(book_id=1, title="Shared Title", author_id=10, year=2020, collection_id=1),
        Book(book_id=2, title="Shared Title", author_id=10, year=2021, collection_id=2),
    ]
    assert window._collect_duplicate_book_ids(books, "title_author_only") == {1, 2}

    window.close()


def test_title_author_year_mode_ignores_collection(qapp, temp_db):
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = MainWindow(temp_db, scaler, theme_manager)

    books = [
        Book(book_id=1, title="Shared Title", author_id=10, year=2020, collection_id=1),
        Book(book_id=2, title="Shared Title", author_id=10, year=2020, collection_id=2),
    ]
    assert window._collect_duplicate_book_ids(books, "title_author_year") == {1, 2}

    window.close()


class _FakeCollectionCombo:
    def count(self):
        return 0


class _StubImportDialog:
    total_imported = 0

    def __init__(self, *args, **kwargs):
        self.collection_combo = _FakeCollectionCombo()

    def exec(self):
        return 0


def test_import_exits_duplicate_mode_before_opening(qapp, temp_db, monkeypatch):
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = MainWindow(temp_db, scaler, theme_manager)

    window.duplicate_mode_active = True
    window.duplicate_mode_match_mode = "title_author"
    window.duplicate_mode_book_ids = {1, 2}
    window._duplicate_saved_filter = SearchFilter(order_by="Title")

    monkeypatch.setattr(
        "src.ui.main_window.ImportWindow",
        lambda *args, **kwargs: _StubImportDialog(),
    )

    window.on_import()

    assert window.duplicate_mode_active is False
    assert window.duplicate_mode_book_ids == set()
    window.close()


def test_book_list_import_exits_duplicate_mode_before_opening(
    qapp, temp_db, monkeypatch
):
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = MainWindow(temp_db, scaler, theme_manager)

    window.duplicate_mode_active = True
    window.duplicate_mode_match_mode = "title_author"
    window.duplicate_mode_book_ids = {1, 2}
    window._duplicate_saved_filter = SearchFilter(order_by="Title")

    monkeypatch.setattr(
        "src.ui.book_list_import_window.BookListImportWindow",
        lambda *args, **kwargs: _StubImportDialog(),
    )

    window.on_book_list_import()

    assert window.duplicate_mode_active is False
    assert window.duplicate_mode_book_ids == set()
    window.close()
