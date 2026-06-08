--
-- AbCS SQLite schema (committed copy for tests and fresh clones).
-- Runtime builds may also use data/abcdDB_def.sql (local, gitignored).
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

CREATE TABLE authors (
    author_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT    NOT NULL
                        UNIQUE
);

CREATE TABLE collections (
    collection_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT    NOT NULL
                            UNIQUE,
    active          INTEGER DEFAULT 1
);

CREATE TABLE genres (
    genre_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT    NOT NULL
                        UNIQUE
);

CREATE TABLE series (
    series_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT    NOT NULL
                        UNIQUE
);

CREATE TABLE books (
    book_id       INTEGER  PRIMARY KEY AUTOINCREMENT,
    title         TEXT     NOT NULL,
    author_id     INTEGER,
    year          INTEGER,
    series_id     INTEGER,
    genre_id      INTEGER,
    collection_id INTEGER,
    reader        TEXT,
    time_hours    INTEGER  DEFAULT 0,
    time_minutes  INTEGER  DEFAULT 0,
    tracks        INTEGER  DEFAULT 0,
    size_mb       REAL     DEFAULT 0.0,
    bitrate       INTEGER  DEFAULT 0,
    file_format   TEXT,
    path          TEXT,
    comments      TEXT,
    read_date     DATE,
    date_added    DATETIME DEFAULT CURRENT_TIMESTAMP,
    source        TEXT,
    FOREIGN KEY (author_id) REFERENCES authors (author_id),
    FOREIGN KEY (series_id) REFERENCES series (series_id),
    FOREIGN KEY (genre_id) REFERENCES genres (genre_id),
    FOREIGN KEY (collection_id) REFERENCES collections (collection_id)
);

CREATE INDEX idx_books_author ON books(author_id);
CREATE INDEX idx_books_series ON books(series_id);
CREATE INDEX idx_books_genre ON books(genre_id);
CREATE INDEX idx_books_collection ON books(collection_id);
CREATE INDEX idx_books_title ON books(title);
CREATE INDEX idx_books_collection_title ON books(collection_id, title);
CREATE INDEX idx_books_duplicate_key ON books(title, author_id, year, collection_id);
CREATE INDEX idx_books_read_date ON books(read_date);
CREATE INDEX idx_authors_name ON authors (name ASC);
CREATE INDEX idx_genres_name ON genres (name ASC);
CREATE INDEX idx_series_name ON series (name ASC);
CREATE INDEX idx_collections_active_name ON collections(active, name ASC);

INSERT INTO collections (name, active) VALUES ('Audio Books', 1);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
