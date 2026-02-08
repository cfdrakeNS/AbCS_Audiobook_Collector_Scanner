# Accessibility Status Note (2026-02-06)

## What we confirmed
- The app and diagnostics run without freezing when the QAccessible query is delayed or skipped.
- Qt's accessibility layer can see the window (QAccessible query succeeds).
- JAWS still reports the window class as Qt6102QWindowIcon and virtualizes.

## Key findings
- PySide6 wheels on Windows do not include plugins/accessible.
- Qt SDK installs for 6.10.2 and 6.6.3 (MSVC) also do not include plugins/accessible.
- The missing plugins/accessible folder is not the primary blocker on Qt 6 for Windows.

## Current diagnostic behavior
- diagnose_accessibility.py now:
  - uses PySide6/plugins as the plugin root
  - treats missing plugins/accessible as info
  - supports --accessible-query-delay-ms to avoid startup hangs

## Last known good run
Command:
  .\.venv\Scripts\python.exe diagnose_accessibility.py --accessible-query-delay-ms 2000
Results:
  - QAccessible.isActive(): True
  - QAccessible query returns window role/name/description
  - JAWS still virtualizes (Qt6102QWindowIcon)

## Open questions / next steps if resuming
1) Verify behavior with NVDA as a control test.
2) Review JAWS settings for UIA vs MSAA to ensure Qt UIA is enabled.
3) Run existing harness scripts:
   - run_jaws_with_roles.bat
   - run_jaws_with_events.bat

## Files touched
- diagnose_accessibility.py
  - Added delayed query option and safer plugin path check.

