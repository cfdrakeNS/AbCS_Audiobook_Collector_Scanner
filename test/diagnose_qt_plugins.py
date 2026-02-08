"""Diagnostic script for Qt/PySide6 plugin discovery.

Run inside the active venv:
  python diagnose_qt_plugins.py
"""

from __future__ import annotations

import os
from pathlib import Path

try:
    from PySide6.QtCore import QCoreApplication, QLibraryInfo
except Exception as exc:  # pragma: no cover - diagnostic script
    raise SystemExit(f"PySide6 import failed: {exc}")


def _dir_exists(path: str | Path) -> bool:
    try:
        return Path(path).is_dir()
    except OSError:
        return False


def _list_dir(path: str | Path) -> list[str]:
    try:
        return sorted(p.name for p in Path(path).iterdir())
    except OSError:
        return []


def main() -> int:
    app = QCoreApplication([])

    qt_plugins_path = QLibraryInfo.path(QLibraryInfo.PluginsPath)
    lib_paths = QCoreApplication.libraryPaths()
    

    print("Qt plugin discovery diagnostic")
    print("=")
    print(f"QLibraryInfo PluginsPath: {qt_plugins_path}")
    print("QCoreApplication.libraryPaths():")
    for p in lib_paths:
        print(f"  - {p}")

    print("\nFilesystem checks:")
    print(f"Plugins path exists: {_dir_exists(qt_plugins_path)}")

    accessible_dir = Path(qt_plugins_path) / "accessible"
    platform_dir = Path(qt_plugins_path) / "platforms"

    print(f"Accessible dir exists: {_dir_exists(accessible_dir)}")
    if _dir_exists(accessible_dir):
        print("  accessible/*:")
        for name in _list_dir(accessible_dir):
            print(f"    - {name}")

    print(f"Platforms dir exists: {_dir_exists(platform_dir)}")
    if _dir_exists(platform_dir):
        print("  platforms/*:")
        for name in _list_dir(platform_dir):
            print(f"    - {name}")

    print("\nEnv vars:")
    for key in [
        "QT_DEBUG_PLUGINS",
        "QT_ACCESSIBILITY",
        "QT_ACCESSIBILITY_API_VERSION",
        "QT_QPA_PLATFORM",
        "QT_PLUGIN_PATH",
    ]:
        value = os.environ.get(key, "(not set)")
        print(f"  {key} = {value}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
