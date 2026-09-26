"""Check Books Path — books whose stored path is empty, missing, or incorrect."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Iterator, List, Optional

from src.core.library_root import path_is_under_root, resolve_book_location

STATUS_EMPTY = "Empty"
STATUS_MISSING = "Missing"
STATUS_INCORRECT = "Incorrect"
STATUS_OK = "OK"

# Filter combo data values (UI labels: Missing / Incorrect / All)
FILTER_MISSING = "missing"
FILTER_INCORRECT = "incorrect"
FILTER_ALL = "all"

_MISSING_STATUSES = frozenset({STATUS_EMPTY, STATUS_MISSING})
_INCORRECT_ONLY = frozenset({STATUS_INCORRECT})
_PROBLEM_STATUSES = frozenset({STATUS_EMPTY, STATUS_MISSING, STATUS_INCORRECT})


@dataclass(frozen=True)
class PathHealthRow:
    """One book path check result for Check Books Path."""

    book_id: int
    author: str
    title: str
    path: str
    status: str
    collection_id: Optional[int] = None
    collection_name: str = ""
    resolved_path: str = ""


@dataclass
class PathHealthCounts:
    """Running totals for progress (Missing / Incorrect / Valid)."""

    missing: int = 0
    incorrect: int = 0
    valid: int = 0
    processed: int = 0

    def record(self, status: str) -> None:
        self.processed += 1
        if status in _MISSING_STATUSES:
            self.missing += 1
        elif status == STATUS_INCORRECT:
            self.incorrect += 1
        elif status == STATUS_OK:
            self.valid += 1


def check_book_path(
    path: str | None,
    collection_root: str = "",
    import_dir: str = "",
) -> str:
    """Return Empty, Missing, Incorrect, or OK for a stored book path.

    Uses the same location resolve as Play: when the stored path is gone,
    remap under the collection library root or Preferences import folder.

    - Empty: no stored path (cannot play)
    - Missing: no existing location after that resolve (cannot play)
    - Incorrect: playable, but stored path is blank of meaning — either the
      stored path is gone and only the remapped location works, or the stored
      path exists but is not under the collection library root
    - OK: stored path exists (and under root when a root is set)
    """
    text = (path or "").strip()
    if not text:
        return STATUS_EMPTY

    root = (collection_root or "").strip()
    prefs = (import_dir or "").strip()
    stored_exists = Path(text).exists()
    resolved = resolve_book_location(text, root, prefs)
    resolved_exists = bool(resolved) and Path(resolved).exists()

    if not resolved_exists:
        return STATUS_MISSING

    if stored_exists:
        if root and not path_is_under_root(text, root):
            return STATUS_INCORRECT
        return STATUS_OK

    # Stored path is stale; Play finds it via root/import remap.
    return STATUS_INCORRECT


def row_matches_filter(status: str, filter_key: str) -> bool:
    """True when a row status belongs in the chosen filter.

    - missing: blank path or not playable after Play-style resolve
    - incorrect: playable via remap or off library root
    - all: every invalid path (missing and incorrect; not OK)
    """
    key = (filter_key or FILTER_MISSING).strip().casefold()
    if key == FILTER_ALL:
        return status in _PROBLEM_STATUSES
    if key == FILTER_MISSING:
        return status in _MISSING_STATUSES
    return status in _INCORRECT_ONLY


def build_path_health_row(
    book,
    *,
    collection_root: str = "",
    import_dir: str = "",
) -> PathHealthRow | None:
    """Build one check row for a book, or None when book_id is missing."""
    book_id = getattr(book, "book_id", None)
    if book_id is None:
        return None
    path = getattr(book, "path", "") or ""
    path_text = path.strip() if isinstance(path, str) else str(path or "")
    status = check_book_path(path_text, collection_root, import_dir)
    resolved = ""
    if path_text:
        resolved = resolve_book_location(path_text, collection_root, import_dir)
    return PathHealthRow(
        book_id=int(book_id),
        author=getattr(book, "author_name", "") or "",
        title=getattr(book, "title", "") or "",
        path=path_text,
        status=status,
        collection_id=getattr(book, "collection_id", None),
        collection_name=getattr(book, "collection_name", "") or "",
        resolved_path=resolved if resolved != path_text else "",
    )


def _root_for_book(
    book,
    *,
    collection_root: str = "",
    collection_roots: dict | None = None,
) -> str:
    """Pick library root for one book (per-collection map when scanning All)."""
    if collection_roots is not None:
        cid = getattr(book, "collection_id", None)
        if cid is None:
            return ""
        return (collection_roots.get(int(cid), "") or "").strip()
    return (collection_root or "").strip()


def iter_book_path_checks(
    books: Iterable,
    *,
    collection_root: str = "",
    collection_roots: dict | None = None,
    import_dir: str = "",
    cancel_check: Callable[[], bool] | None = None,
) -> Iterator[PathHealthRow]:
    """Yield one path-check row per book (all statuses, including OK).

    ``collection_roots`` maps collection_id → root_path for All-collections scans.
    ``cancel_check`` returning True stops before the next book.
    """
    for book in books:
        if cancel_check is not None and cancel_check():
            return
        root = _root_for_book(
            book,
            collection_root=collection_root,
            collection_roots=collection_roots,
        )
        row = build_path_health_row(
            book,
            collection_root=root,
            import_dir=import_dir,
        )
        if row is not None:
            yield row


def scan_book_paths(
    books: Iterable,
    *,
    collection_root: str = "",
    collection_roots: dict | None = None,
    import_dir: str = "",
    filter_key: str = FILTER_MISSING,
) -> List[PathHealthRow]:
    """Scan books and return path check rows for the filter.

    Args:
        books: Iterable of book-like objects with book_id, title, path,
            author_name, collection_id, collection_name.
        collection_root: Collection library root (Play remap + Incorrect).
        collection_roots: Optional map of collection_id → root for All scans.
        import_dir: Preferences import folder (Play remap fallback).
        filter_key: missing | incorrect | all (default missing).
            ``all`` means every invalid path, not OK books.
    """
    rows: List[PathHealthRow] = []
    for row in iter_book_path_checks(
        books,
        collection_root=collection_root,
        collection_roots=collection_roots,
        import_dir=import_dir,
    ):
        if row_matches_filter(row.status, filter_key):
            rows.append(row)
    return rows


def summarize_statuses(rows: Iterable[PathHealthRow]) -> dict[str, int]:
    """Count rows by status label."""
    counts = {
        STATUS_EMPTY: 0,
        STATUS_MISSING: 0,
        STATUS_INCORRECT: 0,
        STATUS_OK: 0,
    }
    for row in rows:
        if row.status in counts:
            counts[row.status] += 1
        else:
            counts[row.status] = counts.get(row.status, 0) + 1
    return counts
