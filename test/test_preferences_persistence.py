"""PreferencesWindow persistence via QSettings."""

from __future__ import annotations

from PySide6.QtCore import QSettings

from src.core.update_check import AUTO_CHECK_UPDATES_SETTING
from src.ui.preferences_window import PreferencesWindow


def test_auto_check_updates_defaults_off_and_restores(
    ui_scaler, theme_manager, isolated_qsettings, qtbot
):
    from unittest.mock import patch

    from PySide6.QtWidgets import QMessageBox

    window = PreferencesWindow(ui_scaler, theme_manager)
    qtbot.addWidget(window)
    assert window.auto_check_updates_checkbox.isChecked() is False

    window.auto_check_updates_checkbox.setChecked(True)
    window.on_save()

    stored = QSettings("AbCS", "AudioBookCollector")
    assert stored.value(AUTO_CHECK_UPDATES_SETTING, False, type=bool) is True

    reopened = PreferencesWindow(ui_scaler, theme_manager)
    qtbot.addWidget(reopened)
    assert reopened.auto_check_updates_checkbox.isChecked() is True

    with patch(
        "src.ui.preferences_window.exec_styled_message_box",
        return_value=QMessageBox.Yes,
    ):
        reopened.on_restore_defaults()
    assert reopened.auto_check_updates_checkbox.isChecked() is False
    assert stored.value(AUTO_CHECK_UPDATES_SETTING, True, type=bool) is False
    reopened.close()


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


def test_preferences_tag_mapping_round_trip_and_restore(
    ui_scaler, theme_manager, isolated_qsettings, qtbot
):
    from unittest.mock import patch

    from PySide6.QtWidgets import QMessageBox

    from src.core.tag_mapping import (
        AUTHOR_ARTIST_ONLY,
        AUTHOR_TAG_SETTING,
        TITLE_ALBUM,
        TITLE_TAG_SETTING,
        TITLE_TRACK,
    )

    window = PreferencesWindow(ui_scaler, theme_manager)
    qtbot.addWidget(window)
    assert window.title_tag_combo.currentData() == TITLE_ALBUM
    assert window.title_tag_combo.accessibleName() == "Book title tag"
    assert window.author_tag_combo.accessibleName() == "Author tag"

    window.title_tag_combo.setCurrentIndex(window.title_tag_combo.findData(TITLE_TRACK))
    window.author_tag_combo.setCurrentIndex(
        window.author_tag_combo.findData(AUTHOR_ARTIST_ONLY)
    )
    window.on_save()

    stored = QSettings("AbCS", "AudioBookCollector")
    assert stored.value(TITLE_TAG_SETTING, type=str) == TITLE_TRACK
    assert stored.value(AUTHOR_TAG_SETTING, type=str) == AUTHOR_ARTIST_ONLY

    reopened = PreferencesWindow(ui_scaler, theme_manager)
    qtbot.addWidget(reopened)
    assert reopened.title_tag_combo.currentData() == TITLE_TRACK
    assert reopened.author_tag_combo.currentData() == AUTHOR_ARTIST_ONLY

    with patch(
        "src.ui.preferences_window.exec_styled_message_box",
        return_value=QMessageBox.Yes,
    ):
        reopened.on_restore_defaults()
    assert reopened.title_tag_combo.currentData() == TITLE_ALBUM
    assert stored.value(TITLE_TAG_SETTING, type=str) == TITLE_ALBUM
    reopened.close()
