# AbCS Project Index (Current)

Last updated: 2026-03-03

This index reflects the **current workspace layout**. Several older investigation files were moved to `archive/`; stale root-level references were removed.

---

## Core project docs (active)

- [README.md](README.md) — project overview and current behavior
- [INSTALL.md](INSTALL.md) — setup and run instructions
- [AbCS_Guide_(Draft).md](AbCS_Guide_(Draft).md) — user-facing guide (current UI/shortcut behavior)
- [App_Standardization_Implementation_Order.md](App_Standardization_Implementation_Order.md) — UI standardization roadmap and status

## Accessibility + collaboration docs (active)

- [Copilot_JAWS_ Working_Agreement (AbCS).md](Copilot_JAWS_%20Working_Agreement%20(AbCS).md) — collaboration workflow
- [accessibility_gap_testing.md](accessibility_gap_testing.md) — active gap-testing notes
- [accessibility_app_patterns.md](accessibility_app_patterns.md) — implementation patterns
- [Accessibility_best-practice_ rules (PySide6).md](Accessibility_best-practice_%20rules%20(PySide6).md) — reference rules
- [Jaws_and_PySide6_best_practices.md](Jaws_and_PySide6_best_practices.md) — JAWS/PySide6 guidance

## Shortcut + UI reference docs (active)

- [AbCS_shortcut Keys.md](AbCS_shortcut%20Keys.md) — shortcut reference
- [ShortCut_Normalization_plan.md](ShortCut_Normalization_plan.md) — normalization plan
- [Feedback_app_structure.md](Feedback_app_structure.md) — source feedback used for standardization
- [Status_bar_option_workaround.md](Status_bar_option_workaround.md) — status bar behavior notes
- [pref win layout new minimal.md](pref%20win%20layout%20new%20minimal.md) — preferences layout notes

## Project structure pointers

- [src/](src/) — application source (`main.py`, UI, database, accessibility)
- [test/](test/) — active automated tests
- [data/](data/) — DB scripts and related data files

---

## Archived documentation (kept available)

### Accessibility reports archive
- [archive/acessibility/Accessibility_DELIVERABLES.md](archive/acessibility/Accessibility_DELIVERABLES.md)
- [archive/acessibility/accessibility_gaps_mar01.md](archive/acessibility/accessibility_gaps_mar01.md)
- [archive/acessibility/Accessibility_VALIDATION_REPORT.md](archive/acessibility/Accessibility_VALIDATION_REPORT.md)
- [archive/acessibility/Accessibility_VISUAL_SUMMARY.md](archive/acessibility/Accessibility_VISUAL_SUMMARY.md)
- [archive/comprehensive_accessibility_changes_reorganized.md](archive/comprehensive_accessibility_changes_reorganized.md) — Completed accessibility standardization work (Mar 2026)

### Historical investigation/test bundle
- [archive/test/ACCESSIBILITY_DOCS_README.md](archive/test/ACCESSIBILITY_DOCS_README.md)
- [archive/test/JAWS_INVESTIGATION_RESULTS.md](archive/test/JAWS_INVESTIGATION_RESULTS.md)
- [archive/test/JAWS_ACCESSIBILITY_DIAGNOSIS.md](archive/test/JAWS_ACCESSIBILITY_DIAGNOSIS.md)
- [archive/test/JAWS_TESTING_GUIDE.md](archive/test/JAWS_TESTING_GUIDE.md)
- [archive/test/ACCESSIBILITY_DEBUG_GUIDE.md](archive/test/ACCESSIBILITY_DEBUG_GUIDE.md)
- [archive/test/CHANGES_SUMMARY.md](archive/test/CHANGES_SUMMARY.md)

---

## Notes on cleanup

- Removed stale root-level references to docs that are no longer present at root.
- Kept important archived items discoverable via explicit `archive/` links.
- Promoted currently relevant implementation/tracking docs (especially roadmap + guide) to the top.

## Keep readily available (recommended)

- [App_Standardization_Implementation_Order.md](App_Standardization_Implementation_Order.md)
- [AbCS_Guide_(Draft).md](AbCS_Guide_(Draft).md)
- [Copilot_JAWS_ Working_Agreement (AbCS).md](Copilot_JAWS_%20Working_Agreement%20(AbCS).md)
- [ShortCut_Normalization_plan.md](ShortCut_Normalization_plan.md)
- [archive/test/ACCESSIBILITY_DOCS_README.md](archive/test/ACCESSIBILITY_DOCS_README.md)
- [archive/acessibility/accessibility_gaps_mar01.md](archive/acessibility/accessibility_gaps_mar01.md)

---

## Document lifecycle (Active vs Archive)

Use these rules when adding, moving, or cleaning docs:

- **Active (keep in project root):** currently used for implementation, testing, user guidance, or team workflow.
- **Archive (move under `archive/`):** historical snapshots, completed investigations, old plans, or one-time logs not needed day-to-day.
- **Index policy:** if a file is moved to `archive/`, update its index link immediately and remove stale root references.
- **Promotion rule:** if an archived doc becomes relevant again, move it back to active location and restore it in active sections.
- **Review cadence:** quick index review at each milestone close or major refactor to keep links and classifications current.
