"""HTML prose blocks for accessible About, License, and Setup dialogs."""

from __future__ import annotations

import html as html_module

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QTextEdit

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
    widget.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
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
