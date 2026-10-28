# Default Preferences

## What this is

This guide lists the factory values for AbCS preferences. A new install starts with these values, and **Restore Defaults** in the Preferences window (**Alt+R** on that screen) sets them again.

Use this guide to check that preferences reset correctly, or to see the starting values before you change settings.

## How to check defaults

1. Open **Manage → Preferences** from the menu bar.
2. Move through each tab to review the settings.
3. To return to these values, press **Restore Defaults** (**Alt+R**) and confirm with **Yes**. The values are saved right away.

Press **F1** in Preferences for that window's shortcuts. Press **Alt+/** to re-read the status bar.

## Display settings (first tab)

| Setting | Default |
|---------|---------|
| Theme | Default (follows system) |
| Zoom | 150%, shown as Custom |
| Google Books API key | Empty |
| Automatically check for updates | Unchecked |

## Import settings (second tab)

| Setting | Default |
|---------|---------|
| Default import directory | Empty |
| Audio formats | All checked: MP3, M4A, M4B, FLAC, OGG, WAV, WMA, AAC, OPUS |
| Import scenario | Mass Standard Import |
| Book title tag | Album |
| Author tag | Album artist then artist |

## Fallback & Auto Correct (third tab)

| Setting | Default |
|---------|---------|
| Author fallback to folder | Checked |
| Title fallback to file | Checked |
| Reader keywords | reader, read by, narrator, narrated by |

When the author or title is missing from the file tags, AbCS fills it from the folder or file name when these fallbacks are checked. When a fallback is unchecked, the field stays blank and validation reports an error.

### Auto correct defaults

Each option has a main checkbox, with an indented **Skip review** checkbox below it. Skip review is available when its main option is checked. By default every option and every Skip review is checked, so these corrections run without holding books for review.

| Option | Main (apply) | Skip review |
|--------|--------------|-------------|
| Apply proper case to title and author | Checked | Checked |
| Trim extra and leading/trailing whitespace | Checked | Checked |
| Remove leading punctuation from title and author | Checked | Checked |
| Remove non-printable control characters | Checked | Checked |

**Skip review** means a book corrected only by that option is still added automatically. See [Import preferences](18_import_preferences.md) for details.

## Validation rules (fourth tab)

| Rule | Default severity | Other default |
|------|------------------|---------------|
| Author in Title | Warning | — |
| Title in Author | Warning | — |
| Unknown / Various author | Warning | — |
| Minimum title length | Warning | Minimum 3 characters |
| Minimum book length | None (off) | Value 0 |
| Maximum book length | None (off) | Value 0 |
| File structure | Warning | Pattern Author/Title |
| Year consistency | Warning | Year after 1800 and not in the future |
| Duplicate match | — | Title + Author |
| Fuzzy duplicate | — | 90% |

Severity **None** turns the rule off. **Warning** and **Error** both hold the book for review. A book with an **Error** cannot be added with Add Selected until it is fixed.

## Fuzzy duplicate threshold

Fuzzy matching compares how similar the title and author text are, from 0 to 100%. **Both** the title and the author must meet the threshold to count as a duplicate.

| Value | Meaning |
|-------|---------|
| 0% | Fuzzy off: near-exact text only |
| 50% | Lenient: catches common shortenings and typos |
| 90% | Strict (the default): minor differences only |
| 100% | Nearly exact: mainly case differences |

Examples at 50%:

| Book in your library | Book being imported | Duplicate? | Why |
|----------------------|---------------------|------------|-----|
| The Moonstone / Wilkie Collins | Moonstone / Wilkie Collins | Yes | Title and author both pass |
| The Moonstone / Wilkie Collins | Moonstone / Lewis Carroll | No | Author fails |
| The Moonstone / Wilkie Collins | The Woman in White / Wilkie Collins | No | Title fails |

A higher percentage means stricter matching and fewer duplicate flags. A lower percentage means more duplicate flags.

At the default **90%**, only small typos and near-matches are flagged.

## Related help

- How each scenario uses these settings: [Import preferences](18_import_preferences.md)
- The Preferences window: [Preferences](10_preferences.md)
- Folder scan: [Import (Folder Scan)](02_import.md)
