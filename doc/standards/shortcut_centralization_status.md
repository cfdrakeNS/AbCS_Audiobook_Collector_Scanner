# AbCS Shortcut Centralization Status (March 2026)

**Source:** copied from `archive/acessibility/AbCS_Shortcut_Centralization_Status.md` so the standard is tracked in git. Phase 29 ([standard_shortcuts.md](standard_shortcuts.md)) later moved Save to Ctrl+S and New to Ctrl+N; those Ctrl keys are local `QShortcut`s in each window, like F1, Escape, and Alt+/.

## Overview
This document tracks the status of Alt+letter shortcut centralization in the AbCS application, focusing on accessibility, consistency, and screen reader reliability. Centralization means all Alt+letter shortcuts are registered via the ShortcutManager and ShortcutContext, not via local QShortcut or setShortcut calls.

## Centralization Principles
- **Centralized:** All Alt+letter shortcuts for fields and actions are registered via ShortcutManager for each window context.
- **Intentionally Local:** F1 (help), Escape, and Alt+/ (status bar read) remain local QShortcuts for accessibility/screen reader reliability.
- **Goal:** All main windows and dialogs use centralized shortcuts for actions and navigation, except where local handling is required for accessibility.

---

## Centralization Status by Window

### Fully Centralized (All Alt+letter via ShortcutManager)
- **MainWindow**
- **ImportWindow**
- **BookDetailsWindow**
- **PreferencesWindow**
- **UpdateWindow**
- **BackupRestoreWindow**
- **CollectionWindow**
  - All Alt+N, Alt+E, Alt+S, Alt+L, Alt+D, Alt+B, Alt+A are centralized.


### Intentionally Local (For Accessibility)
- **All Windows:**
  - F1 (Help)
  - Escape (Close/Cancel)
  - Alt+/ (Status bar read)
  - These remain local QShortcuts for screen reader reliability and are not centralized.

---

## Recommendations
- **Centralize** remaining Alt+letter shortcuts in BookDetailsWindow, ImportDetailWindow, ImportProgressWindow, and ImportWindow for consistency, unless local handling is required for accessibility.
- **Document** any exceptions in this file, with rationale (e.g., "kept local for JAWS/NVDA reliability").
- **Test** all shortcuts with JAWS/NVDA after centralization.

---

## Summary Table
| Window                | Centralized Alt+Letter | Local Alt+Letter | Local (F1/Esc/Alt+/) | Notes |
|-----------------------|:---------------------:|:----------------:|:--------------------:|-------|
| MainWindow            | Yes                   | No               | Yes                  |       |
| ImportWindow          | Yes                   | No               | Yes                  |       |
| BookDetailsWindow     | Yes                   | No               | Yes                  |       |
| PreferencesWindow     | Yes                   | No               | Yes                  |       |
| UpdateWindow          | Yes                   | No               | Yes                  |       |
| BackupRestoreWindow   | Yes                   | No               | Yes                  |       |
| CollectionWindow      | Yes                   | No               | Yes                  |       |
| ImportDetailWindow    | Most                  | Alt+S/D          | Yes                  |       |
| ImportProgressWindow  | Most                  | Alt+L            | Yes                  |       |

---

## Last Updated: March 13, 2026
