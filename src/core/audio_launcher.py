"""Resolve an audiobook file for in-app Preview."""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from src.core.library_root import (
    folder_exists,
    locate_book_under_collection,
    path_exists,
    resolve_book_location,
)
from src.core.tag_reader import TagReader


@dataclass(frozen=True)
class PreviewTarget:
    path: Path | None = None
    error: str = ""
    # Set when the book was found by author/title layout, not its stored path.
    found_path: str = ""
    # Set on an author/title miss: where a Browse for the book should start.
    browse_dir: str = ""


@dataclass(frozen=True)
class PreviewPlaylist:
    """Ordered audio files for Preview next/previous and resume."""

    files: tuple[Path, ...] = ()
    start_index: int = 0
    folder_mode: bool = False
    error: str = ""
    # Set when the book was found by author/title layout, not its stored path.
    found_path: str = ""
    # Set on an author/title miss: where a Browse for the book should start.
    browse_dir: str = ""

    @property
    def path(self) -> Path | None:
        if not self.files:
            return None
        index = min(max(self.start_index, 0), len(self.files) - 1)
        return self.files[index]


@dataclass(frozen=True)
class BookLocation:
    path: str = ""
    error: str = ""
    found_path: str = ""
    browse_dir: str = ""


_BookLocation = BookLocation


def _collection_folder_phrase(collection_name: str = "") -> str:
    name = (collection_name or "").strip()
    return f"the {name} collection folder" if name else "the collection folder"


def _collection_folder_not_set_fix() -> str:
    return (
        "To fix, open Manage > Collections, edit the collection, and set the "
        "collection folder."
    )


def locate_book_path(
    stored_path: str,
    collection_root: str,
    import_dir: str,
    author_name: str,
    book_title: str,
    series_name: str,
    collection_name: str = "",
    series_number=None,
) -> BookLocation:
    """Stored path first; when blank or missing, the collection folder layout.

    Listen and Check Book Locations both use this so they agree on where a book is.
    """
    text = (stored_path or "").strip()
    resolved = ""
    if text:
        resolved = resolve_book_location(
            text, collection_root=collection_root, import_dir=import_dir
        )
        if path_exists(resolved):
            return _BookLocation(path=resolved)

    root = (collection_root or "").strip()
    author = (author_name or "").strip()
    if root and author:
        lookup = locate_book_under_collection(
            root,
            author_name,
            book_title,
            series_name,
            collection_name=collection_name,
            series_number=series_number,
        )
        if lookup.path:
            return _BookLocation(path=lookup.path, found_path=lookup.path)
        if lookup.message:
            return _BookLocation(error=lookup.message, browse_dir=lookup.browse_dir)

    if not text and not root:
        where = _collection_folder_phrase(collection_name)
        return _BookLocation(
            error=(
                f"This book has no file path and {where} is not set. "
                f"{_collection_folder_not_set_fix()}"
            )
        )
    if not text:
        if not author:
            reason = (
                "This book has no file path and no author, so Listen cannot "
                "look for it in the collection folder."
            )
        else:
            reason = "This book has no file path."
        return _BookLocation(
            error=reason,
            browse_dir=root if folder_exists(root) else "",
        )
    if not root:
        where = _collection_folder_phrase(collection_name)
        where_cap = f"{where[0].upper()}{where[1:]}" if where else where
        return _BookLocation(
            error=(
                f"Book not found in - {resolved}. {where_cap} is not set, "
                "so Listen cannot search by author and title. "
                f"{_collection_folder_not_set_fix()}"
            )
        )
    return _BookLocation(error=f"Book not found in - {resolved}")


_locate_book = locate_book_path


def parse_tag_number(raw) -> int | None:
    """Parse track/disc tags such as 4, '4', or '4/24' into the leading int."""
    if raw is None:
        return None
    if isinstance(raw, (list, tuple)):
        if not raw:
            return None
        raw = raw[0]
        if isinstance(raw, (list, tuple)):
            raw = raw[0] if raw else None
    if isinstance(raw, (int, float)):
        value = int(raw)
        return value if value > 0 else None
    text = str(raw).strip()
    if not text:
        return None
    if "/" in text:
        text = text.split("/", 1)[0].strip()
    try:
        value = int(text)
    except ValueError:
        return None
    return value if value > 0 else None


_SORTED_AUDIO_CACHE: dict[tuple, tuple[Path, ...]] = {}
_DURATION_CACHE: dict[tuple, float] = {}
_SORTED_AUDIO_CACHE_LIMIT = 128
_DURATION_CACHE_LIMIT = 4000


def _cache_store(cache: dict, key: tuple, value, limit: int) -> None:
    cache[key] = value
    if len(cache) > limit:
        cache.pop(next(iter(cache)))


def _file_cache_key(path: Path) -> tuple | None:
    try:
        stat = path.stat()
    except OSError:
        return None
    return (str(path), stat.st_mtime_ns, stat.st_size)


def _synchsafe(data: bytes) -> int:
    return (
        ((data[0] & 0x7F) << 21)
        | ((data[1] & 0x7F) << 14)
        | ((data[2] & 0x7F) << 7)
        | (data[3] & 0x7F)
    )


def _decode_id3_text(payload: bytes) -> str:
    if not payload:
        return ""
    encoding = payload[0]
    data = payload[1:]
    if encoding == 0:
        text = data.decode("latin-1", errors="ignore")
    elif encoding == 1:
        text = data.decode("utf-16", errors="ignore")
    elif encoding == 2:
        text = data.decode("utf-16-be", errors="ignore")
    elif encoding == 3:
        text = data.decode("utf-8", errors="ignore")
    else:
        return ""
    return text.split("\x00", 1)[0].strip()


def _mp3_disc_and_track(path: Path) -> tuple[int | None, int | None] | None:
    """Read TRCK/TPOS without loading the rest of the tag (cover art).

    Returns None when the tag is missing or not a simple v2.3/v2.4 tag, so the
    caller can fall back to a full parse.
    """
    try:
        with path.open("rb") as handle:
            header = handle.read(10)
            if len(header) < 10 or header[:3] != b"ID3":
                return None
            version = header[3]
            flags = header[5]
            if version < 3 or flags & 0xC0:
                return None
            remaining = _synchsafe(header[6:10])
            disc = None
            track = None
            while remaining >= 10 and (disc is None or track is None):
                frame_header = handle.read(10)
                if len(frame_header) < 10 or frame_header[:4] == b"\x00\x00\x00\x00":
                    break
                if version >= 4:
                    frame_size = _synchsafe(frame_header[4:8])
                else:
                    frame_size = int.from_bytes(frame_header[4:8], "big")
                if frame_size < 0 or frame_size > remaining - 10:
                    return None
                remaining -= 10 + frame_size
                frame_id = frame_header[:4]
                if frame_id in (b"TRCK", b"TPOS") and frame_size <= 64:
                    number = parse_tag_number(_decode_id3_text(handle.read(frame_size)))
                    if frame_id == b"TRCK":
                        track = number
                    else:
                        disc = number
                else:
                    handle.seek(frame_size, 1)
            return disc, track
    except OSError:
        return None


def _mp3_duration_seconds(path: Path) -> float:
    """Duration from the MPEG header, skipping the ID3 tag and its cover art."""
    try:
        from mutagen.mp3 import HeaderNotFoundError, MPEGInfo

        with path.open("rb") as handle:
            header = handle.read(10)
            offset = 0
            if len(header) >= 10 and header[:3] == b"ID3":
                offset = 10 + _synchsafe(header[6:10])
            try:
                return float(MPEGInfo(handle, offset).length or 0)
            except HeaderNotFoundError:
                return 0.0
    except Exception:
        return 0.0


def file_duration_seconds(path: Path) -> float:
    """Cached playback length. MP3 uses the frame header, not the full tag."""
    key = _file_cache_key(path)
    if key is not None and key in _DURATION_CACHE:
        return _DURATION_CACHE[key]
    length = _mp3_duration_seconds(path) if path.suffix.lower() == ".mp3" else 0.0
    if length <= 0:
        length = float(TagReader().read_file(str(path)).duration_seconds or 0)
    if key is not None:
        _cache_store(_DURATION_CACHE, key, length, _DURATION_CACHE_LIMIT)
    return length


def read_disc_and_track(path: Path) -> tuple[int | None, int | None]:
    """Return (disc, track) from embedded tags when present."""
    if path.suffix.lower() == ".mp3":
        light = _mp3_disc_and_track(path)
        if light is not None:
            return light
    return _mutagen_disc_and_track(path)


def _mutagen_disc_and_track(path: Path) -> tuple[int | None, int | None]:
    audio = None
    try:
        from mutagen import File as MutagenFile

        audio = MutagenFile(str(path))
    except Exception:
        return None, None
    if audio is None:
        return None, None

    disc = None
    track = None
    tags = getattr(audio, "tags", None)

    if tags is not None:
        if "TPOS" in tags:
            disc = parse_tag_number(tags["TPOS"])
        if "TRCK" in tags:
            track = parse_tag_number(tags["TRCK"])
        if disc is None:
            disc = parse_tag_number(
                _first_tag_value(tags, ("discnumber", "DISCNUMBER", "disk"))
            )
        if track is None:
            track = parse_tag_number(
                _first_tag_value(tags, ("tracknumber", "TRACKNUMBER", "track"))
            )
        if disc is None and hasattr(tags, "get"):
            try:
                disc = parse_tag_number(tags.get("disk"))
            except Exception:
                pass
        if track is None and hasattr(tags, "get"):
            try:
                track = parse_tag_number(tags.get("trkn"))
            except Exception:
                pass

    return disc, track


def _first_tag_value(tags, names: tuple[str, ...]):
    for name in names:
        try:
            if name in tags:
                value = tags[name]
                if isinstance(value, list) and value:
                    return value[0]
                return value
        except Exception:
            continue
    return None


def audio_sort_key(path: Path) -> tuple:
    """Sort key: disc, then track, then file name. Missing track sorts last."""
    disc, track = read_disc_and_track(path)
    return (
        disc if disc is not None else 0,
        track if track is not None else 10**9,
        path.name.casefold(),
    )


def path_has_playable_audio(path: str | Path) -> bool:
    """True when Listen can play this path (a supported file, or audio in the folder).

    Matches the folders ``list_audio_in_folder`` uses, and stops at the first
    file so a path check does not sort or open every track.
    """
    target = Path(path)
    extensions = {ext.lower() for ext in TagReader.SUPPORTED_EXTENSIONS}
    try:
        if target.is_file():
            return target.suffix.lower() in extensions
        if not target.is_dir():
            return False
        children = list(target.iterdir())
    except OSError:
        return False
    if any(child.is_file() and child.suffix.lower() in extensions for child in children):
        return True
    for child in children:
        if not child.is_dir():
            continue
        try:
            grandchildren = child.iterdir()
        except OSError:
            continue
        for grandchild in grandchildren:
            if grandchild.is_file() and grandchild.suffix.lower() in extensions:
                return True
    return False


def list_audio_in_folder(folder: Path) -> list[Path]:
    """Audio files in a book folder, ordered for Preview playback."""
    extensions = {ext.lower() for ext in TagReader.SUPPORTED_EXTENSIONS}
    files = [
        child
        for child in folder.iterdir()
        if child.is_file() and child.suffix.lower() in extensions
    ]
    if not files:
        nested: list[Path] = []
        for child in folder.iterdir():
            if not child.is_dir():
                continue
            nested.extend(
                grandchild
                for grandchild in child.iterdir()
                if grandchild.is_file() and grandchild.suffix.lower() in extensions
            )
        files = nested
    cache_key = None
    parts = []
    for path in files:
        part = _file_cache_key(path)
        if part is None:
            parts = None
            break
        parts.append(part)
    if parts is not None:
        cache_key = (str(folder), tuple(parts))
        cached = _SORTED_AUDIO_CACHE.get(cache_key)
        if cached is not None:
            return list(cached)
    files.sort(key=audio_sort_key)
    if cache_key is not None:
        _cache_store(
            _SORTED_AUDIO_CACHE, cache_key, tuple(files), _SORTED_AUDIO_CACHE_LIMIT
        )
    return files


def playlist_elapsed_ms(
    files: tuple[Path, ...] | list[Path], current_index: int, position_ms: int
) -> int:
    """Return elapsed playlist time using the current file's local position."""
    index = min(max(int(current_index), 0), len(files))
    elapsed_ms = max(0, int(position_ms))
    for path in files[:index]:
        duration_seconds = file_duration_seconds(path)
        if duration_seconds > 0:
            elapsed_ms += int(duration_seconds * 1000)
    return elapsed_ms


def resolve_preview_source(
    path: str,
    collection_root: str = "",
    import_dir: str = "",
    author_name: str = "",
    book_title: str = "",
    series_name: str = "",
    collection_name: str = "",
    series_number=None,
) -> PreviewTarget:
    """Return one playable file without building or metadata-sorting a playlist."""
    location = _locate_book(
        path,
        collection_root,
        import_dir,
        author_name,
        book_title,
        series_name,
        collection_name=collection_name,
        series_number=series_number,
    )
    if location.error:
        return PreviewTarget(error=location.error, browse_dir=location.browse_dir)
    resolved = location.path
    found_path = location.found_path
    target = Path(resolved)
    if target.is_file():
        if target.suffix.lower() in TagReader.SUPPORTED_EXTENSIONS:
            return PreviewTarget(path=target, found_path=found_path)
        return PreviewTarget(error="This path is not a recognized audiobook file.")
    if not target.is_dir():
        return PreviewTarget(error=f"Book not found in - {resolved}")

    extensions = TagReader.SUPPORTED_EXTENSIONS
    try:
        children = sorted(target.iterdir(), key=lambda item: item.name.casefold())
        for child in children:
            if child.is_file() and child.suffix.lower() in extensions:
                return PreviewTarget(path=child, found_path=found_path)
        for child in children:
            if not child.is_dir():
                continue
            for item in sorted(child.iterdir(), key=lambda entry: entry.name.casefold()):
                if item.is_file() and item.suffix.lower() in extensions:
                    return PreviewTarget(path=item, found_path=found_path)
    except OSError:
        return PreviewTarget(error=f"Book not found in - {resolved}")
    return PreviewTarget(error="This folder has no recognized audiobook files.")

def resolve_preview_file(
    path: str, collection_root: str = "", import_dir: str = ""
) -> PreviewTarget:
    """Return the file to play, or an error when Preview must stay off.

    When the stored path is missing, the path is remapped onto the collection
    library root (drive and root stripped), then onto the Preferences import
    folder if that is set.

    Folder scan: immediate children first. If none, one level of
    subfolders. Files are ordered by disc number, then track number,
    then file name. Files without a track number come last.
    """
    playlist = resolve_preview_playlist(
        path, collection_root=collection_root, import_dir=import_dir
    )
    if playlist.error:
        return PreviewTarget(error=playlist.error)
    return PreviewTarget(path=playlist.path)


def resolve_preview_playlist(
    path: str,
    collection_root: str = "",
    import_dir: str = "",
    listen_file_name: str = "",
    author_name: str = "",
    book_title: str = "",
    series_name: str = "",
    collection_name: str = "",
    series_number=None,
) -> PreviewPlaylist:
    """Return the ordered playlist and start index for Preview.

    A blank or missing stored path falls back to the collection folder:
    the author folder, then the series folder when the book has a series.
    """
    location = _locate_book(
        path,
        collection_root,
        import_dir,
        author_name,
        book_title,
        series_name,
        collection_name=collection_name,
        series_number=series_number,
    )
    if location.error:
        return PreviewPlaylist(error=location.error, browse_dir=location.browse_dir)
    playlist = _playlist_for_existing_path(
        location.path, listen_file_name=listen_file_name
    )
    if location.found_path and not playlist.error:
        return replace(playlist, found_path=location.found_path)
    return playlist


def _playlist_for_existing_path(
    text: str, listen_file_name: str = ""
) -> PreviewPlaylist:
    target = Path(text)
    if target.is_file():
        if target.suffix.lower() in TagReader.SUPPORTED_EXTENSIONS:
            return PreviewPlaylist(files=(target,), start_index=0, folder_mode=False)
        return PreviewPlaylist(error="This path is not a recognized audiobook file.")
    if target.is_dir():
        files = list_audio_in_folder(target)
        if not files:
            return PreviewPlaylist(
                error="This folder has no recognized audiobook files."
            )
        start = 0
        wanted = (listen_file_name or "").strip()
        if wanted:
            for index, item in enumerate(files):
                if item.name == wanted or item.name.casefold() == wanted.casefold():
                    start = index
                    break
        return PreviewPlaylist(
            files=tuple(files), start_index=start, folder_mode=True
        )
    return PreviewPlaylist(error=f"Book not found in - {text}")


def _apic_bytes(tags) -> bytes | None:
    if tags is None or not hasattr(tags, "getall"):
        return None
    for frame in tags.getall("APIC"):
        data = getattr(frame, "data", None)
        if data:
            return bytes(data)
    return None


def embedded_cover_bytes(audio) -> bytes | None:
    """Return embedded cover art from an open mutagen file, or None."""
    if audio is None:
        return None
    pictures = getattr(audio, "pictures", None) or []
    for picture in pictures:
        data = getattr(picture, "data", None)
        if data:
            return bytes(data)
    from_tags = _apic_bytes(getattr(audio, "tags", None))
    if from_tags:
        return from_tags
    from_id3 = _apic_bytes(audio)
    if from_id3:
        return from_id3
    tags = getattr(audio, "tags", None)
    if tags is None:
        return None
    try:
        covers = tags.get("covr")
    except Exception:
        covers = None
    if covers:
        return bytes(covers[0])
    return None


def read_embedded_cover(path: Path) -> bytes | None:
    """Read embedded cover art from an audio file. Missing art is None."""
    audio = None
    try:
        from mutagen import File as MutagenFile

        audio = MutagenFile(str(path))
    except Exception:
        audio = None
    found = embedded_cover_bytes(audio)
    if found:
        return found
    if path.suffix.lower() != ".mp3":
        return None
    try:
        from mutagen.id3 import ID3

        return embedded_cover_bytes(ID3(str(path)))
    except Exception:
        return None


def preview_can_launch(
    path: str, collection_root: str = "", import_dir: str = ""
) -> bool:
    """True when Preview should be enabled for this stored path."""
    return (
        resolve_preview_file(
            path, collection_root=collection_root, import_dir=import_dir
        ).path
        is not None
    )
