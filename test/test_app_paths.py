"""Tests for cross-platform user data directory resolution."""

from pathlib import Path

from src import app_paths


def test_linux_frozen_uses_xdg_data_home(monkeypatch, tmp_path: Path):
    home = tmp_path / "home"
    home.mkdir()
    xdg = tmp_path / "xdg"
    xdg.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("XDG_DATA_HOME", str(xdg))
    monkeypatch.setattr(app_paths.sys, "platform", "linux")
    monkeypatch.setattr(app_paths.sys, "frozen", True, raising=False)

    assert app_paths.get_user_data_dir() == xdg / "AbCS"


def test_linux_frozen_default_share_dir(monkeypatch, tmp_path: Path):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    monkeypatch.setattr(app_paths.sys, "platform", "linux")
    monkeypatch.setattr(app_paths.sys, "frozen", True, raising=False)

    assert app_paths.get_user_data_dir() == home / ".local" / "share" / "AbCS"


def test_windows_frozen_uses_localappdata(monkeypatch, tmp_path: Path):
    local = tmp_path / "AppData" / "Local"
    local.mkdir(parents=True)
    monkeypatch.setenv("LOCALAPPDATA", str(local))
    monkeypatch.setattr(app_paths.sys, "platform", "win32")
    monkeypatch.setattr(app_paths.sys, "frozen", True, raising=False)

    assert app_paths.get_user_data_dir() == local / "AbCS"
