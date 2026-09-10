"""Book list import CSV/content helper coverage."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

pd = pytest.importorskip("pandas")

from src.ui.book_list_import_window import BookListImportWindow


def test_read_csv_with_fallback_loads_columns_and_rows(tmp_path: Path):
    csv_path = tmp_path / "books.csv"
    csv_path.write_text(
        "Title,Author,Year\nFoundation,Isaac Asimov,1951\nDune,Frank Herbert,1965\n",
        encoding="utf-8",
    )

    win = BookListImportWindow.__new__(BookListImportWindow)
    frame = BookListImportWindow._read_csv_with_fallback(
        win, str(csv_path), has_headers=True
    )

    assert list(frame.columns) == ["Title", "Author", "Year"]
    assert len(frame) == 2
    assert frame.iloc[0]["Title"] == "Foundation"
    assert frame.iloc[1]["Author"] == "Frank Herbert"


def test_parse_time_value_common_formats():
    win = BookListImportWindow.__new__(BookListImportWindow)
    assert BookListImportWindow._parse_time_value(win, "8:30") == (8, 30)
    assert BookListImportWindow._parse_time_value(win, "2h 15m") == (2, 15)
    assert BookListImportWindow._parse_time_value(win, None) is None


def test_parse_read_date_value_common_formats():
    win = BookListImportWindow.__new__(BookListImportWindow)
    assert BookListImportWindow._parse_read_date_value(win, "2024-04-05") == date(
        2024, 4, 5
    )
    assert BookListImportWindow._parse_read_date_value(win, "05/04/2024") in {
        date(2024, 4, 5),
        date(2024, 5, 4),
    }
    assert BookListImportWindow._parse_read_date_value(win, "not-a-date") is None


def test_excel_column_label():
    win = BookListImportWindow.__new__(BookListImportWindow)
    assert BookListImportWindow._excel_column_label(win, 0) == "A"
    assert BookListImportWindow._excel_column_label(win, 25) == "Z"
    assert BookListImportWindow._excel_column_label(win, 26) == "AA"
