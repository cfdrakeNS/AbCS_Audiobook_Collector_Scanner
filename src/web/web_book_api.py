"""
Web Book API - Audio Book Collection
Fetches book metadata from Google Books, Open Library, and WikiData APIs.
"""

import json
import urllib.request
import urllib.parse
import re
import time
from typing import Optional, Dict, List


class WebBookAPI:
    """API client for fetching book metadata from web sources."""

    def _move_article_to_beginning(self, title: str) -> str:
        """Move trailing articles ', the', ', a', ', an' to beginning of title."""
        if not title:
            return title
        # Lowercase for matching, but preserve original case
        trailing_articles = [", the", ", a", ", an"]
        for article in trailing_articles:
            if title.lower().endswith(article):
                base = title[: -len(article)].strip()
                article_word = article[2:].capitalize()
                return f"{article_word} {base}"
        return title

    def __init__(self):
        """Initialize the API client."""
        self.google_books_url = "https://www.googleapis.com/books/v1/volumes"
        self.open_library_url = "https://openlibrary.org/search.json"
        self.open_library_work_url = "https://openlibrary.org/works"
        # WikiData SPARQL endpoint
        self.wikidata_url = "https://query.wikidata.org/sparql"
        self._cache = {}  # Initialize cache to avoid hasattr checks

    def get_book_metadata(
        self,
        title: str,
        author: str = None,
        year: str = None,
        refresh: int = 0,
        move_articles: bool = False,
        flip_author: bool = False,
    ) -> Optional[Dict]:
        """
        Fetch book metadata from multiple web sources.

        Args:
            title: Book title
            author: Author name (optional)
            year: Publication year (optional)
            refresh: 0=first attempt, 1=skip first source, 2=skip first two sources
            move_articles: Move 'The', 'A', 'An' to end of title for search
            flip_author: Flip author name format for search

        Returns:
            Dictionary with book metadata and source info, or None if not found
        """

        import time

        cache_key = f"{title}|{author}|{year}|{refresh}"
        current_time = time.time()

        print(
            f"[WebBookAPI] Fetching metadata for: title='{title}', author='{author}', year='{year}', refresh={refresh}"
        )

        # Check if we have a recent cache entry (within CACHE_DURATION seconds)
        if hasattr(self, "_cache") and cache_key in self._cache:
            cached_time, cached_result = self._cache[cache_key]
            if cached_time and (current_time - cached_time) < self.CACHE_DURATION:
                print(
                    f"[WebBookAPI] Returning cached result (age={current_time-cached_time:.2f}s)"
                )
                return cached_result

            if cached_time:
                self._cache[cache_key] = None  # Clear expired cache

        # Always strip series number for search
        search_title, _ = self._strip_series_number(title)

        # Move trailing article to beginning if present (e.g., 'Great Gatsby, The' -> 'The Great Gatsby')
        search_title = self._move_article_to_beginning(search_title)

        # Optionally move leading article to end (for sources that expect it)
        if move_articles:
            search_title = self._move_article_to_end(search_title)

        # Clean the title
        search_title = self._clean_text_field(search_title)

        # Author transformation as before
        if flip_author and author:
            search_author = self._apply_author_transformations(author, flip_author)
        else:
            search_author = author

        # Try Google Books first (fast and reliable)
        if refresh == 0:
            print("[WebBookAPI] Trying Google Books...")
            t0 = time.time()
            try:
                metadata = self._fetch_from_google_books(
                    search_title, search_author, year
                )
                t1 = time.time()
                print(
                    f"[WebBookAPI] Google Books result: {'FOUND' if metadata else 'not found'} (elapsed={t1-t0:.2f}s)"
                )
                # Only accept if it's a real match (plot or close title/author match)
                is_real_match = False
                if metadata:
                    title_match = metadata.get("title", "").lower()
                    search_title_lower = (search_title or "").lower()
                    author_match = metadata.get("author", "").lower()
                    search_author_lower = (search_author or "").lower()
                    # Has plot content - likely a real match
                    if metadata.get("plot"):
                        is_real_match = True
                    elif search_title_lower and title_match:
                        # Check if title similarity (contains at least part of search title)
                        if (
                            search_title_lower in title_match
                            or title_match in search_title_lower
                            or any(
                                word in title_match
                                for word in search_title_lower.split()
                                if len(word) > 2
                            )
                        ):
                            is_real_match = True
                    elif search_author_lower and author_match:
                        if (
                            search_author_lower in author_match
                            or author_match in search_author_lower
                        ):
                            is_real_match = True

                if metadata and is_real_match:
                    metadata["source"] = "google_books"
                    metadata["first_attempt"] = True
                    # Cache the result
                    self._cache[cache_key] = (current_time, metadata)
                    return metadata
                elif metadata and not is_real_match:
                    print(
                        "[WebBookAPI] Google Books result is weak/irrelevant, continuing to next source."
                    )
            except Exception as e:
                t1 = time.time()
                print(f"[WebBookAPI] Google Books error: {e} (elapsed={t1-t0:.2f}s)")
                # Continue to next source

        # Try Open Library second (always try when refresh=0, or when refresh=1 and Google Books failed)
        if refresh == 0 or refresh == 1:
            print("[WebBookAPI] Trying Open Library...")
            t0 = time.time()
            try:
                metadata = self._fetch_from_open_library(
                    search_title, search_author, year
                )
                t1 = time.time()
                print(
                    f"[WebBookAPI] Open Library result: {'FOUND' if metadata else 'not found'} (elapsed={t1-t0:.2f}s)"
                )
                if metadata:
                    metadata["source"] = "open_library"
                    metadata["first_attempt"] = refresh == 0
                    # Cache the result
                    self._cache[cache_key] = (current_time, metadata)
                    return metadata
            except Exception as e:
                t1 = time.time()
                print(f"[WebBookAPI] Open Library error: {e} (elapsed={t1-t0:.2f}s)")
                # Continue to next source instead of failing

        # Try WikiData third (great for series and author data)
        print("[WebBookAPI] Trying WikiData...")
        t0 = time.time()
        try:
            metadata = self._fetch_from_wikidata(search_title, search_author, year)
            t1 = time.time()
            print(
                f"[WebBookAPI] WikiData result: {'FOUND' if metadata else 'not found'} (elapsed={t1-t0:.2f}s)"
            )
            if metadata:
                metadata["source"] = "wikidata"
                metadata["first_attempt"] = False
                # Cache the result
                self._cache[cache_key] = (current_time, metadata)
                return metadata
        except Exception as e:
            t1 = time.time()
            print(f"[WebBookAPI] WikiData error: {e} (elapsed={t1-t0:.2f}s)")

        print("[WebBookAPI] No data found in any source. Returning None.")
        # Cache the failure too to avoid repeated failed requests
        self._cache[cache_key] = (current_time, None)
        return None

    def _fetch_from_google_books(
        self, title: str, author: str = None, year: str = None
    ) -> Optional[Dict]:
        """Fetch metadata from Google Books API."""
        try:
            # Build search query - use intitle and inauthor for better results
            query_parts = []
            if title:
                query_parts.append(f"intitle:{title}")
            if author:
                query_parts.append(f"inauthor:{author}")
            query = " ".join(query_parts)

            # Include more fields to get series info and subtitle
            params = {
                "q": query,
                "maxResults": 3,  # Get more results to find better match
                "fields": "items(id,volumeInfo(title,subtitle,authors,publisher,publishedDate,description,industryIdentifiers,categories,averageRating,ratingsCount,seriesInfo))",
            }
            url = f"{self.google_books_url}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "AudiobookCollectorScanner/1.0")
            with urllib.request.urlopen(req, timeout=6) as response:
                data = json.loads(response.read().decode("utf-8"))

            if "items" in data and data["items"]:
                # Find the best match among returned items
                best_item = None
                best_score = -1

                for item in data["items"]:
                    volume_info = item.get("volumeInfo", {})
                    item_title = volume_info.get("title", "").lower()
                    item_subtitle = volume_info.get("subtitle", "").lower()

                    # Score based on title match
                    score = 0
                    if title and title.lower() in item_title:
                        score += 10
                    if title and title.lower() in item_subtitle:
                        score += 5
                    if author:
                        item_authors = [
                            a.lower() for a in volume_info.get("authors", [])
                        ]
                        if any(author.lower() in a for a in item_authors):
                            score += 5

                    if score > best_score:
                        best_score = score
                        best_item = item

                if best_item:
                    volume_info = best_item.get("volumeInfo", {})

                    # Extract series and series number from multiple sources
                    series = ""
                    series_number = ""

                    # 1. Check seriesInfo (primarily for comics/manga)
                    series_info = volume_info.get("seriesInfo", {})
                    if series_info:
                        series_number = series_info.get("bookDisplayNumber", "")
                        # Try to get series name from volumeSeries
                        volume_series = series_info.get("volumeSeries", [])
                        if volume_series:
                            series = (
                                volume_series[0]
                                .get("seriesId", "")
                                .replace("_", " ")
                                .title()
                            )

                    # 2. Check subtitle for series info (common for novels)
                    subtitle = volume_info.get("subtitle", "")
                    if subtitle and not series_number:
                        import re

                        # Look for patterns like "Book 1", "Volume 2", "#3", etc.
                        patterns = [
                            r"(?:book|volume|#)\s*(\d+)",
                            r"(?:part|novel)\s*(\w+)",
                        ]
                        for pattern in patterns:
                            match = re.search(pattern, subtitle, re.IGNORECASE)
                            if match:
                                series_number = match.group(1)
                                # Use subtitle without the book number as series name
                                series = re.sub(
                                    pattern, "", subtitle, flags=re.IGNORECASE
                                ).strip(" -")
                                break

                    # 3. Check description for series info
                    description = volume_info.get("description", "")
                    if description and not series_number:
                        import re

                        # Look for series mentions in description
                        patterns = [
                            r"(?:book|volume|#)\s*(\d+)\s+(?:in\s+)?(?:the\s+)?(.+?)(?:\s+series|\s+trilogy|\s+quartet|$)",
                            r"(.+?)\s+(?:book|volume|#)\s*(\d+)",
                        ]
                        for pattern in patterns:
                            match = re.search(pattern, description, re.IGNORECASE)
                            if match:
                                if pattern.startswith(r"(?:book|volume|#)"):
                                    series_number = match.group(1)
                                    series = match.group(2).strip()
                                else:
                                    series = match.group(1).strip()
                                    series_number = match.group(2)
                                break

                    # Return the metadata with enhanced series info
                    return {
                        "title": volume_info.get("title", ""),
                        "author": self._format_authors(volume_info.get("authors", [])),
                        "year": self._extract_year(
                            volume_info.get("publishedDate", "")
                        ),
                        "publisher": volume_info.get("publisher", ""),
                        "plot": volume_info.get("description", ""),
                        "genre": self._format_categories(
                            volume_info.get("categories", [])
                        ),
                        "isbn": self._extract_isbn(
                            volume_info.get("industryIdentifiers", [])
                        ),
                        "rating": volume_info.get("averageRating", 0),
                        "ratings_count": volume_info.get("ratingsCount", 0),
                        "series": series,
                        "series_number": series_number,
                        "source": "Google Books",
                        "confidence": 0.9,
                    }
        except Exception as e:
            print(f"Google Books API error: {e}")
        return None

    def _fetch_from_open_library(
        self, title: str, author: str = None, year: str = None
    ) -> Optional[Dict]:
        """Fetch metadata from Open Library API."""
        try:
            # Build search query - combine title and author properly
            queries_to_try = []

            # Special handling for "1984" - try exact title first
            if "1984" in title.lower():
                base_query = title
                if author:
                    base_query += f" author:{author}"
                queries_to_try.append(base_query)

                # Also try alternative title
                if "nineteen eighty-four" not in title.lower():
                    alt_query = "nineteen eighty-four"
                    if author:
                        alt_query += f" author:{author}"
                    queries_to_try.append(alt_query)
            else:
                base_query = title
                if author:
                    base_query += f" author:{author}"
                queries_to_try.append(base_query)
                # Fallback to title-only if no results
                queries_to_try.append(title)

            # Try multiple queries if first one fails
            for query in queries_to_try[:2]:  # Try at most 2 queries
                params = {
                    "q": query,
                    "limit": 1,
                    "fields": "key,title,author_name,first_publish_year,publisher,subject,cover_i,isbn,ratings_average,ratings_count",
                }

                # Add year parameter if provided
                if year:
                    params["first_publish_year"] = year

                # Build URL with parameters
                url = f"{self.open_library_url}?{urllib.parse.urlencode(params)}"

                # Make request
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode("utf-8"))

                if data.get("docs"):
                    doc = data["docs"][0]
                    return {
                        "title": doc.get("title", ""),
                        "author": ", ".join(doc.get("author_name", [])),
                        "year": str(doc.get("first_publish_year", "")),
                        "publisher": ", ".join(doc.get("publisher", [])),
                        "plot": self._get_open_library_description(doc.get("key", "")),
                        "genre": ", ".join(
                            doc.get("subject", [])[:3]
                        ),  # Limit to first 3 genres
                        "rating": str(doc.get("ratings_average", "")),
                        "ratings_count": str(doc.get("ratings_count", "")),
                        "source": "open_library",
                    }

            return None
        except Exception as e:
            print(f"Open Library API error: {e}")
            return None

    def _get_open_library_description(self, work_key: str) -> str:
        """Get description from Open Library work."""
        try:
            # Extract work ID from key (e.g., "/works/OL1168083W" -> "OL1168083W")
            work_id = work_key.split("/")[-1] if "/" in work_key else work_key

            url = f"{self.open_library_work_url}/{work_id}.json"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=6) as response:
                data = json.loads(response.read().decode("utf-8"))
                return self._extract_description(data.get("description", ""))
        except Exception:
            return ""

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

        year_match = re.search(r"\b(19|20)\d{2}\b", published_date)
        return year_match.group(0) if year_match else published_date

    def _extract_isbn(self, identifiers: List[Dict]) -> str:
        """Extract ISBN from industry identifiers."""
        if not identifiers:
            return ""

        # Prefer ISBN-13, fallback to ISBN-10
        for identifier in identifiers:
            if identifier.get("type") == "ISBN_13":
                return identifier.get("identifier", "")

        for identifier in identifiers:
            if identifier.get("type") == "ISBN_10":
                return identifier.get("identifier", "")

        return ""

    def _extract_description(self, description) -> str:
        """Extract description from various formats."""
        if isinstance(description, str):
            return description
        elif isinstance(description, dict):
            return description.get("value", "")
        else:
            return str(description) if description else ""

    def _fetch_from_wikidata(
        self, title: str, author: str = None, year: str = None
    ) -> Optional[Dict]:
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
                safe_title.replace(" ", ""),
                safe_title.replace(" and ", " & ").replace(" And ", " & "),
            ]

            # Create a more flexible query with multiple title options
            title_conditions = []
            for term in search_terms:
                title_conditions.append(f'CONTAINS(LCASE(?bookLabel), LCASE("{term}"))')

            title_filter = " || ".join(title_conditions)

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
                SELECT DISTINCT ?book ?bookLabel ?bookDescription WHERE {{
                  ?author rdfs:label "George Orwell"@en.
                  ?book wdt:P50 ?author.
                  {{ ?book rdfs:label ?label. }}
                  UNION
                  {{ ?book skos:altLabel ?label. }}
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
            req.add_header(
                "User-Agent",
                "AbCS-Audiobook-Collector/1.0 (Educational audiobook metadata tool)",
            )
            req.add_header("Accept", "application/sparql-results+json")

            with urllib.request.urlopen(req, timeout=6) as response:
                response_text = response.read().decode("utf-8")

                # Check if we got JSON
                if not response_text.strip().startswith("{"):
                    print("WikiData: Got non-JSON response")
                    return None

                data = json.loads(response_text)

            # Parse results
            results = data.get("results", {}).get("bindings", [])

            if results:
                result = results[0]  # Take first result

                # Extract basic metadata
                metadata = {
                    "title": self._get_sparql_value(result, "bookLabel"),
                    "author": self._get_sparql_value(result, "authorLabel"),
                    "source": "WikiData",
                }

                return metadata if metadata["title"] else None
        except Exception as e:
            print(f"WikiData API error: {e}")
            return None

    def _get_sparql_value(self, result: dict, field: str) -> str:
        """Extract value from SPARQL result binding."""
        try:
            if field in result and result[field]:
                return result[field].get("value", "").strip()
        except Exception:
            pass
        return ""

    def _strip_series_number(self, title: str) -> tuple[str, str]:
        """Strip series number from title and return (clean_title, series_number)."""
        if not title:
            return "", ""

        # Patterns to match series numbers
        patterns = [
            r"^(.*?)\s*-\s*(\d+)$",  # "Title - 09"
            r"^(.*?)\s*#\s*(\d+)$",  # "Title #09"
            r"^(.*?)\s*Book\s*(\d+)$",  # "Title Book 09"
            r"^(.*?)\s*Volume\s*(\d+)$",  # "Title Volume 09"
            r"^(\d+)\s*(.*?)$",  # "09 Title"
        ]

        for pattern in patterns:
            match = re.match(pattern, title.strip(), re.IGNORECASE)
            if match:
                if pattern == r"^(\d+)\s*(.*?)$":
                    # Number first pattern
                    series_number = match.group(1)
                    clean_title = match.group(2)
                else:
                    # Title first patterns
                    clean_title = match.group(1)
                    series_number = match.group(2)

                # Clean up the title
                clean_title = clean_title.strip()
                if clean_title:
                    return clean_title, series_number

        # No series number found
        return title.strip(), ""

    def _move_article_to_end(self, title: str) -> str:
        """Move leading articles 'The', 'A', 'An' to end of title."""
        if not title:
            return title

        articles = ["The ", "A ", "An "]
        for article in articles:
            if title.startswith(article):
                # Remove article and any extra spaces
                title_without_article = title[len(article) :].strip()
                # Add article to end with comma
                return f"{title_without_article}, {article.strip()}"

        return title

    def _clean_text_field(self, text: str) -> str:
        """Clean text field: remove extra spaces, special chars, capitalize properly."""
        if not text:
            return ""

        # Convert multiple spaces to single space and trim
        text = re.sub(r"\s+", " ", text.strip())

        # Remove non-alphanumeric characters from start
        text = re.sub(r"^[^a-zA-Z0-9]+", "", text)

        # Remove special characters (keep basic punctuation)
        text = re.sub(r'[^\w\s\-\.,:;\'"!?()]', " ", text)

        # Clean up any extra spaces again
        text = re.sub(r"\s+", " ", text.strip())

        return text

    def _apply_title_transformations(
        self, title: str, move_articles: bool = False
    ) -> str:
        """Apply title transformations: strip series, move articles, clean."""
        # Strip series number first
        clean_title, series_number = self._strip_series_number(title)

        # Move articles to end if requested
        if move_articles:
            clean_title = self._move_article_to_end(clean_title)

        # Clean the title
        clean_title = self._clean_text_field(clean_title)

        # Re-add series number if it existed
        if series_number:
            clean_title = f"{clean_title} - {series_number}"

        return clean_title

    def _apply_author_transformations(
        self, author: str, flip_name: bool = False
    ) -> str:
        """Apply author transformations: flip name if requested, clean."""
        if not author:
            return ""

        # Clean the author name first
        author = self._clean_text_field(author)

        # Flip name if requested (John Smith -> Smith, John)
        if flip_name and "," not in author:
            parts = author.split()
            if len(parts) >= 2:
                # Last name first, then first name
                author = f"{parts[-1]}, {' '.join(parts[:-1])}"

        return author

    def clean_web_data_for_storage(
        self, web_data: Dict, move_articles: bool = False, flip_author: bool = False
    ) -> Dict:
        """Clean web data according to user preferences before storing in database."""
        if not web_data:
            return web_data

        cleaned_data = web_data.copy()

        # Clean title
        if "title" in cleaned_data:
            cleaned_data["title"] = self._apply_title_transformations(
                cleaned_data["title"], move_articles
            )

        # Clean author
        if "author" in cleaned_data:
            cleaned_data["author"] = self._apply_author_transformations(
                cleaned_data["author"], flip_author
            )

        # Clean other text fields
        for field in ["publisher", "genre", "plot"]:
            if field in cleaned_data:
                cleaned_data[field] = self._clean_text_field(cleaned_data[field])

        # Clean series
        if "series" in cleaned_data:
            cleaned_data["series"] = self._clean_text_field(cleaned_data["series"])

        return cleaned_data
