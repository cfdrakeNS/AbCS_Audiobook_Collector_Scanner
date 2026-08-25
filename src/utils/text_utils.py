"""
Text Utilities - Unified text normalization and similarity functions.

Centralizes fuzzy matching logic to eliminate duplication between:
- validator.py (import validation)
- book_list_import_window.py (list import duplicate checking)
"""

import re
import string
from difflib import SequenceMatcher


_TRAILING_ARTICLE_RE = re.compile(r"^(.*?),\s*(the|a|an)\s*$", re.IGNORECASE)
_TRAILING_PARENS_RE = re.compile(r"\s*\([^)]*\)\s*$")

# Series suffix patterns aligned with web_book_api._strip_series_number, plus decimals
# (e.g. "Busted - 6.5"). Import-only; web metadata is unchanged.
_SERIES_NUMBER_PATTERNS = (
    r"^(.*?)\s*-\s*(\d+(?:\.\d+)?)$",  # "Title - 09", "Title - 6.5"
    r"^(.*?)\s*#\s*(\d+(?:\.\d+)?)$",  # "Title #09"
    r"^(.*?)\s+Book\s*(\d+(?:\.\d+)?)$",  # "Title Book 09"
    r"^(.*?)\s+Volume\s*(\d+(?:\.\d+)?)$",  # "Title Volume 09"
    r"^(.*?)\s*,\s*(\d+)$",  # "Title, 09" (integer only; comma-year guard below)
)


def _looks_like_year(number: str) -> bool:
    """True when digits are probably a publication year, not a series index."""
    digits = re.sub(r"[^\d]", "", str(number or ""))
    if len(digits) != 4:
        return False
    try:
        value = int(digits)
    except ValueError:
        return False
    return 1700 <= value <= 2099


def strip_series_number(title: str) -> str:
    """Return title with trailing series number removed when clearly separated.

    Mirrors web_book_api._strip_series_number for book-list import compare only.
    """
    if not isinstance(title, str) or not title.strip():
        return ""

    t = title.strip()
    for pattern in _SERIES_NUMBER_PATTERNS:
        match = re.match(pattern, t, re.IGNORECASE)
        if not match:
            continue
        clean_title = match.group(1).strip()
        series_number = match.group(2)
        if clean_title and not _looks_like_year(series_number):
            return clean_title

    return t


def pre_normalize_title(title: str) -> str:
    """Pre-process a title before aggressive normalization for import comparison.

    Prepares DB and sheet titles the same way web metadata prepares a DB title
    for search (series strip, parenthetical series, article move). Does not
    modify web_metadata code paths.

    Steps applied (in order):
    1. Strip separated series suffix: ``Triptych - 01``, ``Busted - 6.5``, etc.
    2. Strip trailing parenthetical series/subtitle markers when series-like.
    3. Move trailing article: ``Hobbit, The`` → ``The Hobbit``.
    """
    if not isinstance(title, str):
        return ""
    t = title.strip()

    t = strip_series_number(t)

    # Strip series annotation in parentheses at the end of the title.
    # Only fires when the content looks like a series marker.
    paren_match = _TRAILING_PARENS_RE.search(t)
    if paren_match:
        inner = t[paren_match.start() + 1 : paren_match.end() - 1].lower()
        if re.search(r"#|\bbook\b|\bvol\b|\bvolume\b|\bseries\b|\bpart\b", inner):
            t = t[: paren_match.start()].strip()
        elif re.search(r"\d", inner):
            # e.g. "Bury Your Dead (Armand Gamache 6)"
            t = t[: paren_match.start()].strip()

    # Move trailing comma-article: "Title, The" → "The Title"
    art_match = _TRAILING_ARTICLE_RE.match(t)
    if art_match:
        base = art_match.group(1).strip()
        article = art_match.group(2).capitalize()
        t = f"{article} {base}"

    return t


def compare_normalize_title(title: str) -> str:
    """Normalize a title for import duplicate / read-date comparison."""
    return normalize_title(pre_normalize_title(title), aggressive=True)


def normalize_title(title: str, aggressive: bool = False) -> str:
    """
    Normalize title for comparison.
    
    Args:
        title: Raw title string
        aggressive: If True, removes all spaces and punctuation.
                   If False, only lowercase and strip.
    
    Returns:
        Normalized title string
    """
    if not isinstance(title, str):
        return ""
    
    t = title.strip().lower()
    
    if aggressive:
        # Remove all spaces and punctuation
        t = "".join(
            c for c in t if c not in string.whitespace and c not in string.punctuation
        )
    
    return t


def normalize_author(author: str, aggressive: bool = False) -> str:
    """
    Normalize author name for comparison.
    
    Args:
        author: Raw author string
        aggressive: If True, removes all spaces and punctuation.
                   If False, only lowercase and strip.
    
    Returns:
        Normalized author string
    """
    if not isinstance(author, str):
        return ""
    
    a = author.strip().lower()
    
    if aggressive:
        # Remove spaces and punctuation
        a = "".join(
            c for c in a if c not in string.whitespace and c not in string.punctuation
        )
    
    return a


def similarity_ratio(left: str, right: str) -> float:
    """
    Calculate normalized text similarity score from 0.0 to 1.0.
    
    Uses difflib.SequenceMatcher for fuzzy comparison.
    
    Args:
        left: First string to compare
        right: Second string to compare
    
    Returns:
        Similarity ratio from 0.0 (completely different) to 1.0 (identical)
    """
    if not left or not right:
        return 0.0
    
    if left == right:
        return 1.0
    
    return SequenceMatcher(None, left, right).ratio()


def similarity_percentage(left: str, right: str) -> float:
    """
    Calculate text similarity as percentage from 0 to 100.
    
    Convenience wrapper around similarity_ratio() for use with
    threshold values typically stored as integers (0-100).
    
    Args:
        left: First string to compare
        right: Second string to compare
    
    Returns:
        Similarity percentage from 0 to 100
    """
    return similarity_ratio(left, right) * 100
