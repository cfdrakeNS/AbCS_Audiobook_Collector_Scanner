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

    assert app_paths.get_user_data_dir(migrate_legacy=False) == xdg / "AbCS"


def test_linux_frozen_default_share_dir(monkeypatch, tmp_path: Path):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    monkeypatch.setattr(app_paths.sys, "platform", "linux")
    monkeypatch.setattr(app_paths.sys, "frozen", True, raising=False)

    assert app_paths.get_user_data_dir(migrate_legacy=False) == home / ".local" / "share" / "AbCS"


def test_windows_frozen_uses_localappdata(monkeypatch, tmp_path: Path):
    local = tmp_path / "AppData" / "Local"
    local.mkdir(parents=True)
    monkeypatch.setenv("LOCALAPPDATA", str(local))
    monkeypatch.setattr(app_paths.sys, "platform", "win32")
    monkeypatch.setattr(app_paths.sys, "frozen", True, raising=False)

    assert app_paths.get_user_data_dir(migrate_legacy=False) == local / "AbCS"


def test_migrates_legacy_linux_appdata_dir(monkeypatch, tmp_path: Path):
    home = tmp_path / "home"
    home.mkdir()
    legacy = home / "AppData" / "Local" / "AbCS"
    legacy.mkdir(parents=True)
    (legacy / "abcs.db").write_bytes(b"db")
    (legacy / ".bundled_first_run_complete").write_text("1", encoding="utf-8")

    monkeypatch.setenv("HOME", str(home))
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    monkeypatch.setattr(app_paths.sys, "platform", "linux")
    monkeypatch.setattr(app_paths.sys, "frozen", True, raising=False)

    target = app_paths.get_user_data_dir()
    assert target == home / ".local" / "share" / "AbCS"
    assert (target / "abcs.db").read_bytes() == b"db"
    assert (target / ".migrated_from_windows_style_path").exists()
