"""Shared key-event filtering helpers for accessibility behavior."""

from collections.abc import Iterable

from PySide6.QtCore import Qt, QEvent


def is_unmapped_alt_letter(event, allowed_letters: Iterable[str]) -> bool:
    """Return True when event is Alt+letter that is not in allowed_letters."""
    if event.type() != QEvent.KeyPress:
        return False

    if event.modifiers() != Qt.AltModifier:
        return False

    key = event.key()
    if not (Qt.Key_A <= key <= Qt.Key_Z):
        return False

    letter = chr(key)
    return letter not in set(allowed_letters)
