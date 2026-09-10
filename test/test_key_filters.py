"""Unit tests for accessibility key-filter helpers."""

from __future__ import annotations

from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QKeyEvent

from src.accessibility.key_filters import is_unmapped_alt_letter


def _key_press(key: int, modifiers: Qt.KeyboardModifier = Qt.NoModifier) -> QKeyEvent:
    return QKeyEvent(QEvent.KeyPress, key, modifiers)


def test_mapped_alt_letter_is_not_unmapped(qapp):
    event = _key_press(Qt.Key_S, Qt.AltModifier)
    assert is_unmapped_alt_letter(event, {"S", "D"}) is False


def test_unmapped_alt_letter_is_blocked(qapp):
    event = _key_press(Qt.Key_Z, Qt.AltModifier)
    assert is_unmapped_alt_letter(event, {"S", "D"}) is True


def test_alt_number_always_unmapped(qapp):
    event = _key_press(Qt.Key_5, Qt.AltModifier)
    assert is_unmapped_alt_letter(event, {"5", "S"}) is True


def test_plain_letter_without_alt_is_not_unmapped(qapp):
    event = _key_press(Qt.Key_S, Qt.NoModifier)
    assert is_unmapped_alt_letter(event, set()) is False


def test_non_keypress_event_is_not_unmapped(qapp):
    event = QKeyEvent(QEvent.KeyRelease, Qt.Key_A, Qt.AltModifier)
    assert is_unmapped_alt_letter(event, set()) is False


def test_alt_plus_non_letter_non_digit_is_not_unmapped(qapp):
    event = _key_press(Qt.Key_Slash, Qt.AltModifier)
    assert is_unmapped_alt_letter(event, set()) is False


def test_extra_modifiers_with_alt_are_not_treated_as_alt_only(qapp):
    event = _key_press(Qt.Key_A, Qt.AltModifier | Qt.ShiftModifier)
    assert is_unmapped_alt_letter(event, set()) is False
