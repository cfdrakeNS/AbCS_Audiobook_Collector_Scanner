"""Collection library root folder checks (Phase 11 Part A)."""

from __future__ import annotations

from pathlib import Path

from src.core.tag_reader import TagReader


def path_exists(path: str | Path) -> bool:
    """True when the path exists; False if missing or stat fails (e.g. shared-folder permissions)."""
    try:
        return Path(path).exists()
    except OSError:
        return False


def folder_exists(path: str) -> bool:
    """True when path is an existing directory."""
    text = (path or "").strip()
    if not text:
        return False
    try:
        return Path(text).is_dir()
    except OSError:
        return False


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
        if path_exists(candidate):
            return str(candidate)

    if len(rel_parts) >= 2:
        return str(root.joinpath(*rel_parts[1:]))
    return str(root.joinpath(*rel_parts))


def resolve_book_location(
    stored_path: str,
    collection_root: str = "",
    import_dir: str = "",
) -> str:
    """Return an existing book path for Play, or the last tried path if none exist.

    Order when the stored path is missing: remap under the collection library
    root (strip drive / root), then under the Preferences import folder.
    """
    text = (stored_path or "").strip()
    if not text:
        return ""
    if path_exists(text):
        return text
    last = text
    for base in ((collection_root or "").strip(), (import_dir or "").strip()):
        if not base:
            continue
        candidate = apply_collection_root(text, base)
        if not candidate:
            continue
        if path_exists(candidate):
            return candidate
        if last == text:
            last = candidate
    return last


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


def path_is_under_root(path: str, root: str) -> bool:
    """True when ``path`` resolves under ``root`` (both non-empty)."""
    path_text = (path or "").strip()
    root_text = (root or "").strip()
    if not path_text or not root_text:
        return False
    return _is_under(Path(path_text), Path(root_text))


def browse_start_directory(
    current_path: str,
    collection_root: str = "",
    prefs_import_dir: str = "",
) -> str:
    """Directory for a path Browse dialog (first existing candidate).

    Order: current path if it is a directory; else its parent if it is a file;
    when the stored path is missing, the same remap as Play (collection root,
    then Preferences import); then the collection or import folder itself.
    """
    current = (current_path or "").strip()
    if current:
        current_p = Path(current)
        if current_p.is_dir():
            return str(current_p)
        if current_p.is_file():
            parent = current_p.parent
            if parent.is_dir():
                return str(parent)
        resolved = resolve_book_location(
            current, collection_root, prefs_import_dir
        )
        if resolved:
            resolved_p = Path(resolved)
            if resolved_p.is_dir():
                return str(resolved_p)
            if resolved_p.is_file():
                parent = resolved_p.parent
                if parent.is_dir():
                    return str(parent)
            parent = resolved_p.parent
            if parent.is_dir():
                return str(parent)
    root = (collection_root or "").strip()
    if root and Path(root).is_dir():
        return root
    prefs = (prefs_import_dir or "").strip()
    if prefs and Path(prefs).is_dir():
        return prefs
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
