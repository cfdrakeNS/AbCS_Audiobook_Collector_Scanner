# JAWS Virtualization Investigation

## Problem
- Friday evening build (for Wayne): ✅ Virtualizes with Insert+Alt+W
- Current VS Code version: ❌ Does NOT virtualize with Insert+Alt+W
- Both versions are accessible except status bar

## What Changed Between Versions

### Friday Evening Build (commit b4f0d66)
**Simple, clean approach:**
- No explicit QAccessible calls
- No setActive(True)
- No setRootObject()
- No accessible_events.py module
- Let Qt handle accessibility naturally

### Current Version (commit cde31bd - Saturday)
**Added explicit accessibility code:**

1. **In main.py `__init_qt_app()`:**
   ```python
   QAccessible.setActive(True)
   QAccessible.setRootObject(self.qt_app)
   ```

2. **New accessibility modules:**
   - `accessible_events.py` - Event announcements for JAWS
   - `accessible_widgets.py` - Custom accessible widgets

3. **In book_details.py:**
   ```python
   self.setAccessibleName(title)
   self.setAccessibleDescription("Form for viewing and editing...")
   ```

4. **Added diagnostic output:**
   - Prints QAccessible.isActive() status
   - Checks accessibility interface setup

## Root Cause Hypothesis

The explicit `QAccessible.setActive(True)` and `QAccessible.setRootObject()` calls may be interfering with JAWS's ability to virtualize the window.

**Why?**
- JAWS virtualization (Insert+Alt+W) works by capturing the window's text content
- When Qt's accessibility is explicitly activated, it may change how JAWS interacts with the window
- `setRootObject(app)` might anchor the accessibility tree in a way that prevents virtualization

## Testing Plan

### Option 1: Test App (Fastest)
Run `test_virtualization.py` to isolate the issue:

```bash
python test_virtualization.py
```

This opens 3 windows:
1. Basic Qt (no accessibility changes) - baseline
2. With `setActive(True)` only
3. With `setActive(True)` + `setRootObject()`

Try Insert+Alt+W in each window to see which virtualizes.

### Option 2: Revert to Friday (Most Accurate)
Use the revert scripts to test the actual Friday build:

```bash
# Revert to Friday's version
python revert_to_friday.py

# Test with JAWS
python src/main.py
# Try Insert+Alt+W

# Restore current version
python restore_current_version.py
```

## Recommendations

### If Test Shows setActive/setRootObject Breaks Virtualization:

**Solution 1: Remove explicit QAccessible calls (RECOMMENDED)**
```python
# Remove from main.py __init_qt_app():
# QAccessible.setActive(True)  # ← DELETE
# QAccessible.setRootObject(self.qt_app)  # ← DELETE
```

**Why this works:**
- Qt automatically activates accessibility when JAWS is running
- You don't need to force it
- Letting Qt handle it naturally preserves virtualization

**Trade-off:**
- You lose the diagnostic output (isActive status)
- But you gain virtualization support
- All other accessibility (keyboard nav, Alt+shortcuts) still works

**Solution 2: Conditional QAccessible calls**
Only call if not already active:
```python
if not QAccessible.isActive():
    QAccessible.setActive(True)
# Don't call setRootObject at all
```

**Solution 3: Make it optional**
Add a setting to toggle explicit accessibility:
```python
FORCE_ACCESSIBILITY = False  # User can set to True if needed
if FORCE_ACCESSIBILITY:
    QAccessible.setActive(True)
```

### If Test Shows It's Something Else:

We'll need to dig deeper into:
- Accessible names/descriptions on widgets
- Event emission (QAccessibleEvent)
- Hidden announcement widgets

## Key Insight

**The Friday build worked perfectly because it was simpler:**
- No explicit accessibility activation
- No accessibility events
- Just clean PySide6 code with proper keyboard shortcuts
- Qt + JAWS handled the rest automatically

**"Less is more" applies here.** The accessibility system works better when you don't force it.

## Next Steps

1. **Run test_virtualization.py** to confirm the hypothesis
2. **If confirmed:** Remove `setActive()` and `setRootObject()` from main.py
3. **Rebuild and test** with JAWS
4. **Keep all the other accessibility features:**
   - 14pt fonts, scaling
   - High contrast themes
   - Alt+letter shortcuts
   - F-key navigation
   - Status bar messages (visible text still works)

The goal is to get back to Friday's working virtualization while keeping the UI improvements we added.
