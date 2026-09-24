"""Collection library root folder checks (Phase 11 Part A)."""

from __future__ import annotations

from pathlib import Path

from src.core.tag_reader import TagReader


def folder_exists(path: str) -> bool:
    """True when path is an existing directory."""
    text = (path or "").strip()
    return bool(text) and Path(text).is_dir()


def folder_has_supported_audio(path: str) -> bool:
    """True when the folder tree has at least one TagReader audio file."""
    folder = Path((path or "").strip())
    if not folder.is_dir():
        return False
    extensions = {ext.lower() for ext in TagReader.SUPPORTED_EXTENSIONS}
    for child in folder.rglob("*"):
        if child.is_file() and child.suffix.lower() in extensions:
            return True
    return False


def apply_collection_root(stored_path: str, collection_root: str) -> str:
    """Replace the import-time root with the current collection library folder.

    The stored book path keeps author, title, and file folders. Those are
    joined under ``collection_root`` so a portable drive can move without
    rewriting ``books.path``.
    """
    stored_text = (stored_path or "").strip()
    root_text = (collection_root or "").strip()
    if not stored_text or not root_text:
        return stored_text
    stored = Path(stored_text)
    root = Path(root_text)
    if _is_under(stored, root):
        return str(stored)

    rel_parts = _parts_after_drive(stored)
    if not rel_parts:
        return str(root)

    root_name = root.name
    if root_name:
        for index, part in enumerate(rel_parts):
            if part.casefold() == root_name.casefold():
                suffix = rel_parts[index + 1 :]
                return str(root.joinpath(*suffix)) if suffix else str(root)

    for start in range(len(rel_parts)):
        candidate = root.joinpath(*rel_parts[start:])
        if candidate.exists():
            return str(candidate)

    if len(rel_parts) >= 2:
        return str(root.joinpath(*rel_parts[1:]))
    return str(root.joinpath(*rel_parts))


def _parts_after_drive(path: Path) -> tuple[str, ...]:
    parts = path.parts
    if path.drive and parts:
        return parts[1:]
    if parts and parts[0] in ("/", "\\"):
        return parts[1:]
    return parts


def _is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (ValueError, OSError):
        return False


IMPORT_DEFAULT_DIRECTORY_KEY = "import/default_directory"


def sync_single_collection_import_path(collection_queries, settings) -> str:
    """If there is only one collection, copy the filled path into the empty one.

    Returns ``collection``, ``prefs``, or ``""``. Does not overwrite a path
    that is already set. Two or more collections are left unchanged.
    """
    collections = collection_queries.get_all(active_only=False)
    if len(collections) != 1:
        return ""
    collection = collections[0]
    try:
        prefs = settings.value(IMPORT_DEFAULT_DIRECTORY_KEY, "", type=str)
    except TypeError:
        prefs = settings.value(IMPORT_DEFAULT_DIRECTORY_KEY, "")
    prefs = (prefs or "").strip()
    root = (collection.root_path or "").strip()
    if root and not prefs:
        settings.setValue(IMPORT_DEFAULT_DIRECTORY_KEY, root)
        return "prefs"
    if prefs and not root:
        collection.root_path = prefs
        collection_queries.update(collection)
        return "collection"
    return ""


def root_path_issue(path: str) -> str:
    """Return ``missing``, ``empty``, or ``""`` when the path is usable or blank."""
    text = (path or "").strip()
    if not text:
        return ""
    if not folder_exists(text):
        return "missing"
    if not folder_has_supported_audio(text):
        return "empty"
    return ""
