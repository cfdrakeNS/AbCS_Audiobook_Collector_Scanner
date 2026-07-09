"""Temporary diagnostics for Book Details open timing (remove after investigation)."""

from __future__ import annotations

import os
import sys
import time

_origin: float | None = None


def enabled() -> bool:
    """True when ABCS_OPEN_TIMING is set to 1, true, or yes."""
    return os.environ.get("ABCS_OPEN_TIMING", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def mark_origin() -> None:
    """Reset the timing origin for a new open sequence."""
    global _origin
    _origin = time.perf_counter()


def log(phase: str) -> None:
    """Log a phase label with milliseconds since mark_origin()."""
    if not enabled():
        return
    now = time.perf_counter()
    if _origin is None:
        rel_ms = 0.0
    else:
        rel_ms = (now - _origin) * 1000
    print(f"[AbCS timing] +{rel_ms:7.1f}ms  {phase}", file=sys.stderr, flush=True)
