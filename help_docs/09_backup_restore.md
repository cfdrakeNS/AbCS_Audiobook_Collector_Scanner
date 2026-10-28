# Backup and Restore

## What this is

Backup and Restore saves a copy of your whole AbCS database and restores it later. You can also delete old backup files, or run a full reset to start with an empty database.

## When to use it

- Before a large import or cleanup: create a backup first.
- To recover from a mistake: restore an earlier backup.
- To start completely fresh: run Full Reset, with care.

## Before you start

- **Backup** is safe at any time. Your current data stays as it is.
- **Restore** replaces your current database with the chosen backup. Create a backup of the current state first if you might need it.
- **Full Reset** deletes all books and collections. Use it only when you intend to start over.

## Window layout

- **Backup List:** a one-column list of backup files, newest first.
- **Browse** button, for a backup file stored somewhere else.
- **Restore file:** a read-only field that shows the file to restore.
- Buttons: **Backup**, **Restore**, **Delete**, and **Full Reset**.
- Status bar at the bottom.

The window opens with focus on the backup list. Tab order: backup list, Browse, Restore file, Backup, Restore, Delete, Full Reset.

## Create a backup

1. Open **Manage → Backup & Restore** (**Alt+M**, then **B**).
2. Press **Backup** (**Alt+K**).
3. AbCS saves a new backup file in its backup folder and adds it to the list.
4. The status bar confirms the backup.

## Restore from a backup

1. Select a backup in the list, or press **Browse** (**Alt+B**) to choose a backup file from another location.
2. The selected file appears in **Restore file** (**Alt+T**).
3. Press **Restore** (**Alt+R**).
4. Confirm when asked. Your current database is replaced.
5. When the restore completes, the main window refreshes and shows **All Collections**.

## Delete a backup file

1. Select a backup in the list.
2. Press **Delete** (**Alt+D**), or press the **Delete** key while the list has focus.
3. Confirm. The backup file is removed; your live database stays as it is.

## Full reset

1. Press **Full Reset** (**Alt+F**).
2. Confirm carefully. All data is cleared and an empty database is created.
3. The main window refreshes to All Collections.

Press **Escape** to close the Backup and Restore window.

## What happens next

- After a restore or full reset, the main book list reloads.
- The collection filter resets to **All Collections**.
- A status message on the main window says the database was updated.

## Mouse, shortcuts, and accessibility

- Click **Backup**, **Restore**, **Delete**, **Browse**, and **Full Reset** as needed.
- Click a backup in the list to select it before Restore or Delete.
- Click **Yes** or **No** on the confirmation messages.

| Shortcut | Action |
|----------|--------|
| Alt+M, B | Open Backup and Restore (main window) |
| Alt+L | Backup list |
| Alt+B | Browse for restore file |
| Alt+T | Focus restore file |
| Alt+K | Create backup |
| Alt+R | Run restore from selected backup |
| Alt+D | Delete selected backup |
| Alt+F | Full reset |
| Escape | Close window |
| Alt+/ | Re-read status |
| F1 | Keyboard shortcuts for this window |
| Shift+F1 | Help for this window |

## Common confusion

**Where are backup files stored?**
In the AbCS backup folder. The backup list shows the files there. You can also browse to a backup saved somewhere else.

**What happens to my backup files when I restore?**
They stay. Restore replaces only your live database. A backup file is removed only when you delete it.

**Should I back up before a restore?**
Yes, if you might want to return to your current state. To undo a restore, restore a different backup.

## Related help

- A readable copy of your book list (not a database backup): [Export Library](25_export_library.md)
