"""Search all help topics for the Help window.

Each topic in ``help_docs/`` is split into sections at its h2/h3 headings.
Section anchors (``h0``, ``h1``, ...) match ``help_window.extract_headings`` so a
result can jump to its section. Text before the first h2 belongs to the topic
itself (blank anchor). Matching is case-insensitive and works on whole words:
a typed word matches a word that starts with it, and short typed words must
match exactly. Small words such as "a" and "to" are skipped. Every remaining
word must appear in the same section. All-help results keep one row per topic.
No Qt here, so it can be tested on its own.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from src.accessibility.help_paths import (
    discover_help_topics,
    resolve_help_doc_path,
    resolve_help_docs_dir,
)

MAX_RESULTS = 50
SNIPPET_CHARS = 110

_HEADER_RE = re.compile(r"^(#{1,6})\s+(.+)$")
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_LIST_MARKER_RE = re.compile(r"^(?:[-*]\s+|\d+\.\s+)")
_TABLE_DIVIDER_RE = re.compile(r"^[\s|:-]+$")
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_WORD_RE = re.compile(r"\w+(?:[+'’]\w+)*")

# Typed words of this length or shorter must match a whole word exactly.
EXACT_WORD_MAX_LEN = 2

STOP_WORDS = frozenset(
    {
        "a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "does",
        "for", "from", "how", "i", "in", "is", "it", "my", "of", "on", "or",
        "the", "to", "what", "when", "where", "why", "with",
    }
)

# Link-only sections that repeat other topics' names.
SKIPPED_HEADINGS = frozenset({"related help"})

# Lower is better.
RANK_TITLE = 0
RANK_HEADING = 1
RANK_BODY = 2


@dataclass(frozen=True)
class HelpSection:
    filename: str
    topic_title: str
    heading: str
    anchor_id: str
    text: str
    order: int


@dataclass(frozen=True)
class HelpSearchHit:
    filename: str
    topic_title: str
    heading: str
    anchor_id: str
    snippet: str
    match_text: str
    rank: int

    @property
    def label(self) -> str:
        """List text: section, guide (when different), then the snippet."""
        return self.label_for(include_guide=True)

    def label_for(self, *, include_guide: bool) -> str:
        """Guide (all-help scope), then section when different, then snippet."""
        heading = self.heading or self.topic_title
        parts = []
        if include_guide:
            parts.append(self.topic_title)
        if not include_guide or heading.casefold() != self.topic_title.casefold():
            parts.append(heading)
        if self.snippet:
            parts.append(self.snippet)
        return " - ".join(parts)


@dataclass(frozen=True)
class HelpSearchResult:
    query: str
    hits: tuple[HelpSearchHit, ...]
    total: int
    topic_count: int = 0

    @property
    def truncated(self) -> bool:
        return self.total > len(self.hits)


def query_words(query: str) -> list[str]:
    """Distinct search words in typed order, case-folded."""
    words: list[str] = []
    for key in _WORD_RE.findall((query or "").casefold()):
        if key not in words:
            words.append(key)
    return words


def meaningful_words(words: list[str]) -> list[str]:
    """Words without small words; all words when every one is small."""
    kept = [word for word in words if word not in STOP_WORDS]
    return kept or list(words)


def _text_words(text: str) -> set[str]:
    return set(_WORD_RE.findall(text.casefold()))


def _word_matches(word: str, text_words: set[str]) -> bool:
    if len(word) <= EXACT_WORD_MAX_LEN:
        return word in text_words
    return any(candidate.startswith(word) for candidate in text_words)


def _plain_line(line: str) -> str:
    text = _LINK_RE.sub(r"\1", line.strip())
    stripped = text.strip()
    if stripped.startswith("|") and stripped.endswith("|"):
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if _TABLE_DIVIDER_RE.match("".join(cells)):
            return ""
        text = " - ".join(cell for cell in cells if cell)
    text = _LIST_MARKER_RE.sub("", text.strip())
    text = text.replace("**", "").replace("`", "")
    return " ".join(text.split())


def split_help_sections(filename: str, markdown: str) -> list[HelpSection]:
    """Split one topic into searchable sections (anchors match the help window)."""
    topic_title = ""
    sections: list[HelpSection] = []
    heading = ""
    anchor_id = ""
    lines: list[str] = []
    anchor_index = 0

    def flush() -> None:
        text = " ".join(line for line in lines if line)
        if text or heading:
            sections.append(
                HelpSection(
                    filename=filename,
                    topic_title=topic_title,
                    heading=heading or topic_title,
                    anchor_id=anchor_id,
                    text=text,
                    order=len(sections),
                )
            )

    for raw_line in markdown.replace("\r\n", "\n").split("\n"):
        stripped = raw_line.strip()
        if (
            stripped.startswith("|")
            and _TABLE_DIVIDER_RE.match(stripped)
            and lines
        ):
            lines.pop()  # table header row (column names) is not help text
            continue
        match = _HEADER_RE.match(stripped)
        if match:
            level = len(match.group(1))
            title = _plain_line(match.group(2))
            if level < 2:
                if not topic_title:
                    topic_title = title
                continue
            flush()
            heading = title
            anchor_id = f"h{anchor_index}"
            anchor_index += 1
            lines = []
            continue
        lines.append(_plain_line(raw_line))
    flush()

    if not topic_title:
        topic_title = Path(filename).stem
    return [
        HelpSection(
            filename=section.filename,
            topic_title=topic_title,
            heading=section.heading or topic_title,
            anchor_id=section.anchor_id,
            text=section.text,
            order=section.order,
        )
        for section in sections
    ]


_SECTION_CACHE: dict[str, tuple[list[str], list[HelpSection]]] = {}


def load_help_sections() -> tuple[list[str], list[HelpSection]]:
    """All sections in curated topic order; read once per session."""
    key = str(resolve_help_docs_dir())
    cached = _SECTION_CACHE.get(key)
    if cached is not None:
        return cached
    order: list[str] = []
    sections: list[HelpSection] = []
    for _label, filename in discover_help_topics():
        path = resolve_help_doc_path(filename)
        try:
            markdown = path.read_text(encoding="utf-8")
        except OSError:
            continue
        order.append(filename)
        sections.extend(split_help_sections(filename, markdown))
    _SECTION_CACHE[key] = (order, sections)
    return order, sections


def _word_start_index(text: str, word: str) -> int:
    """Index of ``word`` where it starts a word in ``text``, or -1."""
    match = re.search(r"(?<!\w)" + re.escape(word), text.casefold())
    return match.start() if match else -1


def _snippet(text: str, word: str) -> str:
    """Sentence holding the first match, trimmed around it."""
    index = _word_start_index(text, word)
    if index < 0:
        return ""
    sentence_start = 0
    for match in _SENTENCE_SPLIT_RE.finditer(text):
        if match.end() > index:
            break
        sentence_start = match.end()
    end_match = _SENTENCE_SPLIT_RE.search(text, index)
    sentence_end = end_match.start() if end_match else len(text)
    sentence = text[sentence_start:sentence_end].strip()
    if len(sentence) <= SNIPPET_CHARS:
        return sentence
    offset = index - sentence_start
    start = max(0, offset - SNIPPET_CHARS // 3)
    piece = sentence[start : start + SNIPPET_CHARS].strip()
    prefix = "..." if start > 0 else ""
    suffix = "..." if start + SNIPPET_CHARS < len(sentence) else ""
    return f"{prefix}{piece}{suffix}"


def _all_match(words: list[str], text: str) -> bool:
    text_words = _text_words(text)
    return all(_word_matches(word, text_words) for word in words)


def _rank(section: HelpSection, words: list[str]) -> int | None:
    if section.order == 0 and _all_match(words, section.topic_title):
        return RANK_TITLE
    if not _all_match(words, f"{section.heading} {section.text}"):
        return None
    if _all_match(words, section.heading):
        return RANK_HEADING
    return RANK_BODY


def search_help(
    query: str,
    *,
    sections: list[HelpSection] | None = None,
    topic_order: list[str] | None = None,
    limit: int = MAX_RESULTS,
    group_by_topic: bool = True,
) -> HelpSearchResult:
    """Find sections holding every meaningful query word; best topics first.

    With ``group_by_topic`` each topic keeps only its best section, so the
    result list has one row per topic.
    """
    typed = query_words(query)
    if not typed:
        return HelpSearchResult(query=(query or "").strip(), hits=(), total=0)
    words = meaningful_words(typed)
    if sections is None:
        topic_order, sections = load_help_sections()
    order_index = {name: index for index, name in enumerate(topic_order or [])}

    phrase = " ".join(typed)

    def has_phrase(section: HelpSection) -> bool:
        return _word_start_index(f"{section.heading} {section.text}", phrase) >= 0

    matched: list[tuple[HelpSection, int, int]] = []
    for section in sections:
        if section.heading.casefold() in SKIPPED_HEADINGS:
            continue
        rank = _rank(section, words)
        if rank is not None:
            score = rank * 2 + (0 if len(typed) == 1 or has_phrase(section) else 1)
            matched.append((section, rank, score))

    # A typed phrase found as written outranks scattered words: keep only
    # phrase, heading, and title matches.
    if len(typed) > 1 and any(score == rank * 2 for _s, rank, score in matched):
        matched = [
            entry
            for entry in matched
            if entry[2] == entry[1] * 2 or entry[1] < RANK_BODY
        ]

    topic_score: dict[str, int] = {}
    for section, _rank_value, score in matched:
        topic_score[section.filename] = min(
            score, topic_score.get(section.filename, score)
        )

    if group_by_topic:
        matched.sort(
            key=lambda entry: (
                topic_score[entry[0].filename],
                order_index.get(entry[0].filename, len(order_index)),
                entry[2],
                entry[0].order,
            )
        )
        seen: set[str] = set()
        best: list[tuple[HelpSection, int, int]] = []
        for entry in matched:
            if entry[0].filename not in seen:
                seen.add(entry[0].filename)
                best.append(entry)
        matched = best
    else:
        matched.sort(
            key=lambda entry: (
                topic_score[entry[0].filename],
                order_index.get(entry[0].filename, len(order_index)),
                entry[0].order,
            )
        )

    hits: list[HelpSearchHit] = []
    for section, rank, _score in matched[: max(0, limit)]:
        match_text = phrase if len(typed) > 1 and has_phrase(section) else words[0]
        snippet = _snippet(section.text, match_text) or _snippet(
            section.text, words[0]
        )
        hits.append(
            HelpSearchHit(
                filename=section.filename,
                topic_title=section.topic_title,
                heading=section.heading,
                anchor_id=section.anchor_id,
                snippet=snippet,
                match_text=match_text,
                rank=rank,
            )
        )
    return HelpSearchResult(
        query=(query or "").strip(),
        hits=tuple(hits),
        total=len(matched),
        topic_count=len(topic_score),
    )


def search_summary(result: HelpSearchResult, topic_title: str = "") -> str:
    """Status text after a search; ``topic_title`` set means current-topic scope."""
    if not result.query:
        return "Type words to search help, then press Enter."
    if not result.hits:
        if topic_title:
            return f"No matches for {result.query} in {topic_title}."
        return f"No matches for {result.query}."
    if topic_title:
        sections = "section" if result.total == 1 else "sections"
        verb = "matches" if result.total == 1 else "match"
        text = f"{result.total} {sections} in {topic_title} {verb} {result.query}."
    else:
        topics = "topic" if result.topic_count == 1 else "topics"
        verb = "matches" if result.topic_count == 1 else "match"
        text = f"{result.topic_count} {topics} {verb} {result.query}."
    if result.truncated:
        text += f" Showing first {len(result.hits)}."
    return text
