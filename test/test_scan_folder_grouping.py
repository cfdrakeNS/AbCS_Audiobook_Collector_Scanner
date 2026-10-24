"""BookScanner.scan_folder groups files by album and album artist."""

from __future__ import annotations

import os

import pytest

from src.core.tag_mapping import AUTHOR_ALBUM_ARTIST_THEN_ARTIST, TITLE_ALBUM
from src.core.tag_reader import AudioFileInfo, BookScanner


@pytest.fixture
def scanner(monkeypatch):
    monkeypatch.setattr(
        "src.core.tag_mapping.read_title_mapping", lambda settings=None: TITLE_ALBUM
    )
    monkeypatch.setattr(
        "src.core.tag_mapping.read_author_mapping",
        lambda settings=None: AUTHOR_ALBUM_ARTIST_THEN_ARTIST,
    )
    return BookScanner()


def _write(folder, names):
    folder.mkdir(parents=True, exist_ok=True)
    for name in names:
        (folder / name).write_bytes(b"stub")


def _use_tags(scanner, monkeypatch, album_for, artist_for=lambda _path: "Author"):
    def _fake_read(file_path: str) -> AudioFileInfo:
        info = AudioFileInfo()
        info.file_path = file_path
        info.album = album_for(file_path)
        info.album_artist = artist_for(file_path)
        return info

    monkeypatch.setattr(scanner.tag_reader, "read_file", _fake_read)


def _use_album_with_bad_file(scanner, monkeypatch, album):
    def _fake_read(file_path: str) -> AudioFileInfo:
        info = AudioFileInfo()
        info.file_path = file_path
        info.album_artist = "Author"
        if file_path.endswith("bad.mp3"):
            info.read_error = "Error reading file: can't sync to MPEG frame"
        else:
            info.album = album
        return info

    monkeypatch.setattr(scanner.tag_reader, "read_file", _fake_read)


def _counts_by_folder(books):
    return {os.path.basename(book["folder"]): book["tracks"] for book in books}


@pytest.mark.parametrize(
    "disc_names",
    [
        ("World Gone By [Disc 1]", "World Gone By [Disc 2]"),
        ("The Moonstone cd1", "The Moonstone cd2"),
        ("cd1", "cd2"),
    ],
)
def test_same_album_and_artist_across_subfolders_is_one_book(
    tmp_path, scanner, monkeypatch, disc_names
):
    _write(tmp_path / "Book" / disc_names[0], ["01.mp3", "02.mp3"])
    _write(tmp_path / "Book" / disc_names[1], ["03.mp3"])
    _use_tags(scanner, monkeypatch, lambda _path: "The Book")

    books = scanner.scan_folder(str(tmp_path), include_subfolders=True)

    assert len(books) == 1
    assert books[0]["tracks"] == 3
    assert books[0]["folder"] == str(tmp_path / "Book")


def test_one_folder_book_keeps_its_folder(tmp_path, scanner, monkeypatch):
    _write(tmp_path / "Book", ["01.mp3", "02.mp3"])
    _use_tags(scanner, monkeypatch, lambda _path: "The Book")

    books = scanner.scan_folder(str(tmp_path), include_subfolders=True)

    assert len(books) == 1
    assert books[0]["folder"] == str(tmp_path / "Book")


def test_same_album_different_album_artist_is_two_books(
    tmp_path, scanner, monkeypatch
):
    _write(tmp_path / "Book One", ["01.mp3", "02.mp3"])
    _write(tmp_path / "Book Two", ["01.mp3"])
    _use_tags(
        scanner,
        monkeypatch,
        lambda _path: "Collected Stories",
        lambda path: "Author One" if "Book One" in path else "Author Two",
    )

    books = scanner.scan_folder(str(tmp_path), include_subfolders=True)

    assert len(books) == 2
    assert _counts_by_folder(books) == {"Book One": 2, "Book Two": 1}


def test_no_album_with_same_disc_folder_names_stays_two_books(
    tmp_path, scanner, monkeypatch
):
    _write(tmp_path / "Book One" / "CD1", ["01.mp3", "02.mp3"])
    _write(tmp_path / "Book Two" / "CD1", ["01.mp3"])
    _use_tags(scanner, monkeypatch, lambda _path: "")

    books = scanner.scan_folder(str(tmp_path), include_subfolders=True)

    assert len(books) == 2
    assert sorted(book["tracks"] for book in books) == [1, 2]


def test_album_key_ignores_case_and_spaces(tmp_path, scanner, monkeypatch):
    _write(tmp_path / "Book", ["01.mp3", "02.mp3"])
    _use_tags(
        scanner,
        monkeypatch,
        lambda path: "The Book" if path.endswith("01.mp3") else " the book ",
    )

    books = scanner.scan_folder(str(tmp_path), include_subfolders=True)

    assert len(books) == 1
    assert books[0]["tracks"] == 2


def test_unreadable_file_joins_book_in_its_folder(tmp_path, scanner, monkeypatch):
    _write(tmp_path / "Book" / "cd1", ["01.mp3", "02.mp3"])
    _write(tmp_path / "Book" / "cd2", ["03.mp3", "bad.mp3"])
    _use_album_with_bad_file(scanner, monkeypatch, "The Book")

    books = scanner.scan_folder(str(tmp_path), include_subfolders=True)

    assert len(books) == 1
    assert books[0]["tracks"] == 4
    assert any("bad.mp3" in err for err in books[0]["errors"])
    assert "_unreadable_only" not in books[0]
    assert "_folder_keys" not in books[0]


def test_unreadable_file_without_album_book_stays_separate(
    tmp_path, scanner, monkeypatch
):
    _write(tmp_path / "Book", ["01.mp3"])
    _write(tmp_path / "Other", ["bad.mp3"])
    _use_album_with_bad_file(scanner, monkeypatch, "The Book")

    books = scanner.scan_folder(str(tmp_path), include_subfolders=True)

    assert len(books) == 2
    assert _counts_by_folder(books) == {"Book": 1, "Other": 1}
