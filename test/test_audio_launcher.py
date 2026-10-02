"""Phase 12: resolve and launch audiobook preview without opening a player."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.core.audio_launcher import (
    embedded_cover_bytes,
    preview_can_launch,
    read_embedded_cover,
    resolve_preview_file,
    resolve_preview_source,
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
    assert resolve_preview_file("").error == (
        "This book has no file path and the collection folder is not set. "
        "To fix, open Manage > Collections, edit the collection, and set the "
        "Library root folder."
    )
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


def test_resolve_preview_source_skips_playlist_metadata_sort(tmp_path, monkeypatch):
    folder = tmp_path / "book"
    folder.mkdir()
    audio = folder / "chapter.mp3"
    audio.write_bytes(b"x")
    monkeypatch.setattr(
        "src.core.audio_launcher.audio_sort_key",
        lambda _path: pytest.fail("lightweight source lookup must not sort metadata"),
    )

    found = resolve_preview_source(str(folder))

    assert found.path == audio
    assert found.error == ""

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


def test_resolve_preview_uses_stored_when_both_exist(tmp_path):
    rel = Path("Author") / "Title"
    old_book = tmp_path / "old" / "lib" / rel
    new_book = tmp_path / "new" / "lib" / rel
    old_book.mkdir(parents=True)
    new_book.mkdir(parents=True)
    (old_book / "old.mp3").write_bytes(b"o")
    (new_book / "new.mp3").write_bytes(b"n")
    found = resolve_preview_file(str(old_book), collection_root=str(new_book.parent.parent))
    assert found.path == old_book / "old.mp3"


def test_resolve_preview_falls_back_to_stored_if_collection_copy_missing(tmp_path):
    old_book = tmp_path / "old" / "lib" / "Author" / "Title"
    new_root = tmp_path / "new" / "lib"
    old_book.mkdir(parents=True)
    new_root.mkdir(parents=True)
    audio = old_book / "track.mp3"
    audio.write_bytes(b"x")
    found = resolve_preview_file(str(old_book), collection_root=str(new_root))
    assert found.path == audio


def test_resolve_preview_falls_back_to_import_dir(tmp_path):
    stored = tmp_path / "gone_drive" / "lib" / "Author" / "Title"
    import_root = tmp_path / "prefs_import"
    book = import_root / "Author" / "Title"
    book.mkdir(parents=True)
    audio = book / "01.mp3"
    audio.write_bytes(b"x")
    found = resolve_preview_file(
        str(stored),
        collection_root=str(tmp_path / "empty_collection"),
        import_dir=str(import_root),
    )
    assert found.path == audio


def test_resolve_preview_prefers_collection_over_import_when_missing_stored(tmp_path):
    stored = tmp_path / "gone" / "lib" / "Author" / "Title"
    collection_root = tmp_path / "collection"
    import_root = tmp_path / "import"
    coll_book = collection_root / "Author" / "Title"
    imp_book = import_root / "Author" / "Title"
    coll_book.mkdir(parents=True)
    imp_book.mkdir(parents=True)
    (coll_book / "c.mp3").write_bytes(b"c")
    (imp_book / "i.mp3").write_bytes(b"i")
    found = resolve_preview_file(
        str(stored),
        collection_root=str(collection_root),
        import_dir=str(import_root),
    )
    assert found.path == coll_book / "c.mp3"


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
    assert preview.position_slider.focusPolicy() == Qt.StrongFocus
    assert preview.position_label.accessibleName() == "Seek position at 0:00"
    assert preview.cover_label.isVisible()
    assert preview.cover_label.accessibleName() == "No cover"
    assert not preview.cover_label.pixmap().isNull()
    assert preview.cover_label.focusPolicy() == Qt.NoFocus
    assert not hasattr(preview, "file_label")
    assert preview.part_label.isHidden()
    assert "cover" not in preview.status_bar.currentMessage().lower()
    if preview_mod._open_preview is not None:
        preview_mod._open_preview.close()
    ok, message = show_preview(None, "", ui_scaler, theme_manager)
    assert ok is False
    assert "collection folder is not set" in message


def test_listen_progress_uses_book_time_or_track_ordinal(tmp_path, monkeypatch):
    from types import SimpleNamespace

    from src.core.tag_reader import TagReader
    from src.ui.book_details import BookDetailsWindow

    tracks = tmp_path / "tracks"
    tracks.mkdir()
    for number in range(1, 11):
        (tracks / f"{number:02}.mp3").write_bytes(b"x")

    monkeypatch.setattr(
        TagReader,
        "read_file",
        lambda _reader, _path: SimpleNamespace(duration_seconds=6 * 60),
    )

    class PathEdit:
        def text(self):
            return str(tracks)

    window = SimpleNamespace(
        book=SimpleNamespace(
            listen_position_ms=3 * 60 * 1000,
            listen_file_name="02.mp3",
            time_hours=1,
            time_minutes=0,
        ),
        path_edit=PathEdit(),
        _preview_collection_root=lambda: "",
        _preview_import_dir=lambda: "",
        _preview_author_name=lambda: "",
        _preview_book_title=lambda: "",
        _preview_series_name=lambda: "",
    )
    assert BookDetailsWindow._format_listen_progress(window) == "15%"

    window.book.time_hours = 0
    window.book.time_minutes = 0
    assert BookDetailsWindow._format_listen_progress(window) == "20%"


def test_legacy_linux_player_keeps_gstreamer_fakesink(
    ui_scaler, theme_manager, qtbot, monkeypatch
):
    from src.ui import preview_window as preview_mod
    from src.ui.preview_window import PreviewWindow

    class DummySignal:
        def connect(self, *_args, **_kwargs):
            return None

    class FakePlayer:
        def __init__(self):
            self.playbackStateChanged = DummySignal()
            self.errorOccurred = DummySignal()
            self.mediaStatusChanged = DummySignal()
            self.positionChanged = DummySignal()
            self.durationChanged = DummySignal()
            self.video_output = None

        def setAudioOutput(self, *_args):
            return None

        def setVideoOutput(self, sink):
            self.video_output = sink

    monkeypatch.setattr(preview_mod.sys, "platform", "linux")
    monkeypatch.setattr(preview_mod, "_qt_version_tuple", lambda: (6, 3))
    window = PreviewWindow(
        None,
        ui_scaler,
        theme_manager,
        player_types=(FakePlayer, object),
    )
    qtbot.addWidget(window)
    assert window._video_sink is None
    assert window._player.video_output is None
    window.close()


def test_closing_listen_releases_player_and_audio(ui_scaler, theme_manager, qtbot):
    from src.ui.preview_window import PreviewWindow

    calls = []

    class Signal:
        def connect(self, *_args, **_kwargs):
            return None

        def disconnect(self):
            calls.append("disconnect")

    class FakePlayer:
        def __init__(self):
            self.playbackStateChanged = Signal()
            self.errorOccurred = Signal()
            self.mediaStatusChanged = Signal()
            self.positionChanged = Signal()
            self.durationChanged = Signal()

        def setAudioOutput(self, *_args):
            return None

        def setVideoOutput(self, *_args):
            return None

        def stop(self):
            calls.append("stop")

        def setSource(self, url):
            calls.append(("source", url.isEmpty()))

        def position(self):
            return 0

        def deleteLater(self):
            calls.append("player deleted")

    class FakeAudio:
        def deleteLater(self):
            calls.append("audio deleted")

    window = PreviewWindow(
        None,
        ui_scaler,
        theme_manager,
        player_types=(FakePlayer, FakeAudio),
    )
    qtbot.addWidget(window)
    window.show()
    window.close()

    assert window._player is None
    assert window._audio is None
    assert "stop" in calls
    assert ("source", True) in calls
    assert "player deleted" in calls
    assert "audio deleted" in calls


def test_escape_on_later_track_does_not_prompt_for_short_track_position(
    tmp_path, ui_scaler, theme_manager, qtbot, monkeypatch
):
    from types import SimpleNamespace

    from src.ui.preview_window import PreviewWindow

    tracks = (tmp_path / "01.mp3", tmp_path / "02.mp3")
    for track in tracks:
        track.write_bytes(b"x")

    class DummySignal:
        def connect(self, *_args, **_kwargs):
            return None

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
            self._position = 60_000
            self._state = self.PlaybackState.PlayingState

        def setAudioOutput(self, *_args):
            return None

        def setSource(self, *_args):
            return None

        def setPlaybackRate(self, *_args):
            return None

        def setPosition(self, *_args):
            return None

        def position(self):
            return self._position

        def duration(self):
            return 0

        def play(self):
            return None

        def pause(self):
            self._state = self.PlaybackState.PausedState

        def stop(self):
            self._state = self.PlaybackState.StoppedState

        def playbackState(self):
            return self._state

    prompts = []
    monkeypatch.setattr(
        "src.ui.preview_window.exec_styled_message_box",
        lambda *_args, **_kwargs: prompts.append(True),
    )
    window = PreviewWindow(
        None,
        ui_scaler,
        theme_manager,
        player_types=(FakePlayer, object),
    )
    qtbot.addWidget(window)
    ok, _message = window.play_playlist(
        SimpleNamespace(
            files=tracks,
            start_index=1,
            folder_mode=True,
            error="",
        )
    )
    assert ok
    window._player._position = 60_000
    window.request_close()
    assert prompts == []


def test_preview_next_returns_focus_to_play_pause(
    tmp_path, ui_scaler, theme_manager, qtbot, monkeypatch
):
    from types import SimpleNamespace

    from PySide6.QtCore import Qt
    from PySide6.QtGui import QAccessible

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
    window._on_duration_changed(60_000)
    window.next_button.setFocus(Qt.OtherFocusReason)
    assert window.focusWidget() is window.next_button
    window.on_next()
    # Status announce briefly focuses the status bar, then restores Play.
    qtbot.waitUntil(
        lambda: window.focusWidget() is window.play_pause_button,
        timeout=1500,
    )
    assert window._playlist_index == 1
    window._on_duration_changed(60_000)
    assert not hasattr(window, "file_label")
    assert not window.next_button.isEnabled()
    assert window.previous_button.isEnabled()
    assert window.part_label.isVisible()
    assert window.part_label.text() == "Part 2 / 2"
    # Tab order: Previous -> Rewind -> Play -> Forward -> Next.
    assert window.previous_button.nextInFocusChain() is window.rewind_button
    assert window.rewind_button.nextInFocusChain() is window.play_pause_button
    assert window.play_pause_button.nextInFocusChain() is window.forward_button
    assert window.forward_button.nextInFocusChain() is window.next_button
    assert window.position_label.focusPolicy() == Qt.StrongFocus
    assert window.position_slider.focusPolicy() == Qt.StrongFocus
    position_accessible = QAccessible.queryAccessibleInterface(window.position_label)
    assert position_accessible.role() == QAccessible.Role.StaticText
    assert position_accessible.valueInterface() is None
    window.position_label.setFocus(Qt.TabFocusReason)
    qtbot.wait(20)
    path = []
    for _ in range(8):
        fw = window.focusWidget()
        path.append(fw)
        window.focusNextChild()
    assert window.rewind_button in path
    assert window.forward_button in path
    assert window.previous_button in path
    assert window.position_label in path
    assert window.position_slider in path
    # Next is disabled on the last file, so Tab skips it (expected).
    assert window.next_button not in path
    window.position_label.setFocus(Qt.TabFocusReason)
    qtbot.keyClick(window.position_label, Qt.Key_Tab)
    assert window.focusWidget() is window.position_slider
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
    window.position_slider.setRange(0, 60)
    window.position_slider.setValue(15)
    window._on_slider_released()
    assert window._player.position() == 15_000
    assert window.position_label.accessibleName() == "Seek position at 0:15"
    window.position_label.setFocus(Qt.TabFocusReason)
    qtbot.keyClick(window.position_label, Qt.Key_Right)
    assert window._player.position() == 20_000
    assert window.position_label.accessibleName() == "Seek position at 0:20"
    window.position_slider.setFocus(Qt.TabFocusReason)
    qtbot.keyClick(window.position_slider, Qt.Key_Right)
    assert window._player.position() == 25_000
    assert window.position_label.accessibleName() == "Seek position at 0:25"
    slider_accessible = QAccessible.queryAccessibleInterface(window.position_slider)
    assert slider_accessible.role() == QAccessible.Role.Slider
    assert slider_accessible.text(QAccessible.Text.Name) == "Seek position at 0:25"
    assert slider_accessible.valueInterface().currentValue() == 25
    window.close()
