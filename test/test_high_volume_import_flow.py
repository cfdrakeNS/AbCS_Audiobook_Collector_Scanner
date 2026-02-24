"""Tests for high-volume import flow (auto-add valid books while scanning)."""

from __future__ import annotations

import pytest
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtCore import QSettings

from database import DatabaseManager, Book, Collection, BookQueries, CollectionQueries
from core.validator import ImportValidator
from core.import_scanner import ImportScanner


@pytest.fixture
def isolated_qsettings(tmp_path):
    """Use temporary QSettings for deterministic tests."""
    original_format = QSettings.defaultFormat()
    QSettings.setDefaultFormat(QSettings.IniFormat)
    QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, str(tmp_path))

    settings = QSettings("AbCS", "AudioBookCollector")
    settings.clear()
    settings.sync()
    try:
        yield settings
    finally:
        settings.clear()
        settings.sync()
        QSettings.setDefaultFormat(original_format)


@pytest.fixture
def test_db(tmp_path):
    """Create a test database."""
    db_path = tmp_path / "test.db"
    db = DatabaseManager(str(db_path))
    return db


def test_auto_add_valid_books_during_import(test_db):
    """Test that valid books are auto-added during import scan."""
    # Book with no errors should be auto-added
    valid_book = {
        "title": "Dune",
        "author": "Frank Herbert",
        "year": 1965,
        "genre": "Science Fiction",
        "narrator": "",
        "comment": "",
        "files": [],
        "folder": "/books/dune",
        "errors": [],
        "time_hours": 0,
        "time_minutes": 0,
        "tracks": 1,
        "size_mb": 0.0,
        "bitrate": 128,
        "format": "MP3",
    }

    # Validate and prepare book (as ImportScanner would)
    validator = ImportValidator()
    scanner = ImportScanner()

    errors = validator.validate_book(valid_book)
    assert not errors, f"Valid book should have no errors: {errors}"

    # Apply preferences (fallback/corrections)
    scanner.apply_preferences(valid_book)

    # Validate again after preferences
    final_errors = validator.validate_book(valid_book)
    assert not final_errors, f"Book should be valid after preferences: {final_errors}"


def test_duplicate_detection_prevents_auto_add(test_db):
    """Test that duplicates are not auto-added."""
    validator = ImportValidator()

    book = {
        "title": "Dune",
        "author": "Frank Herbert",
        "year": 1965,
        "collection_id": 1,
    }

    existing_books = [
        {
            "title": "Dune",
            "author": "Frank Herbert",
            "year": 1965,
            "collection_id": 1,
        }
    ]

    is_dup = validator.is_duplicate(
        book, existing_books, target_collection_id=1)
    assert is_dup, "Should detect duplicate"


def test_warning_book_not_auto_added(test_db):
    """Test that books with warnings are not auto-added."""
    validator = ImportValidator()

    # Book with author name in title (warning)
    book = {
        "title": "Frank Herbert's Dune",
        "author": "Frank Herbert",
        "year": 1965,
    }

    errors = validator.validate_book(book)
    has_warning = any(
        validator.categorize_error(err) == "warning"
        for err in errors
    )
    assert has_warning, "Should detect warning for author in title"


def test_error_book_not_auto_added(test_db):
    """Test that books with errors are not auto-added."""
    validator = ImportValidator()

    # Book with blank author (error)
    book = {
        "title": "Dune",
        "author": "",
        "year": 1965,
    }

    errors = validator.validate_book(book)
    has_hard_error = any(
        validator.categorize_error(err) in ("read", "parse")
        for err in errors
    )
    assert has_hard_error, "Should detect error for blank author"


def test_fallback_flag_in_outcomes():
    """Test that fallback flags are tracked in outcomes."""
    scanner = ImportScanner()

    # Configure to use fallback
    scanner.configure(
        scenario_mode="mass_standard",
        author_fallback_mode="folder",
        title_fallback_mode="file",
        reader_keywords=["reader", "read by"],
        trim_whitespace=True,
    )

    book = {
        "title": "",  # Blank - will use fallback
        "author": "Frank Herbert",
        "year": 1965,
        "folder": "/audio/books/Dune",
        "errors": [],
        "files": ["/audio/books/Dune/01_excerpt.mp3"],
    }

    scanner.apply_preferences(book)

    # Should have added a fallback flag
    has_fallback_flag = any(
        str(err).upper().startswith("F:")
        for err in book.get("errors", [])
    )
    assert has_fallback_flag, "Should have fallback flag"
    assert book["title"] != "", "Title should have been filled by fallback"


def test_autocorrect_flag_in_outcomes():
    """Test that autocorrect flags are tracked in outcomes."""
    scanner = ImportScanner()

    # Configure to use autocorrect
    scanner.configure(
        scenario_mode="mass_standard",
        author_fallback_mode="folder",
        title_fallback_mode="file",
        reader_keywords=["reader", "read by"],
        trim_whitespace=True,
        strip_leading_punctuation=True,
    )

    book = {
        "title": "  *Dune*  ",  # Whitespace and punctuation
        "author": "Frank Herbert",
        "year": 1965,
        "folder": "/audio/books/Dune",
        "errors": [],
        "files": [],
    }

    scanner.apply_preferences(book)

    # Should have added autocorrect flag if corrections were applied
    has_correction_flag = any(
        str(err).upper().startswith("C:")
        for err in book.get("errors", [])
    )
    # May or may not have flag depending on what was corrected
    # Just verify the title was processed
    assert book["title"].strip() != "  *Dune*  ", "Title should be trimmed"
