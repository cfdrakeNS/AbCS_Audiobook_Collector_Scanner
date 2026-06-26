# CI and Test Hardening — Future Improvement Plan

**Status:** Planned (not yet implemented)  
**Created:** June 2026  
**Related:** [TESTING.md](../TESTING.md), [plan_enhancements_fall2026.md](plan_enhancements_fall2026.md)

---

## What this is

Strengthen automated regression around fall waves — not a user-facing feature. Supports **unit testing as you go**.

---

## Problem

New modules (cover_storage, rescan_matcher, etc.) need consistent CI coverage. Ad-hoc test adds may miss integration paths.

---

## Design

| Item | Action |
|------|--------|
| CI | Ensure [`.github/workflows/pytest.yml`](../.github/workflows/pytest.yml) runs on PR; optional Windows runner if feasible |
| Coverage | Optional `pytest-cov` report for `src/core/` and `src/database/` — threshold advisory not blocking v1 |
| Wave gates | Document in [qa_verification.md](qa_verification.md) per-wave manual + automated checklist |
| New module rule | Each new `src/core/*.py` ships with `test/test_*.py` in same PR |

**Estimate:** 1–2 days setup + ongoing discipline

---

## Tests

Meta — CI itself; smoke test that imports all UI modules (optional).

---

## Out of scope v1

Full UI automation; coverage gates blocking merge.
