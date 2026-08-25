r"""
One-time script: update series_id and title suffix from Audio_book_catalog_mp3.csv.

Matches DB books to catalog rows by author + title (fuzzy). On match:
  - sets books.series_id from CSV Series column
  - sets title to "{base_title} - {NN}" (series number zero-padded to 2 digits)

Close AbCS before running (--apply) to avoid SQLite lock errors.

Preview (dry-run, default):
  python scripts/update_series_from_catalog.py

Apply updates (backs up abcs.db first):
  python scripts/update_series_from_catalog.py --apply

Options:
  --csv PATH       Catalog CSV (default: data/Audio_book_catalog_mp3.csv)
  --db PATH        Database (default: data/abcs.db)
  --threshold N    Fuzzy match percent 0-100 (default: 90)
  --report PATH    Write full unmatched/ambiguous log
"""

from __future__ import annotations

import argparse
import csv
import io
import re
import shutil
import sqlite3
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.utils.text_utils import (  # noqa: E402
    normalize_author,
    normalize_title,
    similarity_percentage,
)

SERIES_STRIP_PATTERNS = [
    r"^(.*?)\s*-\s*(\d+)$",
    r"^(.*?)\s*#\s*(\d+)$",
    r"^(.*?)\s+Book\s*(\d+)$",
    r"^(.*?)\s+Volume\s*(\d+)$",
    r"^(.*?)\s*,\s*(\d+)$",
]

AMBIGUITY_TITLE_GAP = 1.0
SAMPLE_LINES = 20


@dataclass
class CatalogEntry:
    author: str
    title: str
    base_title: str
    series: str
    series_no: str
    norm_author: str
    norm_title: str
    formatted_suffix: str


@dataclass
class MatchResult:
    entry: CatalogEntry
    title_similarity: float
    author_similarity: float
    exact_title: bool


def strip_series_number(title: str) -> Tuple[str, str]:
    """Return (base_title, series_number) using the same rules as WebBookAPI."""
    if not title:
        return "", ""
    text = title.strip()
    for pattern in SERIES_STRIP_PATTERNS:
        match = re.match(pattern, text, re.IGNORECASE)
        if match:
            clean_title = match.group(1).strip()
            series_number = match.group(2)
            if clean_title:
                return clean_title, series_number
    return text, ""


def format_suffix(series_no: str) -> str:
    digits = re.sub(r"[^\d]", "", (series_no or "").strip())
    return digits.zfill(2) if digits else ""


def build_title(base_title: str, suffix: str) -> str:
    return f"{base_title} - {suffix}".strip()


def flip_author_name(author: str) -> str:
    """Swap 'Last, First' to 'First Last' and vice versa when comma present."""
    author = (author or "").strip()
    if "," not in author:
        return author
    parts = [p.strip() for p in author.split(",", 1)]
    if len(parts) == 2 and parts[0] and parts[1]:
        return f"{parts[1]} {parts[0]}"
    return author


def author_lookup_keys(author: str) -> List[str]:
    keys = []
    for variant in (author, flip_author_name(author)):
        key = normalize_author(variant, aggressive=True)
        if key and key not in keys:
            keys.append(key)
    return keys


def _cell(row: dict, *names: str) -> str:
    for name in names:
        if name in row and row[name] is not None:
            val = str(row[name]).strip()
            if val and val.lower() != "nan":
                return val
    return ""


def _decode_catalog_text(csv_path: Path) -> str:
    """Decode catalog CSV; try UTF-8 then Windows-1252 (common for exported Excel CSV)."""
    raw = csv_path.read_bytes()
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1")


def load_catalog(csv_path: Path) -> Tuple[Dict[str, List[CatalogEntry]], int]:
    """Load CSV and index by aggressive-normalized author key."""
    index: Dict[str, List[CatalogEntry]] = defaultdict(list)
    skipped = 0

    text = _decode_catalog_text(csv_path)
    reader = csv.DictReader(io.StringIO(text, newline=""))
    for row in reader:
        author = _cell(row, "Author", "author")
        title = _cell(row, "Title", "title")
        series = _cell(row, "Series", "series")
        series_no = _cell(row, "Series No", "Series No.", "Series No", "series_no")
        if not author or not title or not series or not series_no:
            skipped += 1
            continue

        base_title, _ = strip_series_number(title)
        suffix = format_suffix(series_no)
        if not suffix:
            skipped += 1
            continue

        entry = CatalogEntry(
            author=author,
            title=title,
            base_title=base_title,
            series=series,
            series_no=series_no,
            norm_author=normalize_author(author, aggressive=True),
            norm_title=normalize_title(base_title, aggressive=True),
            formatted_suffix=suffix,
        )
        for key in author_lookup_keys(author):
            index[key].append(entry)

    return dict(index), skipped


def find_best_match(
    norm_author: str,
    norm_title: str,
    author_name: str,
    catalog_index: Dict[str, List[CatalogEntry]],
    threshold: float,
) -> Tuple[Optional[MatchResult], str]:
    """
    Find best catalog row for a DB book.
    Returns (match, reason) where reason is '' on success or 'ambiguous' / 'unmatched'.
    """
    candidates: List[CatalogEntry] = []
    seen: set = set()

    for key in author_lookup_keys(author_name):
        for entry in catalog_index.get(key, []):
            ident = (entry.author, entry.base_title, entry.series, entry.series_no)
            if ident in seen:
                continue
            seen.add(ident)
            candidates.append(entry)

    if not candidates:
        return None, "unmatched"

    scored: List[MatchResult] = []
    for entry in candidates:
        if entry.norm_title == norm_title:
            scored.append(
                MatchResult(
                    entry=entry,
                    title_similarity=100.0,
                    author_similarity=100.0,
                    exact_title=True,
                )
            )
            continue

        author_sim = similarity_percentage(entry.norm_author, norm_author)
        title_sim = similarity_percentage(entry.norm_title, norm_title)
        if author_sim >= threshold and title_sim >= threshold:
            scored.append(
                MatchResult(
                    entry=entry,
                    title_similarity=title_sim,
                    author_similarity=author_sim,
                    exact_title=False,
                )
            )

    if not scored:
        return None, "unmatched"

    scored.sort(
        key=lambda m: (
            not m.exact_title,
            -m.title_similarity,
            -m.author_similarity,
        )
    )
    best = scored[0]
    if len(scored) > 1:
        second = scored[1]
        if abs(best.title_similarity - second.title_similarity) <= AMBIGUITY_TITLE_GAP:
            if (
                best.entry.base_title != second.entry.base_title
                or best.entry.series != second.entry.series
            ):
                return None, "ambiguous"

    return best, ""


def get_or_create_series_id(
    cursor: sqlite3.Cursor, name: str, *, dry_run: bool = False
) -> int:
    row = cursor.execute(
        "SELECT series_id FROM series WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))",
        (name,),
    ).fetchone()
    if row:
        return int(row[0])
    if dry_run:
        return -1
    cursor.execute("INSERT INTO series (name) VALUES (?)", (name,))
    return int(cursor.lastrowid)


def backup_database(db_path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = db_path.with_name(f"{db_path.stem}.bak.{stamp}{db_path.suffix}")
    shutil.copy2(db_path, backup_path)
    return backup_path


def print_sample(label: str, lines: List[str]) -> None:
    if not lines:
        return
    print(f"\n{label} (showing up to {SAMPLE_LINES}):")
    for line in lines[:SAMPLE_LINES]:
        print(f"  {line}")
    if len(lines) > SAMPLE_LINES:
        print(f"  ... and {len(lines) - SAMPLE_LINES} more")


def run_update(
    csv_path: Path,
    db_path: Path,
    *,
    dry_run: bool = True,
    threshold: float = 90.0,
    report_path: Optional[Path] = None,
) -> int:
    if not csv_path.exists():
        print(f"ERROR: CSV not found: {csv_path}")
        return 1
    if not db_path.exists():
        print(f"ERROR: Database not found: {db_path}")
        return 1

    catalog_index, skipped_csv = load_catalog(csv_path)
    total_csv_indexed = sum(len(v) for v in catalog_index.values())
    print(f"Catalog: indexed {total_csv_indexed} row references, skipped {skipped_csv} rows without series data")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT b.book_id, b.title, b.series_id,
               a.name AS author_name, s.name AS series_name
        FROM books b
        JOIN authors a ON b.author_id = a.author_id
        LEFT JOIN series s ON b.series_id = s.series_id
        """
    )
    db_rows = cursor.fetchall()
    print(f"Database: {len(db_rows)} book(s)")

    updated: List[str] = []
    unchanged: List[str] = []
    unmatched: List[str] = []
    ambiguous: List[str] = []

    if not dry_run:
        backup = backup_database(db_path)
        print(f"Backup created: {backup}")

    changes_applied = 0

    for row in db_rows:
        book_id = row["book_id"]
        db_title = row["title"] or ""
        author_name = row["author_name"] or ""
        db_series_id = row["series_id"]
        db_series_name = row["series_name"] or ""

        base_title, _ = strip_series_number(db_title)
        norm_author = normalize_author(author_name, aggressive=True)
        norm_title = normalize_title(base_title, aggressive=True)

        match, reason = find_best_match(
            norm_author, norm_title, author_name, catalog_index, threshold
        )

        label = f"book_id={book_id} | {author_name} | {db_title}"

        if reason == "ambiguous":
            ambiguous.append(label)
            continue
        if match is None:
            unmatched.append(label)
            continue

        entry = match.entry
        new_series_id = get_or_create_series_id(cursor, entry.series, dry_run=dry_run)
        new_title = build_title(base_title, entry.formatted_suffix)

        if (
            not dry_run
            and db_series_id == new_series_id
            and db_title == new_title
        ) or (
            dry_run
            and db_title == new_title
            and (db_series_name or "").strip().lower()
            == entry.series.strip().lower()
        ):
            unchanged.append(label)
            continue

        detail = (
            f"{label}\n"
            f"    CSV: {entry.title} / {entry.series} #{entry.series_no}\n"
            f"    series: {db_series_name or '(none)'} -> {entry.series}\n"
            f"    title: {db_title} -> {new_title}"
        )
        updated.append(detail)

        if not dry_run:
            cursor.execute(
                "UPDATE books SET title = ?, series_id = ? WHERE book_id = ?",
                (new_title, new_series_id, book_id),
            )
            changes_applied += 1

    if not dry_run:
        conn.commit()

    conn.close()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  updated:   {len(updated)}")
    print(f"  unchanged: {len(unchanged)}")
    print(f"  unmatched: {len(unmatched)}")
    print(f"  ambiguous: {len(ambiguous)}")
    print(f"  skipped CSV rows (no series data): {skipped_csv}")

    if dry_run:
        print("\nDRY RUN — no changes written. Use --apply to commit.")
    else:
        print(f"\nApplied {changes_applied} update(s).")

    print_sample("Updated", updated)
    print_sample("Unmatched", unmatched)
    print_sample("Ambiguous", ambiguous)

    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with report_path.open("w", encoding="utf-8") as report:
            report.write("Series catalog update report\n")
            report.write(f"CSV: {csv_path}\n")
            report.write(f"DB: {db_path}\n")
            report.write(f"Dry run: {dry_run}\n")
            report.write(f"Threshold: {threshold}%\n\n")
            report.write(f"Updated ({len(updated)}):\n")
            for line in updated:
                report.write(line + "\n\n")
            report.write(f"\nUnmatched ({len(unmatched)}):\n")
            for line in unmatched:
                report.write(line + "\n")
            report.write(f"\nAmbiguous ({len(ambiguous)}):\n")
            for line in ambiguous:
                report.write(line + "\n")
            report.write(f"\nUnchanged ({len(unchanged)}):\n")
            for line in unchanged:
                report.write(line + "\n")
        print(f"\nFull report written to: {report_path}")

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Update abcs.db series and title suffixes from catalog CSV."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes (default is dry-run preview only)",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=_REPO_ROOT / "data" / "Audio_book_catalog_mp3.csv",
        help="Path to catalog CSV",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=_REPO_ROOT / "data" / "abcs.db",
        help="Path to SQLite database",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=90.0,
        help="Fuzzy match threshold 0-100 (default: 90)",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Write full log to this file",
    )
    args = parser.parse_args()

    if args.threshold < 0 or args.threshold > 100:
        print("ERROR: --threshold must be between 0 and 100")
        sys.exit(1)

    dry_run = not args.apply
    if dry_run:
        print("=" * 60)
        print("DRY RUN MODE — preview only")
        print("Add --apply to execute updates (creates DB backup first)")
        print("=" * 60)
    else:
        print("=" * 60)
        print("APPLYING CHANGES")
        print("=" * 60)

    print()
    exit_code = run_update(
        args.csv.resolve(),
        args.db.resolve(),
        dry_run=dry_run,
        threshold=args.threshold,
        report_path=args.report.resolve() if args.report else None,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
