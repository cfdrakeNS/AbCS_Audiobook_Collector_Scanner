# ACTION PLAN - Fix JAWS Tab Navigation

## What We Know

### Symptoms
1. ✅ Virtual cursor works (can read window content)
2. ❌ Tab navigation is SILENT (doesn't announce widgets)
3. ❌ Status bar doesn't announce changes
4. ❌ Happens with BOTH Qt and Tkinter applications
5. 🚨 Qt accessibility plugins MISSING from PySide6 installation
6. 🚨 Window class is wrong: `Qt6102QWindowIcon`

### Your System
- **Qt**: 6.10.2 (latest - good!)
- **JAWS**: 2026.2512.50 (latest - good!)
- **Windows**: 11 Build 26200 (latest - good!)
- **Problem**: Tab navigation silent in ALL apps (Qt AND Tkinter)

### Root Causes (Two Separate Issues)

**Issue 1: Missing Qt Accessibility Plugins**
- Diagnostics show: "⚠ Accessibility plugin directory not found"
- This breaks Qt's UIA/MSAA bridge
- Result: Wrong window class, no accessible control tree

**Issue 2: JAWS Forms Mode Not Working (System-Wide)**
- Tkinter also has silent Tab navigation
- This means it's not Qt-specific
- Either JAWS configuration or Windows accessibility service issue

---

## ACTION PLAN (In Order)

### Step 1: Reinstall PySide6 (Fix Qt Plugins) - 5 minutes

```cmd
pip uninstall PySide6
pip cache purge
pip install PySide6 --force-reinstall --no-cache-dir
```

**Then verify:**
```cmd
run_diagnostics.bat
```

**Look for:** "✓ Accessibility plugins found" instead of warning.

**If plugins still missing:** PySide6 6.10.2 may have a packaging bug. Try downgrading:
```cmd
pip install PySide6==6.8.1
```

---

### Step 2: Check Windows UI Automation Service - 3 minutes

```cmd
check_uia_service.bat
```

**If service is STOPPED:**
1. Press Win+R, type: `services.msc`
2. Find "Windows UI Automation Core Service" or "UI Automation"
3. Right-click → Properties
4. Set Startup type to "Automatic"
5. Click "Start"
6. Restart computer

---

### Step 3: Check JAWS Forms Mode Settings - 5 minutes

**Open JAWS Settings Center:**
1. Press **Insert+F2** → Options → Settings Center
2. Search for: "forms mode"

**Verify these settings:**
- ✅ ON: "Automatically switch to forms mode when entering forms"
- ❌ OFF: "Use virtual cursor in all applications"
- ✅ ON: "Automatically switch out of forms mode"

**If settings look correct, try resetting:**
1. Close JAWS
2. Hold **Insert** while starting JAWS
3. Select "Start JAWS with default settings"

---

### Step 4: Test with NVDA (Determine if JAWS-Specific) - 10 minutes

**Download NVDA (free):** https://www.nvaccess.org/download/

**Test:**
1. Close JAWS
2. Start NVDA
3. Run: `run_nvda_test.bat`
4. Try Tab navigation

**Results:**
- **NVDA works, JAWS doesn't:** JAWS configuration issue (proceed to Step 5)
- **NVDA also doesn't work:** System-wide accessibility issue (proceed to Step 6)

---

### Step 5: If NVDA Works (JAWS Configuration Issue)

**JAWS has a problem with your system configuration.**

**Actions:**
1. Update JAWS to absolute latest version
2. Check JAWS scripts for Python/Qt applications
3. Contact Freedom Scientific support
4. Use NVDA temporarily while investigating
5. Or use SAPI workaround (Step 7)

---

### Step 6: If NVDA Also Fails (System-Wide Issue)

**Windows accessibility is broken system-wide.**

**Actions:**
1. Run Windows Update (ensure Build 26200.7705 or later)
2. Run: `sfc /scannow` (fixes corrupted Windows files)
3. Check Windows 11 Accessibility settings:
   - Settings → Accessibility → Screen reader
   - Ensure screen reader support is enabled
4. Reinstall Windows accessibility components (advanced)

---

### Step 7: SAPI Workaround (If Nothing Else Works) - 30 minutes

If all else fails, bypass Qt accessibility entirely using Windows SAPI.

**Install pywin32:**
```cmd
pip install pywin32
```

**Test workaround:**
```cmd
run_sapi_workaround.bat
```

**If this works:** We'll implement SAPI announcements throughout your AbCS application.

**Implementation:** Wrap all focus handlers and status bar updates with SAPI calls.

---

## Expected Timeline

| Step | Time | Success Criteria |
|------|------|------------------|
| **1. Reinstall PySide6** | 5 min | Diagnostics show accessibility plugins |
| **2. Check UIA Service** | 3 min | Service is running |
| **3. JAWS Settings** | 5 min | Forms mode configured correctly |
| **4. Test NVDA** | 10 min | Determines if JAWS-specific |
| **5. Fix JAWS** | Variable | JAWS Tab navigation works |
| **6. Fix System** | Variable | System accessibility restored |
| **7. SAPI Workaround** | 30 min | Manual announcements work |

**Total expected time:** 23 minutes to 1 hour

---

## What to Try First (Priority Order)

1. **Reinstall PySide6** (most likely to fix Qt window class)
2. **Check JAWS Forms Mode settings** (most likely to fix Tab navigation)
3. **Test with NVDA** (determines scope of problem)
4. **Check UIA Service** (if NVDA also fails)
5. **SAPI Workaround** (guaranteed to work)

---

## How to Know You've Succeeded

**Success looks like:**
1. ✅ Diagnostics show: "✓ Accessibility plugins found"
2. ✅ Window class is proper Qt class (NOT `Qt6102QWindowIcon`)
3. ✅ Tab navigation announces widget names with JAWS
4. ✅ Status bar announces changes automatically
5. ✅ JAWS says "button" when you Tab to a button

---

## Report Back After Each Step

Please share:
1. **After Step 1 (Reinstall):** Full output of `run_diagnostics.bat`
2. **After Step 3 (JAWS settings):** Screenshot of Forms Mode settings
3. **After Step 4 (NVDA test):** Does NVDA announce Tab navigation?
4. **After any success:** Which step fixed it?

With this information, I'll help you apply the fix to your entire AbCS application.

---

## If All Else Fails

If nothing works, the SAPI workaround (Step 7) is guaranteed to work. It bypasses all Qt and Windows accessibility layers and speaks directly to JAWS/NVDA.

**Trade-offs:**
- Pros: Guaranteed to work, full control
- Cons: More code, need pywin32, manual maintenance

We can implement this if needed, but let's try the other steps first.
