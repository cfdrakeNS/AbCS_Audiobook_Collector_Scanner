"""Collection library root folder checks (Phase 11 Part A)."""

from __future__ import annotations

from dataclasses import dataclass
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
IMPORT_SCENARIO_KEY = "import/scenario/mode"
DEFAULT_IMPORT_SCENARIO = "mass_standard"

_NAME_STRIP_CHARS = '<>:"/\\|?*'


def saved_import_scenario() -> str:
    """Return the Preferences import scenario, or Mass Standard when unset."""
    from PySide6.QtCore import QSettings

    settings = QSettings("AbCS", "AudioBookCollector")
    try:
        value = settings.value(IMPORT_SCENARIO_KEY, DEFAULT_IMPORT_SCENARIO, type=str)
    except TypeError:
        value = settings.value(IMPORT_SCENARIO_KEY, DEFAULT_IMPORT_SCENARIO)
    return (value or DEFAULT_IMPORT_SCENARIO).strip() or DEFAULT_IMPORT_SCENARIO


def _name_key(name: str) -> str:
    """Folder/file name compare key: case-insensitive, ignores filename-illegal characters."""
    text = "".join(ch for ch in (name or "") if ch not in _NAME_STRIP_CHARS)
    return " ".join(text.casefold().split())


def _child_dir(parent: Path, name: str) -> Path | None:
    key = _name_key(name)
    if not key:
        return None
    try:
        for child in parent.iterdir():
            if child.is_dir() and _name_key(child.name) == key:
                return child
    except OSError:
        return None
    return None


def _audio_extensions() -> set[str]:
    return {ext.lower() for ext in TagReader.SUPPORTED_EXTENSIONS}


def _title_file(parent: Path, title: str) -> Path | None:
    key = _name_key(title)
    if not key:
        return None
    extensions = _audio_extensions()
    try:
        for child in parent.iterdir():
            if (
                child.is_file()
                and child.suffix.lower() in extensions
                and _name_key(child.stem) == key
            ):
                return child
    except OSError:
        return None
    return None


def _folder_has_direct_audio(folder: Path) -> bool:
    extensions = _audio_extensions()
    try:
        return any(
            child.is_file() and child.suffix.lower() in extensions
            for child in folder.iterdir()
        )
    except OSError:
        return False


@dataclass(frozen=True)
class CollectionLookup:
    """Result of an author/title search under the collection folder.

    ``path`` is set on a match. On a miss, ``message`` says which folder was
    missing and ``browse_dir`` is the closest existing folder to start a
    Browse from. Both stay empty when no search ran.
    """

    path: str = ""
    message: str = ""
    browse_dir: str = ""


def locate_book_under_collection(
    collection_root: str,
    author_name: str,
    book_title: str,
    series_name: str = "",
    scenario: str = DEFAULT_IMPORT_SCENARIO,
    collection_name: str = "",
    root_audio_cache: dict | None = None,
) -> CollectionLookup:
    """Find a book's folder or file under the collection folder by import layout.

    Only the folders named by the scenario are checked; the library tree is
    not scanned. Single-item import has no library layout, so no search runs.
    ``root_audio_cache`` lets a many-book scan check each collection folder for
    audio once instead of once per book.
    """
    root_text = (collection_root or "").strip()
    author = (author_name or "").strip()
    title = (book_title or "").strip()
    series = (series_name or "").strip()
    mode = (scenario or DEFAULT_IMPORT_SCENARIO).strip()
    if not root_text or not author or mode == "single_item":
        return CollectionLookup()
    root = Path(root_text)
    name = (collection_name or "").strip()
    where = f"the {name} collection folder" if name else "the collection folder"
    if not folder_exists(root_text):
        return CollectionLookup(
            message=(
                f"{where[0].upper()}{where[1:]} is missing - {root}. To fix, "
                "open Manage > Collections, edit the collection, "
                "and set the collection folder."
            )
        )
    author_dir = _child_dir(root, author)
    if author_dir is None:
        if root_audio_cache is None:
            root_has_audio = folder_has_supported_audio(root_text)
        else:
            if root_text not in root_audio_cache:
                root_audio_cache[root_text] = folder_has_supported_audio(root_text)
            root_has_audio = root_audio_cache[root_text]
        if not root_has_audio:
            return CollectionLookup(
                message=(
                    f"{where[0].upper()}{where[1:]} has no audiobook files - {root}. "
                    "It may be the wrong folder. To fix, open Manage > Collections, "
                    "edit the collection, and set the collection folder."
                ),
                browse_dir=str(root),
            )
        return CollectionLookup(
            message=f'Author folder "{author}" was not found in {where} - {root}.',
            browse_dir=str(root),
        )

    def title_folder(parent: Path | None) -> Path | None:
        if parent is None or not title:
            return None
        folder = _child_dir(parent, title)
        if folder is not None and folder_has_supported_audio(str(folder)):
            return folder
        return None

    def title_missing(parent: Path) -> CollectionLookup:
        return CollectionLookup(
            message=(
                f'Author folder found. Book title "{title}" was not found '
                f"in {where} - {parent}."
            ),
            browse_dir=str(parent),
        )

    def series_missing() -> CollectionLookup:
        return CollectionLookup(
            message=(
                f'Author folder found. Series folder "{series}" was not found '
                f"in {where} - {author_dir}."
            ),
            browse_dir=str(author_dir),
        )

    series_dir = _child_dir(author_dir, series) if series else None

    if mode == "series_from_directory":
        if series:
            if series_dir is None:
                return series_missing()
            if _folder_has_direct_audio(series_dir):
                return CollectionLookup(path=str(series_dir))
            return title_missing(series_dir)
        found = title_folder(author_dir)
        return CollectionLookup(path=str(found)) if found else title_missing(author_dir)

    if mode == "series_from_directory_nested":
        if series:
            if series_dir is None:
                return series_missing()
            found = title_folder(series_dir)
            return (
                CollectionLookup(path=str(found)) if found else title_missing(series_dir)
            )
        found = title_folder(author_dir)
        return CollectionLookup(path=str(found)) if found else title_missing(author_dir)

    # Mass Standard and Series From File Name.
    found = title_folder(author_dir)
    if found is not None:
        return CollectionLookup(path=str(found))
    if title:
        single = _title_file(author_dir, title)
        if single is not None:
            return CollectionLookup(path=str(single))
    found = title_folder(series_dir)
    if found is not None:
        return CollectionLookup(path=str(found))
    return title_missing(author_dir)


def find_book_under_collection(
    collection_root: str,
    author_name: str,
    book_title: str,
    series_name: str = "",
    scenario: str = DEFAULT_IMPORT_SCENARIO,
) -> str:
    """Return the matched folder or file path, or ``""`` on a miss."""
    return locate_book_under_collection(
        collection_root, author_name, book_title, series_name, scenario
    ).path


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
