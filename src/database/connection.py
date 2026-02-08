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
from pathlib import Path
from typing import Optional
from contextlib import contextmanager


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
            # If no path specified, use the default: data/abcs.db in the project root
            # Go up 3 folders to find project root
            project_root = Path(__file__).parent.parent.parent
            data_dir = project_root / 'data'  # Look for 'data' subfolder
            # Create 'data' folder if it doesn't exist
            data_dir.mkdir(exist_ok=True)
            # Create full path: data/abcs.db
            db_path = str(data_dir / 'abcs.db')

        self.db_path = db_path  # Store the database file path
        # Connection object (initialized as None)
        self._connection: Optional[sqlite3.Connection] = None

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
        return self._connection

    def close(self):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None

    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.

        Usage:
            with db.transaction() as conn:
                conn.execute("INSERT INTO ...")
        """
        conn = self.connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

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

    def execute_many(self, query: str, params_list: list):
        """
        Execute a query with multiple parameter sets.

        Args:
            query: SQL query string
            params_list: List of parameter tuples
        """
        conn = self.connect()
        conn.executemany(query, params_list)
        conn.commit()

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

    def get_table_count(self, table_name: str) -> int:
        """
        Get count of records in a table.

        Args:
            table_name: Name of the table

        Returns:
            Number of records
        """
        cursor = self.execute(f"SELECT COUNT(*) FROM {table_name}")
        return cursor.fetchone()[0]

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
            (table_name,)
        )
        return cursor.fetchone() is not None

    def initialize_database(self):
        """
        Initialize database schema if not exists.
        If tables don't exist, create them from the bundled SQL schema file.
        """
        # Check if main tables exist
        if not self.table_exists('books'):
            self._create_schema()

    def _create_schema(self):
        """
        Create database schema.
        Uses the bundled SQL schema file in data/abcdDB_def.sql.
        """
        project_root = Path(__file__).parent.parent.parent
        schema_path = project_root / 'data' / 'abcdDB_def.sql'

        if not schema_path.exists():
            raise FileNotFoundError(
                f"Schema file not found: {schema_path}")

        schema = schema_path.read_text(encoding='utf-8')
        conn = self.connect()
        conn.executescript(schema)
        conn.commit()

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
