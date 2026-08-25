# Help Docs — Authoring Guide

How to create and update in-app help topics in `help_docs/`. End users read these through **Help → Help...**; authors maintain them as markdown files in the repository.

For a short summary, see [README.md](../README.md#adding-or-changing-help-topics-dynamic-topics). Implementation lives in `src/ui/help_window.py` (markdown conversion) and `src/accessibility/help_paths.py` (discovery).

---

## File naming standard

Every help topic is one markdown file in `help_docs/`:

```text
nn_topic_name.md
```

| Part | Rule | Example |
|------|------|---------|
| `nn` | Two digits — sort order in **All Help Topics** | `02`, `19` |
| `topic_name` | Lowercase words, underscores only | `import_book_list` |
| Extension | Always `.md` | |

**Valid examples**

- `01_overview.md` → appears as **overview**
- `11_import_book_list.md` → **import book list**
- `19_import_explained.md` → **import explained**

**Invalid examples**

- `import.md` — missing numeric prefix (ignored by discovery)
- `2_import.md` — must be two digits
- `02 Import.md` — no spaces in filename
- `02_Import.md` — use lowercase topic slug

The regex used at runtime is `^\d{2}_[\w-]+\.md$` (see `help_paths.HELP_DOC_FILENAME_RE`).

### Suggested number ranges

| Range | Purpose |
|-------|---------|
| `01` | Help overview / hub |
| `02`–`15` | Process guides (one workflow per window) |
| `16`–`18` | Reference (shortcuts, defaults, import preferences) |
| `19`–`22` | Explained guides (everyday-language walkthroughs) |
| `22+` | Next free numbers for new topics |

Use the **next free** `nn` when adding a file. Do not renumber existing files unless you are deliberately reordering the whole library.

---

## How topics appear in the app

1. **All Help Topics** — `discover_help_topics()` scans `help_docs/*.md` matching the naming pattern. **No code change** is required for a new file to show up here.
2. **Section list** — After opening a topic, the left list shows `##` and `###` headings from that file (plus **All Help Topics** to go back).
3. **Shift+F1** — Opens a **fixed** file per window class via `WINDOW_HELP_MAP` in `src/ui/help_router.py`. Add a map entry when a **new window** needs its own default help doc.
4. **F1** — Keyboard shortcut tables built in code per window; not loaded from these markdown files.

### Window and file number reference

The two-digit prefix (`nn`) is the stable ID for each topic. **Renaming** `02_import.md` to `02_folder_scan.md` is safe for **All Help Topics** (discovery uses the pattern), but you must update **`WINDOW_HELP_MAP`** and any **cross-links** that use the old filename.

#### Shift+F1 — window class to help file

| `nn` | Help file | Window class (`__name__`) | Notes |
|------|-----------|---------------------------|-------|
| 01 | `01_overview.md` | *(none)* | **Help → Help...** menu; fallback when no map entry |
| 02 | `02_import.md` | `ImportWindow` | Folder scan import |
| 02 | `02_import.md` | `ImportProgressWindow` | Same doc as Import |
| 03 | `03_find_filters.md` | `MainWindow` | Main book list (normal mode) |
| 08 | `08_duplicate_mode.md` | `MainWindow` | When duplicate mode is active (overrides `03`) |
| 04 | `04_book_details.md` | `BookDetailsWindow` | New / edit one book |
| 05 | `05_update.md` | `UpdateWindow` | Bulk update selected books |
| 06 | `06_collections.md` | `CollectionWindow` | Collections manager |
| 07 | `07_web_metadata.md` | `WebMetadataWindow` | Fetch web info |
| 09 | `09_backup_restore.md` | `BackupRestoreWindow` | Backup / restore / reset |
| 10 | `10_preferences.md` | `PreferencesWindow` | App preferences |
| 11 | `11_import_book_list.md` | `BookListImportWindow` | Spreadsheet import |
| 12 | `12_import_detail.md` | `ImportDetailWindow` | Import review — one held item |
| 13 | `13_reading_history.md` | `ReadingHistoryWindow` | Reading history |
| 14 | `14_statistics.md` | `StatisticsDialog` | Library statistics |
| 15 | `15_name_list.md` | `NameListWindow` | Author / series / genre lists |

When adding a window: pick the next free process-guide number (`02`–`15`), create `nn_topic.md`, add `ClassName → nn_topic.md` to `WINDOW_HELP_MAP`.

#### All numbered help files

| `nn` | File | Type | Shift+F1 window |
|------|------|------|-----------------|
| 01 | `01_overview.md` | Hub | Menu only |
| 02 | `02_import.md` | Process | Import, Import progress |
| 03 | `03_find_filters.md` | Process | Main window |
| 04 | `04_book_details.md` | Process | Book Details |
| 05 | `05_update.md` | Process | Update |
| 06 | `06_collections.md` | Process | Collections |
| 07 | `07_web_metadata.md` | Process | Web metadata |
| 08 | `08_duplicate_mode.md` | Process | Main window (duplicate mode) |
| 09 | `09_backup_restore.md` | Process | Backup / restore |
| 10 | `10_preferences.md` | Process | Preferences |
| 11 | `11_import_book_list.md` | Process | Import book list |
| 12 | `12_import_detail.md` | Process | Import detail |
| 13 | `13_reading_history.md` | Process | Reading history |
| 14 | `14_statistics.md` | Process | Statistics |
| 15 | `15_name_list.md` | Process | Name list |
| 16 | `16_shortcuts.md` | Reference | — |
| 17 | `17_default_preferences.md` | Reference | — |
| 18 | `18_import_preferences.md` | Reference | — |
| 19 | `19_import_explained.md` | Explained | — |
| 20 | `20_import_book_list_explained.md` | Explained | — |
| 21 | `21_web_metadata_explained.md` | Explained | — |
| 22 | `22_web_metadata_title_compare.md` | Explained | — |

Reference and explained guides (`16`–`22`) appear in **All Help Topics** only unless linked from another topic or the overview tables in `01_overview.md`.

### Cross-links between topics

Link with the **filename only** (no folder path):

```markdown
See [Import](02_import.md) for folder scan steps.
See [Import explained](19_import_explained.md) for a plain walkthrough.
```

Links to `.md` files are collected for navigation; link text is what screen readers hear when the label is read aloud.

### Packaging

Windows and Linux builds bundle `help_docs/` into the installer. Add or edit markdown in the repo, then **rebuild** so testers receive updated help.

---

## Document structure

### Required

1. **One `#` heading** at the top — becomes the help window title when the topic is open.
2. **`##` sections** for major parts (What this is, Steps, Common confusion, and so on).
3. **`###` subsections** when a section needs smaller jumps (optional).

### Recommended sections (process guides)

Process guides (`02`–`15`) usually include:

- **What this is** / **When to use it**
- **Before you start**
- **Steps** (numbered list)
- **What happens next**
- **Settings that affect this** (if any)
- **Mouse, shortcuts, and accessibility** — shortcut table plus mouse tips
- **Common confusion** — FAQ-style Q&A

Explained guides (`19`–`21`) use narrative sections instead of full shortcut tables; link to the matching process guide for Alt+key detail.

Reference guides (`16`–`18`) may be table-heavy; keep prose short.

---

## Markdown styles allowed

AbCS uses a **small custom subset** of markdown tuned for screen readers (JAWS/NVDA). The converter is `markdown_to_html()` in `src/ui/help_window.py` — not a full CommonMark engine.

### Supported

| Style | Syntax | Notes |
|-------|--------|-------|
| **Title** | `# Heading` | One per file; window title |
| **Section** | `## Heading` | Appears in section navigation |
| **Subsection** | `### Heading` | Appears in section navigation |
| **Bold** | `**text**` | Only inline emphasis supported |
| **Bullet list** | `- item` | Unordered list |
| **Numbered steps** | `1. step` | Renumbered from 1 after each `##`/`###` heading |
| **Shortcut table** | See below | Renders as `Shortcut — Action` lines |
| **Generic table** | Pipe table | Renders as `cell — cell — cell` lines |
| **FAQ question** | `**Question text?**` on its own line | Next line(s) = answer |
| **Link** | `[label](02_import.md)` | Target must be `*.md` filename |

**Shortcut table** (preferred for keyboard sections):

```markdown
| Shortcut | Action |
|----------|--------|
| Ctrl+I | Open Import |
| Alt+/ | Re-read status |
```

The header row must be exactly `Shortcut` and `Action` (case-insensitive) for shortcut styling.

**FAQ block** (for Common confusion):

```markdown
**Why were some books held for review?**
Clean books are added immediately. Others wait until you confirm.
```

The question line must be **only** bold text on that line (whole line wrapped in `**...**`).

**Bold in prose:**

```markdown
Press **Escape** to close without saving.
```

### Not supported

Do **not** use these — they will appear as plain text or break layout:

| Not supported | Instead |
|---------------|---------|
| `*italic*` | Use plain text or **bold** sparingly |
| `` `code` `` or fenced code blocks | Describe keys in prose: **Alt+I** |
| HTML tags (`<b>`, `<br>`, etc.) | Use markdown constructs above |
| Images `![alt](file.png)` | Describe in text only |
| `####` and deeper headings | Use `###` at most |
| Horizontal rules `---` | Use a `##` heading |
| Block quotes `>` | Normal paragraphs |
| Nested bullet lists | Flatten to one level |
| Real HTML tables | Use pipe tables (rendered as lines) |

---

## Accessibility writing rules

The help viewer splits **body paragraphs** into **one sentence per paragraph** so screen readers can move line by line without repeated wrapped-line noise.

1. **Prefer short sentences.** Two ideas → two sentences.
2. **Avoid empty lines inside FAQ answers** that could split meaning oddly; one blank line between blocks is fine.
3. **Put shortcuts in tables** or inline as **Alt+letter** — spell out **Ctrl**, **Shift**, **Escape**.
4. **Do not rely on visual layout** (columns, alignment). Tables become linear `A — B` lines.
5. **Numbered steps** under a heading always restart at 1 when the heading changes — do not depend on continuing `3.` `4.` across sections.
6. **Link labels** should make sense alone: `[Import preferences](18_import_preferences.md)` not `[click here](18_import_preferences.md)`.

---

## Checklist — adding a new topic

1. Pick the next free `nn` and a `topic_name` slug.
2. Create `help_docs/nn_topic_name.md` with `#` title and `##` sections.
3. Cross-link related topics using `[label](filename.md)`.
4. If a **new window** needs Shift+F1, add `ClassName → nn_topic.md` to `WINDOW_HELP_MAP` in `src/ui/help_router.py` (see **Window and file number reference** above).
5. Optionally add a row to [01_overview.md](../help_docs/01_overview.md) process or explained tables.
6. Run tests: `python -m pytest test/test_help_router.py -v`
7. Open **Help → Help... → All Help Topics** and confirm the new name and sections.
8. Rebuild installers if shipping to testers.

---

## Checklist — updating an existing topic

1. Edit the markdown file only; topic list updates automatically.
2. Keep the `#` title accurate — it is the window title.
3. If you rename a file, update **all** cross-links in other `help_docs/` files.
4. If you rename a file used by Shift+F1, update `WINDOW_HELP_MAP` and the **Window and file number reference** table in this guide if the number assignment changes.
5. Run `test/test_help_router.py` after structural changes (tables, FAQ blocks, new links).

---

## Tests and reference code

| File | Role |
|------|------|
| `test/test_help_router.py` | Discovery, display names, markdown conversion |
| `src/accessibility/help_paths.py` | Filename rules, `discover_help_topics()` |
| `src/ui/help_window.py` | `markdown_to_html()`, Help UI |
| `src/ui/help_router.py` | Shift+F1 routing |

Example markdown patterns tested in `test_markdown_to_html_*` — copy those tests when unsure if a construct will render correctly.

---

## Related user-facing docs

| Doc | Audience |
|-----|------------|
| [help_docs/01_overview.md](../help_docs/01_overview.md) | End users — help system overview |
| [README.md](../README.md) | Developers — quick add-topic summary |
