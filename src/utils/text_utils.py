"""
Text Utilities - Unified text normalization and similarity functions.

Centralizes fuzzy matching logic to eliminate duplication between:
- validator.py (import validation)
- book_list_import_window.py (list import duplicate checking)
"""

import string
from difflib import SequenceMatcher


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
