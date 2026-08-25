"""Tests for import scanner fallback behavior (Scenario 2 focus)."""

from src.core.import_scanner import ImportScanner


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


def _apply_nested_scenario(book: dict, *, title_fallback_mode: str | None = None):
    scanner = ImportScanner()
    scanner.configure(
        scenario_mode="series_from_directory_nested",
        author_fallback_mode=None,
        title_fallback_mode=title_fallback_mode,
    )
    scanner.apply_preferences(book)
    return book


def test_nested_series_sets_series_and_title_from_book_folder():
    book = {
        "title": "unknown",
        "author": "John Sandford",
        "series": "",
        "folder": (
            r"F:\Audio Books\John Sandford\Lucas Deavenport Series\1- Rules of Prey"
        ),
        "files": [
            r"F:\Audio Books\John Sandford\Lucas Deavenport Series\1- Rules of Prey\01 Rules of Prey.mp3"
        ],
        "errors": [],
    }

    updated = _apply_nested_scenario(book, title_fallback_mode="file")

    assert updated["series"] == "Lucas Deavenport Series"
    assert updated["title"] == "Rules of Prey"
    assert any(
        "F: Title fallback from folder used" in str(err) for err in updated["errors"]
    )


def test_nested_standalone_book_has_no_series():
    book = {
        "title": "Dead Watch",
        "author": "John Sandford",
        "series": "",
        "folder": r"F:\Audio Books\John Sandford\Dead Watch",
        "files": [r"F:\Audio Books\John Sandford\Dead Watch\01 Dead Watch.mp3"],
        "errors": [],
    }

    updated = _apply_nested_scenario(book)

    assert updated["series"] == ""
    assert not any(
        "Series from directory skipped" in str(err) for err in updated["errors"]
    )


def test_nested_cd_subfolder_uses_series_and_book_folder_for_title():
    book = {
        "title": "unknown",
        "author": "John Sandford",
        "series": "",
        "folder": (
            r"F:\Audio Books\John Sandford\Kidd And LuEllen Book"
            r"\04 - The Hanged Man's Song\CD-01"
        ),
        "files": [
            r"F:\Audio Books\John Sandford\Kidd And LuEllen Book"
            r"\04 - The Hanged Man's Song\CD-01\01 The Hanged Man's Song.m4b"
        ],
        "errors": [],
    }

    updated = _apply_nested_scenario(book, title_fallback_mode="file")

    assert updated["series"] == "Kidd And LuEllen Book"
    assert updated["title"] == "The Hanged Man's Song"
    assert any(
        "F: Title fallback from folder used" in str(err) for err in updated["errors"]
    )


def test_nested_ambiguous_path_skips_series_with_warning():
    book = {
        "title": "Rules of Prey",
        "author": "John Sandford",
        "series": "",
        "folder": (
            r"F:\Audio Books\Other Author\Lucas Deavenport Series\1- Rules of Prey"
        ),
        "files": [
            r"F:\Audio Books\Other Author\Lucas Deavenport Series\1- Rules of Prey\01 Rules of Prey.mp3"
        ],
        "errors": [],
    }

    updated = _apply_nested_scenario(book)

    assert updated["series"] == ""
    assert any(
        "W: Series from directory skipped (author not found in path)" in str(err)
        for err in updated["errors"]
    )


def test_nested_author_fallback_from_path_depth():
    book = {
        "title": "Dead Watch",
        "author": "unknown",
        "series": "",
        "folder": r"F:\Audio Books\John Sandford\Dead Watch",
        "files": [r"F:\Audio Books\John Sandford\Dead Watch\01 Dead Watch.mp3"],
        "errors": [],
    }

    scanner = ImportScanner()
    scanner.configure(
        scenario_mode="series_from_directory_nested",
        author_fallback_mode="folder",
        title_fallback_mode=None,
    )
    scanner.apply_preferences(book)

    assert book["author"] == "John Sandford"
    assert any(
        "F: Author fallback from folder used" in str(err) for err in book["errors"]
    )


def test_trim_whitespace_flags_correction_by_default():
    scanner = ImportScanner()
    scanner.configure(
        scenario_mode="mass_standard",
        trim_whitespace=True,
        trim_whitespace_skip_review=False,
    )
    book = {
        "title": "  Spaced Title  ",
        "author": "Author One",
        "errors": [],
    }

    scanner.apply_preferences(book)

    assert book["title"] == "Spaced Title"
    assert any("C: Title whitespace trimmed" in str(err) for err in book["errors"])


def test_trim_whitespace_skip_review_suppresses_correction_flag():
    scanner = ImportScanner()
    scanner.configure(
        scenario_mode="mass_standard",
        trim_whitespace=True,
        trim_whitespace_skip_review=True,
    )
    book = {
        "title": "  Spaced Title  ",
        "author": "Author One",
        "errors": [],
    }

    scanner.apply_preferences(book)

    assert book["title"] == "Spaced Title"
    assert not any(str(err).startswith("C:") for err in book["errors"])


def test_proper_case_skip_review_suppresses_correction_flag():
    scanner = ImportScanner()
    scanner.configure(
        scenario_mode="mass_standard",
        proper_case_fields=True,
        proper_case_skip_review=True,
    )
    book = {
        "title": "the hobbit",
        "author": "j.r.r. tolkien",
        "errors": [],
    }

    scanner.apply_preferences(book)

    assert book["title"] == "The Hobbit"
    assert not any(str(err).startswith("C:") for err in book["errors"])


def test_author_equals_title_skipped_when_author_fallback_disabled():
    book = {
        "title": "Dead Watch",
        "author": "Dead Watch",
        "series": "",
        "folder": r"F:\Audio Books\John Sandford\Dead Watch",
        "files": [r"F:\Audio Books\John Sandford\Dead Watch\01 Dead Watch.mp3"],
        "errors": [],
    }

    scanner = ImportScanner()
    scanner.configure(
        scenario_mode="mass_standard",
        author_fallback_mode=None,
        title_fallback_mode=None,
    )
    scanner.apply_preferences(book)

    assert book["author"] == "Dead Watch"
    assert not any(str(err).startswith("F:") for err in book["errors"])


def test_nested_title_from_folder_skipped_when_title_fallback_disabled():
    book = {
        "title": "unknown",
        "author": "John Sandford",
        "series": "",
        "folder": (
            r"F:\Audio Books\John Sandford\Lucas Deavenport Series\1- Rules of Prey"
        ),
        "files": [
            r"F:\Audio Books\John Sandford\Lucas Deavenport Series\1- Rules of Prey\01 Rules of Prey.mp3"
        ],
        "errors": [],
    }

    updated = _apply_nested_scenario(book, title_fallback_mode=None)

    assert updated["series"] == "Lucas Deavenport Series"
    assert updated["title"] == "unknown"
    assert not any(str(err).startswith("F:") for err in updated["errors"])
