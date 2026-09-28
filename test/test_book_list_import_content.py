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


def test_header_auto_mapping_from_column_names(tmp_path, qtbot, temp_db, ui_scaler, theme_manager, isolated_qsettings):
    csv_path = tmp_path / "export_like.csv"
    csv_path.write_text(
        "Title,Author,Year,Series,Series Number,Genre,Narrator,Read Date,Time,Tracks,Collection,Comments\n"
        "One,A,2020,S,1,G,N,2026-01-01,1:00,3,Col,Plot here\n",
        encoding="utf-8-sig",
    )
    window = BookListImportWindow(temp_db, ui_scaler, theme_manager)
    qtbot.addWidget(window)
    window.file_has_header_check.setChecked(True)
    window.load_file(str(csv_path))
    mapping = window.get_field_mapping()
    assert mapping["title"] == 0
    assert mapping["author"] == 1
    assert mapping["plot"] == 11
    assert mapping["reader"] == 6
    window.close()


def test_mapping_table_field_order_plot_last(
    qtbot, temp_db, ui_scaler, theme_manager, isolated_qsettings
):
    window = BookListImportWindow(temp_db, ui_scaler, theme_manager)
    qtbot.addWidget(window)
    labels = []
    for row in range(window.mapping_table.rowCount()):
        widget = window.mapping_table.cellWidget(row, 0)
        if widget is not None:
            labels.append(widget.text().strip())
    assert labels[-1] == "Plot"
    assert "Plot" not in labels[:-1]
    window.close()
