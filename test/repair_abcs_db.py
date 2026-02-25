"""Repair and optimize an AbCS database by applying indexes and VACUUM."""

import sqlite3
import sys
from pathlib import Path


def repair_database(db_path: str) -> bool:
    """
    Apply missing indexes and optimize an AbCS database.
    Safe for existing databases—uses CREATE INDEX IF NOT EXISTS.

    Args:
        db_path: Path to the abcs.db file

    Returns:
        True if successful, False otherwise
    """
    try:
        db_path = Path(db_path)
        if not db_path.exists():
            print(f"ERROR: Database not found: {db_path}")
            return False

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        print(f"Repairing database: {db_path}")
        print("Creating indexes...")

        # These are the same indexes created by initialize_database()
        indexes = [
            ("idx_books_author", "books(author_id)"),
            ("idx_books_series", "books(series_id)"),
            ("idx_books_genre", "books(genre_id)"),
            ("idx_books_collection", "books(collection_id)"),
            ("idx_books_title", "books(title)"),
            ("idx_books_collection_title", "books(collection_id, title)"),
            ("idx_books_duplicate_key", "books(title, author_id, year, collection_id)"),
            ("idx_books_read_date", "books(read_date)"),
            ("idx_author_name", "authors(name)"),
            ("idx_genre_name", "genres(name)"),
            ("idx_series_name", "series(name)"),
            ("idx_collection_active_name", "collections(active, name)"),
        ]

        for idx_name, idx_def in indexes:
            try:
                cursor.execute(
                    f"CREATE INDEX IF NOT EXISTS {idx_name} ON {idx_def}")
                print(f"  ✓ {idx_name}")
            except sqlite3.Error as e:
                print(f"  ✗ {idx_name}: {e}")

        print("Analyzing database...")
        cursor.execute("ANALYZE")

        print("Optimizing database (VACUUM)...")
        cursor.execute("VACUUM")

        conn.commit()
        conn.close()

        print("✓ Database repair complete.")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python repair_abcs_db.py <path_to_abcs.db>")
        print("\nThis script applies missing indexes and optimizes an AbCS database.")
        print("Safe to run on existing databases—uses CREATE INDEX IF NOT EXISTS.")
        sys.exit(1)

    db_path = sys.argv[1]
    success = repair_database(db_path)
    sys.exit(0 if success else 1)
