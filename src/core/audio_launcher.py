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


def read_disc_and_track(path: Path) -> tuple[int | None, int | None]:
    """Return (disc, track) from embedded tags when present."""
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
    files.sort(key=audio_sort_key)
    return files


def playlist_elapsed_ms(
    files: tuple[Path, ...] | list[Path], current_index: int, position_ms: int
) -> int:
    """Return elapsed playlist time using the current file's local position."""
    index = min(max(int(current_index), 0), len(files))
    elapsed_ms = max(0, int(position_ms))
    reader = TagReader()
    for path in files[:index]:
        duration_seconds = reader.read_file(str(path)).duration_seconds
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
