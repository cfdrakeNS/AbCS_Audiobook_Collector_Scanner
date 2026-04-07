# Double-Trigger Analysis And Fix Progress

Date: 2026-04-06
Branch analyzed: final
Scope: `src/ui` plus shared announce helper behavior, including both Alt+/ and normal status updates

## Goal
Identify windows that currently produce duplicate or near-duplicate announcements, including cases triggered by regular status updates (not only Alt+/).

## Important Clarification
Yes, dual announcing can happen on normal status updates.

Reason:
- `announce_status_message(...)` always does `status_bar.showMessage(message)`.
- When `move_focus=True`, it also moves focus to the status bar to force a read.
- If the caller already updates status frequently, the focus-move announce pattern can create repeated speech events.

Evidence in shared helper:
- `src/accessibility/accessible_events.py`: line 35 (`status_bar.showMessage(message)`)
- `src/accessibility/accessible_events.py`: line 43 (`if move_focus and QAccessible.isActive(): ...`)

## Findings Summary (High-Use First)

### Priority 1 (Main Window, high-use and high impact)

1) `src/ui/main_window.py` - status updates default to announce
- Pattern:
  - `set_status(..., announce: bool = True)` defaults to announce for every call unless explicitly overridden.
- Evidence:
  - line 1307: `def set_status(... announce: bool = True)`
- Why this matters:
  - Many routine status updates in main will trigger focus-move speech by default.
  - This increases repeated announcements in normal navigation, not just Alt+/.
- Update:
  - `set_status(...)` now defaults `announce=False` in main window.
  - Explicit spoken messages remain opt-in via `announce=True`.

2) `src/ui/main_window.py` - one selection event can trigger two announcement paths
- Pattern:
  - Selection change path calls `update_selection_ui()` and then `announce_selection()`.
  - `update_selection_ui()` calls `set_default_status(announce=has_selection)`.
  - `announce_selection()` calls `set_status(announcement, timeout_ms=0)` (inherits announce=True default).
- Evidence:
  - line 1985: `def on_table_selection_changed(...)`
  - line 2497: `self.set_default_status(announce=has_selection)`
  - line 2012: `self.announce_selection()`
  - line 2464: `self.set_status(announcement, timeout_ms=0)`
- Why this is likely heard as double:
  - Two consecutive status announcements occur from a single user selection action.
- Update:
  - Selection announcement path now explicitly uses `announce=True` only where selection speech is intended.

### Priority 2 (Confirmed duplicate trigger path)

3) `src/ui/import_progress_window.py`
- Previous pattern: Alt+/ was wired in three places.
- Previous evidence:
  - local `QShortcut("Alt+/")`
  - `eventFilter` manually called status read on Alt+/
  - `keyPressEvent` also manually called status read on Alt+/
- Update:
  - Removed the manual `eventFilter` and `keyPressEvent` Alt+/ handlers.
  - Kept a single local `QShortcut("Alt+/")` as the sole owner.
  - Added event-filter pass-through for Alt+/ variants (`Alt+/`, `Alt+7`) so unmapped Alt-key blocking does not interfere on layouts that emit `/` as `7`.
- Current status:
  - Tested after changes: status read still does not speak reliably during active scanning.
  - Leave this item until the end; it remains unresolved and needs a fresh focused pass.

### Priority 3 (Previously intentional multi-announce; now flattened)

4) `src/ui/reading_history_window.py`
- Pattern: Date Range Alt+/ intentionally performs a two-step announce.
- Evidence:
  - lines 742-748: first announce of period message
  - line 751: delayed second step (`QTimer.singleShot(1000, self._announce_status_bar)`)
  - lines 760-763: helper announce of status message
- Update:
  - Changed to a single Alt+/ announcement path to avoid duplicate reads.

### Priority 4 (Resolved)

5) `src/ui/name_list_window.py` (non-collection mode)
- Previous pattern: Alt+F was owned by both centralized mapping and a local shortcut.
- Resolution:
  - Removed the local `QShortcut("Alt+F")` so centralized registration is now the sole owner.
  - Updated help text and accessibility wording so Alt+F is described consistently as clear find / new search.
- Result:
  - Shortcut ownership is no longer split, reducing focus/state-dependent ambiguity.

## Progress Update (Current)

Completed:
- `src/ui/main_window.py`
  - Reduced duplicate selection announcement behavior.
  - Removed Find success status echo of title/author.
  - Restored table keyboard focus after no-match popup.
  - Changed `set_status(...)` default to `announce=False` to reduce passive speech churn.
  - Kept selection announcement speech explicit with `announce=True`.
  - Changed refresh flow default status reset to `set_default_status(announce=False)` to avoid passive announce on routine refresh.
  - Verified in testing: passive updates are quiet while explicit selection/status reads still work.
  - Restored the no-data popup for Fetch Web Info when no meaningful web metadata is found.
- `src/ui/book_details.py`
  - Web metadata lookup now relies on a single `WebBookAPI` cascade instead of repeating manual refresh retries.
- `src/accessibility/accessible_events.py`
  - Added short-window dedup guard for repeated focus announcements.
  - Kept changes focused on duplicate-read suppression only.
- `src/ui/import_progress_window.py`
  - Reduced status-bar noise and collapsed Alt+/ routing to a single shortcut path.
  - Manual Alt+/ handling in `eventFilter` and `keyPressEvent` was removed.
  - Added event-filter pass-through for Alt+/ variants (`Alt+/`, `Alt+7`) so unmapped Alt-key blocking does not interfere on keyboard layouts that emit `Alt+7` for `/`.
  - Repeated-read behavior during active scanning still needs runtime verification.
- `src/ui/import_window.py`
  - Added duplicate-announcement suppression window in status updates to reduce repeated reads.
  - Changed canceled scan summaries to put `Scan canceled` at the beginning of the status text.
- `src/ui/reading_history_window.py`
  - Replaced two-step Alt+/ (period + delayed status) with one announcement path.
  - Updated Alt+/ to read only the currently visible status-bar text (no tab-specific fallback synthesis).
  - Removed status-bar accessibility label in this window to reduce extra screen-reader noise.
  - Prevented Date Range status text from overwriting General tab status on window open.
  - Added explicit initial tab status on open (for example, `Viewing General statistics`).
  - Added standard `Ctrl+Tab` / `Ctrl+Shift+Tab` tab switching.
- `src/ui/backup_restore_window.py`
  - Updated Alt+/ to read only the currently visible status-bar text.
  - Removed status-bar accessibility name/description in this window to reduce extra spoken noise.
  - Prevented Alt+/ keypress from being overwritten by shortcut-hint status text.
- `src/ui/name_list_window.py`
  - Removed the duplicate local Alt+F shortcut.
  - Aligned F1 help and accessibility text with the actual clear-find/new-search behavior.

Preventive audit completed:
- `src/ui/update_window.py`
  - Audited Alt+/ handling and event-filter behavior.
  - No confirmed double-trigger path found in current code.
- `src/ui/book_list_import_window.py`
  - Audited Alt+/ handling and event-filter behavior.
  - No confirmed double-trigger path found in current code.

Remaining priority order:
1. `src/ui/import_progress_window.py` (leave until the end): status read still does not speak reliably during active scanning and needs a fresh focused pass.
2. Final regression pass: confirm Alt+/ in all windows reads only visible status text with no extra label chatter.

## Verification Checklist for Later
- In Main Window selection actions, confirm exactly one spoken message per action.
- In Main Window passive status updates (sort/filter/refresh), confirm they do not force repeated focus-jumps.
- In Main Window refresh operations, confirm default status returns without a forced announcement.
- Confirm one spoken announcement per Alt+/ press in each affected window.
- In Import Progress window, confirm repeated Alt+/ presses continue to read status during active scanning.
- In Import Progress window on layouts that emit `/` as `Alt+7`, confirm Alt+7 also triggers one status read.
- In Backup / Restore and Reading History windows, confirm Alt+/ speaks only visible status text (no extra status-bar label/description noise).
- In Update Window and Book List Import Window, keep an eye out for duplicate Alt+/ reads during general window testing, but no current code-level issue is confirmed.
- In Name List window, confirm Alt+F performs one clear-find/new-search action and matches the F1 help text.
- Re-test with both JAWS and NVDA.
- Re-open F1 shortcut lists to verify displayed shortcuts match runtime behavior.

## Notes
- Main-window duplicate status behavior has been addressed in current branch work.
