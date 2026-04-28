"""
Quick tests for web search improvement methods.
Run with: python test/test_web_search_improvements.py
"""

import sys

sys.path.insert(0, "c:/Users/cfran/PythonProjects/abcs/src")

from web.web_book_api import WebBookAPI, STOPWORDS


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

    # Empty author - should allow (can't verify)
    assert api._author_matches("", "Stephen King") == True

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


if __name__ == "__main__":
    test_stopwords()
    test_extract_last_name()
    test_author_matches()
    test_title_word_match_score()
    test_title_matches()
    print("\n[PASS] All tests passed!")
