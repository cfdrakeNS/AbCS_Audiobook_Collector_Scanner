"""Unit tests for WebBookAPI match gates, plot helpers, and search helpers."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from src.web.web_book_api import STOPWORDS, WebBookAPI, _clear_source_cooldown


@pytest.fixture
def api(web_api):
    return web_api


def test_stopwords():
    """Test that STOPWORDS constant exists."""
    assert "the" in STOPWORDS
    assert "and" in STOPWORDS
    assert "of" in STOPWORDS
    print("[PASS] STOPWORDS constant defined")

def test_extract_last_name():
    """Test _extract_last_name with various formats."""
    api = WebBookAPI()

    # "First Last" format
    assert api._extract_last_name("Agatha Christie") == "Christie"
    assert api._extract_last_name("Arthur Conan Doyle") == "Doyle"

    # "Last, First" format
    assert api._extract_last_name("Christie, Agatha") == "Christie"
    assert api._extract_last_name("Doyle, Arthur Conan") == "Doyle"

    # Edge cases
    assert api._extract_last_name("") == ""
    assert api._extract_last_name("Madonna") == "Madonna"  # Single name

    print("[PASS] _extract_last_name works correctly")

def test_author_matches():
    """Test _author_matches logic."""
    api = WebBookAPI()

    # Matching cases
    assert api._author_matches("Agatha Christie", "Agatha Christie") == True
    assert api._author_matches("Agatha Christie", "Christie, Agatha") == True
    assert api._author_matches("Christie, Agatha", "Agatha Christie") == True

    # Non-matching cases
    assert api._author_matches("Agatha Christie", "Stephen King") == False
    assert api._author_matches("Agatha Christie", "Arthur Conan Doyle") == False

    # Empty DB or web author must not match (collection always has an author)
    assert api._author_matches("", "Stephen King") == False
    assert api._author_matches("Agatha Christie", "") == False

    # Case insensitive
    assert api._author_matches("agatha christie", "AGATHA CHRISTIE") == True

    print("[PASS] _author_matches works correctly")

def test_title_word_match_score():
    """Test _title_word_match_score calculation."""
    api = WebBookAPI()

    # Perfect match
    score = api._title_word_match_score("The Great Gatsby", "The Great Gatsby")
    assert score == 1.0, f"Expected 1.0, got {score}"

    # 50% match (1 of 2 meaningful words)
    score = api._title_word_match_score("Great Gatsby", "Gatsby Returns")
    assert score == 0.5, f"Expected 0.5, got {score}"

    # Stopwords should be ignored
    score = api._title_word_match_score("The Great Gatsby", "A Great Gatsby")
    assert score == 1.0, f"Expected 1.0 (stopwords ignored), got {score}"

    # Empty titles
    score = api._title_word_match_score("", "Something")
    assert score == 0.0, f"Expected 0.0, got {score}"

    print("[PASS] _title_word_match_score works correctly")

def test_title_matches():
    """Test _title_matches 50% threshold."""
    api = WebBookAPI()

    # Exactly 50% should pass
    assert api._title_matches("Great Gatsby", "Gatsby Returns") == True

    # Above 50%
    assert api._title_matches("Great Gatsby", "The Great Gatsby") == True

    # Below 50%
    assert api._title_matches("Great Gatsby Book", "Gatsby Returns") == False  # 1/3

    # Perfect match
    assert api._title_matches("Dune", "Dune") == True

    print("[PASS] _title_matches works correctly")

def test_clean_web_data_for_storage_removes_series_plot():
    """Test that plot values equal to series names are cleared before UI update/db save."""
    api = WebBookAPI()

    web_data = {
        "title": "A Great Mystery",
        "author": "Louise Penny",
        "series": "How The Light Gets In",
        "plot": "How The Light Gets In",
    }

    cleaned = api.clean_web_data_for_storage(web_data)
    assert cleaned["plot"] == ""

    web_data["plot"] = "How The Light Gets In series"
    cleaned = api.clean_web_data_for_storage(web_data)
    assert cleaned["plot"] == ""

    print("[PASS] clean_web_data_for_storage filters redundant series plot text")

def test_clean_web_data_for_storage_rejects_long_series_text():
    """Test that series values containing plot-like narrative text are dropped."""
    api = WebBookAPI()

    web_data = {
        "title": "How the Light Gets In",
        "author": "Louise Penny",
        "series": "New York Times bestselling author Louise Penny. \"There is a crack in everything. That's how the light gets in.\" Leonard Cohen Christmas is approaching, and in Québec it's a time of dazzling snowfalls, bright lights, and gatherings with friends in front of blazing hearths.",
        "plot": "How the Light Gets In is the ninth Chief Inspector Gamache Novel from 1 New York Times bestselling author Louise Penny. \"There is a crack in everything. That's how the light gets in.\" Leonard Cohen Christmas is approaching, and in Québec it's a time of dazzling snowfalls, bright lights, and gatherings with friends in front of blazing hearths.",
    }

    cleaned = api.clean_web_data_for_storage(web_data)
    assert cleaned["series"] == ""

    print("[PASS] clean_web_data_for_storage rejects long narrative series text")


def test_metadata_matches_db_requires_title_and_author(api):
    meta = {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald"}
    assert api._metadata_matches_db("The Great Gatsby", "F. Scott Fitzgerald", meta)

    assert not api._metadata_matches_db(
        "The Great Gatsby", "F. Scott Fitzgerald", {"title": "", "author": "X"}
    )
    assert not api._metadata_matches_db(
        "The Great Gatsby",
        "F. Scott Fitzgerald",
        {"title": "The Great Gatsby", "author": "Stephen King"},
    )

def test_metadata_matches_db_rejects_title_only_bypass(api):
    """Results with plot/rating but wrong author must not pass when DB author is set."""
    meta = {
        "title": "The Great Gatsby",
        "author": "Stephen King",
        "plot": "Long description here.",
        "rating": 4.5,
        "genre": "Fiction",
    }
    assert not api._metadata_matches_db(
        "The Great Gatsby", "F. Scott Fitzgerald", meta
    )
    assert api._metadata_matches_db(
        "The Great Gatsby",
        "F. Scott Fitzgerald",
        meta,
        require_author_match=False,
    )

def test_strip_author_honorifics_for_search(api):
    assert api._strip_author_honorifics("Sir Arthur Conan Doyle") == "Arthur Conan Doyle"
    assert api._extract_last_name("Sir Arthur Conan Doyle") == "Doyle"

def test_should_use_title_only_for_librivox_and_narrator(api):
    assert api._likely_librivox_source(path=r"C:\Audio\librivox\book")
    assert api._should_use_title_only_fallback(
        "Charles Dickens",
        narrator="Charles Dickens",
    )
    assert api._should_use_title_only_fallback(
        "Jane Reader",
        path=r"D:\LibriVox\pride_and_prejudice",
    )

def test_metadata_matches_db_rejects_deaver_issue_cases(api):
    assert not api._metadata_matches_db(
        "Cause Of Death",
        "Jeffery Deaver",
        {"title": "Cause Of Death", "author": "Patricia Cornwell"},
    )
    assert not api._metadata_matches_db(
        "Date Night",
        "Jeffery Deaver",
        {"title": "Date Night Club", "author": "Saxon Bennett"},
    )

def test_metadata_matches_db_rejects_empty_db_author(api):
    meta = {"title": "Dune", "author": "Frank Herbert"}
    assert not api._metadata_matches_db("Dune", "", meta)
    assert not api._metadata_matches_db("Dune", "Frank Herbert", {"title": "Dune", "author": ""})

def test_plot_is_adequate_threshold(api):
    assert not api._plot_is_adequate("short")
    assert api._plot_is_adequate("x" * 80)

def test_rejects_non_book_song_plot(api):
    song_plot = (
        '"Blue on Black" is a song by American blues rock group Kenny Wayne Shepherd Band. '
        "Written by Shepherd with Mark Selby and Tia Sillers, it was originally released on "
        "their second studio album, Trouble Is... (1997). In 1998, the song was released as a "
        "single and reached the top position on the US Billboard Mainstream Rock Tracks chart."
    )
    assert api._is_non_book_plot(song_plot)
    metadata = {"title": "Blue On Black", "author": "Michael Connelly"}
    assert not api._apply_plot_to_metadata(
        metadata,
        song_plot,
        "wikipedia",
        "Blue On Black",
        "Michael Connelly",
    )
    assert "plot" not in metadata or not metadata.get("plot")

def test_wikipedia_plot_requires_author_or_book_context(api):
    metadata = {"title": "Blue On Black", "author": "Michael Connelly"}
    unrelated = "A" * 120
    assert not api._apply_plot_to_metadata(
        metadata,
        unrelated,
        "wikipedia",
        "Blue On Black",
        "Michael Connelly",
    )
    metadata = {"title": "Blue On Black", "author": "Michael Connelly"}
    book_plot = (
        "Blue On Black is a novella by Michael Connelly featuring detective Harry Bosch "
        "in a case involving a mysterious death tied to a jazz club."
    )
    assert api._apply_plot_to_metadata(
        metadata,
        book_plot,
        "wikipedia",
        "Blue On Black",
        "Michael Connelly",
    )
    assert metadata["plot"] == book_plot

def test_strip_html_removes_tags(api):
    raw = "<p>Hello <b>world</b> &amp; friends</p>"
    assert "<" not in api._strip_html(raw)
    assert "Hello" in api._strip_html(raw)

def test_google_item_picker_rejects_wrong_author(api):
    items = [
        {
            "volumeInfo": {
                "title": "Dune",
                "authors": ["Stephen King"],
                "publishedDate": "1965",
            }
        },
        {
            "volumeInfo": {
                "title": "Dune",
                "authors": ["Frank Herbert"],
                "publishedDate": "1965",
            }
        },
    ]
    best = api._pick_best_google_match(
        items, "Dune", "Frank Herbert", require_author_match=True
    )
    assert best is not None
    assert "Herbert" in best["author"]

def test_cache_key_includes_isbn_param(api):
    with patch.object(api, "_fetch_metadata_by_isbn") as isbn_fetch:
        isbn_fetch.return_value = {
            "title": "Dune",
            "author": "Frank Herbert",
            "_resolved_source": "open_library",
        }
        with patch.object(api, "_enrich_metadata_plot"):
            with patch.object(api, "_fill_series_fields"):
                with patch.object(api, "_save_persistent_cache"):
                    api.get_book_metadata(
                        "Dune", "Frank Herbert", isbn="9780441172719"
                    )
    assert any("9780441172719" in key for key in api._cache)

def test_dedupe_fetch_errors_keeps_one_per_source():
    from src.web.web_book_api import _dedupe_fetch_errors

    errors = [
        "google_books: HTTP Error 429: Too Many Requests",
        "google_books: HTTP Error 429: Too Many Requests",
        "open_library: timed out",
    ]
    assert _dedupe_fetch_errors(errors) == [
        "google_books: HTTP Error 429: Too Many Requests",
        "open_library: timed out",
    ]

def test_format_web_fetch_status_message_rate_limit():
    from src.web.web_book_api import format_web_fetch_status_message

    msg = format_web_fetch_status_message(
        ["google_books: HTTP Error 429: Too Many Requests"]
    )
    assert "rate limited" in msg.lower()
    assert "re-fetch" in msg.lower()

def test_format_web_fetch_status_message_includes_cooldown_seconds():
    from src.web.web_book_api import (
        _note_rate_limited,
        format_web_fetch_status_message,
    )

    _clear_source_cooldown()
    _note_rate_limited("google_books", seconds=40)
    msg = format_web_fetch_status_message(
        ["google_books: HTTP Error 429: Too Many Requests"]
    )
    assert "rate limited" in msg.lower()
    assert "re-fetch" in msg.lower()
    assert "about" in msg.lower()
    assert "s" in msg.lower()
    _clear_source_cooldown()


def test_extract_year_returns_empty_when_no_year(api):
    assert api._extract_year("unknown") == ""
    assert api._extract_year("2020-01-01") == "2020"
    assert api._extract_year("") == ""

