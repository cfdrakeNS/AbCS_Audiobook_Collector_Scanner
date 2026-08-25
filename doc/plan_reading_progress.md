# Reading Progress / Bookmark — Future Improvement Plan

**Status:** Planned (not yet implemented)  
**Created:** June 2026  
**Related:** [Reading History](help_docs/13_reading_history.md), [plan_audiobook_preview.md](plan_audiobook_preview.md)

---

## What this is

Store **playback position** (file + timestamp or chapter) and **percent complete** per book — beyond binary read_date.

---

## Problem

`read_date` only marks finished. Users want resume position and partial progress.

---

## Design

- Columns: `progress_seconds`, `progress_file`, `progress_updated` OR single JSON field.
- UI: Book Details **Progress** read-only or edit; no embedded player in v1 — manual entry or future player sync.
- Distinct from read_date: progress &lt; 100% still unread.

**Estimate:** 2–3 weeks with UI; longer if tied to player

---

## Tests

Progress save/load; read_date vs progress rules.

---

## Risks

Product direction shifts toward player app — conflicts with collection-manager focus.

---

## Out of scope v1

Auto-sync from OS player; chapter markers for m4b.
