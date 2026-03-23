"""
Windows theme detection workaround for broken Qt system palette detection.
This uses Windows registry to detect dark mode when Qt fails.
"""

import winreg
from typing import Optional

def detect_windows_dark_mode() -> Optional[bool]:
    """
    Detect if Windows is in dark mode using registry.
    
    Returns:
        True if dark mode, False if light mode, None if detection fails
    """
    try:
        # Check Windows 10/11 dark mode setting
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                           r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as key:
            # 0 = light mode, 1 = dark mode
            apps_use_light_theme, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return apps_use_light_theme == 0
    except (WindowsError, OSError):
        try:
            # Fallback to system theme setting
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as key:
                system_use_light_theme, _ = winreg.QueryValueEx(key, "SystemUsesLightTheme")
                return system_use_light_theme == 0
        except (WindowsError, OSError):
            return None

def get_fallback_dark_theme_colors() -> dict:
    """
    Get dark theme colors to use when system detection fails.
    
    Returns:
        Dictionary of dark theme colors
    """
    return {
        'window': '#2B2B2B',
        'window_text': '#E0E0E0',
        'base': '#1E1E1E',
        'text': '#E0E0E0',
        'button': '#3C3C3C',
        'button_text': '#E0E0E0',
        'highlight': '#0078D4',
        'highlight_text': '#FFFFFF',
        'link': '#569CD6',
    }

def get_fallback_light_theme_colors() -> dict:
    """
    Get light theme colors to use when system detection fails.
    
    Returns:
        Dictionary of light theme colors
    """
    return {
        'window': '#F0F0F0',
        'window_text': '#000000',
        'base': '#FFFFFF',
        'text': '#000000',
        'button': '#F0F0F0',
        'button_text': '#000000',
        'highlight': '#0078D4',
        'highlight_text': '#FFFFFF',
        'link': '#0000FF',
    }

if __name__ == "__main__":
    # Test the detection
    dark_mode = detect_windows_dark_mode()
    if dark_mode is True:
        print("Windows is in DARK mode")
    elif dark_mode is False:
        print("Windows is in LIGHT mode")
    else:
        print("Could not detect Windows theme")
