# Preferences Process

## What this is

Preferences controls how AbCS looks and how **import** behaves: theme, zoom, default import folder, audio formats, import scenario, fallback rules, and validation. Changes apply to future sessions after you save.

## When to use it

- Before your first large import — set scenario, formats, and validation rules.
- Adjust theme or zoom for readability.
- Reset all settings to factory defaults.

## Before you start

- Theme and zoom **preview immediately** while the dialog is open.
- Other import settings apply on the **next** Import scan (close and reopen Import if it is already open).
- Factory defaults are listed in [Default preferences](14_default_preference.md). Import scenario detail is in [Import preferences](15_import_preferences.md).

## Steps

1. Open **Manage → Preferences** (**Alt+M**, then **P**).
2. Work through the four tabs:

### Display Settings (Alt+D)

- **Theme** — system default or high-contrast themes.
- **Zoom** — preset or custom scale (default **150%** after Restore Defaults).

### Import Settings (Alt+P)

- **Default import directory** — pre-fills Import window (Alt+B to browse).
- **Audio formats** — which extensions to scan.
- **Import scenario** — how folders map to author, title, and series (default: **Mass Standard Import**). See [Import preferences](15_import_preferences.md).

### Fallback and Parsing (Alt+F)

- **Author fallback to folder** / **Title fallback to file** — fill missing tags from paths.
- **Reader keywords** — detect narrator in comments.

### Validation Rules (Alt+V)

- Duplicate matching and fuzzy percent.
- Title/author consistency, length limits, folder structure, year checks.
- Each rule: off, warning, or error.

3. Click **Save** (Alt+S) to keep changes.
4. To reset everything: **Restore Defaults** (Alt+R), confirm **Yes**, then **Save**.
5. Press **Alt+/** to re-read the status bar.
6. Press **Escape** to close. If you have unsaved changes, AbCS asks whether to save, keep editing, or discard.

## What happens next

- Saved preferences persist across restarts (Qt settings).
- Import, web metadata duplicate options, and display settings use the new values on the next relevant action.

## Shortcuts and accessibility

| Shortcut | Action |
|----------|--------|
| Alt+M, P | Open Preferences (Manage menu) |
| Alt+D | Display Settings tab |
| Alt+P | Import Settings tab |
| Alt+F | Fallback and Parsing tab |
| Alt+V | Validation Rules tab |
| Alt+B | Browse default import directory |
| Alt+R | Restore Defaults |
| Alt+S | Save |
| Ctrl+Tab / Ctrl+Shift+Tab | Move between tabs |
| Alt+/ | Re-read status |
| F1 | Help for this window |

## Common confusion

**I changed preferences but Import behaved the same.**
Close the Import window and start a new scan, or reopen Import after saving.

**Restore Defaults vs Save**
Restore Defaults resets fields in the dialog only until you click **Save**. Press **Save** to write defaults to disk.

**Where are zoom and theme on the main window?**
You can also use **View → Zoom In/Out/Reset** (Ctrl+/Ctrl-/Ctrl+0) without opening Preferences.

## Related documentation

- [Default preferences](14_default_preference.md) — factory values
- [Import preferences](15_import_preferences.md) — scenario and validation detail
- [Import process](02_import_process.md) — folder scan workflow
- [Keyboard shortcuts by window](13_shortcuts_list.md)
