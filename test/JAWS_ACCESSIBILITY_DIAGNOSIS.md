# JAWS Accessibility Diagnosis - Critical Finding

## Problem Summary
JAWS screen reader cannot detect or read ANY content from the Qt/PySide6 application, including:
- Status bar messages
- Font/color information  
- Table content
- Any other UI elements

Even though `QAccessible.setActive(True)` was added and `setAccessibleName()` is being called.

## Root Cause Analysis

### Critical Issue: Windows Native Accessibility Bridge is Missing

Qt's accessibility on Windows relies on **Windows UIA (UI Automation) Bridge** - a native Windows component that translates Qt's accessibility objects into Windows native accessibility APIs that JAWS understands.

**The Problem:**
1. Qt provides `QAccessible` (the Qt accessibility API)
2. Windows needs `IAccessible2` or **UIA (UI Automation)** to communicate with JAWS
3. Qt has platform bridges to convert Qt accessibility → Windows native APIs
4. **For QWidget applications on Windows, the UIA bridge must be properly initialized**

### Why `setActive()` Alone Isn't Enough

Even with `QAccessible.setActive(True)`:
- Qt's internal accessibility tree is enabled
- But Windows/JAWS still can't see it without the platform bridge
- The bridge is typically initialized automatically, but may fail silently

### What JAWS Actually Needs (On Windows)

JAWS doesn't read from Qt directly. It reads from:
1. **IAccessible2 (IA2)** - older COM-based accessibility (MSAA)
2. **UI Automation (UIA)** - newer Windows accessibility framework (preferred)
3. **NVDA API** - for NVDA specifically

Qt must bridge to one of these. The Qt UIA bridge (in `qtbase/src/plugins/platforms/windows/`) converts Qt objects to Windows UIA objects.

## Key Discoveries from Research

### From Qt Documentation
- **Status Bar Role:** Qt has `QAccessible::StatusBar` as a standard role
- **Widget Information Flow:** 
  - `setAccessibleName()` → Sets the Name property
  - `setAccessibleDescription()` → Sets the Description property  
  - `QAccessibleEvent()` → Notifies the platform of changes
  - But all of this goes through the **UIA bridge** to reach JAWS

- **Tree Navigation:** JAWS uses:
  1. `QAccessibleInterface::parent()` - navigates up
  2. `QAccessibleInterface::child()` - navigates down
  3. `QAccessibleInterface::text()` - gets Name, Description, Value, etc.

- **Event Types Relevant to Status Bars:**
  - `NameChanged` (0x800C) - what we're using (correct)
  - `Announcement` (0x80D0) - for urgent announcements
  - `Alert` (0x0002) - for system alerts

### The QStatusBar Specific Issue

Standard `QStatusBar` should already have accessibility support built-in. However:
1. We're calling `setAccessibleName()` which may conflict with its default behavior
2. We're sending `NameChanged` events which may not be the right approach for status bars
3. Status bars may need special handling

## Potential Solutions (In Order of Priority)

### Solution 1: Enable Environment Variable for Windows Accessibility
Add this **before** QApplication creation:

```python
import os
os.environ['QT_LINUX_ACCESSIBILITY_ALWAYS_ON'] = '1'  # For Linux
# Windows equivalents aren't well documented, but try:
# os.environ['QT_ACCESSIBILITY_ALWAYS_ON'] = '1'
```

**Note:** Linux has this; Windows should use the platform bridge automatically.

### Solution 2: Call setRootObject() Explicitly

```python
from PySide6.QtGui import QAccessible
from PySide6.QtWidgets import QApplication

app = QApplication(sys.argv)
QAccessible.setActive(True)
QAccessible.setRootObject(app)  # Explicitly set root for accessibility tree
```

### Solution 3: Stop Manually Managing Status Bar Accessibility

Instead of manually calling `setAccessibleName()` and `updateAccessibility()`, let Qt handle it natively:

```python
# WRONG (what we're doing):
status_bar.setAccessibleName(message)
event = QAccessibleEvent(status_bar, QAccessible.Event.NameChanged)
QAccessible.updateAccessibility(event)

# RIGHT (let Qt handle native status bar updates):
status_bar.showMessage(message)  # This is sufficient
# Qt's built-in QStatusBar accessibility handles the rest
```

### Solution 4: Use QAccessibleAnnouncementEvent for Important Messages

For messages that should be announced immediately by screen readers:

```python
from PySide6.QtGui import QAccessibleAnnouncementEvent, QAccessible

def announce_important_message(parent_widget, message):
    """Announce a message immediately to screen readers."""
    if QAccessible.isActive():
        # Use Announcement event (0x80D0) instead of NameChanged
        event = QAccessibleAnnouncementEvent(
            parent_widget, 
            message,
            QAccessible.AnnouncementPoliteness.Assertive  # Interrupt current speech
        )
        QAccessible.updateAccessibility(event)
```

### Solution 5: Verify Qt UIA Bridge is Loaded

Check that Qt's UIA bridge plugin is actually being used:

```python
# Add diagnostic code to check platform accessibility bridge
from PySide6.QtGui import QAccessible

def check_accessibility_support():
    """Debug: Check if accessibility is properly initialized."""
    print("QAccessible.isActive():", QAccessible.isActive())
    
    # Check for active accessibility interfaces
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance()
    if app:
        iface = QAccessible.queryAccessibleInterface(app)
        print("QApplication has accessible interface:", iface is not None)
        if iface:
            print("  Role:", iface.role())
            print("  Name:", iface.text(QAccessible.Text.Name))
```

### Solution 6: Check for Required DLLs (Windows)

On Windows, verify these Qt plugins exist:
- `platforms/qwindows.dll` - Windows platform plugin
- `platforms/qwindowsuiaa.dll` - Windows UIA accessibility bridge (NEW in Qt 6.x)
- `plugins/accessible/qwindowsaccessibility.dll` - legacy accessibility

Missing UIA bridge = JAWS can't communicate with Qt app.

## Recommended Immediate Actions

1. **Add explicit `setRootObject()` call:**
   ```python
   # In src/main.py, after QApplication creation:
   QAccessible.setRootObject(app)
   ```

2. **Stop manually managing status bar accessibility:**
   ```python
   # In accessible_events.py announce_status_message():
   def announce_status_message(status_bar: QStatusBar, message: str) -> None:
       status_bar.showMessage(message)
       # Let Qt's built-in accessibility handle the rest
   ```

3. **Verify Windows UIA bridge is loaded:**
   - Check your Qt installation for `qwindowsuiaa.dll`
   - If missing, you may need to rebuild Qt with UIA support

4. **Test with diagnostic script:**
   - Create a test script that checks `QAccessible.isActive()` 
   - Verify accessibility interfaces exist for all widgets

## Why We're Not Hearing Anything

```
JAWS → Windows UIA → Qt UIA Bridge → QAccessible → Our Code
                      ↑ 
                 THIS IS MISSING OR BROKEN
```

Without the UIA bridge properly initialized and working, JAWS sees nothing.

## Next Steps for User

1. **Simplify accessibility code** - Remove manual event management for now
2. **Explicitly call `setRootObject()`** - Ensure accessibility tree is anchored
3. **Check Qt installation** - Verify UIA bridge DLL exists
4. **Test with diagnostic code** - Print out what accessibility sees
5. **Consider using `QAccessibleAnnouncementEvent`** - For important messages that must be spoken
6. **Review Qt version** - Older Qt versions had incomplete UIA support; Qt 6.6+ has better support

## Additional Resources

- Qt Accessibility Documentation: https://doc.qt.io/qt-6/accessible.html
- Qt Accessibility for Widgets: https://doc.qt.io/qt-6/accessible-qwidget.html
- QAccessible Event Types: https://doc.qt.io/qt-6/qaccessible.html#Event-enum
- Windows UI Automation: https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-overview
- JAWS/NVDA debugging tips: Use JAWS Inspector or NVDA Log Viewer while running your app

---

**Summary:** The issue is almost certainly the Windows UIA platform bridge not being properly initialized or loaded. Adding `QAccessible.setRootObject(app)` and verifying the UIA bridge DLL exists are the most likely fixes.
