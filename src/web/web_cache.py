"""Persistent and in-memory cache constants for web metadata."""

from __future__ import annotations

from src.web.web_http import WEB_CACHE_FILE, _resolve_web_cache_file

WEB_CACHE_MAX_ENTRIES = 500
NEGATIVE_CACHE_TTL_SECONDS = 3600
TRANSIENT_CACHE_TTL_SECONDS = 60
CACHE_DURATION = 86400
WEB_CACHE_SCHEMA_VERSION = 3

__all__ = [
    "WEB_CACHE_FILE",
    "WEB_CACHE_MAX_ENTRIES",
    "NEGATIVE_CACHE_TTL_SECONDS",
    "TRANSIENT_CACHE_TTL_SECONDS",
    "CACHE_DURATION",
    "WEB_CACHE_SCHEMA_VERSION",
    "_resolve_web_cache_file",
]
