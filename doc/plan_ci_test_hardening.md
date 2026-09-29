# CI and Test Hardening — Future Improvement Plan

**Status:** Complete — September 29, 2026. Existing Windows CI runs the full pytest suite on pushes and pull requests, with advisory coverage for `src/core/` and `src/database/`.
**Created:** June 2026  
**Related:** [TESTING.md](../TESTING.md), [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md)

---

## What this is

Strengthen automated regression around version 3 waves — not a user-facing feature. Supports **unit testing as you go**. The existing workflow and `TESTING.md` now cover the scheduled work; no extra coverage gate or UI automation is warranted.

---

## Problem

New modules (cover_storage, rescan_matcher, etc.) need consistent CI coverage. Ad-hoc test adds may miss integration paths.

---

## Design

| Item | Action |
|------|--------|
| CI | Complete: [`.github/workflows/pytest.yml`](../.github/workflows/pytest.yml) runs on Windows for pushes and pull requests |
| Coverage | Complete: `pytest-cov` reports advisory coverage for `src/core/` and `src/database/` |
| Wave gates | Use [TESTING.md](../TESTING.md) and the v3 phase-specific manual/accessibility gates |
| New module rule | Keep as review guidance: new core modules should ship with focused tests in the same change |

**Estimate:** Completed; maintain through normal review and CI.

---

## Tests

Meta — CI itself; smoke test that imports all UI modules (optional).

---

## Out of scope v1

Full UI automation; coverage gates blocking merge.
