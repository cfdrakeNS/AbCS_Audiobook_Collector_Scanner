# AGENTS.md — AbCS Project AI Agent Instructions

This file provides essential guidance for AI coding agents working on the AbCS (Audiobook Collector Scanner) project. It summarizes project-specific conventions, accessibility requirements, and key references to ensure productive, accessible, and consistent contributions.

---
## user uses screen readers both JAWS and NVDA 
## don't put large blocks of code in the response panel 
##  Format: Factual summaries only (What changed / What will change).
## NEVER use question cards / multiple-choice pickers (the AskQuestion tool). They are not readable with JAWS. Ask clarifying questions as plain numbered text in the chat response and wait for a typed reply.

## 1. Project Overview
- **Purpose:** Cross-platform audiobook collection manager with full accessibility support (JAWS, NVDA, Narrator, Orca).
- **Tech:** Python 3.9+, PySide6, SQLite, custom accessibility patterns.
- **Key Folders:**
  - `src/` — Main source code
  - `src/ui/` — All user interface windows/dialogs
  - `src/accessibility/` — Accessibility helpers, patterns, and event logic

## 2. Build & Test
- **Run app:** `python src/main.py`
- **Install deps:** `pip install -r requirements.txt`
- **Run tests:** `python -m pytest test/`
- **Do NOT run the full test suite unless the user asks.** The user runs it. At most, run only the specific test file(s) you added or changed.

## 3. Accessibility Protocols (MANDATORY)
- **Screen Reader Protocol:**
  - All major windows/dialogs must support `Alt+/` to re-read the current status message.
  - Use `set_status(..., announce=True)` for meaningful state changes; avoid noise on passive updates.
  - Block unmapped `Alt+letter` keys in text fields (see `is_unmapped_alt_letter`).
  - Block plain Up/Down in editable combos; allow only with `Alt` (see combo anti-noise pattern).
  - Always set accessible names/descriptions for controls and dialogs.
  - Restore focus intentionally after dialogs/operations.
- **Reference docs (external sample repo):**
  - [PySide6_Accessibility_Patterns_and_Implementation_Reference.md](https://github.com/cfdrakeNS/pyside6-accessible-ui-reference/blob/main/doc/PySide6_Accessibility_Patterns_and_Implementation_Reference.md)
  - [PySide6_Screen_Reader_Accessibility_Best_Practices.md](https://github.com/cfdrakeNS/pyside6-accessible-ui-reference/blob/main/doc/PySide6_Screen_Reader_Accessibility_Best_Practices.md)
  - Runnable sample: clone [pyside6-accessible-ui-reference](https://github.com/cfdrakeNS/pyside6-accessible-ui-reference) and run `python main.py`

## 4. Keyboard Shortcuts
- **F1:** Show help/shortcuts
- **Shift+F1:** Context-sensitive process help (see `help_router.py`)
- **Alt+/**: Read status
- **Escape:** Cancel/close
- **Alt+U/D:** Update/Delete selected
- **See:** [README.md](README.md) for full shortcut list

## 4a. App Standards (MANDATORY — read before changing any window)
The app's standards live in `doc/standards/` (tracked in git). Read the relevant one before editing UI, shortcuts, F1, or status code:
- [doc/standards/accessibility_ui_standards.md](doc/standards/accessibility_ui_standards.md): master checklist for windows, dialogs, buttons, combos, status, focus, and the per-change JAWS gate.
- [doc/standards/standard_shortcuts.md](doc/standards/standard_shortcuts.md) (Phase 29): current key standard (Save is always Ctrl+S, Edit Alt+E, New Ctrl+N, Find Ctrl+F, Listen Ctrl+L, Narrator label).
- [doc/standards/shortcut_centralization_status.md](doc/standards/shortcut_centralization_status.md): what is centralized and what is intentionally local.
- [doc/standards/shortcut_normalization_plan.md](doc/standards/shortcut_normalization_plan.md): older normalization rules; Phase 29 overrides it where they differ.
- Originals stay in the gitignored `archive/` folder. When a standard changes, update the `doc/standards/` copy.

**Shortcut and F1 rules (do not deviate):**
- Alt+letter keys only go in the window's map in `src/accessibility/shortcuts.py` and register through `ShortcutManager.register_alt_shortcuts`.
- Ctrl keys (Ctrl+N, Ctrl+S, Ctrl+F, Ctrl+L) are local `QShortcut`s in each window. Do not add them to the central maps.
- F1, Escape, and Alt+/ stay local `QShortcut`s in every window, on purpose, for screen reader reliability. Do not move them into the maps.
- Do not change `register_alt_shortcuts`, and do not add new shortcut or F1 helpers or registries.
- F1 popup: each window passes its own explicit list to `exec_f1_shortcuts_dialog`. Shift+F1 is prepended automatically. When keys change, edit that list, the window's help topic, and `help_docs/16_shortcuts.md`.
- No Alt letter does two things in one window. Freed Alt letters must beep (`is_unmapped_alt_letter`).

**What "centralized" means here:** use the existing shared helpers. These are the Alt-letter maps, `exec_f1_shortcuts_dialog`, `read_status_bar_message`, `announce_status_message`, `install_shift_f1_help`, and the style helpers. It does NOT mean moving every key into one map or building a new mechanism.

**Change discipline:**
- If something already works and meets the standards, do not rewrite it. Fix only the reported defect.
- Never create a new handler, helper, or framework when an existing one does the job.
- If a request could mean "replace the existing mechanism", ask in plain numbered text first.
- Match existing look and behavior: copy the closest existing window (for example, name list tables for row height and padding) instead of inventing styles.

## 5. Implementation Patterns
- **Status bar:** Use `announce_status_message` (see `src/accessibility/accessible_events.py`).
- **Combo anti-noise:** See `eventFilter` in `src/ui/book_details.py`, `src/ui/update_window.py`, `src/ui/preferences_window.py`.
- **Alt-key hygiene:** See `is_unmapped_alt_letter` in `src/accessibility/key_filters.py`.
- **Help dialogs:** Use simple, accessible lists/tables for shortcut help.
- **Help topics:** Add `help_docs/nn_topic_name.md` files (discovered at runtime). Update `src/ui/help_router.py` `WINDOW_HELP_MAP` only for Shift+F1 per-window routing. Authoring rules: [doc/help_docs_authoring.md](doc/help_docs_authoring.md). See also `src/accessibility/help_paths.py` and `src/ui/help_window.py` module docstrings.
- **Focus safety:** Deselect text on FocusIn for line edits/combo edits.

## 6. Common Pitfalls
- Do NOT rely on `QStatusBar.showMessage()` alone for announcements.
- Do NOT add global Enter/Return shortcuts that override button activation.
- Do NOT leave controls without accessible names/descriptions.
- Do NOT break tab order or focus flow after operations.

## 7. Further Reading
- [README.md](README.md): Project intro, features, structure, and shortcuts
- [help_docs/01_overview.md](help_docs/01_overview.md): User workflow guides
- [TESTING.md](TESTING.md): Automated test guide
- [PySide6_Accessibility_Patterns_and_Implementation_Reference.md](https://github.com/cfdrakeNS/pyside6-accessible-ui-reference/blob/main/doc/PySide6_Accessibility_Patterns_and_Implementation_Reference.md): Code patterns
- [PySide6_Screen_Reader_Accessibility_Best_Practices.md](https://github.com/cfdrakeNS/pyside6-accessible-ui-reference/blob/main/doc/PySide6_Screen_Reader_Accessibility_Best_Practices.md): Design principles

---

**Edit this file to update agent instructions as project conventions evolve.**
