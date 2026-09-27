"""Tests for src/core/library_export.py (v3 Phase 27)."""

import csv
import json
from datetime import date, datetime

from src.core.library_export import (
    CSV_CELL_LIMIT,
    CSV_HEADERS,
    CSV_TRUNCATED_MARKER,
    FORMAT_CSV,
    FORMAT_JSON,
    JSON_KEYS,
    ensure_extension,
    export_books,
    format_for_path,
)
from src.database.models import Book


def _book(**overrides):
    values = dict(
        book_id=1,
        title="The Hobbit",
        author_name="Tolkien, J.R.R.",
        year=1937,
        series_name="Middle-earth",
        series_number=1.0,
        genre_name="Fantasy",
        collection_name="Audio Books",
        reader="Andy Serkis",
        time_hours=10,
        time_minutes=25,
        tracks=12,
        size_mb=512.34,
        bitrate=64,
        file_format="m4b",
        path="F:\\audiobook\\Hobbit",
        comments="Line one\nLine two, with comma",
        read_date=date(2026, 3, 4),
        date_added=datetime(2026, 1, 2, 9, 30),
        want_to_read=False,
        listen_position_ms=3_723_000,
        listen_file_name="02.mp3",
    )
    values.update(overrides)
    return Book(**values)


def _read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))


def test_csv_headers_and_row(tmp_path):
    out = tmp_path / "lib.csv"
    result = export_books([_book()], str(out), FORMAT_CSV)
    assert result.count == 1
    assert result.truncated_books == 0
    rows = _read_csv(out)
    assert tuple(rows[0]) == CSV_HEADERS
    row = dict(zip(rows[0], rows[1]))
    assert row["Title"] == "The Hobbit"
    assert row["Author"] == "Tolkien, J.R.R."
    assert row["Year"] == "1937"
    assert row["Series Number"] == "1"
    assert row["Time"] == "10:25"
    assert row["Size MB"] == "512.3"
    assert row["Read Date"] == "2026-03-04"
    assert row["Date Added"] == "2026-01-02"
    assert row["Want to Read"] == "No"
    assert row["Listen Position"] == "1:02:03"
    assert row["Listen File"] == "02.mp3"
    assert row["Comments"] == "Line one\nLine two, with comma"


def test_csv_has_bom_for_excel(tmp_path):
    out = tmp_path / "lib.csv"
    export_books([_book()], str(out), FORMAT_CSV)
    assert out.read_bytes().startswith(b"\xef\xbb\xbf")


def test_csv_blank_optional_fields(tmp_path):
    out = tmp_path / "lib.csv"
    book = _book(
        year=None,
        series_number=None,
        read_date=None,
        listen_position_ms=None,
        listen_file_name="",
        want_to_read=True,
    )
    export_books([book], str(out), FORMAT_CSV)
    row = dict(zip(*_read_csv(out)))
    assert row["Year"] == ""
    assert row["Series Number"] == ""
    assert row["Read Date"] == ""
    assert row["Listen Position"] == ""
    assert row["Want to Read"] == "Yes"


def test_decimal_series_number(tmp_path):
    out = tmp_path / "lib.csv"
    export_books([_book(series_number=6.5)], str(out), FORMAT_CSV)
    row = dict(zip(*_read_csv(out)))
    assert row["Series Number"] == "6.5"


def test_non_ascii_names_round_trip(tmp_path):
    out = tmp_path / "lib.csv"
    export_books([_book(author_name="Márquez, Gabriel García")], str(out), FORMAT_CSV)
    row = dict(zip(*_read_csv(out)))
    assert row["Author"] == "Márquez, Gabriel García"


def test_json_typed_values(tmp_path):
    out = tmp_path / "lib.json"
    result = export_books(
        [_book(), _book(book_id=2, title="Second", want_to_read=True, year=None)],
        str(out),
        FORMAT_JSON,
    )
    assert result.count == 2
    data = json.loads(out.read_text(encoding="utf-8"))
    assert len(data) == 2
    assert tuple(data[0].keys()) == JSON_KEYS
    assert data[0]["year"] == 1937
    assert data[0]["series_number"] == 1
    assert data[0]["want_to_read"] is False
    assert data[0]["listen_position_ms"] == 3_723_000
    assert data[0]["read_date"] == "2026-03-04"
    assert data[1]["year"] is None
    assert data[1]["want_to_read"] is True


def test_export_keeps_given_order(tmp_path):
    out = tmp_path / "lib.csv"
    books = [_book(book_id=i, title=f"Book {i}") for i in (3, 1, 2)]
    export_books(books, str(out), FORMAT_CSV)
    titles = [row[0] for row in _read_csv(out)[1:]]
    assert titles == ["Book 3", "Book 1", "Book 2"]


def test_empty_library_csv_writes_headers_only(tmp_path):
    out = tmp_path / "lib.csv"
    assert export_books([], str(out), FORMAT_CSV).count == 0
    assert _read_csv(out) == [list(CSV_HEADERS)]


def test_empty_library_json_is_empty_array(tmp_path):
    out = tmp_path / "lib.json"
    assert export_books([], str(out), FORMAT_JSON).count == 0
    assert json.loads(out.read_text(encoding="utf-8")) == []


def test_csv_cuts_cells_over_spreadsheet_limit(tmp_path):
    out = tmp_path / "lib.csv"
    long_text = "0000028A " * 10_000
    books = [_book(comments=long_text), _book(book_id=2, comments="short")]
    result = export_books(books, str(out), FORMAT_CSV)
    assert result.truncated_books == 1
    rows = [dict(zip(_read_csv(out)[0], r)) for r in _read_csv(out)[1:]]
    assert len(rows[0]["Comments"]) == CSV_CELL_LIMIT
    assert rows[0]["Comments"].endswith(CSV_TRUNCATED_MARKER)
    assert rows[1]["Comments"] == "short"


def test_csv_cell_at_limit_is_not_cut(tmp_path):
    out = tmp_path / "lib.csv"
    text = "x" * CSV_CELL_LIMIT
    result = export_books([_book(comments=text)], str(out), FORMAT_CSV)
    assert result.truncated_books == 0
    assert dict(zip(*_read_csv(out)))["Comments"] == text


def test_json_keeps_long_text(tmp_path):
    out = tmp_path / "lib.json"
    long_text = "y" * (CSV_CELL_LIMIT + 500)
    result = export_books([_book(comments=long_text)], str(out), FORMAT_JSON)
    assert result.truncated_books == 0
    assert json.loads(out.read_text(encoding="utf-8"))[0]["comments"] == long_text


def test_format_for_path():
    assert format_for_path("a.json") == FORMAT_JSON
    assert format_for_path("a.CSV") == FORMAT_CSV
    assert format_for_path("a", "JSON Files (*.json)") == FORMAT_JSON
    assert format_for_path("a", "CSV Files (*.csv)") == FORMAT_CSV
    assert format_for_path("a.csv", "JSON Files (*.json)") == FORMAT_CSV


def test_ensure_extension():
    assert ensure_extension("out", FORMAT_JSON).endswith("out.json")
    assert ensure_extension("out", FORMAT_CSV).endswith("out.csv")
    assert ensure_extension("out.txt", FORMAT_CSV) == "out.txt"
