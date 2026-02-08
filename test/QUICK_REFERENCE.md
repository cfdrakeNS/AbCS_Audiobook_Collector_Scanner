# JAWS Testing Quick Reference

## Your Test Results So Far

From `run_jaws_basic_test.bat`:
- ✅ Insert+T works (reads title)
- ❌ Tab navigation silent
- ❌ Status bar silent
- ✅ Virtual cursor works
- 🚨 Window class: `Qt6102QWindowIcon` (WRONG - should be Qt widget class)

**Diagnosis:** Qt's UIA bridge is not properly initialized. Forms Mode broken.

## Next Tests to Run (Priority Order)

### 1. MSAA Mode (HIGHEST PRIORITY - Most likely to fix)
```cmd
run_jaws_msaa_basic.bat
```
Changes to older, more stable accessibility API.

### 2. Run Diagnostics
```cmd
run_diagnostics.bat
```
Checks Qt version, plugins, and configuration.

### 3. Native Window Mode
```cmd
run_jaws_native_window.bat
```
Forces proper Windows native windows.

### 4. Explicit Roles
```cmd
run_jaws_with_roles.bat
```
Explicitly sets widget types.

### 5. Manual Events
```cmd
python test\test_jaws_with_events.py
```
Manually fires accessibility events.

## What to Check for Each Test

For EVERY test, check:
1. **Insert+Ctrl+F1** - Window class changed?
2. **Tab navigation** - Does JAWS speak?
3. **Status bar** - Does it announce automatically?
4. **Terminal output** - Any errors?

## Success Criteria

Test is successful if:
- Tab navigation speaks widget names
- Window class is NOT `Qt6102QWindowIcon`
- Status bar announces changes

## Report Back

Tell me which test(s) worked, and I'll help apply the fix to your main AbCS application.

## Files Created

**Test Scripts:**
- `test\test_jaws_basic.py` - Simple test (already ran)
- `test\test_jaws_native_window.py` - Native windows test
- `test\test_jaws_with_roles.py` - Explicit roles test
- `test\test_jaws_with_events.py` - Manual events test
- `test\test_tkinter_basic.py` - Tkinter comparison

**Batch Launchers:**
- `run_jaws_basic_test.bat` - Simple test (already ran)
- `run_jaws_msaa_basic.bat` - MSAA mode (try this next!)
- `run_jaws_native_window.bat` - Native windows
- `run_jaws_with_roles.bat` - Explicit roles
- `run_diagnostics.bat` - Configuration check

**Documentation:**
- `test\NEXT_STEPS.md` - Detailed next steps
- `test\JAWS_QUICK_START.md` - Testing guide
- `test\JAWS_TESTING_GUIDE.md` - Complete reference
