"""
ID3 Tag reader for audio files.
Extracts metadata from audio files using mutagen library.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from mutagen import File as MutagenFile
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4
from mutagen.oggvorbis import OggVorbis


class AudioFileInfo:
    """Information extracted from an audio file."""

    def __init__(self):
        self.title: str = ""
        self.album: str = ""  # Book title
        self.artist: str = ""
        self.album_artist: str = ""  # Primary author field
        self.year: Optional[int] = None
        self.genre: str = ""
        self.comment: str = ""
        self.composer: str = ""  # Sometimes contains narrator
        self.track_number: Optional[int] = None
        self.total_tracks: Optional[int] = None
        self.duration_seconds: float = 0.0
        self.bitrate: int = 0
        self.file_size_bytes: int = 0
        self.file_format: str = ""
        self.file_path: str = ""
        self.read_error: Optional[str] = None


class TagReader:
    """
    Reads ID3 tags and metadata from audio files.
    Supports MP3, FLAC, M4A/M4B, OGG, and other formats.
    """

    # Supported audio extensions
    SUPPORTED_EXTENSIONS = {
        '.mp3', '.m4a', '.m4b', '.flac', '.ogg', '.oga',
        '.wma', '.wav', '.aac', '.opus'
    }

    def __init__(self):
        """Initialize tag reader."""
        pass

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
            info.file_format = Path(file_path).suffix.lstrip('.').upper()

            # Load file with mutagen
            audio = MutagenFile(file_path)

            if audio is None:
                info.read_error = "Unrecognized audio format"
                return info

            # Get duration
            if hasattr(audio.info, 'length'):
                info.duration_seconds = audio.info.length

            # Get bitrate
            if hasattr(audio.info, 'bitrate'):
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

        except Exception as e:
            info.read_error = f"Error reading file: {str(e)}"

        return info

    def _read_mp3_tags(self, audio: MP3, info: AudioFileInfo):
        """Read tags from MP3 file."""
        if audio.tags:
            # Album (book title)
            if 'TALB' in audio.tags:
                info.album = str(audio.tags['TALB'])

            # Album Artist (primary author)
            if 'TPE2' in audio.tags:
                info.album_artist = str(audio.tags['TPE2'])

            # Artist (fallback author)
            if 'TPE1' in audio.tags:
                info.artist = str(audio.tags['TPE1'])

            # Title
            if 'TIT2' in audio.tags:
                info.title = str(audio.tags['TIT2'])

            # Year
            if 'TDRC' in audio.tags:
                try:
                    year_str = str(audio.tags['TDRC'])
                    info.year = int(year_str[:4])
                except (ValueError, IndexError):
                    pass

            # Genre
            if 'TCON' in audio.tags:
                info.genre = str(audio.tags['TCON'])

            # Comment
            if 'COMM' in audio.tags:
                # COMM can have multiple values
                comments = audio.tags.getall('COMM')
                if comments:
                    info.comment = str(comments[0])

            # Composer (narrator)
            if 'TCOM' in audio.tags:
                info.composer = str(audio.tags['TCOM'])

            # Track number
            if 'TRCK' in audio.tags:
                try:
                    track_str = str(audio.tags['TRCK'])
                    if '/' in track_str:
                        track, total = track_str.split('/')
                        info.track_number = int(track)
                        info.total_tracks = int(total)
                    else:
                        info.track_number = int(track_str)
                except (ValueError, IndexError):
                    pass

    def _read_flac_tags(self, audio: FLAC, info: AudioFileInfo):
        """Read tags from FLAC file."""
        if audio.tags:
            info.album = self._get_tag(audio, 'album')
            info.album_artist = self._get_tag(audio, 'albumartist')
            info.artist = self._get_tag(audio, 'artist')
            info.title = self._get_tag(audio, 'title')
            info.genre = self._get_tag(audio, 'genre')
            info.comment = self._get_tag(audio, 'comment')
            info.composer = self._get_tag(audio, 'composer')

            # Year
            date_str = self._get_tag(audio, 'date')
            if date_str:
                try:
                    info.year = int(date_str[:4])
                except (ValueError, IndexError):
                    pass

            # Track number
            track_str = self._get_tag(audio, 'tracknumber')
            if track_str:
                try:
                    if '/' in track_str:
                        track, total = track_str.split('/')
                        info.track_number = int(track)
                        info.total_tracks = int(total)
                    else:
                        info.track_number = int(track_str)
                except (ValueError, IndexError):
                    pass

    def _read_mp4_tags(self, audio: MP4, info: AudioFileInfo):
        """Read tags from M4A/M4B file."""
        if audio.tags:
            info.album = self._get_mp4_tag(audio, '©alb')
            info.album_artist = self._get_mp4_tag(audio, 'aART')
            info.artist = self._get_mp4_tag(audio, '©ART')
            info.title = self._get_mp4_tag(audio, '©nam')
            info.genre = self._get_mp4_tag(audio, '©gen')
            info.comment = self._get_mp4_tag(audio, '©cmt')
            info.composer = self._get_mp4_tag(audio, '©wrt')

            # Year
            year_str = self._get_mp4_tag(audio, '©day')
            if year_str:
                try:
                    info.year = int(year_str[:4])
                except (ValueError, IndexError):
                    pass

            # Track number
            if 'trkn' in audio.tags:
                track_info = audio.tags['trkn'][0]
                if isinstance(track_info, tuple) and len(track_info) >= 2:
                    info.track_number = track_info[0]
                    info.total_tracks = track_info[1]

    def _read_ogg_tags(self, audio: OggVorbis, info: AudioFileInfo):
        """Read tags from OGG file."""
        # OGG uses similar tags to FLAC
        self._read_flac_tags(audio, info)

    def _read_generic_tags(self, audio, info: AudioFileInfo):
        """Try to read tags generically."""
        if hasattr(audio, 'tags') and audio.tags:
            # Try common tag names
            for tag_name in ['album', 'title', 'artist', 'genre']:
                if tag_name in audio.tags:
                    value = audio.tags[tag_name]
                    if isinstance(value, list) and value:
                        value = str(value[0])
                    else:
                        value = str(value)
                    setattr(info, tag_name, value)

    def _get_tag(self, audio, tag_name: str) -> str:
        """Get tag value from FLAC/OGG."""
        if tag_name in audio:
            values = audio[tag_name]
            if values:
                return str(values[0])
        return ""

    def _get_mp4_tag(self, audio: MP4, tag_name: str) -> str:
        """Get tag value from MP4."""
        if tag_name in audio.tags:
            values = audio.tags[tag_name]
            if values:
                return str(values[0])
        return ""

    def extract_narrator(self, comment: str, composer: str) -> str:
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

        # Check comment for "read by", "narrated by", etc.
        if comment:
            comment_lower = comment.lower()
            patterns = [
                'read by ', 'narrated by ', 'narrator: ',
                'reader: ', 'performed by '
            ]

            for pattern in patterns:
                if pattern in comment_lower:
                    idx = comment_lower.index(pattern)
                    narrator = comment[idx + len(pattern):].strip()
                    # Get first line/sentence
                    narrator = narrator.split('\n')[0].split('.')[0]
                    return narrator.strip()

        return ""


class BookScanner:
    """
    Scans folders for audiobook files and groups them by book.
    """

    def __init__(self):
        """Initialize book scanner."""
        self.tag_reader = TagReader()

    def scan_folder(self, folder_path: str, include_subfolders: bool = True,
                    allowed_extensions: Optional[set] = None,
                    progress_callback: Optional[Callable[[
                        int, int, str], None]] = None,
                    cancel_check: Optional[Callable[[], bool]] = None) -> List[Dict[str, Any]]:
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
            return self.scan_file(folder_path, progress_callback, cancel_check)

        # Find all audio files
        audio_files = []
        if not folder_path or not os.path.isdir(folder_path):
            return []

        def is_allowed(file_path: str) -> bool:
            ext = Path(file_path).suffix.lower()
            if allowed_extensions is not None:
                return ext in allowed_extensions
            return self.tag_reader.is_supported_file(file_path)

        if include_subfolders:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if is_allowed(file_path):
                        audio_files.append(file_path)
        else:
            for entry in os.scandir(folder_path):
                if entry.is_file():
                    if is_allowed(entry.path):
                        audio_files.append(entry.path)

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
            book_key = info.album or os.path.basename(
                os.path.dirname(file_path))

            if book_key not in books:
                books[book_key] = {
                    'title': info.album,
                    'author': info.album_artist or info.artist,
                    'year': info.year,
                    'genre': info.genre,
                    'narrator': self.tag_reader.extract_narrator(info.comment, info.composer),
                    'comments': [],
                    'files': [],
                    'total_duration': 0.0,
                    'total_size': 0,
                    'bitrate': info.bitrate,
                    'format': info.file_format,
                    'folder': os.path.dirname(file_path),
                    'errors': []
                }

            book = books[book_key]

            # Accumulate data
            book['files'].append(file_path)
            book['total_duration'] += info.duration_seconds
            book['total_size'] += info.file_size_bytes

            # Collect unique comments
            if info.comment and info.comment not in book['comments']:
                book['comments'].append(info.comment)

            # Collect errors
            if info.read_error:
                book['errors'].append(
                    f"{os.path.basename(file_path)}: {info.read_error}")

        # Convert to list and finalize
        result = []
        for book in books.values():
            # Combine comments
            book['comment'] = '\n\n'.join(book['comments'])
            del book['comments']

            # Convert duration to hours/minutes
            total_minutes = int(book['total_duration'] / 60)
            book['time_hours'] = total_minutes // 60
            book['time_minutes'] = total_minutes % 60

            # Convert size to MB
            book['size_mb'] = book['total_size'] / (1024 * 1024)

            # Track count
            book['tracks'] = len(book['files'])

            result.append(book)

        return result

    def scan_file(self, file_path: str,
                  progress_callback: Optional[Callable[[
                      int, int, str], None]] = None,
                  cancel_check: Optional[Callable[[], bool]] = None) -> List[Dict[str, Any]]:
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

        if not self.tag_reader.is_supported_file(file_path):
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
            'title': info.album or book_key,
            'author': info.album_artist or info.artist,
            'year': info.year,
            'genre': info.genre,
            'narrator': self.tag_reader.extract_narrator(info.comment, info.composer),
            'comment': info.comment or '',
            'files': [file_path],
            'total_duration': info.duration_seconds,
            'total_size': info.file_size_bytes,
            'bitrate': info.bitrate,
            'format': info.file_format,
            'folder': os.path.dirname(file_path),
            'errors': []
        }

        # Add error if present
        if info.read_error:
            book['errors'].append(f"{file_name}: {info.read_error}")

        # Convert duration to hours/minutes
        total_minutes = int(book['total_duration'] / 60)
        book['time_hours'] = total_minutes // 60
        book['time_minutes'] = total_minutes % 60

        # Convert size to MB
        book['size_mb'] = book['total_size'] / (1024 * 1024)

        # Track count (always 1 for single file)
        book['tracks'] = 1

        return [book]
