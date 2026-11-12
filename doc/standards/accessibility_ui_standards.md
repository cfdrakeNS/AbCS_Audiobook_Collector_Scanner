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

### Confirmed in testing (November 2026)

These come from the JAWS and NVDA pass on branch `a11y-fixes`. A new or changed window follows them. Older windows do not all follow the default-button, first-focus, shortcut-hint, and single Alt-beep rules yet. Leave those until a reported problem calls for a change.

- Screen reader detection: use [`is_screen_reader_active`](../../src/accessibility/screen_reader.py) (process detection) to change the interface, such as typed year and date fields or hiding the Book Details header card. `QAccessible.isActive()` alone also turns on for Magnifier and the touch keyboard. Announcements may use either check ([`_accessibility_announcements_enabled`](../../src/accessibility/accessible_events.py)).
- Dialog prose (About, License, Setup) does not wrap. Call [`prepare_dialog_prose`](../../src/accessibility/dialog_prose.py) so each paragraph stays on one line and is read once. Help may wrap, and it keeps one sentence per paragraph.
- After a message box closes, put focus back on the field that needs it. Book Details returns to the last changed field after No, and to Year after the year warning. One Enter closes that warning. Escape on the warning does not also open the unsaved-changes prompt.
- A popup or progress window that opens right after a dialog closes must let the owner finish becoming active, or the screen reader reads the owner instead of the popup. [`exec_styled_message_box`](../../src/accessibility/style_helpers.py) does this in `_settle_owner_activation`. Any other popup opened at that moment does the same: raise, activate, and process events.
- When a long operation starts, the progress window is the next thing spoken. Show, raise, activate, and focus it before disabling the caller's controls. If a confirm box just closed, let that window finish reactivating before the progress window opens.
- With focus in a text field, the JAWS read-dialog key reads only the window title and that field. Put the dialog's instructions in the field's accessible description, or start focus on a button or combo when that key must read the whole dialog. Read date and Recently Added put the instructions on the date field.
- Shortcut hints stay out of status text, except "Press Escape to cancel" or "Esc to close" while a long operation is running. Hints belong in descriptions and F1. Find and Recently Added add "Alt+/ read status" to the on-screen status only when a screen reader is running.
- In an AbCS message, Escape works like Cancel, or like No when the message has no Cancel. When Escape must not answer a visible button, pass `escape_only_button` to `exec_styled_message_box`. Review each stays on the book this way. Escape and the close box both run the same unsaved-changes check.
- If Tab would leave a table and the next control is hidden, keep focus on the current cell. The main table does this when no footer button is showing.
- Selecting many table rows uses [`rows_to_selection`](../../src/ui/table_selection.py): one range per run of consecutive rows, not one selection per cell.
- Speech of the main window, the book table, and the selected book when a dialog closes is expected. Treat it as a bug only when that speech cuts off a message the user still needs, or when focus goes to the wrong window. Web Metadata stores `saved_message` and the caller announces it after focus is back.

Still not on every window:

- Unmapped Alt+letter beeps from one shared place. Several windows are still silent.
- First focus is `showEvent` plus `QTimer.singleShot(0, ...)`, not the constructor and not a timer started in `__init__`. Read date and Recently Added were moved. About, License, Backup, Book Details, Collection, Help, and the update check still set focus earlier.
- Shortcut hints are not yet removed from every status message.

External reference (patterns + principles):

- [PySide6 Accessibility Patterns](https://github.com/cfdrakeNS/pyside6-screen-reader-accessibility/blob/main/doc/PySide6_Accessibility_Patterns_and_Implementation_Reference.md)
- [Screen Reader Best Practices](https://github.com/cfdrakeNS/pyside6-screen-reader-accessibility/blob/main/doc/PySide6_Screen_Reader_Accessibility_Best_Practices.md)
- [AbCS Standards Crosswalk](https://github.com/cfdrakeNS/pyside6-screen-reader-accessibility/blob/main/doc/AbCS_Standards_Crosswalk.md) (maps each standard here to the reference section and demo code)

### Buttons, footers, and control formatting

- New **QPushButton**s use [`build_accessible_button_style`](../../src/accessibility/style_helpers.py) with scaled height from `UIScaler` (same as Update / Delete / Import footers). Do not invent per-dialog button CSS.
- Footer action buttons on the main window follow `update_selection_ui()` visibility/enable rules (multi-select patterns like Update/Delete).
- Default button: only on a dialog with one clear main action. A form turns defaults off, and Enter clicks the focused button (Preferences). Not every existing form does this yet; a new or changed form must.
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
5. Open the window both ways — its Ctrl shortcut and its menu item (Alt+menu letter) — and confirm only the new window is spoken, not the main window title or book table. Trigger any confirm box (for example Escape with changes) and confirm no "<title> unavailable" before it. Speech of the main window and table when a dialog closes is expected; item 5 is about opening a window.
6. New buttons look and focus like existing AbCS buttons (highlight focus ring, scaled height).
7. Arrow through a table. Each move reads the cell content, not "row 2 column 1" or a row number.
8. Arrow through dialog prose. Each line is read once, not again as part of a longer line.
9. Up or Down on a year or date field speaks the new value. Arrowing a table or list does not fire a status announcement for that move. Extending a selection may still speak the title and the count.
10. An unavailable action says why. Escape and the window's close box both run the unsaved-changes check.
