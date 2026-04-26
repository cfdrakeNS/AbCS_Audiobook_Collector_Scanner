"""
Book Helpers - Centralized book application logic for web metadata.

This module provides utilities for applying web metadata to book objects
based on field differences and checkbox states.
"""

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from src.models.book import Book


def apply_web_field(
    book: "Book",
    field_name: str,
    web_value: str,
    field_differences: dict,
    checkbox_visible: Callable[[], bool],
    is_checked: Callable[[], bool],
    apply_func: Callable[[str], None],
    applied_fields: list,
) -> None:
    """
    Apply web field value to book based on difference state and checkbox.
    
    Pattern:
    - If field differs: apply if checkbox is checked
    - If DB was empty: auto-apply web data
    
    Args:
        book: Book object to update
        field_name: Name of field (e.g., "title", "author")
        web_value: Value from web metadata
        field_differences: Dict of fields that differ between DB and web
        checkbox_visible: Function returning if checkbox widget is visible
        is_checked: Function returning if checkbox is checked
        apply_func: Function to apply the value (receives web_value)
        applied_fields: List to append field_name to if applied
    """
    if field_name not in field_differences:
        return
    
    if checkbox_visible():
        # Field differs - apply if checked
        if is_checked():
            apply_func(web_value)
            applied_fields.append(field_name.capitalize())
    else:
        # DB field was empty - auto-apply web data
        apply_func(web_value)
        applied_fields.append(field_name.capitalize())


def apply_author_field(
    book: "Book",
    author_queries,
    author_name: str,
    field_differences: dict,
    checkbox_visible: Callable[[], bool],
    is_checked: Callable[[], bool],
    applied_fields: list,
) -> None:
    """
    Apply author field with lookup/insert logic.
    
    Gets or creates author record and assigns author_id to book.
    """
    if "author" not in field_differences:
        return
    
    def apply_author(name: str) -> None:
        if name:
            author = author_queries.get_by_name(name)
            if not author:
                author_id = author_queries.insert(name)
            else:
                author_id = author.author_id
            book.author_id = author_id
    
    if checkbox_visible():
        if is_checked():
            apply_author(author_name)
            applied_fields.append("Author")
    else:
        apply_author(author_name)
        applied_fields.append("Author")


def apply_series_field(
    book: "Book",
    series_queries,
    series_text: str,
    field_differences: dict,
    checkbox_visible: Callable[[], bool],
    is_checked: Callable[[], bool],
    applied_fields: list,
) -> None:
    """
    Apply series field with "Series Name - Number" parsing.
    
    Parses series name and optional number, gets or creates series record.
    """
    if "series" not in field_differences:
        return
    
    def apply_series(text: str) -> None:
        if not text:
            book.series_id = None
            book.series_number = None
            return
        
        series_id = None
        series_number = None
        
        if " - " in text:
            parts = text.split(" - ")
            series_name = parts[0].strip()
            try:
                series_number = int(parts[1].strip())
            except ValueError:
                series_number = None
        else:
            series_name = text
        
        if series_name:
            series = series_queries.get_by_name(series_name)
            if not series:
                series_id = series_queries.insert(series_name)
            else:
                series_id = series.series_id
        
        book.series_id = series_id
        book.series_number = series_number
    
    if checkbox_visible():
        if is_checked():
            apply_series(series_text)
            applied_fields.append("Series")
    else:
        apply_series(series_text)
        applied_fields.append("Series")
