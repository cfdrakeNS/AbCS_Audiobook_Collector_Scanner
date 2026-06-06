"""Cross-platform writable user data directory for AbCS."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

APP_DIR_NAME = "AbCS"
_LEGACY_FROZEN_DIR = Path("AppData") / "Local" / APP_DIR_NAME
_MIGRATION_MARKER = ".migrated_from_windows_style_path"


def get_user_data_dir(*, migrate_legacy: bool = True) -> Path:
    """
    Return the per-user data directory for AbCS (database, backups, markers).

    Windows frozen: %LOCALAPPDATA%\\AbCS
    Linux frozen:   $XDG_DATA_HOME/AbCS or ~/.local/share/AbCS
    macOS frozen:   ~/Library/Application Support/AbCS
    """
    target = _platform_user_data_dir()
    target.mkdir(parents=True, exist_ok=True)

    if migrate_legacy and getattr(sys, "frozen", False):
        _migrate_legacy_frozen_data_dir(target)

    return target


def _home_dir() -> Path:
    home = os.environ.get("HOME")
    if home:
        return Path(home)
    return Path.home()


def _platform_user_data_dir() -> Path:
    if sys.platform.startswith("win32"):
        local = os.environ.get("LOCALAPPDATA")
        if local:
            return Path(local) / APP_DIR_NAME
        return Path.home() / _LEGACY_FROZEN_DIR

    if sys.platform == "darwin":
        return _home_dir() / "Library" / "Application Support" / APP_DIR_NAME

    xdg_data = os.environ.get("XDG_DATA_HOME")
    if xdg_data:
        return Path(xdg_data) / APP_DIR_NAME
    return _home_dir() / ".local" / "share" / APP_DIR_NAME


def _migrate_legacy_frozen_data_dir(target: Path) -> None:
    """Move data from mistaken ~/AppData/Local/AbCS on Linux/macOS frozen builds."""
    if sys.platform.startswith("win32"):
        return

    legacy = _home_dir() / _LEGACY_FROZEN_DIR
    if not legacy.is_dir() or legacy.resolve() == target.resolve():
        return
    if (target / _MIGRATION_MARKER).exists():
        return
    if (target / "abcs.db").exists():
        return

    legacy_db = legacy / "abcs.db"
    legacy_marker = legacy / ".bundled_first_run_complete"
    if not legacy_db.exists() and not legacy_marker.exists():
        return

    for item in legacy.iterdir():
        dest = target / item.name
        if dest.exists():
            continue
        if item.is_dir():
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)

    (target / _MIGRATION_MARKER).write_text(str(legacy.resolve()), encoding="utf-8")
