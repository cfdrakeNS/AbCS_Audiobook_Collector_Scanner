"""
Database queries for AbCS application.

ARCHITECTURE PATTERN: Query Objects (not ORM)
Instead of using an ORM like SQLAlchemy, this project uses explicit Query classes.
Each class handles SQL queries for a specific database table.

Key concepts:
1. Each Query class (BookQueries, AuthorQueries, etc.) wraps a DatabaseManager
2. Query methods execute SQL and convert results to Python dataclass objects
3. The DatabaseManager handles low-level SQLite operations (connect, execute, fetch)

This approach gives us:
- Full control over SQL (important for performance)
- Clear visibility of database access (good for learning)
- Type-safe results (Python objects instead of raw rows)
"""

from typing import List, Optional, Tuple
from datetime import date, datetime
from .connection import DatabaseManager
from .models import Book, Author, Series, Genre, Collection, SearchFilter, Statistics


class BookQueries:
    """
    Queries for the 'books' table in SQLite.

    This class contains all database operations related to books.
    Each method executes a SQL query and returns Python Book objects.
    """

    def __init__(self, db: DatabaseManager):
        # db is a DatabaseManager object that handles SQLite connection and operations
        self.db = db

    def get_all(self, filter_criteria: SearchFilter = None) -> List[Book]:
        """
        Get all books with optional filtering and searching.

        Args:
            filter_criteria: SearchFilter object with optional filters

        Returns:
            List of Book objects
        """
        query = """
            SELECT b.*,
                   a.name AS author_name,
                   s.name AS series_name,
                   g.name AS genre_name,
                   c.name AS collection_name
            FROM books b
            LEFT JOIN authors a ON b.author_id = a.author_id
            LEFT JOIN series s ON b.series_id = s.series_id
            LEFT JOIN genres g ON b.genre_id = g.genre_id
            LEFT JOIN collections c ON b.collection_id = c.collection_id
            WHERE 1=1
        """
        params = []

        if filter_criteria is None:
            filter_criteria = SearchFilter()

        # Collection filter
        if filter_criteria.collection_id is not None:
            query += " AND b.collection_id = ?"
            params.append(filter_criteria.collection_id)

        # Read status filter
        if filter_criteria.read_filter == "Read":
            query += " AND b.read_date IS NOT NULL"
        elif filter_criteria.read_filter == "Unread":
            query += " AND b.read_date IS NULL"

        # Search/keyword filter
        if filter_criteria.has_search:
            is_keyword = filter_criteria.search_text.startswith(
                '?') or filter_criteria.is_keyword_search

            # Remove leading ? if keyword search
            search_text = filter_criteria.search_text[1:] if filter_criteria.search_text.startswith(
                '?') else filter_criteria.search_text

            # Keyword search: contains; regular search: starts with
            if is_keyword:
                search_term = f"%{search_text}%"
            else:
                search_term = f"{search_text}%"

            if filter_criteria.order_by == "Author":
                query += " AND a.name LIKE ? COLLATE NOCASE"
            elif filter_criteria.order_by == "Genre":
                query += " AND g.name LIKE ? COLLATE NOCASE"
            elif filter_criteria.order_by == "Series":
                query += " AND s.name LIKE ? COLLATE NOCASE"
            else:  # Title
                query += " AND b.title LIKE ? COLLATE NOCASE"
            params.append(search_term)

        # Order by
        if filter_criteria.order_by == "Author":
            query += " ORDER BY a.name, b.year, b.title"
        elif filter_criteria.order_by == "Genre":
            query += " ORDER BY g.name IS NULL, g.name, b.title"
        elif filter_criteria.order_by == "Series":
            query += " ORDER BY s.name IS NULL, s.name, b.year, b.title"
        else:  # Title
            query += " ORDER BY b.title"

        rows = self.db.fetch_all(query, tuple(params) if params else None)
        # Large list views (e.g., 30k+ books) are much faster when we avoid
        # per-row datetime parsing during hydration.
        return [self._row_to_book(row, parse_dates=False) for row in rows]

    def get_by_id(self, book_id: int) -> Optional[Book]:
        """Get book by ID."""
        query = """
            SELECT b.*,
                   a.name AS author_name,
                   s.name AS series_name,
                   g.name AS genre_name,
                   c.name AS collection_name
            FROM books b
            LEFT JOIN authors a ON b.author_id = a.author_id
            LEFT JOIN series s ON b.series_id = s.series_id
            LEFT JOIN genres g ON b.genre_id = g.genre_id
            LEFT JOIN collections c ON b.collection_id = c.collection_id
            WHERE b.book_id = ?
        """
        row = self.db.fetch_one(query, (book_id,))
        # Detail form benefits from parsed dates.
        return self._row_to_book(row, parse_dates=True) if row else None

    def insert(self, book: Book, commit: bool = True) -> int:
        """Insert a new book into the 'books' table."""
        read_date_value = self._serialize_read_date(book.read_date)
        date_added_value = self._serialize_date_added(book.date_added)
        query = """
            INSERT INTO books(
                title, author_id, year, series_id, genre_id, collection_id,
                reader, time_hours, time_minutes, tracks, size_mb, bitrate,
                file_format, path, comments, read_date, date_added, source
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            book.title, book.author_id, book.year, book.series_id,
            book.genre_id, book.collection_id, book.reader,
            book.time_hours, book.time_minutes, book.tracks,
            book.size_mb, book.bitrate, book.file_format,
            book.path, book.comments, read_date_value,
            date_added_value, book.source
        )
        cursor = self.db.execute(query, params)
        if commit:
            self.db.connect().commit()
        return cursor.lastrowid

    def update(self, book: Book):
        """Update an existing book."""
        read_date_value = self._serialize_read_date(book.read_date)
        query = """
            UPDATE books SET
                title = ?, author_id = ?, year = ?, series_id = ?,
                genre_id = ?, collection_id = ?, reader = ?,
                time_hours = ?, time_minutes = ?, tracks = ?,
                size_mb = ?, bitrate = ?, file_format = ?,
                path = ?, comments = ?, read_date = ?, source = ?
            WHERE book_id = ?
        """
        params = (
            book.title, book.author_id, book.year, book.series_id,
            book.genre_id, book.collection_id, book.reader,
            book.time_hours, book.time_minutes, book.tracks,
            book.size_mb, book.bitrate, book.file_format,
            book.path, book.comments, read_date_value, book.source,
            book.book_id
        )
        self.db.execute(query, params)
        self.db.connect().commit()

    def delete(self, book_id: int):
        """Delete a book."""
        self.db.execute("DELETE FROM books WHERE book_id = ?", (book_id,))
        self.db.connect().commit()

    def delete_many(self, book_ids: List[int]):
        """Delete multiple books."""
        placeholders = ','.join('?' * len(book_ids))
        self.db.execute(f"DELETE FROM books WHERE book_id IN ({placeholders})",
                        tuple(book_ids))
        self.db.connect().commit()

    def find_duplicates(self) -> List[Book]:
        """Find duplicate books (same title, author, year, collection)."""
        query = """
            SELECT b.*,
                   a.name AS author_name,
                   s.name AS series_name,
                   g.name AS genre_name,
                   c.name AS collection_name
            FROM books b
            LEFT JOIN authors a ON b.author_id = a.author_id
            LEFT JOIN series s ON b.series_id = s.series_id
            LEFT JOIN genres g ON b.genre_id = g.genre_id
            LEFT JOIN collections c ON b.collection_id = c.collection_id
            WHERE (b.title, b.author_id, b.year, b.collection_id) IN(
                SELECT title, author_id, year, collection_id
                FROM books
                GROUP BY title, author_id, year, collection_id
                HAVING COUNT(*) > 1
            )
            ORDER BY b.title, a.name, b.year
        """
        rows = self.db.fetch_all(query)
        return [self._row_to_book(row, parse_dates=False) for row in rows]

    def bulk_update_series(self, book_ids: List[int], series_id: Optional[int]):
        """Bulk update series for multiple books."""
        placeholders = ','.join('?' * len(book_ids))
        params = [series_id] + book_ids
        self.db.execute(
            f"UPDATE books SET series_id = ? WHERE book_id IN ({placeholders})",
            tuple(params)
        )
        self.db.connect().commit()

    def bulk_update_genre(self, book_ids: List[int], genre_id: Optional[int]):
        """Bulk update genre for multiple books."""
        placeholders = ','.join('?' * len(book_ids))
        params = [genre_id] + book_ids
        self.db.execute(
            f"UPDATE books SET genre_id = ? WHERE book_id IN ({placeholders})",
            tuple(params)
        )
        self.db.connect().commit()

    def bulk_update_collection(self, book_ids: List[int], collection_id: int):
        """Bulk update collection for multiple books."""
        placeholders = ','.join('?' * len(book_ids))
        params = [collection_id] + book_ids
        self.db.execute(
            f"UPDATE books SET collection_id = ? WHERE book_id IN ({placeholders})",
            tuple(params)
        )
        self.db.connect().commit()

    def _row_to_book(self, row, parse_dates: bool = True):
        """Convert database row to Book dataclass."""
        row_dict = dict(row) if not isinstance(row, dict) else row

        if parse_dates:
            # Convert string dates from SQLite to Python date objects
            read_date_str = row_dict.get('read_date')
            read_date_obj = None
            if read_date_str and read_date_str.strip() and read_date_str != '2000-01-01':
                try:
                    # Try YYYY-MM-DD format (our standard)
                    read_date_obj = datetime.strptime(
                        read_date_str, '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    try:
                        # Try M/D/YYYY format (from Access import)
                        read_date_obj = datetime.strptime(
                            read_date_str, '%m/%d/%Y').date()
                    except (ValueError, TypeError):
                        read_date_obj = None

            date_added_str = row_dict.get('date_added')
            date_added_obj = None
            if date_added_str:
                try:
                    # SQLite stores datetime as 'YYYY-MM-DD HH:MM:SS' strings
                    date_added_obj = datetime.strptime(
                        date_added_str, '%Y-%m-%d %H:%M:%S')
                except (ValueError, TypeError):
                    date_added_obj = datetime.now()
            else:
                date_added_obj = datetime.now()
        else:
            # Fast path for large list hydration: keep date values as strings.
            read_date_obj = row_dict.get('read_date')
            date_added_obj = row_dict.get(
                'date_added') or datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return Book(
            book_id=row_dict.get('book_id', 0),
            title=row_dict.get('title', ''),
            author_id=row_dict.get('author_id'),
            author_name=row_dict.get('author_name', ''),
            series_id=row_dict.get('series_id'),
            series_name=row_dict.get('series_name', ''),
            genre_id=row_dict.get('genre_id'),
            genre_name=row_dict.get('genre_name', ''),
            collection_id=row_dict.get('collection_id'),
            collection_name=row_dict.get('collection_name', ''),
            year=row_dict.get('year'),
            reader=row_dict.get('reader', ''),
            time_hours=row_dict.get('time_hours', 0),
            time_minutes=row_dict.get('time_minutes', 0),
            tracks=row_dict.get('tracks', 0),
            size_mb=row_dict.get('size_mb', 0.0),
            bitrate=row_dict.get('bitrate', 0),
            file_format=row_dict.get('file_format', ''),
            path=row_dict.get('path', ''),
            comments=row_dict.get('comments', ''),
            read_date=read_date_obj,
            date_added=date_added_obj,
            source=row_dict.get('source', ''),
        )

    @staticmethod
    def _serialize_read_date(value):
        """Serialize read_date to YYYY-MM-DD or None for SQLite."""
        if not value:
            return None
        if isinstance(value, datetime):
            return value.date().strftime('%Y-%m-%d')
        if isinstance(value, date):
            return value.strftime('%Y-%m-%d')
        if isinstance(value, str):
            return value
        return None

    @staticmethod
    def _serialize_date_added(value):
        """Serialize date_added to YYYY-MM-DD HH:MM:SS or None for SQLite."""
        if not value:
            return None
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(value, date):
            return datetime(value.year, value.month, value.day).strftime(
                '%Y-%m-%d %H:%M:%S')
        if isinstance(value, str):
            return value
        return None


class AuthorQueries:
    """Queries for authors table."""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def get_all(self) -> List[Author]:
        """Get all authors."""
        rows = self.db.fetch_all("SELECT * FROM authors ORDER BY name")
        return [Author(author_id=r['author_id'], name=r['name']) for r in rows]

    def get_by_id(self, author_id: int) -> Optional[Author]:
        """Get author by ID."""
        row = self.db.fetch_one("SELECT * FROM authors WHERE author_id = ?",
                                (author_id,))
        return Author(author_id=row['author_id'], name=row['name']) if row else None

    def get_by_name(self, name: str) -> Optional[Author]:
        """Get author by name."""
        row = self.db.fetch_one(
            "SELECT * FROM authors WHERE name = ?", (name,))
        return Author(author_id=row['author_id'], name=row['name']) if row else None

    def insert(self, name: str, commit: bool = True) -> int:
        """Insert a new author."""
        cursor = self.db.execute(
            "INSERT INTO authors (name) VALUES (?)", (name,))
        if commit:
            self.db.connect().commit()
        return cursor.lastrowid

    def get_or_create(self, name: str, commit: bool = True) -> int:
        """Get author ID by name, create if doesn't exist."""
        author = self.get_by_name(name)
        if author:
            return author.author_id
        return self.insert(name, commit=commit)

    def update(self, author_id: int, name: str):
        """Update author name."""
        self.db.execute("UPDATE authors SET name = ? WHERE author_id = ?",
                        (name, author_id))
        self.db.connect().commit()

    def delete(self, author_id: int):
        """Delete author if no books reference it."""
        self.db.execute(
            "DELETE FROM authors WHERE author_id = ?", (author_id,))
        self.db.connect().commit()

    def cleanup_unused(self):
        """Remove authors with no associated books."""
        query = """
            DELETE FROM authors 
            WHERE author_id NOT IN (SELECT DISTINCT author_id FROM books WHERE author_id IS NOT NULL)
        """
        self.db.execute(query)
        self.db.connect().commit()


class SeriesQueries:
    """Queries for series table."""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def get_all(self) -> List[Series]:
        """Get all series."""
        rows = self.db.fetch_all("SELECT * FROM series ORDER BY name")
        return [Series(series_id=r['series_id'], name=r['name']) for r in rows]

    def get_by_id(self, series_id: int) -> Optional[Series]:
        """Get series by ID."""
        row = self.db.fetch_one("SELECT * FROM series WHERE series_id = ?",
                                (series_id,))
        return Series(series_id=row['series_id'], name=row['name']) if row else None

    def get_by_name(self, name: str) -> Optional[Series]:
        """Get series by name."""
        row = self.db.fetch_one(
            "SELECT * FROM series WHERE name = ?", (name,))
        return Series(series_id=row['series_id'], name=row['name']) if row else None

    def insert(self, name: str, commit: bool = True) -> int:
        """Insert a new series."""
        cursor = self.db.execute(
            "INSERT INTO series (name) VALUES (?)", (name,))
        if commit:
            self.db.connect().commit()
        return cursor.lastrowid

    def get_or_create(self, name: str, commit: bool = True) -> int:
        """Get series ID by name, create if doesn't exist."""
        series = self.get_by_name(name)
        if series:
            return series.series_id
        return self.insert(name, commit=commit)

    def update(self, series_id: int, name: str):
        """Update series name."""
        self.db.execute("UPDATE series SET name = ? WHERE series_id = ?",
                        (name, series_id))
        self.db.connect().commit()

    def delete(self, series_id: int):
        """Delete series if no books reference it."""
        self.db.execute("DELETE FROM series WHERE series_id = ?", (series_id,))
        self.db.connect().commit()

    def cleanup_unused(self):
        """Remove series with no associated books."""
        query = """
            DELETE FROM series 
            WHERE series_id NOT IN (SELECT DISTINCT series_id FROM books WHERE series_id IS NOT NULL)
        """
        self.db.execute(query)
        self.db.connect().commit()


class GenreQueries:
    """Queries for genres table."""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def get_all(self) -> List[Genre]:
        """Get all genres."""
        rows = self.db.fetch_all("SELECT * FROM genres ORDER BY name")
        return [Genre(genre_id=r['genre_id'], name=r['name']) for r in rows]

    def get_by_id(self, genre_id: int) -> Optional[Genre]:
        """Get genre by ID."""
        row = self.db.fetch_one("SELECT * FROM genres WHERE genre_id = ?",
                                (genre_id,))
        return Genre(genre_id=row['genre_id'], name=row['name']) if row else None

    def get_by_name(self, name: str) -> Optional[Genre]:
        """Get genre by name."""
        row = self.db.fetch_one(
            "SELECT * FROM genres WHERE name = ?", (name,))
        return Genre(genre_id=row['genre_id'], name=row['name']) if row else None

    def insert(self, name: str, commit: bool = True) -> int:
        """Insert a new genre."""
        cursor = self.db.execute(
            "INSERT INTO genres (name) VALUES (?)", (name,))
        if commit:
            self.db.connect().commit()
        return cursor.lastrowid

    def get_or_create(self, name: str, commit: bool = True) -> int:
        """Get genre ID by name, create if doesn't exist."""
        genre = self.get_by_name(name)
        if genre:
            return genre.genre_id
        return self.insert(name, commit=commit)

    def update(self, genre_id: int, name: str):
        """Update genre name."""
        self.db.execute("UPDATE genres SET name = ? WHERE genre_id = ?",
                        (name, genre_id))
        self.db.connect().commit()

    def delete(self, genre_id: int):
        """Delete genre if no books reference it."""
        self.db.execute("DELETE FROM genres WHERE genre_id = ?", (genre_id,))
        self.db.connect().commit()

    def cleanup_unused(self):
        """Remove genres with no associated books."""
        query = """
            DELETE FROM genres 
            WHERE genre_id NOT IN (SELECT DISTINCT genre_id FROM books WHERE genre_id IS NOT NULL)
        """
        self.db.execute(query)
        self.db.connect().commit()


class CollectionQueries:
    """Queries for collections table."""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def get_all(self, active_only: bool = True) -> List[Collection]:
        """Get all collections."""
        query = "SELECT * FROM collections"
        if active_only:
            query += " WHERE active = 1"
        query += " ORDER BY name"

        rows = self.db.fetch_all(query)
        return [Collection(
            collection_id=r['collection_id'],
            name=r['name'],
            active=bool(r['active'])
        ) for r in rows]

    def get_by_id(self, collection_id: int) -> Optional[Collection]:
        """Get collection by ID."""
        row = self.db.fetch_one(
            "SELECT * FROM collections WHERE collection_id = ?",
            (collection_id,)
        )
        if row:
            return Collection(
                collection_id=row['collection_id'],
                name=row['name'],
                active=bool(row['active'])
            )
        return None

    def insert(self, collection: Collection) -> int:
        """Insert a new collection."""
        cursor = self.db.execute(
            "INSERT INTO collections (name, active) VALUES (?, ?)",
            (collection.name, collection.active)
        )
        self.db.connect().commit()
        return cursor.lastrowid

    def update(self, collection: Collection):
        """Update a collection."""
        self.db.execute(
            "UPDATE collections SET name = ?, active = ? WHERE collection_id = ?",
            (collection.name, collection.active, collection.collection_id)
        )
        self.db.connect().commit()

    def delete(self, collection_id: int):
        """Delete collection if no books reference it."""
        self.db.execute("DELETE FROM collections WHERE collection_id = ?",
                        (collection_id,))
        self.db.connect().commit()


class StatisticsQueries:
    """Queries for application statistics."""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def get_statistics(self) -> Statistics:
        """Get application statistics."""
        stats = Statistics()

        # Total books
        stats.total_books = self.db.fetch_one("SELECT COUNT(*) FROM books")[0]

        # Total authors
        stats.total_authors = self.db.fetch_one(
            "SELECT COUNT(*) FROM authors")[0]

        # Total series
        stats.total_series = self.db.fetch_one(
            "SELECT COUNT(*) FROM series")[0]

        # Total genres
        stats.total_genres = self.db.fetch_one(
            "SELECT COUNT(*) FROM genres")[0]

        # Total collections
        stats.total_collections = self.db.fetch_one(
            "SELECT COUNT(*) FROM collections WHERE active = 1"
        )[0]

        # Books read/unread
        stats.books_read = self.db.fetch_one(
            "SELECT COUNT(*) FROM books WHERE read_date not null"
        )[0]
        stats.books_unread = stats.total_books - stats.books_read

        # Total listening time
        time_row = self.db.fetch_one(
            "SELECT SUM(time_hours) + SUM(time_minutes) / 60 FROM books"
        )
        stats.total_time_hours = int(time_row[0] or 0)

        return stats
