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


def test_resolve_book_author_default_prefers_album_artist():
    info = SimpleNamespace(album_artist="Album Artist", artist="Track Artist")
    assert resolve_book_author(info, "album_artist_then_artist") == "Album Artist"
