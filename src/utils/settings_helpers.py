"""
Settings Helpers - Centralized preference reading with legacy fallback.

This module provides utilities for reading application settings with
automatic fallback to legacy settings locations.
"""

from __future__ import annotations

from typing import Any, TypeVar

from PySide6.QtCore import QSettings

_SETTINGS_ORG = "AbCS"
_SETTINGS_APP = "AudioBookCollector"
_LEGACY_APP = "AbCS"

T = TypeVar("T")

_SCAN_PROPER_CASE_KEY = "import/scan/proper_case"
_LEGACY_PROPER_CASE_KEY = "import/autocorrect/proper_case"

_STALE_SETTINGS_KEYS = (
    "import/rules/genre_missing",
    "import/rules/bitrate_below_minimum",
    _LEGACY_PROPER_CASE_KEY,
)

# Legacy QSettings keys still read by web metadata fetch/clean (not import scan).
_WEB_METADATA_PREF_KEYS = (
    "import/flip_author_name",
    "import/autocorrect/move_leading_the_title",
)


def _current_settings() -> QSettings:
    return QSettings(_SETTINGS_ORG, _SETTINGS_APP)


def _legacy_settings() -> QSettings:
    return QSettings(_SETTINGS_ORG, _LEGACY_APP)


def read_setting(key: str, default: T, *, type: type | None = None) -> Any:
    """
    Read a QSettings value from AudioBookCollector, falling back to legacy AbCS.

    New preferences are stored under QSettings("AbCS", "AudioBookCollector").
    Older installs may still have values under QSettings("AbCS", "AbCS") only.
    """
    settings = _current_settings()
    if settings.contains(key):
        if type is None:
            return settings.value(key, default)
        return settings.value(key, default, type=type)

    legacy = _legacy_settings()
    if type is None:
        return legacy.value(key, default)
    return legacy.value(key, default, type=type)


def is_proper_case_enabled() -> bool:
    """Return whether name proper-case autocorrect is enabled (Preferences scan setting)."""
    settings = _current_settings()
    if settings.contains(_SCAN_PROPER_CASE_KEY):
        return settings.value(_SCAN_PROPER_CASE_KEY, False, type=bool)
    return bool(read_setting(_LEGACY_PROPER_CASE_KEY, False, type=bool))


def get_import_preferences() -> tuple[bool, bool]:
    """
    Read title/author formatting prefs for web metadata (legacy QSettings keys).

    Returns:
        Tuple of (move_articles, flip_author).
    """
    move_articles = bool(
        read_setting("import/autocorrect/move_leading_the_title", False, type=bool)
    )
    flip_author = bool(read_setting("import/flip_author_name", False, type=bool))
    return move_articles, flip_author


def purge_stale_settings() -> None:
    """Remove obsolete QSettings keys and retired import toggles."""
    current = _current_settings()
    legacy = _legacy_settings()
    for key in _STALE_SETTINGS_KEYS:
        current.remove(key)
        legacy.remove(key)
    current.sync()
    legacy.sync()


def migrate_legacy_import_settings() -> None:
    """Copy legacy proper-case pref into scan key, then drop legacy import tree."""
    current = _current_settings()
    legacy = _legacy_settings()

    if not current.contains(_SCAN_PROPER_CASE_KEY) and legacy.contains(
        _LEGACY_PROPER_CASE_KEY
    ):
        current.setValue(
            _SCAN_PROPER_CASE_KEY,
            legacy.value(_LEGACY_PROPER_CASE_KEY, False, type=bool),
        )

    for key in _WEB_METADATA_PREF_KEYS:
        if not current.contains(key) and legacy.contains(key):
            current.setValue(key, legacy.value(key))

    if legacy.contains("import"):
        legacy.remove("import")
        legacy.sync()

    current.sync()


def run_settings_maintenance() -> None:
    """Startup housekeeping for QSettings (stale keys, legacy import migration)."""
    migrate_legacy_import_settings()
    purge_stale_settings()
