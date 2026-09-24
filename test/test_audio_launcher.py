"""Phase 12: resolve and launch audiobook preview without opening a player."""

from __future__ import annotations

from src.core.audio_launcher import (
    launch_preview,
    preview_can_launch,
    resolve_preview_file,
)


def test_resolve_preview_empty_and_missing(tmp_path):
    missing = tmp_path / "gone.mp3"
    assert resolve_preview_file("").error == "No file path is set."
    assert preview_can_launch("") is False
    target = resolve_preview_file(str(missing))
    assert target.path is None
    assert target.error == f"Book not found in - {missing}"


def test_resolve_preview_single_file_and_unsupported(tmp_path):
    audio = tmp_path / "book.m4b"
    audio.write_bytes(b"x")
    notes = tmp_path / "notes.txt"
    notes.write_text("no audio", encoding="utf-8")

    found = resolve_preview_file(str(audio))
    assert found.path == audio
    assert found.error == ""
    assert preview_can_launch(str(audio)) is True

    bad = resolve_preview_file(str(notes))
    assert bad.path is None
    assert "recognized audiobook" in bad.error


def test_resolve_preview_folder_first_file_then_nested(tmp_path):
    folder = tmp_path / "album"
    folder.mkdir()
    later = folder / "10 Chapter.mp3"
    earlier = folder / "02 Chapter.mp3"
    later.write_bytes(b"x")
    earlier.write_bytes(b"x")
    found = resolve_preview_file(str(folder))
    assert found.path == earlier

    nested_root = tmp_path / "book_folder"
    nested_root.mkdir()
    child = nested_root / "disc1"
    child.mkdir()
    nested = child / "track.flac"
    nested.write_bytes(b"x")
    nested_found = resolve_preview_file(str(nested_root))
    assert nested_found.path == nested

    empty = tmp_path / "empty"
    empty.mkdir()
    empty_found = resolve_preview_file(str(empty))
    assert empty_found.path is None
    assert "no recognized audiobook" in empty_found.error


def test_launch_preview_uses_open_helper(tmp_path, monkeypatch):
    audio = tmp_path / "play.mp3"
    audio.write_bytes(b"x")
    opened = []
    monkeypatch.setattr(
        "src.core.audio_launcher.open_preview_file",
        lambda path: opened.append(path),
    )
    ok, message = launch_preview(str(audio))
    assert ok is True
    assert opened == [audio]
    assert "play.mp3" in message

    ok, message = launch_preview("")
    assert ok is False
    assert "No file path" in message
