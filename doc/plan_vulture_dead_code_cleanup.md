# Dead Code Cleanup (Vulture) — Future Improvement Plan

**Status:** Planned (not yet implemented)  
**Created:** June 2026  
**Related:** [CLEANUP_VULTURE_FINDINGS.md](../CLEANUP_VULTURE_FINDINGS.md)

---

## What this is

Periodic **maintenance pass** using vulture to remove unused code — between feature waves, not a product feature.

---

## Problem

Small dead symbols accumulate (`_plot_title`, unused helpers). Low risk but adds noise for agents and maintainers.

---

## Design

1. Run `python -m vulture src test --min-confidence 60`
2. Update [CLEANUP_VULTURE_FINDINGS.md](../CLEANUP_VULTURE_FINDINGS.md)
3. Remove confirmed dead code only; respect documented false positives
4. Run full pytest after removals

**Estimate:** 0.5–1 day per pass

---

## When to run

Between fall waves or before a release tag — not during active feature branches.

---

## Out of scope

Large refactors; renaming for style only.
