"""Resolve an audiobook file for in-app Preview."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.core.library_root import apply_collection_root
from src.core.tag_reader import TagReader


@dataclass(frozen=True)
class PreviewTarget:
    path: Path | None = None
    error: str = ""


def resolve_preview_file(path: str, collection_root: str = "") -> PreviewTarget:
    """Return the file to play, or an error when Preview must stay off.

    When a collection library root is set, the stored import path is
    remapped onto that folder so a portable drive can move. If the
    remapped location is missing, the stored path is tried next.

    Folder scan: immediate children first. If none, one level of
    subfolders. Files are sorted by name, case-insensitive. The first
    supported audio file is used. Filename order may not match listening
    order (for example chapter 10 before chapter 2).
    """
    text = (path or "").strip()
    if not text:
        return PreviewTarget(error="No file path is set.")
    remapped = apply_collection_root(text, collection_root)
    remapped_path = Path(remapped)
    if remapped_path.exists():
        return _resolve_existing_path(remapped)
    if remapped != text:
        stored_result = _resolve_existing_path(text)
        if stored_result.path is not None:
            return stored_result
    return PreviewTarget(error=f"Book not found in - {remapped}")


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


def preview_can_launch(path: str, collection_root: str = "") -> bool:
    """True when Preview should be enabled for this stored path."""
    return resolve_preview_file(path, collection_root=collection_root).path is not None


def _resolve_existing_path(text: str) -> PreviewTarget:
    target = Path(text)
    if target.is_file():
        if target.suffix.lower() in TagReader.SUPPORTED_EXTENSIONS:
            return PreviewTarget(path=target)
        return PreviewTarget(error="This path is not a recognized audiobook file.")
    if target.is_dir():
        found = _first_audio_in_folder(target)
        if found is None:
            return PreviewTarget(
                error="This folder has no recognized audiobook files."
            )
        return PreviewTarget(path=found)
    return PreviewTarget(error=f"Book not found in - {text}")


def _first_audio_in_folder(folder: Path) -> Path | None:
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
    if not files:
        return None
    files.sort(key=lambda item: item.name.casefold())
    return files[0]
