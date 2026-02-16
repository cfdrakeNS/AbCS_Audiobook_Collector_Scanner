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
