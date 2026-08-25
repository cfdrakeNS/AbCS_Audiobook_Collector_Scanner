# Scheduled Backup Reminder — Future Improvement Plan

**Status:** Planned (not yet implemented)  
**Created:** June 2026  
**Related:** [Backup and Restore](help_docs/09_backup_restore.md), [Plan_covers.md](Plan_covers.md) (zip backup)

---

## What this is

Remind users to create a backup on a schedule or at key moments — not silent auto-backup without consent.

---

## Problem

Users forget to backup before large import/rescan. Zip backup (covers) makes backups more important.

---

## Design (v1)

**Preferences → Backup:**

- Checkbox: **Remind me to backup** (default on for new installs optional).
- Interval: every N days since last manual backup (7, 14, 30).
- Optional: remind on exit if last backup older than N days.

On trigger: accessible dialog — **Create backup now** / **Remind later** / **Don't ask for 30 days**.

Track `last_backup_reminder_dismissed` and last backup time via existing [`list_backups`](../src/database/connection.py) or QSettings.

**Estimate:** 1–2 days (after zip backup)

---

## Tests

Reminder logic with mocked dates; dismiss settings.

---

## Accessibility

Dialog buttons named; announce backup created.

---

## Out of scope v1

Fully automatic silent backup; cloud backup.
