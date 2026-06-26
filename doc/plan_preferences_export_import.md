# Preferences Export / Import — Future Improvement Plan

**Status:** Planned (not yet implemented)  
**Created:** June 2026  
**Related:** [Preferences](help_docs/10_preferences.md), [preferences_window.py](../src/ui/preferences_window.py)

---

## What this is

Export AbCS **settings** (QSettings / import rules / UI scale) to a file and import on another machine — without copying the whole user data folder.

---

## Problem

New PC or test install requires reconfiguring preferences manually. Database backup does not include all QSettings keys.

---

## Design

- **Preferences → Export settings…** / **Import settings…**
- JSON file listing known keys from [`preferences_window.py`](../src/ui/preferences_window.py) save paths (document key list in plan implement phase).
- Import: confirm overwrite; merge vs replace — **v1 full replace of exported keys only**.
- Exclude: window geometry, last paths (optional separate checkbox).

**Estimate:** 2 days

---

## Tests

Round-trip export/import; invalid file handling.

---

## Accessibility

Confirm dialog for import; status announce.

---

## Out of scope v1

Sync settings across machines automatically; encrypt settings file.
