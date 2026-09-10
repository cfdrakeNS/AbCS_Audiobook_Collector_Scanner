"""Focused unit tests for ImportRulesEngine."""

from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QSettings

from src.core.import_rules import ImportRulesEngine


def _settings() -> QSettings:
    settings = QSettings("AbCS", "AudioBookCollector")
    settings.clear()
    return settings


def _valid_book(**overrides):
    book = {
        "title": "Foundation",
        "author": "Isaac Asimov",
        "year": 1951,
        "folder": "Isaac Asimov/Foundation",
        "files": [],
        "time_hours": 8,
        "time_minutes": 30,
    }
    book.update(overrides)
    return book


def test_engine_loads_default_rule_settings(isolated_qsettings, qapp):
    _settings()
    engine = ImportRulesEngine()

    assert engine._rule_settings["title_blank"].enabled is True
    assert engine._rule_settings["title_blank"].severity == "error"
    assert engine._rule_settings["minimum_title_length"].enabled is False
    assert engine.min_title_length == 3
    assert engine.min_year == 1801
    assert engine.max_year == datetime.now().year


def test_reload_settings_reads_preference_keys(isolated_qsettings, qapp):
    settings = _settings()
    settings.setValue("import/rules/title_blank/enabled", False)
    settings.setValue("import/rules/title_blank/severity", "warning")
    settings.setValue("import/rules/minimum_title_length/enabled", True)
    settings.setValue("import/rules/minimum_title_length/value", 10)
    settings.setValue("import/rules/file_structure/pattern", "year_author_title")
    settings.sync()

    engine = ImportRulesEngine()
    assert engine._rule_settings["title_blank"].enabled is False
    assert engine._rule_settings["title_blank"].severity == "warning"
    assert engine._rule_settings["minimum_title_length"].enabled is True
    assert engine.min_title_length == 10
    assert engine.file_structure_pattern == "year_author_title"


def test_validate_reports_blank_title_and_author(isolated_qsettings, qapp):
    _settings()
    engine = ImportRulesEngine()
    errors = engine.validate(_valid_book(title="", author=""))

    assert "Title Blank" in errors
    assert "Author Blank" in errors


def test_validate_detects_author_name_in_title(isolated_qsettings, qapp):
    _settings()
    engine = ImportRulesEngine()
    errors = engine.validate(
        _valid_book(title="Isaac Asimov Foundation", author="Isaac Asimov")
    )
    assert "Author name in Title" in errors


def test_disabled_rule_is_skipped(isolated_qsettings, qapp):
    settings = _settings()
    settings.setValue("import/rules/author_name_in_title/enabled", False)
    settings.sync()

    engine = ImportRulesEngine()
    errors = engine.validate(
        _valid_book(title="Isaac Asimov Foundation", author="Isaac Asimov")
    )
    assert "Author name in Title" not in errors


def test_unknown_author_rule(isolated_qsettings, qapp):
    _settings()
    engine = ImportRulesEngine()
    errors = engine.validate(_valid_book(author="Various Artists"))
    assert "Author contains Unknown or Various" in errors


def test_message_severity_uses_configured_severity(isolated_qsettings, qapp):
    settings = _settings()
    settings.setValue("import/rules/author_name_in_title/severity", "error")
    settings.sync()

    engine = ImportRulesEngine()
    assert engine.message_severity("Author name in Title") == "error"
    assert engine.message_severity("Totally unknown message") is None


def test_year_out_of_range_when_enabled(isolated_qsettings, qapp):
    settings = _settings()
    settings.setValue("import/rules/year_out_of_range/enabled", True)
    settings.sync()

    engine = ImportRulesEngine()
    errors = engine.validate(_valid_book(year=1700))
    assert any("Year outside allowed range" in err for err in errors)

    errors = engine.validate(_valid_book(year="not-a-year"))
    assert "Year is not a valid number" in errors


def test_unreadable_audio_length_when_files_present(isolated_qsettings, qapp):
    _settings()
    engine = ImportRulesEngine()
    errors = engine.validate(
        _valid_book(files=["/tmp/a.mp3"], time_hours=0, time_minutes=0)
    )
    assert "Could not read length from audio files" in errors
