"""Tests for Help-window-only zoom with screen readers."""

import pytest
from PySide6.QtCore import QSettings

from src.accessibility.help_scaling import (
    HELP_SR_DEFAULT_SCALE,
    HELP_UI_SCALE_KEY,
    HelpUIScaler,
    help_preset_name,
    resolve_initial_help_scale,
    save_help_scale,
)


@pytest.fixture
def isolated_qsettings(tmp_path):
    """Use temporary INI-based QSettings to avoid user-profile settings writes."""
    original_format = QSettings.defaultFormat()
    QSettings.setDefaultFormat(QSettings.IniFormat)
    QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, str(tmp_path))
    try:
        yield
    finally:
        QSettings.setDefaultFormat(original_format)


class _ScalerStub:
    def __init__(self, scale: int):
        self.current_scale = scale

    def get_scaled_size(self, base_size: int) -> int:
        return int(base_size * (self.current_scale / 100.0))


def test_help_ui_scaler_uses_local_percentage():
    scaler = HelpUIScaler(100)
    assert scaler.current_scale == 100
    assert scaler.get_scaled_size(12) == 12

    large = HelpUIScaler(150)
    assert large.get_scaled_size(12) == 18

    large.set_scale(125)
    assert large.current_scale == 125
    assert large.get_scaled_size(12) == 15


def _fresh_settings() -> QSettings:
    settings = QSettings("AbCS", "AudioBookCollector")
    settings.clear()
    return settings


def test_resolve_initial_without_screen_reader_uses_global(
    isolated_qsettings, monkeypatch
):
    monkeypatch.setattr(
        "src.accessibility.help_scaling.is_screen_reader_active",
        lambda: False,
    )
    settings = _fresh_settings()

    assert resolve_initial_help_scale(_ScalerStub(150), settings=settings) == 150
    assert not settings.contains(HELP_UI_SCALE_KEY)


def test_resolve_initial_without_screen_reader_uses_saved_help_pref(
    isolated_qsettings, monkeypatch
):
    monkeypatch.setattr(
        "src.accessibility.help_scaling.is_screen_reader_active",
        lambda: False,
    )
    settings = _fresh_settings()
    settings.setValue(HELP_UI_SCALE_KEY, 125)

    assert resolve_initial_help_scale(_ScalerStub(150), settings=settings) == 125


def test_resolve_initial_sr_defaults_100_without_persisting(
    isolated_qsettings, monkeypatch
):
    monkeypatch.setattr(
        "src.accessibility.help_scaling.is_screen_reader_active",
        lambda: True,
    )
    settings = _fresh_settings()
    settings.setValue("ui_scale", 150)
    assert not settings.contains(HELP_UI_SCALE_KEY)

    assert (
        resolve_initial_help_scale(_ScalerStub(150), settings=settings)
        == HELP_SR_DEFAULT_SCALE
    )
    assert not settings.contains(HELP_UI_SCALE_KEY)


def test_resolve_initial_sr_uses_saved_help_pref(isolated_qsettings, monkeypatch):
    monkeypatch.setattr(
        "src.accessibility.help_scaling.is_screen_reader_active",
        lambda: True,
    )
    settings = _fresh_settings()
    settings.setValue(HELP_UI_SCALE_KEY, 150)

    assert resolve_initial_help_scale(_ScalerStub(150), settings=settings) == 150


def test_save_help_scale_persists_choice(isolated_qsettings):
    settings = _fresh_settings()

    assert save_help_scale(125, settings=settings) == 125
    assert settings.value(HELP_UI_SCALE_KEY, type=int) == 125

    fresh_read = QSettings("AbCS", "AudioBookCollector")
    assert fresh_read.value(HELP_UI_SCALE_KEY, type=int) == 125


def test_read_saved_help_scale_handles_int_string(isolated_qsettings):
    settings = _fresh_settings()
    settings.setValue(HELP_UI_SCALE_KEY, "150")
    settings.sync()
    assert resolve_initial_help_scale(_ScalerStub(100), settings=settings) == 150


def test_help_preset_name_matches_uiscaler_presets():
    assert help_preset_name(100) == "Normal"
    assert help_preset_name(150) == "Extra Large"
    assert help_preset_name(123) == "Custom"
