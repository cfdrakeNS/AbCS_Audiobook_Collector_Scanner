# Standard Shortcuts (Tester Feedback) — Version 3 Phase 29

**Status:** Complete — Sept 27, 2026. Phase 16 help review is next.  
**Created:** September 27, 2026 (from tester feedback; first drafted in chat, saved here)  
**Related:** [accessibility_ui_standards.md](accessibility_ui_standards.md), [shortcut_centralization_status.md](shortcut_centralization_status.md), [shortcuts.py](../../src/accessibility/shortcuts.py), [help_docs/16_shortcuts.md](../../help_docs/16_shortcuts.md)  
**Source:** copied from `archive/doc/v3_enhancements/plan_standard_shortcuts.md` (Phase 29 plan) so the standard is tracked in git.

---

## Bug or enhancement

**Enhancement.** Current keys work as designed and are documented. This is a usability and consistency change. It changes muscle memory and help text, so it is a v3 phase **before Phase 16 help** (help must describe the final keys).

---

## Tester feedback

1. Book Details: Alt+E for **Edit**, not Update (rename Update to Edit). Then Reader becomes **Narrator** (Alt+N), Read date **Alt+R**, **Ctrl+S** Save, Series **Alt+S**.
2. Name list window: **Ctrl+F** Find instead of Alt+F, and **Ctrl+S** Save.
3. (No item 3 in the feedback list.)
4. Preferences window: Save with **Ctrl+S** (feedback said "Ctrl+"; assumed Ctrl+S).
5. Main window: remove **Import** from the toolbar.
6. Are there other shortcuts to look at?
7. (Added later) Do not like **Alt+Shift+P** for the player. Suggested Ctrl+P for Play, or **Ctrl+L** with the label changed to **Listen**.

---

## Design

### 1. Book Details — Edit instead of Update

"Update" collides in meaning with the main window **Update** window (bulk, Alt+U). "Edit" with **Alt+E** also matches Collection and Name list, which already use Alt+E for Edit. Keys are taken today in `BOOK_DETAILS_SHORTCUTS` and [book_details.py](../../src/ui/book_details.py), so a chain of moves is needed:

| Today | New |
|-------|-----|
| Alt+U Update | **Alt+E Edit** (button text Edit; no Alt+U alias) |
| Alt+E Read date | **Alt+R Read date** |
| Alt+R Reader | **Alt+N Narrator** (label Narrator) |
| Alt+N New book | **Ctrl+N** (same as main window New Book) |
| Alt+S Save | **Ctrl+S Save** |
| Alt+I Series | **Alt+S Series** (matches the Update window) |

Freed Alt letters (U, I) must be blocked by `ALLOWED_ALT_LETTERS` / `is_unmapped_alt_letter`.

### 2. Name list window — Ctrl+F and Ctrl+S

Alt+F (find) and Alt+S (Save) in `NAMELIST_WINDOW_SHORTCUTS` move to **Ctrl+F** and **Ctrl+S**. Ctrl+F focuses Find and selects its text. The existing rule that Ctrl chords stay on the list during find (Phase 13 fix) must keep Ctrl+C working; Ctrl+F and Ctrl+S are handled before that rule.

### 4. Preferences — Ctrl+S

Replace Alt+S in `PREFERENCES_WINDOW_SHORTCUTS` and the Save button description.

### 5. Main window — remove Import from the toolbar

Remove the `"import"` entry in the main toolbar setup ([main_window.py](../../src/ui/main_window.py)). Import stays on **File → Import** (Ctrl+I); Import Book List stays Ctrl+Shift+I.

### 6. Other shortcuts to align

- **Ctrl+S Save in every window with a Save button**: Collection (Alt+S today), Import Detail (Alt+S), Web Metadata (Alt+S). One rule: Save is always Ctrl+S.
- **Narrator** wherever Reader appears as a book field: Import Detail (`IMPORT_DETAIL_WINDOW_SHORTCUTS`). Book List Import is a column-mapping form where Alt+N is Series number, so the **Narrator** field mapping keeps **Alt+R** (not Alt+N).
- **Reading History**: Alt+R Refresh and Alt+S Search point at the same button — drop one.
- Leave main window Alt+U (Update window), Alt+D, Alt+W, Ctrl+F, Ctrl+N as they are.
- UI label "Reader" becomes **Narrator** in Book Details, Import Detail, and the Book List Import mapping form. Main book list has no Reader column. Database column `reader` and CSV export/import headers stay **Reader** for compatibility.

### 7. Listen (Ctrl+L) — implemented September 27, 2026

- The action that opens the player is **Listen**: main window **Edit → Listen** (Alt+E, L), toolbar **Listen**, Book Details **Listen** button, and the **Listen** window title.
- **Ctrl+L** opens Listen from the main window and Book Details. **Alt+Shift+P is removed** (no alias).
- Inside the Listen window, Ctrl+L does nothing. Space still plays or pauses; Alt+P / Alt+N previous and next file; the transport button stays **Play / Pause**.
- Accessible names and descriptions: "Listen to audiobook", "Listen to this book inside AbCS - Ctrl+L", "Listen position".
- Help topics 01, 04, 07, 08, 16, and 24 updated. Tests updated and added (main window action text and Ctrl+L; Book Details button and Ctrl+L; Listen window has no Ctrl+L binding and ignores it).
- Test safety fix found while doing this: UI tests copy `data/abcs.db`, which can hold real books. `test/conftest.py` now mutes all audio output in tests and stops a Listen window from waiting to be closed, so a test can never play a real audiobook or hang.

---

## Implementation (items 1–6)

| Area | Change |
|------|--------|
| [shortcuts.py](../../src/accessibility/shortcuts.py) | Update the maps above. `register_alt_shortcuts` only builds `Alt+` sequences, so add Ctrl keys as local `QShortcut(QKeySequence.Save)` / `QKeySequence.Find` in each window, like the existing local Alt+/ and F1 shortcuts. |
| [book_details.py](../../src/ui/book_details.py) | Button text Edit; local shortcuts; accessible descriptions ("Alt+U to edit" to "Alt+E to edit"); F1 list; labels Narrator / Read date with correct buddies. |
| [name_list_window.py](../../src/ui/name_list_window.py), [preferences_window.py](../../src/ui/preferences_window.py), [collection_window.py](../../src/ui/collection_window.py), [import_detail_window.py](../../src/ui/import_detail_window.py), [web_metadata.py](../../src/ui/web_metadata.py) | Ctrl+S (and Ctrl+F for name list); F1 lists; descriptions. |
| [book_list_import_window.py](../../src/ui/book_list_import_window.py) | **Narrator** label on the reader field mapping row; F1 / accessible names; Alt+R unchanged. |
| [main_window.py](../../src/ui/main_window.py) | Remove the Import toolbar action. |
| [reading_history_window.py](../../src/ui/reading_history_window.py) | Drop the duplicate Refresh/Search key. |
| Docs | `help_docs/16_shortcuts.md`, Book Details / Name list / Preferences / Import Detail help, README shortcut list, `AbCS_Shortcut_June07.csv`, AGENTS.md shortcut line (Alt+U/D note), release notes. |

**Estimate:** 1–2 days.

---

## Tests

- Update shortcut tests that assert Alt+U / Alt+S / Alt+R / Alt+E / Alt+N in Book Details, name list, Preferences, Collection, Import Detail.
- New checks: Ctrl+S saves in each window; Ctrl+F focuses name-list Find; Book Details Alt+E enters edit, Alt+N focuses Narrator, Alt+R focuses Read date, Alt+S focuses Series, Ctrl+N new book; toolbar has no Import action; freed Alt letters beep.
- Tests must not show or activate real windows (that turns on Qt accessibility for the rest of the run when JAWS or NVDA is running) and must not send key events through `QApplication.sendEvent` where a main-window shortcut could fire.
- Full `python -m pytest test/` green.

---

## Gate

Tester JAWS/NVDA check: each window's F1 list matches the real keys; Save is Ctrl+S everywhere; no Alt letter does two things in one window; focus and status announcements unchanged; Ctrl+L opens Listen from the main window and Book Details and does nothing inside Listen.

---

## Decisions (tester)

**Status: all answered Sept 27, 2026 — proceed with items 1–6.**

| # | Question | Answer |
|---|----------|--------|
| 1 | Item 4: is Preferences Save **Ctrl+S**? | **Yes** |
| 2 | Book Details New book moves from Alt+N to **Ctrl+N** — OK? | **Yes** |
| 3 | Extend Ctrl+S to Collection, Import Detail, and Web Metadata too, or only the windows testers named? | **Yes** — all windows with Save |
| 4 | Rename "Reader" to "Narrator" in the UI — Book Details and Import Detail only, or more? | **Yes** — Book Details, Import Detail, **and Book List Import** (mapping labels). Main book list column stays "Reader"; DB column and CSV headers unchanged. |
| 5 | Listen label and shortcut | **Listen** with **Ctrl+L**; Alt+Shift+P removed; Ctrl+L does nothing inside Listen (implemented Sept 27, 2026). |
