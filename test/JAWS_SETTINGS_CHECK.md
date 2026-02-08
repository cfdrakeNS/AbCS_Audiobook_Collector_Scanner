# JAWS Settings to Check

## The Problem

Both Qt (PySide6) AND Tkinter applications have **silent Tab navigation** with JAWS. This suggests a JAWS configuration issue, not an application issue.

## JAWS Settings to Check

### 1. Forms Mode Configuration

**Location:** JAWS Settings Center → Forms Mode

**Settings to check:**
- ✅ "Automatically switch to forms mode when entering forms" - Should be ON
- ❌ "Use virtual cursor in all applications" - Should be OFF
- ✅ "Automatically switch out of forms mode" - Should be ON

**How to check:**
1. Press **Insert+F2** (JAWS Manager)
2. Select "Options"
3. Select "Settings Center"
4. Search for "forms mode"
5. Verify the settings above

---

### 2. Verbosity Settings

**Location:** JAWS Settings Center → Verbosity

**Settings to check:**
- Verbosity level: At least "Intermediate" (not "Beginner")
- "Speak role of control" - Should be ON
- "Speak object type" - Should be ON

---

### 3. Virtual Cursor Settings

**Location:** JAWS Settings Center → Virtual Cursor

**Check:**
- "Restrict virtual cursor to web pages and documents" - Try turning this ON
  (This prevents virtual cursor from interfering with desktop apps)

---

### 4. Application-Specific Settings

JAWS may have application-specific settings that override global settings.

**Check:**
1. With your test app running, press **Insert+V** (Quick Settings)
2. Check if any custom settings are active
3. Try resetting to defaults for this application

---

### 5. Reset JAWS to Defaults (Last Resort)

If nothing else works, try resetting JAWS:

1. Close JAWS
2. Hold **Insert** while starting JAWS
3. Select "Start JAWS with default settings"

**Warning:** This resets ALL your customizations!

---

## Alternative: Manual Verbosity Toggle

While your test app is running:

1. Press **Insert+V** (Quick Settings)
2. Try toggling "Forms Mode" manually: **Enter** on a control, then **Numpad Plus**
3. See if this makes Tab announce controls

---

## JAWS Keystroke to Force Forms Mode

When focused on your application window:

1. Press **Numpad Plus** - Enter virtual cursor
2. Navigate to a button
3. Press **Enter** - This should activate forms mode for that control
4. Try **Tab** now - Does it announce?

---

## Check JAWS Scripts

Your test applications might be using default JAWS scripts.

**To check:**
1. With app running, press **Insert+F2** (JAWS Manager)
2. Select "Explore JAWS"
3. Select "JAWS Scripts"
4. See if "Python" or "Qt" scripts exist

If no scripts exist, JAWS uses default system behavior.

---

## Diagnostic: Listen for JAWS Sounds

JAWS makes sounds when:
- Entering forms mode (high beep)
- Exiting forms mode (low beep)
- Finding no focusable controls (silence)

**Test:**
1. Run: `python test\test_jaws_basic.py`
2. Press **Tab** repeatedly
3. **Listen for beeps or sounds**

**If you hear nothing:**
- JAWS thinks there are no focusable controls
- This confirms the Qt accessibility bridge is broken

**If you hear a low beep:**
- JAWS exited forms mode (thinks it's in a document)
- Forms mode settings need adjustment

---

## Why Tkinter Also Fails

If Tkinter Tab navigation is also silent, this suggests:

1. **Forms mode is disabled globally** - Check settings above
2. **Windows UI Automation service is disabled** - Run `check_uia_service.bat`
3. **JAWS is using virtual cursor mode for everything** - Check virtual cursor settings

Tkinter should "just work" with JAWS, so if it doesn't, it's a JAWS or Windows configuration issue.

---

## Next Steps

1. ✅ **Check Forms Mode settings** (most likely cause)
2. ✅ **Run `check_uia_service.bat`** (check Windows service)
3. ✅ **Test with NVDA** (`run_nvda_test.bat`) to rule out JAWS-specific issue
4. ✅ **Reinstall PySide6** to restore missing accessibility plugins
5. ✅ **Try SAPI workaround** if all else fails

If NVDA works but JAWS doesn't, it's definitely a JAWS configuration issue.
