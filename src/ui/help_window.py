"""Accessible help viewer using read-only rich text and markdown help files."""

from __future__ import annotations

import html
import re
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAccessible, QAccessibleEvent, QKeySequence, QShortcut, QTextCursor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
)

from src.accessibility.accessible_events import (
    configure_status_bar_accessibility,
    read_status_bar_message,
)
from src.accessibility.help_paths import resolve_help_doc_path
from src.accessibility.read_only_text import (
    configure_navigable_text_edit,
    create_accessible_read_only_text,
)
from src.accessibility.scaling import UIScaler
from src.accessibility.style_helpers import build_modern_button_style
from src.ui.accessible_dialog import AccessibleDialog
from src.accessibility.help_paths import HELP_TOPICS

_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_HEADER_RE = re.compile(r"^(#{1,6})\s+(.+)$")
_ORDERED_LIST_RE = re.compile(r"^\d+\.\s+")
_FAQ_QUESTION_RE = re.compile(r"^\*\*(.+)\*\*$")
_TABLE_DIVIDER_RE = re.compile(r"^[\s|:-]+$")
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'])")

_HELP_DOCUMENT_STYLESHEET = """
p.body { margin-left: 1.25em; margin-top: 0.08em; margin-bottom: 0.08em; }
p.step { margin-left: 1.5em; margin-top: 0.08em; margin-bottom: 0.08em; }
p.faq-q { margin-left: 1.5em; margin-top: 0.15em; margin-bottom: 0.05em; font-weight: bold; }
p.faq-a { margin-left: 2em; margin-top: 0.05em; margin-bottom: 0.08em; }
p.shortcut { margin-left: 1.5em; margin-top: 0.05em; margin-bottom: 0.05em; }
p.table-row { margin-left: 1.25em; margin-top: 0.05em; margin-bottom: 0.05em; }
p.heading1 { font-weight: bold; font-size: 115%; margin-top: 0.45em; margin-bottom: 0.12em; }
p.heading2 { font-weight: bold; font-size: 108%; margin-top: 0.4em; margin-bottom: 0.1em; }
p.heading3 { font-weight: bold; margin-top: 0.35em; margin-bottom: 0.08em; margin-left: 0.5em; }
ul { margin-top: 0.1em; margin-bottom: 0.12em; margin-left: 1.25em; padding-left: 1.1em; }
li { margin-top: 0.05em; margin-bottom: 0.05em; }
"""


def _title_from_markdown(text: str) -> str:
    for line in text.splitlines():
        match = _HEADER_RE.match(line.strip())
        if match:
            return match.group(2).strip()
    return "AbCS Help"


def _inline_markdown_to_html(text: str) -> str:
    """Convert inline markdown emphasis to HTML."""
    parts = re.split(r"\*\*([^*]+)\*\*", text)
    chunks: list[str] = []
    for index, part in enumerate(parts):
        escaped = html.escape(part)
        if index % 2 == 1:
            chunks.append(f"<strong>{escaped}</strong>")
        else:
            chunks.append(escaped)
    return "".join(chunks)


def _collect_links(markdown: str) -> list[tuple[str, str]]:
    links: list[tuple[str, str]] = []
    seen: set[str] = set()
    for label, target in _LINK_RE.findall(markdown):
        filename = Path(target.strip()).name
        if filename.endswith(".md") and filename not in seen:
            links.append((label.strip(), filename))
            seen.add(filename)
    return links


def _strip_links_to_labels(text: str) -> str:
    return _LINK_RE.sub(lambda match: match.group(1).strip(), text)


def _is_shortcut_table_header(cells: list[str]) -> bool:
    return (
        len(cells) >= 2
        and cells[0].strip().lower() == "shortcut"
        and cells[1].strip().lower() == "action"
    )


def _append_table_row_paragraph(
    body_parts: list[str], cells: list[str], table_mode: str
) -> None:
    """Render markdown table rows as plain paragraphs for screen-reader review."""
    if table_mode == "shortcut" and len(cells) >= 2:
        row_text = (
            f"{_inline_markdown_to_html(cells[0])} — "
            f"{_inline_markdown_to_html(cells[1])}"
        )
        body_parts.append(f'<p class="shortcut">{row_text}</p>')
        return
    row_text = " — ".join(_inline_markdown_to_html(cell) for cell in cells)
    body_parts.append(f'<p class="table-row">{row_text}</p>')


def _split_sentences(text: str) -> list[str]:
    """Split prose into sentence-sized blocks for screen-reader line review."""
    cleaned = text.strip()
    if not cleaned:
        return []
    if _ORDERED_LIST_RE.match(cleaned):
        return [cleaned]
    parts = [part.strip() for part in _SENTENCE_SPLIT_RE.split(cleaned) if part.strip()]
    return parts or [cleaned]


def _append_faq_answer_paragraphs(body_parts: list[str], text: str) -> None:
    for sentence in _split_sentences(text):
        body_parts.append(f'<p class="faq-a">{_inline_markdown_to_html(sentence)}</p>')


def _append_body_paragraphs(body_parts: list[str], text: str) -> None:
    """Emit one HTML paragraph per sentence to avoid wrapped-line repeat in JAWS."""
    for sentence in _split_sentences(text):
        body_parts.append(f'<p class="body">{_inline_markdown_to_html(sentence)}</p>')


def markdown_to_html(markdown: str) -> tuple[str, list[tuple[str, str]]]:
    """Convert markdown help to HTML with visual spacing and no empty lines."""
    links = _collect_links(markdown)
    body_parts: list[str] = []
    in_ul = False
    table_mode: str | None = None
    step_counter = 0
    after_faq_question = False

    def reset_step_counter() -> None:
        nonlocal step_counter
        step_counter = 0

    def next_step_number() -> int:
        nonlocal step_counter
        step_counter += 1
        return step_counter

    def close_lists() -> None:
        nonlocal in_ul
        if in_ul:
            body_parts.append("</ul>")
            in_ul = False

    def close_table_block() -> None:
        nonlocal table_mode
        table_mode = None

    for raw_line in markdown.replace("\r\n", "\n").split("\n"):
        line = _strip_links_to_labels(raw_line).rstrip()

        if not line.strip():
            close_lists()
            close_table_block()
            continue

        faq_match = _FAQ_QUESTION_RE.match(line.strip())
        if faq_match:
            close_lists()
            close_table_block()
            after_faq_question = True
            question = html.escape(faq_match.group(1).strip())
            body_parts.append(f'<p class="faq-q"><strong>{question}</strong></p>')
            continue

        if line.strip().startswith("|") and line.strip().endswith("|"):
            after_faq_question = False
            close_lists()
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if _TABLE_DIVIDER_RE.match("".join(cells)):
                continue
            if table_mode is None:
                if _is_shortcut_table_header(cells):
                    table_mode = "shortcut"
                else:
                    table_mode = "generic"
                continue
            _append_table_row_paragraph(body_parts, cells, table_mode)
            continue

        header_match = _HEADER_RE.match(line.strip())
        if header_match:
            close_lists()
            close_table_block()
            after_faq_question = False
            reset_step_counter()
            level = min(len(header_match.group(1)), 3)
            title = header_match.group(2).strip()
            body_parts.append(
                f'<p class="heading{level}"><strong>{html.escape(title)}</strong></p>'
            )
            continue

        if line.lstrip().startswith("- "):
            after_faq_question = False
            close_table_block()
            if not in_ul:
                body_parts.append("<ul>")
                in_ul = True
            item_text = line.lstrip()[2:].strip()
            body_parts.append(f"<li>{_inline_markdown_to_html(item_text)}</li>")
            continue

        ordered_match = _ORDERED_LIST_RE.match(line.strip())
        if ordered_match:
            after_faq_question = False
            close_lists()
            close_table_block()
            item_text = line.strip()[ordered_match.end() :].strip()
            body_parts.append(
                f'<p class="step">{next_step_number()}. '
                f"{_inline_markdown_to_html(item_text)}</p>"
            )
            continue

        close_lists()
        close_table_block()
        if after_faq_question:
            _append_faq_answer_paragraphs(body_parts, line)
        else:
            _append_body_paragraphs(body_parts, line)

    close_lists()
    close_table_block()
    document = "<html><body>\n" + "\n".join(body_parts) + "\n</body></html>"
    return document, links


def markdown_to_plain_text(markdown: str) -> tuple[str, list[tuple[str, str]]]:
    """Plain-text fallback used by tests and simple previews."""
    html_doc, links = markdown_to_html(markdown)
    plain = re.sub(r"<[^>]+>", "", html_doc)
    plain = html.unescape(plain)
    plain = re.sub(r"\n{3,}", "\n\n", plain).strip()
    return plain, links


def _announce_help_text_loaded(widget) -> None:
    QAccessible.updateAccessibility(
        QAccessibleEvent(widget, QAccessible.Event.TextCaretMoved)
    )


class HelpWindow(AccessibleDialog):
    """Display help topics as accessible read-only text."""

    def __init__(self, scaler, parent=None, doc_filename: str = "01_overview.md"):
        super().__init__(parent)
        self.scaler = scaler or UIScaler()
        self._current_filename = Path(doc_filename).name
        self._current_title = "AbCS Help"
        self._syncing_combo = False

        self.setWindowTitle("AbCS Help")
        self.setAccessibleName("AbCS Help")
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(self.scaler.get_scaled_size(780))
        self.setMinimumHeight(self.scaler.get_scaled_size(560))
        self.resize(
            self.scaler.get_scaled_size(820),
            self.scaler.get_scaled_size(620),
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            self.scaler.get_scaled_size(16),
            self.scaler.get_scaled_size(12),
            self.scaler.get_scaled_size(16),
            self.scaler.get_scaled_size(12),
        )
        layout.setSpacing(self.scaler.get_scaled_size(8))

        topic_row = QHBoxLayout()
        topic_row.setSpacing(self.scaler.get_scaled_size(8))

        self.topic_label = QLabel("Help &Topic:")
        self.topic_label.setAccessibleName("Help Topic")
        topic_row.addWidget(self.topic_label)

        self.topic_combo = QComboBox(self)
        self.topic_combo.setAccessibleName("Help Topic")
        self.topic_combo.setAccessibleDescription(
            "Choose a help topic. Same list as the main window Help menu."
        )
        for label, _filename in HELP_TOPICS:
            self.topic_combo.addItem(label)
        self.topic_label.setBuddy(self.topic_combo)
        self.topic_combo.currentIndexChanged.connect(self._on_topic_changed)
        topic_row.addWidget(self.topic_combo, stretch=1)
        layout.addLayout(topic_row)

        self.help_text = create_accessible_read_only_text(
            self,
            "",
            "Help content",
            "Help document text. Use arrow keys to read line by line.",
            transparent_background=False,
        )
        font = self.help_text.font()
        font.setPointSize(self.scaler.get_scaled_size(12))
        self.help_text.setFont(font)
        configure_navigable_text_edit(self.help_text)
        self.help_text.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.help_text.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.help_text.document().setDefaultStyleSheet(_HELP_DOCUMENT_STYLESHEET)
        layout.addWidget(self.help_text, stretch=1)

        self.related_label = QLabel("Related topics")
        self.related_label.setAccessibleName("Related topics")
        self.related_label.setFocusPolicy(Qt.NoFocus)
        layout.addWidget(self.related_label)

        self.related_list = QListWidget(self)
        self.related_list.setAccessibleName("Related help topics")
        self.related_list.setAccessibleDescription(
            "List of related help topics. Press Enter to open the selected topic."
        )
        self.related_list.itemActivated.connect(self._on_related_topic_activated)
        self.related_list.setMaximumHeight(self.scaler.get_scaled_size(120))
        layout.addWidget(self.related_list)

        close_row = QHBoxLayout()
        close_row.addStretch()
        button_height = self.scaler.get_scaled_size(28)
        button_style = build_modern_button_style(button_height)
        self.close_button = QPushButton("Close")
        self.close_button.setAccessibleName("Close")
        self.close_button.setAccessibleDescription("Close help window")
        self.close_button.setDefault(True)
        self.close_button.clicked.connect(self.accept)
        self.close_button.setStyleSheet(button_style)
        close_row.addWidget(self.close_button)
        layout.addLayout(close_row)

        self.status_bar = QStatusBar()
        configure_status_bar_accessibility(self.status_bar)
        layout.addWidget(self.status_bar)

        escape_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        escape_shortcut.activated.connect(self.reject)

        self.status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.status_shortcut.activated.connect(self.on_read_status)

        self.help_shortcut = QShortcut(QKeySequence("F1"), self)
        self.help_shortcut.activated.connect(self.on_show_shortcuts)

        self.topic_shortcut = QShortcut(QKeySequence("Alt+H"), self)
        self.topic_shortcut.activated.connect(
            lambda: self.topic_combo.setFocus(Qt.ShortcutFocusReason)
        )

        self._load_doc(self._current_filename)
        QTimer.singleShot(100, self._focus_help_text)

    def _focus_help_text(self) -> None:
        if self.isVisible():
            self.help_text.setFocus(Qt.TabFocusReason)
            _announce_help_text_loaded(self.help_text)

    def _sync_topic_combo(self, filename: str) -> None:
        self._syncing_combo = True
        try:
            for index, (_label, doc_name) in enumerate(HELP_TOPICS):
                if doc_name == filename:
                    self.topic_combo.setCurrentIndex(index)
                    break
        finally:
            self._syncing_combo = False

    def _on_topic_changed(self, index: int) -> None:
        if self._syncing_combo or index < 0:
            return
        _label, filename = HELP_TOPICS[index]
        if filename != self._current_filename:
            self._load_doc(filename)

    def _load_doc(self, filename: str) -> None:
        path = resolve_help_doc_path(filename)
        if not path.is_file():
            self._current_filename = filename
            self._current_title = "Help not found"
            missing_text = (
                "<html><body>"
                "<p class='heading1'><strong>Help not found</strong></p>"
                f"<p class='body'>The help file {html.escape(Path(filename).name)} "
                "could not be loaded.</p>"
                "</body></html>"
            )
            self._set_help_body(missing_text, [])
            self._sync_topic_combo(filename)
            self._apply_window_title()
            self.status_bar.showMessage(f"Help file not found: {Path(filename).name}")
            return

        markdown = path.read_text(encoding="utf-8")
        html_doc, links = markdown_to_html(markdown)
        self._current_filename = path.name
        self._current_title = _title_from_markdown(markdown)
        self._set_help_body(html_doc, links)
        self._sync_topic_combo(self._current_filename)
        self._apply_window_title()
        self.status_bar.showMessage(f"Showing help: {self._current_title}")
        QTimer.singleShot(100, self._focus_help_text)

    def _set_help_body(self, html_doc: str, links: list[tuple[str, str]]) -> None:
        self.help_text.setHtml(html_doc)
        cursor = self.help_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.help_text.setTextCursor(cursor)
        self.help_text.setAccessibleName(self._current_title)
        self.help_text.setAccessibleDescription(
            f"Help topic: {self._current_title}. "
            "Use arrow keys to move line by line. Each sentence is its own paragraph."
        )

        self.related_list.clear()
        has_links = bool(links)
        self.related_label.setVisible(has_links)
        self.related_list.setVisible(has_links)
        for label, filename in links:
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, filename)
            self.related_list.addItem(item)

    def _apply_window_title(self) -> None:
        title = f"AbCS Help - {self._current_title}"
        self.setWindowTitle(title)
        self.setAccessibleName(title)

    def _on_related_topic_activated(self, item: QListWidgetItem) -> None:
        filename = item.data(Qt.UserRole)
        if filename:
            self._load_doc(str(filename))

    def on_read_status(self) -> None:
        read_status_bar_message(
            self.status_bar,
            fallback=f"Showing help: {self._current_title}",
        )

    def on_show_shortcuts(self) -> None:
        """Show keyboard shortcuts for the help window."""
        from src.accessibility.shortcut_helpers import (
            build_accessible_f1_popup_style,
            get_accessible_shortcuts_list,
        )

        shortcuts = get_accessible_shortcuts_list(
            [
                ("Shift+F1", "Open help for current window"),
                ("Alt+H", "Help Topics combo"),
                ("Arrow keys", "Read line by line"),
                ("Alt+/", "Re-read status"),
                ("F1", "Show these shortcuts"),
                ("Escape", "Close help"),
            ]
        )

        dlg = AccessibleDialog(self)
        dlg.setWindowTitle("Keyboard Shortcuts - Help")
        dlg.setAccessibleName("Keyboard Shortcuts")
        dlg.resize(480, 320)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        table = QTableWidget()
        table.setAccessibleName("Shortcuts list")
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels([""])
        table.setRowCount(len(shortcuts))
        table.setVerticalHeaderLabels([""] * len(shortcuts))
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectItems)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setTabKeyNavigation(False)
        table.setAlternatingRowColors(False)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setMouseTracking(False)
        table.viewport().setMouseTracking(False)
        table.setAttribute(Qt.WA_Hover, False)
        table.viewport().setAttribute(Qt.WA_Hover, False)
        table.setStyleSheet(build_accessible_f1_popup_style())

        for row, (key, desc) in enumerate(shortcuts):
            item = QTableWidgetItem(f"{desc} - {key}")
            item.setData(Qt.AccessibleTextRole, f"{desc}: {key}")
            table.setItem(row, 0, item)

        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        font = table.font()
        font.setPointSize(self.scaler.get_scaled_size(11))
        table.setFont(font)
        layout.addWidget(table)
        dlg.exec()
