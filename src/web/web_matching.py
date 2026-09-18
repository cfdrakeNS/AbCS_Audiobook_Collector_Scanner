"""Title/author matching helpers for web metadata.

Matching currently lives on ``WebBookAPI`` methods in ``web_book_api.py``.
This module holds shared constants used by those methods and is the home for
future extractions of scoring helpers.
"""

from __future__ import annotations

import re

STOPWORDS = {"the", "a", "an", "and", "or", "of", "in", "on", "to", "for"}

AUTHOR_HONORIFIC_PREFIX = re.compile(
    r"^(?:sir|dame|dr\.?|prof\.?|mr\.?|mrs\.?|ms\.?|lord|lady)\s+",
    re.IGNORECASE,
)

ORWELL_1984_TITLE_TOKEN = "1984"
ORWELL_AUTHOR_LABEL = "George Orwell"
