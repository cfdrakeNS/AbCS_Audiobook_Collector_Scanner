---- Create indexes 
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

--- Index: idx_author_name
DROP INDEX IF EXISTS idx_author_name;
CREATE INDEX IF NOT EXISTS idx_Author_name ON authors (
    name ASC
);

-- Index: idx_Genre_genre_name
DROP INDEX IF EXISTS idx_Genre_genre_name;
CREATE INDEX IF NOT EXISTS idx_Genre_genre_name ON genres (
    name ASC
);

-- Index: idx_Series_series_name
DROP INDEX IF EXISTS idx_Series_series_name;
CREATE INDEX IF NOT EXISTS idx_Series_series_name ON series (
    name ASC
);

-- Index: idx_books_author_id
DROP INDEX IF EXISTS idx_books_author;
CREATE INDEX IF NOT EXISTS idx_books_author ON books (
    author_id ASC
);

-- Index: idx_books_collection_id
DROP INDEX IF EXISTS idx_books_collection;
CREATE INDEX IF NOT EXISTS idx_books_collection ON books (
    collection_id ASC
);

-- Index: idx_books_genre_id
DROP INDEX IF EXISTS idx_books_genre;
CREATE INDEX IF NOT EXISTS idx_books_genre ON books (
    genre_id asc
);
-- Index: idx_books_series_id
DROP INDEX IF EXISTS idx_books_series;
CREATE INDEX IF NOT EXISTS idx_books_series ON books (
    series_id ASC
);
-- Index: idx_books_title
DROP INDEX IF EXISTS idx_books_title;
CREATE INDEX IF NOT EXISTS idx_books_title ON books (
    title ASC
);

-- Index: idx_books_collection_title
DROP INDEX IF EXISTS idx_books_collection_title;
CREATE INDEX IF NOT EXISTS idx_books_collection_title ON books (
    collection_id ASC,
    title ASC
);

-- Index: idx_books_duplicate_key
DROP INDEX IF EXISTS idx_books_duplicate_key;
CREATE INDEX IF NOT EXISTS idx_books_duplicate_key ON books (
    title ASC,
    author_id ASC,
    year ASC,
    collection_id ASC
);

-- Index: idx_books_read_date
DROP INDEX IF EXISTS idx_books_read_date;
CREATE INDEX IF NOT EXISTS idx_books_read_date ON books (
    read_date ASC
);

-- Index: idx_collections_active_name
DROP INDEX IF EXISTS idx_collections_active_name;
CREATE INDEX IF NOT EXISTS idx_collections_active_name ON collections (
    active ASC,
    name ASC
);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;

