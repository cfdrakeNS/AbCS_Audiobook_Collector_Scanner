"""
Web Book API - Audio Book Collection
Fetches book metadata from Open Library, Google Books, and WikiData APIs (in that order).
"""

import json
import urllib.request
import urllib.parse
import re
import time
from typing import Optional, Dict, List

# Common stopwords to ignore in title matching
STOPWORDS = {"the", "a", "an", "and", "or", "of", "in", "on", "to", "for"}

# Leading honorifics to strip from author search (Sir Arthur Conan Doyle -> Arthur Conan Doyle)
AUTHOR_HONORIFIC_PREFIX = re.compile(
    r"^(?:sir|dame|dr\.?|prof\.?|mr\.?|mrs\.?|ms\.?|lord|lady)\s+",
    re.IGNORECASE,
)


class WebBookAPI:
    """API client for fetching book metadata from web sources."""

    def _move_article_to_beginning(self, title: str) -> str:
        """Move trailing articles (comma, optional space, then article) to beginning of title."""
        if not title:
            return title
        # Accept variations: ',the', ', the', ',  the', ',An', etc.
        match = re.match(r"^(.*?)[,\s]+(the|a|an)$", title.strip(), re.IGNORECASE)
        if match:
            base = match.group(1).strip()
            article = match.group(2).capitalize()
            return f"{article} {base}"
        return title

    def _strip_author_honorifics(self, author: str) -> str:
        """Remove leading titles/honorifics used in library author fields."""
        cleaned = (author or "").strip()
        while cleaned:
            match = AUTHOR_HONORIFIC_PREFIX.match(cleaned)
            if not match:
                break
            cleaned = cleaned[match.end() :].strip()
        return cleaned

    def _extract_last_name(self, author: str) -> str:
        """Extract last name from author string."""
        author = self._strip_author_honorifics(author)
        if not author:
            return ""
        # Handle "Last, First" format
        if "," in author:
            return author.split(",")[0].strip()
        # Handle "First Last" format
        parts = author.strip().split()
        return parts[-1] if parts else ""

    def _author_matches(self, db_author: str, web_author: str) -> bool:
        """Check that web author contains the DB author's last name."""
        db_author = (db_author or "").strip()
        web_author = (web_author or "").strip()
        if not db_author or not web_author:
            return False
        last_name = self._extract_last_name(db_author)
        if not last_name:
            return False
        return last_name.lower() in web_author.lower()

    def _title_word_match_score(self, db_title: str, web_title: str) -> float:
        """Calculate percentage of DB title words found in web title."""
        if not db_title or not web_title:
            return 0.0

        # Clean and split titles
        db_words = set(re.findall(r"\b\w+\b", db_title.lower())) - STOPWORDS
        web_words = set(re.findall(r"\b\w+\b", web_title.lower()))

        if not db_words:
            return 1.0  # No meaningful words to match

        matches = len(db_words & web_words)
        return matches / len(db_words)

    def _title_matches(self, db_title: str, web_title: str) -> bool:
        """Check if at least 50% of DB title words appear in web title."""
        return self._title_word_match_score(db_title, web_title) >= 0.5

    def _metadata_matches_db(
        self,
        db_title: str,
        db_author: str,
        metadata: Optional[Dict],
        *,
        require_author_match: bool = True,
    ) -> bool:
        """Require title word match; optionally require DB last name in web author."""
        if not metadata:
            return False
        web_title = (metadata.get("title") or "").strip()
        if not web_title:
            return False
        if not self._title_matches(db_title, web_title):
            return False
        if not require_author_match:
            return True
        if not self._author_matches(db_author, metadata.get("author", "")):
            return False
        return True

    @staticmethod
    def _normalize_person_name(value: str) -> str:
        return re.sub(r"\s+", " ", (value or "").strip().lower())

    def _names_likely_same(self, left: str, right: str) -> bool:
        """True when two person names likely refer to the same individual."""
        left_norm = self._normalize_person_name(left)
        right_norm = self._normalize_person_name(right)
        if not left_norm or not right_norm:
            return False
        if left_norm == right_norm:
            return True
        left_last = self._extract_last_name(left).lower()
        right_last = self._extract_last_name(right).lower()
        return bool(left_last and left_last == right_last)

    @staticmethod
    def _likely_librivox_source(
        path: str | None = None,
        source: str | None = None,
        comments: str | None = None,
    ) -> bool:
        blob = " ".join([path or "", source or "", comments or ""]).lower()
        return "librivox" in blob

    def _should_use_title_only_fallback(
        self,
        author: str | None,
        *,
        narrator: str | None = None,
        path: str | None = None,
        source: str | None = None,
        comments: str | None = None,
        search_without_author: bool = False,
    ) -> bool:
        """Heuristics for Librivox-style rows where DB author may be the narrator."""
        if search_without_author:
            return True
        if not (author or "").strip():
            return True
        if self._names_likely_same(author, narrator or ""):
            return True
        return self._likely_librivox_source(path, source, comments)

    def __init__(self):
        """Initialize the API client."""
        self.google_books_url = "https://www.googleapis.com/books/v1/volumes"
        self.open_library_url = "https://openlibrary.org/search.json"
        self.open_library_work_url = "https://openlibrary.org/works"
        # WikiData SPARQL endpoint
        self.wikidata_url = "https://query.wikidata.org/sparql"
        # Wikipedia API for plot summaries
        self.wikipedia_url = "https://en.wikipedia.org/w/api.php"
        self._cache = {}  # Initialize cache to avoid hasattr checks
        self.CACHE_DURATION = 300  # seconds

    def get_book_metadata(
        self,
        title: str,
        author: str = None,
        year: str = None,
        refresh: int = 0,
        move_articles: bool = False,
        flip_author: bool = False,
        append_series_to_title: bool = True,
        *,
        narrator: str | None = None,
        path: str | None = None,
        source: str | None = None,
        comments: str | None = None,
        search_without_author: bool = False,
    ) -> Optional[Dict]:
        """
        Fetch book metadata from multiple web sources.

        Args:
            title: Book title
            author: Author name (optional)
            year: Ignored for search (library years are often wrong); kept for API compatibility
            refresh: 0=Open Library then Google Books then WikiData;
                     1=Google Books then WikiData (skip Open Library);
                     2=WikiData only
            move_articles: Move 'The', 'A', 'An' to end of title for search
            flip_author: Flip author name format for search
            narrator: Reader/narrator when tagged separately from author
            path: Book folder path (Librivox detection)
            source: Book source field (Librivox detection)
            comments: Book comments (Librivox detection)
            search_without_author: Force title-only matching after author search fails

        Returns:
            Dictionary with book metadata and source info, or None if not found
        """

        import time

        cache_key = (
            f"{title}|{author}|{refresh}|{narrator}|{path}|{source}|"
            f"{search_without_author}"
        )
        current_time = time.time()

        # Cache successful lookups only (do not cache failures).
        if hasattr(self, "_cache") and cache_key in self._cache:
            cached_time, cached_result = self._cache[cache_key]
            if (
                cached_result
                and cached_time
                and (current_time - cached_time) < self.CACHE_DURATION
            ):
                return cached_result
            if cached_time and (current_time - cached_time) >= self.CACHE_DURATION:
                del self._cache[cache_key]

        # Normalize title for search and comparison (do NOT append series number)
        search_title, series_number = self._strip_series_number(title)
        search_title = self._move_article_to_beginning(search_title)
        # Move articles to end logic removed for accessibility compliance
        search_title = self._clean_text_field(search_title)

        # Only append series number to title when SAVING, not for search/compare
        # The code that saves to DB should append series number if and only if a real series number is found

        # Author transformation: clean and strip honorifics for web search queries
        search_author = self._strip_author_honorifics(
            self._apply_author_transformations(author)
        )

        def _finish_metadata(
            metadata: Dict,
            source: str,
            first_attempt: bool,
        ) -> Dict:
            if append_series_to_title and series_number:
                if not metadata["title"].rstrip().endswith(f"- {series_number}"):
                    metadata["title"] = (
                        f"{metadata['title']} - {series_number}".strip()
                    )
            metadata["source"] = source
            metadata["first_attempt"] = first_attempt
            self._cache[cache_key] = (current_time, metadata)
            return metadata

        metadata = self._search_metadata_sources(
            search_title,
            search_author,
            refresh,
            require_author_match=True,
        )
        if metadata:
            return _finish_metadata(
                metadata,
                metadata.pop("_resolved_source", metadata.get("source", "")),
                first_attempt=True,
            )

        use_title_only = self._should_use_title_only_fallback(
            search_author,
            narrator=narrator,
            path=path,
            source=source,
            comments=comments,
            search_without_author=search_without_author,
        )
        if search_title and (use_title_only or search_author):
            metadata = self._search_metadata_sources(
                search_title,
                None,
                refresh,
                require_author_match=False,
            )
            if metadata:
                metadata["title_only_search"] = True
                return _finish_metadata(
                    metadata,
                    metadata.pop("_resolved_source", metadata.get("source", "")),
                    first_attempt=refresh >= 1,
                )

        return None

    def _search_metadata_sources(
        self,
        search_title: str,
        search_author: str | None,
        refresh: int,
        *,
        require_author_match: bool,
    ) -> Optional[Dict]:
        """Query Open Library, Google Books, and WikiData with shared match rules."""
        query_author = search_author if require_author_match else None

        if refresh == 0:
            try:
                metadata = self._fetch_from_open_library(
                    search_title,
                    query_author,
                    require_author_match=require_author_match,
                )
                if metadata:
                    metadata["_resolved_source"] = "open_library"
                    return metadata
            except Exception:
                pass

        if refresh <= 1:
            try:
                metadata = self._fetch_from_google_books(
                    search_title,
                    query_author,
                    require_author_match=require_author_match,
                )
                if metadata:
                    if not metadata.get("plot"):
                        plot = self._fetch_plot_from_open_library(
                            metadata.get("title", ""), metadata.get("author", "")
                        )
                        if not plot:
                            plot = self._fetch_plot_from_wikipedia(
                                metadata.get("title", ""), metadata.get("author", "")
                            )
                        if plot and not (
                            metadata.get("series")
                            and plot.strip().lower()
                            == metadata["series"].strip().lower()
                        ):
                            metadata["plot"] = plot
                    metadata["_resolved_source"] = "google_books"
                    return metadata
            except Exception:
                pass

        if refresh <= 2:
            try:
                metadata = self._fetch_from_wikidata(
                    search_title,
                    query_author,
                    require_author_match=require_author_match,
                )
                if metadata:
                    metadata["_resolved_source"] = "wikidata"
                    return metadata
            except Exception:
                pass

        return None

    def _google_item_to_metadata(self, item: dict) -> Optional[Dict]:
        """Build metadata dict from one Google Books API item."""
        volume_info = item.get("volumeInfo", {})
        if not volume_info.get("title"):
            return None

        series = ""
        series_number = ""

        series_info = volume_info.get("seriesInfo", {})
        if series_info:
            series_number = series_info.get("bookDisplayNumber", "")
            volume_series = series_info.get("volumeSeries", [])
            if volume_series:
                series = (
                    volume_series[0]
                    .get("seriesId", "")
                    .replace("_", " ")
                    .title()
                )

        subtitle = volume_info.get("subtitle", "")
        if subtitle and not series_number:
            patterns = [
                r"(?:book|volume|#)\s*(\d+)",
                r"(?:part|novel)\s*(\w+)",
            ]
            for pattern in patterns:
                match = re.search(pattern, subtitle, re.IGNORECASE)
                if match:
                    series_number = match.group(1)
                    series = re.sub(
                        pattern, "", subtitle, flags=re.IGNORECASE
                    ).strip(" -")
                    break

        description = volume_info.get("description", "")
        if description and not series_number:
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

        return {
            "title": volume_info.get("title", ""),
            "author": self._format_authors(volume_info.get("authors", [])),
            "year": self._extract_year(volume_info.get("publishedDate", "")),
            "publisher": volume_info.get("publisher", ""),
            "plot": volume_info.get("description", ""),
            "genre": self._format_categories(volume_info.get("categories", [])),
            "isbn": self._extract_isbn(volume_info.get("industryIdentifiers", [])),
            "rating": volume_info.get("averageRating", 0),
            "ratings_count": volume_info.get("ratingsCount", 0),
            "series": series,
            "series_number": series_number,
            "source": "Google Books",
            "confidence": 0.9,
        }

    def _fetch_from_google_books(
        self,
        title: str,
        author: str = None,
        *,
        require_author_match: bool = True,
    ) -> Optional[Dict]:
        """Fetch metadata from Google Books API."""
        try:
            # Build search query - use intitle and inauthor for better results
            query_parts = []
            if title:
                query_parts.append(f"intitle:{title}")
            if author:
                query_parts.append(f"inauthor:{author}")
            elif not require_author_match and title:
                query_parts = [title]
            query = " ".join(query_parts)

            # Include more fields to get series info and subtitle
            params = {
                "q": query,
                "maxResults": 10,
                "fields": "items(id,volumeInfo(title,subtitle,authors,publisher,publishedDate,description,industryIdentifiers,categories,averageRating,ratingsCount,seriesInfo))",
            }
            url = f"{self.google_books_url}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "AudiobookCollectorScanner/1.0")
            with urllib.request.urlopen(req, timeout=6) as response:
                data = json.loads(response.read().decode("utf-8"))

            if "items" in data and data["items"]:
                best_metadata = None
                best_title_score = -1.0

                for item in data["items"]:
                    candidate = self._google_item_to_metadata(item)
                    if not candidate:
                        continue
                    if not self._metadata_matches_db(
                        title,
                        author,
                        candidate,
                        require_author_match=require_author_match,
                    ):
                        continue
                    title_score = self._title_word_match_score(
                        title, candidate.get("title", "")
                    )
                    if title_score > best_title_score:
                        best_title_score = title_score
                        best_metadata = candidate

                if best_metadata:
                    return best_metadata
        except Exception as e:
            pass
        return None

    def _fetch_from_open_library(
        self,
        title: str,
        author: str = None,
        *,
        require_author_match: bool = True,
    ) -> Optional[Dict]:
        """Fetch metadata from Open Library API (title and author only; no DB year filter)."""
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
                if author:
                    queries_to_try.append(f"{title} author:{author}")
                    stripped_author = self._strip_author_honorifics(author)
                    if stripped_author and stripped_author.lower() != author.lower():
                        queries_to_try.append(f"{title} author:{stripped_author}")
                queries_to_try.append(title)

            seen_queries = set()
            for query in queries_to_try:
                if query in seen_queries:
                    continue
                seen_queries.add(query)
                if len(seen_queries) > 4:
                    break
                params = {
                    "q": query,
                    "limit": 10,
                    "fields": "key,title,author_name,first_publish_year,publisher,subject,cover_i,isbn,ratings_average,ratings_count",
                }

                url = f"{self.open_library_url}?{urllib.parse.urlencode(params)}"
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode("utf-8"))

                if data.get("docs"):
                    best_metadata = None
                    best_title_score = -1.0
                    best_work_key = ""
                    for doc in data["docs"]:
                        candidate = {
                            "title": doc.get("title", ""),
                            "author": ", ".join(doc.get("author_name", [])),
                            "year": str(doc.get("first_publish_year", "")),
                            "publisher": ", ".join(doc.get("publisher", [])),
                            "plot": "",
                            "genre": ", ".join(doc.get("subject", [])[:3]),
                            "rating": str(doc.get("ratings_average", "")),
                            "ratings_count": str(doc.get("ratings_count", "")),
                            "source": "open_library",
                        }
                        if not self._metadata_matches_db(
                            title,
                            author,
                            candidate,
                            require_author_match=require_author_match,
                        ):
                            continue
                        title_score = self._title_word_match_score(
                            title, candidate.get("title", "")
                        )
                        if title_score > best_title_score:
                            best_title_score = title_score
                            best_metadata = candidate
                            best_work_key = doc.get("key", "") or ""
                    if best_metadata:
                        if best_work_key:
                            best_metadata["plot"] = self._get_open_library_description(
                                best_work_key
                            )
                        return best_metadata

            return None
        except Exception as e:
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

    def _fetch_plot_from_open_library(self, title: str, author: str = None) -> str:
        """Search Open Library for a book and return its plot/description."""
        try:
            if not title:
                return ""

            # Build search query
            query = title
            if author:
                query += f" author:{author}"

            params = {
                "q": query,
                "limit": 3,
                "fields": "key,title,author_name,description",
            }

            url = f"{self.open_library_url}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "AbCS-Audiobook-Collector/1.0")

            with urllib.request.urlopen(req, timeout=8) as response:
                data = json.loads(response.read().decode("utf-8"))

            if not data.get("docs"):
                return ""

            # Find best match with plot
            for doc in data["docs"]:
                work_key = doc.get("key", "")
                if work_key:
                    plot = self._get_open_library_description(work_key)
                    if plot and len(plot) > 20:
                        return plot

            return ""
        except Exception:
            return ""

    def _fetch_plot_from_wikipedia(self, title: str, author: str = None) -> str:
        """Search Wikipedia for a book and return its summary/extract."""
        try:
            if not title:
                return ""

            # Build search query - be more specific to find book pages
            search_terms = [f"{title} novel", f"{title} book"]
            if author:
                search_terms.insert(0, f"{title} {author} novel")
                search_terms.insert(1, f"{title} {author} book")

            for search_query in search_terms:
                # Search for the page
                search_params = {
                    "action": "query",
                    "list": "search",
                    "srsearch": search_query,
                    "srlimit": 3,
                    "format": "json",
                    "origin": "*",
                }

                search_url = (
                    f"{self.wikipedia_url}?{urllib.parse.urlencode(search_params)}"
                )
                req = urllib.request.Request(search_url)
                req.add_header("User-Agent", "AbCS-Audiobook-Collector/1.0")

                with urllib.request.urlopen(req, timeout=8) as response:
                    search_data = json.loads(response.read().decode("utf-8"))

                if not search_data.get("query", {}).get("search"):
                    continue

                # Try each search result
                for result in search_data["query"]["search"][:2]:
                    page_title = result.get("title", "")
                    if not page_title:
                        continue

                    # Skip author biography pages (e.g., "John Connolly (author)")
                    if author:
                        author_parts = author.lower().split()
                        # If page title is just the author name, skip it
                        if all(part in page_title.lower() for part in author_parts):
                            if "(" in page_title or "author" in page_title.lower():
                                continue

                    # Get the extract/summary for this page
                    extract_params = {
                        "action": "query",
                        "prop": "extracts",
                        "explaintext": True,
                        "exsentences": 10,
                        "titles": page_title,
                        "format": "json",
                        "origin": "*",
                    }

                    extract_url = (
                        f"{self.wikipedia_url}?{urllib.parse.urlencode(extract_params)}"
                    )
                    req2 = urllib.request.Request(extract_url)
                    req2.add_header("User-Agent", "AbCS-Audiobook-Collector/1.0")

                    with urllib.request.urlopen(req2, timeout=8) as response2:
                        extract_data = json.loads(response2.read().decode("utf-8"))

                    pages = extract_data.get("query", {}).get("pages", {})
                    for _, page_data in pages.items():
                        extract = page_data.get("extract", "")
                        # Filter out disambiguation pages and short extracts
                        if extract and len(extract) > 50:
                            # Skip if it's a disambiguation page
                            if "may refer to" in extract.lower()[:100]:
                                continue
                            if "disambiguation" in page_data.get("title", "").lower():
                                continue
                            # Verify author appears in extract (if author provided)
                            if author:
                                author_last = author.split()[-1].lower()
                                if author_last not in extract.lower():
                                    continue
                            return extract

            return ""
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
        self,
        title: str,
        author: str = None,
        *,
        require_author_match: bool = True,
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
                    return None

                data = json.loads(response_text)

            # Parse results
            results = data.get("results", {}).get("bindings", [])

            best_metadata = None
            best_title_score = -1.0
            for result in results:
                metadata = {
                    "title": self._get_sparql_value(result, "bookLabel"),
                    "author": self._get_sparql_value(result, "authorLabel"),
                    "source": "WikiData",
                }
                if not metadata.get("title"):
                    continue
                if not self._metadata_matches_db(
                    title,
                    author,
                    metadata,
                    require_author_match=require_author_match,
                ):
                    continue
                title_score = self._title_word_match_score(
                    title, metadata.get("title", "")
                )
                if title_score > best_title_score:
                    best_title_score = title_score
                    best_metadata = metadata

            if best_metadata:
                return best_metadata
        except Exception as e:
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

        # Patterns to match series numbers (only if clearly separated)
        patterns = [
            r"^(.*?)\s*-\s*(\d+)$",  # "Title - 09"
            r"^(.*?)\s*#\s*(\d+)$",  # "Title #09"
            r"^(.*?)\s+Book\s*(\d+)$",  # "Title Book 09"
            r"^(.*?)\s+Volume\s*(\d+)$",  # "Title Volume 09"
            r"^(.*?)\s*,\s*(\d+)$",  # "Title, 09"
        ]

        for pattern in patterns:
            match = re.match(pattern, title.strip(), re.IGNORECASE)
            if match:
                clean_title = match.group(1).strip()
                series_number = match.group(2)
                if clean_title:
                    return clean_title, series_number

        # No series number found
        return title.strip(), ""

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

    def _is_redundant_plot(self, plot: str, series: str) -> bool:
        """Return True when the plot appears to be just a series label rather than a real description."""
        if not plot or not series:
            return False

        normalized_plot = re.sub(r"\s+", " ", plot.strip().lower())
        normalized_series = re.sub(r"\s+", " ", series.strip().lower())

        if normalized_plot == normalized_series:
            return True

        redundant_variants = [
            f"{normalized_series} series",
            f"{normalized_series} book",
            f"{normalized_series} books",
            f"book in the {normalized_series} series",
            f"series: {normalized_series}",
        ]
        if normalized_plot in redundant_variants:
            return True

        return False

    def _is_unlikely_series_name(
        self, series: str, title: str = "", plot: str = ""
    ) -> bool:
        """Return True when the series value is too long or looks like plot/article text."""
        if not series:
            return False

        normalized_series = re.sub(r"\s+", " ", series.strip())
        if len(normalized_series) > 90:
            return True
        if len(normalized_series.split()) > 12:
            return True
        if len(re.findall(r"[\.\?!]", normalized_series)) > 1:
            return True

        series_lower = normalized_series.lower()
        if "new york times" in series_lower or "bestselling author" in series_lower:
            return True
        if "novel" in series_lower and "chief inspector" in series_lower:
            return True

        if plot:
            normalized_plot = re.sub(r"\s+", " ", plot.strip().lower())
            if series_lower in normalized_plot and len(normalized_plot) > len(series_lower) + 20:
                return True

        if title:
            title_lower = title.strip().lower()
            if title_lower and title_lower in series_lower and len(series_lower) > len(title_lower) + 20:
                return True

        return False

    def _apply_title_transformations(
        self, title: str, move_articles: bool = False
    ) -> str:
        """Apply title transformations: strip series, move articles, clean."""
        # Strip series number first
        clean_title, series_number = self._strip_series_number(title)

        # Move articles to end logic removed for accessibility compliance

        # Clean the title
        clean_title = self._clean_text_field(clean_title)

        # Re-add series number if it existed
        if series_number:
            clean_title = f"{clean_title} - {series_number}"

        return clean_title

    def _apply_author_transformations(self, author: str) -> str:
        """Apply author transformations: clean only (no flipping)."""
        if not author:
            return ""

        # Clean the author name only
        author = self._clean_text_field(author)
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
                cleaned_data["title"], False
            )

        # Clean author
        if "author" in cleaned_data:
            cleaned_data["author"] = self._apply_author_transformations(
                cleaned_data["author"]
            )

        # Clean other text fields
        for field in ["publisher", "genre", "plot"]:
            if field in cleaned_data:
                cleaned_data[field] = self._clean_text_field(cleaned_data[field])

        # Clean series
        if "series" in cleaned_data:
            cleaned_data["series"] = self._clean_text_field(cleaned_data["series"])
            if self._is_unlikely_series_name(
                cleaned_data["series"],
                title=cleaned_data.get("title", ""),
                plot=cleaned_data.get("plot", ""),
            ):
                cleaned_data["series"] = ""

        # Remove plot text that is just the series name or a series-only label
        if "plot" in cleaned_data and cleaned_data.get("plot"):
            if self._is_redundant_plot(cleaned_data["plot"], cleaned_data.get("series", "")):
                cleaned_data["plot"] = ""

        return cleaned_data
