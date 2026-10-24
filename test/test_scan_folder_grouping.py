"""BookScanner.scan_folder groups files by album within each book folder."""

from __future__ import annotations

import os

import pytest

from src.core.tag_mapping import AUTHOR_ALBUM_ARTIST_THEN_ARTIST, TITLE_ALBUM
from src.core.tag_reader import AudioFileInfo, BookScanner, book_folder_for_file


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


def _use_album(scanner, monkeypatch, album_for):
    def _fake_read(file_path: str) -> AudioFileInfo:
        info = AudioFileInfo()
        info.file_path = file_path
        info.album = album_for(file_path)
        info.album_artist = "Author"
        return info

    monkeypatch.setattr(scanner.tag_reader, "read_file", _fake_read)


def _counts_by_folder(books):
    return {os.path.basename(book["folder"]): book["tracks"] for book in books}


def test_shared_album_in_two_folders_stays_two_books(tmp_path, scanner, monkeypatch):
    _write(tmp_path / "Book One", ["01.mp3", "02.mp3"])
    _write(tmp_path / "Book Two", ["01.mp3", "02.mp3", "03.mp3"])
    _use_album(scanner, monkeypatch, lambda _path: "Series Name")

    books = scanner.scan_folder(str(tmp_path), include_subfolders=True)

    assert len(books) == 2
    assert _counts_by_folder(books) == {"Book One": 2, "Book Two": 3}


def test_no_album_with_same_disc_folder_names_stays_two_books(
    tmp_path, scanner, monkeypatch
):
    _write(tmp_path / "Book One" / "CD1", ["01.mp3", "02.mp3"])
    _write(tmp_path / "Book Two" / "CD1", ["01.mp3"])
    _use_album(scanner, monkeypatch, lambda _path: "")

    books = scanner.scan_folder(str(tmp_path), include_subfolders=True)

    assert len(books) == 2
    assert _counts_by_folder(books) == {"Book One": 2, "Book Two": 1}


def test_disc_folders_of_one_book_stay_one_book(tmp_path, scanner, monkeypatch):
    _write(tmp_path / "Book" / "CD1", ["01.mp3", "02.mp3"])
    _write(tmp_path / "Book" / "Disc 2", ["01.mp3", "02.mp3", "03.mp3"])
    _use_album(scanner, monkeypatch, lambda _path: "The Book")

    books = scanner.scan_folder(str(tmp_path), include_subfolders=True)

    assert len(books) == 1
    assert books[0]["tracks"] == 5
    assert os.path.basename(books[0]["folder"]) == "Book"


def test_album_key_ignores_case_and_spaces(tmp_path, scanner, monkeypatch):
    _write(tmp_path / "Book", ["01.mp3", "02.mp3"])
    _use_album(
        scanner,
        monkeypatch,
        lambda path: "The Book" if path.endswith("01.mp3") else " the book ",
    )

    books = scanner.scan_folder(str(tmp_path), include_subfolders=True)

    assert len(books) == 1
    assert books[0]["tracks"] == 2


@pytest.mark.parametrize(
    "disc_name", ["CD1", "cd 2", "Disc 3", "Disk_4", "Part 1", "pt.2"]
)
def test_book_folder_for_file_rolls_disc_folders_up(tmp_path, disc_name):
    path = tmp_path / "Book" / disc_name / "01.mp3"
    assert book_folder_for_file(str(path)) == str(tmp_path / "Book")


@pytest.mark.parametrize("folder_name", ["Book", "Chapter 1", "CD Collection"])
def test_book_folder_for_file_keeps_normal_folders(tmp_path, folder_name):
    path = tmp_path / folder_name / "01.mp3"
    assert book_folder_for_file(str(path)) == str(tmp_path / folder_name)


@pytest.mark.parametrize(
    "disc_name", ["The Moonstone cd1", "the moonstone CD 2", "The_Moonstone-Disc3"]
)
def test_book_folder_for_file_rolls_titled_disc_folders_up(tmp_path, disc_name):
    path = tmp_path / "The Moonstone" / disc_name / "01.mp3"
    assert book_folder_for_file(str(path)) == str(tmp_path / "The Moonstone")


def test_titled_disc_folders_of_one_book_stay_one_book(
    tmp_path, scanner, monkeypatch
):
    _write(tmp_path / "The Moonstone" / "The Moonstone cd1", ["01.mp3", "02.mp3"])
    _write(tmp_path / "The Moonstone" / "The Moonstone cd2", ["03.mp3"])
    _use_album(scanner, monkeypatch, lambda _path: "The Moonstone")

    books = scanner.scan_folder(str(tmp_path), include_subfolders=True)

    assert len(books) == 1
    assert books[0]["tracks"] == 3
    assert os.path.basename(books[0]["folder"]) == "The Moonstone"


def test_sibling_titled_disc_folders_stay_two_books(tmp_path, scanner, monkeypatch):
    _write(tmp_path / "Author" / "Book One cd1", ["01.mp3", "02.mp3"])
    _write(tmp_path / "Author" / "Book Two cd1", ["01.mp3"])
    _use_album(scanner, monkeypatch, lambda _path: "Series Name")

    books = scanner.scan_folder(str(tmp_path), include_subfolders=True)

    assert len(books) == 2
    assert _counts_by_folder(books) == {"Book One cd1": 2, "Book Two cd1": 1}


def test_unreadable_disc_file_joins_its_book(tmp_path, scanner, monkeypatch):
    _write(tmp_path / "Book" / "cd1", ["01.mp3", "02.mp3"])
    _write(tmp_path / "Book" / "cd2", ["03.mp3", "bad.mp3"])

    def _fake_read(file_path: str) -> AudioFileInfo:
        info = AudioFileInfo()
        info.file_path = file_path
        info.album_artist = "Author"
        if file_path.endswith("bad.mp3"):
            info.read_error = "Error reading file: can't sync to MPEG frame"
        else:
            info.album = "The Book"
        return info

    monkeypatch.setattr(scanner.tag_reader, "read_file", _fake_read)

    books = scanner.scan_folder(str(tmp_path), include_subfolders=True)

    assert len(books) == 1
    assert books[0]["tracks"] == 4
    assert any("bad.mp3" in err for err in books[0]["errors"])
    assert "_unreadable_disc_only" not in books[0]


def test_unreadable_file_in_book_folder_stays_separate(
    tmp_path, scanner, monkeypatch
):
    _write(tmp_path / "Book", ["01.mp3", "bad.mp3"])

    def _fake_read(file_path: str) -> AudioFileInfo:
        info = AudioFileInfo()
        info.file_path = file_path
        info.album_artist = "Author"
        if file_path.endswith("bad.mp3"):
            info.read_error = "Error reading file: can't sync to MPEG frame"
        else:
            info.album = "The Book"
        return info

    monkeypatch.setattr(scanner.tag_reader, "read_file", _fake_read)

    books = scanner.scan_folder(str(tmp_path), include_subfolders=True)

    assert len(books) == 2
