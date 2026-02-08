# Accessibility Documentation - Quick Navigation

This folder contains comprehensive documentation about JAWS screen reader accessibility for AbCS.

## Start Here

### If JAWS isn't working...
👉 **Read first:** [JAWS_TESTING_GUIDE.md](JAWS_TESTING_GUIDE.md)
- Step-by-step testing instructions
- Troubleshooting section
- Expected behavior

### If you want to understand the technical issue...
👉 **Read:** [JAWS_INVESTIGATION_RESULTS.md](JAWS_INVESTIGATION_RESULTS.md)
- What was researched
- Key findings and root causes
- What was changed and why
- Summary of all issues

### If you want detailed diagnosis/debugging...
👉 **Read:** [JAWS_ACCESSIBILITY_DIAGNOSIS.md](JAWS_ACCESSIBILITY_DIAGNOSIS.md)
- Deep technical analysis
- Windows UIA bridge explanation
- 6 different solutions (priority order)
- Potential fixes to try

### If you're a developer debugging accessibility...
👉 **Read:** [ACCESSIBILITY_DEBUG_GUIDE.md](ACCESSIBILITY_DEBUG_GUIDE.md)
- Python diagnostic scripts
- How to check Qt version and DLL files
- Runtime diagnostics code
- Test application you can run

### Quick summary of what changed...
👉 **Read:** [CHANGES_SUMMARY.md](CHANGES_SUMMARY.md)
- What was modified in the code
- Why changes were made
- Files that were edited
- Next steps for user

---

## The TL;DR (Too Long; Didn't Read)

**Problem:** JAWS screen reader can't see AbCS application.

**Root Cause:** Windows UI Automation (UIA) bridge not initialized.

**Solution:** 
1. Start JAWS FIRST (before running AbCS)
2. Run `python src/main.py`
3. Check console output for: `QAccessible.isActive(): True`
4. Press Insert+F6 in JAWS to hear status bar

---

## Files Overview

| File | Purpose | Read Time |
|------|---------|-----------|
| [JAWS_TESTING_GUIDE.md](JAWS_TESTING_GUIDE.md) | How to test JAWS with AbCS | 15 min |
| [JAWS_INVESTIGATION_RESULTS.md](JAWS_INVESTIGATION_RESULTS.md) | Summary of research findings | 10 min |
| [JAWS_ACCESSIBILITY_DIAGNOSIS.md](JAWS_ACCESSIBILITY_DIAGNOSIS.md) | Technical root cause analysis | 20 min |
| [ACCESSIBILITY_DEBUG_GUIDE.md](ACCESSIBILITY_DEBUG_GUIDE.md) | Debugging scripts and tools | 15 min |
| [CHANGES_SUMMARY.md](CHANGES_SUMMARY.md) | Code changes made | 10 min |

---

## Quick Checklist

Before testing with JAWS, verify:

- [ ] JAWS is installed and up-to-date
- [ ] PySide6 version 6.6 or higher: `python -c "from PySide6 import __version__; print(__version__)"`
- [ ] `qwindowsuiaa.dll` exists in PySide6 plugins
- [ ] Windows 10 or 11

When testing:
- [ ] Start JAWS first
- [ ] Wait 10+ seconds for JAWS to fully load
- [ ] Then run `python src/main.py`
- [ ] Check console for accessibility diagnostics
- [ ] Test pressing Insert+F6 to hear status bar

---

## Common Issues and Solutions

### Issue: JAWS doesn't hear anything
**Solution:** Make sure JAWS is running BEFORE you start AbCS
- Close AbCS
- Start JAWS
- Wait 10+ seconds
- Then start AbCS
- Look for "QAccessible.isActive(): True" in console

### Issue: Console shows "QAccessible.isActive(): False"
**Solution:** JAWS is not running or not detected
- Check that JAWS is actually running (should have window open)
- Restart JAWS and AbCS
- If still False, see [JAWS_TESTING_GUIDE.md](JAWS_TESTING_GUIDE.md) troubleshooting

### Issue: Status bar not being read
**Solution:** Verify accessibility is initialized
1. Check console shows "QAccessible.isActive(): True"
2. In JAWS, press Insert+F6 (status bar command)
3. If no response, see troubleshooting section

### Issue: Can't find `qwindowsuiaa.dll`
**Solution:** Upgrade PySide6
```bash
pip install --upgrade PySide6
```
Then check again:
```python
python -c "from PySide6 import __version__; print(__version__)"  # Should be 6.6+
```

---

## Key Insights

### Why JAWS Must Run First
Windows only activates UI Automation (UIA) when a screen reader is active. If AbCS starts before JAWS, the platform bridge doesn't get activated.

### Why We Added `setRootObject()`
The Windows UIA bridge needs to know where the accessibility tree starts. `setRootObject(app)` anchors it.

### Why Status Bar Was Simplified
Qt's QStatusBar has built-in accessibility. We were over-complicating it by manually emitting events. Now we just update the message and let Qt handle the rest.

### Why `isActive()` Returns False Sometimes
This isn't a bug! It's correct behavior. It means no screen reader is attached yet. Once JAWS connects, it becomes True.

---

## Technical References

- **Qt Accessibility Documentation:** https://doc.qt.io/qt-6/accessible.html
- **Windows UI Automation:** https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-overview
- **JAWS Documentation:** https://www.freedomscientific.com/products/software/jaws/
- **NVDA (Free Screen Reader):** https://www.nvaccess.org/

---

## Contact and Support

If you're still having issues after reading these guides:

1. Check [JAWS_TESTING_GUIDE.md](JAWS_TESTING_GUIDE.md) troubleshooting section
2. Run diagnostic scripts from [ACCESSIBILITY_DEBUG_GUIDE.md](ACCESSIBILITY_DEBUG_GUIDE.md)
3. Verify requirements in the Checklist above
4. Contact JAWS or Qt support with:
   - PySide6 version
   - Qt version
   - Whether `qwindowsuiaa.dll` exists
   - Output from diagnostic scripts

---

## Document Versions

- **Created:** January 31, 2026
- **Last Updated:** January 31, 2026
- **Version:** 1.0 (Initial comprehensive documentation)

---

**Next Step:** 👉 [JAWS_TESTING_GUIDE.md](JAWS_TESTING_GUIDE.md)
