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

### Priority 2 (Confirmed duplicate trigger path)

3) `src/ui/import_progress_window.py`
- Pattern: Alt+/ is wired in three places.
- Evidence:
  - line 150: local `QShortcut("Alt+/")`
  - lines 166-173: `eventFilter` manually calls status read on Alt+/
  - lines 182-189: `keyPressEvent` also manually calls status read on Alt+/
- Impact:
  - Same key can trigger multiple announce paths depending on focus/event order.

### Priority 3 (Previously intentional multi-announce; now flattened)

4) `src/ui/reading_history_window.py`
- Pattern: Date Range Alt+/ intentionally performs a two-step announce.
- Evidence:
  - lines 742-748: first announce of period message
  - line 751: delayed second step (`QTimer.singleShot(1000, self._announce_status_bar)`)
  - lines 760-763: helper announce of status message
- Update:
  - Changed to a single Alt+/ announcement path to avoid duplicate reads.

### Priority 4 (Shortcut overlap, lower than main-window speech churn)

5) `src/ui/name_list_window.py` (non-collection mode)
- Pattern: Alt+F appears owned by both centralized mapping and local shortcut.
- Evidence:
  - line 458: centralized registration includes `find_edit`
  - lines 476-478: local `QShortcut("Alt+F")` for clear-find
- Impact:
  - Possible conflicting behavior based on state/focus.

## Progress Update (Current)

Completed:
- `src/ui/main_window.py`
  - Reduced duplicate selection announcement behavior.
  - Removed Find success status echo of title/author.
  - Restored table keyboard focus after no-match popup.
- `src/accessibility/accessible_events.py`
  - Added short-window dedup guard for repeated focus announcements.
  - Kept changes focused on duplicate-read suppression only.
- `src/ui/import_progress_window.py`
  - Reduced status-bar noise and tried multiple Alt+/ routing approaches.
  - Remaining issue: during active scanning, Alt+/ reads on the first press but not reliably on repeated presses.
  - Current state should be treated as unresolved and needs a fresh pass next session.
- `src/ui/import_window.py`
  - Added duplicate-announcement suppression window in status updates to reduce repeated reads.
- `src/ui/reading_history_window.py`
  - Replaced two-step Alt+/ (period + delayed status) with one announcement path.

Remaining priority order:
1. `src/ui/import_progress_window.py`: make repeated Alt+/ reads work reliably during active scanning.
2. `src/ui/name_list_window.py`: resolve Alt+F ownership (centralized vs local).

## Verification Checklist for Later
- In Main Window selection actions, confirm exactly one spoken message per action.
- In Main Window passive status updates (sort/filter/refresh), confirm they do not force repeated focus-jumps.
- Confirm one spoken announcement per Alt+/ press in each affected window.
- Re-test with both JAWS and NVDA.
- Re-open F1 shortcut lists to verify displayed shortcuts match runtime behavior.

## Notes
- Main-window duplicate status behavior has been addressed in current branch work.
