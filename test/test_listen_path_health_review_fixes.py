"""Accessibility review fixes for Listen and Check Book Locations."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QAccessible, QKeyEvent, QKeySequence, QShortcut


class _Signal:
    def connect(self, *_args, **_kwargs):
        return None


class _FakeAudio:
    pass


class _FakePlayer:
    def __init__(self):
        self.playbackStateChanged = _Signal()
        self.errorOccurred = _Signal()
        self.mediaStatusChanged = _Signal()
        self.positionChanged = _Signal()
        self.durationChanged = _Signal()
        self._position = 0

    def setAudioOutput(self, *_args):
        return None

    def setPlaybackRate(self, _rate):
        return None

    def setPosition(self, position):
        self._position = position

    def position(self):
        return self._position

    def duration(self):
        return 60_000


@pytest.fixture
def listen_window(ui_scaler, theme_manager, qtbot, monkeypatch):
    from src.ui import preview_window

    saved: list = []
    monkeypatch.setattr(preview_window, "save_preview_speed", saved.append)
    window = preview_window.PreviewWindow(
        None, ui_scaler, theme_manager, player_types=(_FakePlayer, _FakeAudio)
    )
    window.saved_speeds = saved
    qtbot.addWidget(window)
    window.show()
    yield window
    window._close_requested = True
    window.close()


def _shortcut_for(window, keys: str) -> QShortcut | None:
    wanted = QKeySequence(keys)
    for shortcut in window.findChildren(QShortcut):
        if shortcut.key() == wanted:
            return shortcut
    return None


def test_listen_alt_shortcuts_come_from_central_map(listen_window, qtbot):
    window = listen_window
    assert window.ALLOWED_ALT_LETTERS == {"N", "P", "S", "/"}
    for keys in ("Alt+N", "Alt+P", "Alt+S", "Space", "Alt+Left", "Alt+Right"):
        shortcut = _shortcut_for(window, keys)
        assert shortcut is not None, keys
        assert shortcut.context() == Qt.WidgetWithChildrenShortcut
    window.play_pause_button.setFocus(Qt.TabFocusReason)
    _shortcut_for(window, "Alt+S").activated.emit()
    qtbot.waitUntil(lambda: window.speed_combo.hasFocus(), timeout=1000)


def test_listen_space_on_speed_opens_list_instead_of_play(
    listen_window, qtbot, monkeypatch
):
    window = listen_window
    toggles: list = []
    popups: list = []
    monkeypatch.setattr(window, "on_play_pause", lambda: toggles.append(1))
    monkeypatch.setattr(window.speed_combo, "showPopup", lambda: popups.append(1))
    window.speed_combo.setFocus(Qt.TabFocusReason)
    qtbot.waitUntil(lambda: window.speed_combo.hasFocus(), timeout=1000)
    window.on_space()
    assert popups == [1]
    assert toggles == []
    window.play_pause_button.setFocus(Qt.TabFocusReason)
    qtbot.waitUntil(lambda: window.play_pause_button.hasFocus(), timeout=1000)
    window.on_space()
    assert toggles == [1]


def test_listen_speed_combo_blocks_plain_arrows_and_applies_on_activated(
    listen_window, monkeypatch
):
    from src.ui import preview_window

    window = listen_window
    combo = window.speed_combo
    beeps: list = []
    popups: list = []
    monkeypatch.setattr(preview_window.QApplication, "beep", lambda: beeps.append(1))
    monkeypatch.setattr(combo, "showPopup", lambda: popups.append(1))
    start = combo.currentIndex()
    for key in (Qt.Key_Down, Qt.Key_Up):
        event = QKeyEvent(QEvent.KeyPress, key, Qt.NoModifier)
        assert window.eventFilter(combo, event) is True
    assert combo.currentIndex() == start
    assert len(beeps) == 2
    assert window.saved_speeds == []
    event = QKeyEvent(QEvent.KeyPress, Qt.Key_Down, Qt.AltModifier)
    assert window.eventFilter(combo, event) is True
    assert popups == [1]
    target = combo.findData(1.5)
    combo.setCurrentIndex(target)
    assert window.saved_speeds == []
    combo.activated.emit(target)
    assert window.saved_speeds == [1.5]


def test_listen_player_ticks_do_not_fire_name_changed(listen_window, monkeypatch):
    from src.ui import preview_window

    window = listen_window
    events: list = []

    class _StubAccessible:
        Event = QAccessible.Event

        @staticmethod
        def isActive():
            return True

        @staticmethod
        def updateAccessibility(event):
            events.append(event.type())

    monkeypatch.setattr(preview_window, "QAccessible", _StubAccessible)
    window._set_slider_range(60_000)
    window.position_label.setFocus(Qt.TabFocusReason)
    monkeypatch.setattr(window.position_label, "hasFocus", lambda: True)
    window._on_position_changed(3_000)
    window._on_position_changed(4_000)
    assert events == []
    assert window.position_label.accessibleName() == "Play position 0:04"
    window._seek_by(5_000)
    assert events == [QAccessible.Event.NameChanged]


def _path_window(temp_db, ui_scaler, theme_manager, qtbot):
    from src.ui.path_health_window import PathHealthWindow

    window = PathHealthWindow(temp_db, ui_scaler, theme_manager, parent=None)
    qtbot.addWidget(window)
    return window


def test_path_health_combos_block_plain_arrows(
    temp_db, ui_scaler, theme_manager, qtbot, monkeypatch
):
    from src.ui import path_health_window

    window = _path_window(temp_db, ui_scaler, theme_manager, qtbot)
    beeps: list = []
    monkeypatch.setattr(
        path_health_window.QApplication, "beep", lambda: beeps.append(1)
    )
    for combo in (window.collection_combo, window.filter_combo):
        popups: list = []
        monkeypatch.setattr(combo, "showPopup", lambda p=popups: p.append(1))
        start = combo.currentIndex()
        for key in (Qt.Key_Down, Qt.Key_Up):
            event = QKeyEvent(QEvent.KeyPress, key, Qt.NoModifier)
            assert window.eventFilter(combo, event) is True
        assert combo.currentIndex() == start
        event = QKeyEvent(QEvent.KeyPress, Qt.Key_Down, Qt.AltModifier)
        assert window.eventFilter(combo, event) is True
        assert popups == [1]
    assert len(beeps) == 4
    window.close()


def test_path_health_alt_filter_on_all_controls_and_title_summary(
    temp_db, ui_scaler, theme_manager, qtbot
):
    from src.core.path_health import STATUS_MISSING, PathHealthRow

    window = _path_window(temp_db, ui_scaler, theme_manager, qtbot)
    unmapped = QKeyEvent(QEvent.KeyPress, Qt.Key_Q, Qt.AltModifier)
    for widget in (
        window.collection_combo,
        window.filter_combo,
        window.guide_label,
        window.export_button,
        window.table,
        window.scan_button,
    ):
        assert window.eventFilter(widget, unmapped) is True
    window._rows = [
        PathHealthRow(
            book_id=1,
            author="Ann Author",
            title="Book One",
            path="",
            status=STATUS_MISSING,
            reason="Author folder not found",
        )
    ]
    window._fill_table()
    title_text = window.table.item(0, window.COL_TITLE).data(Qt.AccessibleTextRole)
    assert title_text.startswith("Book One, by Ann Author, missing.")
    assert "Author folder not found" in title_text
    for col in (window.COL_AUTHOR, window.COL_PATH):
        assert "missing" in window.table.item(0, col).data(Qt.AccessibleTextRole)
    window.close()
