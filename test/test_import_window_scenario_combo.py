"""Import window Scenario combo: starts at Preferences, never writes them."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QKeySequence, QShortcut

from helpers.import_window_helpers import (
    apply_suppress_import_confirmations,
    cleanup_window,
)

from src.ui.import_window import ImportWindow


@pytest.fixture(autouse=True)
def suppress_import_confirmations(monkeypatch):
    apply_suppress_import_confirmations(monkeypatch)


def _shortcut_for(window, keys: str) -> QShortcut | None:
    wanted = QKeySequence(keys)
    for shortcut in window.findChildren(QShortcut):
        if shortcut.key() == wanted:
            return shortcut
    return None


def test_scenario_combo_starts_at_preferences_value(
    qtbot, temp_db, ui_scaler, theme_manager, isolated_qsettings
):
    QSettings("AbCS", "AudioBookCollector").setValue(
        "import/scenario/mode", "series_from_filename"
    )
    window = ImportWindow(temp_db, ui_scaler, theme_manager)
    qtbot.addWidget(window)

    assert window.scenario_combo.currentData() == "series_from_filename"
    assert window.import_scenario_mode == "series_from_filename"
    assert window.import_scanner.scenario_mode == "series_from_filename"

    cleanup_window(window)


def test_scenario_change_applies_to_scan_without_writing_preferences(
    qtbot, temp_db, ui_scaler, theme_manager, isolated_qsettings
):
    settings = QSettings("AbCS", "AudioBookCollector")
    settings.setValue("import/scenario/mode", "mass_standard")
    window = ImportWindow(temp_db, ui_scaler, theme_manager)
    qtbot.addWidget(window)

    window.scenario_combo.setCurrentIndex(
        window.scenario_combo.findData("series_from_directory_nested")
    )
    assert window.import_scenario_mode == "series_from_directory_nested"
    assert window.import_scanner.scenario_mode == "series_from_directory_nested"
    assert "Scenario for this import:" in window.status_bar.currentMessage()

    window._reload_scan_settings()
    assert window.import_scanner.scenario_mode == "series_from_directory_nested"
    assert settings.value("import/scenario/mode", type=str) == "mass_standard"

    cleanup_window(window)


def test_scenario_combo_locked_while_held_books_remain(
    qtbot, temp_db, ui_scaler, theme_manager, isolated_qsettings
):
    window = ImportWindow(temp_db, ui_scaler, theme_manager)
    qtbot.addWidget(window)

    window._set_review_combos_enabled(False)
    window.scanned_items = [{"status": "Duplicate"}]
    window._finish_scan_progress(
        canceled=False,
        elapsed_text="00:00",
        files_scanned=1,
        books_added=0,
        read_errors=0,
        summary_text="",
    )
    assert not window.scenario_combo.isEnabled()
    assert not window.collection_combo.isEnabled()

    window.scanned_items = []
    window._finish_scan_progress(
        canceled=False,
        elapsed_text="00:00",
        files_scanned=1,
        books_added=1,
        read_errors=0,
        summary_text="",
    )
    assert window.scenario_combo.isEnabled()
    assert window.collection_combo.isEnabled()

    cleanup_window(window)


def test_alt_n_focuses_scenario_combo(
    qtbot, temp_db, ui_scaler, theme_manager, isolated_qsettings
):
    window = ImportWindow(temp_db, ui_scaler, theme_manager)
    qtbot.addWidget(window)
    window.show()

    assert "N" in window.ALLOWED_ALT_LETTERS
    shortcut = _shortcut_for(window, "Alt+N")
    assert shortcut is not None
    window.folder_edit.setFocus(Qt.TabFocusReason)
    shortcut.activated.emit()
    qtbot.waitUntil(lambda: window.scenario_combo.hasFocus(), timeout=1000)

    cleanup_window(window)
