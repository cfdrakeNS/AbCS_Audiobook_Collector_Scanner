"""Central Alt+key maps in shortcuts.py."""

from src.accessibility.shortcuts import (
    ShortcutContext,
    allowed_alt_letters,
    shortcuts_for_context,
)


def test_every_context_has_a_map():
    for context in ShortcutContext:
        assert shortcuts_for_context(context), context


def test_new_window_maps_are_central():
    assert set(shortcuts_for_context(ShortcutContext.PREVIEW_WINDOW)) == {"N", "P", "S"}
    assert set(shortcuts_for_context(ShortcutContext.HELP_WINDOW)) == {"L"}
    assert set(shortcuts_for_context(ShortcutContext.BATCH_WEB_FETCH_SUMMARY)) == {
        "A",
        "R",
        "L",
    }
    assert {"G", "Y", "M", "R"} <= set(
        shortcuts_for_context(ShortcutContext.READING_HISTORY_WINDOW)
    )


def test_allowed_alt_letters_adds_extras():
    letters = allowed_alt_letters(ShortcutContext.COLLECTION_WINDOW, "/")
    assert {"B", "E", "L", "D", "M", "F", "A", "/"} <= letters
