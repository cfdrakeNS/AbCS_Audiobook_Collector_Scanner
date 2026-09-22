"""Tests for import tag mapping."""

from __future__ import annotations

from types import SimpleNamespace

from src.core.tag_mapping import (
    AUTHOR_ARTIST_ONLY,
    TITLE_TRACK,
    resolve_book_author,
    resolve_book_title,
)


def test_resolve_book_title_defaults_to_album():
    info = SimpleNamespace(album="Album Title", track_title="Track Title")
    assert resolve_book_title(info, "album") == "Album Title"


def test_resolve_book_title_track():
    info = SimpleNamespace(album="Album Title", track_title="Track Title")
    assert resolve_book_title(info, TITLE_TRACK) == "Track Title"


def test_resolve_book_author_artist_only():
    info = SimpleNamespace(album_artist="Album Artist", artist="Track Artist")
    assert resolve_book_author(info, AUTHOR_ARTIST_ONLY) == "Track Artist"


def test_resolve_book_title_album_does_not_use_track_when_empty():
    info = SimpleNamespace(album="", track_title="Track Title")
    assert resolve_book_title(info, "album") == ""


def test_resolve_book_title_album_then_track():
    from src.core.tag_mapping import TITLE_ALBUM_THEN_TRACK

    present = SimpleNamespace(album="Album Title", track_title="Track Title")
    missing = SimpleNamespace(album="", track_title="Track Title")
    assert resolve_book_title(present, TITLE_ALBUM_THEN_TRACK) == "Album Title"
    assert resolve_book_title(missing, TITLE_ALBUM_THEN_TRACK) == "Track Title"


def test_resolve_book_author_album_artist_only():
    from src.core.tag_mapping import AUTHOR_ALBUM_ARTIST_ONLY

    info = SimpleNamespace(album_artist="", artist="Track Artist")
    assert resolve_book_author(info, AUTHOR_ALBUM_ARTIST_ONLY) == ""


def test_scan_groups_by_album_when_title_is_track(tmp_path, monkeypatch):
    import os

    from src.core.tag_mapping import AUTHOR_ALBUM_ARTIST_THEN_ARTIST, TITLE_TRACK
    from src.core.tag_reader import AudioFileInfo, BookScanner

    monkeypatch.setattr(
        "src.core.tag_mapping.read_title_mapping", lambda settings=None: TITLE_TRACK
    )
    monkeypatch.setattr(
        "src.core.tag_mapping.read_author_mapping",
        lambda settings=None: AUTHOR_ALBUM_ARTIST_THEN_ARTIST,
    )

    folder = tmp_path / "book"
    folder.mkdir()
    first = folder / "01.mp3"
    second = folder / "02.mp3"
    first.write_bytes(b"stub")
    second.write_bytes(b"stub")

    def _fake_read(file_path: str) -> AudioFileInfo:
        info = AudioFileInfo()
        info.file_path = file_path
        info.album = "Shared Album"
        info.track_title = "Chapter " + os.path.basename(file_path)
        info.album_artist = "Album Author"
        info.artist = "Track Author"
        return info

    scanner = BookScanner()
    monkeypatch.setattr(scanner.tag_reader, "read_file", _fake_read)
    books = scanner.scan_folder(str(folder), include_subfolders=False)
    assert len(books) == 1
    assert books[0]["title"].startswith("Chapter ")
    assert books[0]["author"] == "Album Author"
    assert books[0]["tracks"] == 2


def test_scan_author_artist_only_ignores_album_artist(tmp_path, monkeypatch):
    from src.core.tag_mapping import AUTHOR_ARTIST_ONLY, TITLE_ALBUM
    from src.core.tag_reader import AudioFileInfo, BookScanner

    monkeypatch.setattr(
        "src.core.tag_mapping.read_title_mapping", lambda settings=None: TITLE_ALBUM
    )
    monkeypatch.setattr(
        "src.core.tag_mapping.read_author_mapping",
        lambda settings=None: AUTHOR_ARTIST_ONLY,
    )

    folder = tmp_path / "book"
    folder.mkdir()
    audio = folder / "01.mp3"
    audio.write_bytes(b"stub")

    def _fake_read(file_path: str) -> AudioFileInfo:
        info = AudioFileInfo()
        info.file_path = file_path
        info.album = "Shared Album"
        info.album_artist = "Album Author"
        info.artist = "Track Author"
        return info

    scanner = BookScanner()
    monkeypatch.setattr(scanner.tag_reader, "read_file", _fake_read)
    books = scanner.scan_folder(str(folder), include_subfolders=False)
    assert books[0]["title"] == "Shared Album"
    assert books[0]["author"] == "Track Author"


def test_placeholder_title_still_uses_file_fallback(tmp_path):
    from src.core.import_scanner import ImportScanner

    audio = tmp_path / "01 Real Name.mp3"
    audio.write_bytes(b"stub")
    book = {
        "title": "unknown album",
        "author": "Jane Author",
        "folder": str(tmp_path),
        "files": [str(audio)],
        "comment": "",
        "narrator": "",
        "errors": [],
    }
    ImportScanner().apply_preferences(book)
    assert book["title"] == "Real Name"


def test_resolve_book_author_default_prefers_album_artist():
    info = SimpleNamespace(album_artist="Album Artist", artist="Track Artist")
    assert resolve_book_author(info, "album_artist_then_artist") == "Album Artist"
