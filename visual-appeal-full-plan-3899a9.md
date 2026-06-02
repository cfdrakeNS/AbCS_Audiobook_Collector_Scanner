# Visual Appeal Completion Plan

Implement the full sighted-user visual appeal plan in phases while preserving all existing screen reader behavior, shortcuts, focus flow, and accessible names.

## Scope

- **Primary windows**
  - Main window
  - Import window
  - Preferences window

- **Secondary follow-up windows**
  - Book details
  - Book list import
  - Update window
  - Reading history
  - Backup/restore and collection/name-list dialogs where the shared styling applies safely

## Phase 1: Shared visual foundation

- **Add shared style helpers**
  - Extend `src/accessibility/style_helpers.py` with reusable helpers for:
    - Card-style `QGroupBox` panels
    - Modern accessible buttons
    - Primary action buttons
    - Table/header polish
    - Toolbar buttons
  - Use palette-based colors only, so high-contrast and custom themes continue to work.

- **Preserve accessibility rules**
  - Keep visible text on buttons.
  - Do not remove accessible names/descriptions.
  - Do not change `Alt+/` status reread behavior.
  - Do not introduce conflicting `Alt+letter` shortcuts.
  - Keep focus indicators strong and visible.

## Phase 2: Tooltip and accessible-description pass

- **Preferences window first**
  - Add short action-focused tooltips for import settings, validation settings, theme controls, format checkboxes, and restore/default controls.
  - Fill missing accessible names/descriptions where controls currently have placeholders or comments.

- **Import window next**
  - Confirm tooltips for collection, folder, browse, import/scan, error filter, Add Selected, Export, and table.
  - Keep table navigation and JAWS row-announcement fixes intact.

- **Main window next**
  - Confirm tooltips for table, menus, sort/read/collection controls, update/delete/export duplicate actions, and status/sort labels.

## Phase 3: Visual polish for existing layouts

- **Main window**
  - Apply card/panel treatment to top filter/search/sort areas and bottom action/status area.
  - Improve button hierarchy:
    - Primary: Add/New or main action where applicable
    - Destructive: Delete stays visually distinct but not noisy
    - Contextual: Update and Export Duplicates
  - Improve table header and selection styling through shared helpers.

- **Import window**
  - Polish header row as a clear import action area.
  - Make Browse and Import visually distinct while keeping text labels.
  - Polish footer action area containing status, Add Selected, and Export.
  - Keep current import table selection and screen reader behavior unchanged.

- **Preferences window**
  - Apply card-style group boxes to Display Settings, Import Settings, Path & Scope, Fallback/Parsing, and Validation Rules.
  - Keep current layout and tab order unless a change is required for visual spacing.

## Phase 4: Icons with no accessibility regression

- **Icon source**
  - Use Qt standard icons first, or existing centralized icon helper if suitable.
  - Avoid adding new external dependencies unless explicitly approved.

- **Buttons to receive icons**
  - Import / Scan
  - Add / Add Selected
  - Update / Edit
  - Delete
  - Browse
  - Preferences
  - Help
  - Save / Restore Defaults
  - Cancel / Close
  - Export

- **Accessibility constraints**
  - Icons are decorative.
  - Button text remains visible.
  - Accessible names describe the action, not the icon.
  - Tooltips remain short and action-focused.

## Phase 5: Accessible toolbar

- **Main window toolbar first**
  - Add a single-row toolbar, not a ribbon.
  - Use labeled buttons for:
    - Add Book
    - Import
    - Find 
    - Search Web
    - Statistics
    - Preferences
    - Help
  - Reuse existing handlers instead of duplicating logic.

- **Shortcut safety**
  - Keep existing keyboard shortcuts.
  - Do not add new `Alt+letter` shortcuts unless checked against the shortcut registry.
  - Toolbar buttons should be reachable by Tab and screen reader friendly.

- **Later toolbar candidates**
  - Import window action toolbar if the main toolbar pattern tests well.
  - Preferences mini-toolbar only if useful for Save/Restore/Close actions.

## Phase 6: Theme options and theme-safe refinements

- **Review existing themes first**
  - `ThemeManager` already includes Default, High Contrast, Dark, Solarized, Comfort, Nord, Oceanic, Forest Mist, and Paper Sepia.
  - Map the document’s proposed theme names to existing themes instead of duplicating choices.

- **Possible additions**
  - Add a clearly named `Modern` theme only if existing themes do not satisfy the need.
  - Add or rename a `Classic Accessible` option only if it maps cleanly to current default/system behavior.

- **Testing requirement**
  - Verify all new styles in Default, High Contrast Dark, High Contrast Light, and at least one custom light/dark theme.

## Verification checklist

- **Static checks**
  - Run `python -m py_compile` for every edited Python file.

- **Accessibility checks**
  - Confirm `Alt+/` still rereads current status in major windows.
  - Confirm no unmapped `Alt+letter` noise was introduced in text fields.
  - Confirm button text remains visible with icons.
  - Confirm tab order is unchanged or intentionally improved.
  - Confirm focus indicators are visible.

- **Screen reader checks**
  - Quick NVDA/JAWS pass on:
    - Main window toolbar and table
    - Import window header/footer buttons and table
    - Preferences controls with new tooltips/accessibility metadata

- **Visual checks**
  - Verify card/group-box styling does not crowd controls at 100%, enlarged zoom, and high contrast.
  - Verify table selected rows remain visible.
  - Verify toolbar wraps or remains usable on narrower windows.

## Implementation order

1. Add shared visual/style helper functions.
2. Add Preferences tooltips and card styling.
3. Polish Import window buttons/header/footer and confirm table behavior.
4. Polish Main window action areas and table/header styling.
5. Add icons to major buttons with visible text preserved.
6. Add the main window labeled toolbar using existing handlers.
7. Review theme names/options and make only safe refinements.
8. Run syntax checks and targeted manual accessibility checks.
