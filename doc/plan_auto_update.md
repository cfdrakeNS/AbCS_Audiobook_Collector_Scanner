# Auto-Update — Version 3 Phase 4

**Status:** Planned — **Version 3 Phase 4**  
**Created:** June 2026  
**Updated:** September 2026  
**Related:** [build_installer.iss](../build_installer.iss), [src/build_config.py](../src/build_config.py), [src/app_urls.py](../src/app_urls.py), GitHub releases

---

## What this is

In-app **update check** — notify when a newer AbCS version is available with a link to the download page. No silent install.

---

## Problem

Users on old builds miss fixes unless they watch releases manually.

---

## Design (v1 minimal)

- **Help → Check for updates…** — fetch latest GitHub release (or a small version manifest URL), compare to [`APP_VERSION`](../src/build_config.py).
- Prefer the existing releases URL in [`app_urls.py`](../src/app_urls.py) / GitHub API `releases/latest`.
- Dialog: current vs latest; **Open download page** button (default focus).
- Offline / network failure: announce clearly; do not hang the UI (short timeout; run check off the GUI thread or use a brief wait dialog).
- No silent auto-install in v1 (SmartScreen/signing complexity).

**Estimate:** 2–3 days

---

## Tests

Mock manifest / API; newer / older / same version logic; offline error path.

---

## Accessibility

Accessible dialog name and description; focus on Open download or Close; status announce of result.

---

## Risks

Offline users; privacy (no telemetry).

---

## Out of scope v1

Background delta updates; mandatory updates; auto-download of the installer.
