# Selection Mode Toolbar and Shortcuts — Version 3 Phase 4

**Status:** Planned — Phase 4  
**Created:** September 2026  
**Related:** [plan_bulk_web_metadata.md](plan_bulk_web_metadata.md), [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md)

---

## What this is

While main-window **selection mode** is active, toolbar buttons and shortcuts that are **not** selection actions must not run. They are **blocked** (disabled + intercept). Escape remains the only way to cancel selection. Do **not** clear-and-then-run (click Import would drop the selection and open Import).

Separate from batch web fetch UI. Duplicate mode is unchanged.

---

## Problem

Selection (`selected_book_ids` in `src/ui/main_window.py`) already shows a footer (Update, Delete, Web fetch for 2+) and Escape clears selection. The **action toolbar and most shortcuts still fire** (Add Book, Import, Find, Search Web, Statistics, Preferences, plot/read/recent-added).

Search Web / Alt+W is especially wrong: `on_get_web_info_clicked` runs if `currentRow` is valid, which it always is during multi-select, so the “ignore selection” branch never runs.

---

## Keep enabled

- Footer **Update** / **Delete** / **Web fetch** (Alt+U / Alt+D / Alt+B)
- **Escape** (clear selection)
- Selection keys (Shift+arrows, etc.)
- **Alt+L**, **Alt+/**, **F1** / **Shift+F1**

## Disable and intercept

- Add Book (Ctrl+N), Import (Ctrl+I), Find (Ctrl+F)
- Search Web (Alt+W)
- Statistics, Preferences
- Plot / Read / Recently added filters (Alt+P / Alt+R / recent toggle)

Disabled toolbar items stay visible. Blocked shortcuts announce via `set_status(..., announce=True)`: selection is active; **Escape to cancel selection**. First press does **not** clear selection.

**Enter** while selected: out of this plan unless tester reports it (today it opens Book Details).

---

## Implementation

- Helper `_selection_mode_active()` — `selected_book_ids` or `selection_anchor_row`, and not `duplicate_mode_active`.
- `update_selection_ui()`: `setEnabled(False)` on blocked toolbar `QAction`s; re-enable when selection clears. Footer unchanged.
- Shortcut handlers in `MAIN_WINDOW_SHORTCUTS` for N/I/F/W/P/R/splash/preferences: early return + announce.
- If selection is active, never open single-book web fetch.

Tests: selection on → blocked actions disabled; Alt+W does not open web UI; Alt+U still works; after Escape, toolbar enabled. Help: one sentence on the main-window / shortcuts topic.

---

## Tester gate

1. Select two books. Toolbar Add/Import/Find/Search Web/Statistics/Preferences/filters disabled. Status still explains Escape.
2. Alt+W / Ctrl+F / Ctrl+I / Ctrl+N do not open windows; status announces Escape.
3. Alt+U, Alt+D, Alt+B, F1, Alt+/ still work.
4. Escape restores the toolbar.
5. Duplicate mode unchanged.
