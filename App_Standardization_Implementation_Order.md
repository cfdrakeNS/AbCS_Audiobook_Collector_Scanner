# AbCS UI Standardization Roadmap (from `Feedback_app_structure.md`)

## Goal
Standardize the Main Window interaction model by moving filter/sort controls into menus, clarifying the Length field naming, and replacing the inline search box with an accessible popup search workflow.

## Source and Intent
This roadmap is derived from feedback in `Feedback_app_structure.md` (Wayne feedback). The objective is **consistency + accessibility** with minimal logic risk.

## Scope
- In scope:
  - Main window filter/sort/search UX standardization
  - Time → Length terminology update
  - Preserve status bar and focus behavior
- Out of scope (unless discovered as required):
  - New data model features
  - Non-related visual redesign
  - Changes to import logic unrelated to field naming/search behavior

## Recommended Implementation Order

## Current Status (as of 2026-03-03)
- ✅ **Phase 1 implemented in code** (UI terminology update only).
- Updated user-facing text from **Time** to **Length** in:
   - `src/ui/main_window.py` (table/header-facing labels)
   - `src/ui/book_details.py` (field label, dirty-field/status naming, shortcut help text)
   - `src/ui/import_detail_window.py` (field label, dirty-field/status naming, shortcut help text)
- ✅ **Phase 1 follow-up fix applied:** Restored `Alt+M` mnemonic behavior for Length fields in:
   - `src/ui/book_details.py`
   - `src/ui/import_detail_window.py`
   - Implementation detail: label changed to `Length (&M):` so `Alt+M` focuses the Length control.
- ✅ **Phase 2 implemented in code** (Collection filter moved to menu):
   - Added `View > Collections` submenu with dynamic collection list.
   - Main header Collection control is no longer visible to users.
   - `Alt+C` collection shortcut/handler removed (it only opened View menu).
- ✅ **Phase 3 implemented in code** (Read filter moved to menu):
   - Added `View > Read` submenu options (`All`, `Read`, `Unread`).
   - Main header Read control is no longer visible to users.
   - `Alt+R` read shortcut/handlers removed from Main Window definitions.
- ✅ **Phase 3 user validation complete:** reported working with no issues.
- ✅ **Phase 4 implemented in code** (Sort moved to menu):
   - Added dedicated top-level `Sort` menu with entries for table sort fields.
   - Main header `Order By` control is no longer visible to users.
   - Existing primary and non-primary sort behavior preserved.
   - `Alt+O` main-window shortcut binding removed.
- ✅ **Phase 5 implemented in code** (Find popup + legacy search path cleanup):
   - Rebranded user-facing Search to **Find**.
   - Added `Ctrl+F` menu/shortcut entry for Find popup.
   - Main inline search control is no longer visible to users.
   - Added Find dialog with field selection, exact-match toggle, and dialog status area.
   - Removed old live inline-search code paths (`on_search_changed`, `on_search_enter`, `on_search_timeout` wiring and related timer/event handling).
   - Added Find accessibility shortcuts (`Alt+I`, `Alt+T`, `Alt+X`, `Alt+/`).
- ✅ **Phase 6 completed** (accessibility/status/focus verification updates):
   - Sort menu mnemonic activation works via first-letter Alt behavior (like other menus).
   - Status bar now reflects all active sort modes (including non-primary sorts like Year).
   - Find dialog status reading added via `Alt+/` for screen-reader parity.
- Internal storage/logic names remain unchanged (`time_hours`, `time_minutes`, `time_edit`) to avoid schema/logic risk.

---

### Phase 0 — Baseline and Safety Net
1. Capture current behavior (manual checklist + existing tests).
2. Confirm all current shortcuts and focus behaviors (especially `Alt+S`, `Esc`, and status announcements).
3. Add/refresh regression checks for:
   - Main window filtering and sorting
   - Search find/fail behaviors
   - Status bar announcements

**Exit criteria:** Current behavior documented, tests/checklist ready before refactor.

---

### Phase 1 — Rename **Time** to **Length** (Do First)
> This should be first because it impacts multiple windows (`main`, `book_details`, `import_detail`).

**Implementation status:** ✅ Completed

1. Rename user-facing labels/headers from **Time** to **Length**.
2. Update related status bar messages and accessible names.
3. Keep underlying data storage unchanged unless schema change is explicitly required.
4. Verify display consistency across all affected windows.

**Why first:** Removes ambiguous terminology early and prevents rework in later UI changes.

**Exit criteria:** No visible “Time” labels remain where duration is intended; all related screens read “Length”.

---

### Phase 2 — Move Collection Filter to View Menu
**Implementation status:** ✅ Completed

1. Remove Collection combo from main header.
2. Add `View > Collections` submenu.
3. Dynamically list all collections.
4. Keep equivalent filtering behavior and selection persistence.
5. Ensure menu is keyboard accessible and screen-reader friendly.

**Exit criteria:** Collection filter works only via menu and matches previous results.

---

### Phase 3 — Move Read Filter to View Menu
**Implementation status:** ✅ Completed

1. Remove Reader/Read combo from main header.
2. Add `View > Read` submenu options:
   - All
   - Read
   - Unread
3. Preserve current filtering semantics.
4. Announce active filter changes in status bar.
5. Remove `Alt+R` shortcut and handlers.

**Exit criteria:** Read-state filter behavior is unchanged except for control location.

---

### Phase 4 — Move Order By to Sort Menu
**Implementation status:** ✅ Completed

1. Remove Order By combo from main header.
2. Add new `Sort` menu with one item per table sort field (Author, Title, Series, etc.).
3. Preserve existing custom sort implementations (author/title/series behaviors).
4. Indicate current active sort in status bar and/or checked menu state.

**Exit criteria:** All current sort options are available in `Sort` menu with equivalent ordering.

---

### Phase 5 — Replace Inline Search with Find Popup
**Implementation status:** ✅ Completed

1. Remove inline search box from main header.
2. Add popup find dialog with:
   - Field combo: Author, Title, Series, Genre
   - Editable find text box
   - Exact-match checkbox (checked = exact; unchecked = keyword find)
   - Status area compatible with screen readers
3. Behavior requirements:
   - `Enter`: attempt find; if found, close popup and move focus to matched item/column context
   - If not found: keep dialog open and announce status message
   - `Esc` in popup: close popup
   - `Ctrl+F`: open popup find dialog (standard Find shortcut)
4. Main window `Esc` behavior remains: clear search filter state.
5. Add menu entry for Find and map to `Ctrl+F`.

**Exit criteria:** Popup fully replaces old inline search UX and maintains keyboard/screen-reader usability.

---

### Phase 6 — Preserve/Verify Status Bar + Focus Rules
**Implementation status:** ✅ Completed

1. Validate all prior status bar messages still announce actionable state.
2. Verify focus transitions after filter/sort/search operations.
3. Confirm no regressions for JAWS/NVDA workflows.

**Exit criteria:** Accessibility behavior is at least equal to current baseline.

## Decision Notes / Open Clarifications
1. **Find menu location**
   - Implemented as `View > Find...` with `Ctrl+F`.
2. **Time → Length depth**
   - Default: UI label/accessibility text rename only.
   - Schema rename only if explicitly requested (higher migration risk).
3. **Status bar requirement in item 6 appears truncated**
   - Interpreted as: keep all existing status bar + focus rules intact.

## Suggested Delivery Milestones
- Milestone A: ✅ Phase 1 complete (Length terminology)
- Milestone B: ✅ complete (Phases 2–4 menu standardization)
- Milestone C: ✅ complete (Phase 5 Find popup + search-path cleanup)
- Milestone D: ✅ complete (Phase 6 accessibility regression pass)

## Next Test Focus (Post-Phase Cleanup)
- Optional: remove hidden legacy combo widgets entirely (Collection/Read/Order/Search) after behavior is frozen.
- Re-test `Ctrl+F` Find workflow and `Escape` clear behavior after cleanup refactor.
- Re-run keyboard shortcut help text review for any stale references.

## Validation Checklist (per milestone)
- Keyboard-only navigation complete
- `Alt` shortcuts work and are announced
- `Esc` behavior matches specification (popup close vs main filter clear)
- Status bar messages are meaningful and screen-reader readable
- Sorting/filtering/search return expected records
- No regressions in main/book_details/import_detail windows

## Rollout Strategy
- Implement phase-by-phase with verification after each phase.
- Avoid bundling all UX moves in one commit to simplify rollback.
- Keep behavior parity first; visual refinements second.
