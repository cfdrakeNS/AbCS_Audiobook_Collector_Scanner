"""Tests for screen reader process detection and focus-delay mapping."""

from types import SimpleNamespace

import pytest

import src.accessibility.screen_reader as screen_reader


def _mock_processes(names):
    """Build fake psutil process_iter entries from process name strings."""
    return [
        SimpleNamespace(info={"name": name})
        for name in names
    ]


@pytest.fixture
def mock_psutil(monkeypatch):
    """Patch process_iter; caller sets process names via returned setter."""

    class FakePsutil:
        def __init__(self):
            self._names = []

        def set_processes(self, names):
            self._names = names

        def process_iter(self, _attrs):
            return _mock_processes(self._names)

    fake = FakePsutil()
    monkeypatch.setattr(screen_reader, "psutil", fake)
    return fake


def test_narrator_detected(mock_psutil):
    mock_psutil.set_processes(["explorer.exe", "Narrator.exe"])

    assert screen_reader.get_active_screen_reader() == "narrator"
    assert screen_reader.is_screen_reader_active() is True
    assert screen_reader.get_screen_reader_focus_delay_ms() == 3500


def test_jaws_detected(mock_psutil):
    mock_psutil.set_processes(["jaws.exe"])

    assert screen_reader.get_active_screen_reader() == "jaws"
    assert screen_reader.get_screen_reader_focus_delay_ms() == 300


def test_nvda_detected(mock_psutil):
    mock_psutil.set_processes(["nvda.exe"])

    assert screen_reader.get_active_screen_reader() == "nvda"
    assert screen_reader.get_screen_reader_focus_delay_ms() == 1500


def test_orca_detected(mock_psutil):
    mock_psutil.set_processes(["orca-daemon"])

    assert screen_reader.get_active_screen_reader() == "orca"
    assert screen_reader.get_screen_reader_focus_delay_ms() == 800


def test_no_screen_reader_detected(mock_psutil):
    mock_psutil.set_processes(["explorer.exe", "python.exe"])

    assert screen_reader.get_active_screen_reader() == ""
    assert screen_reader.is_screen_reader_active() is False
    assert screen_reader.get_screen_reader_focus_delay_ms() == 0


def test_psutil_unavailable(monkeypatch):
    monkeypatch.setattr(screen_reader, "psutil", None)

    assert screen_reader.get_active_screen_reader() == ""
    assert screen_reader.is_screen_reader_active() is False
    assert screen_reader.get_screen_reader_focus_delay_ms() == 0
