"""Tests for centralized QSettings read with legacy fallback."""

import pytest
from PySide6.QtCore import QSettings

from src.utils.settings_helpers import (
    get_import_preferences,
    is_proper_case_enabled,
    migrate_legacy_import_settings,
    purge_stale_settings,
    read_setting,
)


@pytest.fixture
def isolated_qsettings(tmp_path):
    original_format = QSettings.defaultFormat()
    QSettings.setDefaultFormat(QSettings.IniFormat)
    QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, str(tmp_path))
    try:
        yield
    finally:
        QSettings.setDefaultFormat(original_format)


def _fresh_settings(app: str) -> QSettings:
    settings = QSettings("AbCS", app)
    settings.clear()
    return settings


def test_read_setting_uses_audiobook_collector_first(isolated_qsettings):
    current = _fresh_settings("AudioBookCollector")
    legacy = _fresh_settings("AbCS")
    legacy.setValue("import/rules/duplicate/match_mode", "legacy_mode")
    current.setValue("import/rules/duplicate/match_mode", "current_mode")

    assert (
        read_setting(
            "import/rules/duplicate/match_mode",
            "title_author_year_collection",
            type=str,
        )
        == "current_mode"
    )


def test_read_setting_falls_back_to_legacy(isolated_qsettings):
    _fresh_settings("AudioBookCollector")
    legacy = _fresh_settings("AbCS")
    legacy.setValue("import/rules/duplicate/fuzzy_threshold", 88)

    assert read_setting("import/rules/duplicate/fuzzy_threshold", 0, type=int) == 88


def test_read_setting_default_when_missing_everywhere(isolated_qsettings):
    _fresh_settings("AudioBookCollector")
    _fresh_settings("AbCS")

    assert (
        read_setting(
            "import/rules/duplicate/match_mode",
            "title_author_year_collection",
            type=str,
        )
        == "title_author_year_collection"
    )


def test_is_proper_case_enabled_uses_scan_key(isolated_qsettings):
    current = _fresh_settings("AudioBookCollector")
    legacy = _fresh_settings("AbCS")
    legacy.setValue("import/autocorrect/proper_case", False)
    current.setValue("import/scan/proper_case", True)

    assert is_proper_case_enabled() is True


def test_is_proper_case_enabled_falls_back_to_legacy_autocorrect_key(
    isolated_qsettings,
):
    _fresh_settings("AudioBookCollector")
    legacy = _fresh_settings("AbCS")
    legacy.setValue("import/autocorrect/proper_case", True)

    assert is_proper_case_enabled() is True


def test_migrate_legacy_import_settings_copies_prefs_and_removes_legacy_import(
    isolated_qsettings,
):
    current = _fresh_settings("AudioBookCollector")
    legacy = _fresh_settings("AbCS")
    legacy.setValue("import/flip_author_name", True)
    legacy.setValue("import/autocorrect/move_leading_the_title", True)
    legacy.setValue("import/autocorrect/proper_case", True)
    legacy.sync()

    migrate_legacy_import_settings()

    assert current.value("import/flip_author_name", type=bool) is True
    assert (
        current.value("import/autocorrect/move_leading_the_title", type=bool) is True
    )
    assert current.value("import/scan/proper_case", type=bool) is True
    assert not legacy.contains("import")


def test_purge_stale_settings_removes_obsolete_import_rules(isolated_qsettings):
    from src.utils.settings_helpers import purge_stale_settings

    settings = _fresh_settings("AudioBookCollector")
    settings.setValue("import/rules/genre_missing/enabled", True)
    settings.setValue("import/rules/bitrate_below_minimum/enabled", True)
    settings.setValue("import/rules/bitrate_below_minimum/value", 64)
    settings.sync()

    purge_stale_settings()

    assert not settings.contains("import/rules/genre_missing")
    assert not settings.contains("import/rules/bitrate_below_minimum")
    assert not settings.contains("import/rules/bitrate_below_minimum/enabled")


def test_get_import_preferences_reads_legacy_keys(isolated_qsettings):
    _fresh_settings("AudioBookCollector")
    legacy = _fresh_settings("AbCS")
    legacy.setValue("import/flip_author_name", True)
    legacy.setValue("import/autocorrect/move_leading_the_title", False)
    legacy.sync()

    move_articles, flip_author = get_import_preferences()

    assert move_articles is False
    assert flip_author is True


def test_purge_stale_settings_preserves_web_metadata_pref_keys(isolated_qsettings):
    settings = _fresh_settings("AudioBookCollector")
    settings.setValue("import/flip_author_name", True)
    settings.setValue("import/autocorrect/move_leading_the_title", True)
    settings.sync()

    purge_stale_settings()

    assert settings.value("import/flip_author_name", type=bool) is True
    assert (
        settings.value("import/autocorrect/move_leading_the_title", type=bool) is True
    )
