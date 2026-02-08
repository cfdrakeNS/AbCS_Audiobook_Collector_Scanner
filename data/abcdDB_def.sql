--
-- File generated with SQLiteStudio v3.4.20 on Sun Jan 25 10:14:18 2026
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: authors
CREATE TABLE authors (
    author_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    author_name TEXT    NOT NULL
                        UNIQUE
);

-- Table: collections
CREATE TABLE collections (
    collection_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_name TEXT    NOT NULL
                            UNIQUE,
    active          INTEGER DEFAULT 1
);


-- Table: genres
CREATE TABLE genres (
    genre_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    genere_name TEXT    NOT NULL
                        UNIQUE
);


-- Table: series
CREATE TABLE series (
    series_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    series_name TEXT    NOT NULL
                        UNIQUE
);

-- Table: books
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
    FOREIGN KEY (
        author_id
    )
    REFERENCES authors (author_id),
    FOREIGN KEY (
        series_id
    )
    REFERENCES series (series_id),
    FOREIGN KEY (
        genre_id
    )
    REFERENCES genres (genre_id),
    FOREIGN KEY (
        collection_id
    )
    REFERENCES collections (collection_id) 
);


-- create index 
CREATE INDEX idx_books_author ON books(author_id);
CREATE INDEX idx_books_series ON books(series_id);
CREATE INDEX idx_books_genre ON books(genre_id);
CREATE INDEX idx_books_collection ON books(collection_id);
CREATE INDEX idx_books_title ON books(title);
CREATE INDEX idx_Author_name ON authors (name ASC);
CREATE INDEX idx_Genre_genre_name ON genres (name ASC);
CREATE INDEX idx_Series_series_name ON series (name ASC);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;

