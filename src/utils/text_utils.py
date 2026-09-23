"""
Text Utilities - Unified text normalization and similarity functions.

Centralizes fuzzy matching logic to eliminate duplication between:
- validator.py (import validation)
- book_list_import_window.py (list import duplicate checking)
- web_metadata.py (web review title/author comparison)
"""

import re
import string
import unicodedata
from difflib import SequenceMatcher


_TRAILING_ARTICLE_RE = re.compile(r"^(.*?),\s*(the|a|an)\s*$", re.IGNORECASE)
_LEADING_ARTICLE_RE = re.compile(r"^(the|an|a)\s+", re.IGNORECASE)
_TRAILING_PARENS_RE = re.compile(r"\s*\([^)]*\)\s*$")

# Shared series suffix patterns used by import, web metadata, and catalog tools.
# Decimals allowed (e.g. "Busted - 6.5"); comma form stays integer-only for year guard.
_SERIES_NUMBER_PATTERNS = (
    r"^(.*?)\s*-\s*(\d+(?:\.\d+)?)$",  # "Title - 09", "Title - 6.5"
    r"^(.*?)\s*#\s*(\d+(?:\.\d+)?)$",  # "Title #09"
    r"^(.*?)\s+Book\s*(\d+(?:\.\d+)?)$",  # "Title Book 09"
    r"^(.*?)\s+Volume\s*(\d+(?:\.\d+)?)$",  # "Title Volume 09"
    r"^(.*?)\s*,\s*(\d+)$",  # "Title, 09" (integer only; comma-year guard below)
)
_SERIES_NUMBER_TOKEN_RE = re.compile(r"^\d+(?:\.\d+)?$")

# Web metadata review: cosmetic filler tails stripped before title compare.
_TITLE_FILLER_TAIL_RE = re.compile(
    r"(?:"
    r"\s*:\s*a\s+(?:novel|thriller|memoir|mystery|romance|story|tale)\s*$"
    r"|"
    r"\s*\((?:unabridged|abridged)\)\s*$"
    r"|"
    r"\s+(?:library\s+edition|complete\s+and\s+unabridged)\s*$"
    r")",
    re.IGNORECASE,
)

# Honorifics / suffixes for web author comparison (mirrored from web_book_api).
_AUTHOR_HONORIFIC_PREFIX = re.compile(
    r"^(?:sir|dame|dr\.?|prof\.?|mr\.?|mrs\.?|ms\.?|lord|lady)\s+",
    re.IGNORECASE,
)
_AUTHOR_SUFFIX_TOKENS = frozenset(
    {"jr", "sr", "ii", "iii", "iv", "phd", "md", "esq"}
)
_AUTHOR_NON_ALNUM_RE = re.compile(r"[^\w]+", re.UNICODE)


def _looks_like_year(number: str) -> bool:
    """True when digits are probably a publication year, not a series index."""
    digits = re.sub(r"[^\d]", "", str(number or ""))
    if len(digits) != 4:
        return False
    try:
        value = int(digits)
    except ValueError:
        return False
    return 1700 <= value <= 2099


def split_series_number(title: str) -> tuple:
    """Return ``(clean_title, series_number)`` when a trailing series index is found.

    ``series_number`` is kept as a string so decimals like ``6.5`` survive.
    Returns ``(stripped_title, "")`` when no series index is present.
    """
    if not isinstance(title, str) or not title.strip():
        return "", ""

    t = title.strip()
    for pattern in _SERIES_NUMBER_PATTERNS:
        match = re.match(pattern, t, re.IGNORECASE)
        if not match:
            continue
        clean_title = match.group(1).strip()
        series_number = match.group(2)
        if clean_title and not _looks_like_year(series_number):
            return clean_title, series_number

    return t, ""


def series_number_for_storage(value) -> int | float | None:
    """Series index for the database column, or None.

    Whole numbers collapse (``2``, ``2.0``, and ``02`` become ``2``).
    Decimals stay (``6.5`` stays ``6.5``). Blank and zero are empty.
    """
    key = series_number_key(value)
    if not key:
        return None
    try:
        number = float(key) if "." in key else int(key)
    except ValueError:
        return None
    if number == 0:
        return None
    return number


def title_without_matching_series_suffix(
    title: str, series_number: int | float | None
) -> str:
    """Drop a trailing `` - N`` only when it is the same number being stored."""
    if series_number is None or not isinstance(title, str):
        return title or ""
    clean, existing = split_series_number(title)
    if not existing or not clean:
        return title
    if series_number_key(existing) == series_number_key(series_number):
        return clean
    return title


def strip_series_number(title: str) -> str:
    """Return title with trailing series number removed when clearly separated."""
    clean_title, _ = split_series_number(title)
    return clean_title


def series_number_key(value) -> str:
    """Return a canonical series-number key for duplicate tiebreaking.

    Whole numbers collapse to unpadded digits (``01``, ``1``, ``1.0`` → ``1``).
    Decimals keep their fractional form (``6.5`` → ``6.5``). Empty / missing
    values return ``""``.
    """
    if value is None:
        return ""

    if isinstance(value, float):
        if value != value:  # NaN
            return ""
        if value == int(value):
            return str(int(value))
        text = str(value).strip()
        return text if _SERIES_NUMBER_TOKEN_RE.match(text) else ""

    if isinstance(value, int):
        return str(value)

    text = str(value).strip()
    if not text or text.lower() == "nan":
        return ""
    if text.startswith("#"):
        text = text[1:].strip()
    if not text:
        return ""

    # Integral float strings: "1.0" / "01.0" → "1"
    if re.fullmatch(r"0*\d+\.0+", text):
        text = text.split(".", 1)[0]

    if not _SERIES_NUMBER_TOKEN_RE.match(text):
        return ""

    if "." in text:
        # "06.5" → "6.5"; leave "0.5" alone
        if text.startswith("0.") or text.startswith("."):
            return text
        return text.lstrip("0") or text

    # Strip leading zeros from whole numbers ("01" → "1"), keep bare "0"
    stripped = text.lstrip("0")
    return stripped if stripped else "0"


def series_numbers_compatible(left, right) -> bool:
    """True when series numbers do not conflict for duplicate matching.

    An empty series number is compatible with any value so a bare title can
    still match a titled-with-suffix DB entry. Two present and different keys
    are incompatible (``01`` vs ``02``).
    """
    left_key = series_number_key(left)
    right_key = series_number_key(right)
    if not left_key or not right_key:
        return True
    return left_key == right_key


def titles_match(left: str, right: str, fuzzy_threshold: int = 0) -> bool:
    """Compare two raw titles for import duplicate purposes.

    Strips series numbers via ``compare_normalize_title``, then applies the
    series-number tiebreaker. When ``fuzzy_threshold`` is greater than 0 and
    the normalized titles are not exact, uses ``similarity_percentage``.
    """
    left_norm = compare_normalize_title(left)
    right_norm = compare_normalize_title(right)
    if not left_norm or not right_norm:
        return False

    _, left_series = split_series_number(left if isinstance(left, str) else "")
    _, right_series = split_series_number(right if isinstance(right, str) else "")
    if not series_numbers_compatible(left_series, right_series):
        return False

    if left_norm == right_norm:
        return True

    if fuzzy_threshold > 0:
        return similarity_percentage(left_norm, right_norm) >= fuzzy_threshold

    return False


def format_series_suffix(value) -> str:
    """Normalize a raw series-number cell or field for title suffixes.

    Whole numbers are zero-padded to two digits (``2`` / ``2.0`` → ``02``).
    Decimals are left as written (``6.5`` → ``6.5``). Leading ``#`` is stripped.
    """
    if value is None:
        return ""

    if isinstance(value, float):
        if value != value:  # NaN
            return ""
        if value == int(value):
            value = int(value)
        else:
            text = str(value).strip()
            return text if _SERIES_NUMBER_TOKEN_RE.match(text) else ""

    if isinstance(value, int):
        return str(value).zfill(2)

    text = str(value).strip()
    if not text or text.lower() == "nan":
        return ""
    if text.startswith("#"):
        text = text[1:].strip()
    if not text:
        return ""

    # Integral float strings from spreadsheets: "2.0" → "02"
    if re.fullmatch(r"\d+\.0+", text):
        text = text.split(".", 1)[0]

    if _SERIES_NUMBER_TOKEN_RE.match(text):
        if "." in text:
            return text
        return text.zfill(2)

    return text


def append_series_suffix(title: str, value) -> str:
    """Return ``title - NN`` when a series number is present and not already on title."""
    if not isinstance(title, str):
        title = str(title or "")
    title = title.strip()
    if not title:
        return title

    clean_title, existing = split_series_number(title)
    if existing:
        return title

    suffix = format_series_suffix(value)
    if not suffix:
        return title

    base = clean_title or title
    return f"{base} - {suffix}"


def pre_normalize_title(title: str) -> str:
    """Pre-process a title before aggressive normalization for import comparison.

    Prepares DB and sheet titles the same way web metadata prepares a DB title
    for search (series strip, parenthetical series, article move). Does not
    modify web_metadata code paths.

    Steps applied (in order):
    1. Strip separated series suffix: ``Triptych - 01``, ``Busted - 6.5``, etc.
    2. Strip trailing parenthetical series/subtitle markers when series-like.
    3. Move trailing article: ``Hobbit, The`` → ``The Hobbit``.
    """
    if not isinstance(title, str):
        return ""
    t = title.strip()

    t = strip_series_number(t)

    # Strip series annotation in parentheses at the end of the title.
    # Only fires when the content looks like a series marker.
    paren_match = _TRAILING_PARENS_RE.search(t)
    if paren_match:
        inner = t[paren_match.start() + 1 : paren_match.end() - 1].lower()
        if re.search(r"#|\bbook\b|\bvol\b|\bvolume\b|\bseries\b|\bpart\b", inner):
            t = t[: paren_match.start()].strip()
        elif re.search(r"\d", inner):
            # e.g. "Bury Your Dead (Armand Gamache 6)"
            t = t[: paren_match.start()].strip()

    # Move trailing comma-article: "Title, The" → "The Title"
    art_match = _TRAILING_ARTICLE_RE.match(t)
    if art_match:
        base = art_match.group(1).strip()
        article = art_match.group(2).capitalize()
        t = f"{article} {base}"

    return t


def _strip_optional_leading_article(title: str) -> str:
    """Drop a leading A/An/The when the rest of the title is still non-empty."""
    text = (title or "").strip()
    match = _LEADING_ARTICLE_RE.match(text)
    if not match:
        return text
    rest = text[match.end() :].strip()
    return rest if rest else text


def compare_normalize_title(title: str) -> str:
    """Normalize a title for import duplicate / read-date comparison."""
    return normalize_title(pre_normalize_title(title), aggressive=True)


def normalize_title(title: str, aggressive: bool = False) -> str:
    """
    Normalize title for comparison.
    
    Args:
        title: Raw title string
        aggressive: If True, removes all spaces and punctuation.
                   If False, only lowercase and strip.
    
    Returns:
        Normalized title string
    """
    if not isinstance(title, str):
        return ""
    
    t = title.strip().lower()
    
    if aggressive:
        # Remove all spaces and punctuation
        t = "".join(
            c for c in t if c not in string.whitespace and c not in string.punctuation
        )
    
    return t


def normalize_author(author: str, aggressive: bool = False) -> str:
    """
    Normalize author name for comparison.
    
    Args:
        author: Raw author string
        aggressive: If True, removes all spaces and punctuation.
                   If False, only lowercase and strip.
    
    Returns:
        Normalized author string
    """
    if not isinstance(author, str):
        return ""
    
    a = author.strip().lower()
    
    if aggressive:
        # Remove spaces and punctuation
        a = "".join(
            c for c in a if c not in string.whitespace and c not in string.punctuation
        )
    
    return a


def fold_text(value: str) -> str:
    """Fold accents and rewrite ``&`` to ``and`` for web title/author compare."""
    if not isinstance(value, str):
        return ""
    text = value.strip()
    if not text:
        return ""
    # NFKD then drop combining marks so Émile → Emile
    decomposed = unicodedata.normalize("NFKD", text)
    without_marks = "".join(
        c for c in decomposed if not unicodedata.combining(c)
    )
    without_marks = without_marks.replace("&", " and ")
    return re.sub(r"\s+", " ", without_marks).strip()


def web_compare_title_storage_key(title: str) -> str:
    """Title key for whether to *offer* a save (keeps leading A/An/The)."""
    if not isinstance(title, str):
        return ""
    folded = fold_text(title)
    folded = _TITLE_FILLER_TAIL_RE.sub("", folded).strip()
    return compare_normalize_title(folded)


def web_compare_title_key(title: str) -> str:
    """Canonical title key for “same work” (optional leading A/An/The folded)."""
    if not isinstance(title, str):
        return ""
    folded = fold_text(title)
    folded = _TITLE_FILLER_TAIL_RE.sub("", folded).strip()
    prepared = pre_normalize_title(folded)
    prepared = _strip_optional_leading_article(prepared)
    return normalize_title(prepared, aggressive=True)


def web_titles_match(left: str, right: str) -> bool:
    """True when two titles are the same work for web review (leading article optional)."""
    left_key = web_compare_title_key(left)
    right_key = web_compare_title_key(right)
    if not left_key or not right_key:
        return False
    return left_key == right_key


def _author_tokens(author: str) -> list[str]:
    """Tokenize an author name after fold/honorific/suffix strip."""
    text = fold_text(author)
    if not text:
        return []
    # Strip leading honorifics repeatedly
    while True:
        match = _AUTHOR_HONORIFIC_PREFIX.match(text)
        if not match:
            break
        text = text[match.end() :].strip()
    # Split on non-alphanumerics; keep unicode letters/digits
    raw_tokens = [
        t.casefold()
        for t in _AUTHOR_NON_ALNUM_RE.split(text)
        if t
    ]
    return [t for t in raw_tokens if t and t not in _AUTHOR_SUFFIX_TOKENS]


def web_compare_author_key(author: str) -> str:
    """Sorted-token author key (order-independent) for web review."""
    tokens = _author_tokens(author)
    if not tokens:
        return ""
    return " ".join(sorted(tokens))


def _given_names_compatible(left: list[str], right: list[str]) -> bool:
    """Pairwise given-name compatibility (equal length; initials allowed)."""
    if len(left) != len(right):
        return False
    for a, b in zip(left, right):
        if a == b:
            continue
        if len(a) == 1 and b.startswith(a):
            continue
        if len(b) == 1 and a.startswith(b):
            continue
        return False
    return True


def web_authors_match(left: str, right: str) -> bool:
    """True when two author names likely refer to the same person.

    Matches when sorted-token keys are equal (covers ``King, Stephen`` vs
    ``Stephen King`` and punctuation), or when surnames match and given-name
    lists are initial-compatible pairwise.
    """
    left_tokens = _author_tokens(left)
    right_tokens = _author_tokens(right)
    if not left_tokens or not right_tokens:
        return False

    if " ".join(sorted(left_tokens)) == " ".join(sorted(right_tokens)):
        return True

    # Surname = last token; given names = everything before.
    if left_tokens[-1] != right_tokens[-1]:
        return False
    return _given_names_compatible(left_tokens[:-1], right_tokens[:-1])


def similarity_ratio(left: str, right: str) -> float:
    """
    Calculate normalized text similarity score from 0.0 to 1.0.
    
    Uses difflib.SequenceMatcher for fuzzy comparison.
    
    Args:
        left: First string to compare
        right: Second string to compare
    
    Returns:
        Similarity ratio from 0.0 (completely different) to 1.0 (identical)
    """
    if not left or not right:
        return 0.0
    
    if left == right:
        return 1.0
    
    return SequenceMatcher(None, left, right).ratio()


def similarity_percentage(left: str, right: str) -> float:
    """
    Calculate text similarity as percentage from 0 to 100.
    
    Convenience wrapper around similarity_ratio() for use with
    threshold values typically stored as integers (0-100).
    
    Args:
        left: First string to compare
        right: Second string to compare
    
    Returns:
        Similarity percentage from 0 to 100
    """
    return similarity_ratio(left, right) * 100
