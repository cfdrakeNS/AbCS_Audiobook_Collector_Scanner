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
    # Block Alt+letter (A-Z) and Alt+number (0-9) if not allowed
    if Qt.Key_A <= key <= Qt.Key_Z:
        letter = chr(key)
        return letter not in set(allowed_letters)
    if Qt.Key_0 <= key <= Qt.Key_9:
        # Always block Alt+number
        return True
    return False
