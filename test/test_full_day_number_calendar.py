"""FullDayNumberCalendar: single-letter days, no week column, readable cells."""

from __future__ import annotations

import sys

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QCalendarWidget, QDateEdit, QTableView

from src.accessibility.style_helpers import FullDayNumberCalendar


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def _day_row(cal: FullDayNumberCalendar) -> list[str]:
    view = cal.findChild(QTableView, "qt_calendar_calendarview")
    assert view is not None
    model = view.model()
    assert model is not None
    return [
        str(model.data(model.index(0, col), Qt.DisplayRole) or "")
        for col in range(model.columnCount())
    ]


def test_single_letter_day_names_no_week_column(qapp):
    cal = FullDayNumberCalendar()
    cal.show()
    qapp.processEvents()
    cal.fit_day_cells()
    qapp.processEvents()

    assert cal.verticalHeaderFormat() == QCalendarWidget.NoVerticalHeader
    assert cal.horizontalHeaderFormat() == QCalendarWidget.SingleLetterDayNames
    # Follows app/UIScaler font, not a fixed 10pt ignore-zoom size.
    assert cal.font().pointSize() >= 9

    names = _day_row(cal)
    assert len(names) == 7
    assert all(len(n) == 1 for n in names), names
    # Locale-dependent letters, but must be single chars not "Wed"/empty.
    assert "" not in names


def test_calendar_font_tracks_app_scale(qapp):
    """Calendar must not stay stuck at a fixed point size when UI font grows."""
    from PySide6.QtGui import QFont

    previous = QFont(qapp.font())
    grown = QFont(previous)
    grown.setPointSize(18)
    qapp.setFont(grown)
    try:
        cal = FullDayNumberCalendar()
        cal.show()
        qapp.processEvents()
        cal.fit_day_cells()
        assert cal.font().pointSize() >= 18
        names = _day_row(cal)
        assert all(len(n) == 1 for n in names), names
    finally:
        qapp.setFont(previous)


def test_date_edit_popup_sites_keep_single_letters(qapp):
    """Main / Book Details / Reading History all use the same calendar class."""
    large = QFont()
    large.setPointSize(14)

    for label in ("main", "book_details", "reading_history"):
        edit = QDateEdit()
        edit.setCalendarPopup(True)
        edit.setFont(large)
        if label == "book_details":
            # Mirror Book Details scaled stylesheet (must not force ShortDayNames).
            cal = FullDayNumberCalendar(edit)
            cal.setStyleSheet(
                """
                QCalendarWidget { font-size: 14pt; }
                QCalendarWidget QAbstractItemView:enabled { font-size: 14pt; }
                """
            )
        else:
            cal = FullDayNumberCalendar(edit)
        edit.setCalendarWidget(cal)
        edit.show()
        qapp.processEvents()
        cal.show()
        cal.fit_day_cells()
        qapp.processEvents()

        names = _day_row(cal)
        assert len(names) == 7, label
        assert all(len(n) == 1 for n in names), (label, names)
        view = cal.findChild(QTableView, "qt_calendar_calendarview")
        assert view is not None
        assert all(view.columnWidth(c) >= 28 for c in range(7)), label
        edit.hide()
        cal.hide()
