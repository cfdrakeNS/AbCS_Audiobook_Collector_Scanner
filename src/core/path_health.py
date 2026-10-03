"""Check Book Locations — books whose stored path is empty, missing, or incorrect."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Iterator, List, Optional

from src.core.library_root import path_is_under_root, saved_import_scenario

STATUS_EMPTY = "Empty"
STATUS_MISSING = "Missing"
STATUS_INCORRECT = "Incorrect"
STATUS_RESOLVED = "Resolved"
STATUS_OK = "OK"

# Filter combo data values (UI labels: Missing / Incorrect / All).
# Resolved books are corrected during the scan, so no filter lists them.
FILTER_MISSING = "missing"
FILTER_INCORRECT = "incorrect"
FILTER_ALL = "all"

_MISSING_STATUSES = frozenset({STATUS_EMPTY, STATUS_MISSING})
_PROBLEM_STATUSES = frozenset({STATUS_EMPTY, STATUS_MISSING, STATUS_INCORRECT})


@dataclass(frozen=True)
class PathHealthRow:
    """One book path check result for Check Book Locations."""

    book_id: int
    author: str
    title: str
    path: str
    status: str
    collection_id: Optional[int] = None
    collection_name: str = ""
    # Path found when the stored path is blank or wrong.
    resolved_path: str = ""
    # Why the book could not be found (when status is missing or empty).
    reason: str = ""


@dataclass
class PathHealthCounts:
    """Running totals for progress (Missing / Incorrect / Resolved / Valid)."""

    missing: int = 0
    incorrect: int = 0
    resolved: int = 0
    valid: int = 0
    processed: int = 0

    def record(self, status: str) -> None:
        self.processed += 1
        if status in _MISSING_STATUSES:
            self.missing += 1
        elif status == STATUS_INCORRECT:
            self.incorrect += 1
        elif status == STATUS_RESOLVED:
            self.resolved += 1
        elif status == STATUS_OK:
            self.valid += 1

    def summary(self) -> str:
        """Counter text shared by the progress window and the status bar."""
        return (
            f"{self.processed} books scanned: "
            f"Missing {self.missing} | Corrected {self.resolved} | "
            f"Incorrect {self.incorrect} | Valid {self.valid}"
        )


@dataclass(frozen=True)
class _PathCheck:
    status: str
    resolved_path: str = ""
    reason: str = ""


def _classify_book_path(
    path: str | None,
    collection_root: str = "",
    import_dir: str = "",
    *,
    author_name: str = "",
    book_title: str = "",
    series_name: str = "",
    collection_name: str = "",
    import_scenario: str | None = None,
    root_audio_cache: dict | None = None,
) -> _PathCheck:
    from src.core.audio_launcher import locate_book_path

    text = (path or "").strip()
    root = (collection_root or "").strip()
    if text and Path(text).exists():
        if root and not path_is_under_root(text, root):
            return _PathCheck(STATUS_INCORRECT)
        return _PathCheck(STATUS_OK)

    location = locate_book_path(
        text,
        root,
        (import_dir or "").strip(),
        author_name,
        book_title,
        series_name,
        import_scenario,
        collection_name=collection_name,
        root_audio_cache=root_audio_cache,
    )
    if location.path:
        return _PathCheck(STATUS_RESOLVED, resolved_path=location.path)
    return _PathCheck(
        STATUS_EMPTY if not text else STATUS_MISSING, reason=location.error
    )


def check_book_path(
    path: str | None,
    collection_root: str = "",
    import_dir: str = "",
    **lookup,
) -> str:
    """Return Empty, Missing, Resolved, Incorrect, or OK for a stored book path.

    Stored path first, then remap under the collection folder or Preferences
    import folder, then the collection folder layout (author, series, and title
    folders) when ``lookup`` gives the author and title.

    - Empty: no stored path, and the book cannot be found
    - Missing: stored path gone, and the book cannot be found
    - Resolved: the stored path is blank or gone, but the book is found under
      the collection folder
    - Incorrect: the stored path exists but is not under the collection folder
    - OK: stored path exists (and under root when a root is set)
    """
    return _classify_book_path(path, collection_root, import_dir, **lookup).status


def row_matches_filter(status: str, filter_key: str) -> bool:
    """True when a row status belongs in the chosen filter.

    - missing: book cannot be found
    - incorrect: stored path exists but is off the collection folder
    - all: missing and incorrect (not OK, not Resolved)
    """
    key = (filter_key or FILTER_MISSING).strip().casefold()
    if key == FILTER_ALL:
        return status in _PROBLEM_STATUSES
    if key == FILTER_MISSING:
        return status in _MISSING_STATUSES
    return status == STATUS_INCORRECT


def build_path_health_row(
    book,
    *,
    collection_root: str = "",
    import_dir: str = "",
    import_scenario: str | None = None,
    root_audio_cache: dict | None = None,
) -> PathHealthRow | None:
    """Build one check row for a book, or None when book_id is missing."""
    book_id = getattr(book, "book_id", None)
    if book_id is None:
        return None
    path = getattr(book, "path", "") or ""
    path_text = path.strip() if isinstance(path, str) else str(path or "")
    author = getattr(book, "author_name", "") or ""
    title = getattr(book, "title", "") or ""
    collection_name = getattr(book, "collection_name", "") or ""
    check = _classify_book_path(
        path_text,
        collection_root,
        import_dir,
        author_name=author,
        book_title=title,
        series_name=getattr(book, "series_name", "") or "",
        collection_name=collection_name,
        import_scenario=import_scenario,
        root_audio_cache=root_audio_cache,
    )
    return PathHealthRow(
        book_id=int(book_id),
        author=author,
        title=title,
        path=path_text,
        status=check.status,
        collection_id=getattr(book, "collection_id", None),
        collection_name=collection_name,
        resolved_path=check.resolved_path if check.resolved_path != path_text else "",
        reason=check.reason,
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
    scenario = saved_import_scenario()
    root_audio_cache: dict = {}
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
            import_scenario=scenario,
            root_audio_cache=root_audio_cache,
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
            ``all`` means missing and incorrect, not OK or Resolved books.
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
        STATUS_RESOLVED: 0,
        STATUS_INCORRECT: 0,
        STATUS_OK: 0,
    }
    for row in rows:
        if row.status in counts:
            counts[row.status] += 1
        else:
            counts[row.status] = counts.get(row.status, 0) + 1
    return counts
