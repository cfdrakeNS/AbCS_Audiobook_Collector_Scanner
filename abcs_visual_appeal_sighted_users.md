# Plan

## Go.al

Improve the visual_appeal_sighted_users **without weakening screen reader accessibility**.

## Recommended Direction

Use a **modern accessible toolbar + styled panels/cards**, not a full ribbon at first.

This gives the app more visual structure while keeping:

- Keyboard navigation predictable
- Screen reader output clear
- Tab order manageable
- Existing shortcuts intact

# Phase 1: Visual Polish Foundation

## What will change

- **Window headers**
  - Add clearer title/header areas to major windows.
  - Use larger section headings where helpful.

- **Grouped sections**
  - Style existing `QGroupBox` areas to look more like cards.
  - Add subtle borders, padding, and spacing.

- **Buttons**
  - Improve button styling.
  - Make primary actions visually stronger.
  - Keep text labels visible.

- **Tables**
  - Improve header styling.
  - Add clearer selected-row colors.
  - Preserve strong focus indication.

- **Status areas**
  - Keep current status announcement behavior.
  - Improve visual contrast and spacing.

## Windows to start with

- **Main window**
- **Import window**
- **Preferences window**

## Shortcut consistency notes

- **List/table focus**
  - Use `Alt+L` as the app-standard shortcut for moving focus to the primary list or table.
  - Reading History should not use `Alt+B` for table focus.

# Phase 2: Icons Without Accessibility Regression

## What will change

- Add icons beside text for common actions:
  - Import
  - Scan
  - Add
  - Edit
  - Delete
  - Preferences
  - Help
  - Save
  - Cancel
  - Browse

## Accessibility requirements

- **No icon-only critical buttons**
  - Text remains visible.

- **Accessible names stay meaningful**
  - Example:
    - Button text: `Scan`
    - Accessible name: `Scan selected folder for audiobooks`

- **Icons are decorative**
  - Screen readers should announce the action, not the icon name.

- **Tooltips match the action**
  - Tooltip should be short and useful.

# Phase 3: Accessible Toolbar

## What will change

Add a simple toolbar to major windows, likely starting with the main window.

## Toolbar style

Not a ribbon.

Use a single-row action toolbar with labeled buttons:

- **Add Book**
- **Import**
- **Search Web**
- **Statistics**
- **Preferences**
- **Help**

## Accessibility requirements

- Keep existing keyboard shortcuts.
- Do not create conflicting Alt shortcuts.
- Toolbar buttons must have:
  - Visible text
  - Tooltip
  - Accessible name
  - Accessible description where useful

# Phase 4: Theme Options

## What will change

Add or improve theme choices later:

- **Default/System**
- **Modern**
- **High Contrast**
- **Classic Accessible**

## Why later

Theme work touches many windows. It is safer after the toolbar/card styling patterns are proven.

# About Tooltips

Tooltips are a good idea for sighted users, but they should be treated as **visual help only**, not the only source of information.

## Tooltip rules

- **Short**
  - One sentence or phrase.

- **Action-focused**
  - Say what the control does.

- **Not required for screen reader understanding**
  - Screen readers should rely on accessible names/descriptions.

- **Consistent**
  - Similar buttons should use similar wording.

## Good tooltip examples

- **Browse**
  - `Choose an import folder`

- **Scan**
  - `Scan the selected folder for audiobooks`

- **Add Selected**
  - `Add selected books to the collection`

- **Preferences**
  - `Open application preferences`

- **Restore Defaults**
  - `Restore recommended default settings`

- **Reader Keywords**
  - `Comma-separated words used to detect narrators in comments`

- **Minimum Book Minutes**
  - `Flag books shorter than this many minutes`

- **Maximum Book Hours**
  - `Flag books longer than this many hours`

# Tooltip Accessibility Pattern

For each important control:

- **Visible label**
  - What sighted users see.

- **Tooltip**
  - Short visual explanation.

- **Accessible name**
  - Clear screen reader name.

- **Accessible description**
  - Slightly longer screen reader explanation if needed.

Example behavior:

```text
Visible label: Min Book Minutes
Tooltip: Flag books shorter than this many minutes
Accessible name: Minimum book length in minutes value
Accessible description: Sets the minimum allowed book length for import validation
```

# Suggested First Implementation

I recommend starting with:

- **Preferences window tooltip pass**
  - Low risk.
  - Many controls already have accessible names.
  - Good place to establish the pattern.

- **Import window toolbar/button polish**
  - High visibility.
  - Directly addresses tester feedback.

- **Main window action toolbar**
  - Makes the whole app feel more polished.

# My Recommendation

Start with **tooltips + visual polish**, then add icons, then add a toolbar.

Best order:

1. Add consistent tooltips to Preferences and Import windows.
2. Apply card-style group boxes and improved button styling.
3. Add icons to major buttons.
4. Add simple toolbar to the main window.