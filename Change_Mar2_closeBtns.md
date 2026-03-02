# Change Mar 2 - Remove Close Buttons (All Windows)

## Goal
Remove explicit **Close** buttons across AbCS windows and rely on **Escape** (and standard window close) for dismissal.

## Reasoning
1. Escape already closes dialogs/windows.
2. Fewer shortcuts and fewer footer buttons reduces cognitive load.
3. Improves consistency for screen-reader users by reducing duplicate close/cancel affordances.

## Scope
- Remove UI close buttons where they are only for window dismissal.
- Keep action buttons that are true workflow actions (Save, Update, Delete, Scan, Add, Export, etc.).
- Preserve safety prompts and cancel-in-progress flows (scan/add operations) where behavior is not equivalent to close.

## Critical Caution
Some "Close" controls are **reused as Cancel** with label swap during active operations (example pattern already present in Import Window).
- Do **not** remove these without replacing the cancel-in-progress path.
- If a button serves both Close and Cancel, convert to **Cancel-only during active operation**, and rely on Escape/window close when idle.

---

## Window-by-Window Approach

## Phase 1: Inventory and Classification
For each window in `src/ui/`:
- Identify footer buttons and classify each as:
  - `dismiss-only` (safe to remove)
  - `cancel-edit` (may be required)
  - `cancel-operation` (must retain equivalent behavior)
  - `action` (must keep)
- Identify where `reject()`, `closeEvent`, `on_cancel*` are used.
- Identify where a close button is also in tab order and shortcut help text.

Suggested initial candidates from current code scan:
- `src/ui/import_window.py` (has close/cancel dual behavior)
- `src/ui/import_progress_window.py` (close shown post-completion)
- `src/ui/preferences_window.py` (Cancel used for revert flow)
- `src/ui/update_window.py` (explicit Close button)
- `src/ui/name_list_window.py` (cancel/edit workflows)
- `src/ui/book_details.py` and `src/ui/import_detail_window.py` (dismiss/navigation flows)

### Per-Window Action Matrix (Phase 1)

| Window | Current Close Control | Classification | Planned Action | Risk |
|---|---|---|---|---|
| `src/ui/import_progress_window.py` | Footer `&Close` + `Alt+C` (post-complete) | dismiss-only | **Remove button + Alt+C**, keep `Escape` close and `Alt+L` cancel while active | Low |
| `src/ui/update_window.py` | Footer `&Close` | dismiss-only | **Remove button**, keep `Escape` close | Low |
| `src/ui/preferences_window.py` | Footer `Cancel` (revert+close), help dialogs with `Close` | cancel-edit | Keep cancel workflow; remove only help-dialog close buttons later if desired | Medium |
| `src/ui/name_list_window.py` | Footer `&Close` plus edit `Cancel` | mixed (dismiss + cancel-edit) | Remove dismiss-only close, keep edit cancel path | Medium |
| `src/ui/collection_window.py` | Footer `&Close` plus edit `Cancel` | mixed (dismiss + cancel-edit) | Remove dismiss-only close, keep edit cancel path | Medium |
| `src/ui/import_window.py` | Footer button toggles `Close`/`Cancel` by scan state | cancel-operation reuse | Split to operation-cancel only; no idle close button | High |
| `src/ui/book_details.py` | Footer `&Close` plus `Cancel` for edit state | mixed (dismiss + cancel-edit) | Remove dismiss-only close, keep cancel-edit and Escape behavior | High |
| `src/ui/import_detail_window.py` | Footer close/dismiss flow + unsaved guards | dismiss with guard | Remove close button, keep reject/unsaved confirmation and Escape | Medium |
| `src/ui/backup_restore_window.py` | Footer `&Close` + `Alt+C` | dismiss-only | Remove close button + Alt+C, keep `Escape` | Medium |

### Phase 1 Progress (This Pass)
- Completed: `import_progress_window.py` (close button removed).
- Completed: `update_window.py` (close button removed).
- Completed: `name_list_window.py` (dismiss-only close removed; Escape close added).
- Completed: `collection_window.py` (dismiss-only close removed; Escape close added).
- Completed: `backup_restore_window.py` (dismiss-only close removed; Escape retained).
- Completed: `book_details.py` (dismiss-only close removed; Escape retained).
- Completed: `import_window.py` (idle close removed; footer action is cancel-only during active scan).
- Completed: helper/shortcut pop-up dialog cleanup (removed local `Close` buttons, rely on Escape/window close).
- Completed: non-F1 informational popup cleanup (Display Audit + Main stats popup `Close` buttons removed).
- Completed: empty-DB startup options dialog buttons now use shared accessible popup button styling.
- Completed: Import Progress follow-up fixes for JAWS (F1 dialog table format, valid-shortcuts-only list, Alt+/ post-complete focus handling).

## Current Status (End of Day)
- This **Close-button removal** change set is functionally complete.
- All targeted regressions and full suite runs passed during implementation (`24 passed`).
- Escape-based dismissal is now the consistent close path across the updated windows/dialogs.

## Remaining Work (Outside This Change Set)
1. **Accessibility gaps** from `accessibility_gap_Todo.md`.
2. **Shortcut normalization** pass (consistency review and cleanup across all windows).

## Suggested Next Session Start
- Begin with `accessibility_gap_Todo.md` high-priority items.
- Then run a focused shortcut-normalization pass (labels, help text, allowed Alt letters, and status announcements).

## Phase 2: Behavioral Rules
Apply consistent rules:
- **Dialogs/windows**: Escape closes (existing behavior retained/added).
- **Long-running operation windows**: keep **Cancel operation** action while active.
- Remove **Close** button in idle states when dismiss path via Escape/window close exists.
- Keep any confirmation prompts required for unsaved/partial state.

## Phase 3: Shortcut Changes
Per affected window:
- Remove `Alt+<close-key>` shortcut registration where tied to removed Close button.
- Keep `Escape` handling.
- Update F1 shortcut help list to remove close-key entry.
- Update status messages that announce close shortcut text.

## Phase 4: Alt-Key Blocking Updates
Per affected window with `ALLOWED_ALT_LETTERS` + `is_unmapped_alt_letter`:
- Remove letter assigned only to removed Close button.
- Keep letters still mapped to active controls/actions.
- Validate no mapped shortcut is blocked by stale allowlist.

## Phase 5: UI + Focus/Tab Order Cleanup
For each removed button:
- Remove from layout.
- Remove from `setTabOrder` chain.
- Remove signal connections and dead handler code if no longer used.
- Ensure focus lands on a sensible control after operation completion.

## Phase 6: Accessibility Text Cleanup
Per window:
- Update accessible descriptions that mention removed close shortcut.
- Update keyboard-shortcuts dialogs/help text.
- Keep status-bar announcements accurate and concise.

---

## Implementation Safety Checklist
For each edited window:
- [ ] Close button removed only if dismiss-only.
- [ ] Escape closes window/dialog.
- [ ] Cancel-in-progress behavior still available when needed.
- [ ] Tab order has no removed controls.
- [ ] Shortcut help text is current.
- [ ] `ALLOWED_ALT_LETTERS` matches active Alt shortcuts.
- [ ] No orphan signal connections/handlers remain.

## Testing & Validation Plan

## 1) Targeted per-window manual checks
For each modified window:
- Open window, verify no close button shown (if in scope).
- Press Escape -> window closes or triggers expected cancel-confirm flow.
- Run each remaining Alt shortcut and verify action executes.
- Verify F1 shortcut help reflects current keys.
- Verify JAWS/NVDA reads status/help without stale "Alt+Close" guidance.

## 2) Operation-state checks
For windows with active operations:
- Start operation.
- Verify cancel path remains reachable and announced.
- Verify idle state no longer exposes redundant close button.

## 3) Regression tests
- Run existing targeted tests around edited windows.
- Add tests only where there is established test coverage pattern.
- Re-run full suite after all windows updated.

## 4) Accessibility validation
- Keyboard-only traversal through each affected window.
- Confirm no focus traps after button removal.
- Confirm status bar messages and shortcut lists are accurate.

---

## Suggested Execution Order
1. `import_progress_window.py` (cleanest close-only candidate)
2. `update_window.py`
3. `preferences_window.py` (careful: cancel semantics)
4. `name_list_window.py`
5. `import_window.py` (highest caution: close/cancel reuse)
6. detail windows (`book_details.py`, `import_detail_window.py`) as needed

---

## Done When
- Close buttons are removed where redundant.
- Escape-based dismissal is consistent.
- Cancel semantics are preserved for active operations and unsaved edits.
- Shortcut docs, Alt blocklists, and status messaging are all aligned.
- Manual accessibility checks and test suite pass.
