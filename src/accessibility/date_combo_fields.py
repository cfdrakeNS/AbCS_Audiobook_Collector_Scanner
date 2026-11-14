"""Year, Month, and Day as three non-editable combo boxes.

Small dialogs that must be read whole by the screen reader's read-dialog
command have no text fields: once focus has been in one, that command reads
only the window title and the focused control. Dates in those dialogs use
this widget instead of a typed date or QDateEdit.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from PySide6.QtCore import QDate, Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QWidget

from src.accessibility.screen_reader import is_screen_reader_active
from src.accessibility.style_helpers import build_accessible_combo_box_style

DEFAULT_MIN_YEAR = 1900
BLANK_TEXT = "Not set"


def make_date_combo_fields(parent=None, **kwargs):
    """Return DateComboFields when a screen reader is running, else None."""
    if is_screen_reader_active():
        return DateComboFields(parent, **kwargs)
    return None


class DateComboFields(QWidget):
    """Plain Up and Down step each value; typing digits jumps to a value.

    Values run oldest to newest, so Up moves earlier and Down moves later in
    all three boxes. The year list ends at the current year.

    With ``allow_blank``, each box ends with "Not set". Setting any box to
    "Not set" blanks the date; picking a value in a blank date fills the
    other boxes from today. The typed date field's ``text``,
    ``validated_date``, and ``setNullDate`` are provided so callers can use
    the same validation helpers.
    """

    dateChanged = Signal(QDate)

    def __init__(
        self,
        parent=None,
        *,
        min_year: int = DEFAULT_MIN_YEAR,
        max_year: int | None = None,
        scaled_height: int | None = None,
        allow_blank: bool = False,
        names: tuple[str, str, str] = ("Year", "Month", "Day"),
    ):
        super().__init__(parent)
        self._min_year = min_year
        self._max_year = QDate.currentDate().year() if max_year is None else max_year
        self._allow_blank = allow_blank
        self._disallow_future = False
        self._null_date = QDate()
        self._syncing = False
        self.year = QComboBox(self)
        self.month = QComboBox(self)
        self.month.addItems([f"{m:02d}" for m in range(1, 13)])
        if allow_blank:
            self.month.addItem(BLANK_TEXT)
        self.day = QComboBox(self)
        self._fill_years(None if allow_blank else str(self._max_year))
        style = build_accessible_combo_box_style(scaled_height)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        for combo, name in zip(self.parts(), names):
            combo.setEditable(False)
            combo.setAccessibleName(name)
            combo.setToolTip(name)
            combo.setStyleSheet(style)
            layout.addWidget(combo)
        layout.addStretch(1)
        self.setFocusProxy(self.year)
        if allow_blank:
            self.month.setCurrentIndex(self.month.count() - 1)
        self._refill_days()
        for combo in self.parts():
            combo.currentIndexChanged.connect(
                lambda _index, c=combo: self._on_part_changed(c)
            )

    def parts(self) -> tuple[QComboBox, QComboBox, QComboBox]:
        return (self.year, self.month, self.day)

    def _is_blank_part(self, combo: QComboBox) -> bool:
        return self._allow_blank and combo.currentText() == BLANK_TEXT

    def is_blank(self) -> bool:
        return self._is_blank_part(self.year)

    def _fill_years(self, select_text: str | None) -> None:
        self.year.blockSignals(True)
        self.year.clear()
        self.year.addItems(
            [str(y) for y in range(self._min_year, self._max_year + 1)]
        )
        if self._allow_blank:
            self.year.addItem(BLANK_TEXT)
        index = self.year.findText(select_text) if select_text else -1
        self.year.setCurrentIndex(index if index >= 0 else self.year.count() - 1)
        self.year.blockSignals(False)

    def _refill_days(self) -> None:
        was_blank = self._is_blank_part(self.day)
        keep = self.day.currentIndex()
        if self._is_blank_part(self.year) or self._is_blank_part(self.month):
            days = 31
        else:
            days = QDate(
                int(self.year.currentText()), self.month.currentIndex() + 1, 1
            ).daysInMonth()
        self.day.blockSignals(True)
        self.day.clear()
        self.day.addItems([f"{d:02d}" for d in range(1, days + 1)])
        if self._allow_blank:
            self.day.addItem(BLANK_TEXT)
        if was_blank or (self._allow_blank and self.is_blank()):
            self.day.setCurrentIndex(self.day.count() - 1)
        else:
            self.day.setCurrentIndex(min(max(keep, 0), days - 1))
        self.day.blockSignals(False)

    def _on_part_changed(self, combo: QComboBox) -> None:
        if self._syncing:
            return
        self._syncing = True
        try:
            if self._is_blank_part(combo):
                self._set_all_blank()
            elif self._allow_blank:
                self._fill_blank_parts_from_today()
            self._refill_days()
        finally:
            self._syncing = False
        self._emit_date_changed()

    def _set_all_blank(self) -> None:
        for combo in self.parts():
            combo.setCurrentIndex(combo.count() - 1)

    def _fill_blank_parts_from_today(self) -> None:
        today = QDate.currentDate()
        if self._is_blank_part(self.year):
            self.year.setCurrentText(str(today.year()))
        if self._is_blank_part(self.month):
            self.month.setCurrentIndex(today.month() - 1)
        if self._is_blank_part(self.day):
            self.day.setCurrentIndex(today.day() - 1)

    def _emit_date_changed(self) -> None:
        self.dateChanged.emit(self.date())

    def setNullDate(self, qdate: QDate) -> None:
        self._null_date = QDate(qdate)

    def setDisallowFuture(self, disallow: bool) -> None:
        self._disallow_future = bool(disallow)

    def setDate(self, qdate: QDate) -> None:
        """Show ``qdate``; the year list grows when the date is outside it.

        An invalid date or the null date blanks the boxes when blank is allowed.
        """
        if not qdate.isValid() or (self._allow_blank and qdate == self._null_date):
            if self._allow_blank:
                self._syncing = True
                try:
                    self._set_all_blank()
                    self._refill_days()
                finally:
                    self._syncing = False
                self._emit_date_changed()
            return
        self._syncing = True
        try:
            if qdate.year() < self._min_year or qdate.year() > self._max_year:
                self._min_year = min(self._min_year, qdate.year())
                self._max_year = max(self._max_year, qdate.year())
                self._fill_years(str(qdate.year()))
            self.year.setCurrentText(str(qdate.year()))
            self.month.setCurrentIndex(qdate.month() - 1)
            self.day.setCurrentIndex(0)
            self._refill_days()
            self.day.setCurrentIndex(qdate.day() - 1)
        finally:
            self._syncing = False
        self._emit_date_changed()

    def date(self) -> QDate:
        if self.is_blank():
            return QDate(self._null_date)
        return QDate(
            int(self.year.currentText()),
            self.month.currentIndex() + 1,
            self.day.currentIndex() + 1,
        )

    def text(self) -> str:
        """The date as yyyy-MM-dd, or empty when blank."""
        if self.is_blank():
            return ""
        return self.date().toString("yyyy-MM-dd")

    def validated_date(self) -> Optional[date]:
        """None when blank. Raises ValueError("future") for a date after today."""
        if self.is_blank():
            return None
        qdate = self.date()
        if self._disallow_future and qdate > QDate.currentDate():
            raise ValueError("future")
        return date(qdate.year(), qdate.month(), qdate.day())
