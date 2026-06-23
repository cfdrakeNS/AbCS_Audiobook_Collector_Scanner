# AbCS Development Plans — Status

**Last updated:** June 2026

All Cursor development plans from the 2025–2026 AbCS rollout are **complete** except the Name Consistency Check feature (deferred to a future release).

## Active (future work)

| Plan | Location | Status |
|------|----------|--------|
| Name Consistency Check | [Plan_name_consistency_check.md](Plan_name_consistency_check.md) | Planned — not yet implemented |

## Completed

The following plan areas were implemented and verified in code:

- Help system rollout (dynamic `help_docs/`, Help window navigation, Shift+F1 routing)
- README, INSTALL, AGENTS, and user guide refresh
- Status bar unification
- Plot filter and title-plot indicator
- Recently added filter
- Screen reader row reading and Narrator detection
- Web fetch/matching improvements
- Name list accessibility and focus
- Book details layout and performance
- JAWS Book Details label fix (Insert+W pilot — code complete; formal verification checklist closed, not tracked)
- Toolbar/filter shortcuts
- Linux combo and packaging fixes
- Dynamic SQLite pragmas
- Duplicate mode, import, collections, backup/restore, reading history, statistics, preferences

Cursor plan files under `.cursor/plans/` on the development machine may still show stale `pending` todos for superseded work (for example Help System Phase 2, replaced by the navigation redesign). Treat this document and the codebase as the source of truth.

## Related

- Manual QA log: [qa_verification.md](qa_verification.md) (detailed tracker in local `archive/AbCS_Bug_Final_fixes.md`)
- Dead-code review: [CLEANUP_VULTURE_FINDINGS.md](../CLEANUP_VULTURE_FINDINGS.md)
