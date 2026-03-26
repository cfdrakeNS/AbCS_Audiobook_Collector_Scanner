"""
Screen Reader Detection Utility
Detects if JAWS or NVDA is running on Windows.
"""
import psutil


def detect_screen_reader():
    """
    Returns:
        'JAWS' if JAWS is running
        'NVDA' if NVDA is running
        None if neither is running
    """
    for proc in psutil.process_iter(['name']):
        name = proc.info['name']
        if name is None:
            continue
        lname = name.lower()
        if lname in ('jaws.exe', 'jfw.exe'):
            return 'JAWS'
        if lname == 'nvda.exe':
            return 'NVDA'
    return None
