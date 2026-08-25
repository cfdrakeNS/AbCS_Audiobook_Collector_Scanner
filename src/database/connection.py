"""
Database connection management for AbCS.

WHAT IS THIS FILE?
This file manages the connection to the SQLite database file on disk.
It provides:
1. A persistent connection to the database
2. Methods to execute queries (INSERT, UPDATE, SELECT, DELETE)
3. Automatic connection pooling (reuse same connection)

HOW DOES THIS WORK?
When you want to access data, you don't open/close the connection for each operation.
Instead, you keep one connection open and reuse it, which is faster.
"""

import sqlite3
import os
import sys
import time
from datetime import datetime
import shutil
from pathlib import Path
from typing import Optional

DEFAULT_SQLITE_CACHE_KB = -32768  # 32 MB (32 * 1024 KiB)
DEFAULT_SQLITE_MMAP_BYTES = 134217728  # 128 MB


def _compute_sqlite_pragmas(db_path: str) -> tuple[int, int]:
    """Return (cache_size_kb_negative, mmap_size_bytes) tuned to DB size and RAM."""
    db_bytes = 0
    if os.path.exists(db_path):
        db_bytes = os.path.getsize(db_path)
        wal_path = db_path + "-wal"
        if os.path.exists(wal_path):
            db_bytes += os.path.getsize(wal_path)

    ram_mb = 8192  # fallback when psutil unavailable
    try:
        import psutil

        ram_mb = psutil.virtual_memory().total / (1024 * 1024)
    except Exception:
        pass

    if db_bytes == 0:
        return DEFAULT_SQLITE_CACHE_KB, DEFAULT_SQLITE_MMAP_BYTES

    db_mb = db_bytes / (1024 * 1024)
    cache_mb = max(8, min(db_mb * 2, 128, ram_mb * 0.05))
    mmap_mb = max(64, min(db_mb * 4, 256, ram_mb * 0.10))

    # Keep desktop defaults on 8 GB+ machines so small DBs do not regress
    if ram_mb >= 8192:
        cache_mb = max(cache_mb, 32)
        mmap_mb = max(mmap_mb, 128)

    return -int(cache_mb * 1024), int(mmap_mb * 1024 * 1024)


class DatabaseManager:
    """
    Manages SQLite database connections and query execution.

    This is a low-level manager that handles all communication with the SQLite database file.
    Think of it as the "driver" that talks to the database.
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database manager - connects to a SQLite database file.

        Args:
            db_path: Path to SQLite database file (e.g., "data/abcs.db")
                     If None, uses default location (data/abcs.db in project root)
        """
        if db_path is None:
            if getattr(sys, "frozen", False):
                from src.app_paths import get_user_data_dir

                data_dir = get_user_data_dir()
                db_path = str(data_dir / "abcs.db")
            else:
                project_root = Path(__file__).parent.parent.parent
                data_dir = project_root / "data"
                data_dir.mkdir(exist_ok=True)
                db_path = str(data_dir / "abcs.db")

        self.db_path = db_path  # Store the database file path
        # Connection object (initialized as None)
        self._connection: Optional[sqlite3.Connection] = None
        self.schema_repair_performed = False
        self.schema_repair_message = ""

    def connect(self) -> sqlite3.Connection:
        """
        Get or create database connection - implements "lazy connection pooling".

        This method ensures we only have ONE connection to the database (reused).
        If connection doesn't exist, it creates one. Otherwise, it returns the existing one.

        Returns:
            SQLite connection object (an open connection to the database file)
        """
        if self._connection is None:
            # First time: open connection to the SQLite database file
            # This creates the database file if it doesn't exist
            self._connection = sqlite3.connect(self.db_path)
            # row_factory = sqlite3.Row allows accessing columns by name (like a dictionary)
            # Without this, you'd have to access columns by number: row[0], row[1], etc.
            self._connection.row_factory = sqlite3.Row
            # Enable foreign key constraints - SQLite doesn't enforce these by default
            # This prevents you from deleting an author if books still reference them
            self._connection.execute("PRAGMA foreign_keys = ON")
            # PHASE 1 OPTIMIZATION: Enable WAL mode for better concurrency and performance
            # WAL allows readers and writers to proceed concurrently
            self._connection.execute("PRAGMA journal_mode=WAL")
            # Keep hot pages in memory across repeated reads in long sessions
            cache_kb, mmap_bytes = _compute_sqlite_pragmas(self.db_path)
            self._connection.execute(f"PRAGMA cache_size = {cache_kb}")
            self._connection.execute("PRAGMA temp_store = MEMORY")
            self._connection.execute(f"PRAGMA mmap_size = {mmap_bytes}")
        return self._connection

    def close(self):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None

    @staticmethod
    def _remove_sqlite_sidecars(db_path: Path) -> None:
        """Remove WAL/SHM files so a replaced database opens cleanly."""
        for suffix in ("-wal", "-shm"):
            sidecar = Path(f"{db_path}{suffix}")
            if sidecar.exists():
                sidecar.unlink()

    def _checkpoint_wal(self) -> None:
        """Flush WAL contents into the main database file before copying."""
        if self._connection is None:
            return
        try:
            self._connection.execute("PRAGMA wal_checkpoint(FULL)")
            self._connection.commit()
        except sqlite3.Error:
            pass

    def execute(self, query: str, params: tuple = None) -> sqlite3.Cursor:
        """
        Execute a SQL query (INSERT, UPDATE, DELETE, etc.).

        IMPORTANT: Use this for INSERT/UPDATE/DELETE. For SELECT, use fetch_one() or fetch_all().

        Args:
            query: SQL query string (e.g., "INSERT INTO books (title) VALUES (?)")
            params: Tuple of values to substitute for ? placeholders
                    (e.g., ("My Book Title",) - note the comma to make it a tuple)

        Returns:
            Cursor object - contains information about the query execution
            (For INSERT, use cursor.lastrowid to get the ID of the inserted row)
        """
        conn = self.connect()  # Get (or reuse) the connection
        if params:
            # If parameters provided, substitute them for ? placeholders
            # Example: query="INSERT INTO books (title) VALUES (?)", params=("My Book",)
            # Result: "INSERT INTO books (title) VALUES ('My Book')"
            return conn.execute(query, params)
        # If no params, just execute the query as-is
        return conn.execute(query)

    def fetch_one(self, query: str, params: tuple = None) -> Optional[sqlite3.Row]:
        """
        Fetch a single row from a SELECT query.

        Use this when you expect 0 or 1 result (e.g., getting a book by ID).

        Args:
            query: SELECT SQL query string
            params: Tuple of values to substitute for ? placeholders

        Returns:
            Row object or None
        """
        cursor = self.execute(query, params)
        return cursor.fetchone()

    def fetch_all(self, query: str, params: tuple = None) -> list:
        """
        Fetch all rows from a SELECT query.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of Row objects
        """
        cursor = self.execute(query, params)
        return cursor.fetchall()

    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists.

        Args:
            table_name: Name of the table

        Returns:
            True if table exists
        """
        cursor = self.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        )
        return cursor.fetchone() is not None

    def initialize_database(self):
        """
        Initialize database schema if not exists.
        If tables don't exist, create them from the bundled SQL schema file.
        """
        # Check if main tables exist
        if not self.table_exists("books"):
            self._create_schema()

        self.schema_repair_performed = False
        self.schema_repair_message = ""
        self._ensure_legacy_schema_compatibility()
        self._ensure_minimum_seed_data()
        self._ensure_indexes()

    def _ensure_legacy_schema_compatibility(self):
        """
        Repair older tester databases so current import and query flows work.

        Strategy:
        1) Ensure required tables exist
        2) Ensure required columns exist (add missing where possible)
        3) If critical ID/name columns are still incompatible, backup and rebuild
        """
        conn = self.connect()

        table_create_sql: dict[str, str] = {
            "authors": """
                CREATE TABLE IF NOT EXISTS authors (
                    author_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            """,
            "genres": """
                CREATE TABLE IF NOT EXISTS genres (
                    genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            """,
            "series": """
                CREATE TABLE IF NOT EXISTS series (
                    series_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            """,
            "collections": """
                CREATE TABLE IF NOT EXISTS collections (
                    collection_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    active INTEGER DEFAULT 1
                )
            """,
            "books": """
                CREATE TABLE IF NOT EXISTS books (
                    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author_id INTEGER,
                    year INTEGER,
                    series_id INTEGER,
                    genre_id INTEGER,
                    collection_id INTEGER,
                    reader TEXT,
                    time_hours INTEGER DEFAULT 0,
                    time_minutes INTEGER DEFAULT 0,
                    tracks INTEGER DEFAULT 0,
                    size_mb REAL DEFAULT 0.0,
                    bitrate INTEGER DEFAULT 0,
                    file_format TEXT,
                    path TEXT,
                    comments TEXT,
                    read_date DATE,
                    date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
                    source TEXT,
                    FOREIGN KEY (author_id) REFERENCES authors(author_id),
                    FOREIGN KEY (series_id) REFERENCES series(series_id),
                    FOREIGN KEY (genre_id) REFERENCES genres(genre_id),
                    FOREIGN KEY (collection_id) REFERENCES collections(collection_id)
                )
            """,
        }

        column_specs: dict[str, dict[str, str]] = {
            "authors": {
                "author_id": "INTEGER",
                "name": "TEXT",
            },
            "genres": {
                "genre_id": "INTEGER",
                "name": "TEXT",
            },
            "series": {
                "series_id": "INTEGER",
                "name": "TEXT",
            },
            "collections": {
                "collection_id": "INTEGER",
                "name": "TEXT",
                "active": "INTEGER DEFAULT 1",
            },
            "books": {
                "book_id": "INTEGER",
                "title": "TEXT",
                "author_id": "INTEGER",
                "year": "INTEGER",
                "series_id": "INTEGER",
                "genre_id": "INTEGER",
                "collection_id": "INTEGER",
                "reader": "TEXT",
                "time_hours": "INTEGER DEFAULT 0",
                "time_minutes": "INTEGER DEFAULT 0",
                "tracks": "INTEGER DEFAULT 0",
                "size_mb": "REAL DEFAULT 0.0",
                "bitrate": "INTEGER DEFAULT 0",
                "file_format": "TEXT",
                "path": "TEXT",
                "comments": "TEXT",
                "read_date": "DATE",
                "date_added": "DATETIME",
                "source": "TEXT",
            },
        }

        critical_columns: dict[str, set[str]] = {
            "authors": {"author_id", "name"},
            "genres": {"genre_id", "name"},
            "series": {"series_id", "name"},
            "collections": {"collection_id", "name"},
            "books": {"book_id", "title", "author_id", "collection_id"},
        }

        existing_tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            ).fetchall()
        }
        created_tables: list[str] = []
        added_columns: list[str] = []
        backup_path: Optional[Path] = None

        planned_changes = False
        for table_name in table_create_sql:
            if table_name not in existing_tables:
                planned_changes = True
                continue
            existing_columns = self._get_existing_columns(table_name)
            for column_name in column_specs.get(table_name, {}):
                if column_name not in existing_columns:
                    planned_changes = True
                    break

        if planned_changes and existing_tables:
            backup_path = self._backup_database_file("schema_repair")

        for table_name, create_sql in table_create_sql.items():
            if table_name not in existing_tables:
                created_tables.append(table_name)
            conn.execute(create_sql)

        for table_name, columns in column_specs.items():
            if not self.table_exists(table_name):
                continue
            existing_columns = self._get_existing_columns(table_name)
            for column_name, column_def in columns.items():
                if column_name in existing_columns:
                    continue
                conn.execute(
                    f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}"
                )
                added_columns.append(f"{table_name}.{column_name}")

        conn.commit()

        for table_name, required in critical_columns.items():
            if not self.table_exists(table_name):
                self._rebuild_database_from_schema("missing_critical_table")
                return
            existing_columns = self._get_existing_columns(table_name)
            if not required.issubset(existing_columns):
                self._rebuild_database_from_schema("missing_critical_columns")
                return

        if created_tables or added_columns:
            self.schema_repair_performed = True
            backup_note = ""
            if backup_path is not None:
                backup_note = f" Backup: {backup_path.name}."
            self.schema_repair_message = (
                "Database upgraded from legacy format for compatibility."
                f"{backup_note}"
            )

    def _get_existing_columns(self, table_name: str) -> set[str]:
        """Return existing column names for a table."""
        conn = self.connect()
        rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        return {row[1] for row in rows}

    def _backup_database_file(self, reason: str) -> Optional[Path]:
        """Create a timestamped backup of the current database file."""
        db_file = Path(self.db_path)
        if not db_file.exists():
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{db_file.stem}.backup_{reason}_{timestamp}{db_file.suffix}"
        backup_path = db_file.parent / backup_name
        shutil.copy2(db_file, backup_path)
        self._stamp_backup_creation_time(backup_path)
        return backup_path

    def _rebuild_database_from_schema(self, reason: str):
        """Backup incompatible DB and rebuild a fresh compatible schema."""
        backup_path = self._backup_database_file(reason)

        self.close()
        db_file = Path(self.db_path)
        if db_file.exists():
            db_file.unlink()

        self._create_schema()
        self.schema_repair_performed = True
        if backup_path is not None:
            self.schema_repair_message = (
                "Database rebuilt from schema for compatibility. "
                f"Backup: {backup_path.name}."
            )
        else:
            self.schema_repair_message = (
                "Database rebuilt from schema for compatibility."
            )

    def _ensure_indexes(self):
        """Ensure critical indexes exist for query performance."""
        conn = self.connect()

        if self.table_exists("books"):
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_books_author ON books(author_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_books_series ON books(series_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_books_genre ON books(genre_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_books_collection ON books(collection_id)"
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_books_title ON books(title)")
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_books_collection_title ON books(collection_id, title)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_books_duplicate_key ON books(title, author_id, year, collection_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_books_read_date ON books(read_date)"
            )

        if self.table_exists("authors"):
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_authors_name ON authors(name ASC)"
            )

        if self.table_exists("genres"):
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_genres_name ON genres(name ASC)"
            )

        if self.table_exists("series"):
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_series_name ON series(name ASC)"
            )

        if self.table_exists("collections"):
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_collections_active_name ON collections(active, name ASC)"
            )

        conn.commit()

    def _ensure_minimum_seed_data(self):
        """Ensure required seed data exists for first-run and repaired databases."""
        if not self.table_exists("collections"):
            return

        row = self.fetch_one("SELECT COUNT(*) FROM collections")
        collection_count = row[0] if row else 0
        if collection_count == 0:
            self.execute(
                "INSERT INTO collections (name, active) VALUES (?, ?)",
                ("Audio Books", 1),
            )
            self.connect().commit()

    def _create_schema(self):
        """
        Create database schema.
        Uses the bundled SQL schema file in data/abcdDB_def.sql.
        """
        schema_path = self._resolve_schema_path()

        if schema_path is None:
            searched_paths = self._candidate_schema_paths()
            searched_text = "\n".join(str(path) for path in searched_paths)
            raise FileNotFoundError(
                "Schema file not found. Searched:\n" f"{searched_text}"
            )

        schema = schema_path.read_text(encoding="utf-8")
        conn = self.connect()
        conn.executescript(schema)
        conn.commit()

    def _resolve_schema_path(self) -> Optional[Path]:
        """Return the first existing schema file path, if any."""
        for path in self._candidate_schema_paths():
            if path.exists():
                return path
        return None

    def _candidate_schema_paths(self) -> list[Path]:
        """Build schema path candidates for dev, one-folder, and one-file builds."""
        candidates: list[Path] = []
        schema_name = "abcdDB_def.sql"

        module_path = Path(__file__).resolve()
        project_root = module_path.parent.parent.parent
        candidates.append(project_root / "data" / schema_name)
        candidates.append(project_root / "test" / "fixtures" / schema_name)

        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidates.append(Path(meipass) / "data" / schema_name)

        executable_dir = Path(sys.executable).resolve().parent
        candidates.append(executable_dir / "data" / schema_name)

        cwd = Path.cwd()
        candidates.append(cwd / "data" / schema_name)

        unique_paths: list[Path] = []
        seen: set[str] = set()
        for path in candidates:
            key = str(path)
            if key in seen:
                continue
            seen.add(key)
            unique_paths.append(path)
        return unique_paths

    def get_backup_directory(self) -> Path:
        """Return backup directory and ensure it exists."""
        backup_dir = Path(self.db_path).resolve().parent / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir

    @staticmethod
    def _stamp_backup_creation_time(backup_path: Path) -> None:
        """Set backup file times to now so list_backups orders by creation, not DB mtime."""
        now = time.time()
        os.utime(backup_path, (now, now))

    def list_backups(self) -> list[Path]:
        """Return known backup files ordered newest-first."""
        db_file = Path(self.db_path).resolve()
        backup_dir = self.get_backup_directory()
        manual_prefix = "abcs_backup_"
        schema_prefix = f"{db_file.stem}.backup_".lower()

        candidates: list[Path] = []
        if backup_dir.is_dir():
            for path in backup_dir.iterdir():
                if path.is_file() and path.name.lower().startswith(manual_prefix):
                    candidates.append(path)

        if db_file.parent.is_dir():
            for path in db_file.parent.iterdir():
                if path.is_file() and path.name.lower().startswith(schema_prefix):
                    candidates.append(path)

        unique: dict[str, Path] = {}
        for path in candidates:
            unique[str(path.resolve())] = path.resolve()

        return sorted(
            unique.values(), key=lambda item: item.stat().st_mtime, reverse=True
        )

    def create_manual_backup(self) -> Path:
        """Create a timestamped manual backup in the backup directory."""
        db_file = Path(self.db_path).resolve()
        if not db_file.exists():
            raise FileNotFoundError(f"Database file not found: {db_file}")

        conn = self.connect()
        conn.commit()
        self._checkpoint_wal()

        timestamp = datetime.now().strftime("%A_%B_%d_%y_at_%H_%M")
        extension = db_file.suffix or ".db"
        backup_name = f"abcs_backup_{timestamp}{extension}"
        backup_path = self.get_backup_directory() / backup_name
        shutil.copy2(db_file, backup_path)
        self._stamp_backup_creation_time(backup_path)
        return backup_path

    def restore_from_backup(self, backup_file: str | Path):
        """Restore current database from a selected backup file."""
        source = Path(backup_file).resolve()
        if not source.exists() or not source.is_file():
            raise FileNotFoundError(f"Backup file not found: {source}")

        destination = Path(self.db_path).resolve()
        self._checkpoint_wal()
        self.close()
        self._remove_sqlite_sidecars(destination)

        if source != destination:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

        self._remove_sqlite_sidecars(destination)
        self.initialize_database()

    def delete_backup_file(self, backup_file: str | Path) -> Path:
        """Delete a backup file and return the deleted path."""
        source = Path(backup_file).resolve()
        if not source.exists() or not source.is_file():
            raise FileNotFoundError(f"Backup file not found: {source}")

        destination = Path(self.db_path).resolve()
        if source == destination:
            raise ValueError("Cannot delete the active database file")

        source.unlink()
        return source

    def full_reset_database(self, create_backup: bool = True) -> Optional[Path]:
        """Reset database to a fresh schema, optionally creating a backup first."""
        backup_path: Optional[Path] = None
        db_file = Path(self.db_path).resolve()

        if create_backup and db_file.exists():
            backup_path = self.create_manual_backup()

        self.close()
        if db_file.exists():
            db_file.unlink()

        self.initialize_database()
        return backup_path

    def vacuum(self):
        """Optimize database (VACUUM command)."""
        conn = self.connect()
        conn.execute("VACUUM")
        conn.commit()


# Global database instance
_db_instance: Optional[DatabaseManager] = None


def get_db(db_path: Optional[str] = None) -> DatabaseManager:
    """
    Get global database instance.

    Args:
        db_path: Path to database (only used on first call)

    Returns:
        DatabaseManager instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager(db_path)
    return _db_instance


def close_db():
    """Close global database instance."""
    global _db_instance
    if _db_instance:
        _db_instance.close()
        _db_instance = None
