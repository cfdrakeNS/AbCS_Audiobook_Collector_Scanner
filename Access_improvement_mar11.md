# Access_improvement_mar11

## Objective
Enhance AbCS accessibility by contextually adapting Alt+/ shortcut visibility, improving NVDA status bar reading, and adding user-configurable timing for status bar messages.

---

### 1. Hide Alt+/ Shortcut in F1 Menus When No Screen Reader Is Active
- Detect screen reader (JAWS/NVDA) at runtime using process check.
- In all window F1 shortcut menus/help dialogs:
    - If no screen reader is active, hide Alt+/ shortcut from the list.
    - If a screen reader is active, show Alt+/ shortcut as usual.
- Alt+/ remains functional but is not advertised to sighted/low vision users unless needed.

### 2. Leave Alt+/ Active
- Do not disable Alt+/ shortcut; it remains available for all users.
- No negative effect if pressed when no screen reader is active.

### 3. Improve NVDA Status Bar Reading via Alt+/
- Investigate timing issue where NVDA overspeaks status bar message.
- Adjust status bar message timing (delay, repeat, focus) for NVDA.
- Test and tune timing to ensure NVDA reliably reads status bar when Alt+/ is pressed.

### 4. Add Preferences Setting for Status Bar Timing (Visible Only if Screen Reader Is Active)
- Add a new setting in Preferences window:
    - "Status Bar Read Timing" (e.g., delay in ms, repeat count)
    - Only show this setting if a screen reader is detected.
- Allow users to customize timing for status bar messages to optimize screen reader feedback.

---

## Implementation Steps
1. Update screen reader detection utility to reliably identify JAWS/NVDA.
2. Refactor F1 shortcut menu generation in all windows to conditionally show/hide Alt+/.
3. Update status bar announcement logic to use timing from preferences and auto-tune for NVDA.
4. Add preferences UI for timing setting, visible only when screen reader is active.
5. Test with both JAWS and NVDA for correct behavior.

---

## Notes
- No changes to Alt+/ shortcut functionality; only visibility and timing are adapted.
- All changes follow accessibility-first design and minimize confusion for sighted/low vision users.
- Status bar timing setting empowers screen reader users to optimize their experience.
