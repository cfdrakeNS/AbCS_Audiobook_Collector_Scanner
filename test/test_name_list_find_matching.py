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


def test_find_match_rank_exact_beats_collaborative_author():
    exact_rank = NameListWindow._find_match_rank(
        "Stephen King",
        "Stephen King",
        is_author_mode=True,
    )
    collaborative_rank = NameListWindow._find_match_rank(
        "Joe Hill, Stephen King",
        "Stephen King",
        is_author_mode=True,
    )
    assert exact_rank == 0
    assert collaborative_rank == 3
    assert exact_rank < collaborative_rank


def test_row_visible_for_live_find_matches_display_substring():
    assert NameListWindow._row_visible_for_live_find(
        "James Patterson",
        "james",
    )
    assert not NameListWindow._row_visible_for_live_find(
        "James Patterson",
        "pattersonx",
    )


def test_row_visible_for_live_find_matches_normalized_substring():
    assert NameListWindow._row_visible_for_live_find(
        "King, Stephen",
        "stephen",
    )


def test_row_visible_for_live_find_empty_search_shows_all():
    assert NameListWindow._row_visible_for_live_find("Stephen King", "")
    assert NameListWindow._row_visible_for_live_find("Stephen King", "   ")


def test_row_visible_for_live_find_does_not_use_enter_token_matching():
    assert not NameListWindow._row_visible_for_live_find(
        "King, Stephen",
        "Stephen King",
    )


def test_table_focus_policy_no_focus_while_searching():
    from PySide6.QtCore import Qt

    assert NameListWindow._table_focus_policy_for_find_filter(True) == Qt.NoFocus
    assert NameListWindow._table_focus_policy_for_find_filter(False) == Qt.StrongFocus


def test_best_match_row_from_entries_prefers_exact_over_collaborative():
    entries = [
        (0, "Joe Hill, Stephen King"),
        (1, "Stephen King"),
    ]
    best_row, total = NameListWindow._best_match_row_from_entries(
        entries,
        "Stephen King",
        is_author_mode=True,
    )
    assert best_row == 1
    assert total == 2


def test_best_match_row_from_entries_empty_when_no_eligible_rows():
    best_row, total = NameListWindow._best_match_row_from_entries(
        [],
        "Stephen King",
        is_author_mode=True,
    )
    assert best_row == -1
    assert total == 0


def test_find_match_rank_reordered_name_is_weaker_than_exact():
    exact_rank = NameListWindow._find_match_rank(
        "Stephen King",
        "Stephen King",
        is_author_mode=True,
    )
    reordered_rank = NameListWindow._find_match_rank(
        "King, Stephen",
        "Stephen King",
        is_author_mode=True,
    )
    assert exact_rank == 0
    assert reordered_rank == 6
    assert exact_rank < reordered_rank
