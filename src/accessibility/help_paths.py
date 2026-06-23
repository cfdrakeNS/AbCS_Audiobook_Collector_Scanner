"""Resolve help documentation paths for dev and installed builds.

Help topics live in ``help_docs/`` as markdown files named ``nn_topic_name.md``
(two digits, underscore, topic slug). ``discover_help_topics()`` scans that folder
at runtime and builds sorted (display label, filename) pairs for the help window
topic list. Display labels drop the numeric prefix and replace underscores with
spaces (``11_import_book_list.md`` → ``import book list``).

Shift+F1 context help uses per-window filenames in ``src/ui/help_router.py``
(``WINDOW_HELP_MAP``), not the dynamic topic list. Cross-links inside markdown
should use the bare filename (for example ``[Import](02_import.md)``).

See ``help_docs/01_overview.md`` (user-facing) and README.md (developer summary).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from src.accessibility.graphics_paths import bundle_base, project_root

OVERVIEW_DOC = "01_overview.md"

HELP_DOC_FILENAME_RE = re.compile(r"^\d{2}_[\w-]+\.md$", re.IGNORECASE)


def help_doc_display_name(filename: str) -> str:
    """Build a list label from nn_topic.md by dropping the numeric prefix."""
    stem = Path(filename).stem
    if len(stem) >= 3 and stem[:2].isdigit() and stem[2] == "_":
        return stem[3:].replace("_", " ")
    return stem.replace("_", " ")


def discover_help_topics() -> list[tuple[str, str]]:
    """Return sorted (display label, filename) pairs for help_docs/*.md files."""
    docs_dir = resolve_help_docs_dir()
    topics: list[tuple[str, str]] = []
    for path in sorted(docs_dir.glob("*.md")):
        name = path.name
        if HELP_DOC_FILENAME_RE.match(name):
            topics.append((help_doc_display_name(name), name))
    return topics


def _search_bases() -> list[Path]:
    """Directories to search for help_docs (dev, frozen, and installed app)."""
    bases: list[Path] = []
    seen: set[Path] = set()

    def add_base(path: Path) -> None:
        resolved = path.resolve()
        if resolved in seen:
            return
        seen.add(resolved)
        bases.append(resolved)

    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            add_base(Path(meipass))
        if getattr(sys, "executable", None):
            add_base(Path(sys.executable).resolve().parent)

    add_base(bundle_base())
    root = project_root()
    if root.resolve() not in seen:
        add_base(root)

    return bases


def resolve_help_docs_dir() -> Path:
    """Return the directory containing markdown help files."""
    for base in _search_bases():
        candidate = base / "help_docs"
        if candidate.is_dir():
            return candidate.resolve()
    return (project_root() / "help_docs").resolve()


def resolve_help_doc_path(filename: str) -> Path:
    """Return the path to a help markdown file, or a predictable fallback."""
    safe_name = Path(filename).name
    docs_dir = resolve_help_docs_dir()
    return docs_dir / safe_name


def help_doc_exists(filename: str) -> bool:
    """True when the requested help file is present on disk."""
    return resolve_help_doc_path(filename).is_file()
