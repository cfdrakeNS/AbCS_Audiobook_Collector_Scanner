
# Shortcut Discrepancy Report (March 11, 2026)

## Method
- Compared shortcut keys and actions defined in src/accessibility/shortcuts.py against the F1 shortcut menus listed in AbCS_shortcut Keys.md for each window.
- Focused only on actual shortcut dictionaries in shortcuts.py (ignoring comments).
- Documented any differences, missing, or extra shortcuts found in shortcuts.py that do not match the F1 menus.

---

## Main Window
- F1 menu (AbCS_shortcut Keys.md): Alt+B, Alt+U, Alt+D, Alt+L, Alt+1..Alt+0, Alt+/, Ctrl+N, Ctrl+I, Ctrl+Q, Ctrl+Enter, Ctrl+Plus, Ctrl+Minus, Ctrl+0, F1, Escape
- shortcuts.py: Alt+B, Alt+U, Alt+D, Alt+L
- Discrepancy: shortcuts.py does NOT define Alt+1..Alt+0, Alt+/, Ctrl+N, Ctrl+I, Ctrl+Q, Ctrl+Enter, Ctrl+Plus, Ctrl+Minus, Ctrl+0, F1, Escape (these are likely handled elsewhere or via Qt menus, not ShortcutManager).

## Book Details Window
- F1 menu: Alt+T, Alt+A, Alt+O, Alt+Y, Alt+M, Alt+R, Alt+E, Alt+I, Alt+G, Alt+K, Alt+F, Alt+B, Alt+Z, Alt+H, Alt+N, Alt+S, Alt+D, Alt+L, Alt+C, Alt+/
- shortcuts.py: Alt+T, Alt+A, Alt+Y, Alt+F, Alt+I, Alt+G, Alt+R, Alt+K, Alt+M, Alt+E, Alt+Z, Alt+B, Alt+H, Alt+O, Alt+N, Alt+S, Alt+D, Alt+L, Alt+C
- Discrepancy: shortcuts.py does NOT define Alt+/ (status bar read), but all other shortcuts match.

## Import Window
- F1 menu: Alt+C, Alt+F, Alt+E, Alt+W, Alt+S, Alt+I, Alt+V, Alt+L, Alt+B, Alt+1..Alt+5, Alt+/, Ctrl+Enter, Alt+X, F1, Escape
- shortcuts.py: Alt+C, Alt+F, Alt+E, Alt+W, Alt+S, Alt+I, Alt+V, Alt+L, Alt+B, Alt+X
- Discrepancy: shortcuts.py does NOT define Alt+1..Alt+5, Alt+/, Ctrl+Enter, F1, Escape (likely handled elsewhere).

## Update Window
- F1 menu: Alt+S, Alt+G, Alt+L, Alt+C, Alt+B, Alt+Down, Alt+/, F1, Escape
- shortcuts.py: Alt+S, Alt+G, Alt+L, Alt+C, Alt+B
- Discrepancy: shortcuts.py does NOT define Alt+Down, Alt+/, F1, Escape (likely handled elsewhere).

## Preferences Window
- F1 menu: Alt+/, Alt+T, Alt+P, Alt+Z, Alt+D, Alt+B, Alt+O, Alt+S, Alt+R, Alt+A, Alt+I, Alt+F, Alt+K, Alt+W, Alt+L, Alt+U, Alt+V, Alt+C, F1
- shortcuts.py: Alt+T, Alt+P, Alt+Z, Alt+D, Alt+B, Alt+O, Alt+S, Alt+R, Alt+A, Alt+I, Alt+F, Alt+K, Alt+W, Alt+L, Alt+V, Alt+C
- Discrepancy: shortcuts.py does NOT define Alt+/, Alt+U, F1 (likely handled elsewhere).

---

## Summary of Discrepancies
- Many shortcuts listed in F1 menus (AbCS_shortcut Keys.md) are not defined in shortcuts.py, including Alt+/, Alt+1..Alt+0, Alt+Down, Ctrl+N, Ctrl+I, Ctrl+Q, Ctrl+Enter, F1, Escape, Alt+U (Preferences).
- These are likely handled via Qt menus, direct widget setup, or other code (not ShortcutManager).
- shortcuts.py only defines Alt+letter shortcuts for direct widget focus/actions, not menu navigation, status bar read, or global keys.

## Proposed Changes
- Review and clarify which shortcuts are managed by ShortcutManager (shortcuts.py) vs those handled elsewhere (menus, widget setup, etc).
- Remove any shortcuts from shortcuts.py that are not actually registered or used in the UI.
- Ensure F1 menus only list shortcuts that are truly active and registered for each window.
- Consider centralizing all shortcut registration (including Alt+/, Alt+Down, Alt+1..Alt+0, etc) in ShortcutManager for consistency.
- Document in code and F1 menus which shortcuts are handled outside ShortcutManager.

## Action Items
- Audit each window's shortcut registration to ensure only active shortcuts are listed in both code and F1 menus.
- Remove legacy or unused shortcuts from shortcuts.py.
- Update F1 menus to match only active, registered shortcuts.
- Optionally, automate shortcut extraction from ShortcutManager for future documentation.
