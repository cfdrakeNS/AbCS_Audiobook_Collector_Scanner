"""HTML prose blocks for accessible About, License, and Setup dialogs."""

from __future__ import annotations

import html as html_module
import re

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontMetricsF
from PySide6.QtWidgets import QApplication, QFrame, QStyle, QTextEdit

from src.accessibility.read_only_text import configure_navigable_text_edit

DialogBlock = tuple[str, str]

_DIALOG_HTML_STYLESHEET = """
p.body { margin-top: 0.1em; margin-bottom: 0.1em; }
p.heading { font-weight: bold; margin-top: 0.35em; margin-bottom: 0.08em; }
p.item { margin-left: 1.25em; margin-top: 0.06em; margin-bottom: 0.06em; }
"""


def blocks_to_dialog_html(blocks: list[DialogBlock]) -> str:
    """Convert labeled prose blocks to HTML for screen-reader line review."""
    parts: list[str] = []
    for kind, text in blocks:
        cleaned = text.strip()
        if not cleaned:
            continue
        escaped = html_module.escape(cleaned)
        if kind == "heading":
            parts.append(f'<p class="heading"><strong>{escaped}</strong></p>')
        elif kind == "item":
            parts.append(f'<p class="item">{escaped}</p>')
        else:
            parts.append(f'<p class="body">{escaped}</p>')
    return "<html><body>\n" + "\n".join(parts) + "\n</body></html>"


def configure_dialog_html_text(
    widget: QTextEdit,
    blocks: list[DialogBlock],
    *,
    accessible_name: str,
    accessible_description: str,
    transparent_background: bool = True,
) -> QTextEdit:
    """Load dialog prose as HTML paragraphs for JAWS/NVDA line-by-line review."""
    widget.setReadOnly(True)
    widget.setFrameShape(QFrame.NoFrame)
    widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    widget.setAccessibleName(accessible_name)
    widget.setAccessibleDescription(accessible_description)
    if transparent_background:
        widget.setStyleSheet("QTextEdit { background: transparent; border: none; }")
    configure_navigable_text_edit(widget)
    # NoWrap is required. A wrapped paragraph is read twice: once for each
    # visual line, then again as the whole paragraph.
    widget.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
    widget.document().setDefaultStyleSheet(_DIALOG_HTML_STYLESHEET)
    widget.setHtml(blocks_to_dialog_html(blocks))
    return widget


def create_dialog_html_text(
    parent,
    blocks: list[DialogBlock],
    accessible_name: str,
    accessible_description: str,
    *,
    transparent_background: bool = True,
) -> QTextEdit:
    """Create a read-only QTextEdit with HTML dialog prose."""
    widget = QTextEdit(parent)
    return configure_dialog_html_text(
        widget,
        blocks,
        accessible_name=accessible_name,
        accessible_description=accessible_description,
        transparent_background=transparent_background,
    )


def _dialog_chrome(dialog, text_widget: QTextEdit) -> int:
    """Pixels outside the prose that the dialog width must still hold."""
    margins = dialog.layout().contentsMargins() if dialog.layout() else None
    chrome = (margins.left() + margins.right()) if margins else 0
    chrome += 2 * text_widget.frameWidth()
    chrome += text_widget.style().pixelMetric(QStyle.PixelMetric.PM_ScrollBarExtent)
    return chrome


def content_budget_for_dialog_width(dialog, text_widget: QTextEdit, dialog_width: int) -> float:
    """Widest paragraph that fits inside a dialog of dialog_width."""
    margin = text_widget.document().documentMargin()
    # fit_dialog_width_to_text uses text_width * 1.05 + chrome + 16.
    budget = (dialog_width - _dialog_chrome(dialog, text_widget) - 16) / 1.05 - 2 * margin
    return max(40.0, budget)


def line_width_budget(
    dialog,
    text_widget: QTextEdit,
    *,
    max_screen_fraction: float = 0.9,
) -> float:
    """Widest paragraph that still fits on this screen without wrapping."""
    screen = dialog.screen() or QApplication.primaryScreen()
    if screen is None:
        dialog_limit = 1100
    else:
        dialog_limit = int(screen.availableGeometry().width() * max_screen_fraction)
    return content_budget_for_dialog_width(dialog, text_widget, dialog_limit)


def _font_for_kind(base: QFont, kind: str) -> QFont:
    font = QFont(base)
    if kind == "heading":
        font.setBold(True)
    return font


def _extra_width(font: QFont, kind: str) -> float:
    """Indent that HTML adds on top of the measured words."""
    if kind != "item":
        return 0.0
    return QFontMetricsF(font).horizontalAdvance("M") * 1.25


def text_width(text: str, font: QFont) -> float:
    return QFontMetricsF(font).horizontalAdvance(text)


def split_text_to_width(text: str, font: QFont, max_width: float) -> list[str]:
    """Break text into pieces that each fit on one unwrapped line."""
    cleaned = " ".join(text.split())
    if not cleaned:
        return []
    if max_width <= 0 or text_width(cleaned, font) <= max_width:
        return [cleaned]
    for pattern in (r"(?<=[.!?])\s+", r"(?<=;)\s+", r"(?<=,)\s+"):
        parts = [part.strip() for part in re.split(pattern, cleaned) if part.strip()]
        if len(parts) > 1:
            return _pack_parts(parts, font, max_width)
    return _wrap_words(cleaned, font, max_width)


def _pack_parts(parts: list[str], font: QFont, max_width: float) -> list[str]:
    lines: list[str] = []
    current = ""
    for part in parts:
        if text_width(part, font) > max_width:
            if current:
                lines.append(current)
                current = ""
            lines.extend(split_text_to_width(part, font, max_width))
            continue
        candidate = f"{current} {part}".strip() if current else part
        if text_width(candidate, font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = part
    if current:
        lines.append(current)
    return lines


def _wrap_words(text: str, font: QFont, max_width: float) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip() if current else word
        if current and text_width(candidate, font) > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def split_blocks_to_width(
    blocks: list[DialogBlock],
    font: QFont,
    max_width: float,
) -> list[DialogBlock]:
    """Split any block that would wrap into blocks that fit."""
    fitted: list[DialogBlock] = []
    for kind, text in blocks:
        measure_font = _font_for_kind(font, kind)
        budget = max(40.0, max_width - _extra_width(measure_font, kind))
        for piece in split_text_to_width(text, measure_font, budget):
            fitted.append((kind, piece))
    return fitted


def _widest_line_px(text_widget: QTextEdit) -> float:
    doc = text_widget.document()
    widest = 0.0
    block = doc.begin()
    while block.isValid():
        fmt = block.blockFormat()
        line = fmt.leftMargin() + fmt.rightMargin() + fmt.textIndent()
        it = block.begin()
        while not it.atEnd():
            fragment = it.fragment()
            font = fragment.charFormat().font().resolve(doc.defaultFont())
            line += QFontMetricsF(font).horizontalAdvance(fragment.text())
            it += 1
        widest = max(widest, line)
        block = block.next()
    return widest


def fit_dialog_width_to_text(
    dialog,
    text_widget: QTextEdit,
    *,
    height: int,
    max_screen_fraction: float = 0.9,
) -> None:
    """Resize dialog so each paragraph in text_widget stays on one line.

    Call after the dialog layout is built and the prose font is set.
    """
    doc = text_widget.document()
    widest = 0.0
    block = doc.begin()
    while block.isValid():
        fmt = block.blockFormat()
        line = fmt.leftMargin() + fmt.rightMargin() + fmt.textIndent()
        it = block.begin()
        while not it.atEnd():
            fragment = it.fragment()
            font = fragment.charFormat().font().resolve(doc.defaultFont())
            line += QFontMetricsF(font).horizontalAdvance(fragment.text())
            it += 1
        widest = max(widest, line)
        block = block.next()
    text_width_px = widest + 2 * doc.documentMargin()
    width = int(text_width_px * 1.05) + _dialog_chrome(dialog, text_widget) + 16
    screen = dialog.screen() or QApplication.primaryScreen()
    if screen is not None:
        width = min(width, int(screen.availableGeometry().width() * max_screen_fraction))
    hint = dialog.minimumSizeHint().width()
    dialog.resize(max(width, hint, dialog.minimumWidth()), height)


def prepare_dialog_prose(
    dialog,
    text_widget: QTextEdit,
    blocks: list[DialogBlock],
    *,
    height: int,
    width_scale: float = 1.0,
) -> None:
    """Keep each paragraph on one line and size the dialog to match.

    ``width_scale`` sizes the dialog to that fraction of the width the text
    would otherwise take, then refits the lines so they still do not wrap.
    """
    font = text_widget.font()
    text_widget.document().setDefaultFont(font)
    fitted = split_blocks_to_width(blocks, font, line_width_budget(dialog, text_widget))
    text_widget.setHtml(blocks_to_dialog_html(fitted))
    text_widget.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
    fit_dialog_width_to_text(dialog, text_widget, height=height)
    if width_scale >= 0.999:
        return
    target = max(1, int(dialog.width() * width_scale))
    if target < dialog.minimumWidth():
        dialog.setMinimumWidth(target)
    # A vertical scrollbar shows once the dialog is open and narrows the text.
    scrollbar = text_widget.style().pixelMetric(QStyle.PixelMetric.PM_ScrollBarExtent)
    budget = content_budget_for_dialog_width(dialog, text_widget, target) - scrollbar
    fitted = split_blocks_to_width(blocks, font, max(40.0, budget))
    text_widget.setHtml(blocks_to_dialog_html(fitted))
    text_widget.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
    widest = _widest_line_px(text_widget)
    # A single word can be wider than the narrowed budget. Grow only for that.
    if widest > budget + 1:
        margin = text_widget.document().documentMargin()
        needed = int(widest + 2 * margin + _dialog_chrome(dialog, text_widget) + scrollbar + 24)
        target = max(target, needed)
        if target < dialog.minimumWidth():
            dialog.setMinimumWidth(target)
    dialog.resize(target, height)
