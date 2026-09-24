"""Phase 12: resolve and launch audiobook preview without opening a player."""

from __future__ import annotations

from pathlib import Path

from src.core.audio_launcher import preview_can_launch, resolve_preview_file


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


def test_resolve_preview_uses_collection_root_not_import_path(tmp_path):
    old_book = tmp_path / "old_drive" / "import" / "Jeffery Deaver" / "A Maiden's Grave"
    new_book = tmp_path / "portable" / "import" / "Jeffery Deaver" / "A Maiden's Grave"
    new_book.mkdir(parents=True)
    audio = new_book / "01 A Maiden's Grave.mp3"
    audio.write_bytes(b"x")
    found = resolve_preview_file(str(old_book), collection_root=str(new_book.parent.parent))
    assert found.path == audio
    assert found.error == ""


def test_resolve_preview_prefers_collection_root_when_both_exist(tmp_path):
    rel = Path("Author") / "Title"
    old_book = tmp_path / "old" / "lib" / rel
    new_book = tmp_path / "new" / "lib" / rel
    old_book.mkdir(parents=True)
    new_book.mkdir(parents=True)
    (old_book / "old.mp3").write_bytes(b"o")
    (new_book / "new.mp3").write_bytes(b"n")
    found = resolve_preview_file(str(old_book), collection_root=str(new_book.parent.parent))
    assert found.path == new_book / "new.mp3"


def test_resolve_preview_falls_back_to_stored_if_collection_copy_missing(tmp_path):
    old_book = tmp_path / "old" / "lib" / "Author" / "Title"
    new_root = tmp_path / "new" / "lib"
    old_book.mkdir(parents=True)
    new_root.mkdir(parents=True)
    audio = old_book / "track.mp3"
    audio.write_bytes(b"x")
    found = resolve_preview_file(str(old_book), collection_root=str(new_root))
    assert found.path == audio


def test_resolve_preview_missing_on_collection_root_reports_remapped_path(tmp_path):
    stored = tmp_path / "old" / "lib" / "Author" / "Title"
    new_root = tmp_path / "portable" / "lib"
    remapped = new_root / "Author" / "Title"
    found = resolve_preview_file(str(stored), collection_root=str(new_root))
    assert found.path is None
    assert found.error == f"Book not found in - {remapped}"


def test_show_preview_plays_inside_abcs(tmp_path, ui_scaler, theme_manager, qtbot, monkeypatch):
    from src.ui.preview_window import show_preview

    audio = tmp_path / "play.mp3"
    audio.write_bytes(b"x")
    played = []

    class DummySignal:
        def connect(self, *_args, **_kwargs):
            return None

    class FakeAudio:
        pass

    class FakePlayer:
        class PlaybackState:
            StoppedState = 0
            PlayingState = 1
            PausedState = 2

        def __init__(self):
            self.playbackStateChanged = DummySignal()
            self.errorOccurred = DummySignal()
            self._state = 0

        def setAudioOutput(self, *_args):
            return None

        def setSource(self, *_args):
            return None

        def play(self):
            self._state = 1
            played.append("play")

        def pause(self):
            self._state = 2

        def stop(self):
            self._state = 0

        def playbackState(self):
            return self._state

    monkeypatch.setattr("PySide6.QtMultimedia.QMediaPlayer", FakePlayer)
    monkeypatch.setattr("PySide6.QtMultimedia.QAudioOutput", FakeAudio)
    monkeypatch.setattr(
        "src.ui.preview_window.exec_styled_message_box",
        lambda *_args, **_kwargs: 0,
    )
    ok, message = show_preview(
        None,
        str(audio),
        ui_scaler,
        theme_manager,
        book_title="A Maiden's Grave",
        author_name="Jeffrey Deaver",
        series_name="Lincoln Rhyme",
        series_number="1",
        length_text="10:35",
    )
    assert ok is True
    assert message == "Playing. Press Escape to exit."
    assert played
    from src.ui import preview_window as preview_mod

    preview = preview_mod._open_preview
    assert preview is not None
    assert preview.title_label.text() == "Title: A Maiden's Grave"
    assert preview.author_label.text() == "Author: Jeffrey Deaver"
    assert preview.series_label.text() == "Series: Lincoln Rhyme - 01"
    assert preview.length_label.text() == "Length: 10:35"
    if preview_mod._open_preview is not None:
        preview_mod._open_preview.close()
    ok, message = show_preview(None, "", ui_scaler, theme_manager)
    assert ok is False
    assert "No file path" in message
