r"""
One-time script: remove a trailing series number from books.title.

Uses the same suffix rules as Book Details:
  - A number such as 3, 03, or 6.5 is stripped from the title.
  - A blank series_number is filled from that suffix first.
  - A series_number already stored is left as it is.
  - If the stored number and the suffix disagree, the stored number is kept
    and the title is still stripped. Those rows are listed as conflicts.
  - A year such as 1999 stays on the title.

Close AbCS before running (--apply) to avoid SQLite lock errors.

Preview (dry-run, default):
  python scripts/strip_series_suffix_from_titles.py

Apply updates (backs up abcs.db first):
  python scripts/strip_series_suffix_from_titles.py --apply

Options:
  --db PATH      Database (default: data/abcs.db)
  --report PATH  Write the full update list to this file
"""

from __future__ import annotations

import argparse
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.utils.text_utils import (  # noqa: E402
    series_number_for_storage,
    series_number_key,
    split_series_number,
)

SAMPLE_LINES = 20


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


def _column_exists(cursor: sqlite3.Cursor, table: str, column: str) -> bool:
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())


def run_update(
    db_path: Path,
    *,
    dry_run: bool = True,
    report_path: Optional[Path] = None,
) -> int:
    if not db_path.exists():
        print(f"ERROR: Database not found: {db_path}")
        return 1

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if not _column_exists(cursor, "books", "series_number"):
        conn.close()
        print("ERROR: books.series_number is missing.")
        print("Start AbCS once so the database upgrade adds the column, then run this again.")
        return 1

    cursor.execute("SELECT book_id, title, series_number FROM books ORDER BY book_id")
    rows = cursor.fetchall()
    print(f"Database: {len(rows)} book(s)")

    updates: List[str] = []
    conflicts: List[str] = []
    no_suffix = 0

    if not dry_run:
        backup = backup_database(db_path)
        print(f"Backup created: {backup}")

    for row in rows:
        title = row["title"] or ""
        clean, existing = split_series_number(title)
        number = series_number_for_storage(existing)
        if not number or not clean or clean == title:
            no_suffix += 1
            continue

        stored = series_number_for_storage(row["series_number"])
        keep_number = stored or number
        conflict = bool(
            stored
            and series_number_key(stored) != series_number_key(number)
        )
        line = (
            f"book_id={row['book_id']} | series_number={keep_number} | "
            f"{title} -> {clean}"
        )
        if conflict:
            line += f" | kept stored {stored}, title had {number}"
            conflicts.append(line)
        updates.append(line)
        if not dry_run:
            cursor.execute(
                "UPDATE books SET title = ?, series_number = ? WHERE book_id = ?",
                (clean, keep_number, row["book_id"]),
            )

    if not dry_run:
        conn.commit()
    conn.close()

    print(f"No series number on the title: {no_suffix}")
    print(f"{'Would strip' if dry_run else 'Stripped'}: {len(updates)}")
    print(f"Conflicts (kept stored series number): {len(conflicts)}")
    print_sample("Updates" if not dry_run else "Would strip", updates)
    print_sample("Conflicts", conflicts)

    if report_path is not None:
        with report_path.open("w", encoding="utf-8") as report:
            report.write("Strip series number suffix from titles\n")
            report.write(f"DB: {db_path}\n")
            report.write(f"Dry run: {dry_run}\n")
            report.write(f"No series number on the title: {no_suffix}\n")
            report.write(f"Updates: {len(updates)}\n")
            report.write(f"Conflicts: {len(conflicts)}\n\n")
            for line in updates:
                report.write(line + "\n")
            if conflicts:
                report.write("\nConflicts:\n")
                for line in conflicts:
                    report.write(line + "\n")
        print(f"\nFull report written to: {report_path}")

    if dry_run:
        print("\nDRY RUN - no changes written. Use --apply to commit.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Remove a trailing series number from book titles."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes (default is dry-run preview only)",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=_REPO_ROOT / "data" / "abcs.db",
        help="Path to SQLite database",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Write the full update list to this file",
    )
    args = parser.parse_args()

    dry_run = not args.apply
    if dry_run:
        print("=" * 60)
        print("DRY RUN MODE - preview only")
        print("Add --apply to execute updates (creates DB backup first)")
        print("=" * 60)
    else:
        print("=" * 60)
        print("APPLYING CHANGES")
        print("=" * 60)
    print()

    exit_code = run_update(
        args.db.resolve(),
        dry_run=dry_run,
        report_path=args.report.resolve() if args.report else None,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
