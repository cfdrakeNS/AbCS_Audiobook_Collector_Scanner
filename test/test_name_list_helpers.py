"""NameListWindow find matching and status formatting helpers."""

from types import SimpleNamespace

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
    assert NameListWindow._table_focus_policy_for_find_filter(False) == Qt.ClickFocus

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


class _WidgetState:
    def __init__(self, *, visible: bool = False, enabled: bool = False):
        self._visible = visible
        self._enabled = enabled

    def isVisible(self) -> bool:
        return self._visible

    def isEnabled(self) -> bool:
        return self._enabled

def _make_stub(*, edit_mode: bool = False):
    save_button = _WidgetState(visible=edit_mode)
    name_edit = _WidgetState(enabled=edit_mode)
    return SimpleNamespace(
        AUTHOR_FIND_HINT=NameListWindow.AUTHOR_FIND_HINT,
        save_button=save_button,
        name_edit=name_edit,
    )

def test_format_status_appends_alt_e_in_browse_mode():
    stub = _make_stub(edit_mode=False)

    formatted = NameListWindow._format_status_message(stub, "Ready")

    assert formatted == "Ready Alt+E"

def test_format_status_does_not_duplicate_alt_e():
    stub = _make_stub(edit_mode=False)

    formatted = NameListWindow._format_status_message(
        stub, "To edit Author press Alt+E")

    assert formatted == "To edit Author press Alt+E"

def test_format_status_skips_find_messages():
    stub = _make_stub(edit_mode=False)

    found_message = NameListWindow._format_status_message(
        stub,
        "Found author: King, Stephen. enter for next, alt+F new search ",
    )
    no_match_message = NameListWindow._format_status_message(
        stub,
        "No matching authors for 'king'.",
    )

    assert found_message.endswith(" enter for next, alt+F new search")
    assert no_match_message == "No matching authors for 'king'."

def test_format_status_skips_edit_mode():
    stub = _make_stub(edit_mode=True)

    formatted = NameListWindow._format_status_message(
        stub, "Author saved: Test")

    assert formatted == "Author saved: Test"

