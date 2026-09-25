"""Phase 19: add want_to_read and listening progress columns once."""

from __future__ import annotations

import sqlite3

from src.database.connection import DatabaseManager
from src.database.models import Book
from src.database.queries import BookQueries


def _current_library(path):
    """A 2.18 library: series number and collection root, no progress columns."""
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
            active INTEGER DEFAULT 1,
            root_path TEXT
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
        INSERT INTO collections (name, active, root_path)
        VALUES ('Audiobooks', 1, 'D:/Library');
        INSERT INTO books (title, author_id, collection_id, path, series_number)
        VALUES ('Sample Title', 1, 1, '/old/book', 3);
        """
    )
    conn.commit()
    conn.close()


def test_upgrade_adds_progress_columns_once(tmp_path):
    db_path = tmp_path / "abcs.db"
    _current_library(db_path)

    db = DatabaseManager(str(db_path))
    db.initialize_database()

    columns = db._get_existing_columns("books")
    assert "want_to_read" in columns
    assert "listen_position_ms" in columns
    assert "listen_file_name" in columns
    assert "rating" not in columns
    assert "cover_path" not in columns

    row = db.fetch_one(
        """
        SELECT title, series_number, path, want_to_read,
               listen_position_ms, listen_file_name
        FROM books WHERE book_id = 1
        """
    )
    assert row["title"] == "Sample Title"
    assert row["series_number"] == 3
    assert row["path"] == "/old/book"
    assert row["want_to_read"] == 0
    assert row["listen_position_ms"] is None
    assert row["listen_file_name"] is None

    book = BookQueries(db).get_by_id(1)
    assert book.want_to_read is False
    assert book.listen_position_ms is None
    assert book.listen_file_name == ""

    backups = list(tmp_path.glob("abcs.backup_schema_repair_*.db"))
    assert len(backups) == 1
    assert db.schema_repair_performed is True
    assert "Want to read and listening progress storage were added" in (
        db.schema_repair_message
    )
    assert "Your books were not changed." in db.schema_repair_message
    assert backups[0].name in db.schema_repair_message

    db.initialize_database()
    assert db.schema_repair_performed is False
    assert db.schema_repair_message == ""
    assert list(tmp_path.glob("abcs.backup_schema_repair_*.db")) == backups
    db.close()


def test_progress_values_round_trip(tmp_path):
    db = DatabaseManager(str(tmp_path / "abcs.db"))
    db.initialize_database()
    books = BookQueries(db)
    from src.database.queries import AuthorQueries

    author_id = AuthorQueries(db).insert("Ada Author")
    collection_id = db.fetch_one("SELECT collection_id FROM collections")[0]
    book_id = books.insert(
        Book(
            title="In Progress",
            author_id=author_id,
            collection_id=collection_id,
            want_to_read=True,
            listen_position_ms=15000,
            listen_file_name="02 Chapter.mp3",
        )
    )
    loaded = books.get_by_id(book_id)
    assert loaded.want_to_read is True
    assert loaded.listen_position_ms == 15000
    assert loaded.listen_file_name == "02 Chapter.mp3"

    loaded.title = "In Progress"
    loaded.want_to_read = False
    loaded.listen_position_ms = 0
    loaded.listen_file_name = ""
    books.update(loaded)
    saved = books.get_by_id(book_id)
    assert saved.want_to_read is False
    assert saved.listen_position_ms == 0
    assert saved.listen_file_name == ""
    db.close()
