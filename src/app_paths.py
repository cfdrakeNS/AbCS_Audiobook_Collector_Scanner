"""Cross-platform writable user data directory for AbCS."""

from __future__ import annotations

import os
import sys
from pathlib import Path

APP_DIR_NAME = "AbCS"
_LEGACY_FROZEN_DIR = Path("AppData") / "Local" / APP_DIR_NAME


def get_user_data_dir() -> Path:
    """
    Return the per-user data directory for AbCS (database, backups, markers).

    Windows frozen: %LOCALAPPDATA%\\AbCS
    Linux frozen:   $XDG_DATA_HOME/AbCS or ~/.local/share/AbCS
    macOS frozen:   ~/Library/Application Support/AbCS
    """
    target = _platform_user_data_dir()
    target.mkdir(parents=True, exist_ok=True)
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
