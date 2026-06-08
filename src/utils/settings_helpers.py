"""
Settings Helpers - Centralized preference reading with legacy fallback.

This module provides utilities for reading application settings with
automatic fallback to legacy settings locations.
"""

from PySide6.QtCore import QSettings


def get_import_preferences() -> tuple[bool, bool]:
    """
    Read import-related preferences with legacy fallback.
    
    Returns:
        Tuple of (move_articles, flip_author) booleans
        
    Checks current AudioBookCollector settings first, falls back to
    legacy AbCS settings if not found.
    """
    settings = QSettings("AbCS", "AudioBookCollector")

    # Check legacy settings if current settings don't exist
    if not settings.contains("import/flip_author_name"):
        legacy_settings = QSettings("AbCS", "AbCS")
        flip_author = legacy_settings.value(
            "import/flip_author_name", False, type=bool
        )
    else:
        flip_author = settings.value("import/flip_author_name", False, type=bool)

    if not settings.contains("import/autocorrect/move_leading_the_title"):
        legacy_settings = QSettings("AbCS", "AbCS")
        move_articles = legacy_settings.value(
            "import/autocorrect/move_leading_the_title", False, type=bool
        )
    else:
        move_articles = settings.value(
            "import/autocorrect/move_leading_the_title", False, type=bool
        )

    return move_articles, flip_author


# CLEANUP: flip_author_name and move_leading_the_title have no Preferences UI; only
# web fetch paths still read these QSettings keys. Remove helper and callers when done.
