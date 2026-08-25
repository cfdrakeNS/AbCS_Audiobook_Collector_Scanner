"""Tests for NameListWindow status message formatting rules."""

from types import SimpleNamespace

from src.ui.name_list_window import NameListWindow


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
