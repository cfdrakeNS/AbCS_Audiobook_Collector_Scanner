"""
Data models for AbCS application.

IMPORTANT: These are Python dataclasses (not database tables).
Each class represents a row from a SQLite database table.
The field names correspond to SQLite database column names.

For example:
- Book class fields = columns in the 'books' table
- Author class fields = columns in the 'authors' table
- Series class fields = columns in the 'series' table

When data is fetched from SQLite, it's converted from database rows into these Python objects.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, date


@dataclass
class Author:
    """
    Author model - represents a row from the 'authors' table in SQLite.

    Database fields (SQLite columns):
    - author_id: Primary key (unique identifier, auto-incremented)
    - name: Author's name (text)
    """

    author_id: Optional[int] = None  # SQLite column: author_id (PRIMARY KEY)
    name: str = ""  # SQLite column: author_name

    def __str__(self):
        return self.name


@dataclass
class Series:
    """Book series model."""

    series_id: Optional[int] = None
    name: str = ""

    def __str__(self):
        return self.name


@dataclass
class Genre:
    """Genre model."""

    genre_id: Optional[int] = None
    name: str = ""

    def __str__(self):
        return self.name


@dataclass
class Collection:
    """Collection model."""

    collection_id: Optional[int] = None
    name: str = ""
    active: bool = True

    def __str__(self):
        return self.name


@dataclass
class Book:
    """
    Audio book model - represents a row from the 'books' table in SQLite.

    Database fields from 'books' table:
    - book_id: Primary key (unique identifier)
    - title: Book title
    - author_id, series_id, genre_id, collection_id: Foreign keys (links to other tables)
    - reader, year, time_hours, time_minutes, etc.: Audiobook metadata
    - read_date: Set when user marks book as read
    - date_added: Timestamp when book was added to database

    Denormalized fields (for display convenience):
    - author_name, series_name, genre_name, collection_name: Retrieved via SQL JOINs
      (so we don't have to look up IDs every time)
    """

    # Direct SQLite columns from 'books' table:
    book_id: Optional[int] = None
    title: str = ""  # SQLite column: title
    # FOREIGN KEY - references authors.author_id
    author_id: Optional[int] = None
    # Denormalized (retrieved via LEFT JOIN with authors table)
    author_name: str = ""
    year: Optional[int] = None  # SQLite column: year (publication year)
    # FOREIGN KEY - references series.series_id
    series_id: Optional[int] = None
    # Denormalized (retrieved via LEFT JOIN with series table)
    series_name: str = ""
    genre_id: Optional[int] = None  # FOREIGN KEY - references genres.genre_id
    # Denormalized (retrieved via LEFT JOIN with genres table)
    genre_name: str = ""
    # FOREIGN KEY - references collections.collection_id
    collection_id: Optional[int] = None
    # Denormalized (retrieved via LEFT JOIN with collections table)
    collection_name: str = ""
    reader: str = ""  # SQLite column: reader (narrator name)
    time_hours: int = 0  # SQLite column: time_hours (listening duration)
    time_minutes: int = 0  # SQLite column: time_minutes
    tracks: int = 0  # SQLite column: tracks (number of audio tracks)
    size_mb: float = 0.0  # SQLite column: size_mb (file size in megabytes)
    bitrate: int = 0  # SQLite column: bitrate (audio bitrate)
    file_format: str = ""  # SQLite column: file_format (e.g., "mp3", "m4b")
    path: str = ""  # SQLite column: path (file location on disk)
    comments: str = ""  # SQLite column: comments (user notes)
    # SQLite column: read_date (when user finished listening)
    read_date: Optional[date] = None
    # SQLite column: date_added (when entry was created)
    date_added: datetime = field(default_factory=datetime.now)
    source: str = ""  # SQLite column: source (Windows username who imported)

    @property
    def time_display(self) -> str:
        """Format time as HH:MM."""
        try:
            hours = int(self.time_hours) if self.time_hours else 0
            minutes = int(self.time_minutes) if self.time_minutes else 0
            return f"{hours:02d}:{minutes:02d}"
        except (ValueError, TypeError):
            return "0:00"

    @property
    def size_display(self) -> str:
        """Format size in MB."""
        try:
            size = float(self.size_mb) if self.size_mb else 0.0
            return f"{size:.1f}"
        except (ValueError, TypeError):
            return "0.0"

    def __str__(self):
        return f"{self.title} by {self.author_name}"


@dataclass
class SearchFilter:
    """Search and filter criteria for book list."""

    collection_id: Optional[int] = None  # None = All
    read_filter: str = "All"  # All, Read, Unread
    order_by: str = "Title"  # Title, Author, Genre, Series
    search_text: str = ""
    is_keyword_search: bool = False  # True if search starts with "?"

    @property
    def has_search(self) -> bool:
        """Check if search is active."""
        return bool(self.search_text)


@dataclass
class Statistics:
    """Application statistics for splash screen."""

    total_books: int = 0
    total_authors: int = 0
    total_series: int = 0
    total_genres: int = 0
    total_collections: int = 0
    books_read: int = 0
    books_unread: int = 0
    total_time_hours: int = 0

    @property
    def total_time_display(self) -> str:
        """Format total listening time."""
        if self.total_time_hours < 24:
            return f"{self.total_time_hours} hours"
        days = self.total_time_hours // 24
        hours = self.total_time_hours % 24
        return f"{days} days, {hours} hours"
