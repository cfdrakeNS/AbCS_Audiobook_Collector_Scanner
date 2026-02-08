"""
Validator for audiobook import data.
Detects errors and issues in imported audiobook metadata.
"""

from typing import List, Dict, Any
import re


class ImportValidator:
    """
    Validates imported audiobook data and identifies errors.
    Matches the error detection from MS Access version.
    """
    
    def __init__(self):
        """Initialize validator."""
        pass
    
    def validate_book(self, book: Dict[str, Any]) -> List[str]:
        """
        Validate a book record and return list of errors.
        
        Args:
            book: Book dictionary from scanner
            
        Returns:
            List of error messages
        """
        errors = []
        
        # Check for blank title
        if not book.get('title') or book['title'].strip() == '':
            errors.append("Title Blank")
        
        # Check for blank author
        author = book.get('author', '').strip()
        if not author:
            errors.append("Author Blank")
        elif author.lower() == 'unknown artist':
            errors.append("Author Name is 'Unknown Artist'")
        elif author.lower() == 'artist album':
            errors.append("Author Name is 'Artist Album'")
        
        # Check if author name starts with non-alphabetic character
        if author and not author[0].isalpha():
            errors.append("Author Name Starts with non-alphabetic character")
        
        # Check if title contains author name
        title = book.get('title', '').strip()
        if title and author and author.lower() in title.lower():
            errors.append("Author name in Title")
        
        # Check if author contains title
        if author and title and title.lower() in author.lower():
            errors.append("Title in Author name")
        
        # Check for files not found (already in errors from scanner)
        if book.get('errors'):
            # File read errors already present
            pass
        
        return errors
    
    def is_duplicate(self, book: Dict[str, Any], existing_books: List[Dict[str, Any]]) -> bool:
        """
        Check if book is a duplicate of an existing book.
        
        Args:
            book: Book to check
            existing_books: List of existing books
            
        Returns:
            True if duplicate found
        """
        title = book.get('title', '').strip().lower()
        author = book.get('author', '').strip().lower()
        year = book.get('year')
        
        for existing in existing_books:
            if (existing.get('title', '').strip().lower() == title and
                existing.get('author', '').strip().lower() == author and
                existing.get('year') == year):
                return True
        
        return False
    
    def flip_author_name(self, name: str) -> str:
        """
        Flip author name from "First Last" to "Last, First".
        
        Args:
            name: Author name
            
        Returns:
            Flipped name
        """
        if not name or ',' in name:
            # Already in Last, First format or empty
            return name
        
        parts = name.strip().split()
        if len(parts) < 2:
            return name
        
        # Simple flip: last word is last name
        last_name = parts[-1]
        first_names = ' '.join(parts[:-1])
        return f"{last_name}, {first_names}"
    
    def normalize_title(self, title: str) -> str:
        """
        Normalize title by removing extra whitespace and special characters.
        
        Args:
            title: Book title
            
        Returns:
            Normalized title
        """
        # Remove extra whitespace
        title = ' '.join(title.split())
        
        # Remove common problematic patterns
        title = re.sub(r'\s*\(unabridged\)\s*', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*\[unabridged\]\s*', '', title, flags=re.IGNORECASE)
        
        return title.strip()
    
    def categorize_error(self, error: str) -> str:
        """
        Categorize error for display.
        
        Args:
            error: Error message
            
        Returns:
            Error category: 'parse', 'read', or 'warning'
        """
        read_errors = ['Error reading file', 'File not found', 'corrupted']
        
        if any(re_err in error for re_err in read_errors):
            return 'read'
        
        warning_errors = ['Author name in Title', 'Title in Author']
        if any(warn in error for warn in warning_errors):
            return 'warning'
        
        return 'parse'
