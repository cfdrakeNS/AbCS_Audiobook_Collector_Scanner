"""Year, Month, and Day as three non-editable combo boxes.

Small dialogs that must be read whole by the screen reader's read-dialog
command have no text fields: once focus has been in one, that command reads
only the window title and the focused control. Dates in those dialogs use
this widget instead of a typed date or QDateEdit.
"""

from __future__ import annotations

from PySide6.QtCore import QDate, Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QWidget

from src.accessibility.style_helpers import build_accessible_combo_box_style

DEFAULT_MIN_YEAR = 1900


class DateComboFields(QWidget):
    """Plain Up and Down step each value; typing digits jumps to a value.

    Values run oldest to newest, so Up moves earlier and Down moves later in
    all three boxes. The year list ends at the current year.
    """

    dateChanged = Signal(QDate)

    def __init__(
        self,
        parent=None,
        *,
        min_year: int = DEFAULT_MIN_YEAR,
        max_year: int | None = None,
        scaled_height: int | None = None,
    ):
        super().__init__(parent)
        self._min_year = min_year
        self._max_year = QDate.currentDate().year() if max_year is None else max_year
        self.year = QComboBox(self)
        self.month = QComboBox(self)
        self.month.addItems([f"{m:02d}" for m in range(1, 13)])
        self.day = QComboBox(self)
        self._fill_years()
        style = build_accessible_combo_box_style(scaled_height)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        for combo, name in ((self.year, "Year"), (self.month, "Month"), (self.day, "Day")):
            combo.setEditable(False)
            combo.setAccessibleName(name)
            combo.setToolTip(name)
            combo.setStyleSheet(style)
            layout.addWidget(combo)
        layout.addStretch(1)
        self.setFocusProxy(self.year)
        self.year.currentIndexChanged.connect(self._refill_days)
        self.month.currentIndexChanged.connect(self._refill_days)
        self.day.currentIndexChanged.connect(self._emit_date_changed)
        self._refill_days()

    def _fill_years(self) -> None:
        self.year.blockSignals(True)
        self.year.clear()
        self.year.addItems(
            [str(y) for y in range(self._min_year, self._max_year + 1)]
        )
        self.year.setCurrentIndex(self.year.count() - 1)
        self.year.blockSignals(False)

    def _refill_days(self, *_args) -> None:
        keep = self.day.currentIndex()
        days = QDate(
            int(self.year.currentText()), self.month.currentIndex() + 1, 1
        ).daysInMonth()
        self.day.blockSignals(True)
        self.day.clear()
        self.day.addItems([f"{d:02d}" for d in range(1, days + 1)])
        self.day.setCurrentIndex(min(max(keep, 0), days - 1))
        self.day.blockSignals(False)
        self._emit_date_changed()

    def _emit_date_changed(self, *_args) -> None:
        self.dateChanged.emit(self.date())

    def setDate(self, qdate: QDate) -> None:
        """Show ``qdate``; the year list grows when the date is outside it."""
        if not qdate.isValid():
            return
        if qdate.year() < self._min_year or qdate.year() > self._max_year:
            self._min_year = min(self._min_year, qdate.year())
            self._max_year = max(self._max_year, qdate.year())
            self._fill_years()
        self.year.setCurrentText(str(qdate.year()))
        self.month.setCurrentIndex(qdate.month() - 1)
        self.day.setCurrentIndex(qdate.day() - 1)

    def date(self) -> QDate:
        return QDate(
            int(self.year.currentText()),
            self.month.currentIndex() + 1,
            self.day.currentIndex() + 1,
        )
