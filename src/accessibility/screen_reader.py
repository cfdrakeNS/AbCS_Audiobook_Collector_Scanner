"""
Screen Reader Detection Utility
Detects if a screen reader is running on Windows.
"""

# Make psutil optional for Linux compatibility
try:
    import psutil
except ImportError:
    psutil = None


def is_screen_reader_active():
    """
    Returns True if a screen reader is running, otherwise False.
    Only detects Windows screen readers (JAWS/NVDA).
    """
    # psutil not available on Linux or not installed - no Windows screen readers
    if psutil is None:
        return False

    for proc in psutil.process_iter(["name"]):
        name = proc.info["name"]
        if name is None:
            continue
        lname = name.lower()
        # If the process name matches a known screen reader
        if lname in ("jaws.exe", "jfw.exe", "nvda.exe"):
            return True
    return False
