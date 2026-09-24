"""Resolve an audiobook file for in-app Preview."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.core.tag_reader import TagReader


@dataclass(frozen=True)
class PreviewTarget:
    path: Path | None = None
    error: str = ""


def resolve_preview_file(path: str) -> PreviewTarget:
    """Return the file to play, or an error when Preview must stay off.

    Folder scan: immediate children first. If none, one level of
    subfolders. Files are sorted by name, case-insensitive. The first
    supported audio file is used. Filename order may not match listening
    order (for example chapter 10 before chapter 2).
    """
    text = (path or "").strip()
    if not text:
        return PreviewTarget(error="No file path is set.")
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


def preview_can_launch(path: str) -> bool:
    """True when Preview should be enabled for this stored path."""
    return resolve_preview_file(path).path is not None


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
