"""Tests for preference-driven import validation rules."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QSettings

from core.validator import ImportValidator


@pytest.fixture
def isolated_qsettings(tmp_path):
    """Use temporary INI-backed QSettings storage for deterministic tests."""
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


def test_author_in_title_rule_respects_severity_and_enabled(isolated_qsettings):
    isolated_qsettings.setValue(
        "import/rules/author_name_in_title/enabled", True)
    isolated_qsettings.setValue(
        "import/rules/author_name_in_title/severity", "warning")

    validator = ImportValidator()
    book = {"author": "Frank Herbert", "title": "Frank Herbert - Dune"}
    errors = validator.validate_book(book)
    assert "Author name in Title" in errors

    isolated_qsettings.setValue(
        "import/rules/author_name_in_title/severity", "error")
    validator.reload_settings()
    errors = validator.validate_book(book)
    assert "Author name in Title" in errors

    isolated_qsettings.setValue(
        "import/rules/author_name_in_title/enabled", False)
    validator.reload_settings()
    errors = validator.validate_book(book)
    assert not any("Author name in Title" in err for err in errors)


def test_unknown_or_various_author_rule(isolated_qsettings):
    isolated_qsettings.setValue(
        "import/rules/unknown_or_various_author/enabled", True)
    isolated_qsettings.setValue(
        "import/rules/unknown_or_various_author/severity", "warning")

    validator = ImportValidator()
    errors = validator.validate_book(
        {"author": "Various Artists", "title": "Collection"})
    assert "Author contains Unknown or Various" in errors


def test_minimum_title_length_rule_uses_configured_value(isolated_qsettings):
    isolated_qsettings.setValue(
        "import/rules/minimum_title_length/enabled", True)
    isolated_qsettings.setValue("import/rules/minimum_title_length/value", 5)
    isolated_qsettings.setValue(
        "import/rules/minimum_title_length/severity", "warning")

    validator = ImportValidator()
    errors = validator.validate_book({"author": "Author", "title": "ABC"})
    assert "Title below minimum length (5)" in errors

    errors = validator.validate_book({"author": "Author", "title": "ABCDE"})
    assert not any("Title below minimum length" in err for err in errors)


def test_duplicate_match_mode_title_author_year_collection(isolated_qsettings):
    isolated_qsettings.setValue(
        "import/rules/duplicate/match_mode", "title_author_year_collection")

    validator = ImportValidator()
    book = {"title": "Dune", "author": "Frank Herbert", "year": 1965}
    existing_books = [
        {
            "title": "Dune",
            "author": "Frank Herbert",
            "year": 1965,
            "collection_id": 2,
        }
    ]

    assert not validator.is_duplicate(
        book, existing_books, target_collection_id=1)
    assert validator.is_duplicate(
        book, existing_books, target_collection_id=2)


def test_duplicate_match_mode_title_author_year_ignore_collection(isolated_qsettings):
    isolated_qsettings.setValue(
        "import/rules/duplicate/match_mode", "title_author_year_ignore_collection")

    validator = ImportValidator()
    book = {"title": "Dune", "author": "Frank Herbert", "year": 1965}
    existing_books = [
        {
            "title": "Dune",
            "author": "Frank Herbert",
            "year": 1965,
            "collection_id": 2,
        }
    ]

    assert validator.is_duplicate(
        book, existing_books, target_collection_id=1)


def test_duplicate_fuzzy_threshold_disabled_requires_exact_match(isolated_qsettings):
    isolated_qsettings.setValue(
        "import/rules/duplicate/match_mode", "title_author_year_ignore_collection")
    isolated_qsettings.setValue(
        "import/rules/duplicate/fuzzy_threshold", 0)

    validator = ImportValidator()
    book = {"title": "Dune", "author": "Frank Herbert", "year": 1965}
    existing_books = [
        {
            "title": "Dunne",
            "author": "Frank Herbertt",
            "year": 1965,
            "collection_id": 2,
        }
    ]

    assert not validator.is_duplicate(
        book, existing_books, target_collection_id=1)


def test_duplicate_fuzzy_threshold_enabled_matches_similar_values(isolated_qsettings):
    isolated_qsettings.setValue(
        "import/rules/duplicate/match_mode", "title_author_year_ignore_collection")
    isolated_qsettings.setValue(
        "import/rules/duplicate/fuzzy_threshold", 85)

    validator = ImportValidator()
    book = {"title": "Dune", "author": "Frank Herbert", "year": 1965}
    existing_books = [
        {
            "title": "Dunne",
            "author": "Frank Herbertt",
            "year": 1965,
            "collection_id": 2,
        }
    ]

    assert validator.is_duplicate(
        book, existing_books, target_collection_id=1)


def test_file_structure_rule_author_title_warning(isolated_qsettings):
    isolated_qsettings.setValue("import/rules/file_structure/enabled", True)
    isolated_qsettings.setValue(
        "import/rules/file_structure/severity", "warning")
    isolated_qsettings.setValue(
        "import/rules/file_structure/pattern", "author_title")

    validator = ImportValidator()
    errors = validator.validate_book(
        {
            "author": "Frank Herbert",
            "title": "Dune",
            "folder": "Books",
        }
    )
    assert any(
        "Folder path does not match expected structure (Author/Title)" == err
        for err in errors
    )


def test_file_structure_rule_year_author_title(isolated_qsettings):
    isolated_qsettings.setValue("import/rules/file_structure/enabled", True)
    isolated_qsettings.setValue(
        "import/rules/file_structure/severity", "error")
    isolated_qsettings.setValue(
        "import/rules/file_structure/pattern", "year_author_title")

    validator = ImportValidator()
    valid_errors = validator.validate_book(
        {
            "author": "Frank Herbert",
            "title": "Dune",
            "folder": "Library/1965/Frank Herbert/Dune",
        }
    )
    assert not any(
        "Folder path does not match expected structure" in err for err in valid_errors)

    invalid_errors = validator.validate_book(
        {
            "author": "Frank Herbert",
            "title": "Dune",
            "folder": "Library/Frank Herbert/Dune",
        }
    )
    assert any(
        "Folder path does not match expected structure (Year/Author/Title)" == err
        for err in invalid_errors
    )


def test_duplicate_match_mode_title_author_with_collection(isolated_qsettings):
    isolated_qsettings.setValue(
        "import/rules/duplicate/match_mode", "title_author")

    validator = ImportValidator()
    book = {"title": "Dune", "author": "Frank Herbert", "year": 1965}
    existing_books = [
        {
            "title": "Dune",
            "author": "Frank Herbert",
            "year": 1980,
            "collection_id": 2,
        }
    ]

    assert not validator.is_duplicate(
        book, existing_books, target_collection_id=1)
    assert validator.is_duplicate(
        book, existing_books, target_collection_id=2)


def test_duplicate_match_mode_title_author_year(isolated_qsettings):
    isolated_qsettings.setValue(
        "import/rules/duplicate/match_mode", "title_author_year")

    validator = ImportValidator()
    book = {"title": "Dune", "author": "Frank Herbert", "year": 1965}
    existing_books = [
        {
            "title": "Dune",
            "author": "Frank Herbert",
            "year": 1965,
            "collection_id": 2,
        }
    ]

    assert validator.is_duplicate(
        book, existing_books, target_collection_id=1)


def test_duplicate_match_mode_title_author_year_ignore_collection(isolated_qsettings):
    isolated_qsettings.setValue(
        "import/rules/duplicate/match_mode", "title_author_year_ignore_collection")

    validator = ImportValidator()
    book = {"title": "Dune", "author": "Frank Herbert", "year": 1965}
    existing_books = [
        {
            "title": "Dune",
            "author": "Frank Herbert",
            "year": 1965,
            "collection_id": 2,
        }
    ]

    assert validator.is_duplicate(
        book, existing_books, target_collection_id=1)
