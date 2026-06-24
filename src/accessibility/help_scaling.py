"""Help-window-only zoom (independent of global ui_scale)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QSettings

from src.accessibility.screen_reader import is_screen_reader_active

if TYPE_CHECKING:
    from src.accessibility.scaling import UIScaler

HELP_UI_SCALE_KEY = "help/ui_scale"
HELP_SR_DEFAULT_SCALE = 100


class HelpUIScaler:
    """Local zoom for the Help window; does not change global ui_scale."""

    def __init__(self, help_scale_pct: int):
        from src.accessibility.scaling import UIScaler

        self._current_scale = _clamp_scale(help_scale_pct)

    @property
    def current_scale(self) -> int:
        return self._current_scale

    def set_scale(self, help_scale_pct: int) -> None:
        self._current_scale = _clamp_scale(help_scale_pct)

    def get_scaled_size(self, base_size: int) -> int:
        return int(base_size * (self._current_scale / 100.0))


def _settings() -> QSettings:
    return QSettings("AbCS", "AudioBookCollector")


def _clamp_scale(percentage: int) -> int:
    from src.accessibility.scaling import UIScaler

    return max(UIScaler.MIN_SCALE, min(UIScaler.MAX_SCALE, int(percentage)))


def _read_saved_help_scale(store: QSettings) -> int | None:
    """Return saved Help zoom percentage, or None when unset."""
    raw = store.value(HELP_UI_SCALE_KEY)
    if raw is None:
        return None
    try:
        return _clamp_scale(int(raw))
    except (TypeError, ValueError):
        return None


def save_help_scale(percentage: int, settings: QSettings | None = None) -> int:
    """Persist a user-chosen Help zoom percentage."""
    store = settings or _settings()
    scale = _clamp_scale(percentage)
    store.setValue(HELP_UI_SCALE_KEY, scale)
    store.sync()
    return scale


def resolve_initial_help_scale(
    global_scaler: Optional["UIScaler"] = None,
    settings: QSettings | None = None,
) -> int:
    """Return Help zoom for this session without writing settings.

    Uses saved help/ui_scale when present. Otherwise 100% with a screen reader
  active, or the global app zoom when no screen reader is running.
    """
    from src.accessibility.scaling import UIScaler

    store = settings or _settings()
    global_scale = (
        global_scaler.current_scale
        if global_scaler is not None
        else UIScaler.DEFAULT_SCALE
    )

    saved = _read_saved_help_scale(store)
    if saved is not None:
        return saved

    if is_screen_reader_active():
        return HELP_SR_DEFAULT_SCALE

    return global_scale


def help_preset_name(percentage: int) -> str:
    """Return UIScaler preset label for a Help zoom percentage, or Custom."""
    from src.accessibility.scaling import UIScaler

    for name, value in UIScaler.SCALE_PRESETS.items():
        if value == int(percentage):
            return name
    return "Custom"
