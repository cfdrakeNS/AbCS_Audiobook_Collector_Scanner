# JAWS Testing Summary - What to Try Next

## Quick Start

You asked about virtualization not working. Here's what you need to know:

**Qt/PySide6 applications don't support JAWS Virtual Cursor** (Numpad Plus for reading like a document). This is normal and expected. Instead, Qt apps use **Forms Mode** where JAWS reads widgets through Windows accessibility APIs.

## Try These Tests (In Order)

### Test 1: Simple PySide6 Application (5 minutes)

**Goal**: Verify if JAWS can read ANY PySide6 application at all.

```cmd
# Start JAWS FIRST, then run:
run_jaws_basic_test.bat
```

**What to try with JAWS:**
1. Press **Insert+T** - Should read "JAWS Basic Test"
2. Press **Tab** - Should say "Click Me button"
3. Press **Insert+Ctrl+F1** - Check window class (should NOT be `Qt6101QWindowIcon`)
4. Press **Space** - Click button, status should announce

**If this works**: Your PySide6 accessibility is working! The issue is with how you're testing, not the code.

**If this doesn't work**: Proceed to Test 2.

---

### Test 2: Try MSAA Mode (5 minutes)

**Goal**: Use older, more stable accessibility API.

```cmd
# Start JAWS FIRST, then run:
run_test_harness_msaa.bat
```

This forces Qt to use MSAA (Microsoft Active Accessibility) instead of Windows UIA. MSAA is older but more reliable.

**If this works**: Your issue is with Qt's UIA bridge. You can use MSAA mode as a workaround.

**If this doesn't work**: Proceed to Test 3.

---

### Test 3: Compare with Tkinter (10 minutes)

**Goal**: Determine if this is Qt-specific or system-wide.

```cmd
# Start JAWS FIRST, then run:
python test\test_tkinter_basic.py
```

Tkinter uses different accessibility APIs than Qt.

**If this works**: The issue is Qt-specific. Try upgrading PySide6 or using MSAA mode.

**If this doesn't work**: Your system may have accessibility issues. Try Test 4.

---

### Test 4: Try NVDA (Free Screen Reader) (10 minutes)

**Goal**: Determine if this is JAWS-specific.

1. Download NVDA (free): https://www.nvaccess.org/download/
2. Install and start NVDA
3. Run: `python test\test_jaws_basic.py`
4. Try NVDA commands:
   - **NVDA+T**: Read title
   - **Tab**: Navigate
   - **Insert+Up/Down**: Say line/say all

**If NVDA works**: The issue is JAWS-specific. Check JAWS settings or use latest JAWS version.

**If NVDA doesn't work**: Proceed to Test 5.

---

### Test 5: Check PySide6 Version

```cmd
python -c "from PySide6 import __version__; print('PySide6:', __version__)"
python -c "from PySide6.QtCore import qVersion; print('Qt:', qVersion())"
```

**You need:**
- PySide6 >= 6.6.0
- Qt >= 6.6.0

**To upgrade:**
```cmd
pip install --upgrade PySide6
```

---

## Understanding What's Happening

### Why Virtualization Doesn't Work

When you press **Numpad Plus** (JAWS Cursor/Virtual Cursor), you're trying to read the window as if it were a web page or PDF. This doesn't work for desktop applications.

**Desktop applications use a different approach:**
- JAWS automatically switches to "Forms Mode" for applications
- You navigate with **Tab**, **Arrow keys**, and normal application shortcuts
- JAWS reads each widget as you focus it
- You don't need to "virtualize" the content

### What "Good" JAWS Support Looks Like

For a Qt application, JAWS support works when:
1. **Insert+T** reads the window title
2. **Tab** moves between controls and announces each one
3. **Status bar messages** are spoken automatically
4. **Combo boxes** announce their options with arrow keys
5. **Technical info** (Insert+Ctrl+F1) shows proper widget classes

**You will NOT be able to:**
- Use Numpad Plus to read the window as static text
- Read the entire window like a document
- Use virtual cursor commands (Numpad 7/9/1/3 etc.)

This is how ALL desktop applications work with JAWS - not just yours!

---

## Common Python GUI Applications to Test With

Here are some well-known Python applications you can test JAWS with:

### 1. **Thonny IDE** (Python IDE)
- Download: https://thonny.org/
- Uses Tkinter, should work well with JAWS

### 2. **Mu Editor** (Educational Python IDE)
- Download: https://codewith.mu/
- Uses PyQt5, similar to your PySide6 setup

### 3. **Spyder IDE** (Scientific Python IDE)
- Download: https://www.spyder-ide.org/
- Uses PyQt5/PySide2, should behave like your app

### 4. **Windows Calculator** (for comparison)
- Built-in Windows app
- Shows how JAWS reads a native desktop application
- Try the same commands (Insert+T, Tab, etc.)

---

## Expected Results Summary

| Test | If Working | If Not Working |
|------|-----------|----------------|
| **Basic PySide6** | JAWS reads widgets with Tab navigation | Proceed to MSAA mode |
| **MSAA Mode** | Use this mode permanently | Proceed to Tkinter test |
| **Tkinter** | Qt-specific issue, upgrade PySide6 | System accessibility issue |
| **NVDA** | JAWS-specific config problem | Qt accessibility broken |
| **Calculator** | Reference for how desktop apps should behave | N/A |

---

## What to Report Back

After running these tests, let me know:

1. **Which tests worked?** (Basic PySide6, MSAA, Tkinter, NVDA?)
2. **What does Insert+Ctrl+F1 show?** (Window class name)
3. **Does Tab navigation speak widgets?**
4. **Your JAWS version?** (Help → About JAWS)
5. **Your PySide6 version?** (Run the version check command above)

With this information, I can help you solve the specific issue you're facing.

---

## Bottom Line

**You probably don't have a problem** - you're just expecting Qt apps to behave like web browsers. Desktop applications work differently with JAWS, and that's normal.

Run the tests above to confirm your accessibility is actually working, just not the way you expected!
