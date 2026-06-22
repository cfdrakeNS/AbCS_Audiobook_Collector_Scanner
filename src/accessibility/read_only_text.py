"""Read-only and navigable text areas for JAWS/NVDA arrow-key review."""

import re

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAccessible, QAccessibleEvent, QPalette
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QFrame,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QSizePolicy,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTextEdit,
)

_RATING_PREFIX_RE = re.compile(r"^(Rating:\s*.+?)\s*-\s*(.+)$", re.DOTALL)
_SENTENCE_END_RE = re.compile(r'[.!?]["\']?$')
_PLOT_LINE_WIDTH = 73
_ARROW_NAV_KEYS = frozenset(
    {
        Qt.Key_Up,
        Qt.Key_Down,
        Qt.Key_Left,
        Qt.Key_Right,
        Qt.Key_PageUp,
        Qt.Key_PageDown,
        Qt.Key_Home,
        Qt.Key_End,
    }
)


def _collapse_blank_lines(text: str) -> str:
    """Avoid Qt/JAWS repeating the previous line on empty lines."""
    normalized = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    return re.sub(r"\n\s*\n+", "\n", normalized)


def normalize_plot_text(text: str) -> str:
    """Normalize line endings and collapse extra blank lines."""
    text = (text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    return _collapse_blank_lines(text)


def restore_prose_line_breaks(text: str) -> str:
    """Rejoin sentence-per-line plot text saved by older formatting."""
    normalized = normalize_plot_text(text)
    if not normalized or "\n\n" in normalized:
        return normalized
    lines = [line.strip() for line in normalized.split("\n") if line.strip()]
    if len(lines) <= 1:
        return normalized

    rating_line = None
    if lines[0].startswith("Rating:"):
        rating_line = lines[0]
        body_lines = lines[1:]
    else:
        body_lines = lines

    if not body_lines:
        return rating_line or normalized

    if (
        len(body_lines) >= 3
        and all(_SENTENCE_END_RE.search(line) for line in body_lines)
    ):
        body = " ".join(body_lines)
        return f"{rating_line}\n{body}" if rating_line else body
    return normalized


def format_plot_text_for_navigation(text: str) -> str:
    """Prepare plot text for display without injecting sentence line breaks."""
    text = restore_prose_line_breaks(text)
    if not text:
        return ""

    rating_match = _RATING_PREFIX_RE.match(text)
    if rating_match:
        rating_line = rating_match.group(1).strip()
        body = normalize_plot_text(rating_match.group(2).strip())
        return f"{rating_line}\n{body}" if body else rating_line

    return text


def _wrap_at_words(text: str, width: int = _PLOT_LINE_WIDTH) -> list[str]:
    """Split text into lines of at most width characters without breaking words."""
    words = text.split()
    if not words:
        return []
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join(current + [word])
        if current and len(candidate) > width:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return lines


def _split_rating_and_body(prose: str) -> tuple[str | None, str]:
    rating_match = _RATING_PREFIX_RE.match(prose)
    if rating_match:
        return rating_match.group(1).strip(), rating_match.group(2).strip()
    if "\n" in prose:
        first_line, _, remainder = prose.partition("\n")
        if first_line.startswith("Rating:"):
            return first_line.strip(), remainder.strip()
    return None, prose


def plot_lines_for_review(text: str) -> list[str]:
    """Rating in item 0; plot body split into 73-character word-wrapped lines."""
    prose = format_plot_text_for_navigation(text)
    if not prose:
        return []

    rating_line, body = _split_rating_and_body(prose)
    lines: list[str] = []
    if rating_line:
        lines.append(rating_line)
    if body:
        body_flat = re.sub(r"\s+", " ", body.strip())
        lines.extend(_wrap_at_words(body_flat))
    return lines


def plot_text_equivalent(left: str, right: str) -> bool:
    """Compare plot text ignoring line-break and whitespace differences."""
    def _normalize(value: str) -> str:
        return re.sub(r"\s+", " ", (value or "").strip())

    return _normalize(left) == _normalize(right)


def set_navigable_plain_text(widget: QTextEdit | QPlainTextEdit, text: str) -> None:
    """Load text into a navigable text area with logical line breaks."""
    widget.setPlainText(format_plot_text_for_navigation(text))


def _announce_text_caret_moved(widget: QTextEdit | QPlainTextEdit) -> None:
    QAccessible.updateAccessibility(
        QAccessibleEvent(widget, QAccessible.Event.TextCaretMoved)
    )


class _CompactPlotLineDelegate(QStyledItemDelegate):
    """Paint single-line plot rows with no extra vertical gap between items."""

    _H_MARGIN = 4

    def paint(self, painter, option, index):
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        text = index.data(Qt.ItemDataRole.DisplayRole) or ""
        widget = opt.widget
        style = widget.style() if widget else QApplication.style()
        opt.text = ""
        style.drawPrimitive(QStyle.PrimitiveElement.PE_PanelItemViewItem, opt, painter, widget)
        painter.setPen(opt.palette.color(QPalette.ColorRole.Text))
        rect = opt.rect.adjusted(self._H_MARGIN, 0, -self._H_MARGIN, 0)
        painter.drawText(
            rect,
            int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
            text,
        )

    def sizeHint(self, option, index):
        del index
        return QSize(0, option.fontMetrics.height())


class PlotLineList(QListWidget):
    """One plot line per row for reliable JAWS/NVDA Up/Down review."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._plot_title = "Plot"
        self.setFocusPolicy(Qt.StrongFocus)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setTabKeyNavigation(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setSpacing(0)
        self.setUniformItemSizes(True)
        self.setItemDelegate(_CompactPlotLineDelegate(self))
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMouseTracking(False)
        self.viewport().setMouseTracking(False)
        self.setAttribute(Qt.WA_Hover, False)
        self.viewport().setAttribute(Qt.WA_Hover, False)
        self.setAccessibleDescription("")
        self.setStyleSheet(
            "QListWidget { border: 1px solid palette(mid); background: palette(base);"
            " outline: none; show-decoration-selected: 0; }"
            "QListWidget::item { padding: 0px; margin: 0px; border: none;"
            " background: palette(base); color: palette(text); }"
            "QListWidget::item:selected, QListWidget::item:focus {"
            " background: palette(base); color: palette(text); border: none; outline: none; }"
        )

    def setAccessibleName(self, name: str):
        self._plot_title = name
        super().setAccessibleName(name)

    def setAccessibleDescription(self, description: str):
        super().setAccessibleDescription("")

    def set_plot_text(self, text: str) -> None:
        self.clear()
        for line in plot_lines_for_review(text):
            item = QListWidgetItem(line)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            item.setData(Qt.ItemDataRole.AccessibleTextRole, line)
            self.addItem(item)
        if self.count():
            self.setCurrentRow(0)
        self._resize_to_content()

    def _resize_to_content(self, *, min_visible_rows: int = 4, max_visible_rows: int = 10) -> None:
        count = self.count()
        if count == 0:
            return
        frame = self.frameWidth() * 2
        default_row = self.fontMetrics().height()
        rows_to_show = min(max(count, min_visible_rows), max_visible_rows)
        total_height = 0
        for i in range(min(count, rows_to_show)):
            row_h = self.sizeHintForRow(i)
            total_height += row_h if row_h > 0 else default_row
        if count < min_visible_rows:
            total_height += default_row * (min_visible_rows - count)
        ideal_height = total_height + frame
        max_allowed = self.maximumHeight()
        has_cap = 0 < max_allowed < 16777215
        if has_cap:
            self.setMinimumHeight(min(ideal_height, max_allowed))
        else:
            self.setMinimumHeight(ideal_height)
            self.setMaximumHeight(ideal_height)

    def plot_text(self) -> str:
        return "\n".join(self.item(index).text() for index in range(self.count()))


class NavigablePlainTextEdit(QPlainTextEdit):
    """Plain-text plot field tuned for JAWS/NVDA line-by-line arrow review."""

    def __init__(self, parent=None):
        super().__init__(parent)
        configure_navigable_text_edit(self)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() in _ARROW_NAV_KEYS and not (event.modifiers() & Qt.ShiftModifier):
            _announce_text_caret_moved(self)


def configure_accessible_read_only_text(
    widget: QTextEdit,
    *,
    text: str,
    accessible_name: str,
    accessible_description: str,
    transparent_background: bool = True,
) -> QTextEdit:
    """Apply screen-reader-friendly settings for read-only navigable text."""
    widget.setReadOnly(True)
    widget.setPlainText(text)
    widget.setFrameShape(QFrame.NoFrame)
    widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    widget.setFocusPolicy(Qt.StrongFocus)
    widget.setTabChangesFocus(True)
    widget.setTextInteractionFlags(Qt.TextSelectableByKeyboard)
    widget.setMouseTracking(False)
    widget.viewport().setMouseTracking(False)
    widget.viewport().setAttribute(Qt.WA_Hover, False)
    widget.setAccessibleName(accessible_name)
    widget.setAccessibleDescription(accessible_description)
    if transparent_background:
        widget.setStyleSheet("QTextEdit { background: transparent; border: none; }")
    return widget


def create_accessible_read_only_text(
    parent,
    text: str,
    accessible_name: str,
    accessible_description: str,
    *,
    transparent_background: bool = True,
) -> QTextEdit:
    widget = QTextEdit(parent)
    return configure_accessible_read_only_text(
        widget,
        text=_collapse_blank_lines(text),
        accessible_name=accessible_name,
        accessible_description=accessible_description,
        transparent_background=transparent_background,
    )


def configure_navigable_text_edit(widget: QTextEdit | QPlainTextEdit) -> QTextEdit | QPlainTextEdit:
    """Enable arrow-key line review on editable or read-only text fields."""
    widget.setFocusPolicy(Qt.StrongFocus)
    widget.setTabChangesFocus(True)
    widget.setTextInteractionFlags(Qt.TextSelectableByKeyboard)
    widget.setMouseTracking(False)
    widget.viewport().setMouseTracking(False)
    widget.viewport().setAttribute(Qt.WA_Hover, False)
    if isinstance(widget, QPlainTextEdit):
        widget.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
    elif isinstance(widget, QTextEdit):
        widget.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
    return widget
