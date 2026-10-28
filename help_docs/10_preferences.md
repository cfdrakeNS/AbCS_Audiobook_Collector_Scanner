# Preferences

## What this is

Preferences controls how AbCS looks and how **import** behaves: theme, zoom, default import folder, audio formats, import scenario, fallback rules, and validation rules.

## When to use it

- Before your first large import: set the scenario, formats, and validation rules.
- To adjust the theme or zoom for readability.
- To reset all settings to factory defaults.

## Before you start

- Theme and zoom change on screen as soon as you choose them.
- Import settings are used from the **next** Import scan.
- Factory defaults are listed in [Default preferences](17_default_preferences.md). Import scenario detail is in [Import preferences](18_import_preferences.md).

## Window layout

- **Tabs:** Display Settings, Import Settings, Fallback & Auto Correct, and Validation Rules.
- Each tab starts with a short instruction line, then its settings. At high zoom, the tab area scrolls.
- **Footer:** status bar, then the **Restore Defaults** and **Save** buttons.

Tab order on each tab: the instruction line, then each setting from top to bottom, then Restore Defaults and Save.

## Change preferences

1. Open **Manage → Preferences** (**Alt+M**, then **P**).
2. Move to a tab with its Alt key, or with **Ctrl+Tab** and **Ctrl+Shift+Tab**. You can also click a tab label.
3. Change the settings you want.
4. Press **Save** (**Ctrl+S**).
5. Press **Escape** to close. If you have unsaved changes, AbCS asks whether to save, keep editing, or discard.

## Display Settings (Alt+D)

- **Theme** — system default or high-contrast themes.
- **Zoom** — a preset, or drag the **Zoom** slider. The default is **150%**.
- **Web Metadata** — an optional Google Books API key for Fetch Web Info.
- **Automatically check for updates** — off by default. When checked, AbCS runs the same check as **Help → Check for updates** after the main window opens. A message appears only when a newer version is available.

Help has its own zoom, set at the top of the Help window. See [Help overview](01_overview.md).

## Import Settings (Alt+P)

- **Default import directory** — the folder Import starts with. Press **Alt+B** to browse. Choosing a collection in Import keeps this folder.
- With only one collection that has no collection folder, saving this folder also stores it as the collection folder. When the collection already has a folder and this field is empty, AbCS fills this field from the collection.
- **Audio formats** — which file types to scan.
- **Import scenario** — how folders map to author, title, and series. The default is **Mass Standard Import**. See [Import preferences](18_import_preferences.md).
- **Tag mapping** — which audio tags fill the book title and author. The defaults are **Album** for the title, and **Album artist then artist** for the author.
- Other tag choices are **Track title**, **Album then track title**, **Album artist only**, and **Artist only**. Files are still grouped by the album and album artist tags, so a multi-part book stays one book.

## Fallback & Auto Correct (Alt+F)

- **Author fallback to folder** and **Title fallback to file** — when checked, a missing tag is filled from the folder or file name. When unchecked, a missing author or title holds the book with an error.
- **Reader keywords** — words that find the narrator in comments.
- **Auto Correct** — four text cleanup options. Each has a main checkbox, with a **Skip review** checkbox indented below it.
- The options are: apply proper case to title and author; trim extra and leading or trailing spaces; remove leading punctuation from title and author; remove non-printable control characters. Accented letters such as é and ñ are kept.
- **Skip review** is available when its main option is checked. It lets a book be added automatically when that correction is its only issue.

## Validation Rules (Alt+V)

- Duplicate matching and the fuzzy duplicate percent.
- Title and author checks, length limits, folder structure, and year checks.
- Each rule is set to None, Warning, or Error.

## Restore defaults

1. Press **Restore Defaults** (**Alt+R**).
2. Confirm with **Yes**. Every setting goes back to its factory value and is saved right away.
3. The status bar says "All preferences restored to default values".

## What happens next

- Saved preferences are kept across restarts.
- Import and display use the new values from the next action.

## Mouse, shortcuts, and accessibility

- Click a tab label to switch sections.
- Use the dropdowns, checkboxes, and **Browse** button directly with the mouse.
- Click **Save** to keep changes, or **Restore Defaults** to reset everything.

| Shortcut | Action |
|----------|--------|
| Alt+M, P | Open Preferences (main window) |
| Alt+D | Display Settings tab |
| Alt+P | Import Settings tab |
| Alt+B | Browse for default import directory |
| Alt+F | Fallback & Auto Correct tab |
| Alt+V | Validation Rules tab |
| Alt+R | Restore Defaults |
| Ctrl+S | Save |
| Ctrl+Tab / Ctrl+Shift+Tab | Move between tabs |
| Tab/Shift+Tab | Move between controls in the current section |
| Escape | Close (asks about unsaved changes) |
| Alt+/ | Re-read status |
| F1 | Keyboard shortcuts for this window |
| Shift+F1 | Help for this window |

## Common confusion

**I changed preferences but Import behaved the same.**
Save Preferences, then run Import again. Each scan reads the latest saved settings.

**Do I need to Save after Restore Defaults?**
No. Restore Defaults saves the factory values as soon as you confirm.

**Can I change zoom without opening Preferences?**
Yes. On the main window, use **View → Zoom In**, **Zoom Out**, or **Reset**, or press **Ctrl+Plus**, **Ctrl+Minus**, or **Ctrl+0**.

## Related help

- Factory values: [Default preferences](17_default_preferences.md)
- Scenario and validation detail: [Import preferences](18_import_preferences.md)
- Folder scan: [Import (Folder Scan)](02_import.md)
- All shortcuts: [Keyboard shortcuts by window](16_shortcuts.md)
