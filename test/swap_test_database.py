"""
Safely swap the test database to Wayne's 34k-book database.
Backs up the current database before swapping.
"""

import shutil
import sqlite3
import sys
from pathlib import Path
from datetime import datetime


def check_schema_compatibility(db_path: str) -> dict:
    """Check if Wayne's database has the date_added column."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get table info
        cursor.execute("PRAGMA table_info(books)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}

        # Count books
        cursor.execute("SELECT COUNT(*) FROM books")
        book_count = cursor.fetchone()[0]

        conn.close()

        return {
            "has_date_added": "date_added" in columns,
            "date_added_type": columns.get("date_added", "MISSING"),
            "book_count": book_count,
        }
    except Exception as e:
        return {"error": str(e)}


def swap_database(wayne_db_path: str, test_db_path: str = "data/abcs.db") -> bool:
    """
    Swap test database for Wayne's database.
    Creates backup: data/abcs.db.backup.<timestamp>
    """
    wayne_path = Path(wayne_db_path)
    test_path = Path(test_db_path)

    if not wayne_path.exists():
        print(f"ERROR: Wayne's database not found: {wayne_path}")
        return False

    # Create backup of current test database
    if test_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = test_path.parent / f"{test_path.name}.backup.{timestamp}"
        try:
            shutil.copy2(test_path, backup_path)
            print(f"✓ Backed up current database to: {backup_path}")
        except Exception as e:
            print(f"ERROR backing up: {e}")
            return False

    # Copy Wayne's database to test location
    try:
        shutil.copy2(wayne_path, test_path)
        print(f"✓ Copied Wayne's database to: {test_path}")

        # Verify schema
        schema_info = check_schema_compatibility(str(test_path))
        if "error" in schema_info:
            print(f"WARNING: Could not verify schema: {schema_info['error']}")
        else:
            print(f"  Books in database: {schema_info['book_count']:,}")
            print(f"  Has date_added column: {schema_info['has_date_added']}")
            if schema_info['has_date_added']:
                print(f"  Column type: {schema_info['date_added_type']}")
            else:
                print("  WARNING: date_added column missing! May be older schema.")

        return True
    except Exception as e:
        print(f"ERROR copying database: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python swap_test_database.py <path_to_waynes_34k_db>")
        print("\nExample: python swap_test_database.py C:\\Users\\Wayne\\Downloads\\abcs_34k.db")
        print("\nThis will:")
        print("  1. Back up the current data/abcs.db")
        print("  2. Copy Wayne's database to data/abcs.db")
        print("  3. Verify schema compatibility")
        sys.exit(1)

    wayne_db = sys.argv[1]
    success = swap_database(wayne_db)

    if success:
        print("\n✓ Database swapped successfully!")
        print("\nNext steps:")
        print("  1. Run: python test/repair_abcs_db.py data/abcs.db")
        print("     (to ensure all indexes are present)")
        print("  2. Start the app: python src/main.py")
        print("  3. Test sort operations and measure performance")
        print("\nTo restore the original test database:")
        import glob
        backups = sorted(glob.glob("data/abcs.db.backup.*"))
        if backups:
            latest_backup = backups[-1]
            print(f"  cp {latest_backup} data/abcs.db")
        sys.exit(0)
    else:
        print("\n✗ Failed to swap database")
        sys.exit(1)
