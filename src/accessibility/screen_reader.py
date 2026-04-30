"""
Screen Reader Detection Utility
Detects if a screen reader is running on Windows or Linux.
"""

# Make psutil optional for Linux compatibility
try:
    import psutil
except ImportError:
    psutil = None


def is_screen_reader_active():
    """
    Returns True if a screen reader is running, otherwise False.
    Detects Windows screen readers (JAWS/NVDA) and Linux Orca.
    """
    # psutil not available on Linux or not installed
    if psutil is None:
        return False

    # Screen reader process names by platform
    screen_reader_names = (
        # Windows screen readers
        "jaws.exe",
        "jfw.exe",
        "nvda.exe",
        # Linux screen readers
        "orca",
        "orca-daemon",
    )

    for proc in psutil.process_iter(["name"]):
        name = proc.info["name"]
        if name is None:
            continue
        lname = name.lower()
        # If the process name matches a known screen reader
        if lname in screen_reader_names:
            return True
    return False
