"""
Web Book API - Audio Book Collection
Fetches book metadata from Google Books and Open Library APIs.
"""

import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Optional, List
from urllib.parse import quote


class WebBookAPI:
    """API client for fetching book metadata from web sources."""
    
    def __init__(self):
        """Initialize the API client."""
        self.google_books_url = "https://www.googleapis.com/books/v1/volumes"
        self.open_library_url = "https://openlibrary.org/search.json"
        self.open_library_work_url = "https://openlibrary.org/works"
        
    def get_book_metadata(self, title: str, author: str = None, year: str = None) -> Optional[Dict]:
        """
        Fetch book metadata from multiple web sources.
        
        Args:
            title: Book title
            author: Author name (optional)
            year: Publication year (optional)
            
        Returns:
            Dictionary with book metadata or None if not found
        """
        # Try Google Books first
        metadata = self._fetch_from_google_books(title, author, year)
        
        # If Google Books fails, try Open Library
        if not metadata:
            metadata = self._fetch_from_open_library(title, author, year)
            
        return metadata
    
    def _fetch_from_google_books(self, title: str, author: str = None, year: str = None) -> Optional[Dict]:
        """Fetch metadata from Google Books API."""
        try:
            # Build search query
            query_parts = [title]
            if author:
                query_parts.append(f"inauthor:{author}")
            if year:
                query_parts.append(f"inpublisher:{year}")
            
            query = " ".join(query_parts)
            params = {
                'q': query,
                'maxResults': 1,
                'fields': 'items(id,volumeInfo(title,authors,publisher,publishedDate,description,industryIdentifiers,categories,averageRating,ratingsCount))'
            }
            
            # Build URL with parameters
            url = f"{self.google_books_url}?{urllib.parse.urlencode(params)}"
            
            # Make request
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            if 'items' in data and data['items']:
                item = data['items'][0]
                volume_info = item.get('volumeInfo', {})
                
                return {
                    'title': volume_info.get('title', ''),
                    'author': self._format_authors(volume_info.get('authors', [])),
                    'year': self._extract_year(volume_info.get('publishedDate', '')),
                    'publisher': volume_info.get('publisher', ''),
                    'plot': volume_info.get('description', ''),
                    'genre': self._format_categories(volume_info.get('categories', [])),
                    'isbn': self._extract_isbn(volume_info.get('industryIdentifiers', [])),
                    'rating': volume_info.get('averageRating', 0),
                    'ratings_count': volume_info.get('ratingsCount', 0),
                    'source': 'Google Books',
                    'confidence': 0.9
                }
            
        except Exception as e:
            print(f"Google Books API error: {e}")
            
        return None
    
    def _fetch_from_open_library(self, title: str, author: str = None, year: str = None) -> Optional[Dict]:
        """Fetch metadata from Open Library API."""
        try:
            # Build search query
            query_parts = [title]
            if author:
                query_parts.append(f"author:{author}")
            if year:
                query_parts.append(f"first_publish_year:{year}")
            
            query = " ".join(query_parts)
            params = {
                'q': query,
                'limit': 1,
                'fields': 'key,title,author_name,first_publish_year,publisher,subject,cover_i,isbn,ratings_average,ratings_count'
            }
            
            # Build URL with parameters
            url = f"{self.open_library_url}?{urllib.parse.urlencode(params)}"
            
            # Make request
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            if 'docs' in data and data['docs']:
                doc = data['docs'][0]
                
                # Get detailed work information
                work_key = doc.get('key', '')
                if work_key.startswith('/works/'):
                    work_id = work_key.split('/')[-1]
                    work_details = self._get_open_library_work_details(work_id)
                else:
                    work_details = {}
                
                return {
                    'title': doc.get('title', ''),
                    'author': self._format_authors(doc.get('author_name', [])),
                    'year': str(doc.get('first_publish_year', '')),
                    'publisher': ', '.join(doc.get('publisher', [])),
                    'plot': work_details.get('description', ''),
                    'genre': self._format_categories(doc.get('subject', [])),
                    'isbn': doc.get('isbn', [''])[0] if doc.get('isbn') else '',
                    'rating': doc.get('ratings_average', 0),
                    'ratings_count': doc.get('ratings_count', 0),
                    'source': 'Open Library',
                    'confidence': 0.8
                }
            
        except Exception as e:
            print(f"Open Library API error: {e}")
            
        return None
    
    def _get_open_library_work_details(self, work_id: str) -> Dict:
        """Get detailed work information from Open Library."""
        try:
            url = f"{self.open_library_work_url}/{work_id}.json"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            return {
                'description': self._extract_description(data.get('description', ''))
            }
            
        except Exception:
            return {}
    
    def _format_authors(self, authors: List[str]) -> str:
        """Format author list as string."""
        if not authors:
            return ""
        elif len(authors) == 1:
            return authors[0]
        elif len(authors) <= 3:
            return ", ".join(authors)
        else:
            return f"{', '.join(authors[:2])} and {len(authors) - 2} others"
    
    def _format_categories(self, categories: List[str]) -> str:
        """Format category list as string."""
        if not categories:
            return ""
        elif len(categories) == 1:
            return categories[0]
        elif len(categories) <= 3:
            return " > ".join(categories[:3])
        else:
            return f"{' > '.join(categories[:2])} > {len(categories) - 2} more"
    
    def _extract_year(self, published_date: str) -> str:
        """Extract year from published date string."""
        if not published_date:
            return ""
        
        # Try to extract 4-digit year
        import re
        year_match = re.search(r'\b(19|20)\d{2}\b', published_date)
        return year_match.group(0) if year_match else published_date
    
    def _extract_isbn(self, identifiers: List[Dict]) -> str:
        """Extract ISBN from industry identifiers."""
        if not identifiers:
            return ""
        
        # Prefer ISBN-13, fallback to ISBN-10
        for identifier in identifiers:
            if identifier.get('type') == 'ISBN_13':
                return identifier.get('identifier', '')
        
        for identifier in identifiers:
            if identifier.get('type') == 'ISBN_10':
                return identifier.get('identifier', '')
        
        return ""
    
    def _extract_description(self, description) -> str:
        """Extract description from various formats."""
        if isinstance(description, str):
            return description
        elif isinstance(description, dict):
            return description.get('value', '')
        else:
            return str(description) if description else ""
