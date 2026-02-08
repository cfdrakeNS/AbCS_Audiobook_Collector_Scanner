# Debugging and Verification Script for Qt Accessibility

This document explains how to check if your Qt installation is properly configured for accessibility.

## Quick Checks

### 1. Check PySide6 Version

```python
from PySide6 import __version__
print(f"PySide6 Version: {__version__}")
# Should be 6.6 or higher for proper UIA support
```

If less than 6.6, you may have incomplete Windows UIA bridge support.

### 2. Check if JAWS (or NVDA) is Running

On Windows, you can check this in Python:

```python
import subprocess
import sys

def check_jaws_running():
    """Check if JAWS or NVDA is currently running."""
    try:
        # Check for JAWS
        tasklist = subprocess.check_output(['tasklist'], universal_newlines=True)
        if 'jaws.exe' in tasklist.lower():
            print("✓ JAWS is running")
            return True
        if 'nvda.exe' in tasklist.lower():
            print("✓ NVDA is running")
            return True
        print("✗ No screen reader detected (JAWS or NVDA)")
        return False
    except Exception as e:
        print(f"Could not check: {e}")
        return False

check_jaws_running()
```

### 3. Check Qt Plugin Files

```python
import sys
from pathlib import Path

def find_qt_plugins():
    """Find and list Qt accessibility plugin DLLs."""
    try:
        # Find PySide6 installation
        import PySide6
        pyside_path = Path(PySide6.__file__).parent
        
        # Check for accessibility plugins
        plugin_paths = [
            pyside_path / 'plugins' / 'accessible',
            pyside_path / 'plugins' / 'platforms',
        ]
        
        print("Qt Plugin Locations:")
        for plugin_dir in plugin_paths:
            print(f"\n{plugin_dir}:")
            if plugin_dir.exists():
                for dll in plugin_dir.glob('*.dll'):
                    print(f"  ✓ {dll.name}")
                # Also check for .so (Linux) and .dylib (macOS)
                for so in plugin_dir.glob('*.so'):
                    print(f"  ✓ {so.name}")
                for dylib in plugin_dir.glob('*.dylib'):
                    print(f"  ✓ {dylib.name}")
                if not list(plugin_dir.glob('*')):
                    print("  (empty)")
            else:
                print("  (directory not found)")
    except Exception as e:
        print(f"Error: {e}")

find_qt_plugins()
```

Expected output on Windows should include:
- `qwindows.dll` - Windows platform plugin
- `qwindowsuiaa.dll` - Windows UIA accessibility bridge (NEW in Qt 6.6+)
- OR `qwindowsaccessibility.dll` - Legacy accessibility plugin

### 4. Check Accessibility at Runtime

Add this to your application startup:

```python
from PySide6.QtGui import QAccessible
from PySide6.QtWidgets import QApplication

def diagnose_accessibility():
    """Check accessibility status at runtime."""
    print("\nAccessibility Diagnosis:")
    print("-" * 50)
    
    # Check if accessibility is enabled
    is_active = QAccessible.isActive()
    print(f"QAccessible.isActive(): {is_active}")
    
    if not is_active:
        print("  → Screen reader not detected (JAWS/NVDA not running?)")
        print("  → Or UIA bridge not initialized")
    else:
        print("  ✓ Screen reader or accessibility tool is active")
    
    # Check QApplication
    app = QApplication.instance()
    if app:
        print(f"\nQApplication Status:")
        print(f"  Application name: {app.applicationName()}")
        
        # Query accessibility interface
        iface = QAccessible.queryAccessibleInterface(app)
        if iface:
            print(f"  ✓ Has accessible interface")
            print(f"  Role: {iface.role()}")
            print(f"  Name: {iface.text(QAccessible.Text.Name)}")
        else:
            print(f"  ✗ No accessible interface")
    
    print("-" * 50 + "\n")

# Call this after creating QApplication
diagnose_accessibility()
```

## Environment Variables (for advanced users)

### Linux
To force accessibility even without a screen reader:
```bash
export QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1
python src/main.py
```

### Windows
There's no direct equivalent, but you can:
1. Start JAWS/NVDA first
2. Then start your application
3. The UIA bridge will activate automatically

### Mac
```bash
export QT_ACCESSIBILITY_DEBUG=1  # Experimental
python src/main.py
```

## Troubleshooting DLL Issues

If you're missing `qwindowsuiaa.dll`, you have options:

### Option 1: Upgrade PySide6
```bash
pip install --upgrade PySide6
```

Check version after upgrade:
```python
from PySide6 import __version__
print(__version__)  # Should be 6.6 or higher
```

### Option 2: Rebuild with UIA Support (Advanced)

If upgrading doesn't work, you may need to rebuild Qt with UIA support:

```bash
# This is complex and requires Qt source code
# See: https://doc.qt.io/qt-6/windows-accessibility.html
```

### Option 3: Check for Hybrid Accessibility

Some Qt installations provide both:
- Legacy: `qwindowsaccessibility.dll` - MSAA (older, less complete)
- Modern: `qwindowsuiaa.dll` - UIA (newer, more complete)

If you only have the legacy version, JAWS may have limited support.

## Testing Script

Create a file `test_accessibility.py`:

```python
#!/usr/bin/env python3
"""
Test script to verify Qt accessibility is properly configured.
Run this with JAWS running to test actual screen reader support.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from PySide6.QtWidgets import QApplication, QMainWindow, QStatusBar, QPushButton, QVBoxLayout, QWidget
from PySide6.QtGui import QAccessible
from PySide6.QtCore import Qt

def main():
    app = QApplication(sys.argv)
    
    # Enable accessibility
    QAccessible.setActive(True)
    QAccessible.setRootObject(app)
    
    # Create simple test window
    window = QMainWindow()
    window.setWindowTitle("Qt Accessibility Test")
    window.setAccessibleName("Qt Accessibility Test Window")
    
    # Central widget
    central = QWidget()
    layout = QVBoxLayout(central)
    window.setCentralWidget(central)
    
    # Test button
    button = QPushButton("Test Button")
    button.setAccessibleName("Test Button")
    button.setAccessibleDescription("Click this button to test accessibility")
    layout.addWidget(button)
    
    # Status bar
    status = window.statusBar()
    status.showMessage("Accessibility Test Ready")
    status.setAccessibleName("Status Bar")
    
    # Print diagnostics
    print("\n" + "="*60)
    print("ACCESSIBILITY TEST")
    print("="*60)
    print(f"QAccessible.isActive(): {QAccessible.isActive()}")
    
    iface = QAccessible.queryAccessibleInterface(app)
    print(f"QApplication has interface: {iface is not None}")
    
    window_iface = QAccessible.queryAccessibleInterface(window)
    print(f"QMainWindow has interface: {window_iface is not None}")
    
    button_iface = QAccessible.queryAccessibleInterface(button)
    print(f"QPushButton has interface: {button_iface is not None}")
    
    status_iface = QAccessible.queryAccessibleInterface(status)
    print(f"QStatusBar has interface: {status_iface is not None}")
    
    print("="*60)
    print("\nTEST INSTRUCTIONS:")
    print("1. Start this with JAWS running")
    print("2. If QAccessible.isActive() is True, JAWS detected the app")
    print("3. Use JAWS Cursor to navigate window")
    print("4. Press Insert+F6 to read status bar")
    print("5. Press Tab to move to button and hear it announced")
    print("="*60 + "\n")
    
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
```

Run it with:
```bash
python test_accessibility.py
```

With JAWS running, you should be able to navigate the window and hear elements announced.

## References

- **Qt Accessibility (official):** https://doc.qt.io/qt-6/accessible.html
- **Qt QWidget Accessibility:** https://doc.qt.io/qt-6/accessible-qwidget.html
- **Windows UI Automation:** https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-overview
- **JAWS Documentation:** https://www.freedomscientific.com/products/software/jaws/
- **NVDA (Free Screen Reader):** https://www.nvaccess.org/

## Summary

The key things to verify:

1. ✓ PySide6 version 6.6+
2. ✓ JAWS/NVDA is running before the application starts
3. ✓ `qwindowsuiaa.dll` exists in Qt plugins directory
4. ✓ `QAccessible.isActive()` returns `True` when screen reader is active
5. ✓ `QAccessible.queryAccessibleInterface(widget)` returns a valid interface for major widgets

If all of these check out, accessibility should be working.
