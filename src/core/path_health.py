"""Check Book Locations — books whose stored path is empty, missing, or incorrect.

Uses ``locate_book_path`` from ``audio_launcher`` (same lookup as Listen).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Iterator, List, Optional

from src.core.library_root import locate_book_under_collection, path_is_under_root

STATUS_EMPTY = "Empty"
STATUS_MISSING = "Missing"
STATUS_INCORRECT = "Incorrect"
STATUS_RESOLVED = "Resolved"
STATUS_OK = "OK"

# Filter combo data values.
# Labels: Author not found / Book not found / Incorrect / All.
# Resolved books are corrected during the scan, so no filter lists them.
# FILTER_MISSING stays for callers that want every not-found row.
FILTER_AUTHOR = "author"
FILTER_BOOK = "book"
FILTER_MISSING = "missing"
FILTER_INCORRECT = "incorrect"
FILTER_ALL = "all"

# Why a not-found or incorrect row is in the list.
PROBLEM_AUTHOR = "author"
PROBLEM_BOOK = "book"
PROBLEM_COLLECTION = "collection"
PROBLEM_INCORRECT = "incorrect"

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
    # author, book, collection, or incorrect. Empty for OK and Resolved.
    problem: str = ""


@dataclass
class PathHealthCounts:
    """Running totals for progress (Author / Book / Incorrect / Resolved / Valid)."""

    author_not_found: int = 0
    book_not_found: int = 0
    incorrect: int = 0
    resolved: int = 0
    valid: int = 0
    processed: int = 0

    def record(self, status: str, problem: str = "") -> None:
        self.processed += 1
        if status in _MISSING_STATUSES:
            if problem == PROBLEM_AUTHOR:
                self.author_not_found += 1
            else:
                self.book_not_found += 1
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
            f"Author not found {self.author_not_found} | "
            f"Book not found {self.book_not_found} | "
            f"Corrected {self.resolved} | "
            f"Incorrect {self.incorrect} | Valid {self.valid}"
        )


@dataclass(frozen=True)
class _PathCheck:
    status: str
    resolved_path: str = ""
    reason: str = ""
    problem: str = ""


def _miss_wording(
    code: str,
    *,
    author: str,
    browse_dir: str,
    fallback: str,
) -> tuple[str, str]:
    """Path Health error sentence and filter problem for a miss.

    Listen keeps its own sentences. These are only for Check Book Locations.
    Series-folder misses use the Book not found filter, with their own sentence.
    A missing or unset collection folder is its own problem and is listed under All.
    """
    author_name = (author or "").strip()
    looked = (browse_dir or "").strip()
    if code == "author_not_found":
        if looked:
            return PROBLEM_AUTHOR, f"Author not found in {looked}"
        return PROBLEM_AUTHOR, "Author not found in the collection folder"
    if code == "series_not_found":
        if author_name and looked:
            return PROBLEM_BOOK, f"Series not found in author {author_name} - {looked}"
        if author_name:
            return PROBLEM_BOOK, f"Series not found in author {author_name}"
        return PROBLEM_BOOK, "Series not found in the author folder"
    if code == "book_not_found":
        if author_name and looked:
            return PROBLEM_BOOK, f"Book not found in author {author_name} - {looked}"
        if author_name:
            return PROBLEM_BOOK, f"Book not found in author {author_name}"
        return PROBLEM_BOOK, "Book not found"
    if code in ("collection_missing", "collection_not_set"):
        return PROBLEM_COLLECTION, fallback or "Collection folder is missing"
    if author_name and looked:
        return PROBLEM_BOOK, f"Book not found in author {author_name} - {looked}"
    return PROBLEM_BOOK, fallback or "Book not found"


def _classify_book_path(
    path: str | None,
    collection_root: str = "",
    import_dir: str = "",
    *,
    author_name: str = "",
    book_title: str = "",
    series_name: str = "",
    collection_name: str = "",
    series_number=None,
) -> _PathCheck:
    from src.core.audio_launcher import locate_book_path, path_has_playable_audio

    text = (path or "").strip()
    root = (collection_root or "").strip()

    def check_on_disk(on_disk: str) -> _PathCheck:
        if root and not path_is_under_root(on_disk, root):
            # Found under the collection folder: fix the path instead of listing it.
            found = locate_book_under_collection(
                root,
                author_name,
                book_title,
                series_name,
                collection_name=collection_name,
                series_number=series_number,
            ).path
            if found:
                return _PathCheck(STATUS_RESOLVED, resolved_path=found)
            # Listen plays this path. Do not list it as Incorrect.
            if path_has_playable_audio(on_disk):
                return _PathCheck(STATUS_OK)
            return _PathCheck(STATUS_INCORRECT, problem=PROBLEM_INCORRECT)
        return _PathCheck(STATUS_OK)

    if text and Path(text).exists():
        return check_on_disk(text)

    location = locate_book_path(
        text,
        root,
        (import_dir or "").strip(),
        author_name,
        book_title,
        series_name,
        collection_name=collection_name,
        series_number=series_number,
    )
    if location.path and not location.found_path:
        # The stored path was remapped onto the current folder (for example a
        # USB drive with a new letter). Keep it as stored so it stays portable.
        return check_on_disk(location.path)
    if location.path:
        return _PathCheck(STATUS_RESOLVED, resolved_path=location.path)
    problem, reason = _miss_wording(
        location.code,
        author=author_name,
        browse_dir=location.browse_dir,
        fallback=location.error,
    )
    return _PathCheck(
        STATUS_EMPTY if not text else STATUS_MISSING,
        reason=reason,
        problem=problem,
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
    - Resolved: the stored path is blank, gone, or outside the collection
      folder, but the book is found under the collection folder
    - Incorrect: the stored path exists outside the collection folder, Listen
      cannot play it, and the book is not found under the collection folder
    - OK: Listen can play the stored path, including when that path is outside
      the collection folder, or the path maps onto the collection folder (for
      example a USB drive with a new letter); the stored path is kept
    """
    return _classify_book_path(path, collection_root, import_dir, **lookup).status


def sort_path_health_rows(rows: Iterable[PathHealthRow]) -> List[PathHealthRow]:
    """Stable sort for display: author, then title (case-insensitive)."""
    return sorted(
        rows,
        key=lambda row: (
            (row.author or "").casefold(),
            (row.title or "").casefold(),
        ),
    )


def row_matches_filter(status: str, filter_key: str, problem: str = "") -> bool:
    """True when a row belongs in the chosen filter.

    - author: the author folder was not found in the collection folder
    - book: the author folder was found and the book was not, including a
      missing series folder, a blank path, or a stored path that is gone
    - incorrect: stored path exists off the collection folder and Listen cannot play it
    - all: every problem (not OK, not Resolved)
    - missing: every not-found row (author, book, and collection folder)
    """
    key = (filter_key or FILTER_ALL).strip().casefold()
    if key == FILTER_ALL:
        return status in _PROBLEM_STATUSES
    if key == FILTER_AUTHOR:
        return problem == PROBLEM_AUTHOR
    if key == FILTER_BOOK:
        return problem == PROBLEM_BOOK
    if key == FILTER_INCORRECT:
        return status == STATUS_INCORRECT
    if key == FILTER_MISSING:
        return status in _MISSING_STATUSES
    return False


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
        series_number=getattr(book, "series_number", None),
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
        problem=check.problem,
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
        filter_key: author | book | incorrect | all | missing.
            ``all`` means every problem, not OK or Resolved books.
            ``missing`` means every not-found row.
    """
    rows: List[PathHealthRow] = []
    for row in iter_book_path_checks(
        books,
        collection_root=collection_root,
        collection_roots=collection_roots,
        import_dir=import_dir,
    ):
        if row_matches_filter(row.status, filter_key, row.problem):
            rows.append(row)
    return sort_path_health_rows(rows)


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
