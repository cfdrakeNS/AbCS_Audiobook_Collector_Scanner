# Auto-Update — Future Improvement Plan

**Status:** Planned (not yet implemented)  
**Created:** June 2026  
**Related:** [build_installer.iss](../build_installer.iss), releases folder

---

## What this is

In-app or installer **update check** — notify when a newer AbCS version is available with link to download.

---

## Problem

Users on old builds miss fixes unless they watch releases manually.

---

## Design (v1 minimal)

- **Help → Check for updates…** — fetch version manifest (JSON on GitHub releases or static URL), compare to [`APP_VERSION`](../src/build_config.py).
- Dialog: current vs latest; **Open download page** button.
- No silent auto-install in v1 (SmartScreen/signing complexity).

**Estimate:** 2–3 days

---

## Tests

Mock manifest; newer/older/same version logic.

---

## Risks

Offline users; privacy (optional telemetry off by default).

---

## Out of scope v1

Background delta updates; mandatory updates.
