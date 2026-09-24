"""Quiet Qt FFmpeg console chatter during in-app Preview."""

from __future__ import annotations

import ctypes
import os
import sys
from pathlib import Path

_AV_LOG_QUIET = -8
_env_applied = False
_level_applied = False
_stderr_saved = None
_stderr_null = None


def silence_preview_media_logs() -> None:
    """Turn down FFmpeg and Qt multimedia logs. Safe to call more than once."""
    global _env_applied
    if not _env_applied:
        _env_applied = True
        os.environ.setdefault(
            "QT_LOGGING_RULES",
            "qt.multimedia.ffmpeg.debug=false;qt.multimedia.ffmpeg=false",
        )
        try:
            from PySide6.QtCore import QLoggingCategory

            QLoggingCategory.setFilterRules(
                "qt.multimedia.ffmpeg.debug=false\n"
                "qt.multimedia.ffmpeg.info=false\n"
                "qt.multimedia.ffmpeg=false"
            )
        except Exception:
            pass
    _set_ffmpeg_log_quiet()


def mute_preview_stderr() -> None:
    """Hide C-level stderr so FFmpeg probe lines do not fill the console."""
    global _stderr_saved, _stderr_null
    if _stderr_saved is not None:
        return
    try:
        _stderr_saved = os.dup(2)
        _stderr_null = os.open(os.devnull, os.O_WRONLY)
        os.dup2(_stderr_null, 2)
    except OSError:
        _stderr_saved = None
        _stderr_null = None


def restore_preview_stderr() -> None:
    """Restore stderr after Preview closes."""
    global _stderr_saved, _stderr_null
    if _stderr_saved is None:
        return
    try:
        os.dup2(_stderr_saved, 2)
        os.close(_stderr_saved)
        if _stderr_null is not None:
            os.close(_stderr_null)
    except OSError:
        pass
    _stderr_saved = None
    _stderr_null = None


def _set_ffmpeg_log_quiet() -> None:
    global _level_applied
    if _level_applied:
        return
    for name in _ffmpeg_library_names():
        try:
            lib = ctypes.CDLL(name)
            lib.av_log_set_level.argtypes = [ctypes.c_int]
            lib.av_log_set_level(_AV_LOG_QUIET)
            _level_applied = True
            return
        except (OSError, AttributeError):
            continue


def _ffmpeg_library_names() -> list[str]:
    names: list[str] = []
    try:
        import PySide6

        root = Path(PySide6.__file__).resolve().parent
        names.extend(str(path) for path in root.glob("avutil*.dll"))
        plugin = root / "plugins" / "multimedia" / "ffmpegmediaplugin.dll"
        if plugin.is_file():
            names.append(str(plugin))
    except Exception:
        pass
    names.extend(_loaded_ffmpeg_paths())
    names.extend(("avutil-59", "avutil-58", "avutil-57", "avutil"))
    seen: set[str] = set()
    unique: list[str] = []
    for name in names:
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(name)
    return unique


def _loaded_ffmpeg_paths() -> list[str]:
    if sys.platform != "win32":
        return []
    try:
        psapi = ctypes.WinDLL("psapi")
        kernel32 = ctypes.WinDLL("kernel32")
        process = kernel32.GetCurrentProcess()
        handles = (ctypes.c_void_p * 512)()
        needed = ctypes.c_ulong()
        if not psapi.EnumProcessModules(
            process, ctypes.byref(handles), ctypes.sizeof(handles), ctypes.byref(needed)
        ):
            return []
        count = min(needed.value // ctypes.sizeof(ctypes.c_void_p), len(handles))
        paths: list[str] = []
        buf = ctypes.create_unicode_buffer(32768)
        markers = ("avutil", "ffmpeg", "multimedia")
        for i in range(count):
            if not handles[i]:
                continue
            length = psapi.GetModuleFileNameExW(process, handles[i], buf, len(buf))
            if not length:
                continue
            path = buf.value
            lower = path.lower()
            if any(marker in lower for marker in markers):
                paths.append(path)
        return paths
    except Exception:
        return []
