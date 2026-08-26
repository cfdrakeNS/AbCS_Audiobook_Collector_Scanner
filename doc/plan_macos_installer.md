# macOS Installer — Future Improvement Plan

**Status:** Cancelled — out of scope (decided Aug 2026, see [launch_plan.md](launch_plan.md))  
**Created:** June 2026  
**Related:** [linux_build.md](linux_build.md), [INSTALL.md](../INSTALL.md)

> **Decision (Aug 2026):** Dropped from the roadmap — too complex/expensive for the value it adds right now. macOS users continue to run AbCS from source (already documented in [INSTALL.md](../INSTALL.md)). This plan is kept for historical reference only; do not schedule it without a new decision.

---

## What this is

Packaged **macOS build** (.app / dmg) with same accessibility and help bundling as Windows/Linux installers.

---

## Problem

AbCS runs on macOS in dev; no documented installer path for testers on Mac.

---

## Design

- PyInstaller one-folder or one-file `.app` bundle.
- Code signing / notarization notes for distribution (user responsibility).
- `get_user_data_dir()` already supports macOS Application Support path.
- Test: VoiceOver smoke on Book Details + main window.

**Estimate:** 1–2 weeks (platform-specific debugging)

---

## Tests

CI macOS runner optional; manual VM checklist.

---

## Out of scope v1

Mac App Store listing.
