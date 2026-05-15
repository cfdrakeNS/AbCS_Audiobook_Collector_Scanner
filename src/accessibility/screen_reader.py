"""
Screen Reader Detection Utility
Detects if a screen reader is running on Windows or Linux.
"""

# Make psutil optional for Linux compatibility
try:
    import psutil
except ImportError:
    psutil = None


_SCREEN_READER_PROCESSES = {
    "jaws.exe": "jaws",
    "jfw.exe": "jaws",
    "nvda.exe": "nvda",
    "orca": "orca",
    "orca-daemon": "orca",
}


def get_active_screen_reader():
    """
    Returns the detected screen reader name, otherwise an empty string.
    Detects Windows screen readers (JAWS/NVDA) and Linux Orca.
    """
    if psutil is None:
        return ""

    for proc in psutil.process_iter(["name"]):
        name = proc.info["name"]
        if name is None:
            continue
        reader_name = _SCREEN_READER_PROCESSES.get(name.lower())
        if reader_name:
            return reader_name
    return ""


def get_screen_reader_focus_delay_ms():
    """
    Returns the focus restoration delay for the detected screen reader.
    """
    reader_name = get_active_screen_reader()
    return {
        "jaws": 300,
        "nvda": 1500,
        "orca": 800,
    }.get(reader_name, 0)


def is_screen_reader_active():
    """
    Returns True if a screen reader is running, otherwise False.
    Detects Windows screen readers (JAWS/NVDA) and Linux Orca.
    """
    return bool(get_active_screen_reader())
