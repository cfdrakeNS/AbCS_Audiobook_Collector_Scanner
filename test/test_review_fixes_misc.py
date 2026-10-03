"""Accessibility review fixes: reading history, collections, name list, help."""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QTableWidget

from src.ui.accessible_dialog import AccessibleDialog


@pytest.fixture
def f1_rows(monkeypatch):
    """Capture F1 table rows (accessible text) instead of showing the dialog."""
    rows: list[str] = []

    def fake_exec(dlg):
        table = dlg.findChild(QTableWidget)
        rows.extend(
            table.item(r, 0).data(Qt.AccessibleTextRole) for r in range(table.rowCount())
        )
        return 0

    monkeypatch.setattr(AccessibleDialog, "exec", fake_exec)
    return rows


def _shortcut(window, text: str) -> QShortcut:
    seq = QKeySequence(text)
    return next(s for s in window.findChildren(QShortcut) if s.key() == seq)


def test_reading_history_alt_tab_shortcuts_switch_tab(reading_history_window):
    window = reading_history_window
    focused = []
    window.focus_current_table = lambda: focused.append(window.tab_widget.currentIndex())
    for key, index in (("Alt+M", 2), ("Alt+R", 3), ("Alt+Y", 1), ("Alt+G", 0)):
        _shortcut(window, key).activated.emit()
        assert window.tab_widget.currentIndex() == index
        assert focused[-1] == index


def test_reading_history_allowed_alt_letters_from_central_map(reading_history_window):
    assert {"G", "Y", "M", "R", "L", "S", "F", "/"} <= reading_history_window.ALLOWED_ALT_LETTERS


def test_collection_allows_label_mnemonics_and_lists_them(
    temp_db, ui_scaler, theme_manager, qtbot, f1_rows
):
    from src.ui.collection_window import CollectionWindow

    window = CollectionWindow(temp_db, ui_scaler, theme_manager)
    qtbot.addWidget(window)
    assert {"M", "F", "A", "B", "E", "L", "D", "/"} <= window.ALLOWED_ALT_LETTERS
    window.on_show_shortcuts()
    joined = "\n".join(f1_rows)
    for key in ("Alt+M", "Alt+A", "Alt+F", "Enter"):
        assert f": {key}" in joined
    window.close()


def test_collection_browse_while_locked_announces(
    temp_db, ui_scaler, theme_manager, qtbot, monkeypatch
):
    from src.ui.collection_window import CollectionWindow

    window = CollectionWindow(temp_db, ui_scaler, theme_manager)
    qtbot.addWidget(window)
    calls = []
    monkeypatch.setattr(window, "set_status", lambda m, announce=False: calls.append((m, announce)))
    assert window._editor_locked
    window.on_browse_root()
    assert calls == [("Press Alt+E or Ctrl+N to edit first.", True)]
    window.close()


def test_name_list_sort_combo_blocks_plain_arrows_and_announces(
    temp_db, ui_scaler, theme_manager, qtbot, monkeypatch
):
    from src.ui.name_list_window import NameListWindow

    window = NameListWindow(temp_db, ui_scaler, theme_manager, "series")
    qtbot.addWidget(window)
    beeps = []
    monkeypatch.setattr("src.ui.name_list_window.QApplication.beep", lambda: beeps.append(1))
    calls = []
    monkeypatch.setattr(window, "set_status", lambda m, announce=False: calls.append((m, announce)))

    start = window.sort_combo.currentIndex()
    QTest.keyClick(window.sort_combo, Qt.Key_Down)
    assert window.sort_combo.currentIndex() == start
    QTest.keyClick(window.sort_combo, Qt.Key_X, Qt.AltModifier)
    assert len(beeps) == 2

    window.sort_combo.setCurrentIndex(1)
    assert calls and calls[-1][1] is True
    assert calls[-1][0].startswith("Sorted by book count")
    window.close()


def test_name_list_f1_has_no_sort_row_and_full_escape(
    temp_db, ui_scaler, theme_manager, qtbot, f1_rows
):
    from src.ui.name_list_window import NameListWindow

    window = NameListWindow(temp_db, ui_scaler, theme_manager, "series")
    qtbot.addWidget(window)
    window.on_show_shortcuts()
    assert not any(row.endswith(": Sort") for row in f1_rows)
    escape = next(row for row in f1_rows if row.endswith(": Escape"))
    assert "Find" in escape and "cancel edit" in escape and "close window" in escape
    window.close()


def _help_window(qtbot, monkeypatch):
    from src.ui.help_window import HelpWindow

    window = HelpWindow(None, doc_filename="02_import.md")
    qtbot.addWidget(window)
    monkeypatch.setattr("src.ui.help_window.QTimer.singleShot", lambda _ms, fn: fn())
    return window


def test_help_shift_f1_opens_overview(qtbot, monkeypatch):
    window = _help_window(qtbot, monkeypatch)
    assert window._current_filename == "02_import.md"
    assert window.overview_shortcut.key().toString() == "Shift+F1"
    window.overview_shortcut.activated.emit()
    assert window._current_filename == "01_overview.md"
    window.close()


@pytest.mark.parametrize("reader_active", [True, False])
def test_help_f1_lists_shift_f1_first(qtbot, monkeypatch, f1_rows, reader_active):
    monkeypatch.setattr(
        "src.accessibility.shortcut_helpers.is_screen_reader_active", lambda: reader_active
    )
    window = _help_window(qtbot, monkeypatch)
    window.on_show_shortcuts()
    assert f1_rows[0].endswith(": Shift+F1")
    assert sum(row.endswith(": Shift+F1") for row in f1_rows) == 1
    window.close()


def test_help_alt_l_registered_from_central_map(qtbot, monkeypatch):
    window = _help_window(qtbot, monkeypatch)
    assert window.nav_focus_shortcut is _shortcut(window, "Alt+L")
    window.close()
