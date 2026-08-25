"""
ID3 Tag reader for audio files.
Extracts metadata from audio files using mutagen library.
"""

import io
import os
import re
import zipfile
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable, Tuple
from mutagen import File as MutagenFile
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4
from mutagen.oggvorbis import OggVorbis


class AudioFileInfo:
    """Information extracted from an audio file."""

    def __init__(self):
        self.album: str = ""  # Book title
        self.artist: str = ""
        self.album_artist: str = ""  # Primary author field
        self.year: Optional[int] = None
        self.genre: str = ""
        self.comment: str = ""
        self.composer: str = ""  # Sometimes contains narrator
        self.duration_seconds: float = 0.0
        self.bitrate: int = 0
        self.file_size_bytes: int = 0
        self.file_format: str = ""
        self.file_path: str = ""
        self.read_error: Optional[str] = None
        self.embedded_zip_detected: bool = False
        self.outer_duration_seconds: float = 0.0
        self.embedded_zip_track_count: int = 0


class TagReader:
    """
    Reads ID3 tags and metadata from audio files.
    Supports MP3, FLAC, M4A/M4B, OGG, and other formats.
    """

    # Supported audio extensions
    SUPPORTED_EXTENSIONS = {
        ".mp3",
        ".m4a",
        ".m4b",
        ".flac",
        ".ogg",
        ".oga",
        ".wma",
        ".wav",
        ".aac",
        ".opus",
    }

    def __init__(self):
        """Initialize tag reader."""
        pass

    @staticmethod
    def _normalize_reader_keywords(reader_keywords: Optional[List[str]]) -> List[str]:
        keywords = []
        for keyword in reader_keywords or []:
            normalized = " ".join(str(keyword or "").strip().lower().split())
            if normalized and normalized not in keywords:
                keywords.append(normalized)
        return sorted(keywords, key=len, reverse=True)

    @staticmethod
    def split_comment_blocks(comment: str) -> List[str]:
        blocks = []
        for part in re.split(r"(?:\r?\n)+|\s\|\s", str(comment or "")):
            text = " ".join(part.strip().split())
            if text:
                blocks.append(text)
        return blocks

    @classmethod
    def extract_reader_from_comment_text(
        cls, comment: str, reader_keywords: Optional[List[str]] = None
    ) -> str:
        for block in cls.split_comment_blocks(comment):
            lowered = block.lower()
            for keyword in cls._normalize_reader_keywords(reader_keywords):
                match = re.search(
                    rf"(?:^|\b){re.escape(keyword)}(?:\b)?\s*(?:[:\-]\s*)?(.+)$",
                    lowered,
                )
                if match:
                    start_idx = match.start(1)
                    value = block[start_idx:].strip(" .:-")
                    if value:
                        return value
        return ""

    @classmethod
    def is_reader_only_comment(
        cls, comment: str, reader_keywords: Optional[List[str]] = None
    ) -> bool:
        text = " ".join(str(comment or "").strip().split())
        if not text:
            return False
        lowered = text.lower()
        for keyword in cls._normalize_reader_keywords(reader_keywords):
            if re.fullmatch(
                rf"{re.escape(keyword)}\s*(?::|\-|\s)\s*.+",
                lowered,
            ):
                return True
        return False

    @staticmethod
    def format_accumulated_comments(comments: List[str]) -> str:
        formatted_comments = []
        for comment in comments:
            text = " ".join(str(comment or "").strip().split())
            if text:
                formatted_comments.append(text)
        return "; ".join(formatted_comments)

    def is_supported_file(self, file_path: str) -> bool:
        """
        Check if file is a supported audio format.

        Args:
            file_path: Path to file

        Returns:
            True if supported
        """
        ext = Path(file_path).suffix.lower()
        return ext in self.SUPPORTED_EXTENSIONS

    def read_file(self, file_path: str) -> AudioFileInfo:
        """
        Read metadata from an audio file.

        Args:
            file_path: Path to audio file

        Returns:
            AudioFileInfo object
        """
        info = AudioFileInfo()
        info.file_path = file_path

        try:
            # Get file size
            info.file_size_bytes = os.path.getsize(file_path)

            # Detect file format
            info.file_format = Path(file_path).suffix.lstrip(".").upper()

            # Load file with mutagen
            audio = MutagenFile(file_path)

            if audio is None:
                info.read_error = "Unrecognized audio format"
                return info

            # Get duration
            if hasattr(audio.info, "length"):
                info.duration_seconds = audio.info.length

            # Get bitrate
            if hasattr(audio.info, "bitrate"):
                info.bitrate = audio.info.bitrate // 1000  # Convert to kbps

            # Extract tags based on file type
            if isinstance(audio, MP3):
                self._read_mp3_tags(audio, info)
            elif isinstance(audio, FLAC):
                self._read_flac_tags(audio, info)
            elif isinstance(audio, MP4):
                self._read_mp4_tags(audio, info)
            elif isinstance(audio, OggVorbis):
                self._read_ogg_tags(audio, info)
            else:
                # Try generic tag reading
                self._read_generic_tags(audio, info)

            if isinstance(audio, MP3):
                self._maybe_correct_embedded_zip_duration(info)

        except Exception as e:
            info.read_error = f"Error reading file: {str(e)}"

        return info

    @staticmethod
    def _mp3_id3_end_offset(header: bytes) -> int:
        """Return byte offset where MP3 audio (or payload) begins after an ID3v2 tag."""
        if len(header) < 10 or header[:3] != b"ID3":
            return 0
        tag_size = (
            ((header[6] & 0x7F) << 21)
            | ((header[7] & 0x7F) << 14)
            | ((header[8] & 0x7F) << 7)
            | (header[9] & 0x7F)
        )
        return 10 + tag_size

    def _find_embedded_zip_offset(self, file_path: str) -> Optional[int]:
        """Return offset of a ZIP archive embedded immediately after an ID3 tag."""
        try:
            with open(file_path, "rb") as handle:
                header = handle.read(10)
                if header[:3] != b"ID3":
                    return None
                id3_end = self._mp3_id3_end_offset(header)
                handle.seek(id3_end)
                signature = handle.read(4)
            if signature != b"PK\x03\x04":
                return None
            return id3_end
        except OSError:
            return None

    @staticmethod
    def _embedded_zip_audio_extensions() -> Tuple[str, ...]:
        return (".mp3", ".m4a", ".m4b", ".flac", ".ogg", ".oga", ".opus", ".wma")

    def _duration_from_audio_bytes(self, blob: bytes) -> float:
        """Read duration from in-memory audio bytes."""
        if not blob:
            return 0.0
        try:
            audio = MutagenFile(io.BytesIO(blob))
            if audio is not None and hasattr(audio.info, "length"):
                length = float(audio.info.length)
                if length > 0:
                    return length
        except Exception:
            pass
        return 0.0

    def _duration_from_embedded_zip(
        self, file_path: str, zip_offset: int, bitrate_kbps: int
    ) -> Tuple[float, int]:
        """Sum duration of audio files stored inside an embedded ZIP payload."""
        total_duration = 0.0
        track_count = 0
        audio_extensions = self._embedded_zip_audio_extensions()

        try:
            with open(file_path, "rb") as handle:
                handle.seek(zip_offset)
                zip_data = handle.read()
            archive = zipfile.ZipFile(io.BytesIO(zip_data))
        except (OSError, zipfile.BadZipFile):
            return 0.0, 0

        for entry_name in archive.namelist():
            if not entry_name.lower().endswith(audio_extensions):
                continue
            track_count += 1
            try:
                blob = archive.read(entry_name)
            except (KeyError, OSError, zipfile.BadZipFile):
                continue

            inner_duration = self._duration_from_audio_bytes(blob)
            if inner_duration > 0:
                total_duration += inner_duration
            elif bitrate_kbps > 0:
                total_duration += (len(blob) * 8) / (bitrate_kbps * 1000)

        return total_duration, track_count

    def _maybe_correct_embedded_zip_duration(self, info: AudioFileInfo) -> None:
        """Detect ZIP-in-MP3 containers and replace stub duration with inner audio."""
        if info.file_format != "MP3" or not info.file_path:
            return

        zip_offset = self._find_embedded_zip_offset(info.file_path)
        if zip_offset is None:
            return

        outer_duration = float(info.duration_seconds or 0.0)
        inner_duration, inner_count = self._duration_from_embedded_zip(
            info.file_path,
            zip_offset,
            int(info.bitrate or 0),
        )
        if inner_count <= 0 or inner_duration <= 0:
            return

        # Ignore coincidental PK signatures unless inner audio is much longer.
        if inner_duration < max(60.0, outer_duration * 2.0):
            return

        info.embedded_zip_detected = True
        info.outer_duration_seconds = outer_duration
        info.embedded_zip_track_count = inner_count
        info.duration_seconds = inner_duration

    def _read_mp3_tags(self, audio: MP3, info: AudioFileInfo):
        """Read tags from MP3 file."""
        if audio.tags:
            # Album (book title)
            if "TALB" in audio.tags:
                info.album = str(audio.tags["TALB"])

            # Album Artist (primary author)
            if "TPE2" in audio.tags:
                info.album_artist = str(audio.tags["TPE2"])

            # Artist (fallback author)
            if "TPE1" in audio.tags:
                info.artist = str(audio.tags["TPE1"])

            # Title
            # Parsed title tag is intentionally not stored separately;
            # import flow uses album/title aggregation at book level.

            # Year
            if "TDRC" in audio.tags:
                try:
                    year_str = str(audio.tags["TDRC"])
                    info.year = int(year_str[:4])
                except (ValueError, IndexError):
                    pass

            # Genre
            if "TCON" in audio.tags:
                info.genre = str(audio.tags["TCON"])

            # Comment
            comment_frames = [
                frame
                for key, frame in audio.tags.items()
                if str(key).upper().startswith("COMM")
            ]
            if comment_frames:
                unique_comments = []
                for comment in comment_frames:
                    for value in getattr(comment, "text", []) or []:
                        text = str(value).strip()
                        if text and text not in unique_comments:
                            unique_comments.append(text)
                unique_comments = [
                    text
                    for text in unique_comments
                    if not any(
                        other != text
                        and len(other) > len(text)
                        and other.casefold().startswith(text.casefold())
                        for other in unique_comments
                    )
                ]
                info.comment = "\n\n".join(unique_comments)

            # Composer (narrator)
            if "TCOM" in audio.tags:
                info.composer = str(audio.tags["TCOM"])

            # Track number parsing intentionally omitted (not used downstream).

    def _read_flac_tags(self, audio: FLAC, info: AudioFileInfo):
        """Read tags from FLAC file."""
        if audio.tags:
            info.album = self._get_tag(audio, "album")
            info.album_artist = self._get_tag(audio, "albumartist")
            info.artist = self._get_tag(audio, "artist")
            # Title tag is not used downstream.
            info.genre = self._get_tag(audio, "genre")
            info.comment = self._get_tags_joined(audio, "comment")
            info.composer = self._get_tag(audio, "composer")

            # Year
            date_str = self._get_tag(audio, "date")
            if date_str:
                try:
                    info.year = int(date_str[:4])
                except (ValueError, IndexError):
                    pass

            # Track number parsing intentionally omitted (not used downstream).

    def _read_mp4_tags(self, audio: MP4, info: AudioFileInfo):
        """Read tags from M4A/M4B file."""
        if audio.tags:
            info.album = self._get_mp4_tag(audio, "©alb")
            info.album_artist = self._get_mp4_tag(audio, "aART")
            info.artist = self._get_mp4_tag(audio, "©ART")
            # Title tag is not used downstream.
            info.genre = self._get_mp4_tag(audio, "©gen")
            info.comment = self._get_mp4_tags_joined(audio, "©cmt")
            info.composer = self._get_mp4_tag(audio, "©wrt")

            # Year
            year_str = self._get_mp4_tag(audio, "©day")
            if year_str:
                try:
                    info.year = int(year_str[:4])
                except (ValueError, IndexError):
                    pass

            # Track number parsing intentionally omitted (not used downstream).

    def _read_ogg_tags(self, audio: OggVorbis, info: AudioFileInfo):
        """Read tags from OGG file."""
        # OGG uses similar tags to FLAC
        self._read_flac_tags(audio, info)

    def _read_generic_tags(self, audio, info: AudioFileInfo):
        """Try to read tags generically."""
        if hasattr(audio, "tags") and audio.tags:
            info.album = self._get_any_tag(
                audio,
                ["album", "ALBUM", "TALB", "WM/AlbumTitle"],
            )
            info.album_artist = self._get_any_tag(
                audio,
                ["albumartist", "album artist", "ALBUMARTIST", "TPE2", "WM/AlbumArtist"],
            )
            info.artist = self._get_any_tag(
                audio,
                ["artist", "ARTIST", "TPE1", "Author", "WM/Author"],
            )
            info.genre = self._get_any_tag(
                audio,
                ["genre", "GENRE", "TCON", "WM/Genre"],
            )
            info.comment = self._get_any_tags_joined(
                audio,
                ["comment", "COMMENT", "description", "COMM", "Description"],
            )
            info.composer = self._get_any_tag(
                audio,
                ["composer", "COMPOSER", "TCOM", "WM/Composer"],
            )

            year_str = self._get_any_tag(
                audio,
                ["date", "year", "DATE", "YEAR", "TDRC", "TYER", "WM/Year"],
            )
            if year_str:
                try:
                    info.year = int(str(year_str)[:4])
                except (ValueError, IndexError):
                    pass

    def _tag_to_text_values(self, value) -> List[str]:
        if isinstance(value, list):
            raw_values = value
        else:
            raw_values = [value]

        values = []
        for raw_value in raw_values:
            frame_text = getattr(raw_value, "text", None)
            if frame_text is not None:
                if isinstance(frame_text, list):
                    values.extend(str(item).strip() for item in frame_text)
                else:
                    values.append(str(frame_text).strip())
            else:
                values.append(str(raw_value).strip())
        return [value for value in values if value]

    def _get_any_tag(self, audio, tag_names: List[str]) -> str:
        for tag_name in tag_names:
            if tag_name in audio.tags:
                values = self._tag_to_text_values(audio.tags[tag_name])
                if values:
                    return values[0]
        return ""

    def _get_any_tags_joined(self, audio, tag_names: List[str]) -> str:
        unique_values = []
        for key, value in audio.tags.items():
            key_text = str(key)
            if key_text not in tag_names and not any(
                key_text.upper().startswith(tag_name.upper()) for tag_name in tag_names
            ):
                continue
            for text in self._tag_to_text_values(value):
                if text and text not in unique_values:
                    unique_values.append(text)
        return "\n\n".join(unique_values)

    def _get_tag(self, audio, tag_name: str) -> str:
        """Get tag value from FLAC/OGG."""
        if tag_name in audio:
            values = audio[tag_name]
            if values:
                return str(values[0])
        return ""

    def _get_tags_joined(self, audio, tag_name: str) -> str:
        if tag_name in audio:
            values = audio[tag_name]
            unique_values = []
            for value in values:
                text = str(value).strip()
                if text and text not in unique_values:
                    unique_values.append(text)
            return "\n\n".join(unique_values)
        return ""

    def _get_mp4_tag(self, audio: MP4, tag_name: str) -> str:
        """Get tag value from MP4."""
        if tag_name in audio.tags:
            values = audio.tags[tag_name]
            if values:
                return str(values[0])
        return ""

    def _get_mp4_tags_joined(self, audio: MP4, tag_name: str) -> str:
        if tag_name in audio.tags:
            values = audio.tags[tag_name]
            unique_values = []
            for value in values:
                text = str(value).strip()
                if text and text not in unique_values:
                    unique_values.append(text)
            return "\n\n".join(unique_values)
        return ""

    def extract_narrator(
        self, comment: str, composer: str, reader_keywords: Optional[List[str]] = None
    ) -> str:
        """
        Extract narrator from comment or composer field.
        Looks for patterns like "Read by John Doe" or "Narrated by Jane Smith".

        Args:
            comment: Comment field text
            composer: Composer field text

        Returns:
            Narrator name or empty string
        """
        # First check composer (often has narrator)
        if composer:
            return composer

        narrator = self.extract_reader_from_comment_text(comment, reader_keywords)
        if narrator:
            return narrator

        return ""


class BookScanner:
    """
    Scans folders for audiobook files and groups them by book.
    """

    def __init__(self):
        """Initialize book scanner."""
        self.tag_reader = TagReader()

    @staticmethod
    def _append_embedded_zip_flags(book: Dict[str, Any]) -> None:
        """Add import correction flag when ZIP-in-MP3 duration was used."""
        embedded_count = int(book.pop("_embedded_zip_file_count", 0) or 0)
        if embedded_count <= 0:
            return

        from src.core.validator import ImportValidator

        ImportValidator.append_flag_once(
            book,
            "C: Duration corrected from embedded ZIP audio",
        )

    def scan_folder(
        self,
        folder_path: str,
        include_subfolders: bool = True,
        allowed_extensions: Optional[set] = None,
        reader_keywords: Optional[List[str]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        cancel_check: Optional[Callable[[], bool]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Scan folder recursively for audiobooks.
        Groups files by album (book title).

        Args:
            folder_path: Root folder to scan
            include_subfolders: True to scan subfolders
            allowed_extensions: Optional set of lowercase extensions (with dot)
            progress_callback: Optional callback(processed, total, file_path)
            cancel_check: Optional callback that returns True to stop early

        Returns:
            List of book dictionaries
        """
        # Check if path is a single file (for single-item mode)
        if os.path.isfile(folder_path):
            return self.scan_file(
                folder_path,
                allowed_extensions=allowed_extensions,
                reader_keywords=reader_keywords,
                progress_callback=progress_callback,
                cancel_check=cancel_check,
            )

        # Find all audio files
        audio_files = []
        if not folder_path or not os.path.isdir(folder_path):
            return []

        def is_allowed(file_path: str) -> bool:
            ext = Path(file_path).suffix.lower()
            if allowed_extensions is not None:
                return ext in allowed_extensions
            return self.tag_reader.is_supported_file(file_path)

        seen_files = set()

        def add_audio_file(file_path: str):
            normalized_path = os.path.normcase(os.path.abspath(file_path))
            if normalized_path in seen_files:
                return
            seen_files.add(normalized_path)
            audio_files.append(file_path)

        if include_subfolders:
            for root, _dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if is_allowed(file_path):
                        add_audio_file(file_path)
        else:
            for entry in os.scandir(folder_path):
                if entry.is_file():
                    if is_allowed(entry.path):
                        add_audio_file(entry.path)

        # Group by album (book)
        books = {}

        total_files = len(audio_files)

        for index, file_path in enumerate(audio_files, start=1):
            if cancel_check is not None and cancel_check():
                break

            if progress_callback is not None:
                progress_callback(index, total_files, file_path)

            info = self.tag_reader.read_file(file_path)

            # Use album as book identifier
            book_key = info.album or os.path.basename(os.path.dirname(file_path))

            if book_key not in books:
                books[book_key] = {
                    "title": info.album,
                    "author": info.album_artist or info.artist,
                    "year": info.year,
                    "genre": info.genre,
                    "narrator": self.tag_reader.extract_narrator(
                        info.comment, info.composer, reader_keywords
                    ),
                    "comments": [],
                    "_comment_keys": set(),
                    "files": [],
                    "total_duration": 0.0,
                    "total_size": 0,
                    "bitrate": info.bitrate,
                    "format": info.file_format,
                    "folder": os.path.dirname(file_path),
                    "errors": [],
                }

            book = books[book_key]
            if not book.get("narrator"):
                narrator = self.tag_reader.extract_narrator(
                    info.comment, info.composer, reader_keywords
                )
                if narrator:
                    book["narrator"] = narrator

            # Accumulate data
            book["files"].append(file_path)
            book["total_duration"] += info.duration_seconds
            book["total_size"] += info.file_size_bytes

            for comment in self.tag_reader.split_comment_blocks(info.comment):
                if self.tag_reader.is_reader_only_comment(comment, reader_keywords):
                    continue
                normalized_comment = comment.casefold()
                if normalized_comment not in book["_comment_keys"]:
                    book["_comment_keys"].add(normalized_comment)
                    book["comments"].append(comment)

            # Collect errors
            if info.read_error:
                book["errors"].append(
                    f"{os.path.basename(file_path)}: {info.read_error}"
                )

            if info.embedded_zip_detected:
                book["_embedded_zip_file_count"] = (
                    int(book.get("_embedded_zip_file_count", 0) or 0) + 1
                )

        # Convert to list and finalize
        result = []
        for book in books.values():
            # Combine comments
            book["comment"] = self.tag_reader.format_accumulated_comments(
                book["comments"]
            )
            del book["comments"]
            del book["_comment_keys"]
            self._append_embedded_zip_flags(book)

            # Convert duration to hours/minutes
            total_minutes = int(book["total_duration"] / 60)
            book["time_hours"] = total_minutes // 60
            book["time_minutes"] = total_minutes % 60

            # Convert size to MB
            book["size_mb"] = book["total_size"] / (1024 * 1024)

            # Track count
            book["tracks"] = len(book["files"])

            result.append(book)

        return result

    def scan_file(
        self,
        file_path: str,
        allowed_extensions: Optional[set] = None,
        reader_keywords: Optional[List[str]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        cancel_check: Optional[Callable[[], bool]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Scan a single audio file.
        Used for single-item import mode.

        Args:
            file_path: Path to audio file
            progress_callback: Optional callback(processed, total, file_path)
            cancel_check: Optional callback that returns True to stop early

        Returns:
            List with single book dictionary
        """
        if not file_path or not os.path.isfile(file_path):
            return []

        file_ext = Path(file_path).suffix.lower()
        if allowed_extensions is not None:
            if file_ext not in allowed_extensions:
                return []
        elif not self.tag_reader.is_supported_file(file_path):
            return []

        if cancel_check is not None and cancel_check():
            return []

        if progress_callback is not None:
            progress_callback(1, 1, file_path)

        info = self.tag_reader.read_file(file_path)

        # Use filename without extension as book key
        file_name = os.path.basename(file_path)
        book_key = os.path.splitext(file_name)[0]

        # Build book dictionary
        book = {
            "title": info.album or book_key,
            "author": info.album_artist or info.artist,
            "year": info.year,
            "genre": info.genre,
            "narrator": self.tag_reader.extract_narrator(
                info.comment, info.composer, reader_keywords
            ),
            "comment": info.comment or "",
            "files": [file_path],
            "total_duration": info.duration_seconds,
            "total_size": info.file_size_bytes,
            "bitrate": info.bitrate,
            "format": info.file_format,
            "folder": os.path.dirname(file_path),
            "errors": [],
        }

        # Add error if present
        if info.read_error:
            book["errors"].append(f"{file_name}: {info.read_error}")

        if info.embedded_zip_detected:
            book["_embedded_zip_file_count"] = 1
        self._append_embedded_zip_flags(book)

        # Convert duration to hours/minutes
        total_minutes = int(book["total_duration"] / 60)
        book["time_hours"] = total_minutes // 60
        book["time_minutes"] = total_minutes % 60

        # Convert size to MB
        book["size_mb"] = book["total_size"] / (1024 * 1024)

        # Track count (always 1 for single file)
        book["tracks"] = 1

        return [book]
