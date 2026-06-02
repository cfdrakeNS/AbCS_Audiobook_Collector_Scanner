# AbCS Visual Appeal — Remaining Work



Consolidated from:



- `abcs_visual_appeal_sighted_users.md`

- `visual-appeal-full-plan-3899a9.md`

- `visual-appeal-window-by-window-3899a9.md`



**Constraint (all items):** Improve sighted-user polish **without** weakening screen reader accessibility — visible button text, meaningful accessible names/descriptions, `Alt+/` status reread, no new conflicting `Alt+letter` shortcuts, strong focus indicators.



---



## Already done (do not re-implement)



| Area | Status |

|------|--------|

| **Shared helpers** (`src/accessibility/style_helpers.py`) | `build_modern_button_style`, `build_card_group_box_style`, `build_table_polish_style`, `build_toolbar_button_style`, `apply_tooltip_accessibility` (helper exists) |

| **Action icons** (`src/accessibility/icon_helper.py`) | `get_action_icon`, `apply_decorative_action_icon` — Qt standard pixmaps; text stays visible; names unchanged |

| **Preferences** | Card-style group boxes, modern buttons, primary Save, broad tooltip map, status bar styling, browse/restore/save icons |

| **Import window** | Modern buttons, primary Scan / Add Selected, table polish, core tooltips, browse/import/add/export icons |

| **Main window** | Labeled action toolbar (Add, Import, Find, Search Web, Statistics, Preferences, Help) with icons, modern footer buttons, table polish, partial tooltips, layout margins, footer action icons |

| **Secondary windows (steps 5–8)** | Book details, book list import, update/import detail/reading history, collection/name list/backup-restore/statistics, web metadata — modern buttons, table polish, icons where applicable |

| **Book details / book list import** | Decorative icons; book details primary Save / destructive Delete; book list import card group boxes + primary Import |

| **Shortcut hygiene** | Reading History uses `Alt+L` for table focus (not `Alt+B`) |

| **Tooltip + description pass** | `apply_visual_tooltip_map()` / `apply_tooltip_accessibility()` across Preferences, Import, Main (menus/toolbar/filters), Book details, Book list import, Update, Import detail, Reading history, Backup/restore, Name list, Collection, Web metadata, Statistics |



---



## Remaining work

All implementation steps (1–8) are complete. Optional polish and commit are below.

## Completed rollout (reference)



### 1. ~~Tooltip + accessible-description pass~~ (done)



Implemented via `apply_visual_tooltip_map()` in `style_helpers.py` and per-window `apply_visual_tooltips()` (or inline for Statistics). Main window also sets tooltips/descriptions on View/Sort/Collections/Read menu actions and toolbar `QAction`s.



**Tooltip rules:** Short, action-focused, visual help only; screen readers rely on name + description.



---



### 2. ~~Main window layout polish~~ (done)



| Item | Status |

|------|--------|

| **Filter/sort summary panel** | Done — header card shows collection, read, find, sort, book count (and duplicate mode) |

| **Footer card** | Done — sort label + Update/Delete/Export in `footerActionPanel` |

| **Button hierarchy** | Done — Delete = destructive; Update or Export = primary when visible |

| **Toolbar: Find** | Done — Find button uses `on_find`, Ctrl+F unchanged |

| **Toolbar icons** | Done — see item 3 |



---



### 3. ~~Decorative icons on major buttons~~ (done)



| Item | Status |

|------|--------|

| **Icon source** | Done — `icon_helper.py` uses Qt `QStyle.StandardPixmap` (no new deps) |

| **Targets** | Done for Import, Main toolbar + footer, Preferences, Book details, Book list import |

| **A11y** | Icons decorative; accessible names unchanged |

| **Still optional** | Minor panel/card polish on book list import preview; optional header cards on book details |



---



### 4. Secondary windows — shared styling (window-by-window gates)



Apply modern buttons, table polish, and light tooltips only where keyboard/combo behavior is unchanged. Test each window before the next.



| Step | File(s) | Remaining |

|------|---------|-----------|

| 5 | `book_details.py` | ~~Primary/destructive button roles; icons~~ — optional header card if needed later |

| 6 | `book_list_import_window.py` | ~~Card group boxes, modern buttons, primary Import, icons~~ — preview polish optional |

| 7 | `update_window.py`, `import_detail_window.py`, `reading_history_window.py` | ~~Modern buttons/table polish, status bar, scale/theme hooks, icons on Import detail + Reading History Search~~ |

| 8 | `collection_window.py`, `name_list_window.py`, `backup_restore_window.py`, `statistics_dialog.py` | ~~Modern buttons, table polish, status bar, icons, scale/theme hooks~~ |

| — | `web_metadata.py` | ~~Modern Save button, status bar, save icon, scale/theme hooks~~ (tooltips already present) |



**Optional (defer):** Import window single-row action toolbar; Preferences mini-toolbar for Save/Restore/Close — only if main toolbar pattern tests well.



---



### 5. ~~Theme review~~ (done — no new themes)

| Item | Status |

|------|--------|

| **Do not duplicate themes** | Confirmed — `ThemeManager` presets cover the visual plan |

| **Modern / Classic Accessible** | **Not added** — palette-based `style_helpers` already track active theme; existing Default + High Contrast + custom themes are sufficient |

| **Regression test** | **Manual:** switch themes in Preferences and spot-check Main, Import, Preferences (buttons, cards, tables, toolbar, focus rings) |



---



### 6. ~~Final verification~~ (automated done; manual spot-checks remain)

**Automated (2026-06-02)**

| Check | Result |
|-------|--------|
| `py_compile` — `src/accessibility/*.py`, all `src/ui/*.py` | Pass |
| `pytest` — `test_accessibility.py`, `test_accessibility_regression.py`, `test_reading_history_accessibility.py`, `test_main_window_shortcuts_and_menus.py` | 30 passed |
| Icon-only buttons | None introduced (`ToolButtonTextBesideIcon` / text+icon on actions) |
| Styles use `palette(...)` | Confirmed in `style_helpers.py` |

**Manual (before commit)**

- [ ] `Alt+/` status reread: Main, Import, Preferences, one secondary window
- [ ] Default + High Contrast Dark/Light: focus rings on toolbar, footer, Import header
- [ ] NVDA/JAWS: Main toolbar + table; Import header/footer; Preferences sample controls
- [ ] Zoom 100% and enlarged: cards, table selection, toolbar at narrower width
- [ ] F1 shortcuts still open on touched windows

**Checkpoint**

- Commit when manual checklist above is satisfied (per window-by-window plan)



---



## Quick reference: implementation principles



1. **Tooltips + cards + buttons** before icons; icons before optional extra toolbars.

2. **Palette-based** styles only (`palette(...)`) so themes and high contrast stay safe.

3. **Three-layer metadata** on important controls: visible label, short tooltip, accessible name (+ description when needed).

4. **Defect vs noise:** Missing required info for SR users = defect; quieter visuals OK if access stays explicit (`doc/PySide6_Accessibility_Patterns_and_Implementation_Reference.md` §10).



---



## Source documents



| Document | Role |

|----------|------|

| `abcs_visual_appeal_sighted_users.md` | Goals, phases 1–4, tooltip examples |

| `visual-appeal-full-plan-3899a9.md` | Phased rollout + verification checklist |

| `visual-appeal-window-by-window-3899a9.md` | Per-window steps and test gates |



Accessibility principles (unchanged by visual work): `doc/PySide6_Screen_Reader_Accessibility_Best_Practices.md`, `doc/PySide6_Accessibility_Patterns_and_Implementation_Reference.md`.

