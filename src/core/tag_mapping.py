"""Audio tag → book field mapping preferences for folder import."""

from __future__ import annotations

from typing import Any

# QSettings keys
TITLE_TAG_SETTING = "import/tag_mapping/title"
AUTHOR_TAG_SETTING = "import/tag_mapping/author"

# Stored values (stable)
TITLE_ALBUM = "album"
TITLE_TRACK = "track_title"
TITLE_ALBUM_THEN_TRACK = "album_then_track"

AUTHOR_ALBUM_ARTIST_THEN_ARTIST = "album_artist_then_artist"
AUTHOR_ALBUM_ARTIST_ONLY = "album_artist_only"
AUTHOR_ARTIST_ONLY = "artist_only"

TITLE_CHOICES = (
    (TITLE_ALBUM, "Album"),
    (TITLE_TRACK, "Track title"),
    (TITLE_ALBUM_THEN_TRACK, "Album then track title"),
)

AUTHOR_CHOICES = (
    (AUTHOR_ALBUM_ARTIST_THEN_ARTIST, "Album artist then artist"),
    (AUTHOR_ALBUM_ARTIST_ONLY, "Album artist only"),
    (AUTHOR_ARTIST_ONLY, "Artist only"),
)


def read_title_mapping(settings=None) -> str:
    from src.utils.settings_helpers import read_setting

    if settings is not None:
        value = settings.value(TITLE_TAG_SETTING, TITLE_ALBUM, type=str)
    else:
        value = read_setting(TITLE_TAG_SETTING, TITLE_ALBUM, type=str)
    value = (value or TITLE_ALBUM).strip()
    allowed = {key for key, _ in TITLE_CHOICES}
    return value if value in allowed else TITLE_ALBUM


def read_author_mapping(settings=None) -> str:
    from src.utils.settings_helpers import read_setting

    if settings is not None:
        value = settings.value(
            AUTHOR_TAG_SETTING, AUTHOR_ALBUM_ARTIST_THEN_ARTIST, type=str
        )
    else:
        value = read_setting(
            AUTHOR_TAG_SETTING, AUTHOR_ALBUM_ARTIST_THEN_ARTIST, type=str
        )
    value = (value or AUTHOR_ALBUM_ARTIST_THEN_ARTIST).strip()
    allowed = {key for key, _ in AUTHOR_CHOICES}
    return value if value in allowed else AUTHOR_ALBUM_ARTIST_THEN_ARTIST


def resolve_book_title(info: Any, title_mapping: str | None = None) -> str:
    mapping = title_mapping or read_title_mapping()
    album = (getattr(info, "album", "") or "").strip()
    track = (getattr(info, "track_title", "") or "").strip()
    if mapping == TITLE_TRACK:
        return track or album
    if mapping == TITLE_ALBUM_THEN_TRACK:
        return album or track
    return album or track


def resolve_book_author(info: Any, author_mapping: str | None = None) -> str:
    mapping = author_mapping or read_author_mapping()
    album_artist = (getattr(info, "album_artist", "") or "").strip()
    artist = (getattr(info, "artist", "") or "").strip()
    if mapping == AUTHOR_ALBUM_ARTIST_ONLY:
        return album_artist
    if mapping == AUTHOR_ARTIST_ONLY:
        return artist
    return album_artist or artist
