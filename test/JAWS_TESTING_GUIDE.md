# JAWS Screen Reader Testing Guide for AbCS

## Prerequisites

1. **JAWS must be running FIRST** - Before you start the AbCS application
2. **Qt 6.5+** - Required for proper Windows UIA bridge support
3. **Windows 10/11** - JAWS communicates via Windows UI Automation (UIA)

## How JAWS Integration Works

```
JAWS Screen Reader (Active)
        ↓
Windows UI Automation (UIA) Bridge
        ↓
Qt 6.x Application (AbCS)
        ↓
Our Accessibility Code
```

**Critical:** If JAWS is NOT running, then Windows UIA is not active, and `QAccessible.isActive()` will return `False`.

## Step-by-Step Testing Instructions

### Step 1: Start JAWS First

1. Open JAWS (before starting AbCS)
2. Let it fully load
3. You should hear JAWS speak

### Step 2: Run AbCS with Accessibility Diagnostics

1. Open Command Prompt or PowerShell
2. Navigate to the AbCS directory
3. Run: `python src/main.py`
4. **Watch the console output** for the accessibility diagnostics
5. Look for lines like:
   ```
   ============================================================
   ACCESSIBILITY DIAGNOSTICS
   ============================================================
   QAccessible.isActive(): False    ← Should be True if JAWS is running
   QApplication found: True
   QApplication has accessible interface: True
   ```

### Step 3: Interpret the Results

#### If `QAccessible.isActive(): True` ✅

- JAWS detected our application
- The Windows UIA bridge is working
- AbCS should be readable by JAWS

**What to test:**
- Use JAWS Cursor (Insert+F1) to navigate
- Press Insert+F7 to hear window title
- Press Insert+F6 to hear status bar
- Arrow keys should announce elements as you move through them

#### If `QAccessible.isActive(): False` ❌

- JAWS is either not running or didn't detect the application
- The Windows UIA bridge isn't active

**What to try:**
1. Make sure JAWS is fully loaded (wait 10-15 seconds after starting it)
2. Close AbCS and try again
3. Restart JAWS and then start AbCS
4. Check if JAWS has detected any other Qt applications
5. Verify JAWS is set to monitor this type of application

### Step 4: Test Specific UI Elements

If accessibility is active, test these:

| Element | Test Method |
|---------|-------------|
| **Status Bar** | Press Insert+F6 while in the app window. Should read "Ready" or current status message |
| **Window Title** | Press Insert+F7. Should read "AbCS - Audio Book Collector Scanner" |
| **Table** | Press Tab to move to table, then use arrow keys. Should announce rows and columns |
| **Buttons** | Tab to buttons like "Update" or "Delete". Should announce button names |
| **Search Box** | Tab to search field. Should say "Search, Edit" |
| **Menus** | Press Alt+M. Should announce menu options |

### Step 5: Test Table Navigation

1. Tab to the book table
2. Press Down arrow to move through rows
3. Expected: JAWS announces "Row X, Column Y: [Content]"
4. Press Ctrl+Home to go to first cell
5. Press Ctrl+End to go to last cell

### Step 6: Check for Font/Color Information

This is more advanced. Qt's accessibility doesn't expose font/color by default. To make it work:

1. **For now**, these are not accessible - this is a limitation of Qt's standard accessibility
2. We may need to add custom accessibility interfaces if color/font reporting is critical

## Troubleshooting

### Problem: `QAccessible.isActive()` is False

**Cause:** JAWS is not running when the application starts

**Solutions:**
1. Start JAWS FIRST (before AbCS)
2. Wait for JAWS to fully initialize (10-15 seconds)
3. Then start AbCS
4. Check that JAWS hasn't disabled notifications for your application

### Problem: Can hear JAWS but can't hear the application

**Possible Causes:**

1. **Windows UIA bridge not loaded** - Check that these files exist in your Qt installation:
   - `plugins/platforms/qwindowsuiaa.dll` (NEW in Qt 6.6+)
   - OR `plugins/accessible/qwindowsaccessibility.dll` (older version)

2. **Qt version too old** - Qt 6.0-6.5 had incomplete UIA support
   - Check Qt version: Run `python -c "from PySide6 import __version__; print(__version__)"`
   - Should be 6.6+

3. **JAWS not detecting our application** - Try:
   - Closing and restarting AbCS while JAWS is running
   - Check JAWS settings for disabled applications
   - Try JAWS on a different Qt application (e.g., if you have Qt Creator)

### Problem: Status bar not being announced

**Root Causes:**
1. We're letting Qt handle it natively (it should work automatically)
2. If it's not being announced, it may be a JAWS setting
3. Try pressing Insert+F6 to force status bar reading

### Problem: Missing Qt UIA DLL

If `qwindowsuiaa.dll` is missing from your Qt installation:

```python
# Add this code to check which accessibility bridge is loaded
import os
qt_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
plugins_path = os.path.join(qt_path, 'plugins')
print("Qt plugins path:", plugins_path)
print("Files in plugins/accessible/:")
a11y_path = os.path.join(plugins_path, 'accessible')
if os.path.exists(a11y_path):
    print(os.listdir(a11y_path))
else:
    print("  (directory does not exist)")
```

## Advanced Testing

### Test with JAWS Inspector

1. Start AbCS (with JAWS running)
2. In JAWS, press Alt+Insert+J (or navigate to Utility → Inspector)
3. Use JAWS Inspector to view the UIA tree of the application
4. Look for:
   - Application element
   - MainWindow
   - StatusBar
   - Table
   - Buttons

This shows exactly what JAWS can see.

### Test with NVDA (Alternative Screen Reader)

NVDA is free and open-source. You can use it to verify accessibility:

1. Download NVDA: https://www.nvaccess.org/
2. Start NVDA
3. Start AbCS
4. Test navigation with NVDA
5. If NVDA works but JAWS doesn't, it's a JAWS-specific issue

### Enable Qt Accessibility Logging

For detailed debugging, you can enable Qt's accessibility logging:

```python
# Add to src/main.py before creating QApplication
import os
os.environ['QT_ACCESSIBILITY_DEBUG'] = '1'  # Experimental - may not work on all Qt versions
```

## What We've Done to Support Accessibility

1. ✅ **Enabled QAccessible** with `QAccessible.setActive(True)`
2. ✅ **Set root object** with `QAccessible.setRootObject(app)` - ensures accessibility tree is anchored
3. ✅ **Set widget names** via `setAccessibleName()` and `setAccessibleDescription()`
4. ✅ **Emit proper events** when content changes (NameChanged, Selection, ValueChanged, etc.)
5. ✅ **Used standard Qt roles** (StatusBar, Table, Button, etc.) so JAWS recognizes them
6. ✅ **Added diagnostic output** to verify setup is correct

## What's Still Not Supported (Limitations)

1. **Font/Color reporting** - Qt's standard accessibility doesn't expose this by default
   - Would require custom QAccessibleInterface implementation
   - JAWS can still describe elements by role and content

2. **Complex table cell content** - We report row/column; complex formatting isn't exposed
   - Would need QAccessibleTableCellInterface implementation

3. **Live region announcements** - Status changes aren't "live announced" yet
   - We could implement QAccessibleAnnouncementEvent for this

## Expected Behavior (Once Working)

### Status Bar (Most Important - What User Noticed)
- User presses Insert+F6 (JAWS command for status bar)
- JAWS reads: "Ready" or current status message
- ✅ This should work with our current implementation

### Navigation Through Menus
- Alt+M opens File menu
- Arrow keys navigate menu items
- JAWS reads each menu item
- ✅ This should work automatically with Qt

### Table Navigation
- Tab to table, arrow keys navigate
- JAWS reads: "Row 1, Column 2: Title by Author, 6 hours"
- ✅ This should work with our table setup

## How to Get Help

1. **Check JAWS version** - Ensure it's up to date
2. **Check Qt version** - Ensure PySide6 is 6.6+
3. **Verify accessibility is active** - Check console output for "QAccessible.isActive(): True"
4. **Test with NVDA** - To rule out JAWS-specific issues
5. **Report to JAWS/Qt support** - If it's a compatibility issue

## Key Insight

The main thing we discovered: **JAWS must be running BEFORE the application starts**. That's why `QAccessible.isActive()` might return False - not because of an error in our code, but because JAWS wasn't active when the app initialized.

The Windows UIA bridge exists in Qt 6.6+, but it only activates when a screen reader (JAWS, NVDA, etc.) is actually listening for accessibility events.
