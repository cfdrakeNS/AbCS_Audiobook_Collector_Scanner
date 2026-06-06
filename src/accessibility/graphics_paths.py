"""Shared graphics asset path resolution for dev and PyInstaller bundles."""

from __future__ import annotations

import os
import sys
from pathlib import Path

GRAPHICS_DIR_NAMES = ("graphics", "Graphics")

# Prefer PNG on Linux window managers; ICO remains first choice on Windows.
APP_ICON_CANDIDATES = (
    "abcs_icon_256x256.png",
    "abcs_source_256.png",
    "abcs_icon_256x256.ico",
    "AbCS_WinTitle.png",
    "abcs_WinTitle.png",
)


def project_root() -> Path:
    """Repository root (parent of src/)."""
    return Path(__file__).resolve().parents[2]


def bundle_base() -> Path:
    """Base directory for bundled assets (MEIPASS when frozen, else project root)."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return project_root()


def _search_bases() -> list[Path]:
    """Directories to search for bundled graphics (dev and frozen)."""
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
            add_base(Path(sys.executable).resolve().parent / "graphics")

    add_base(bundle_base())
    root = project_root()
    if root.resolve() not in seen:
        add_base(root)

    return bases


def resolve_graphics_path(filename: str) -> str:
    """Return the best existing path for a graphics file, or a predictable fallback."""
    root = project_root()
    for base in _search_bases():
        direct = base / filename
        if direct.is_file():
            return str(direct.resolve())
        for graphics_dir in GRAPHICS_DIR_NAMES:
            candidate = base / graphics_dir / filename
            if candidate.is_file():
                return str(candidate.resolve())

    return str((root / "graphics" / filename).resolve())


def resolve_app_icon_path() -> str:
    """Return the first usable application window icon path."""
    if sys.platform.startswith("win32"):
        candidates = (
            "abcs_icon_256x256.ico",
            "abcs_icon_256x256.png",
            "abcs_source_256.png",
            "AbCS_WinTitle.png",
            "abcs_WinTitle.png",
        )
    else:
        candidates = APP_ICON_CANDIDATES

    for filename in candidates:
        path = resolve_graphics_path(filename)
        if os.path.isfile(path):
            return path

    return resolve_graphics_path("abcs_icon_256x256.ico")
