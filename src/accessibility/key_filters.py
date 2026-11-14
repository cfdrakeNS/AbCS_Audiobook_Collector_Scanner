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


def blocks_plain_combo_arrow(event) -> bool:
    """True for Up or Down without Alt on a combo box.

    Closed lists do not step on plain arrows (easy to change by accident).
    Use Alt+Up/Down or the mouse. Callers that need plain stepping
    (read-date Year/Month/Day boxes) skip this helper.
    """
    if event.type() != QEvent.KeyPress:
        return False
    if event.key() not in (Qt.Key_Up, Qt.Key_Down):
        return False
    if event.modifiers() & Qt.AltModifier:
        return False
    return True
