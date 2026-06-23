"""Accessible help viewer using read-only rich text and markdown help files.

HelpWindow shows a side-by-side layout: Help Navigation list (topics or section
headings) and a read-only QTextEdit for content. Topic names come from
``discover_help_topics()`` in ``help_paths`` (dynamic scan of ``help_docs/``).
After a topic loads, the list switches to section mode (h2/h3 headings plus
**All Help Topics** to return to the full topic list).

Opening help: ``help_router.show_help_doc()`` / ``show_context_help()`` (Shift+F1).
Markdown is converted to accessible HTML (sentence-per-paragraph, named anchors
on section headings for in-doc jumps).

Do not hard-code topic lists here — add ``help_docs/nn_name.md`` files instead.
Update ``help_router.WINDOW_HELP_MAP`` only when a new window needs Shift+F1 routing.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

from PySide6.QtCore import QEvent, QObject, Qt, QTimer
from PySide6.QtGui import QAccessible, QAccessibleEvent, QKeySequence, QShortcut, QTextCursor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
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
from src.accessibility.help_paths import discover_help_topics, resolve_help_doc_path
from src.accessibility.read_only_text import (
    configure_navigable_text_edit,
    create_accessible_read_only_text,
)
from src.accessibility.scaling import UIScaler
from src.accessibility.style_helpers import build_modern_button_style
from src.ui.accessible_dialog import AccessibleDialog

_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_HEADER_RE = re.compile(r"^(#{1,6})\s+(.+)$")
_ORDERED_LIST_RE = re.compile(r"^\d+\.\s+")
_FAQ_QUESTION_RE = re.compile(r"^\*\*(.+)\*\*$")
_TABLE_DIVIDER_RE = re.compile(r"^[\s|:-]+$")
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'])")

_NAV_ROLE_TYPE = Qt.ItemDataRole.UserRole
_NAV_ROLE_FILENAME = Qt.ItemDataRole.UserRole + 1
_NAV_ROLE_ANCHOR = Qt.ItemDataRole.UserRole + 2

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


def extract_headings(markdown: str) -> list[tuple[str, str, int]]:
    """Return h2/h3 headings as (title, anchor_id, level)."""
    headings: list[tuple[str, str, int]] = []
    anchor_index = 0
    for raw_line in markdown.replace("\r\n", "\n").split("\n"):
        match = _HEADER_RE.match(raw_line.strip())
        if not match:
            continue
        level = len(match.group(1))
        if level < 2:
            continue
        title = match.group(2).strip()
        anchor_id = f"h{anchor_index}"
        headings.append((title, anchor_id, level))
        anchor_index += 1
    return headings


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
    heading_anchor_index = 0

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
            raw_level = len(header_match.group(1))
            level = min(raw_level, 3)
            title = header_match.group(2).strip()
            anchor_open = ""
            anchor_close = ""
            if raw_level >= 2:
                anchor_open = f'<a name="h{heading_anchor_index}">'
                anchor_close = "</a>"
                heading_anchor_index += 1
            body_parts.append(
                f'<p class="heading{level}">{anchor_open}'
                f"<strong>{html.escape(title)}</strong>{anchor_close}</p>"
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


def _cursor_at_html_anchor(document, anchor_id: str) -> QTextCursor | None:
    """Return a cursor at a named HTML anchor, if present in the document."""
    block = document.firstBlock()
    while block.isValid():
        fragment_it = block.begin()
        while fragment_it != block.end():
            fragment = fragment_it.fragment()
            if fragment.isValid():
                char_format = fragment.charFormat()
                if char_format.isAnchor() and anchor_id in char_format.anchorNames():
                    cursor = QTextCursor(document)
                    cursor.setPosition(fragment.position())
                    return cursor
            fragment_it += 1
        block = block.next()
    return None


def _cursor_at_heading_title(document, title: str) -> QTextCursor | None:
    """Fallback: find the first block that matches a section heading title."""
    cursor = document.find(title)
    if cursor.isNull():
        return None
    return cursor


class _HelpNavFocusFilter(QObject):
    """Cycle Tab focus between the nav list and help content; handle Enter on nav."""

    def __init__(
        self,
        nav_list: QListWidget,
        help_text: QTextEdit,
        on_nav_activate,
    ) -> None:
        super().__init__(nav_list)
        self.nav_list = nav_list
        self.help_text = help_text
        self.on_nav_activate = on_nav_activate

    def eventFilter(self, obj, event) -> bool:
        if event.type() == QEvent.Type.KeyPress:
            if obj is self.nav_list and event.key() in (
                Qt.Key.Key_Return,
                Qt.Key.Key_Enter,
            ):
                current = self.nav_list.currentItem()
                if current is not None:
                    self.on_nav_activate(current)
                    return True
            if event.key() in (Qt.Key.Key_Tab, Qt.Key.Key_Backtab):
                if obj is self.nav_list:
                    self.help_text.setFocus(Qt.FocusReason.TabFocusReason)
                    return True
                if obj is self.help_text:
                    self.nav_list.setFocus(Qt.FocusReason.TabFocusReason)
                    return True
        return super().eventFilter(obj, event)


class HelpWindow(AccessibleDialog):
    """Display help topics as accessible read-only text."""

    def __init__(self, scaler, parent=None, doc_filename: str = "01_overview.md"):
        super().__init__(parent)
        self.scaler = scaler or UIScaler()
        self._current_filename = Path(doc_filename).name
        self._current_title = "AbCS Help"
        self._nav_mode = "headings"

        self.setWindowTitle("AbCS Help")
        self.setAccessibleName("AbCS Help")
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
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

        splitter = QSplitter(Qt.Orientation.Horizontal, self)

        self.nav_list = QListWidget(splitter)
        self.nav_list.setAccessibleName("Help Navigation")
        self.nav_list.setAccessibleDescription(
            "Help section list. Press Enter to jump to a section. "
            "Use Tab to move to the help content."
        )
        self.nav_list.setMinimumWidth(self.scaler.get_scaled_size(220))
        self.nav_list.itemActivated.connect(self._on_nav_item_activated)
        splitter.addWidget(self.nav_list)

        self.help_text = create_accessible_read_only_text(
            splitter,
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
        splitter.addWidget(self.help_text)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter, stretch=1)

        self._nav_focus_filter = _HelpNavFocusFilter(
            self.nav_list, self.help_text, self._on_nav_item_activated
        )
        self.nav_list.installEventFilter(self._nav_focus_filter)
        self.help_text.installEventFilter(self._nav_focus_filter)

        close_row = QHBoxLayout()
        close_row.addStretch()
        button_height = self.scaler.get_scaled_size(28)
        button_style = build_modern_button_style(button_height)
        self.close_button = QPushButton("Close")
        self.close_button.setAccessibleName("Close")
        self.close_button.setAccessibleDescription("Close help window")
        self.close_button.clicked.connect(self.accept)
        self.close_button.setStyleSheet(button_style)
        close_row.addWidget(self.close_button)
        layout.addLayout(close_row)

        self.status_bar = QStatusBar()
        configure_status_bar_accessibility(self.status_bar)
        layout.addWidget(self.status_bar)

        escape_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        escape_shortcut.activated.connect(self.reject)

        self.status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.status_shortcut.activated.connect(self.on_read_status)

        self.help_shortcut = QShortcut(QKeySequence("F1"), self)
        self.help_shortcut.activated.connect(self.on_show_shortcuts)

        self.nav_focus_shortcut = QShortcut(QKeySequence("Alt+L"), self)
        self.nav_focus_shortcut.activated.connect(self._focus_nav_list)

        self.setTabOrder(self.nav_list, self.help_text)
        self.setTabOrder(self.help_text, self.close_button)

        self._load_doc(self._current_filename)
        QTimer.singleShot(0, lambda: self._focus_help_text(at_start=True))

    def _focus_nav_list(self) -> None:
        self.nav_list.setFocus(Qt.FocusReason.ShortcutFocusReason)

    def _focus_help_text(self, *, at_start: bool = False) -> None:
        if not self.isVisible():
            return
        if at_start:
            cursor = self.help_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.help_text.setTextCursor(cursor)
        self.help_text.setFocus(Qt.FocusReason.TabFocusReason)
        self.help_text.ensureCursorVisible()
        _announce_help_text_loaded(self.help_text)

    def _jump_to_anchor(self, anchor_id: str, title: str) -> None:
        document = self.help_text.document()
        cursor = _cursor_at_html_anchor(document, anchor_id)
        if cursor is None:
            cursor = _cursor_at_heading_title(document, title)
        if cursor is not None:
            self.help_text.setTextCursor(cursor)
        else:
            self.help_text.scrollToAnchor(anchor_id)
        self._focus_help_text()

    def _set_nav_description(self) -> None:
        if self._nav_mode == "topics":
            self.nav_list.setAccessibleDescription(
                "Help topic list. Press Enter to open a topic. "
                "Press Alt+L to focus this list. Use Tab to move to the help content."
            )
            return
        self.nav_list.setAccessibleDescription(
            "Help section list. Press Enter to jump to a section. "
            "Choose All Help Topics to return to the topic list. "
            "Press Alt+L to focus this list. Use Tab to move to the help content."
        )

    def _show_topics_list(self) -> None:
        self._nav_mode = "topics"
        self.nav_list.clear()
        for label, filename in discover_help_topics():
            item = QListWidgetItem(label)
            item.setData(_NAV_ROLE_TYPE, "topic")
            item.setData(_NAV_ROLE_FILENAME, filename)
            self.nav_list.addItem(item)
            if filename == self._current_filename:
                self.nav_list.setCurrentItem(item)
        self._set_nav_description()
        self.status_bar.showMessage("Showing help topics")

    def _show_headings_list(self, headings: list[tuple[str, str, int]]) -> None:
        self._nav_mode = "headings"
        self.nav_list.clear()

        back_item = QListWidgetItem("All Help Topics")
        back_item.setData(_NAV_ROLE_TYPE, "back")
        self.nav_list.addItem(back_item)

        for title, anchor_id, level in headings:
            display = f"  {title}" if level >= 3 else title
            item = QListWidgetItem(display)
            item.setData(_NAV_ROLE_TYPE, "heading")
            item.setData(_NAV_ROLE_ANCHOR, anchor_id)
            item.setData(Qt.ItemDataRole.AccessibleTextRole, title)
            self.nav_list.addItem(item)

        self._set_nav_description()

    def _on_nav_item_activated(self, item: QListWidgetItem) -> None:
        nav_type = item.data(_NAV_ROLE_TYPE)
        if nav_type == "topic":
            filename = item.data(_NAV_ROLE_FILENAME)
            if filename:
                self._load_doc(str(filename))
            return
        if nav_type == "back":
            self._show_topics_list()
            self._focus_nav_list()
            return
        if nav_type == "heading":
            anchor_id = item.data(_NAV_ROLE_ANCHOR)
            title = item.data(Qt.ItemDataRole.AccessibleTextRole) or item.text().strip()
            if anchor_id:
                QTimer.singleShot(
                    0,
                    lambda aid=str(anchor_id), heading_title=str(title): self._jump_to_anchor(
                        aid, heading_title
                    ),
                )
            return

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
            self._set_help_body(missing_text)
            self._show_headings_list([])
            self._apply_window_title()
            self.status_bar.showMessage(f"Help file not found: {Path(filename).name}")
            return

        markdown = path.read_text(encoding="utf-8")
        html_doc, _links = markdown_to_html(markdown)
        self._current_filename = path.name
        self._current_title = _title_from_markdown(markdown)
        self._set_help_body(html_doc)
        self._show_headings_list(extract_headings(markdown))
        self._apply_window_title()
        self.status_bar.showMessage(f"Showing help: {self._current_title}")
        QTimer.singleShot(0, lambda: self._focus_help_text(at_start=True))

    def _set_help_body(self, html_doc: str) -> None:
        self.help_text.setHtml(html_doc)
        cursor = self.help_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.help_text.setTextCursor(cursor)
        self.help_text.setAccessibleName(self._current_title)
        self.help_text.setAccessibleDescription(
            f"Help topic: {self._current_title}. "
            "Use arrow keys to move line by line. Each sentence is its own paragraph. "
            "Use Tab or Alt+L to move to the help navigation list."
        )

    def _apply_window_title(self) -> None:
        title = f"AbCS Help - {self._current_title}"
        self.setWindowTitle(title)
        self.setAccessibleName(title)

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
                ("Alt+L", "Help navigation list"),
                ("Tab", "Switch between list and content"),
                ("Enter", "Open topic or jump to section"),
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
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setTabKeyNavigation(False)
        table.setAlternatingRowColors(False)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setMouseTracking(False)
        table.viewport().setMouseTracking(False)
        table.setAttribute(Qt.WidgetAttribute.WA_Hover, False)
        table.viewport().setAttribute(Qt.WidgetAttribute.WA_Hover, False)
        table.setStyleSheet(build_accessible_f1_popup_style())

        for row, (key, desc) in enumerate(shortcuts):
            item = QTableWidgetItem(f"{desc} - {key}")
            item.setData(Qt.ItemDataRole.AccessibleTextRole, f"{desc}: {key}")
            table.setItem(row, 0, item)

        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        font = table.font()
        font.setPointSize(self.scaler.get_scaled_size(11))
        table.setFont(font)
        layout.addWidget(table)
        dlg.exec()
