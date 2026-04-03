"""
Screen Reader Detection Utility
Detects if a screen reader is running on Windows.
"""
import psutil


def is_screen_reader_active():
    """
    Returns True if a screen reader is running, otherwise False.
    """
    for proc in psutil.process_iter(['name']):
        name = proc.info['name']
        if name is None:
            continue
        lname = name.lower()
        if lname in ('jaws.exe', 'jfw.exe', 'nvda.exe'):
            return True
    return False
