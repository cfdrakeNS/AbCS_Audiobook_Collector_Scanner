"""Phase 9: first-start upgrade adds series_number only."""

from __future__ import annotations

import sqlite3

from src.database.connection import DatabaseManager
from src.database.queries import BookQueries


def _legacy_database(path):
    """Create a pre-upgrade library with one book and no series_number column."""
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE authors (
            author_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );
        CREATE TABLE genres (
            genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );
        CREATE TABLE series (
            series_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );
        CREATE TABLE collections (
            collection_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            active INTEGER DEFAULT 1
        );
        CREATE TABLE books (
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
            source TEXT
        );
        INSERT INTO authors (name) VALUES ('Ada Author');
        INSERT INTO collections (name, active) VALUES ('Audiobooks', 1);
        INSERT INTO books (title, author_id, collection_id)
        VALUES ('Sample Title - 3', 1, 1);
        """
    )
    conn.commit()
    conn.close()


def test_first_start_adds_series_number_only(tmp_path):
    db_path = tmp_path / "abcs.db"
    _legacy_database(db_path)

    db = DatabaseManager(str(db_path))
    db.initialize_database()

    columns = db._get_existing_columns("books")
    collection_columns = db._get_existing_columns("collections")
    assert "series_number" in columns
    assert "want_to_read" not in columns
    assert "rating" not in columns
    assert "ratings_count" not in columns
    assert "cover_path" not in columns
    assert "root_path" in collection_columns
    assert db.fetch_one("SELECT root_path FROM collections WHERE collection_id = 1")[
        "root_path"
    ] in (None, "")

    row = db.fetch_one("SELECT title, series_number FROM books WHERE book_id = 1")
    assert row["title"] == "Sample Title - 3"
    assert row["series_number"] is None

    book = BookQueries(db).get_by_id(1)
    assert book is not None
    assert book.title == "Sample Title - 3"
    assert book.series_number is None

    backups = list(tmp_path.glob("abcs.backup_schema_repair_*.db"))
    assert len(backups) == 1
    assert db.schema_repair_performed is True
    assert "Series number and collection library root storage were added" in (
        db.schema_repair_message
    )
    assert backups[0].name in db.schema_repair_message

    db.initialize_database()
    assert db.schema_repair_performed is False
    assert list(tmp_path.glob("abcs.backup_schema_repair_*.db")) == backups

    db.close()


def _database_with_series_number(path):
    """Create a library that already has series_number but no root_path."""
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE authors (
            author_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );
        CREATE TABLE genres (
            genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );
        CREATE TABLE series (
            series_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );
        CREATE TABLE collections (
            collection_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            active INTEGER DEFAULT 1
        );
        CREATE TABLE books (
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
            series_number REAL
        );
        INSERT INTO authors (name) VALUES ('Ada Author');
        INSERT INTO collections (name, active) VALUES ('Audiobooks', 1);
        INSERT INTO books (title, author_id, collection_id, path, series_number)
        VALUES ('Sample Title', 1, 1, '/old/book', 3);
        """
    )
    conn.commit()
    conn.close()


def test_first_start_adds_root_path_only(tmp_path):
    db_path = tmp_path / "abcs.db"
    _database_with_series_number(db_path)

    db = DatabaseManager(str(db_path))
    db.initialize_database()

    collection_columns = db._get_existing_columns("collections")
    assert "root_path" in collection_columns
    assert "want_to_read" not in db._get_existing_columns("books")

    row = db.fetch_one("SELECT path, series_number FROM books WHERE book_id = 1")
    assert row["path"] == "/old/book"
    assert row["series_number"] == 3

    backups = list(tmp_path.glob("abcs.backup_schema_repair_*.db"))
    assert len(backups) == 1
    assert db.schema_repair_performed is True
    assert "Collection library root storage was added" in db.schema_repair_message
    assert backups[0].name in db.schema_repair_message

    db.initialize_database()
    assert db.schema_repair_performed is False
    db.close()


def test_new_database_does_not_announce_schema_repair(tmp_path):
    db = DatabaseManager(str(tmp_path / "abcs.db"))
    db.initialize_database()
    assert db.schema_repair_performed is False
    assert db.schema_repair_message == ""
    assert "root_path" in db._get_existing_columns("collections")
    assert "series_number" in db._get_existing_columns("books")
    db.close()
