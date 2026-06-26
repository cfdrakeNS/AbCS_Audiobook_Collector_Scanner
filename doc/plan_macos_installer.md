# macOS Installer — Future Improvement Plan

**Status:** Planned (not yet implemented)  
**Created:** June 2026  
**Related:** [linux_build.md](../linux_build.md), [INSTALL.md](../INSTALL.md)

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
