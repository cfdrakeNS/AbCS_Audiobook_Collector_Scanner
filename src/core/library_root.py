"""Collection library root folder checks (Phase 11 Part A)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path, PurePath, PureWindowsPath
from typing import Callable, Iterable

from src.core.tag_reader import TagReader
from src.utils.text_utils import series_number_key, split_series_number


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

    rel_parts = _stored_parts(stored_text)
    if not rel_parts:
        return str(root)

    root_name = root.name
    if root_name:
        for index, part in enumerate(rel_parts):
            if part.casefold() == root_name.casefold():
                suffix = rel_parts[index + 1 :]
                found = _join_ignore_case(root, suffix)
                if found is not None:
                    return str(found)
                return str(root.joinpath(*suffix)) if suffix else str(root)

    for start in range(len(rel_parts)):
        found = _join_ignore_case(root, rel_parts[start:])
        if found is not None:
            return str(found)

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


def _join_ignore_case(root: Path, parts: Iterable[str]) -> Path | None:
    """Existing path under ``root`` for these folder and file names, ignoring case."""
    current = root
    for part in parts:
        exact = current / part
        if path_exists(exact):
            current = exact
            continue
        key = part.casefold()
        children = _list_children(current)
        if children is None:
            return None
        match = next(
            (child for child in children if child.name.casefold() == key),
            None,
        )
        if match is None:
            return None
        current = match
    return current


_WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:")


def _stored_parts(text: str) -> tuple[str, ...]:
    """Folder names after the drive or root, for a path saved on Windows or Linux.

    Linux does not split ``F:\\Books\\Author`` on backslashes, so Windows-style
    paths are parsed as Windows paths on every system.
    """
    if "\\" in text or _WINDOWS_DRIVE_RE.match(text):
        return _parts_after_drive(PureWindowsPath(text))
    return _parts_after_drive(Path(text))


def _parts_after_drive(path: PurePath) -> tuple[str, ...]:
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
_NAME_STRIP_CHARS = '<>:"/\\|?*'


def _name_key(name: str) -> str:
    """Folder/file name compare key: case-insensitive, ignores filename-illegal characters."""
    text = "".join(ch for ch in (name or "") if ch not in _NAME_STRIP_CHARS)
    return " ".join(text.casefold().split())


_DIR_LIST_CACHE: dict[tuple, tuple[Path, ...]] = {}
_DIR_LIST_CACHE_LIMIT = 512


def _list_children(parent: Path) -> list[Path] | None:
    """Names in one folder, kept until that folder's timestamp changes.

    Check Book Locations looks up many books under the same author folder.
    Listing that folder once per book is what made a long scan get slower.
    """
    try:
        stat = parent.stat()
    except OSError:
        return None
    key = (str(parent), getattr(stat, "st_mtime_ns", stat.st_mtime))
    cached = _DIR_LIST_CACHE.get(key)
    if cached is not None:
        return list(cached)
    try:
        children = tuple(parent.iterdir())
    except OSError:
        return None
    _DIR_LIST_CACHE[key] = children
    if len(_DIR_LIST_CACHE) > _DIR_LIST_CACHE_LIMIT:
        _DIR_LIST_CACHE.pop(next(iter(_DIR_LIST_CACHE)))
    return list(children)


def _child_dir(parent: Path, name: str) -> Path | None:
    key = _name_key(name)
    if not key:
        return None
    children = _list_children(parent)
    if children is None:
        return None
    for child in children:
        if child.is_dir() and _name_key(child.name) == key:
            return child
    return None


def _audio_extensions() -> set[str]:
    return {ext.lower() for ext in TagReader.SUPPORTED_EXTENSIONS}


# "4 Bad Blood", "1-  Postmortem", "6 - Title", "6.5 - Title", "01. Title"
_LEADING_INDEX_RE = re.compile(r"^(\d+(?:\.\d+)?)(?:\s*[-.:_]\s*|\s+)(?=\S)")
# "(Quantum Touch 02)", "[Book 2]", "(#2)", "(02)" at the end of a name
_SERIES_TAG_RE = re.compile(
    r"\s*[\(\[]\s*(?:[^()\[\]]*?\s)?#?\s*(\d+(?:\.\d+)?)\s*[\)\]]\s*$"
)
# "(Unabridged)", "[Abridged]": a trailing tag with no number
_PLAIN_TAG_RE = re.compile(r"\s*[\(\[][^()\[\]\d]*[\)\]]\s*$")


def _strip_plain_tag(text: str) -> str:
    """Remove trailing bracket tags that hold no number; keep the text if nothing is left."""
    clean = (text or "").strip()
    while True:
        tag = _PLAIN_TAG_RE.search(clean)
        if not tag or not clean[: tag.start()].strip():
            return clean
        clean = clean[: tag.start()].strip()


def _split_name_index(name: str) -> tuple[str, tuple[str, ...]]:
    """Split a folder or file name into (title part, series indexes).

    Handles a trailing series tag (``Title(Saga 02)``, ``Title [Book 2]``),
    then a leading index (``03 - Title``, ``4 Title``) or a trailing one
    (``Title - 03``, ``Title #3``). Indexes is empty when there is none.
    """
    text = _strip_plain_tag(name)
    indexes: list[str] = []
    tag = _SERIES_TAG_RE.search(text)
    if tag and text[: tag.start()].strip():
        text = text[: tag.start()].strip()
        indexes.append(tag.group(1))
    match = _LEADING_INDEX_RE.match(text)
    if match:
        return text[match.end():].strip(), (match.group(1), *indexes)
    clean, number = split_series_number(text)
    if number:
        return clean, (number, *indexes)
    return text, tuple(indexes)


def _pick_title_match(
    entries: Iterable[Path],
    title: str,
    series_number=None,
    *,
    name_of: Callable[[Path], str],
    usable: Callable[[Path], bool],
) -> Path | None:
    """Pick the entry whose name is the title, allowing a series index on either side.

    An exact name always wins. Otherwise names with an index are compared on
    the title part. When the book has a series number, only that index (or no
    index) is accepted. Without one, a single match is accepted and several
    numbered matches are left alone rather than guessed. A trailing tag with no
    number, such as ``(Unabridged)``, is ignored on both sides; a single such
    match is used before numbered ones.
    """
    key = _name_key(title)
    if not key:
        return None
    base = _strip_plain_tag(title)
    title_clean, title_index = split_series_number(base)
    keys = {key, _name_key(base)}
    if title_index and title_clean:
        keys.add(_name_key(title_clean))
    want = series_number_key(series_number) or series_number_key(title_index)

    loose: list[Path] = []
    candidates: list[tuple[Path, set[str]]] = []
    for entry in entries:
        name = name_of(entry)
        if _name_key(name) == key:
            if usable(entry):
                return entry
            continue
        if _name_key(_strip_plain_tag(name)) in keys:
            if usable(entry):
                loose.append(entry)
            continue
        stem, indexes = _split_name_index(name)
        if indexes and _name_key(stem) in keys and usable(entry):
            candidates.append((entry, {series_number_key(i) for i in indexes}))

    if loose:
        return loose[0] if len(loose) == 1 else None
    if want:
        same = [entry for entry, found in candidates if want in found]
        return same[0] if len(same) == 1 else None
    return candidates[0][0] if len(candidates) == 1 else None


def _child_dirs(parent: Path) -> list[Path]:
    children = _list_children(parent)
    if children is None:
        return []
    return sorted(
        (child for child in children if child.is_dir()),
        key=lambda item: item.name.casefold(),
    )


def _title_child_dir(parent: Path, title: str, series_number=None) -> Path | None:
    """Folder under ``parent`` for this title that holds audio, or None."""
    return _pick_title_match(
        _child_dirs(parent),
        title,
        series_number,
        name_of=lambda item: item.name,
        usable=lambda item: folder_has_supported_audio(str(item)),
    )


def _title_file(parent: Path, title: str, series_number=None) -> Path | None:
    extensions = _audio_extensions()
    children = _list_children(parent)
    if children is None:
        return None
    files = sorted(
        (
            child
            for child in children
            if child.is_file() and child.suffix.lower() in extensions
        ),
        key=lambda item: item.name.casefold(),
    )
    return _pick_title_match(
        files,
        title,
        series_number,
        name_of=lambda item: item.stem,
        usable=lambda _item: True,
    )


def _title_in_subfolders(
    author_dir: Path, title: str, series_number=None
) -> Path | None:
    """Title folder or file one level down (e.g. an unnamed series folder); only a single match counts."""
    hits = []
    for sub in _child_dirs(author_dir):
        found = _title_child_dir(sub, title, series_number) or _title_file(
            sub, title, series_number
        )
        if found is not None:
            hits.append(found)
            if len(hits) > 1:
                return None
    return hits[0] if hits else None


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
    # author_not_found, book_not_found, series_not_found, collection_missing.
    # Listen keeps ``message``. Check Book Locations uses ``code`` for its filter.
    code: str = ""


def locate_book_under_collection(
    collection_root: str,
    author_name: str,
    book_title: str,
    series_name: str = "",
    collection_name: str = "",
    series_number=None,
) -> CollectionLookup:
    """Find a book's folder or file under the collection folder.

    Fixed order, independent of the import scenario: the author folder, then
    (when the book has a series) the series folder under the author. In each,
    a title folder that holds audio wins over a single title audio file. Only
    the collection folder's top level, the author folder, and the series
    folder are listed; the library tree is not scanned.
    Title folders may carry a series index (``03 - Title``, ``Title - 03``).
    When the book has no series, one level of subfolders under the author is
    also checked, and only a single match counts.
    """
    root_text = (collection_root or "").strip()
    author = (author_name or "").strip()
    title = (book_title or "").strip()
    series = (series_name or "").strip()
    if not root_text or not author:
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
            ),
            code="collection_missing",
        )
    author_dir = _child_dir(root, author)
    if author_dir is None:
        return CollectionLookup(
            message=f'Author folder "{author}" was not found in {where} - {root}.',
            browse_dir=str(root),
            code="author_not_found",
        )

    series_dir = _child_dir(author_dir, series) if series else None

    def title_in(parent: Path, skip: Path | None = None) -> Path | None:
        if not title:
            return None
        found = _title_child_dir(parent, title, series_number)
        # Series named like the book: the series folder holds audio in its
        # book folders, so it would match as the book itself.
        if found is not None and skip is not None and found == skip:
            found = None
        if found is None:
            found = _title_file(parent, title, series_number)
        return found

    def title_missing(parent: Path) -> CollectionLookup:
        return CollectionLookup(
            message=(
                f'Author folder found. Book title "{title}" was not found '
                f"in {where} - {parent}."
            ),
            browse_dir=str(parent),
            code="book_not_found",
        )

    def series_missing() -> CollectionLookup:
        return CollectionLookup(
            message=(
                f'Author folder found. Series folder "{series}" was not found '
                f"in {where} - {author_dir}."
            ),
            browse_dir=str(author_dir),
            code="series_not_found",
        )

    found = title_in(author_dir, skip=series_dir)
    if found is not None:
        return CollectionLookup(path=str(found))
    if series:
        if series_dir is None:
            return series_missing()
        found = title_in(series_dir)
        return CollectionLookup(path=str(found)) if found else title_missing(series_dir)
    if title:
        found = _title_in_subfolders(author_dir, title, series_number)
        if found is not None:
            return CollectionLookup(path=str(found))
    return title_missing(author_dir)


def find_book_under_collection(
    collection_root: str,
    author_name: str,
    book_title: str,
    series_name: str = "",
    series_number=None,
) -> str:
    """Return the matched folder or file path, or ``""`` on a miss."""
    return locate_book_under_collection(
        collection_root,
        author_name,
        book_title,
        series_name,
        series_number=series_number,
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
