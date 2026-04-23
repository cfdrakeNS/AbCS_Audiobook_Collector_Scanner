# Web Search Improvement Specification

**Status:** IMPLEMENTED  
**Applies to:** `src/web/web_book_api.py` (search matching logic, lines 100-146)

## Overview
To improve web metadata search accuracy and avoid mismatched authors/titles.

---

## 1. Author Last Name Check (IMPLEMENTED)

**Requirement:**
- Extract the last name from the DB author (e.g., "Agatha Christie" → "Christie").
- Only accept web results where the web author string contains this last name (case-insensitive, ignore punctuation).

**Implementation Location:** `src/web/web_book_api.py` in `get_book_metadata()` method lines 100-146

**Proposed Implementation:**
```python
def _extract_last_name(self, author: str) -> str:
    """Extract last name from author string."""
    if not author:
        return ""
    # Handle "Last, First" format
    if "," in author:
        return author.split(",")[0].strip()
    # Handle "First Last" format
    parts = author.strip().split()
    return parts[-1] if parts else ""

def _author_matches(self, db_author: str, web_author: str) -> bool:
    """Check if web author contains DB author's last name."""
    last_name = self._extract_last_name(db_author)
    if not last_name:
        return True  # Can't verify, allow it
    return last_name.lower() in web_author.lower()
```

---

## 2. Title Word Match - 50% Rule (IMPLEMENTED)

**Requirement:**
- Split the DB title into words (ignoring common stopwords and punctuation).
- Split the web result title into words.
- Count how many words from the DB title appear in the web title.
- Only accept the result if at least 50% of the DB title words are present in the web title.

**Implementation Location:** `src/web/web_book_api.py` in `get_book_metadata()` method lines 100-146

**Proposed Implementation:**
```python
# Common stopwords to ignore
STOPWORDS = {"the", "a", "an", "and", "or", "of", "in", "on", "to", "for"}

def _title_word_match_score(self, db_title: str, web_title: str) -> float:
    """Calculate percentage of DB title words found in web title."""
    if not db_title or not web_title:
        return 0.0
    
    # Clean and split titles
    db_words = set(re.findall(r'\b\w+\b', db_title.lower())) - STOPWORDS
    web_words = set(re.findall(r'\b\w+\b', web_title.lower()))
    
    if not db_words:
        return 1.0  # No meaningful words to match
    
    matches = len(db_words & web_words)
    return matches / len(db_words)

def _title_matches(self, db_title: str, web_title: str) -> bool:
    """Check if at least 50% of DB title words appear in web title."""
    return self._title_word_match_score(db_title, web_title) >= 0.5
```

---

## Current Implementation Status

**IMPLEMENTED - Tiered Confidence Matching (v2):**
- Author last name verification (lines 32-48)
- Title word match with 50% threshold (lines 50-67)
- Tiered matching that accepts books with rating/genre/series even without plot
- Substring title matching as fallback when author matches

---

## Integration Points

**File:** `src/web/web_book_api.py`  
**Method:** `get_book_metadata()`  
**Current location for match check:** Lines 139-176

**Integration Example (Tiered Confidence - Plot Not Required):**
```python
# Tiered confidence matching - works even without plot
is_real_match = False
if metadata:
    title_score = self._title_word_match_score(search_title, metadata.get("title", ""))
    author_match = self._author_matches(search_author, metadata.get("author", ""))
    
    # Check for any useful metadata (plot, rating, genre, series)
    has_metadata = any([
        metadata.get("plot"),
        metadata.get("rating"),
        metadata.get("genre"),
        metadata.get("series")
    ])
    
    # Check if titles contain each other
    web_title_lower = metadata.get("title", "").lower()
    search_title_lower = (search_title or "").lower()
    title_contains = search_title_lower and (
        search_title_lower in web_title_lower or
        web_title_lower in search_title_lower
    )
    
    # Tier 1: Both title (>=50%) and author match
    if title_score >= 0.5 and author_match:
        is_real_match = True
    # Tier 2: Perfect title match + has metadata
    elif title_score >= 1.0 and has_metadata:
        is_real_match = True
    # Tier 3: Author match + title contains search
    elif author_match and title_contains:
        is_real_match = True
    # Tier 4: Good title match + has metadata
    elif title_score >= 0.5 and has_metadata:
        is_real_match = True
```

---

## 3. Plot Enrichment from Open Library + Wikipedia (IMPLEMENTED)

**Problem:** ~50% of Google Books matches return without plot data.

**Solution:** After accepting a match, if plot is missing, try Open Library then Wikipedia.

**Implementation:**
- `_fetch_plot_from_open_library(title, author)` - Searches OL and returns description
- `_fetch_plot_from_wikipedia(title, author)` - Searches Wikipedia and returns page extract
- Called after tiered matching accepts a result but has no plot
- Tries Open Library first, then Wikipedia as fallback
- Wikipedia: skips author bios, verifies author in extract, filters disambiguation pages

**Note:** Wikipedia only has pages for notable/award-winning books or film adaptations. Most genre fiction won't have dedicated pages.

**Expected Result**
- Prevents mismatches where the author is completely different
- Filters out web results with unrelated titles
- Improves overall search accuracy for web metadata
- Accepts more valid results by not requiring plot (uses rating/genre/series instead)
- Better coverage from Google Books, Open Library, WikiData APIs
- **More books get plot summaries** via cross-source enrichment

