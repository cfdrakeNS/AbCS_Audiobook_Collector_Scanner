"""Unit tests for TagReader comment parsing and tag helper logic."""

import os
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.core.tag_reader import AudioFileInfo, TagReader


DEFAULT_KEYWORDS = ["narrator", "read by", "narrated by"]


@pytest.fixture
def reader() -> TagReader:
    return TagReader()


def test_is_supported_file_recognizes_common_extensions(reader):
    assert reader.is_supported_file(r"C:\books\title.m4b")
    assert reader.is_supported_file("/audio/chapter.flac")
    assert reader.is_supported_file("track.MP3")


def test_is_supported_file_rejects_non_audio(reader):
    assert not reader.is_supported_file("notes.txt")
    assert not reader.is_supported_file("cover.jpg")


def test_split_comment_blocks_on_newlines_and_pipes(reader):
    comment = "Plot summary here.\r\n\r\nRead by Jane Smith | Extra note"
    assert reader.split_comment_blocks(comment) == [
        "Plot summary here.",
        "Read by Jane Smith",
        "Extra note",
    ]


def test_normalize_reader_keywords_dedupes_and_orders_longest_first(reader):
    keywords = reader._normalize_reader_keywords(
        ["read by", "Narrator", "read by", "", "  narrated by  "]
    )
    assert keywords == ["narrated by", "narrator", "read by"]


def test_extract_reader_from_comment_read_by_colon(reader):
    comment = "A long plot.\nRead by: John Smith"
    assert reader.extract_reader_from_comment_text(comment, DEFAULT_KEYWORDS) == (
        "John Smith"
    )


def test_extract_reader_from_comment_narrated_by_dash(reader):
    comment = "Narrated by - Mary Jones"
    assert reader.extract_reader_from_comment_text(comment, DEFAULT_KEYWORDS) == (
        "Mary Jones"
    )


def test_extract_reader_from_comment_skips_blocks_without_keyword(reader):
    comment = "Only plot text with no reader label."
    assert reader.extract_reader_from_comment_text(comment, DEFAULT_KEYWORDS) == ""


def test_is_reader_only_comment_true_for_labeled_reader_line(reader):
    assert reader.is_reader_only_comment("Read by: Alice Example", DEFAULT_KEYWORDS)


def test_is_reader_only_comment_false_for_plot_text(reader):
    assert not reader.is_reader_only_comment(
        "This is a plot summary with many sentences.", DEFAULT_KEYWORDS
    )


def test_format_accumulated_comments_joins_non_empty_lines(reader):
    comments = ["First note", "  ", "Second note"]
    assert reader.format_accumulated_comments(comments) == "First note; Second note"


def test_extract_narrator_prefers_composer(reader):
    narrator = reader.extract_narrator(
        comment="Read by: Should Not Win",
        composer="Composer Narrator",
        reader_keywords=DEFAULT_KEYWORDS,
    )
    assert narrator == "Composer Narrator"


def test_extract_narrator_falls_back_to_comment(reader):
    narrator = reader.extract_narrator(
        comment="Narrator: Comment Winner",
        composer="",
        reader_keywords=DEFAULT_KEYWORDS,
    )
    assert narrator == "Comment Winner"


def test_tag_to_text_values_handles_frame_text_list(reader):
    frame = SimpleNamespace(text=["Line one", "Line two"])
    assert reader._tag_to_text_values(frame) == ["Line one", "Line two"]


def test_get_any_tag_returns_first_matching_value(reader):
    audio = SimpleNamespace(tags={"album": ["Book Title"], "ALBUM": ["Other"]})
    assert reader._get_any_tag(audio, ["album", "ALBUM"]) == "Book Title"


def test_get_any_tags_joined_deduplicates_comment_values(reader):
    audio = SimpleNamespace(
        tags={
            "comment": ["Plot part one", "Plot part two"],
            "COMM:eng": ["Plot part one"],
        }
    )
    joined = reader._get_any_tags_joined(audio, ["comment", "COMM"])
    assert joined == "Plot part one\n\nPlot part two"


def test_read_file_sets_error_when_mutagen_returns_none(reader, tmp_path, monkeypatch):
    audio_path = tmp_path / "chapter.mp3"
    audio_path.write_bytes(b"not-a-real-mp3")
    monkeypatch.setattr("src.core.tag_reader.MutagenFile", lambda _path: None)

    info = reader.read_file(str(audio_path))

    assert info.read_error == "Unrecognized audio format"
    assert info.file_format == "MP3"
    assert info.file_size_bytes == audio_path.stat().st_size


def test_read_file_delegates_to_mp3_reader(reader, tmp_path, monkeypatch):
    audio_path = tmp_path / "book.mp3"
    audio_path.write_bytes(b"stub")

    fake_audio = MagicMock()
    fake_audio.info = SimpleNamespace(length=125.5, bitrate=192000)

    def _load(_path):
        return fake_audio

    monkeypatch.setattr("src.core.tag_reader.MutagenFile", _load)
    monkeypatch.setattr("src.core.tag_reader.MP3", type(fake_audio))
    monkeypatch.setattr(
        reader,
        "_read_mp3_tags",
        lambda audio, info: (
            info.__setattr__("album", "Tagged Album")
            or info.__setattr__("album_artist", "Tagged Author")
            or info.__setattr__("year", 2019)
        ),
    )

    info = reader.read_file(str(audio_path))

    assert isinstance(info, AudioFileInfo)
    assert info.read_error is None
    assert info.album == "Tagged Album"
    assert info.album_artist == "Tagged Author"
    assert info.year == 2019
    assert info.duration_seconds == 125.5
    assert info.bitrate == 192


def _synchsafe_size(size: int) -> bytes:
    return bytes(
        [
            (size >> 21) & 0x7F,
            (size >> 14) & 0x7F,
            (size >> 7) & 0x7F,
            size & 0x7F,
        ]
    )


def _make_id3_header(body_size: int = 0) -> bytes:
    return b"ID3\x03\x00\x00" + _synchsafe_size(body_size)


def test_mp3_id3_end_offset_empty_tag(reader):
    header = _make_id3_header(0)
    assert reader._mp3_id3_end_offset(header) == 10


def test_find_embedded_zip_offset_after_id3(reader, tmp_path):
    import io
    import zipfile

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as archive:
        archive.writestr("chapter.mp3", b"not-real-mp3")
    zip_bytes = zip_buffer.getvalue()

    path = tmp_path / "container.mp3"
    path.write_bytes(_make_id3_header(0) + zip_bytes)

    assert reader._find_embedded_zip_offset(str(path)) == 10


def test_maybe_correct_embedded_zip_duration_ignores_small_inner(reader, tmp_path):
    path = tmp_path / "container.mp3"
    path.write_bytes(_make_id3_header(0) + b"PK\x03\x04")

    info = AudioFileInfo()
    info.file_path = str(path)
    info.file_format = "MP3"
    info.duration_seconds = 12.0
    info.bitrate = 64

    reader._maybe_correct_embedded_zip_duration(info)

    assert not info.embedded_zip_detected
    assert info.duration_seconds == 12.0


def test_maybe_correct_embedded_zip_duration_applies(reader, tmp_path, monkeypatch):
    path = tmp_path / "container.mp3"
    path.write_bytes(_make_id3_header(0) + b"PK\x03\x04")

    monkeypatch.setattr(reader, "_find_embedded_zip_offset", lambda _path: 10)
    monkeypatch.setattr(
        reader,
        "_duration_from_embedded_zip",
        lambda _path, _offset, _bitrate: (7200.0, 12),
    )

    info = AudioFileInfo()
    info.file_path = str(path)
    info.file_format = "MP3"
    info.duration_seconds = 10.0
    info.bitrate = 64

    reader._maybe_correct_embedded_zip_duration(info)

    assert info.embedded_zip_detected
    assert info.duration_seconds == 7200.0
    assert info.outer_duration_seconds == 10.0
    assert info.embedded_zip_track_count == 12


def test_book_scanner_adds_embedded_zip_flags(tmp_path, monkeypatch):
    from src.core.tag_reader import BookScanner

    folder = tmp_path / "book"
    folder.mkdir()
    first = folder / "01.mp3"
    second = folder / "02.mp3"
    first.write_bytes(b"stub")
    second.write_bytes(b"stub")

    def _fake_read(file_path: str) -> AudioFileInfo:
        info = AudioFileInfo()
        info.file_path = file_path
        info.album = "Sample Book"
        info.file_format = "MP3"
        info.duration_seconds = 3600.0
        info.bitrate = 64
        info.embedded_zip_detected = True
        info.embedded_zip_track_count = 5
        return info

    scanner = BookScanner()
    monkeypatch.setattr(scanner.tag_reader, "read_file", _fake_read)

    books = scanner.scan_folder(str(folder), include_subfolders=False)

    assert len(books) == 1
    book = books[0]
    assert book["time_hours"] == 2
    assert book["time_minutes"] == 0
    assert any("Duration corrected from embedded ZIP audio" in err for err in book["errors"])
    assert not any(str(err).strip().upper().startswith("W:") for err in book["errors"])


@pytest.mark.skipif(
    not os.path.exists(r"E:\test standard import\Dean Koontz\Whispers"),
    reason="Whispers sample folder not available",
)
def test_whispers_embedded_zip_duration_correction():
    from src.core.tag_reader import BookScanner

    folder = r"E:\test standard import\Dean Koontz\Whispers"
    books = BookScanner().scan_folder(folder, include_subfolders=False)

    assert len(books) == 1
    book = books[0]
    total_minutes = (book["time_hours"] * 60) + book["time_minutes"]
    assert total_minutes >= 1000
    assert any("Duration corrected from embedded ZIP audio" in err for err in book.get("errors", []))
