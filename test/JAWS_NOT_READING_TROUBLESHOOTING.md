# JAWS Not Reading Qt Application - Troubleshooting Guide

## Current Status
- ✓ `QAccessible.isActive()` returns `True` - JAWS is detecting the app
- ✓ Application starts successfully
- ✗ JAWS cursor cannot read screen content
- ✗ Status bar not being announced
- ✗ Selection not being announced
- ⚠ JAWS reports window class as `Qt6101QWindowIcon` (suspicious - should be Qt6QWidget)

## The Problem

Even though Qt reports accessibility is active, JAWS sees the window as `Qt6101QWindowIcon` which suggests Qt's Windows UIA bridge isn't properly exposing the accessible hierarchy. This is a **known limitation with Qt 6.x on Windows**.

## Correct JAWS Commands (for reference)

| Command | Function |
|---------|----------|
| Insert+T | Read window title |
| Insert+F5 | List form fields/controls |
| Insert+F7 | List links |
| Numpad Plus | Toggle JAWS cursor on/off |
| Insert+Ctrl+F1 | Get technical window info |
| Insert+Home | Read current line |
| Insert+Up Arrow | Read from cursor to top |
| Insert+Down Arrow | Read from cursor to bottom |

**Note:** Insert+F6 and F7 are NOT standard JAWS commands.

## Root Cause Analysis

The window class `Qt6101QWindowIcon` indicates Qt is not properly registering the main window with Windows UI Automation (UIA). Possible causes:

1. **Qt 6.x UIA Bridge Issue** - Qt 6.0-6.5 had incomplete Windows UIA support
2. **Missing Platform Plugin** - Windows accessibility bridge DLL might be missing or outdated
3. **Window Role Not Set** - Main window needs explicit role declaration
4. **Status Bar Not Exposed** - Status bar might not be in the accessible tree

## Solutions to Try

### Solution 1: Test with Minimal Application

Run the test script I created:

```bash
python test_jaws_accessibility.py
```

This creates a minimal Qt application to verify if the issue is Qt-specific or our code-specific.

**What to test:**
1. Start JAWS FIRST
2. Run the test script
3. Use Insert+T to read title
4. Use Numpad Plus to enable JAWS cursor
5. Try to read the window content
6. Press Tab to move to button
7. Check if status bar is readable

If the test app works but AbCS doesn't, the issue is in our code.
If the test app also fails, the issue is Qt/JAWS compatibility.

### Solution 2: Check Qt Version and UIA Bridge

```python
# Check PySide6 version
python -c "from PySide6 import __version__; print(__version__)"
```

**Required:** PySide6 6.6 or higher for proper UIA support

**Check for UIA bridge DLL:**
```python
import PySide6
from pathlib import Path

pyside_path = Path(PySide6.__file__).parent
plugins_accessible = pyside_path / 'plugins' / 'accessible'

print(f"PySide6 location: {pyside_path}")
print(f"\nAccessibility plugins:")
if plugins_accessible.exists():
    for dll in plugins_accessible.glob('*.dll'):
        print(f"  ✓ {dll.name}")
else:
    print("  ✗ No accessibility plugins found!")
```

**Expected files:**
- `qwindowsaccessibility.dll` (legacy)
- OR `qwindowsuiaa.dll` (modern UIA bridge - preferred)

### Solution 3: Force Windows MSAA Mode

Qt 6.x prefers UIA but can fall back to MSAA (older but more compatible):

Add this to `src/main.py` BEFORE creating QApplication:

```python
import os
os.environ['QT_QPA_PLATFORM'] = 'windows:accessibility=msaa'
```

This forces Qt to use the older (but more stable) MSAA accessibility instead of UIA.

### Solution 4: Use QAccessible::Announcement Events

Instead of just setting accessible names, use announcement events that force JAWS to speak:

```python
from PySide6.QtGui import QAccessibleAnnouncementEvent, QAccessible

def announce_to_jaws(widget, message):
    """Force JAWS to announce a message immediately."""
    if QAccessible.isActive():
        event = QAccessibleAnnouncementEvent(
            widget,
            message,
            QAccessible.AnnouncementPoliteness.Assertive
        )
        QAccessible.updateAccessibility(event)
```

This should work even if the accessible tree isn't perfect.

### Solution 5: Try with NVDA Instead

NVDA (free screen reader) sometimes works better with Qt:

1. Download NVDA: https://www.nvaccess.org/
2. Install and run NVDA
3. Test AbCS with NVDA
4. Check if NVDA can read the interface

If NVDA works but JAWS doesn't, it's a JAWS-specific compatibility issue.

### Solution 6: Check JAWS Settings

JAWS might have disabled Qt applications:

1. In JAWS, press Insert+F2 (JAWS Manager)
2. Go to Options → Suppress Accessibility
3. Make sure Python.exe or your app isn't in the suppressed list
4. Try adding AbCS to the exception list

### Solution 7: Enable Qt Accessibility Logging

Add debug output to see what Qt is doing:

```python
# In src/main.py, before QApplication
import os
os.environ['QT_LOGGING_RULES'] = 'qt.accessibility*=true'
```

This will print detailed accessibility debug info to console.

## Testing Checklist

Run through these tests systematically:

- [ ] 1. Verify JAWS 2026 is running (Insert+J to check version)
- [ ] 2. Check PySide6 version is 6.6+ (`python -c "from PySide6 import __version__; print(__version__)"`)
- [ ] 3. Verify qwindowsuiaa.dll or qwindowsaccessibility.dll exists
- [ ] 4. Run `test_jaws_accessibility.py` and test if THAT works
- [ ] 5. Try forcing MSAA mode (Solution 3)
- [ ] 6. Test with NVDA to rule out JAWS-specific issues
- [ ] 7. Check JAWS suppress list for Python/Qt applications
- [ ] 8. Enable Qt accessibility logging

## Expected Behavior (Once Working)

### Window Title
- Press Insert+T
- Should hear: "JAWS Accessibility Test" or "AbCS Main Window"

### Status Bar
- Press Insert+Numpad 0 (read active window)
- Should include status bar content at the end
- OR use JAWS cursor (Numpad Plus) and navigate to bottom

### Table Navigation
- Tab to table
- Arrow keys navigate cells
- Should announce: "Row X, Column Y, [Content]"

### Selection
- Ctrl+Click to select
- Should announce: "Title: [Book Name] selected"

## What We've Done

1. ✓ Added `QAccessible.setActive(True)` in main.py
2. ✓ Added `QAccessible.setRootObject(app)` to anchor tree
3. ✓ Set accessible name/description on main window
4. ✓ Set accessible name/description on status bar
5. ✓ Set accessible properties on all major widgets
6. ✓ Created test script to isolate the issue

## Next Steps

1. **Run the test script** (`python test_jaws_accessibility.py`)
   - If it works → Issue is in AbCS code (we can fix)
   - If it fails → Issue is Qt/JAWS compatibility (harder to fix)

2. **Check Qt version and UIA bridge DLL**
   - Upgrade PySide6 if needed: `pip install --upgrade PySide6`

3. **Try MSAA mode** (Solution 3)
   - Add environment variable before QApplication
   - MSAA is older but more compatible with JAWS

4. **Test with NVDA**
   - Free download, easy to test
   - Helps narrow down if it's JAWS-specific

5. **Report findings**
   - Which test worked/failed
   - Qt/PySide6 version
   - Whether UIA bridge DLL exists
   - NVDA results (if tested)

## Known Qt 6.x Accessibility Issues

- Qt 6.0-6.5: Incomplete UIA implementation on Windows
- Qt 6.6+: Improved but still not perfect
- Qt 6.8+: Better UIA support planned
- MSAA mode is more stable but has fewer features

## Alternative Approaches (If Nothing Works)

If Qt accessibility fundamentally doesn't work with JAWS 2026:

1. **Custom Speech Output** - Use Windows SAPI to speak directly
2. **Explicit Announcements** - Use QAccessibleAnnouncementEvent for everything
3. **Wait for Qt 6.8+** - Better Windows accessibility planned
4. **Consider Qt 5.15** - Older but more stable MSAA support

---

**Bottom Line:** The `Qt6101QWindowIcon` class suggests Qt isn't properly exposing the window to Windows accessibility. This is likely a Qt 6.x limitation, not our code. The test script will help determine if it's fixable or a fundamental Qt issue.
