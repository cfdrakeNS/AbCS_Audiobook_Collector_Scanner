# JAWS Reading Fix - Action Plan

## Problem Summary

JAWS 2026 cannot read AbCS application content despite:
- `QAccessible.isActive()` returning `True`
- Accessibility being explicitly enabled in code
- Accessible names/descriptions set on all widgets

**Key Symptom:** Window technical info shows class as `Qt6101QWindowIcon` instead of proper widget class, suggesting Qt's Windows UIA bridge is not properly exposing the application to JAWS.

---

## Immediate Actions to Try (In Order)

### 1. Run Diagnostic Script (5 minutes)

**Purpose:** Determine if this is a Qt-wide issue or AbCS-specific

```cmd
python diagnose_accessibility.py
```

**With JAWS running:**
1. Start JAWS first
2. Run the diagnostic script
3. Try these JAWS commands on the test window:
   - **Insert+T**: Read window title
   - **Insert+Ctrl+F1**: Read technical info
   - **Numpad Plus**: JAWS cursor to read content
   - **Tab**: Navigate to button, **Space** to click

**What to look for:**
- Window class in technical info - should be `Qt6QWidget`, NOT `Qt6101QWindowIcon`
- Can JAWS cursor read the label text?
- Does Tab navigation work and speak button name?

**Report back:** Does the test window work with JAWS?

---

### 2. Try MSAA Mode (5 minutes)

**Purpose:** Use older but more stable accessibility bridge

Qt 6.x has a Windows UIA bridge that's sometimes buggy. MSAA is the older API but more reliable.

```cmd
run_msaa.bat
```

**With JAWS running:**
- Try Insert+T, JAWS cursor (Numpad Plus), navigation
- Check if status bar announcements work
- Try selecting books in the table

**Report back:** Does MSAA mode work better?

---

### 3. Test with NVDA (10 minutes)

**Purpose:** Determine if this is JAWS-specific or screen reader-wide issue

1. Download NVDA (free): https://www.nvaccess.org/download/
2. Install and start NVDA
3. Run AbCS normally: `python src\main.py`
4. Try NVDA commands:
   - **NVDA+T**: Read window title
   - **Numpad Plus**: Object navigation
   - **Tab**: Navigate controls
   - **NVDA+Down Arrow**: Say all

**Report back:** Does NVDA work? If yes, it's JAWS-specific. If no, Qt UIA is broken.

---

### 4. Check PySide6 Version (2 minutes)

**Purpose:** Verify we have Qt 6.6+ which has better accessibility support

```cmd
python -c "from PySide6 import __version__; print('PySide6 version:', __version__)"
python -c "from PySide6.QtCore import qVersion; print('Qt version:', qVersion())"
```

**Required versions:**
- PySide6 >= 6.6.0
- Qt >= 6.6.0

If you have older versions, the UIA bridge may be incomplete.

**To upgrade:**
```cmd
pip install --upgrade PySide6
```

---

### 5. Verify Accessibility Bridge DLL (3 minutes)

**Purpose:** Ensure Windows accessibility plugin is installed

Run diagnostic script - it will show if the DLL exists:

```cmd
python diagnose_accessibility.py
```

Look for the section:
```
Checking for accessibility bridge plugins...
Found accessibility plugins:
  - qwindowsuiaa.dll        <-- Modern UIA bridge
  - qwindowsaccessibility.dll  <-- Legacy MSAA bridge
```

**If missing:** The PySide6 installation is incomplete. Try reinstalling:
```cmd
pip uninstall PySide6
pip install PySide6
```

---

## Code Changes Already Implemented

### 1. Announcement Events ✅
Added `QAccessibleAnnouncementEvent` to force JAWS to speak immediately:
- **File:** `src/accessibility/accessible_events.py`
- **What it does:** Bypasses broken accessible tree by directly announcing text

### 2. Window Attributes ✅
Set explicit window properties:
- **File:** `src/ui/main_window.py`
- **Changes:**
  - `setAccessibleName("AbCS Main Window")`
  - `setAccessibleDescription(...)`
  - `setObjectName("MainWindow")`
  - Window attributes for accessibility

### 3. Status Bar Improvements ✅
Enhanced status bar accessibility:
- Accessible name set to current message
- Announcement events force speech
- Proper role and object name

---

## If Nothing Works

### Option A: Qt 5.15 Fallback

Qt 5.15 has mature, stable MSAA accessibility. If Qt 6.x UIA is fundamentally broken:

```cmd
pip uninstall PySide6
pip install PySide6==5.15.2.1
```

**Warning:** This downgrades Qt. May have compatibility issues with newer code.

### Option B: Custom Accessibility Bridge

Implement direct MSAA calls via `ctypes` or `comtypes` library. This bypasses Qt entirely.

**Complexity:** High - requires Windows MSAA programming
**Benefit:** Full control over what JAWS sees

### Option C: Use Qt.AA_UseSoftwareOpenGL

Some Qt accessibility issues are related to OpenGL rendering:

Add to `src/main.py` before `QApplication()`:
```python
QApplication.setAttribute(Qt.AA_UseSoftwareOpenGL, True)
```

---

## Testing Checklist

After trying each solution, test these scenarios:

### Basic Reading
- [ ] Insert+T reads window title
- [ ] JAWS cursor (Numpad Plus) can read window content
- [ ] Tab navigation speaks control names

### Status Bar
- [ ] Messages appear in status bar visually
- [ ] JAWS announces status messages (might need Insert+End to read status bar)

### Table Navigation
- [ ] Arrow keys navigate table
- [ ] JAWS speaks column header + cell value
- [ ] Selection count is announced

### Forms (Book Details)
- [ ] Tab navigates form fields
- [ ] JAWS speaks field labels
- [ ] Typing into fields works

---

## Expected Results

### Working Correctly
- Window class shows as `Qt6QWidget` or similar (NOT `Qt6101QWindowIcon`)
- JAWS cursor reads all text on screen
- Tab navigation speaks control names and types
- Status bar messages are announced
- Table navigation speaks row/column info

### Still Broken
- Window class is `Qt6101QWindowIcon`
- JAWS cursor says "blank" or nothing
- Tab navigation silent or skips controls
- Status bar never speaks

---

## Next Steps Based on Results

### If Diagnostic Script Works
→ Problem is in AbCS code, not Qt
→ Compare test window to MainWindow to find difference

### If MSAA Mode Works
→ Add MSAA mode as startup option
→ Update documentation
→ File Qt bug report about UIA issues

### If NVDA Works but JAWS Doesn't
→ JAWS-specific compatibility issue
→ May need JAWS script or configuration
→ Contact Freedom Scientific support

### If Nothing Works
→ Qt 6.x Windows accessibility fundamentally broken
→ Consider Qt 5.15 downgrade
→ Or implement custom MSAA bridge

---

## Reporting Back

Please test in this order and report results:

1. **Diagnostic script results**
   - Did test window work with JAWS?
   - What was the window class?

2. **MSAA mode results**
   - Did `run_msaa.bat` help?
   - What changed?

3. **NVDA results**
   - Does NVDA work with AbCS?

4. **Version info**
   - PySide6 version
   - Qt version
   - Plugins found

This will help determine the root cause and best fix.
