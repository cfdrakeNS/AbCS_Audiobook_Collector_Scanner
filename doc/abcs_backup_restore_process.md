# Backup and Restore Process

## What this is

Backup and Restore lets you save a copy of your entire AbCS database and restore it later. You can also delete old backup files or perform a full reset to start with an empty database.

## When to use it

- Before a large import or major cleanup — create a backup first.
- To recover from a mistake — restore a previous backup.
- To start completely fresh — use Full Reset (with caution).

## Before you start

- **Backup** is safe anytime and does not change your current data.
- **Restore** replaces your current database with the chosen backup. Create a backup of the current state first if you might need it.
- **Full Reset** deletes all books and collections. Use only when you intend to start over.

## Steps

1. Open **Manage → Backup & Restore**.
2. The window opens with focus on the **backup list**, which shows backup files already saved.

### Create a backup

3. Click **Backup** (Alt+K).
4. AbCS saves a new backup file in the app's backup folder and adds it to the list.
5. The status bar confirms success.

### Restore from a backup

3. Select a backup in the list, or click **Browse** (Alt+B) to choose a backup file from another location.
4. The selected file appears in the **Restore file** field (Alt+T to focus).
5. Click **Restore** (Alt+R).
6. Confirm the restore when asked. This replaces your current database.
7. When restore completes, the main window refreshes and shows **All Collections**.

### Delete a backup file

3. Select a backup in the list.
4. Click **Delete** (Alt+D), or press the Delete key while the list is focused.
5. Confirm deletion. This removes the backup file only, not your live database.

### Full reset

3. Click **Full Reset** (Alt+F).
4. Confirm carefully. This clears all data and creates an empty database.
5. The main window refreshes to All Collections.

5. Press **Escape** to close the Backup and Restore window.

## What happens next

- After restore or full reset, the main book list reloads.
- Collection filter resets to **All Collections**.
- A status message on the main window notes that the database was updated.

## Settings that affect this

None. Backup and Restore does not use import or display preferences.

## Shortcuts and accessibility

| Shortcut | Action |
|----------|--------|
| Alt+K | Create backup |
| Alt+L | Focus backup list |
| Alt+B | Browse for restore file |
| Alt+T | Focus restore file field |
| Alt+R | Restore |
| Alt+D | Delete selected backup |
| Alt+F | Full reset |
| Delete | Delete selected backup (when list focused) |
| F1 | Help for this window |
| Alt+/ | Re-read status |
| Escape | Close window |

## Things to test

- [ ] Create a backup — confirm it appears in the list and status announces success.
- [ ] Restore a backup — confirm books and collections match the backup date.
- [ ] Browse for a backup file outside the default list — confirm restore works.
- [ ] Delete a backup file — confirm it is removed from the list only.
- [ ] After restore, confirm main window shows All Collections and correct book count.
- [ ] Full reset — confirm empty database (test only if safe to do so).
- [ ] Press Alt+/ after backup and restore operations.

## Common confusion

**Where are backup files stored?**
AbCS keeps backups in its backup folder. The backup list in this window shows available files. You can also browse to a backup saved elsewhere.

**Does restore affect backup files?**
No. Restore changes your live database. Backup files in the list are not deleted unless you delete them.

**Should I backup before restore?**
Yes, if you might want to return to the current state. Restore cannot be undone except by restoring a different backup.
