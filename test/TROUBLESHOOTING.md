# Qt Accessibility Not Working - Troubleshooting Guide

## Your Situation

**Tests run:**
1. ✅ Basic test - Virtual cursor works, Tab navigation silent
2. ✅ MSAA mode - No change, still broken
3. Window class: `Qt6102QWindowIcon` (This is WRONG)

**The problem:** Qt's Windows accessibility bridge is not creating an accessible control tree. JAWS can read pixels (virtual cursor) but cannot navigate the semantic structure (forms mode).

---

## Critical Tests to Run Now

### 1. Run Diagnostics (REQUIRED)

```cmd
run_diagnostics.bat
```

**Share the entire output.** We need to know:
- Your Qt version (must be 6.6+)
- Whether accessibility plugins exist
- Your Windows version

### 2. Try Native Windows

```cmd
run_jaws_native_window.bat
```

Check if window class changes with Insert+Ctrl+F1.

### 3. Try Tkinter (Comparison)

```cmd
python test\test_tkinter_basic.py
```

If Tkinter works but Qt doesn't, confirms Qt-specific issue.

### 4. Try SAPI Workaround (Bypass Qt)

```cmd
run_sapi_workaround.bat
```

This speaks directly using Windows SAPI, bypassing Qt entirely.

---

## Potential Root Causes

### Cause 1: Qt Version Too Old

Qt 6.5 and earlier have broken UIA support on many systems.

**Fix:**
```cmd
python -c "from PySide6.QtCore import qVersion; print(qVersion())"
pip install --upgrade PySide6
```

Must be 6.6.0 or higher.

### Cause 2: Corrupted Qt Installation

Accessibility plugins may be missing or corrupted.

**Fix:**
```cmd
pip uninstall PySide6
pip cache purge
pip install PySide6
```

### Cause 3: Windows Accessibility Disabled

Windows UI Automation service might be disabled.

**Check:**
1. Press Win+R, type `services.msc`
2. Find "Windows UI Automation Core Service"
3. Ensure it's set to "Automatic" and "Running"

### Cause 4: JAWS Configuration Issue

JAWS might not be configured to handle Qt applications.

**Try:**
1. JAWS Settings Center
2. Search for "Forms Mode"
3. Disable "Use virtual cursor in all applications"
4. Enable "Automatically switch to forms mode"

### Cause 5: Qt Platform Plugin Issue

Qt might be using wrong platform plugin.

**Try:**
```cmd
set QT_QPA_PLATFORM=windows
python test\test_jaws_basic.py
```

---

## If Nothing Works: SAPI Workaround

If Qt's accessibility is fundamentally broken on your system, we can bypass it entirely using Windows SAPI (Speech API). This makes your app speak directly to JAWS without going through Qt's bridge.

**Pros:**
- Works even with completely broken Qt accessibility
- Direct control over what's announced
- Can customize announcements

**Cons:**
- More code to maintain
- Need to manually handle every focus change
- Need pywin32 library

**Implementation:**
```python
import win32com.client

def announce(text):
    """Announce text to screen reader via SAPI."""
    try:
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        speaker.Speak(text, 1)  # Async
    except:
        pass  # Fail silently if SAPI unavailable

# Use in focus handlers
def button_focus(event):
    announce("Click Me button")
    # ... rest of handler
```

---

## Known Qt 6 + JAWS Issues

Qt 6's UIA bridge has known issues on some Windows configurations:

1. **Windows 10 1809 or older**: UIA bridge incomplete
2. **JAWS 2020 and earlier**: Poor Qt 6 UIA support
3. **Qt 6.5.x**: Multiple UIA bugs fixed in 6.6+
4. **Windows N editions**: May lack media features UIA depends on

---

## What to Report Back

Please run and share output from:

1. **Diagnostics:**
   ```cmd
   run_diagnostics.bat
   ```

2. **Qt version:**
   ```cmd
   python -c "from PySide6.QtCore import qVersion; print('Qt:', qVersion())"
   ```

3. **JAWS version:**
   - Help → About JAWS (what version?)

4. **Windows version:**
   - Win+R, type `winver` (what build number?)

5. **Native windows test result:**
   ```cmd
   run_jaws_native_window.bat
   ```
   - Did window class change?

6. **Tkinter test result:**
   ```cmd
   python test\test_tkinter_basic.py
   ```
   - Does Tab navigation work?

With this information, I can determine if:
- You need to upgrade Qt
- Your Qt installation is corrupted
- We need to use the SAPI workaround
- There's a system configuration issue

---

## Emergency Workaround: Use NVDA Instead

NVDA (free screen reader) has better Qt support than JAWS in some cases.

**Download:** https://www.nvaccess.org/download/

**Test with NVDA:**
1. Close JAWS
2. Start NVDA
3. Run: `python test\test_jaws_basic.py`
4. Try Tab navigation

If NVDA works but JAWS doesn't, it's a JAWS-specific configuration issue.
