"""Accessibility package for AbCS."""

from .scaling import UIScaler, get_scaler
from .theme_manager import ThemeManager, get_theme_manager, ThemeName
from .shortcuts import ShortcutManager, get_shortcut_manager, ShortcutContext

__all__ = [
    'UIScaler', 'get_scaler',
    'ThemeManager', 'get_theme_manager', 'ThemeName',
    'ShortcutManager', 'get_shortcut_manager', 'ShortcutContext'
]
