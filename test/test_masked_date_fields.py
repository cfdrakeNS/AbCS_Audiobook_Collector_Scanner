"""Tests for typed year and date parsing and shared rules."""

from datetime import date, datetime, timedelta

import pytest

from src.accessibility.masked_date_fields import (
    date_future_message,
    date_invalid_message,
    format_iso_date,
    format_year,
    parse_iso_date_text,
    parse_year_text,
    preferred_year_range,
    year_invalid_message,
)


def test_parse_iso_date_blank_and_valid():
    assert parse_iso_date_text("") is None
    assert parse_iso_date_text("____-__-__") is None
    assert parse_iso_date_text("   -  -  ") is None
    assert parse_iso_date_text("2024-03-15") == date(2024, 3, 15)
    assert parse_iso_date_text("20240315") == date(2024, 3, 15)


def test_parse_iso_date_rejects_bad_values():
    with pytest.raises(ValueError):
        parse_iso_date_text("2024-02-30")
    with pytest.raises(ValueError):
        parse_iso_date_text("2026-09-31")
    with pytest.raises(ValueError):
        parse_iso_date_text("2024-1")
    with pytest.raises(ValueError):
        parse_iso_date_text("2024-03")


def test_parse_year_blank_and_valid():
    assert parse_year_text("") is None
    assert parse_year_text("____") is None
    assert parse_year_text("    ") is None
    assert parse_year_text("1999") == 1999


def test_parse_year_uses_preference_range():
    min_year, max_year = preferred_year_range()
    assert min_year == 1801
    assert max_year >= datetime.now().year
    with pytest.raises(ValueError):
        parse_year_text("1700")
    with pytest.raises(ValueError):
        parse_year_text(str(max_year + 1))
    assert parse_year_text(str(min_year)) == min_year
    assert parse_year_text(str(max_year)) == max_year


def test_parse_year_rejects_incomplete():
    with pytest.raises(ValueError):
        parse_year_text("21")


def test_invalid_messages_include_entered_text():
    assert "2026-09-31" in date_invalid_message("2026-09-31")
    assert "(blank)" in date_invalid_message("   ")
    assert "1799" in year_invalid_message("1799", min_year=1801, max_year=2026)
    assert "1801" in year_invalid_message("1799", min_year=1801, max_year=2026)
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    assert tomorrow in date_future_message(tomorrow)
    assert "future" in date_future_message(tomorrow).lower()


def test_format_helpers():
    assert format_iso_date(None) == ""
    assert format_iso_date(date(2020, 1, 2)) == "2020-01-02"
    assert format_year(None) == ""
    assert format_year(0) == ""
    assert format_year(2020) == "2020"


def test_masked_date_rejects_future(monkeypatch):
    from src.accessibility import masked_date_fields as mdf

    monkeypatch.setattr(mdf, "is_screen_reader_active", lambda: True)
    field = mdf.MaskedDateEdit(allow_blank=True, disallow_future=True)
    tomorrow = date.today() + timedelta(days=1)
    field.setText(tomorrow.isoformat())
    with pytest.raises(ValueError) as exc:
        field.validated_date()
    assert str(exc.value) == "future"
    assert field.validated_date.__doc__  # sanity
    field.setText(date.today().isoformat())
    assert field.validated_date() == date.today()
