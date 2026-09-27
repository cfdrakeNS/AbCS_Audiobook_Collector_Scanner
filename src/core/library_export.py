"""Export library metadata (the books shown on the main window) to CSV or JSON.

CSV is UTF-8 with a byte order mark so Excel opens accented names correctly.
Headers match Book List Import field names where one exists (Title, Author,
Year, Series, Genre, Reader, Read Date, Time) so an export can be re-imported.
JSON is an array of objects with snake_case keys and typed values.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Callable, Iterable

from src.utils.text_utils import series_number_key

FORMAT_CSV = "csv"
FORMAT_JSON = "json"

# Excel and LibreOffice Calc refuse to load a CSV cell longer than this.
CSV_CELL_LIMIT = 32767
CSV_TRUNCATED_MARKER = " [truncated]"


@dataclass
class ExportResult:
    count: int = 0
    truncated_books: int = 0


def _fit_csv_cell(text: str) -> tuple[str, bool]:
    if len(text) <= CSV_CELL_LIMIT:
        return text, False
    keep = CSV_CELL_LIMIT - len(CSV_TRUNCATED_MARKER)
    return text[:keep] + CSV_TRUNCATED_MARKER, True


def _date_text(value) -> str:
    if not value:
        return ""
    if isinstance(value, (date, datetime)):
        return value.strftime("%Y-%m-%d")
    return str(value).split(" ")[0]


def _series_number_value(book) -> int | float | None:
    key = series_number_key(book.series_number)
    if not key:
        return None
    try:
        return float(key) if "." in key else int(key)
    except ValueError:
        return None


def _listen_position_text(position_ms) -> str:
    if position_ms is None:
        return ""
    try:
        total_seconds = max(0, int(position_ms)) // 1000
    except (TypeError, ValueError):
        return ""
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}:{minutes:02d}:{seconds:02d}"


def _int_or_none(value) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _float_or_zero(value) -> float:
    try:
        return round(float(value or 0), 1)
    except (TypeError, ValueError):
        return 0.0


# (json key, CSV header, JSON value getter, CSV text getter)
_Field = tuple[str, str, Callable[[Any], Any], Callable[[Any], str]]

EXPORT_FIELDS: tuple[_Field, ...] = (
    ("title", "Title", lambda b: b.title or "", lambda b: b.title or ""),
    (
        "author",
        "Author",
        lambda b: b.author_name or "",
        lambda b: b.author_name or "",
    ),
    (
        "year",
        "Year",
        lambda b: _int_or_none(b.year),
        lambda b: str(_int_or_none(b.year) or ""),
    ),
    (
        "series",
        "Series",
        lambda b: b.series_name or "",
        lambda b: b.series_name or "",
    ),
    (
        "series_number",
        "Series Number",
        _series_number_value,
        lambda b: series_number_key(b.series_number),
    ),
    ("genre", "Genre", lambda b: b.genre_name or "", lambda b: b.genre_name or ""),
    (
        "collection",
        "Collection",
        lambda b: b.collection_name or "",
        lambda b: b.collection_name or "",
    ),
    ("reader", "Reader", lambda b: b.reader or "", lambda b: b.reader or ""),
    ("time", "Time", lambda b: b.time_display, lambda b: b.time_display),
    (
        "tracks",
        "Tracks",
        lambda b: _int_or_none(b.tracks) or 0,
        lambda b: str(_int_or_none(b.tracks) or 0),
    ),
    (
        "size_mb",
        "Size MB",
        lambda b: _float_or_zero(b.size_mb),
        lambda b: b.size_display,
    ),
    (
        "bitrate",
        "Bitrate",
        lambda b: _int_or_none(b.bitrate) or 0,
        lambda b: str(_int_or_none(b.bitrate) or 0),
    ),
    (
        "format",
        "Format",
        lambda b: b.file_format or "",
        lambda b: b.file_format or "",
    ),
    ("path", "Path", lambda b: b.path or "", lambda b: b.path or ""),
    (
        "read_date",
        "Read Date",
        lambda b: _date_text(b.read_date) or None,
        lambda b: _date_text(b.read_date),
    ),
    (
        "date_added",
        "Date Added",
        lambda b: _date_text(b.date_added) or None,
        lambda b: _date_text(b.date_added),
    ),
    (
        "want_to_read",
        "Want to Read",
        lambda b: bool(b.want_to_read),
        lambda b: "Yes" if b.want_to_read else "No",
    ),
    (
        "listen_position_ms",
        "Listen Position",
        lambda b: _int_or_none(b.listen_position_ms),
        lambda b: _listen_position_text(b.listen_position_ms),
    ),
    (
        "listen_file_name",
        "Listen File",
        lambda b: b.listen_file_name or "",
        lambda b: b.listen_file_name or "",
    ),
    (
        "comments",
        "Comments",
        lambda b: b.comments or "",
        lambda b: b.comments or "",
    ),
)

CSV_HEADERS: tuple[str, ...] = tuple(field[1] for field in EXPORT_FIELDS)
JSON_KEYS: tuple[str, ...] = tuple(field[0] for field in EXPORT_FIELDS)


def book_to_csv_row(book) -> list[str]:
    return [field[3](book) for field in EXPORT_FIELDS]


def book_to_json_object(book) -> dict[str, Any]:
    return {field[0]: field[2](book) for field in EXPORT_FIELDS}


def format_for_path(file_path: str, selected_filter: str = "") -> str:
    """Pick CSV or JSON from the file extension, then the dialog filter text."""
    suffix = Path(file_path).suffix.lower()
    if suffix == ".json":
        return FORMAT_JSON
    if suffix == ".csv":
        return FORMAT_CSV
    if "json" in (selected_filter or "").lower():
        return FORMAT_JSON
    return FORMAT_CSV


def ensure_extension(file_path: str, export_format: str) -> str:
    """Add .csv or .json when the typed name has no extension."""
    path = Path(file_path)
    if path.suffix:
        return file_path
    return str(path.with_suffix(".json" if export_format == FORMAT_JSON else ".csv"))


def export_books(books: Iterable, file_path: str, export_format: str) -> ExportResult:
    """Write books to file_path.

    CSV cells longer than ``CSV_CELL_LIMIT`` are cut and end with
    ``CSV_TRUNCATED_MARKER``; JSON is never cut. Raises OSError when the file
    cannot be written.
    """
    book_list = list(books)
    result = ExportResult(count=len(book_list))
    if export_format == FORMAT_JSON:
        with open(file_path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(
                [book_to_json_object(book) for book in book_list],
                handle,
                ensure_ascii=False,
                indent=2,
            )
            handle.write("\n")
    else:
        with open(file_path, "w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(CSV_HEADERS)
            for book in book_list:
                row = []
                cut_any = False
                for cell in book_to_csv_row(book):
                    text, cut = _fit_csv_cell(cell)
                    row.append(text)
                    cut_any = cut_any or cut
                if cut_any:
                    result.truncated_books += 1
                writer.writerow(row)
    return result
