# Selection Mode Toolbar and Shortcuts — Version 3 Phase 4

**Status:** Complete — Phase 4  
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

- Footer **Update** / **Delete** / **Web fetch** (Alt+U / Alt+D)
- **Alt+W**, toolbar **Search Web**, and footer **Web fetch** when **two or more** books are selected run batch fetch. One selected book: Alt+W and Search Web still fetch that one book. Search Web stays enabled during selection.
- **Escape** (clear selection)
- Selection keys (Shift+arrows, etc.)
- **Alt+L**, **Alt+/**, **F1** / **Shift+F1**
- F1 while selecting lists only selection actions (Update, Delete, web fetch, extend selection, Escape, copy, status) — **not** column jump keys

## Disable and intercept

- Add Book (Ctrl+N), Import (Ctrl+I), Find (Ctrl+F)
- Statistics, Preferences
- Plot / Read / Recently added filters (Alt+P / Alt+R / recent toggle)

Do **not** disable Search Web during 2+ selection — that is the selection action, not a stray navigation control.

Disabled toolbar items stay visible. Blocked shortcuts announce via `set_status(..., announce=True)`: selection is active; **Escape to cancel selection**. First press does **not** clear selection.

**Enter** while selected: out of this plan unless tester reports it (today it opens Book Details).

---

## Implementation

- Helper `_selection_mode_active()` — `selected_book_ids` or `selection_anchor_row`, and not `duplicate_mode_active`.
- `update_selection_ui()`: `setEnabled(False)` on blocked toolbar `QAction`s; re-enable when selection clears. Footer unchanged.
- Shortcut handlers in `MAIN_WINDOW_SHORTCUTS` for N/I/F/P/R/splash/preferences: early return + announce.
- `on_get_web_info_clicked`: if `len(selected_book_ids) >= 2` and not duplicate mode, run batch fetch. Never open single-book web fetch for the focused row while 2+ are selected. No main-window Alt+B.
- `announce_selection()` uses `set_status(..., announce=True)` so JAWS/NVDA speak the selection line. Tests must assert that flag. Checking only `currentMessage()` does not prove speech.
- F1 while selecting lists live shortcuts only (Alt+W, Update, Delete, Shift+arrows, Escape, Ctrl+C, Alt+/). No Alt+1–7 or Alt+L column/list jumps.

Tests: `test/test_main_window_menus_shortcuts.py` — navigation actions disabled while selected; Search Web and footer Web fetch stay on; Alt+W with 2+ selected starts batch; one selected book does not batch; selection requests status speech. Help: Alt+W is one book or the selection.

---

## Tester gate

1. Select two books. Toolbar Add/Import/Find/Statistics/Preferences/filters disabled. Search Web stays enabled. Status is **spoken** and explains Escape.
2. Alt+W, Search Web, and footer Web fetch start **batch** fetch. Ctrl+F / Ctrl+I / Ctrl+N do not open windows; status announces Escape.
3. Alt+U, Alt+D, F1, Alt+/ still work. F1 during selection omits column jumps and blocked shortcuts.
4. Escape restores the toolbar. With no multi-select, Alt+W is one book again.
5. Duplicate mode unchanged.
6. Menus: arrow through disabled items (same list every time); JAWS/NVDA say the item is unavailable/disabled.
