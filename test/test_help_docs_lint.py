"""Style checks for user help in help_docs/ (see doc/help_docs_authoring.md)."""

from __future__ import annotations

import re

import pytest

from src.accessibility.help_paths import HELP_DOC_FILENAME_RE, resolve_help_docs_dir

HELP_DIR = resolve_help_docs_dir()
TOPICS = sorted(path for path in HELP_DIR.glob("*.md") if HELP_DOC_FILENAME_RE.match(path.name))

SCREEN_READER_PRODUCTS_RE = re.compile(r"\b(jaws|nvda|orca|voiceover)\b", re.IGNORECASE)
HEADING_RE = re.compile(r"^(#+)\s+(.*)$")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
ITALIC_RE = re.compile(r"(?<![\w*])\*(?![\s*])[^*\n]+?(?<![\s*])\*(?![\w*])")
BULLET_RE = re.compile(r"^(\s*)- ")


def _lines(path):
    return path.read_text(encoding="utf-8").splitlines()


def _ids(paths):
    return [path.name for path in paths]


def test_help_topics_found():
    assert len(TOPICS) >= 20


@pytest.mark.parametrize("path", TOPICS, ids=_ids(TOPICS))
def test_no_screen_reader_product_names(path):
    found = [
        f"line {number}: {line.strip()}"
        for number, line in enumerate(_lines(path), 1)
        if SCREEN_READER_PRODUCTS_RE.search(line)
    ]
    assert not found, "Say 'screen reader' instead:\n" + "\n".join(found)


@pytest.mark.parametrize("path", TOPICS, ids=_ids(TOPICS))
def test_one_title_at_the_top(path):
    headings = [line for line in _lines(path) if HEADING_RE.match(line)]
    titles = [line for line in headings if line.startswith("# ")]
    assert titles and headings[0] == titles[0], "First heading must be the # title"
    assert len(titles) == 1, f"Only one # title allowed: {titles}"


@pytest.mark.parametrize("path", TOPICS, ids=_ids(TOPICS))
def test_headings_are_supported_and_do_not_start_with_steps(path):
    problems = []
    for number, line in enumerate(_lines(path), 1):
        match = HEADING_RE.match(line)
        if not match:
            continue
        level, text = len(match.group(1)), match.group(2).strip()
        if level > 3:
            problems.append(f"line {number}: use ### at most: {line}")
        if text.startswith("#"):
            problems.append(f"line {number}: malformed heading: {line}")
        if text.casefold().startswith("steps"):
            problems.append(f"line {number}: heading starts with Steps: {line}")
    assert not problems, "\n".join(problems)


@pytest.mark.parametrize("path", TOPICS, ids=_ids(TOPICS))
def test_no_unsupported_markdown(path):
    problems = []
    previous_bullet_indent = None
    for number, line in enumerate(_lines(path), 1):
        stripped = line.strip()
        if stripped in {"---", "***", "___"}:
            problems.append(f"line {number}: horizontal rule")
        if stripped.startswith("```"):
            problems.append(f"line {number}: fenced code block")
        if stripped.startswith(">"):
            problems.append(f"line {number}: block quote")
        if "![" in line:
            problems.append(f"line {number}: image")
        if re.search(r"</?(b|i|br|p|div|span|em|strong)\b", line, re.IGNORECASE):
            problems.append(f"line {number}: HTML tag")
        if not stripped.startswith("|") and ITALIC_RE.search(line.replace("**", "\0\0")):
            problems.append(f"line {number}: italics: {stripped}")
        bullet = BULLET_RE.match(line)
        if bullet:
            indent = len(bullet.group(1))
            if previous_bullet_indent is not None and indent > previous_bullet_indent:
                problems.append(f"line {number}: nested bullet: {stripped}")
            previous_bullet_indent = indent
        elif stripped:
            previous_bullet_indent = None
    assert not problems, "\n".join(problems)


@pytest.mark.parametrize("path", TOPICS, ids=_ids(TOPICS))
def test_links_point_to_existing_topics(path):
    missing = [
        target
        for line in _lines(path)
        for target in LINK_RE.findall(line)
        if target.endswith(".md") and not (HELP_DIR / target).is_file()
    ]
    assert not missing, f"Links to missing topics: {missing}"


@pytest.mark.parametrize("path", TOPICS, ids=_ids(TOPICS))
def test_related_section_uses_one_name(path):
    old_names = {"related documentation", "related guides"}
    headings = [
        match.group(2).strip().casefold()
        for match in map(HEADING_RE.match, _lines(path))
        if match
    ]
    assert not old_names & set(headings), "Use '## Related help'"
