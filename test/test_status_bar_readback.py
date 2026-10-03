"""Tests for centralized status bar Alt+/ readback (bug 102)."""

import pytest
from PySide6.QtWidgets import QMainWindow, QStatusBar

from src.accessibility.accessible_events import (
    _status_bar_focus_delay_ms,
    configure_status_bar_accessibility,
    prepare_status_bar_for_readback,
    read_status_bar_message,
)


def _window_with_bar(qtbot):
    window = QMainWindow()
    qtbot.addWidget(window)
    bar = QStatusBar()
    window.setStatusBar(bar)
    return window, bar


def _capture_readback(monkeypatch):
    captured = {}

    def fake_readback(widget, text, **kwargs):
        captured["widget"] = widget
        captured["message"] = text
        captured.update(kwargs)

    monkeypatch.setattr(
        "src.accessibility.accessible_events.announce_plain_text_readback",
        fake_readback,
    )
    return captured


def test_configure_status_bar_accessibility_clears_metadata(qapp):
    bar = QStatusBar()
    bar.setAccessibleName("noise")
    bar.setAccessibleDescription("Status messages for this window")

    configure_status_bar_accessibility(bar)

    assert bar.accessibleName() == ""
    assert bar.accessibleDescription() == ""


def test_prepare_status_bar_for_readback_uses_visible_message(qapp):
    bar = QStatusBar()
    bar.setAccessibleDescription("Import detail status messages")
    bar.showMessage("3 books selected")

    text = prepare_status_bar_for_readback(bar)

    assert text == "3 books selected"
    assert bar.accessibleName() == "3 books selected"
    assert bar.accessibleDescription() == ""


def test_prepare_status_bar_for_readback_explicit_message(qapp):
    bar = QStatusBar()
    bar.showMessage("old")

    text = prepare_status_bar_for_readback(bar, "explicit")

    assert text == "explicit"
    assert bar.accessibleName() == "explicit"


def test_read_status_bar_message_no_op_without_screen_reader(qtbot, monkeypatch):
    _window, bar = _window_with_bar(qtbot)
    bar.showMessage("hello")
    monkeypatch.setattr(
        "src.accessibility.accessible_events.QAccessible.isActive",
        lambda: False,
    )
    monkeypatch.setattr(
        "src.accessibility.accessible_events.is_screen_reader_active",
        lambda: False,
    )
    captured = _capture_readback(monkeypatch)

    read_status_bar_message(bar, fallback="Ready")

    assert captured == {}


def test_read_status_bar_message_announce_text_override(qtbot, monkeypatch):
    _window, bar = _window_with_bar(qtbot)
    bar.showMessage("footer only")
    monkeypatch.setattr(
        "src.accessibility.accessible_events.QAccessible.isActive",
        lambda: True,
    )
    captured = _capture_readback(monkeypatch)

    read_status_bar_message(
        bar,
        fallback="ignored",
        announce_text="42 books  |  Sort: Title",
        update_visible=False,
    )

    assert captured["message"] == "42 books  |  Sort: Title"
    assert bar.currentMessage() == "footer only"


def test_read_status_bar_message_when_screen_reader_process_detected(qtbot, monkeypatch):
    _window, bar = _window_with_bar(qtbot)
    monkeypatch.setattr(
        "src.accessibility.accessible_events.QAccessible.isActive",
        lambda: False,
    )
    monkeypatch.setattr(
        "src.accessibility.accessible_events.is_screen_reader_active",
        lambda: True,
    )
    captured = _capture_readback(monkeypatch)

    read_status_bar_message(bar, fallback="Moby Dick")

    assert captured["message"] == "Moby Dick"


def test_status_bar_focus_delay_has_minimum_when_reader_active(qapp, monkeypatch):
    monkeypatch.setattr(
        "src.accessibility.accessible_events.QAccessible.isActive",
        lambda: True,
    )
    monkeypatch.setattr(
        "src.accessibility.accessible_events.get_screen_reader_focus_delay_ms",
        lambda: 0,
    )
    assert _status_bar_focus_delay_ms() == 300


def test_read_status_bar_message_speaks_through_window_not_status_bar(qtbot, monkeypatch):
    window, bar = _window_with_bar(qtbot)
    bar.showMessage("visible status")
    monkeypatch.setattr(
        "src.accessibility.accessible_events.QAccessible.isActive",
        lambda: True,
    )
    captured = _capture_readback(monkeypatch)

    read_status_bar_message(bar, fallback="fallback only")

    assert captured["message"] == "visible status"
    assert captured["widget"] is window
    assert captured["widget"] is not bar


def test_plain_readback_on_main_window_uses_central_widget(qtbot, monkeypatch):
    from PySide6.QtWidgets import QWidget

    from src.accessibility.accessible_events import announce_plain_text_readback

    window, _bar = _window_with_bar(qtbot)
    central = QWidget()
    central.setAccessibleName("Library")
    window.setCentralWidget(central)
    window.setAccessibleName("AbCS")
    monkeypatch.setattr(
        "src.accessibility.accessible_events.QAccessible.isActive",
        lambda: True,
    )

    announce_plain_text_readback(window, "12 books")

    assert central.accessibleName() == "12 books"
    assert window.accessibleName() == "AbCS"
    qtbot.waitUntil(lambda: central.accessibleName() == "Library", timeout=2000)
