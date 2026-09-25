"""Year and date fields/validation for AbCS (screen reader and classic).

Rules (single source of truth):
- Publication year: Preferences range (default 1801 through current year), or blank.
- Read dates and history dates: valid calendar day as yyyy-MM-dd, blank only when
  allowed, and never after today.
- Invalid values: beep + warning that includes the text entered. Typed values are
  not cleared on the screen-reader fields so they can be corrected.

Screen reader: plain QLineEdit with placeholder (no underscore mask).
No screen reader: QSpinBox / QDateEdit with the same validation helpers.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional, Tuple

from PySide6.QtCore import QDate, QSettings, QTimer, Signal
from PySide6.QtWidgets import QApplication, QLineEdit, QMessageBox

from src.accessibility.screen_reader import is_screen_reader_active

DATE_DISPLAY = "yyyy-MM-dd"
DATE_PLACEHOLDER = "yyyy-MM-dd"
YEAR_PLACEHOLDER = "yyyy"
DEFAULT_MIN_YEAR = 1801
# Shared null/blank sentinel for classic QDateEdit special value.
NULL_READ_QDATE = QDate(2000, 1, 1)
# Classic QDateEdit: specialValueText must be non-empty or Qt shows the real minimum date.
CLASSIC_DATE_BLANK_TEXT = " "
CLASSIC_DATE_MINIMUM = QDate(1752, 9, 14)


def use_masked_date_fields() -> bool:
    """True when the window should use typed text instead of spin/date edit."""
    return is_screen_reader_active()


def today_date() -> date:
    return date.today()


def today_qdate() -> QDate:
    return QDate.currentDate()


def preferred_year_range() -> Tuple[int, int]:
    """Return (min_year, max_year) matching Preferences year consistency."""
    settings = QSettings("AbCS", "AudioBookCollector")
    current = datetime.now().year
    min_year = settings.value(
        "import/rules/year_out_of_range/min_year", DEFAULT_MIN_YEAR, type=int
    )
    max_year = settings.value(
        "import/rules/year_out_of_range/max_year", current, type=int
    )
    try:
        min_year = int(min_year)
    except (TypeError, ValueError):
        min_year = DEFAULT_MIN_YEAR
    try:
        max_year = int(max_year)
    except (TypeError, ValueError):
        max_year = current
    if min_year < 1:
        min_year = DEFAULT_MIN_YEAR
    if max_year < current:
        max_year = current
    if max_year < min_year:
        max_year = min_year
    return min_year, max_year


def _clean_date_year_text(text: str) -> str:
    return (text or "").strip().replace("_", "").replace(" ", "")


def parse_iso_date_text(text: str) -> Optional[date]:
    """Return a date from yyyy-MM-dd text, or None when blank."""
    raw = _clean_date_year_text(text)
    if not raw or raw == "--":
        return None
    if len(raw) == 8 and raw.isdigit():
        iso = f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"
    elif len(raw) == 10 and raw[4] == "-" and raw[7] == "-":
        iso = raw
    else:
        raise ValueError("incomplete")
    try:
        return datetime.strptime(iso, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError("invalid") from exc


def format_iso_date(value: Optional[date]) -> str:
    if value is None:
        return ""
    return value.isoformat()


def parse_year_text(
    text: str,
    *,
    min_year: Optional[int] = None,
    max_year: Optional[int] = None,
) -> Optional[int]:
    """Return a year int, None when blank, or raise ValueError when invalid."""
    raw = _clean_date_year_text(text)
    if not raw:
        return None
    if not raw.isdigit() or len(raw) != 4:
        raise ValueError("incomplete")
    year = int(raw)
    if min_year is None or max_year is None:
        pref_min, pref_max = preferred_year_range()
        if min_year is None:
            min_year = pref_min
        if max_year is None:
            max_year = pref_max
    if year < min_year or year > max_year:
        raise ValueError("invalid")
    return year


def format_year(value: Optional[int]) -> str:
    if value is None or value == 0:
        return ""
    return f"{int(value):04d}"


def _display_entered(text: str) -> str:
    shown = (text or "").strip()
    return shown if shown else "(blank)"


def year_invalid_message(entered: str, *, min_year: int, max_year: int) -> str:
    return (
        f"Year '{_display_entered(entered)}' is not valid. "
        f"Enter a year from {min_year} to {max_year}, or leave blank."
    )


def date_invalid_message(entered: str, *, allow_blank: bool = True) -> str:
    if allow_blank:
        return (
            f"Date '{_display_entered(entered)}' is not valid. "
            "Enter a date as year-month-day, or leave blank."
        )
    return (
        f"Date '{_display_entered(entered)}' is not valid. "
        "Enter a date as year-month-day."
    )


def date_future_message(entered: str) -> str:
    return (
        f"Date '{_display_entered(entered)}' is in the future. "
        "Enter today or an earlier date."
    )


def warn_masked_field_error(parent, message: str, *, title: str = "Invalid Entry") -> None:
    """Beep and show a warning dialog (works for JAWS/NVDA and sighted)."""
    from src.accessibility.style_helpers import exec_styled_message_box

    QApplication.beep()
    scaled = 14
    scaler = getattr(parent, "scaler", None) if parent is not None else None
    if scaler is None and parent is not None:
        widget = parent.parentWidget() if hasattr(parent, "parentWidget") else None
        while widget is not None and scaler is None:
            scaler = getattr(widget, "scaler", None)
            widget = widget.parentWidget()
    if scaler is not None:
        try:
            scaled = scaler.get_scaled_size(14)
        except Exception:
            pass
    exec_styled_message_box(
        parent,
        scaled,
        icon=QMessageBox.Warning,
        title=title,
        text=message,
    )


def apply_preferred_year_spin_range(spin) -> Tuple[int, int]:
    """Set a QSpinBox to blank=0 and max=Preferences max year."""
    min_year, max_year = preferred_year_range()
    spin.setRange(0, max_year)
    spin.setSpecialValueText("")
    return min_year, max_year


def configure_no_future_date_edit(date_edit, *, null_date: Optional[QDate] = None) -> None:
    """Clamp classic or typed date fields so a future day cannot be chosen."""
    today = today_qdate()
    if hasattr(date_edit, "setMaximumDate"):
        date_edit.setMaximumDate(today)
    if null_date is not None and hasattr(date_edit, "setNullDate"):
        date_edit.setNullDate(null_date)
    if hasattr(date_edit, "setDisallowFuture"):
        date_edit.setDisallowFuture(True)


def configure_clearable_classic_date_edit(date_edit) -> QDate:
    """Make a QDateEdit show blank at minimum (Clear / empty read date).

    Qt ignores an empty specialValueText and would paint the raw minimum date
    (for example 1752-09-14). Returns the blank/minimum QDate to use in checks.
    """
    blank = QDate(CLASSIC_DATE_MINIMUM)
    date_edit.setMinimumDate(blank)
    date_edit.setSpecialValueText(CLASSIC_DATE_BLANK_TEXT)
    return blank


def set_classic_date_blank(date_edit) -> None:
    """Set a clearable classic date edit to its blank special value."""
    date_edit.setDate(date_edit.minimumDate())


def classic_date_is_blank(date_edit) -> bool:
    """True when a clearable classic date edit is on its blank special value."""
    return date_edit.date() == date_edit.minimumDate()


def year_spin_is_blank(spin) -> bool:
    return int(spin.value()) <= int(spin.minimum())


def validate_year_spin(spin, parent, *, restore_to=None) -> bool:
    """Validate publication year (masked or classic). False when invalid."""
    if hasattr(spin, "validated_year"):
        try:
            spin.validated_year()
            return True
        except ValueError:
            message = (
                spin.invalid_message()
                if hasattr(spin, "invalid_message")
                else year_invalid_message(
                    spin.text() if hasattr(spin, "text") else str(spin.value()),
                    min_year=preferred_year_range()[0],
                    max_year=preferred_year_range()[1],
                )
            )
            warn_masked_field_error(parent, message)
            spin.setFocus()
            return False

    if year_spin_is_blank(spin):
        return True
    min_year, max_year = preferred_year_range()
    value = int(spin.value())
    if min_year <= value <= max_year:
        return True
    warn_masked_field_error(
        parent,
        year_invalid_message(str(value), min_year=min_year, max_year=max_year),
    )
    if restore_to is not None:
        spin.setValue(restore_to if restore_to else spin.minimum())
    spin.setFocus()
    return False


def date_edit_display_text(date_edit) -> str:
    """Visible text from a QDateEdit or typed date field."""
    if hasattr(date_edit, "validated_date") and hasattr(date_edit, "text"):
        return date_edit.text()
    line = date_edit.lineEdit() if hasattr(date_edit, "lineEdit") else None
    if line is not None:
        return line.text()
    if hasattr(date_edit, "text"):
        return date_edit.text()
    return date_edit.date().toString(DATE_DISPLAY)


def _parsed_date_from_edit(
    date_edit,
    *,
    allow_blank: bool,
    null_date: Optional[QDate],
) -> Optional[date]:
    """Parse the field. Raises ValueError with reason 'blank'/'incomplete'/'invalid'/'future'."""
    if hasattr(date_edit, "validated_date"):
        # Masked field: keep its own blank/min rules, then apply future check here
        # only when validated_date does not already disallow future.
        return date_edit.validated_date()

    if null_date is not None and date_edit.date() == null_date:
        if allow_blank:
            return None
        raise ValueError("blank")

    text = date_edit_display_text(date_edit).strip()
    special = ""
    if hasattr(date_edit, "specialValueText"):
        special = (date_edit.specialValueText() or "").strip()
    if not text or text == special:
        if allow_blank:
            return None
        raise ValueError("blank")

    parsed = parse_iso_date_text(text)
    if parsed is None:
        if allow_blank:
            return None
        raise ValueError("blank")
    return parsed


def validate_date_edit(
    date_edit,
    parent,
    *,
    allow_blank: bool = True,
    null_date: Optional[QDate] = None,
    disallow_future: bool = True,
) -> bool:
    """Validate a typed or classic date field. False when invalid.

    Always enforces a real calendar date. When disallow_future is True (default),
    the date must be today or earlier.
    """
    text = date_edit_display_text(date_edit)
    try:
        parsed = _parsed_date_from_edit(
            date_edit, allow_blank=allow_blank, null_date=null_date
        )
    except ValueError as exc:
        reason = str(exc)
        if reason == "future":
            warn_masked_field_error(parent, date_future_message(text))
        elif hasattr(date_edit, "invalid_message"):
            warn_masked_field_error(parent, date_edit.invalid_message())
        else:
            warn_masked_field_error(
                parent, date_invalid_message(text, allow_blank=allow_blank)
            )
        date_edit.setFocus()
        return False

    if parsed is None:
        return True

    if disallow_future and parsed > today_date():
        warn_masked_field_error(parent, date_future_message(text))
        date_edit.setFocus()
        return False
    return True


class MaskedYearEdit(QLineEdit):
    """Four-digit year field. Blank means no year (same as spin minimum 0)."""

    valueChanged = Signal(int)
    altStepped = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._blank_value = 0
        self._valid_min, self._valid_max = preferred_year_range()
        self.setPlaceholderText(YEAR_PLACEHOLDER)
        self.setMaxLength(4)
        self.setMaximumWidth(110)
        self.setClearButtonEnabled(False)
        self.setAccessibleName("Publication year")
        self.setAccessibleDescription(
            f"Type a four digit year from {self._valid_min} to {self._valid_max}, "
            "or leave blank. Invalid values show a message when you leave the field or save."
        )
        self.editingFinished.connect(self._emit_value_changed)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        QTimer.singleShot(0, self._place_cursor_for_typing)

    def _place_cursor_for_typing(self) -> None:
        if not self.hasFocus():
            return
        self.deselect()
        self.setCursorPosition(0)

    def setRange(self, minimum: int, maximum: int) -> None:
        self._blank_value = int(minimum) if int(minimum) <= 0 else 0

    def setValidYearRange(self, minimum: int, maximum: int) -> None:
        self._valid_min = int(minimum)
        self._valid_max = int(maximum)
        self.setAccessibleDescription(
            f"Type a four digit year from {self._valid_min} to {self._valid_max}, "
            "or leave blank. Invalid values show a message when you leave the field or save."
        )

    def minimum(self) -> int:
        return self._blank_value

    def maximum(self) -> int:
        return self._valid_max

    def valid_year_range(self) -> Tuple[int, int]:
        return self._valid_min, self._valid_max

    def setSpecialValueText(self, _text: str) -> None:
        return

    def setButtonSymbols(self, _symbols) -> None:
        return

    def lineEdit(self):
        return self

    def setValue(self, value: int) -> None:
        if value is None or int(value) <= self._blank_value:
            self.setText("")
        else:
            self.setText(f"{int(value):04d}")
        if self.hasFocus():
            self.deselect()
            self.setCursorPosition(0)

    def value(self) -> int:
        try:
            parsed = parse_year_text(
                self.text(), min_year=self._valid_min, max_year=self._valid_max
            )
        except ValueError:
            return self._blank_value
        return self._blank_value if parsed is None else parsed

    def validated_year(self) -> Optional[int]:
        return parse_year_text(
            self.text(), min_year=self._valid_min, max_year=self._valid_max
        )

    def invalid_message(self) -> str:
        return year_invalid_message(
            self.text(), min_year=self._valid_min, max_year=self._valid_max
        )

    def _emit_value_changed(self) -> None:
        self.valueChanged.emit(self.value())


class MaskedDateEdit(QLineEdit):
    """ISO date field yyyy-MM-dd. Blank means no date when allowed."""

    dateChanged = Signal(QDate)
    altStepped = Signal()

    def __init__(self, parent=None, *, allow_blank: bool = True, disallow_future: bool = True):
        super().__init__(parent)
        self._allow_blank = allow_blank
        self._disallow_future = disallow_future
        self._minimum = QDate(1752, 9, 14)
        self._maximum = today_qdate() if disallow_future else QDate(9999, 12, 31)
        self._null_date = NULL_READ_QDATE
        self.setPlaceholderText(DATE_PLACEHOLDER)
        self.setMaxLength(10)
        self.setMaximumWidth(150)
        self.setAccessibleName("Date")
        self._refresh_accessible_description()
        self.editingFinished.connect(self._emit_date_changed)

    def _refresh_accessible_description(self) -> None:
        blank_note = "or leave blank. " if self._allow_blank else ""
        future_note = (
            "Must be today or earlier. "
            if self._disallow_future
            else ""
        )
        self.setAccessibleDescription(
            f"Type a date as year dash month dash day, {blank_note}{future_note}"
            "Invalid values show a message when you leave the field or confirm."
        )

    def focusInEvent(self, event):
        super().focusInEvent(event)
        QTimer.singleShot(0, self._place_cursor_for_typing)

    def _place_cursor_for_typing(self) -> None:
        if not self.hasFocus():
            return
        self.deselect()
        self.setCursorPosition(0)

    def setAllowBlank(self, allow: bool) -> None:
        self._allow_blank = bool(allow)
        self._refresh_accessible_description()

    def setDisallowFuture(self, disallow: bool) -> None:
        self._disallow_future = bool(disallow)
        if self._disallow_future:
            self._maximum = today_qdate()
        self._refresh_accessible_description()

    def setNullDate(self, qdate: QDate) -> None:
        self._null_date = QDate(qdate)

    def setCalendarPopup(self, _enabled: bool) -> None:
        return

    def setDisplayFormat(self, _fmt: str) -> None:
        return

    def setCalendarWidget(self, _widget) -> None:
        return

    def calendarWidget(self):
        return None

    def setMinimumDate(self, qdate: QDate) -> None:
        self._minimum = QDate(qdate)

    def minimumDate(self) -> QDate:
        return self._minimum

    def setMaximumDate(self, qdate: QDate) -> None:
        self._maximum = QDate(qdate)

    def maximumDate(self) -> QDate:
        return self._maximum

    def setSpecialValueText(self, _text: str) -> None:
        return

    def lineEdit(self):
        return self

    def setDate(self, qdate: QDate) -> None:
        if not qdate or not qdate.isValid() or qdate == self._null_date:
            self.setText("")
            if self.hasFocus():
                self.deselect()
                self.setCursorPosition(0)
            return
        self.setText(qdate.toString(DATE_DISPLAY))
        if self.hasFocus():
            self.deselect()
            self.setCursorPosition(0)

    def date(self) -> QDate:
        try:
            parsed = parse_iso_date_text(self.text())
        except ValueError:
            return self._null_date
        if parsed is None:
            return self._null_date
        return QDate(parsed.year, parsed.month, parsed.day)

    def validated_date(self) -> Optional[date]:
        """Parse the field. Raises ValueError when bad (including future)."""
        # Refresh "today" each check so midnight rollover stays correct.
        if self._disallow_future:
            self._maximum = today_qdate()
        parsed = parse_iso_date_text(self.text())
        if parsed is None:
            if self._allow_blank:
                return None
            raise ValueError("blank")
        qdate = QDate(parsed.year, parsed.month, parsed.day)
        if qdate < self._minimum:
            raise ValueError("invalid")
        if self._disallow_future and parsed > today_date():
            raise ValueError("future")
        if qdate > self._maximum:
            raise ValueError("future")
        return parsed

    def invalid_message(self) -> str:
        text = self.text()
        try:
            self.validated_date()
        except ValueError as exc:
            if str(exc) == "future":
                return date_future_message(text)
        return date_invalid_message(text, allow_blank=self._allow_blank)

    def _emit_date_changed(self) -> None:
        self.dateChanged.emit(self.date())


def make_year_field(parent=None):
    """Return a typed year field when a screen reader is active, else None."""
    if use_masked_date_fields():
        field = MaskedYearEdit(parent)
        min_year, max_year = preferred_year_range()
        field.setValidYearRange(min_year, max_year)
        return field
    return None


def make_date_field(
    parent=None, *, allow_blank: bool = True, disallow_future: bool = True
):
    """Return a typed date field when a screen reader is active, else None."""
    if use_masked_date_fields():
        return MaskedDateEdit(
            parent, allow_blank=allow_blank, disallow_future=disallow_future
        )
    return None
