"""
Reading History Queries - Audio Book Collection
Provides queries for reading statistics and history analysis.
"""

from typing import List, Dict, Any, Optional
from datetime import date, datetime
from .connection import DatabaseManager
from .models import Book


class ReadingQueries:
    """Queries for reading history and statistics."""

    def __init__(self, db: DatabaseManager):
        """Initialize reading queries."""
        self.db = db

    def get_reading_statistics(self, start_date: Optional[date] = None, end_date: Optional[date] = None, 
                          collection_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get reading statistics for the given date range and collection.
        
        Args:
            start_date: Start date for statistics (inclusive)
            end_date: End date for statistics (inclusive)
            collection_id: Collection ID to filter by (None for all)
            
        Returns:
            Dictionary with statistics:
            - total_books: Number of books read
            - total_hours: Total reading hours
            - avg_hours_per_book: Average hours per book
            - books_per_month: Average books per month
            - most_productive_month: Month with most books
            - yearly_breakdown: Books read per year
            - monthly_breakdown: Books read per month
        """
        query = """
            SELECT 
                COUNT(*) as total_books,
                COALESCE(SUM(time_hours), 0) as total_hours,
                COALESCE(AVG(time_hours), 0) as avg_hours_per_book
            FROM books b
            WHERE b.read_date IS NOT NULL
        """
        params = []
        
        if start_date:
            query += " AND b.read_date >= ?"
            params.append(start_date.strftime("%Y-%m-%d"))
            
        if end_date:
            query += " AND b.read_date <= ?"
            params.append(end_date.strftime("%Y-%m-%d"))
            
        if collection_id is not None:
            query += " AND b.collection_id = ?"
            params.append(collection_id)
        
        result = self.db.fetch_one(query, tuple(params))
        
        # Calculate additional statistics
        stats = {
            'total_books': result['total_books'] if result['total_books'] else 0,
            'total_hours': float(result['total_hours']) if result['total_hours'] else 0.0,
            'avg_hours_per_book': float(result['avg_hours_per_book']) if result['avg_hours_per_book'] else 0.0,
        }
        
        # Calculate books per month
        if stats['total_books'] > 0 and start_date and end_date:
            months = max(1, (end_date - start_date).days // 30)
            stats['books_per_month'] = stats['total_books'] / months
        else:
            stats['books_per_month'] = 0.0
        
        # Get most productive month
        stats['most_productive_month'] = self._get_most_productive_month(start_date, end_date, collection_id)
        
        # Get yearly and monthly breakdowns
        stats['yearly_breakdown'] = self._get_yearly_breakdown(start_date, end_date, collection_id)
        stats['monthly_breakdown'] = self._get_monthly_breakdown(start_date, end_date, collection_id)
        
        return stats

    def get_reading_history(self, start_date: Optional[date] = None, end_date: Optional[date] = None,
                         collection_id: Optional[int] = None, order_by: str = "read_date DESC",
                         limit: Optional[int] = None) -> List[Book]:
        """
        Get reading history for the given criteria.
        
        Args:
            start_date: Start date for history (inclusive)
            end_date: End date for history (inclusive)
            collection_id: Collection ID to filter by (None for all)
            order_by: SQL ORDER BY clause
            limit: Maximum number of records to return
            
        Returns:
            List of Book objects with read dates
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
            WHERE b.read_date IS NOT NULL
        """
        params = []
        
        if start_date:
            query += " AND b.read_date >= ?"
            params.append(start_date.strftime("%Y-%m-%d"))
            
        if end_date:
            query += " AND b.read_date <= ?"
            params.append(end_date.strftime("%Y-%m-%d"))
            
        if collection_id is not None:
            query += " AND b.collection_id = ?"
            params.append(collection_id)
        
        query += f" ORDER BY {order_by}"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        rows = self.db.fetch_all(query, tuple(params))
        
        books = []
        for row in rows:
            # Parse read_date
            read_date_value = None
            if row['read_date']:
                if isinstance(row['read_date'], str):
                    read_date_value = datetime.strptime(row['read_date'], "%Y-%m-%d").date()
                else:
                    read_date_value = row['read_date']
            
            books.append(Book(
                book_id=row['book_id'],
                title=row['title'],
                author_id=row['author_id'],
                year=row['year'],
                series_id=row['series_id'],
                genre_id=row['genre_id'],
                collection_id=row['collection_id'],
                reader=row['reader'],
                time_hours=row['time_hours'],
                time_minutes=row['time_minutes'],
                tracks=row['tracks'],
                size_mb=row['size_mb'],
                bitrate=row['bitrate'],
                file_format=row['file_format'],
                path=row['path'],
                comments=row['comments'],
                read_date=read_date_value,
                date_added=row['date_added'],
                source=row['source'],
                author_name=row['author_name'],
                series_name=row['series_name'],
                genre_name=row['genre_name'],
                collection_name=row['collection_name']
            ))
        
        return books

    def get_books_read_on_date(self, target_date: date, collection_id: Optional[int] = None) -> List[Book]:
        """
        Get books that were being read on a specific date.
        This answers "What was I reading on [specific date]?"
        
        Args:
            target_date: The date to check
            collection_id: Collection ID to filter by (None for all)
            
        Returns:
            List of Book objects that were being read on target_date
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
            WHERE b.read_date IS NOT NULL
            AND (
                (b.read_date <= ? AND DATE(b.read_date, '+'7 days') >= ?)
                OR b.read_date = ?
            )
        """
        params = [target_date.strftime("%Y-%m-%d"), target_date.strftime("%Y-%m-%d"), target_date.strftime("%Y-%m-%d")]
        
        if collection_id is not None:
            query += " AND b.collection_id = ?"
            params.append(collection_id)
        
        query += " ORDER BY b.read_date DESC"
        
        rows = self.db.fetch_all(query, tuple(params))
        
        books = []
        for row in rows:
            read_date_value = datetime.strptime(row['read_date'], "%Y-%m-%d").date() if row['read_date'] else None
            
            books.append(Book(
                book_id=row['book_id'],
                title=row['title'],
                author_id=row['author_id'],
                year=row['year'],
                series_id=row['series_id'],
                genre_id=row['genre_id'],
                collection_id=row['collection_id'],
                reader=row['reader'],
                time_hours=row['time_hours'],
                time_minutes=row['time_minutes'],
                tracks=row['tracks'],
                size_mb=row['size_mb'],
                bitrate=row['bitrate'],
                file_format=row['file_format'],
                path=row['path'],
                comments=row['comments'],
                read_date=read_date_value,
                date_added=row['date_added'],
                source=row['source'],
                author_name=row['author_name'],
                series_name=row['series_name'],
                genre_name=row['genre_name'],
                collection_name=row['collection_name']
            ))
        
        return books

    def _get_most_productive_month(self, start_date: Optional[date], end_date: Optional[date], 
                                 collection_id: Optional[int]) -> Optional[Dict[str, Any]]:
        """Get the month with the most books read."""
        query = """
            SELECT 
                strftime('%Y-%m', read_date) as month,
                COUNT(*) as book_count
            FROM books
            WHERE read_date IS NOT NULL
        """
        params = []
        
        if start_date:
            query += " AND read_date >= ?"
            params.append(start_date.strftime("%Y-%m-%d"))
            
        if end_date:
            query += " AND read_date <= ?"
            params.append(end_date.strftime("%Y-%m-%d"))
            
        if collection_id is not None:
            query += " AND collection_id = ?"
            params.append(collection_id)
        
        query += " GROUP BY strftime('%Y-%m', read_date) ORDER BY book_count DESC LIMIT 1"
        
        result = self.db.fetch_one(query, tuple(params))
        
        if result and result['book_count'] > 0:
            month_str = result['month']
            year = int(month_str[:4])
            month = int(month_str[4:6])
            
            # Get month name
            import calendar
            month_name = calendar.month_name[month]
            
            return {
                'year': year,
                'month': month,
                'month_name': month_name,
                'book_count': result['book_count']
            }
        
        return None

    def _get_yearly_breakdown(self, start_date: Optional[date], end_date: Optional[date], 
                           collection_id: Optional[int]) -> List[Dict[str, Any]]:
        """Get yearly breakdown of books read."""
        query = """
            SELECT 
                strftime('%Y', read_date) as year,
                COUNT(*) as book_count,
                COALESCE(SUM(time_hours), 0) as total_hours
            FROM books
            WHERE read_date IS NOT NULL
        """
        params = []
        
        if start_date:
            query += " AND read_date >= ?"
            params.append(start_date.strftime("%Y-%m-%d"))
            
        if end_date:
            query += " AND read_date <= ?"
            params.append(end_date.strftime("%Y-%m-%d"))
            
        if collection_id is not None:
            query += " AND collection_id = ?"
            params.append(collection_id)
        
        query += " GROUP BY strftime('%Y', read_date) ORDER BY year DESC"
        
        rows = self.db.fetch_all(query, tuple(params))
        
        return [
            {
                'year': int(row['year']),
                'book_count': row['book_count'],
                'total_hours': float(row['total_hours'])
            }
            for row in rows
        ]

    def _get_monthly_breakdown(self, start_date: Optional[date], end_date: Optional[date], 
                             collection_id: Optional[int]) -> List[Dict[str, Any]]:
        """Get monthly breakdown of books read."""
        query = """
            SELECT 
                strftime('%Y-%m', read_date) as month,
                COUNT(*) as book_count,
                COALESCE(SUM(time_hours), 0) as total_hours
            FROM books
            WHERE read_date IS NOT NULL
        """
        params = []
        
        if start_date:
            query += " AND read_date >= ?"
            params.append(start_date.strftime("%Y-%m-%d"))
            
        if end_date:
            query += " AND read_date <= ?"
            params.append(end_date.strftime("%Y-%m-%d"))
            
        if collection_id is not None:
            query += " AND collection_id = ?"
            params.append(collection_id)
        
        query += " GROUP BY strftime('%Y-%m', read_date) ORDER BY month DESC LIMIT 60"  # Show 5 years instead of 1
        
        rows = self.db.fetch_all(query, tuple(params))
        
        breakdown = []
        for row in rows:
            month_str = row['month']
            year = int(month_str[:4])
            month = int(month_str[5:7])  # Fix: get month part after the dash
            
            # Get month name with error handling
            import calendar
            try:
                if 1 <= month <= 12:
                    month_name = calendar.month_name[month]
                else:
                    month_name = f"Invalid Month {month}"
            except (IndexError, ValueError):
                month_name = f"Unknown Month {month}"
            
            breakdown.append({
                'year': year,
                'month': month,
                'month_name': month_name,
                'month_key': month_str,
                'book_count': row['book_count'],
                'total_hours': float(row['total_hours'])
            })
        
        return breakdown
