# Export Library Options Window

**Status:** Proposed — for later review (after v3). Not scheduled. Five outstanding questions (see [Outstanding questions](#outstanding-questions)).  
**Created:** September 2026  
**Related:** [plan_export_library_metadata.md](plan_export_library_metadata.md) (v3 Phase 27, shipped export), [help_docs/25_export_library.md](../help_docs/25_export_library.md), [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md)

---

## What this is

Phase 27 exports the main list exactly as shown. To export one author, you have to set up the main window filters first. This plan adds an **Export Library** window where the user picks **what to export** directly, then saves.

---

## Problem

- Exporting one author, one series, or books read in a date range takes several filter steps on the main window, and then those filters have to be cleared again.
- The main window has no read-date range filter and no date-added *to* date (Recently Added has a *since* date only).

---

## Design

**File → Export Library...** (Alt+F, X) opens the window instead of going straight to the save dialog.

### Export — choose one (radio group)

Only one option is active at a time. Only the control that belongs to the chosen option is enabled; the rest are disabled and skipped by Tab.

| Option | Control | Books exported |
|--------|---------|----------------|
| Current list (default) | none | The main list as shown now, or the selection if books are selected (today's Phase 27 behavior) |
| Collection | Collection combo (All Collections or one) | Every book in that collection |
| Author | Author combo (one author) | Every book by that author |
| Series | Series combo (one series) | Every book in that series, sorted by series number |
| Read date | From and To date fields | Books with a read date in the range, including both ends |
| Date added | From and To date fields | Books added in the range, including both ends |

- Combos start on the main window's current value where there is one (collection filter; the focused book's author or series).
- Date fields use the typed masked date fields from [fix_read_date.md](fix_read_date.md), not `QDateEdit` spin behavior. Blank From means "from the start"; blank To means "up to today". To earlier than From is refused with a spoken message.

### Filters (apply on top of the chosen option)

| Filter | Values |
|--------|--------|
| Read | All, Read, Unread |
| Want to read | All, Want to read |
| In progress | All, In progress |
| Plot | All, With plot, Without plot |

- Defaults are **All**. With **Current list** chosen, the filter combos are disabled because the main list filters already apply.
- The same values and query code as the main window View menu filters (`SearchFilter` fields), so results match.

### Output

- **Format** combo: CSV (spreadsheet) or JSON. The save dialog opens with the matching file type.
- **Book count** line updates when the option, combo, dates, or filters change: "142 books will be exported." Updated quietly; spoken only on Alt+/.
- **Export** button (default) opens the save dialog; **Cancel** / Escape closes. After a successful save the window closes, the Phase 27 status message is spoken on the main window, and focus returns to the book list.
- Zero matching books: Export is disabled and the count line says "No books match."

### Keyboard (proposed; check against `shortcuts.py` before building)

| Key | Action |
|-----|--------|
| Alt+L | Current list |
| Alt+C | Collection |
| Alt+A | Author |
| Alt+S | Series |
| Alt+R | Read date |
| Alt+D | Date added |
| Alt+F | Format |
| Alt+E | Export |
| Escape | Cancel |
| Alt+/ | Re-read status (count) |
| F1 | Shortcuts for this window |
| Shift+F1 | Export Library help (topic 25) |

Alt on an option selects that radio and moves focus to its control (the combo or the From field). Filters get Alt letters only if free after the list above; otherwise they are reached by Tab.

---

## Implementation

| Area | Change |
|------|--------|
| New | `src/ui/export_library_window.py` — `AccessibleDialog` subclass |
| [`library_export.py`](../src/core/library_export.py) | No change to the writer; add a helper that builds the book list for an option + filters |
| [`queries.py`](../src/database/queries.py) | Add author, series, read-date range, and date-added *to* criteria to `BookQueries.get_all` (or a small export query). Read-date range can follow `reading_queries.py`. |
| [`models.py`](../src/database/models.py) | Optional new `SearchFilter` fields (`author_id`, `series_id`, `read_date_from/to`, `date_added_to`), defaulting to "no filter" so the main window is unchanged |
| [`main_window.py`](../src/ui/main_window.py) | `on_export_library` opens the window; passes the current list and selection for the default option |
| [`shortcuts.py`](../src/accessibility/shortcuts.py) | New context for the window |
| [`help_router.py`](../src/ui/help_router.py) | `WINDOW_HELP_MAP` entry → `25_export_library.md` |
| `help_docs/25_export_library.md`, `16_shortcuts.md` | Window section and shortcuts |

**Estimate:** 2–3 days.

---

## Tests

- Query tests: author only; series only (series-number order); read-date range inclusive at both ends; blank From / blank To; date-added range; each filter combined with each option.
- Window tests: only the chosen option's control is enabled; count updates; zero matches disables Export; To before From refused; Current list keeps selection behavior; format combo picks the file type.
- Existing `test_library_export.py` stays green.

---

## Accessibility

- Radio group has an accessible name ("Export"); each radio has a description naming its control.
- Disabled controls are not in the Tab order; JAWS/NVDA does not land on them.
- Editable combos use the anti-noise filter (plain Up/Down blocked, Alt+Up/Down allowed) like Book Details.
- Unmapped Alt+letter blocked in date and combo edits (`is_unmapped_alt_letter`).
- Count line changes are not announced on every keystroke; Alt+/ reads the current count. Errors (To before From) are announced.
- Buttons use `build_accessible_button_style`; Export is the default button.

---

## Outstanding questions

**Status: outstanding — not answered.** Answer all of these before building. Record each answer here with the date, then update the Design section to match.

| # | Question | Draft assumption | Answer |
|---|----------|------------------|--------|
| 1 | Should the options be combinable (for example one author **and** a read-date range), or strictly one option plus the filters? | One option plus the filters | Outstanding |
| 2 | Author and Series: all collections, or limited to the chosen collection filter on the main window? | All collections | Outstanding |
| 3 | Should the window remember the last option and format between uses (`QSettings`)? | No; always start on Current list and CSV | Outstanding |
| 4 | Keep a way to skip the window (for example Shift+Enter or a Preferences setting) for users who always export the current list? | No skip | Outstanding |
| 5 | Add a Ctrl shortcut for File → Export Library (for example Ctrl+E, to match Ctrl+I for Import)? Check for conflicts in `shortcuts.py` first. | No Ctrl shortcut; Alt+F, X only | Outstanding |

---

## Out of scope

Choosing columns; saving export presets; scheduled exports; ratings and tags.
