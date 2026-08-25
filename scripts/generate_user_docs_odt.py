r"""
Generate LibreOffice ODT user guides from numbered Markdown in doc/.

Source files: doc/[0-9][0-9]_*.md (user index, process guides, reference docs)
Output:       doc/user_docs/*.odt

Setup (once):
    pip install pypandoc
    python scripts/generate_user_docs_odt.py --install-pandoc

The --install-pandoc step downloads the Pandoc binary via pypandoc if it is not
already on PATH. You can also install Pandoc yourself (winget install Pandoc).

Run:
    python scripts/generate_user_docs_odt.py
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOC_DIR = PROJECT_ROOT / "doc"
OUTPUT_DIR = DOC_DIR / "user_docs"

LINK_RE = re.compile(r"\((\d{2}_[^)]+\.)md\)")


def _ensure_pypandoc():
    try:
        import pypandoc  # noqa: F401
    except ImportError as exc:
        print(
            "pypandoc is not installed. Run: pip install pypandoc",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc


def ensure_pandoc(install: bool = False) -> None:
    """Verify Pandoc is available; optionally download it through pypandoc."""
    import pypandoc

    try:
        version = pypandoc.get_pandoc_version()
        print(f"Using Pandoc {version}")
        return
    except OSError:
        if not install:
            print(
                "Pandoc was not found. Either install it (winget install Pandoc) or run:\n"
                "  python scripts/generate_user_docs_odt.py --install-pandoc",
                file=sys.stderr,
            )
            raise SystemExit(1)

    print("Downloading Pandoc (one-time setup)...")
    pypandoc.download_pandoc()
    print(f"Using Pandoc {pypandoc.get_pandoc_version()}")


def source_markdown_files() -> list[Path]:
    """Return numbered user-doc Markdown files in doc/."""
    files = sorted(DOC_DIR.glob("[0-9][0-9]_*.md"))
    if not files:
        print(f"No numbered Markdown files found in {DOC_DIR}", file=sys.stderr)
        raise SystemExit(1)
    return files


def rewrite_links_for_odt(text: str) -> str:
    """Point cross-references at sibling .odt files in user_docs/."""
    return LINK_RE.sub(r"(\1odt)", text)


def convert_file(source: Path, output: Path) -> None:
    """Convert one Markdown file to ODT."""
    import pypandoc

    markdown = source.read_text(encoding="utf-8")
    markdown = rewrite_links_for_odt(markdown)

    extra_args = [
        f"--resource-path={DOC_DIR}",
        "--standalone",
        "--from=markdown",
        "--to=odt",
    ]

    pypandoc.convert_text(
        markdown,
        "odt",
        format="md",
        outputfile=str(output),
        extra_args=extra_args,
    )


def generate_all() -> int:
    """Convert all numbered user docs; return count written."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sources = source_markdown_files()
    written = 0

    for source in sources:
        output = OUTPUT_DIR / f"{source.stem}.odt"
        print(f"  {source.name} -> user_docs/{output.name}")
        convert_file(source, output)
        written += 1

    print(f"\nWrote {written} ODT file(s) to {OUTPUT_DIR}")
    return written


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate ODT user guides from doc/[0-9][0-9]_*.md"
    )
    parser.add_argument(
        "--install-pandoc",
        action="store_true",
        help="Download Pandoc via pypandoc if it is not already installed",
    )
    args = parser.parse_args()

    _ensure_pypandoc()
    ensure_pandoc(install=args.install_pandoc)
    generate_all()


if __name__ == "__main__":
    main()
