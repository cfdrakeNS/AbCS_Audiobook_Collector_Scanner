# Default Preferences

## What this is

This document lists the **recommended default values** for AbCS preferences. They match what **Restore Defaults** sets in the Preferences window (**Alt+R** on that screen).

Use this guide when testing that preferences reset correctly, or when you need to know what AbCS expects before you change settings.

## How to check defaults

1. Open **Manage → Preferences**.
2. Review each tab, or press **Restore Defaults** (Alt+R) and confirm with **Yes**.
3. Press **Save** (Alt+S) if you want to keep the restored values.

Press **F1** in Preferences for that window's shortcuts. Press **Alt+/** to re-read the status bar.

**Note for testers:** On a very first run (before any save), a few validation fields may differ until you use **Restore Defaults** — for example, duplicate match mode may show **Title + Author + Year + Collection** and fuzzy duplicate may show **0%**. **Restore Defaults** is the authoritative reset for the values below.

## Display settings (first tab)

| Setting | Default |
|---------|---------|
| Theme | Default (follows system) |
| Zoom | 150% (Extra Large preset; shown as Custom at 150%) |

## Import settings (second tab)

| Setting | Default |
|---------|---------|
| Default import directory | Empty |
| Audio formats | All checked: MP3, M4A, M4B, FLAC, OGG, WAV, WMA |
| Import scenario | Mass Standard Import |
| Include subfolders | On (always enabled when settings are saved) |

## Fallback and parsing (third tab)

| Setting | Default |
|---------|---------|
| Author fallback to folder | Checked |
| Title fallback to file | Checked |
| Reader keywords | `reader, read by, narrator, narrated by` |

When author or title is missing from file tags, AbCS can fill them from folder or file names only if these fallbacks are enabled.

## Validation rules (fourth tab)

| Rule | Default severity | Other default |
|------|------------------|---------------|
| Author in Title | Warning | Enabled |
| Title in Author | **Error** | Enabled |
| Unknown / Various author | Warning | Enabled |
| Minimum title length | Warning | Enabled, minimum **3** characters |
| Minimum book length | None (off) | Value 0 |
| Maximum book length | None (off) | Value 0 |
| File structure | Warning | Enabled, pattern **Author/Title** |
| Year consistency | Warning | Enabled; year must be after 1800 and not in the future |
| Duplicate match | Title + Author + Year | — |
| Fuzzy duplicate % | **90%** | — |

Severity **None** means the rule is turned off. **Warning** reports an issue but does not block import the same way as **Error**.

## Fuzzy duplicate threshold

Fuzzy matching compares title and author text similarity (0–100%). **Both** title and author must meet the threshold to count as a duplicate.

| Value | Meaning |
|-------|---------|
| **0%** | Fuzzy off — near-exact text match only |
| **50%** | Lenient — catches common shortenings and typos |
| **90%** | Strict (default after Restore Defaults) — minor differences only |
| **100%** | Nearly exact — mainly case differences |

**Examples at 50%:**

| Database book | Import book | Duplicate? | Why |
|---------------|-------------|------------|-----|
| The Hobbit / Tolkien | Hobbit / Tolkien | Yes | Title and author both pass |
| The Hobbit / Tolkien | Hobbit / Rowling | No | Author fails |
| The Hobbit / Tolkien | Lord of the Rings / Tolkien | No | Title fails |

Higher percentage = stricter matching and fewer duplicate flags. Lower percentage = more duplicate flags.

At the default **90%**, only small typos and near-matches are flagged; completely different titles will not match.

## Related documentation

- [Import preferences (scenario detail)](15_import_preferences.md) — how each import scenario uses these settings
- [Import process](02_import_process.md) — tester workflow for folder import
