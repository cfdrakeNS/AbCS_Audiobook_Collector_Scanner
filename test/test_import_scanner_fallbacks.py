"""Tests for import scanner fallback behavior on missing/placeholder metadata."""

from core.import_scanner import ImportScanner


def test_author_fallback_uses_parent_when_folder_is_no_author():
    scanner = ImportScanner()
    scanner.configure(
        scenario_mode="mass_standard",
        author_fallback_mode="folder",
        title_fallback_mode="folder",
        reader_keywords=["reader"],
    )

    book = {
        "title": "A Real Book Title",
        "author": "",
        "folder": r"E:\\test books\\Abert Thornhill\\No author",
        "files": [r"E:\\test books\\Abert Thornhill\\No author\\track01.mp3"],
    }

    scanner.apply_preferences(book)

    assert book["author"] == "Abert Thornhill"
    assert "F: Author fallback from folder used" in book.get("errors", [])


def test_title_fallback_uses_folder_when_album_is_placeholder():
    scanner = ImportScanner()
    scanner.configure(
        scenario_mode="mass_standard",
        author_fallback_mode="folder",
        title_fallback_mode="folder",
        reader_keywords=["reader"],
    )

    book = {
        "title": "Unknown Album",
        "author": "Michael R. Stern",
        "folder": r"E:\\test books\\Michael R. Stern\\Quantum Touch",
        "files": [r"E:\\test books\\Michael R. Stern\\Quantum Touch\\Storm Portal (Quantum Touch 1).mp3"],
    }

    scanner.apply_preferences(book)

    assert book["title"] == "Quantum Touch"
    assert "F: Title fallback from folder used" in book.get("errors", [])


def test_autocorrect_adds_c_flag_when_value_is_changed():
    scanner = ImportScanner()
    scanner.configure(
        scenario_mode="mass_standard",
        author_fallback_mode="folder",
        title_fallback_mode="folder",
        reader_keywords=["reader"],
        trim_whitespace=True,
        proper_case_fields=True,
    )

    book = {
        "title": "  the   long   road  ",
        "author": "  jane   DOE  ",
        "folder": r"E:\\test books\\jane DOE\\the long road",
        "files": [r"E:\\test books\\jane DOE\\the long road\\track01.mp3"],
    }

    scanner.apply_preferences(book)

    c_flags = [err for err in book.get(
        "errors", []) if str(err).startswith("C:")]
    # Should have specific correction messages
    assert len(c_flags) >= 1
    # Check for Title and Author corrections with specific details
    title_flags = [f for f in c_flags if "Title" in f]
    author_flags = [f for f in c_flags if "Author" in f]
    assert len(title_flags) > 0
    assert len(author_flags) > 0
    # Verify they mention specific corrections
    assert any("trimmed" in f or "proper case" in f for f in c_flags)


def test_fallback_messages_match_specified_format():
    """Verify exact F: message formats as documented in enhancement spec."""
    scanner = ImportScanner()

    # Test F: Title fallback from file used
    scanner.configure(
        scenario_mode="mass_standard",
        author_fallback_mode="folder",
        title_fallback_mode="file",
        reader_keywords=["reader"],
    )
    book_file_fallback = {
        "title": "",
        "author": "Test Author",
        "folder": r"E:\\books\\Test Author\\Book Title",
        "files": [r"E:\\books\\Test Author\\Book Title\\track01.mp3"],
    }
    scanner.apply_preferences(book_file_fallback)
    assert "F: Title fallback from file used" in book_file_fallback.get("errors", [
    ])

    # Test F: Title fallback from folder used
    scanner.configure(
        scenario_mode="mass_standard",
        author_fallback_mode="folder",
        title_fallback_mode="folder",
        reader_keywords=["reader"],
    )
    book_folder_fallback = {
        "title": "Unknown",
        "author": "Test Author",
        "folder": r"E:\\books\\Test Author\\Book Title",
        "files": [r"E:\\books\\Test Author\\Book Title\\track01.mp3"],
    }
    scanner.apply_preferences(book_folder_fallback)
    assert "F: Title fallback from folder used" in book_folder_fallback.get(
        "errors", [])

    # Test F: Author fallback from folder used
    scanner.configure(
        scenario_mode="mass_standard",
        author_fallback_mode="folder",
        title_fallback_mode="file",
        reader_keywords=["reader"],
    )
    book_author_fallback = {
        "title": "Book Title",
        "author": "",
        "folder": r"E:\\books\\Test Author\\Book Title",
        "files": [r"E:\\books\\Test Author\\Book Title\\track01.mp3"],
    }
    scanner.apply_preferences(book_author_fallback)
    assert "F: Author fallback from folder used" in book_author_fallback.get(
        "errors", [])


def test_autocorrect_ignores_genre_and_series():
    """Verify that corrections to Genre and Series do NOT generate C: flags."""
    scanner = ImportScanner()
    scanner.configure(
        scenario_mode="mass_standard",
        author_fallback_mode="folder",
        title_fallback_mode="file",
        reader_keywords=["reader"],
        trim_whitespace=True,
        proper_case_fields=True,
    )

    # Book with genre and series that will be corrected, but ONLY title/author should generate flags
    book = {
        "title": "  clean   title  ",
        "author": "John Smith",
        "genre": "  SCIENCE   fiction  ",  # Will be corrected but should NOT flag
        "series": "  foundation   SERIES  ",  # Will be corrected but should NOT flag
        "folder": r"E:\\books\\John Smith\\Clean Title",
        "files": [r"E:\\books\\John Smith\\Clean Title\\track01.mp3"],
    }

    scanner.apply_preferences(book)

    # Genre and Series should be corrected in the book data
    assert book["genre"] == "Science Fiction"
    assert book["series"] == "Foundation Series"

    # But C: flag should only mention Title, NOT Genre or Series
    c_flags = [err for err in book.get(
        "errors", []) if str(err).startswith("C:")]
    if c_flags:
        # Should only contain Title, not Genre or Series
        title_flags = [f for f in c_flags if "Title" in f]
        assert len(title_flags) > 0
        # None should mention Genre or Series
        assert all("Genre" not in f for f in c_flags)
        assert all("Series" not in f for f in c_flags)


def test_fallback_suppresses_autocorrect_flag_for_same_field():
    """Verify that F: flag suppresses C: flag for the same field."""
    scanner = ImportScanner()
    scanner.configure(
        scenario_mode="mass_standard",
        author_fallback_mode="folder",
        title_fallback_mode="file",
        reader_keywords=["reader"],
        trim_whitespace=True,
        proper_case_fields=True,
    )

    # Book where Title uses fallback AND will be auto-corrected
    # Should only show F: flag, not C: flag for Title
    book = {
        "title": "",  # Will use file fallback
        "author": "  john   SMITH  ",  # Will be auto-corrected (no fallback)
        "folder": r"E:\\books\\john SMITH\\  the   BOOK  ",
        "files": [r"E:\\books\\john SMITH\\  the   BOOK  \\track01.mp3"],
    }

    scanner.apply_preferences(book)

    errors = book.get("errors", [])
    f_flags = [err for err in errors if str(err).startswith("F:")]
    c_flags = [err for err in errors if str(err).startswith("C:")]

    # Should have F: flag for Title fallback
    assert len(f_flags) == 1
    assert "Title fallback from file used" in f_flags[0]

    # Should have C: flag for Author only, NOT Title
    assert len(c_flags) >= 1
    # All C: flags should be for Author
    assert all("Author" in f for f in c_flags)
    # None should be for Title
    assert all("Title" not in f for f in c_flags)


def test_specific_correction_messages():
    """Verify that C: messages specify exact corrections applied."""
    scanner = ImportScanner()

    # Test trimmed message
    scanner.configure(
        scenario_mode="mass_standard",
        author_fallback_mode="none",
        title_fallback_mode="none",
        reader_keywords=["reader"],
        trim_whitespace=True,
    )
    book1 = {
        "title": "  Clean Title  ",
        "author": "John Smith",
        "folder": r"E:\\books\\John Smith\\Clean Title",
        "files": [r"E:\\books\\John Smith\\Clean Title\\track01.mp3"],
    }
    scanner.apply_preferences(book1)
    c_flags1 = [err for err in book1.get(
        "errors", []) if str(err).startswith("C:")]
    assert any("Title trimmed" in f for f in c_flags1)

    # Test punctuation removed message
    scanner.configure(
        scenario_mode="mass_standard",
        author_fallback_mode="none",
        title_fallback_mode="none",
        reader_keywords=["reader"],
        strip_leading_punctuation=True,
    )
    book2 = {
        "title": "Clean Title",
        "author": "...John Smith",
        "folder": r"E:\\books\\John Smith\\Clean Title",
        "files": [r"E:\\books\\John Smith\\Clean Title\\track01.mp3"],
    }
    scanner.apply_preferences(book2)
    c_flags2 = [err for err in book2.get(
        "errors", []) if str(err).startswith("C:")]
    assert any("Author punctuation removed" in f for f in c_flags2)

    # Test special characters removed message
    scanner.configure(
        scenario_mode="mass_standard",
        author_fallback_mode="none",
        title_fallback_mode="none",
        reader_keywords=["reader"],
        remove_non_alphanumeric=True,
    )
    book3 = {
        "title": "Clean@#$ Title",
        "author": "John Smith",
        "folder": r"E:\\books\\John Smith\\Clean Title",
        "files": [r"E:\\books\\John Smith\\Clean Title\\track01.mp3"],
    }
    scanner.apply_preferences(book3)
    c_flags3 = [err for err in book3.get(
        "errors", []) if str(err).startswith("C:")]
    assert any("Title special characters removed" in f for f in c_flags3)
