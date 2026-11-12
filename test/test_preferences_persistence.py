"""PreferencesWindow persistence via QSettings."""

from __future__ import annotations

from PySide6.QtCore import QSettings

from src.core.update_check import AUTO_CHECK_UPDATES_SETTING
from src.ui.preferences_window import PreferencesWindow


def test_enter_presses_focused_preferences_button(
    ui_scaler, theme_manager, isolated_qsettings, qtbot, monkeypatch
):
    from PySide6.QtCore import QEvent, Qt
    from PySide6.QtGui import QKeyEvent
    from PySide6.QtWidgets import QMessageBox

    monkeypatch.setattr(
        "src.ui.preferences_window.exec_styled_message_box",
        lambda *a, **k: QMessageBox.No,
    )
    window = PreferencesWindow(ui_scaler, theme_manager)
    qtbot.addWidget(window)
    clicked = []
    window.restore_defaults_button.clicked.connect(lambda: clicked.append("restore"))
    window.save_button.clicked.connect(lambda: clicked.append("save"))

    for button, key in (
        (window.restore_defaults_button, Qt.Key_Return),
        (window.save_button, Qt.Key_Enter),
    ):
        monkeypatch.setattr(window, "focusWidget", lambda b=button: b)
        event = QKeyEvent(QEvent.KeyPress, key, Qt.NoModifier)
        window.keyPressEvent(event)
        assert event.isAccepted()

    assert clicked == ["restore", "save"]
    window.close()


def test_restore_defaults_confirms_with_a_popup(
    ui_scaler, theme_manager, isolated_qsettings, qtbot, monkeypatch
):
    from PySide6.QtWidgets import QMessageBox

    boxes = []

    def record_box(*_args, **kwargs):
        boxes.append(kwargs)
        return QMessageBox.Yes

    monkeypatch.setattr("src.ui.preferences_window.exec_styled_message_box", record_box)
    window = PreferencesWindow(ui_scaler, theme_manager)
    qtbot.addWidget(window)
    try:
        window.on_restore_defaults()
        assert len(boxes) == 2
        assert boxes[1]["text"] == "All preferences restored to default values."
        assert boxes[1]["buttons"] == QMessageBox.Ok
    finally:
        window.close()


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


def test_import_settings_have_no_tag_mapping(
    ui_scaler, theme_manager, isolated_qsettings, qtbot
):
    from PySide6.QtWidgets import QComboBox, QGroupBox

    window = PreferencesWindow(ui_scaler, theme_manager)
    qtbot.addWidget(window)
    group_titles = {group.title() for group in window.findChildren(QGroupBox)}
    combo_names = {combo.accessibleName() for combo in window.findChildren(QComboBox)}
    assert "Tag mapping" not in group_titles
    assert "Book title tag" not in combo_names
    assert "Author tag" not in combo_names
    assert "title_tag" not in window._capture_state()
    window.close()


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


def test_preferences_unsaved_prompt_hides_cancel(
    ui_scaler, theme_manager, isolated_qsettings, monkeypatch
):
    from PySide6.QtWidgets import QMessageBox

    seen = {}

    def fake_box(*args, **kwargs):
        seen.update(kwargs)
        return QMessageBox.No

    monkeypatch.setattr("src.ui.preferences_window.exec_styled_message_box", fake_box)
    window = PreferencesWindow(ui_scaler, theme_manager)
    try:
        reply = window._confirm_exit_with_changes()
        assert reply == QMessageBox.No
        assert "Press Escape to cancel" in seen["text"]
        assert "reverts the changes" in seen["text"]
        assert QMessageBox.Cancel not in seen["button_texts"]
        assert seen["escape_only_button"] == QMessageBox.Cancel
    finally:
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
