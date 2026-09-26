# Want to read and playing filter — Version 3 Phase 25

**Status:** Planned (after Phase 24 Path health)  
**Estimate:** 0.5–1 day  
**Depends on:** Phase 20 (Want to read filter), Phase 21 (In progress filter)

---

## Goal

One main-list filter that shows **only** books you are actively managing: marked **Want to read**, or **playing** (in progress / saved listen position), or both.

Today Want to read (View → Want to read / Alt+T) and In progress are separate filters. This phase adds a combined view so you do not have to flip between them.

---

## Behavior

1. **View** menu item (and matching toolbar/status language if used elsewhere): e.g. **Want to read and playing**.
2. When on, the main list shows books that match **either** Want to read **or** In progress (listen progress saved). Books that match both appear once.
3. Turning this filter on clears or supersedes the separate Want to read–only and In progress–only filters (same mutual-exclusion pattern as other exclusive View filters).
4. Alt+letter and accessible name/description for the new View action; status announces when the filter turns on or off.
5. Help: short note under find/filters and shortcuts (after the filter ships; Phase 16 can fold it in).

---

## Out of scope

- Bulk mark Want to read (deferred)
- Changing how listen progress is stored
- Path health or other Manage reports

---

## Gate

- Filter shows the union of Want to read and In progress; no duplicates
- Keyboard and screen reader can turn it on/off; Alt+/ status is clear
- Existing Want to read–only and In progress–only filters still work when chosen alone
