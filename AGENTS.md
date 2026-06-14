# AGENTS.md — AbCS Project AI Agent Instructions

This file provides essential guidance for AI coding agents working on the AbCS (Audio Book Collector Scanner) project. It summarizes project-specific conventions, accessibility requirements, and key references to ensure productive, accessible, and consistent contributions.

---
## user uses screen readers both JAWS and NVDA 
## don't put large blocks of code in the response panel 
##  Format: Factual summaries only (What changed / What will change).

## 1. Project Overview
- **Purpose:** Cross-platform audiobook collection manager with full accessibility support (JAWS/NVDA/VoiceOver).
- **Tech:** Python 3.9+, PySide6, SQLite, custom accessibility patterns.
- **Key Folders:**
  - `src/` — Main source code
  - `src/ui/` — All user interface windows/dialogs
  - `src/accessibility/` — Accessibility helpers, patterns, and event logic
  - `doc/` — Documentation (see below)

## 2. Build & Test
- **Run app:** `python src/main.py`
- **Install deps:** `pip install -r requirements.txt`
- **Run tests:** `python -m pytest test/`

## 3. Accessibility Protocols (MANDATORY)
- **Screen Reader Protocol:**
  - All major windows/dialogs must support `Alt+/` to re-read the current status message.
  - Use `set_status(..., announce=True)` for meaningful state changes; avoid noise on passive updates.
  - Block unmapped `Alt+letter` keys in text fields (see `is_unmapped_alt_letter`).
  - Block plain Up/Down in editable combos; allow only with `Alt` (see combo anti-noise pattern).
  - Always set accessible names/descriptions for controls and dialogs.
  - Restore focus intentionally after dialogs/operations.
- **Reference docs:**
  - [PySide6_Accessibility_Patterns_and_Implementation_Reference.md](doc/PySide6_Accessibility_Patterns_and_Implementation_Reference.md)
  - [PySide6_Screen_Reader_Accessibility_Best_Practices.md](doc/PySide6_Screen_Reader_Accessibility_Best_Practices.md)

## 4. Keyboard Shortcuts
- **F1:** Show help/shortcuts
- **Alt+/**: Read status
- **Escape:** Cancel/close
- **Alt+U/D:** Update/Delete selected
- **See:** [README.md](README.md) for full shortcut list

## 5. Implementation Patterns
- **Status bar:** Use `announce_status_message` (see `src/accessibility/accessible_events.py`).
- **Combo anti-noise:** See `eventFilter` in `src/ui/book_details.py`, `src/ui/update_window.py`, `src/ui/preferences_window.py`.
- **Alt-key hygiene:** See `is_unmapped_alt_letter` in `src/accessibility/key_filters.py`.
- **Help dialogs:** Use simple, accessible lists/tables for shortcut help.
- **Focus safety:** Deselect text on FocusIn for line edits/combo edits.

## 6. Common Pitfalls
- Do NOT rely on `QStatusBar.showMessage()` alone for announcements.
- Do NOT add global Enter/Return shortcuts that override button activation.
- Do NOT leave controls without accessible names/descriptions.
- Do NOT break tab order or focus flow after operations.

## 7. Further Reading
- [README.md](README.md): Project intro, features, structure, and shortcuts
- [doc/01_user_index.md](doc/01_user_index.md): User workflow guides
- [TESTING.md](TESTING.md): Automated test guide
- [doc/PySide6_Accessibility_Patterns_and_Implementation_Reference.md](doc/PySide6_Accessibility_Patterns_and_Implementation_Reference.md): Code patterns
- [doc/PySide6_Screen_Reader_Accessibility_Best_Practices.md](doc/PySide6_Screen_Reader_Accessibility_Best_Practices.md): Design principles

---

**Edit this file to update agent instructions as project conventions evolve.**
