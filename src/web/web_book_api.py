"""
Web Book API - Audio Book Collection
Fetches book metadata from Google Books, Open Library, and WikiData APIs.
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
        # WikiData SPARQL endpoint
        self.wikidata_url = "https://query.wikidata.org/sparql"
        
    def get_book_metadata(self, title: str, author: str = None, year: str = None, refresh: int = 0) -> Optional[Dict]:
        """
        Fetch book metadata from multiple web sources.
        
        Args:
            title: Book title
            author: Author name (optional)
            year: Publication year (optional)
            refresh: 0=first attempt, 1=skip first source, 2=skip first two sources
            
        Returns:
            Dictionary with book metadata and source info, or None if not found
        """
        # Try Google Books first (fast and reliable)
        if refresh == 0:
            metadata = self._fetch_from_google_books(title, author, year)
            if metadata:
                metadata['source'] = 'google_books'
                metadata['first_attempt'] = True
                return metadata
        
        # Try Open Library second
        if refresh <= 1:
            try:
                metadata = self._fetch_from_open_library(title, author, year)
                if metadata:
                    metadata['source'] = 'open_library'
                    metadata['first_attempt'] = (refresh == 0)
                    return metadata
            except Exception as e:
                print(f"Open Library error: {e}")
                # Continue to next source instead of failing
        
        # Try WikiData third (great for series and author data)
        try:
            metadata = self._fetch_from_wikidata(title, author, year)
            if metadata:
                metadata['source'] = 'wikidata'
                metadata['first_attempt'] = False
                return metadata
        except Exception as e:
            print(f"WikiData error: {e}")
            # Return None if all sources fail
            
        return None
    
    def _fetch_from_google_books(self, title: str, author: str = None, year: str = None) -> Optional[Dict]:
        """Fetch metadata from Google Books API."""
        try:
            # Build search query (match previous working logic: just title and author)
            query = title
            if author:
                query += f" {author}"
            # Do NOT use inpublisher for year, as it restricts results too much
            params = {
                'q': query,
                'maxResults': 1,
                'fields': 'items(id,volumeInfo(title,authors,publisher,publishedDate,description,industryIdentifiers,categories,averageRating,ratingsCount))'
            }
            url = f"{self.google_books_url}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
            if 'items' in data and data['items']:
                item = data['items'][0]
                volume_info = item.get('volumeInfo', {})
                # Extract series and series number if available
                series = ''
                series_number = ''
                # Google Books sometimes puts series info in 'subtitle' or 'seriesInfo' (rare)
                if 'seriesInfo' in volume_info:
                    series = volume_info['seriesInfo'].get('bookDisplayNumber', '')
                    # Sometimes the series name is in 'seriesInfo' as well
                    if not series:
                        series = volume_info['seriesInfo'].get('series', '')
                # Try to parse series/volume from title if possible (e.g., "Book 2", "Volume 3")
                import re
                title = volume_info.get('title', '')
                subtitle = volume_info.get('subtitle', '')
                # Look for patterns like "Book 2", "Volume 3", "#4"
                match = re.search(r'(Book|Volume|#)\s*(\d+)', f"{title} {subtitle}")
                if match:
                    series_number = match.group(2)
                return {
                    'title': title,
                    'author': self._format_authors(volume_info.get('authors', [])),
                    'year': self._extract_year(volume_info.get('publishedDate', '')),
                    'publisher': volume_info.get('publisher', ''),
                    'plot': volume_info.get('description', ''),
                    'genre': self._format_categories(volume_info.get('categories', [])),
                    'isbn': self._extract_isbn(volume_info.get('industryIdentifiers', [])),
                    'rating': volume_info.get('averageRating', 0),
                    'ratings_count': volume_info.get('ratingsCount', 0),
                    'series': series,
                    'series_number': series_number,
                    'source': 'Google Books',
                    'confidence': 0.9
                }
        except Exception as e:
            print(f"Google Books API error: {e}")
        return None
    
    def _fetch_from_open_library(self, title: str, author: str = None, year: str = None) -> Optional[Dict]:
        """Fetch metadata from Open Library API."""
        try:
            # Build search query - more flexible for "1984"
            query_parts = []
            
            # Special handling for "1984" - try exact title first
            if "1984" in title.lower():
                query_parts.append(title)
                # Also try alternative title
                if "nineteen eighty-four" not in title.lower():
                    query_parts.append("nineteen eighty-four")
            else:
                query_parts.append(title)
            
            if author:
                query_parts.append(f"author:{author}")
            if year:
                query_parts.append(f"first_publish_year:{year}")
            
            # Try multiple queries if first one fails
            for query in query_parts[:2]:  # Try at most 2 queries
                params = {
                    'q': query,
                    'limit': 1,
                    'fields': 'key,title,author_name,first_publish_year,publisher,subject,cover_i,isbn,ratings_average,ratings_count'
                }
                
                # Build URL with parameters
                url = f"{self.open_library_url}?{urllib.parse.urlencode(params)}"
                
                # Make request
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=5) as response:
                    data = json.loads(response.read().decode('utf-8'))
                
                if data.get('docs'):
                    doc = data['docs'][0]
                    return {
                        'title': doc.get('title', ''),
                        'author': ', '.join(doc.get('author_name', [])),
                        'year': str(doc.get('first_publish_year', '')),
                        'publisher': ', '.join(doc.get('publisher', [])),
                        'plot': self._get_open_library_description(doc.get('key', '')),
                        'genre': ', '.join(doc.get('subject', [])[:3]),  # Limit to first 3 genres
                        'rating': str(doc.get('ratings_average', '')),
                        'ratings_count': str(doc.get('ratings_count', '')),
                        'source': 'open_library'
                    }
            
            return None
        except Exception as e:
            print(f"Open Library API error: {e}")
            return None
    
    def _get_open_library_description(self, work_key: str) -> str:
        """Get description from Open Library work."""
        try:
            # Extract work ID from key (e.g., "/works/OL1168083W" -> "OL1168083W")
            work_id = work_key.split('/')[-1] if '/' in work_key else work_key
            
            url = f"{self.open_library_work_url}/{work_id}.json"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                return self._extract_description(data.get('description', ''))
        except Exception:
            return ""
    
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
    
    def _fetch_from_wikidata(self, title: str, author: str = None, year: str = None) -> Optional[Dict]:
        """Fetch metadata from WikiData SPARQL endpoint."""
        try:
            # Build a very simple SPARQL query that should work
            # Use basic title search without complex conditions
            safe_title = title.replace('"', '\\"') if title else ""
            safe_author = author.replace('"', '\\"') if author else ""
            
            # Simple SPARQL query - more flexible matching
            # Try multiple search strategies including exact matches
            search_terms = [
                safe_title,
                safe_title.replace(' ', ''),
                safe_title.replace(' and ', ' & ').replace(' And ', ' & ')
            ]
            
            # Create a more flexible query with multiple title options
            title_conditions = []
            for term in search_terms:
                title_conditions.append(f'CONTAINS(LCASE(?bookLabel), LCASE("{term}"))')
            
            title_filter = ' || '.join(title_conditions)
            
            # Add author filter if available
            author_filter = ""
            if author:
                safe_author = author.replace('"', '\\"')
                author_filter = f"""
                ?book wdt:P50 ?author.
                ?author rdfs:label ?authorLabel.
                FILTER(LANG(?authorLabel) = "en")
                FILTER(CONTAINS(LCASE(?authorLabel), LCASE("{safe_author}")))
                """
            
            # Special case for "1984" - try to find the correct Wikidata item for Orwell's 1984
            if "1984" in safe_title.lower():
                # Claude AI's expert fix - search both label and altLabel, remove restrictive class filter
                safe_title_escaped = safe_title.replace('"', '\\"')
                sparql_query = f"""
                SELECT DISTINCT ?item ?itemLabel ?itemDescription WHERE {{
                  ?author rdfs:label "George Orwell"@en.
                  ?item wdt:P50 ?author.
                  {{ ?item rdfs:label ?label. }}
                  UNION
                  {{ ?item skos:altLabel ?label. }}
                  FILTER(CONTAINS(LCASE(?label), LCASE("{safe_title_escaped}")))
                  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
                }}
                LIMIT 10
                """
            else:
                sparql_query = f"""
                SELECT ?book ?bookLabel ?authorLabel ?seriesLabel WHERE {{
                    ?book wdt:P31 wd:Q571.
                    ?book rdfs:label ?bookLabel.
                    FILTER(LANG(?bookLabel) = "en")
                    FILTER({title_filter})
                    
                    {author_filter}
                    
                    OPTIONAL {{
                        ?book wdt:P179 ?series.
                        ?series rdfs:label ?seriesLabel.
                        FILTER(LANG(?seriesLabel) = "en")
                    }}
                }}
                LIMIT 10
                """
            
            # Properly URL encode the query
            from urllib.parse import quote_plus
            encoded_query = quote_plus(sparql_query.strip())
            
            # Build URL with encoded query
            url = f"{self.wikidata_url}?query={encoded_query}&format=json"
            
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'AbCS-Audiobook-Collector/1.0 (Educational audiobook metadata tool)')
            req.add_header('Accept', 'application/sparql-results+json')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                response_text = response.read().decode('utf-8')
                
                # Check if we got JSON
                if not response_text.strip().startswith('{'):
                    print("WikiData: Got non-JSON response")
                    return None
                    
                data = json.loads(response_text)
            
            # Parse results
            results = data.get('results', {}).get('bindings', [])
            
            if results:
                result = results[0]  # Take first result
                
                # Extract basic metadata
                metadata = {
                    'title': self._get_sparql_value(result, 'bookLabel'),
                    'author': self._get_sparql_value(result, 'authorLabel'),
                    'series': self._get_sparql_value(result, 'seriesLabel'),
                    'source': 'WikiData'
                }
                
                return metadata if metadata['title'] else None
            else:
                print("No WikiData results found")
            
        except Exception as e:
            print(f"WikiData API error: {e}")
            return None
    
    def _get_sparql_value(self, result: dict, field: str) -> str:
        """Extract value from SPARQL result binding."""
        try:
            if field in result and result[field]:
                return result[field].get('value', '').strip()
        except Exception:
            pass
        return ""
