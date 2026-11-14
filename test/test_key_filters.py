"""Unit tests for accessibility key-filter helpers."""

from __future__ import annotations

from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QKeyEvent

import pytest

from src.accessibility import screen_reader
from src.accessibility.key_filters import blocks_plain_combo_arrow, is_unmapped_alt_letter


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


def test_plain_combo_arrow_always_blocked_without_alt(qapp):
    for key in (Qt.Key_Up, Qt.Key_Down):
        assert blocks_plain_combo_arrow(_key_press(key)) is True
        assert blocks_plain_combo_arrow(_key_press(key, Qt.AltModifier)) is False
    assert blocks_plain_combo_arrow(_key_press(Qt.Key_Left)) is False
    release = QKeyEvent(QEvent.KeyRelease, Qt.Key_Down, Qt.NoModifier)
    assert blocks_plain_combo_arrow(release) is False


def test_screen_reader_cache_rechecks_after_max_age(monkeypatch):
    checks = []
    clock = {"now": 100.0}
    monkeypatch.setattr(screen_reader, "_cached_active", None)
    monkeypatch.setattr(screen_reader.time, "monotonic", lambda: clock["now"])
    monkeypatch.setattr(
        screen_reader, "is_screen_reader_active", lambda: checks.append(1) or len(checks) == 1
    )

    assert screen_reader.is_screen_reader_active_cached() is True
    clock["now"] += 4.9
    assert screen_reader.is_screen_reader_active_cached() is True
    assert len(checks) == 1
    clock["now"] += 0.2
    assert screen_reader.is_screen_reader_active_cached() is False
    assert len(checks) == 2
