"""Tests for web fetch progress message numbering."""

from src.web.web_book_api import _source_progress_message


def test_source_progress_message_fixed_numbers():
    assert _source_progress_message("open_library") == "Trying source 1: Open Library…"
    assert _source_progress_message("google_books") == "Trying source 2: Google Books…"
    assert _source_progress_message("wikidata") == "Trying source 3: WikiData…"
