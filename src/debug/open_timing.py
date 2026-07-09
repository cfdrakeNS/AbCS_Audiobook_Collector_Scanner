"""Temporary diagnostics for Book Details open timing (remove after investigation)."""

from __future__ import annotations

import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from src.app_paths import get_user_data_dir

_origin: float | None = None
_session_started = False


def _flag_file() -> Path:
    return get_user_data_dir() / "open_timing.on"


def _log_file() -> Path:
    return get_user_data_dir() / "open_timing.log"


def enabled() -> bool:
    """True when ABCS_OPEN_TIMING=1 or open_timing.on exists in the AbCS data folder."""
    env = os.environ.get("ABCS_OPEN_TIMING", "").strip().lower()
    if env in ("1", "true", "yes"):
        return True
    try:
        return _flag_file().is_file()
    except OSError:
        return False


def _ensure_session_banner() -> None:
    global _session_started
    if _session_started or not enabled():
        return
    _session_started = True
    banner = (
        f"\n=== AbCS open timing session {datetime.now(timezone.utc).isoformat()} ===\n"
        f"Log file: {_log_file()}\n"
        f"Disable: delete {_flag_file()} or unset ABCS_OPEN_TIMING\n"
    )
    _write_line(banner.rstrip())


def _write_line(line: str) -> None:
    """Write to log file, stderr, and stdout."""
    try:
        with _log_file().open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
    except OSError:
        pass
    try:
        print(line, file=sys.stderr, flush=True)
        print(line, flush=True)
    except OSError:
        pass


def mark_origin() -> None:
    """Reset the timing origin for a new open sequence."""
    global _origin
    _ensure_session_banner()
    _origin = time.perf_counter()


def log(phase: str) -> None:
    """Log a phase label with milliseconds since mark_origin()."""
    if not enabled():
        return
    _ensure_session_banner()
    now = time.perf_counter()
    if _origin is None:
        rel_ms = 0.0
    else:
        rel_ms = (now - _origin) * 1000
    _write_line(f"[AbCS timing] +{rel_ms:7.1f}ms  {phase}")


def log_file_path() -> str:
    """Return the path to the timing log file (for user instructions)."""
    return str(_log_file())
