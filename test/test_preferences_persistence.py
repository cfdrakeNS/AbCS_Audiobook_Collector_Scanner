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


def test_fresh_install_shows_restore_defaults_values(
    ui_scaler, theme_manager, isolated_qsettings, qtbot
):
    from unittest.mock import patch

    from PySide6.QtWidgets import QMessageBox

    window = PreferencesWindow(ui_scaler, theme_manager)
    qtbot.addWidget(window)
    fresh = window._capture_state()

    with patch(
        "src.ui.preferences_window.exec_styled_message_box",
        return_value=QMessageBox.Yes,
    ):
        window.on_restore_defaults()
    restored = window._capture_state()
    window.close()

    # Theme and zoom follow the running app, not stored import defaults.
    for key in ("theme", "scale"):
        fresh.pop(key)
        restored.pop(key)
    assert fresh == restored


def test_aac_and_opus_formats_listed_and_checked_by_default(
    ui_scaler, theme_manager, isolated_qsettings, qtbot
):
    window = PreferencesWindow(ui_scaler, theme_manager)
    qtbot.addWidget(window)
    assert window.format_checks["aac"].isChecked()
    assert window.format_checks["opus"].isChecked()
    assert window.format_checks["aac"].accessibleName() == "AAC format"
    window.format_checks["opus"].setChecked(False)
    window.on_save()
    stored = QSettings("AbCS", "AudioBookCollector")
    assert stored.value("import/formats/opus", True, type=bool) is False
    window.close()


def test_fresh_install_import_checks_use_restore_defaults_values(isolated_qsettings, qapp):
    from src.core.validator import ImportValidator

    validator = ImportValidator()
    assert validator.duplicate_match_mode == "title_author_only"
    assert validator.duplicate_fuzzy_threshold == 90
    rules = validator.rules_engine._rule_settings
    assert rules["title_in_author_name"].severity == "warning"
    assert rules["minimum_title_length"].enabled is True
    assert rules["file_structure"].enabled is True
    assert rules["year_out_of_range"].enabled is True
