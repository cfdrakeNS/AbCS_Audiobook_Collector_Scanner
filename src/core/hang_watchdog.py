"""Write Python stacks to abcs_hang.log when the UI thread stops responding.

Event Viewer records nothing when a hung app is ended from Task Manager, so
this log is the only record of where the UI thread was stuck. Crashes in C
code are written to the same file by faulthandler.
"""
from __future__ import annotations

import faulthandler
import threading
import time
from datetime import datetime
from pathlib import Path

HANG_SECONDS = 15.0
LOG_NAME = "abcs_hang.log"

_log_file = None
_last_beat = time.monotonic()
_timer = None


def log_path() -> Path:
    from src.app_paths import get_user_data_dir

    return get_user_data_dir() / LOG_NAME


def _beat() -> None:
    global _last_beat
    _last_beat = time.monotonic()


def _watch() -> None:
    reported = False
    while True:
        time.sleep(2.0)
        stalled = time.monotonic() - _last_beat
        if stalled < HANG_SECONDS:
            reported = False
            continue
        if reported or _log_file is None:
            continue
        reported = True
        try:
            stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            _log_file.write(
                f"\n=== {stamp} UI not responding for {stalled:.0f} seconds ===\n"
            )
            _log_file.flush()
            faulthandler.dump_traceback(file=_log_file, all_threads=True)
            _log_file.flush()
        except Exception:
            pass


def install() -> None:
    """Start the heartbeat timer and watcher thread. Call after QApplication exists."""
    global _log_file, _timer
    if _timer is not None:
        return
    try:
        _log_file = open(log_path(), "a", encoding="utf-8")
        faulthandler.enable(file=_log_file, all_threads=True)
    except Exception:
        _log_file = None
        return
    from PySide6.QtCore import QTimer

    _timer = QTimer()
    _timer.setInterval(1000)
    _timer.timeout.connect(_beat)
    _timer.start()
    _beat()
    threading.Thread(target=_watch, name="abcs-hang-watchdog", daemon=True).start()
