"""PreferencesWindow persistence via QSettings."""

from __future__ import annotations

from PySide6.QtCore import QSettings

from src.ui.preferences_window import PreferencesWindow


def test_preferences_author_fallback_persists_on_save(
    ui_scaler, theme_manager, isolated_qsettings, qtbot
):
    settings = QSettings("AbCS", "AudioBookCollector")
    settings.clear()
    settings.setValue("import/fallback/author_to_folder", True)
    settings.sync()

    window = PreferencesWindow(ui_scaler, theme_manager)
    qtbot.addWidget(window)
    assert window.author_fallback_checkbox.isChecked() is True

    window.author_fallback_checkbox.setChecked(False)
    window.on_save()

    stored = QSettings("AbCS", "AudioBookCollector")
    assert stored.value("import/fallback/author_to_folder", True, type=bool) is False

    reopened = PreferencesWindow(ui_scaler, theme_manager)
    qtbot.addWidget(reopened)
    assert reopened.author_fallback_checkbox.isChecked() is False
    reopened.close()
