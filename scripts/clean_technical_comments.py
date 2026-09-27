r"""
One-time script: remove iTunes technical tag data from book comments.

Older imports copied iTunes technical tags into Comments: hex blocks
(iTunNORM, iTunSMPB), CD database IDs (iTunes_CDDB_1, iTunes_CDDB_IDs), and
bare track numbers. Import no longer saves them. This script cleans books
that are already in the library:
  - Only comments that contain a hex block or a CD database ID are changed.
  - Real text (plots, notes, reader lines) is kept.
  - Empty and repeated pieces left behind are dropped.
  - A comment with nothing else becomes empty.

Close AbCS before running (--apply) to avoid SQLite lock errors.

Preview (dry-run, default):
  python scripts/clean_technical_comments.py

Apply updates (backs up abcs.db first):
  python scripts/clean_technical_comments.py --apply

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

from src.core.comment_cleanup import clean_comment_text  # noqa: E402

SAMPLE_LINES = 20
PREVIEW_CHARS = 80


def backup_database(db_path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = db_path.with_name(f"{db_path.stem}.bak.{stamp}{db_path.suffix}")
    shutil.copy2(db_path, backup_path)
    return backup_path


def _preview(text: str) -> str:
    flat = " ".join((text or "").split())
    if not flat:
        return "(empty)"
    if len(flat) > PREVIEW_CHARS:
        return flat[:PREVIEW_CHARS] + "..."
    return flat


def print_sample(label: str, lines: List[str]) -> None:
    if not lines:
        return
    print(f"\n{label} (showing up to {SAMPLE_LINES}):")
    for line in lines[:SAMPLE_LINES]:
        print(f"  {line}")
    if len(lines) > SAMPLE_LINES:
        print(f"  ... and {len(lines) - SAMPLE_LINES} more")


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
    cursor.execute(
        "SELECT b.book_id, b.title, a.name AS author, b.comments "
        "FROM books b LEFT JOIN authors a ON a.author_id = b.author_id "
        "WHERE b.comments IS NOT NULL AND b.comments <> '' "
        "ORDER BY b.book_id"
    )
    rows = cursor.fetchall()
    print(f"Database: {len(rows)} book(s) with comments")

    if not dry_run:
        backup = backup_database(db_path)
        print(f"Backup created: {backup}")

    updates: List[str] = []
    emptied = 0
    removed_chars = 0
    for row in rows:
        before = row["comments"] or ""
        after = clean_comment_text(before)
        if after == before:
            continue
        removed_chars += len(before) - len(after)
        if not after:
            emptied += 1
        updates.append(
            f"book_id={row['book_id']} | {row['title']} | {row['author'] or ''} | "
            f"{len(before)} -> {len(after)} chars | now: {_preview(after)}"
        )
        if not dry_run:
            cursor.execute(
                "UPDATE books SET comments = ? WHERE book_id = ?",
                (after, row["book_id"]),
            )

    if not dry_run:
        conn.commit()
    conn.close()

    print(f"{'Would clean' if dry_run else 'Cleaned'}: {len(updates)} book(s)")
    print(f"Comments left empty: {emptied}")
    print(f"Characters removed: {removed_chars}")
    print_sample("Cleaned" if not dry_run else "Would clean", updates)

    if report_path is not None:
        with report_path.open("w", encoding="utf-8") as report:
            report.write("Technical tag data removed from comments\n")
            report.write(f"DB: {db_path}\n")
            report.write(f"Dry run: {dry_run}\n")
            report.write(f"Books: {len(updates)}\n")
            report.write(f"Comments left empty: {emptied}\n")
            report.write(f"Characters removed: {removed_chars}\n\n")
            for line in updates:
                report.write(line + "\n")
        print(f"\nFull report written to: {report_path}")

    if dry_run:
        print("\nDRY RUN - no changes written. Use --apply to commit.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Remove iTunes technical tag data from book comments."
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
