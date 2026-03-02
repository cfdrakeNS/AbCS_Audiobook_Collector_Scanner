"""Tests for import scanner fallback behavior (Scenario 2 focus)."""

from core.import_scanner import ImportScanner


def _apply_scenario_2(book: dict, *, title_fallback_mode: str | None = None):
    scanner = ImportScanner()
    scanner.configure(
        scenario_mode="series_from_directory",
        author_fallback_mode=None,
        title_fallback_mode=title_fallback_mode,
    )
    scanner.apply_preferences(book)
    return book


def test_series_from_directory_expected_depth_sets_series():
    book = {
        "title": "Book One",
        "author": "Test Author",
        "series": "",
        "folder": r"C:\Library\Test Author\Great Series",
        "files": [r"C:\Library\Test Author\Great Series\01 - Book One.mp3"],
        "errors": [],
    }

    updated = _apply_scenario_2(book)

    assert updated["series"] == "Great Series"
    assert not any("Series from directory skipped" in str(err)
                   for err in updated["errors"])


def test_series_from_directory_ambiguous_path_skips_series_with_warning():
    book = {
        "title": "Book One",
        "author": "Test Author",
        "series": "",
        "folder": r"C:\Library\Other Author\Great Series",
        "files": [r"C:\Library\Other Author\Great Series\01 - Book One.mp3"],
        "errors": [],
    }

    updated = _apply_scenario_2(book)

    assert updated["series"] == ""
    assert any(
        "W: Series from directory skipped (folder does not match author/series pattern)" in str(
            err)
        for err in updated["errors"]
    )


def test_series_from_directory_keeps_title_fallback_behavior():
    book = {
        "title": "unknown",
        "author": "Test Author",
        "series": "",
        "folder": r"C:\Library\Test Author\Great Series",
        "files": [r"C:\Library\Test Author\Great Series\03 My Book.mp3"],
        "errors": [],
    }

    updated = _apply_scenario_2(book, title_fallback_mode="file")

    assert updated["title"] == "My Book"
    assert updated["series"] == "Great Series"
    assert any("F: Title fallback from file used" in str(err)
               for err in updated["errors"])
