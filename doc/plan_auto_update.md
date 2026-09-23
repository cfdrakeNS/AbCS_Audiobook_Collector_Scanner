# Auto-Update — Version 3 Phase 7

**Status:** Complete — tester accepted, including Preferences **Automatically check for updates** (default off) and the startup check. Tester build 2.17 still opens the Carrd test site for Help → Website and Open website. Before merge to main, point `ABCS_UPDATE_DOWNLOAD_URL` back at the live site.  
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

- **Help → Check for updates…** — read the latest GitHub release tag and compare it to [`APP_VERSION`](../src/build_config.py).
- **Preferences → Automatically check for updates** (`updates/auto_check`) — default **off**. When on, the same check runs after the main window is shown. The result dialog opens only when an update is available. Up to date and network errors stay silent on startup. Help → Check for updates still always shows the dialog.
- **Open website** and **Help → Website** open the Carrd **test** site `https://abcstest.carrd.co/` until merge to main. **Before merging, change `ABCS_UPDATE_DOWNLOAD_URL` in `src/app_urls.py` back to `ABCS_WEBSITE_URL` (`https://abcs.auroraaccessibility.com/`).** The GitHub API is only the version source.
- Dialog: current vs latest; **Open website** and **Close**. Enter activates the focused button. Alt+/ re-reads the result. F1 shortcuts. Shift+F1 help.
- Buttons use `build_modern_button_style`; default focus on Open website when an update exists, otherwise Close.
- Offline / network failure: announce clearly; do not hang the UI (short timeout; check off the GUI thread).
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
- **Open website** / **Close**: `build_modern_button_style`; default focus on Open website when an update exists, otherwise Close. Enter follows the focused button.
- Alt+/ re-reads the result; F1 shortcuts; Shift+F1 help.
- Focus on Open website or Close on show; status announce of result on the main window after close.
- Offline / failure must be spoken — never a silent hang.

---

## Risks

Offline users; privacy (no telemetry).

---

## Out of scope v1

Background delta updates; mandatory updates; auto-download of the installer.
