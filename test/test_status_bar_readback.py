"""Tests for centralized status bar Alt+/ readback (bug 102)."""

import pytest
from PySide6.QtWidgets import QApplication, QStatusBar

from src.accessibility.accessible_events import (
    _status_bar_focus_delay_ms,
    configure_status_bar_accessibility,
    prepare_status_bar_for_readback,
    read_status_bar_message,
)


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


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


def test_read_status_bar_message_no_op_without_screen_reader(qapp, monkeypatch):
    bar = QStatusBar()
    bar.showMessage("hello")
    called = []

    def fake_announce(*args, **kwargs):
        called.append(True)

    monkeypatch.setattr(
        "src.accessibility.accessible_events.QAccessible.isActive",
        lambda: False,
    )
    monkeypatch.setattr(
        "src.accessibility.accessible_events.is_screen_reader_active",
        lambda: False,
    )
    monkeypatch.setattr(
        "src.accessibility.accessible_events.announce_status_message",
        fake_announce,
    )

    read_status_bar_message(bar, fallback="Ready")

    assert called == []


def test_read_status_bar_message_announce_text_override(qapp, monkeypatch):
    bar = QStatusBar()
    bar.showMessage("footer only")
    captured = {}

    monkeypatch.setattr(
        "src.accessibility.accessible_events.QAccessible.isActive",
        lambda: True,
    )

    def fake_announce(status_bar, message, **kwargs):
        captured["message"] = message

    monkeypatch.setattr(
        "src.accessibility.accessible_events.announce_status_message",
        fake_announce,
    )

    read_status_bar_message(
        bar,
        fallback="ignored",
        announce_text="42 books  |  Sort: Title",
    )

    assert captured["message"] == "42 books  |  Sort: Title"


def test_read_status_bar_message_when_screen_reader_process_detected(qapp, monkeypatch):
    bar = QStatusBar()
    captured = {}

    monkeypatch.setattr(
        "src.accessibility.accessible_events.QAccessible.isActive",
        lambda: False,
    )
    monkeypatch.setattr(
        "src.accessibility.accessible_events.is_screen_reader_active",
        lambda: True,
    )

    def fake_announce(status_bar, message, **kwargs):
        captured["message"] = message

    monkeypatch.setattr(
        "src.accessibility.accessible_events.announce_status_message",
        fake_announce,
    )

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


def test_read_status_bar_message_prefers_current_message(qapp, monkeypatch):
    bar = QStatusBar()
    bar.showMessage("visible status")
    captured = {}

    monkeypatch.setattr(
        "src.accessibility.accessible_events.QAccessible.isActive",
        lambda: True,
    )

    def fake_announce(status_bar, message, **kwargs):
        captured["message"] = message
        captured["name"] = status_bar.accessibleName()
        captured["description"] = status_bar.accessibleDescription()

    monkeypatch.setattr(
        "src.accessibility.accessible_events.announce_status_message",
        fake_announce,
    )

    read_status_bar_message(bar, fallback="fallback only")

    assert captured["message"] == "visible status"
    assert captured["name"] == "visible status"
    assert captured["description"] == ""
