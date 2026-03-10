"""Targeted tests for NameListWindow find normalization and matching."""

from src.ui.name_list_window import NameListWindow


def test_normalize_find_value_strips_punctuation_and_case():
    assert NameListWindow._normalize_find_value(
        "  King, Stephen  ") == "king stephen"
    assert NameListWindow._normalize_find_value(
        "O'Connor-Mary") == "o connor mary"


def test_is_find_match_author_mode_matches_reordered_tokens():
    assert NameListWindow._is_find_match(
        "King, Stephen",
        "Stephen King",
        is_author_mode=True,
    )


def test_is_find_match_non_author_mode_requires_direct_substring():
    assert not NameListWindow._is_find_match(
        "King, Stephen",
        "Stephen King",
        is_author_mode=False,
    )


def test_is_find_match_handles_punctuation_insensitive_search():
    assert NameListWindow._is_find_match(
        "Anne-Marie O'Connor",
        "anne marie oconnor",
        is_author_mode=True,
    )


def test_is_find_match_author_mode_handles_partial_reordered_tokens():
    assert NameListWindow._is_find_match(
        "King, Stephen Edwin",
        "stephen king",
        is_author_mode=True,
    )


def test_is_find_match_author_mode_rejects_when_token_missing():
    assert not NameListWindow._is_find_match(
        "King, Stephen",
        "stephen queen",
        is_author_mode=True,
    )
