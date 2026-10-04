# Accessibility and UI Formatting Standards

**Source:** the "Cross-cutting principles" and "Accessibility and UI formatting standards (all phases)" sections of `archive/doc/plan_enhancements_version3_release.md` (v3 master roadmap), copied here so the standard is tracked in git.  
**Related:** [standard_shortcuts.md](standard_shortcuts.md), [shortcut_centralization_status.md](shortcut_centralization_status.md), [shortcut_normalization_plan.md](shortcut_normalization_plan.md), [../help_docs_authoring.md](../help_docs_authoring.md)

---

## Cross-cutting principles

1. Add or extend tests from each plan's checklist before starting the next phase.
2. Run `python -m pytest test/` — **all** tests green before merge, including files this phase did not touch. Collection must succeed (a SyntaxError in any `test_*.py` fails the suite).
3. Test logic modules first; mock HTTP and DB in CI.
4. Include tests in the same commit/PR as the feature.
5. NVDA/JAWS smoke after each phase. Ship help with each feature.
6. Every UI change must meet the standards below (buttons, dialogs, focus, styles).

---

## Accessibility and UI formatting standards

Mandatory for any new or changed window, dialog, footer button, combo, or status path. Match existing main-window / Book Details / Preferences patterns — do not invent one-off styles or announcement paths.

### Screen reader (JAWS / NVDA)

- Dialogs subclass [`AccessibleDialog`](../../src/ui/accessible_dialog.py) (or reuse `exec_styled_message_box` for simple prompts).
- Set **accessible name** and **description** on the dialog and on every interactive control (buttons, combos, lists, edits). `QAction` menu items use menu text only — do **not** call `setAccessibleName` on `QAction` (not supported).
- Meaningful state changes: `set_status(..., announce=True)` via [`announce_status_message`](../../src/accessibility/accessible_events.py). Do not rely on `QStatusBar.showMessage()` alone.
- Every major window/dialog: **Alt+/** re-reads status ([`read_status_bar_message`](../../src/accessibility/accessible_events.py)).
- After modal close: restore focus intentionally (`restore_main_focus_after_modal` / focus title or table as the parent window already does).
- Window open (name list pattern): pass starting values (collection, filter) through the constructor; do not change combos after construction. Set first focus in `showEvent` with `QTimer.singleShot(0, ...)`. Never `set_status(..., announce=True)` while the window is hidden (`announce=self.isVisible()`), because the focus pulse lands on the parent window and the screen reader reads its title. If an open message is needed, keep it and announce it after `showEvent`.
- Menu items that open windows: the main window holds focus on the menu bar while a keyboard-chosen menu item runs (`_hold_focus_for_menu_action` in [`main_window.py`](../../src/ui/main_window.py)), so the screen reader does not say "book table" before the new window. Menus added in `create_menu_bar` are covered automatically; a menu created elsewhere must connect its `aboutToHide` the same way. Do not add per-window workarounds for this.
- Message boxes over dialogs: always use `exec_styled_message_box`. When its parent is an `AccessibleDialog`, it keeps the dialog enabled (no Qt parent, Win32 owner, window modal) so JAWS does not say "<title> unavailable" before the box. A raw `QMessageBox(dialog).exec()` brings that noise back.
- Opening a progress window from a window: show, raise, activate, and focus the progress window **before** disabling the caller's buttons. Disabling the focused button first moves focus to the next control (for example an instructions label), and the screen reader reads it.
- Modal completion after background work: `raise_()` + `activateWindow()` + focus on the **default button** before announce (learned from fetch/Calibre issues).
- Worker threads must not touch widgets. Progress/UI updates go through a **GUI-thread `QObject` bridge** with `QueuedConnection` to `@Slot` methods — plain Python callables are not enough.
- Block unmapped Alt+letter in text fields (`is_unmapped_alt_letter`). Editable combos: block plain Up/Down; allow with Alt (Preferences / Book Details / Update pattern).
- No global Enter/Return shortcuts that steal default button activation.
- Help: F1 shortcuts; Shift+F1 process help via [`help_router.py`](../../src/ui/help_router.py); ship or update `help_docs/` with the feature.

External reference (patterns + principles):

- [PySide6 Accessibility Patterns](https://github.com/cfdrakeNS/pyside6-accessible-ui-reference/blob/main/doc/PySide6_Accessibility_Patterns_and_Implementation_Reference.md)
- [Screen Reader Best Practices](https://github.com/cfdrakeNS/pyside6-accessible-ui-reference/blob/main/doc/PySide6_Screen_Reader_Accessibility_Best_Practices.md)

### Buttons, footers, and control formatting

- New **QPushButton**s use [`build_accessible_button_style`](../../src/accessibility/style_helpers.py) with scaled height from `UIScaler` (same as Update / Delete / Import footers). Do not invent per-dialog button CSS.
- Footer action buttons on the main window follow `update_selection_ui()` visibility/enable rules (multi-select patterns like Update/Delete).
- Default button: `setDefault(True)` on the primary action; ensure Tab order reaches it; screen reader focus lands on it when the dialog opens when that is the intended start.
- Decorative icons only via [`apply_decorative_action_icon`](../../src/accessibility/icon_helper.py) / `get_app_icon()` — icons must not be the only label.
- Combos: [`build_accessible_combo_box_style`](../../src/accessibility/style_helpers.py) where other prefs/main combos already use it; set accessible name/description; anti-noise event filter when editable.
- Checkboxes: [`build_accessible_checkbox_style`](../../src/accessibility/style_helpers.py) when adding new check groups.
- Message boxes: [`exec_styled_message_box`](../../src/accessibility/style_helpers.py) with scaled font and app window icon — not raw `QMessageBox` with default look.
- Scaling: respect `UIScaler` / theme; no hard-coded px that break zoom or high-contrast themes.
- Tooltips: pair short sighted tooltips with SR descriptions via existing helpers (`apply_visual_tooltip_map`) where the parent window already does.

### Per-change gate (JAWS smoke)

Before marking a change done:

1. Tab through every new control; JAWS/NVDA speaks a useful name (and value where applicable).
2. Activate primary and Cancel/Close with keyboard only (including Alt+letter if registered).
3. Alt+/ reads the latest status after a meaningful action.
4. Focus returns to a sensible place after the dialog closes.
5. Open the window both ways — its Ctrl shortcut and its menu item (Alt+menu letter) — and confirm only the new window is spoken, not the main window title or book table. Trigger any confirm box (for example Escape with changes) and confirm no "<title> unavailable" before it.
6. New buttons look and focus like existing AbCS buttons (highlight focus ring, scaled height).
