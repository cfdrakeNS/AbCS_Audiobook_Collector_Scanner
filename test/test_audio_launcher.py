"""Phase 12: resolve and launch audiobook preview without opening a player."""

from __future__ import annotations

from pathlib import Path

from src.core.audio_launcher import (
    embedded_cover_bytes,
    preview_can_launch,
    read_embedded_cover,
    resolve_preview_file,
)


def test_embedded_cover_bytes_returns_art_or_none():
    class Picture:
        def __init__(self, data):
            self.data = data

    class WithArt:
        pictures = [Picture(b"jpeg-bytes")]

    class NoArt:
        pictures = []
        tags = None

    assert embedded_cover_bytes(WithArt()) == b"jpeg-bytes"
    assert embedded_cover_bytes(NoArt()) is None
    assert embedded_cover_bytes(None) is None


def test_read_embedded_cover_from_id3_and_plain_file(tmp_path):
    from mutagen.id3 import APIC, ID3

    art = tmp_path / "with-art.mp3"
    art.write_bytes(b"")
    tags = ID3()
    payload = b"\xff\xd8\xffcover"
    tags.add(APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=payload))
    tags.save(art)
    assert read_embedded_cover(art) == payload

    plain = tmp_path / "no-art.mp3"
    plain.write_bytes(b"no tags")
    assert read_embedded_cover(plain) is None


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


def test_parse_tag_number_and_sort_key(tmp_path):
    from src.core.audio_launcher import parse_tag_number, list_audio_in_folder

    assert parse_tag_number("4/24") == 4
    assert parse_tag_number(3) == 3
    assert parse_tag_number(None) is None

    folder = tmp_path / "tracks"
    folder.mkdir()
    late_name = folder / "10 Chapter.mp3"
    early_name = folder / "02 Chapter.mp3"
    late_name.write_bytes(b"x")
    early_name.write_bytes(b"x")
    from mutagen.id3 import ID3, TRCK

    tags = ID3()
    tags.add(TRCK(encoding=3, text=["10"]))
    tags.save(late_name)
    tags = ID3()
    tags.add(TRCK(encoding=3, text=["2"]))
    tags.save(early_name)

    ordered = list_audio_in_folder(folder)
    assert ordered == [early_name, late_name]


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


def test_resolve_preview_playlist_resumes_named_file(tmp_path):
    from src.core.audio_launcher import resolve_preview_playlist

    folder = tmp_path / "book"
    folder.mkdir()
    first = folder / "a.mp3"
    second = folder / "b.mp3"
    first.write_bytes(b"x")
    second.write_bytes(b"x")
    playlist = resolve_preview_playlist(str(folder), listen_file_name="b.mp3")
    assert playlist.folder_mode is True
    assert playlist.path == second
    assert playlist.start_index == 1


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
            self.mediaStatusChanged = DummySignal()
            self.positionChanged = DummySignal()
            self._state = 0
            self._position = 0
            self._duration = 0
            self._rate = 1.0

        def setAudioOutput(self, *_args):
            return None

        def setSource(self, *_args):
            return None

        def setPlaybackRate(self, rate):
            self._rate = rate

        def setPosition(self, position):
            self._position = position

        def position(self):
            return self._position

        def duration(self):
            return self._duration

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
    from PySide6.QtCore import Qt

    assert preview.title_label.text() == "Title: A Maiden's Grave"
    assert preview.author_label.text() == "Author: Jeffrey Deaver"
    assert preview.series_label.text() == "Series: Lincoln Rhyme - 01"
    assert preview.series_label.isVisible()
    assert preview.length_label.text() == "Length: 10:35"
    assert preview.play_pause_button.text() == ""
    assert preview.position_label.alignment() & int(Qt.AlignHCenter)
    assert hasattr(preview, "position_slider")
    assert preview.position_slider.accessibleName() == "Seek in current file"
    assert preview.cover_label.isHidden()
    assert preview.cover_label.focusPolicy() == Qt.NoFocus
    assert preview.part_label.isHidden()
    assert "cover" not in preview.status_bar.currentMessage().lower()
    if preview_mod._open_preview is not None:
        preview_mod._open_preview.close()
    ok, message = show_preview(None, "", ui_scaler, theme_manager)
    assert ok is False
    assert "No file path" in message


def test_preview_next_returns_focus_to_play_pause(
    tmp_path, ui_scaler, theme_manager, qtbot, monkeypatch
):
    from types import SimpleNamespace

    from PySide6.QtCore import Qt

    from src.ui.preview_window import PreviewWindow

    folder = tmp_path / "tracks"
    folder.mkdir()
    first = folder / "01.mp3"
    second = folder / "02.mp3"
    first.write_bytes(b"a")
    second.write_bytes(b"b")

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
            self.mediaStatusChanged = DummySignal()
            self.positionChanged = DummySignal()
            self.durationChanged = DummySignal()
            self._state = 0
            self._position = 0
            self._duration = 60_000
            self._rate = 1.0

        def setAudioOutput(self, *_args):
            return None

        def setSource(self, *_args):
            return None

        def setPlaybackRate(self, rate):
            self._rate = rate

        def setPosition(self, position):
            self._position = position

        def position(self):
            return self._position

        def duration(self):
            return self._duration

        def play(self):
            self._state = 1

        def pause(self):
            self._state = 2

        def stop(self):
            self._state = 0

        def playbackState(self):
            return self._state

    monkeypatch.setattr(
        "src.ui.preview_window.exec_styled_message_box",
        lambda *_args, **_kwargs: 0,
    )
    window = PreviewWindow(
        None,
        ui_scaler,
        theme_manager,
        player_types=(FakePlayer, FakeAudio),
    )
    qtbot.addWidget(window)
    window.show()
    ok, _message = window.play_playlist(
        SimpleNamespace(
            files=(first, second),
            start_index=0,
            folder_mode=True,
            error="",
        ),
        book_title="Focus Book",
    )
    assert ok is True
    window.next_button.setFocus(Qt.OtherFocusReason)
    assert window.focusWidget() is window.next_button
    window.on_next()
    # Status announce briefly focuses the status bar, then restores Play.
    qtbot.waitUntil(
        lambda: window.focusWidget() is window.play_pause_button,
        timeout=1500,
    )
    assert window._playlist_index == 1
    assert not window.next_button.isEnabled()
    assert window.previous_button.isEnabled()
    assert window.part_label.isVisible()
    assert window.part_label.text() == "Part 2 / 2"
    # Tab order: Previous -> Rewind -> Play -> Forward -> Next.
    assert window.previous_button.nextInFocusChain() is window.rewind_button
    assert window.rewind_button.nextInFocusChain() is window.play_pause_button
    assert window.play_pause_button.nextInFocusChain() is window.forward_button
    assert window.forward_button.nextInFocusChain() is window.next_button
    window.position_slider.setFocus(Qt.TabFocusReason)
    qtbot.wait(20)
    path = []
    for _ in range(8):
        fw = window.focusWidget()
        path.append(fw)
        window.focusNextChild()
    assert window.rewind_button in path
    assert window.forward_button in path
    assert window.previous_button in path
    # Next is disabled on the last file, so Tab skips it (expected).
    assert window.next_button not in path
    # Custom Tab path: Previous -> Rewind -> Play -> Forward.
    window.previous_button.setFocus(Qt.TabFocusReason)
    assert window._move_preview_focus(True) is True
    assert window.focusWidget() is window.rewind_button
    assert window._move_preview_focus(True) is True
    assert window.focusWidget() is window.play_pause_button
    assert window._move_preview_focus(True) is True
    assert window.focusWidget() is window.forward_button
    # Arrow keys also visit Rewind and Forward in the transport row.
    window.previous_button.setFocus(Qt.TabFocusReason)
    assert window._move_transport_focus(True) is True
    assert window.focusWidget() is window.rewind_button
    assert window._move_transport_focus(True) is True
    assert window.focusWidget() is window.play_pause_button
    assert window._move_transport_focus(True) is True
    assert window.focusWidget() is window.forward_button
    # Activating Rewind must restore focus to Rewind (not stay on status / Play).
    window.rewind_button.setFocus(Qt.TabFocusReason)
    window.on_rewind()
    qtbot.waitUntil(
        lambda: window.focusWidget() is window.rewind_button,
        timeout=1500,
    )
    window.position_slider.setEnabled(True)
    window.position_slider.setRange(0, 60_000)
    window.position_slider.setValue(15_000)
    window._on_slider_released()
    assert window._player.position() == 15_000
    window.close()
