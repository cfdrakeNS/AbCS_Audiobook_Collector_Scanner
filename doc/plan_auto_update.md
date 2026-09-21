# Auto-Update — Version 3 Phase 7

**Status:** Planned — **Version 3 Phase 7**  
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

Follow the master checklist: [Accessibility and UI formatting standards](plan_enhancements_version3_release.md#accessibility-and-ui-formatting-standards-all-phases).

Phase-specific:

- `AccessibleDialog` (or styled message box) with name and description.
- **Open download page** / **Close**: `build_accessible_button_style`; default focus on Open when an update exists, otherwise Close.
- Focus on Open download or Close on show; status announce of result on the main window after close.
- Offline / failure must be spoken — never a silent hang.

---

## Risks

Offline users; privacy (no telemetry).

---

## Out of scope v1

Background delta updates; mandatory updates; auto-download of the installer.
