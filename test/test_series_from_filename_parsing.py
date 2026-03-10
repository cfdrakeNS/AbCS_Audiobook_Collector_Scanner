"""Tests for Scenario 3 series parsing from filename text."""

from src.core.import_scanner import ImportScanner


def _apply_scenario_3(file_name: str, title: str):
    scanner = ImportScanner()
    scanner.configure(
        scenario_mode="series_from_filename",
        author_fallback_mode=None,
        title_fallback_mode=None,
    )

    book = {
        "title": title,
        "author": "Test Author",
        "series": "",
        "folder": r"C:\\Library\\Author",
        "files": [rf"C:\\Library\\Author\\{file_name}"],
        "errors": [],
    }

    scanner.apply_preferences(book)
    return book


def test_series_filename_parses_name_and_number():
    book = _apply_scenario_3("Book Title (Series Name 04).mp3", "Book Title")

    assert book["series"] == "Series Name"
    assert book["title"] == "Book Title - 04"


def test_series_filename_parses_single_digit_number():
    book = _apply_scenario_3("Book (Trilogy 1).mp3", "Book")

    assert book["series"] == "Trilogy"
    assert book["title"] == "Book - 1"


def test_series_filename_parses_name_without_number():
    book = _apply_scenario_3("Title (No Number Here).mp3", "Title")

    assert book["series"] == "No Number Here"
    assert book["title"] == "Title"


def test_series_filename_without_parentheses_is_unchanged():
    book = _apply_scenario_3("Title.mp3", "Title")

    assert book["series"] == ""
    assert book["title"] == "Title"


def test_series_filename_uses_first_parenthesized_block_only():
    book = _apply_scenario_3("Title (First) (Second).mp3", "Title")

    assert book["series"] == "First"
    assert book["title"] == "Title"
