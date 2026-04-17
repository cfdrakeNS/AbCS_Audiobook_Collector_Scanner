r"""
Script to fix book titles with ", The" at the end.
Moves the article to the beginning of the title.
Only processes books in collection_id = 3.

## How to Run
**Preview changes (dry-run - recommended first):**
cd c:\Users\cfran\PythonProjects\abcs
python scripts\fix_title_articles.py

**Apply changes to database:**
cd c:\Users\cfran\PythonProjects\abcs
python scripts\fix_title_articles.py --apply
"""

import sqlite3
import sys
from pathlib import Path


def fix_title_articles(db_path: str, dry_run: bool = True):
    """
    Update book titles by moving ', The' from end to beginning.

    Args:
        db_path: Path to the SQLite database file
        dry_run: If True, only preview changes without applying them
    """
    if not Path(db_path).exists():
        print(f"ERROR: Database not found: {db_path}")
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Find all books with ", The" at the end of title in collection_id = 3
    cursor.execute("""
        SELECT book_id, title 
        FROM books 
        WHERE title LIKE '%, The' 
        AND collection_id = 3
    """)

    books_to_fix = cursor.fetchall()

    if not books_to_fix:
        print("No books found with ', The' at end of title in collection_id = 3")
        conn.close()
        return

    print(f"Found {len(books_to_fix)} book(s) to update:\n")

    updated_count = 0

    for book_id, old_title in books_to_fix:
        # Remove ", The" from end and add "The " to beginning
        new_title = "The " + old_title[:-5]  # Remove last 5 chars (", The")

        print(f"Book ID {book_id}:")
        print(f"  OLD: {old_title}")
        print(f"  NEW: {new_title}")

        if not dry_run:
            cursor.execute(
                "UPDATE books SET title = ? WHERE book_id = ?", (new_title, book_id)
            )
            updated_count += 1
            print(f"  [UPDATED]")
        else:
            print(f"  [DRY RUN - not updated]")

        print()

    if dry_run:
        print(f"\nDRY RUN completed. {len(books_to_fix)} book(s) would be updated.")
        print("To apply changes, run with: fix_title_articles(db_path, dry_run=False)")
    else:
        conn.commit()
        print(f"\nSUCCESS: {updated_count} book(s) updated.")

    conn.close()


def main():
    """Main entry point for command line usage."""
    # Default database path
    db_path = Path(__file__).parent.parent / "data" / "abcs.db"

    # Check for --apply flag first
    dry_run = "--apply" not in sys.argv

    # Check for command line arguments
    args = [arg for arg in sys.argv[1:] if arg != "--apply"]

    if args:
        if args[0] in ("--help", "-h"):
            print("Usage: python fix_title_articles.py [db_path] [--apply]")
            print("\nOptions:")
            print("  db_path    Path to database (default: ../data/abcs.db)")
            print("  --apply    Apply changes (default is dry-run)")
            sys.exit(0)

        db_path = args[0]

    if dry_run:
        print("=" * 60)
        print("DRY RUN MODE - Previewing changes only")
        print("Add --apply to execute the updates")
        print("=" * 60)
        print()
    else:
        print("=" * 60)
        print("APPLYING CHANGES")
        print("=" * 60)
        print()

    fix_title_articles(str(db_path), dry_run=dry_run)


if __name__ == "__main__":
    main()
