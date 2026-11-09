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
_SOURCE_COPY_APP = "AudioBookCollector Dev"
_LEGACY_APP = "AbCS"

_settings_app = _SETTINGS_APP
_legacy_enabled = True

T = TypeVar("T")

_SCAN_PROPER_CASE_KEY = "import/scan/proper_case"
_LEGACY_PROPER_CASE_KEY = "import/autocorrect/proper_case"

_STALE_SETTINGS_KEYS = (
    "import/rules/genre_missing",
    "import/rules/bitrate_below_minimum",
    _LEGACY_PROPER_CASE_KEY,
    "import/flip_author_name",
    "import/autocorrect/move_leading_the_title",
)


def app_settings() -> QSettings:
    """Return the preferences store for this copy of AbCS."""
    return QSettings(_SETTINGS_ORG, _settings_app)


def use_source_copy_settings(enabled: bool = True) -> None:
    """Give the copy run from source its own preferences.

    The source copy uses "AudioBookCollector Dev" and never reads or cleans
    the legacy "AbCS" store, which the installed copy still shares.
    """
    global _settings_app, _legacy_enabled
    _settings_app = _SOURCE_COPY_APP if enabled else _SETTINGS_APP
    _legacy_enabled = not enabled


def settings_app_name() -> str:
    """Application name of the active preferences store."""
    return _settings_app


def _current_settings() -> QSettings:
    return app_settings()


def _legacy_settings() -> QSettings:
    return QSettings(_SETTINGS_ORG, _LEGACY_APP)


def read_setting(key: str, default: T, *, type: type | None = None) -> Any:
    """
    Read a QSettings value from AudioBookCollector, falling back to legacy AbCS.

    New preferences are stored under QSettings("AbCS", "AudioBookCollector").
    Older installs may still have values under QSettings("AbCS", "AbCS") only.
    The source copy skips the legacy fallback.
    """
    settings = _current_settings()
    if settings.contains(key) or not _legacy_enabled:
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


def purge_stale_settings() -> None:
    """Remove obsolete QSettings keys and retired import toggles."""
    current = _current_settings()
    for key in _STALE_SETTINGS_KEYS:
        current.remove(key)
    current.sync()
    if not _legacy_enabled:
        return
    legacy = _legacy_settings()
    for key in _STALE_SETTINGS_KEYS:
        legacy.remove(key)
    legacy.sync()


def migrate_legacy_import_settings() -> None:
    """Copy legacy proper-case pref into scan key, then drop legacy import tree."""
    if not _legacy_enabled:
        return
    current = _current_settings()
    legacy = _legacy_settings()

    if not current.contains(_SCAN_PROPER_CASE_KEY) and legacy.contains(
        _LEGACY_PROPER_CASE_KEY
    ):
        current.setValue(
            _SCAN_PROPER_CASE_KEY,
            legacy.value(_LEGACY_PROPER_CASE_KEY, False, type=bool),
        )

    if legacy.contains("import"):
        legacy.remove("import")
        legacy.sync()

    current.sync()


def run_settings_maintenance() -> None:
    """Startup housekeeping for QSettings (stale keys, legacy import migration)."""
    migrate_legacy_import_settings()
    purge_stale_settings()
