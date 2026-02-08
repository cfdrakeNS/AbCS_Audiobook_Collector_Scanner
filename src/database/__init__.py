"""
Database package for AbCS.
Provides data access layer for the application.
"""

from .connection import DatabaseManager, get_db, close_db
from .models import (
    Book, Author, Series, Genre, Collection,
    ImportRecord, SearchFilter, Statistics
)
from .queries import (
    BookQueries, AuthorQueries, SeriesQueries,
    GenreQueries, CollectionQueries, StatisticsQueries
)

__all__ = [
    # Connection
    'DatabaseManager', 'get_db', 'close_db',
    
    # Models
    'Book', 'Author', 'Series', 'Genre', 'Collection',
    'ImportRecord', 'SearchFilter', 'Statistics',
    
    # Queries
    'BookQueries', 'AuthorQueries', 'SeriesQueries',
    'GenreQueries', 'CollectionQueries', 'StatisticsQueries'
]
