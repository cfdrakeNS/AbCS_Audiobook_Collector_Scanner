"""ImportValidator length/duration warning tests."""

from __future__ import annotations

def test_unreadable_length_warning_when_files_have_no_duration(
    qapp, isolated_qsettings
):
    """Zero length with files present should warn about unreadable length, not minimum."""
    from src.core.validator import ImportValidator

    validator = ImportValidator()
    validator.rules_engine.min_book_length_minutes = 60
    book = {
        "title": "No Duration",
        "author": "Author",
        "year": 2020,
        "files": ["/tmp/a.mp3"],
        "time_hours": 0,
        "time_minutes": 0,
        "tracks": 1,
    }
    errors = validator.validate_book(book)
    assert any("Could not read length" in err for err in errors)
    assert not any("below minimum" in err.lower() for err in errors)

    book["time_hours"] = 1
    book["time_minutes"] = 30
    errors = validator.validate_book(book)
    assert not any("Could not read length" in err for err in errors)

