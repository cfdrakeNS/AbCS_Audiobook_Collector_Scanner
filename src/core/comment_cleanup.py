"""Remove technical tag data from audiobook comment text.

iTunes writes ID3 comment frames named ``iTunNORM``, ``iTunSMPB``,
``iTunPGAP``, ``iTunes_CDDB_1``, ``iTunes_CDDB_IDs``, and
``iTunes_CDDB_TrackNumber``; ripping and conversion tools add MusicBrainz IDs
and encoder stamps. They mean nothing to a listener and can make one book's
Comments tens of thousands of characters long.
"""

from __future__ import annotations

import re

_HEX_GROUP = r"[0-9A-Fa-f]{8}(?:[0-9A-Fa-f]{8})?"

# iTunNORM / iTunSMPB / iTunPGAP: nine or more 8- or 16-digit hex groups.
_HEX_BLOCK_RE = re.compile(rf"^(?:{_HEX_GROUP}\s+){{8,}}{_HEX_GROUP}$")
# iTunes_CDDB_1: disc ID, then track count, lead-in, and track offsets.
_CDDB_DISC_RE = re.compile(r"^[0-9A-Fa-f]{8}(?:\+\d+){3,}$")
# iTunes_CDDB_IDs: track count + 32-digit hash + length.
_CDDB_IDS_RE = re.compile(r"^\d+\+[0-9A-Fa-f]{32}\+\d+$")
_UUID = r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}"
# MusicBrainz / AcoustID identifiers: a bare UUID, or a labelled one.
_MUSICBRAINZ_RE = re.compile(
    rf"^(?:(?:MusicBrainz|AcoustID)[\w ]*[:=]?\s*)?{_UUID}$", re.IGNORECASE
)
# Encoder and converter stamps written by ripping or conversion tools.
_TOOL_STAMP_RE = re.compile(
    r"^(?:"
    r"(?:LAME|Lavf|Lavc|Lavu)\s?\d[\w.\-]*"
    r"|iTunes\s?v?\d+(?:\.\d+)+"
    r"|fre:ac\b.{0,80}"
    r"|(?:https?://)?(?:www\.)?online-audio-converter\.com/?"
    r"|Exact\s?Audio\s?Copy\b.{0,40}"
    r"|dBpoweramp\b.{0,40}"
    r"|Encoded\s(?:by|with)\s.{1,60}"
    r")$",
    re.IGNORECASE,
)
# iTunes_CDDB_TrackNumber: a bare track number, sometimes with trailing ``+``.
_TRACK_NUMBER_RE = re.compile(r"^\d{1,3}\+{0,2}$")

_TECHNICAL_FRAME_WORDS = ("musicbrainz", "acoustid", "encoder", "encoded by", "cddb")

_PIECE_SPLIT_RE = re.compile(r"\s*;\s*|\s*\r?\n(?:\s*\r?\n)*\s*")


def is_technical_comment_frame(description: str) -> bool:
    """True for ID3 comment frame descriptions that hold tool data, not a comment.

    iTunes frames (``iTun...``) and frames named for MusicBrainz, AcoustID,
    CD database, or encoder data.
    """
    desc = str(description or "").strip().lower()
    if desc.startswith("itun"):
        return True
    return any(word in desc for word in _TECHNICAL_FRAME_WORDS)


def is_technical_comment_piece(text: str) -> bool:
    """True when one comment piece is technical data rather than text for a listener.

    Hex blocks, CD database IDs, MusicBrainz / AcoustID identifiers, and
    encoder or converter stamps.
    """
    piece = " ".join(str(text or "").split())
    if not piece:
        return False
    return bool(
        _HEX_BLOCK_RE.match(piece)
        or _CDDB_DISC_RE.match(piece)
        or _CDDB_IDS_RE.match(piece)
        or _MUSICBRAINZ_RE.match(piece)
        or _TOOL_STAMP_RE.match(piece)
    )


def clean_comment_text(text: str) -> str:
    """Return comment text without technical tag data.

    Text with no technical piece is returned unchanged. Otherwise
    the technical pieces, bare track numbers, empty pieces, and repeated pieces
    are dropped, and the rest is joined with ``; `` (or a blank line when the
    original had no ``;``).
    """
    if not text:
        return text or ""
    pieces = _PIECE_SPLIT_RE.split(str(text))
    if not any(is_technical_comment_piece(piece) for piece in pieces):
        return text

    kept: list[str] = []
    seen: set[str] = set()
    for piece in pieces:
        piece = piece.strip()
        if not piece or is_technical_comment_piece(piece):
            continue
        if _TRACK_NUMBER_RE.match(piece):
            continue
        key = " ".join(piece.split()).casefold()
        if key in seen:
            continue
        seen.add(key)
        kept.append(piece)
    separator = "; " if ";" in text else "\n\n"
    return separator.join(kept)
