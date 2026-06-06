"""Tests for shared graphics path resolution."""

from pathlib import Path

from src.accessibility import graphics_paths


def test_resolve_graphics_path_finds_project_graphics(tmp_path: Path, monkeypatch):
    graphics_dir = tmp_path / "graphics"
    graphics_dir.mkdir()
    splash = graphics_dir / "abcs_app_splash.png"
    splash.write_bytes(b"png")

    monkeypatch.setattr(graphics_paths, "project_root", lambda: tmp_path)
    monkeypatch.setattr(graphics_paths, "bundle_base", lambda: tmp_path)

    assert graphics_paths.resolve_graphics_path("abcs_app_splash.png") == str(
        splash.resolve()
    )


def test_resolve_app_icon_path_prefers_png_on_linux(tmp_path: Path, monkeypatch):
    graphics_dir = tmp_path / "graphics"
    graphics_dir.mkdir()
    png = graphics_dir / "abcs_icon_256x256.png"
    ico = graphics_dir / "abcs_icon_256x256.ico"
    png.write_bytes(b"png")
    ico.write_bytes(b"ico")

    monkeypatch.setattr(graphics_paths, "project_root", lambda: tmp_path)
    monkeypatch.setattr(graphics_paths, "bundle_base", lambda: tmp_path)
    monkeypatch.setattr(graphics_paths.sys, "platform", "linux")

    assert graphics_paths.resolve_app_icon_path() == str(png.resolve())


def test_resolve_app_icon_path_prefers_ico_on_windows(tmp_path: Path, monkeypatch):
    graphics_dir = tmp_path / "graphics"
    graphics_dir.mkdir()
    png = graphics_dir / "abcs_icon_256x256.png"
    ico = graphics_dir / "abcs_icon_256x256.ico"
    png.write_bytes(b"png")
    ico.write_bytes(b"ico")

    monkeypatch.setattr(graphics_paths, "project_root", lambda: tmp_path)
    monkeypatch.setattr(graphics_paths, "bundle_base", lambda: tmp_path)
    monkeypatch.setattr(graphics_paths.sys, "platform", "win32")

    assert graphics_paths.resolve_app_icon_path() == str(ico.resolve())
