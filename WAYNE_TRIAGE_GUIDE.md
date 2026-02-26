# tester Feedback Triage Guide (High-Level)

Purpose: quickly classify incoming feedback and decide what to fix first.

Scope: triage findings from packaged build testing (`abcs.exe`).

## Triage Fields (for each issue)
- Issue ID:
- Window name (where issue occurred):
- Category: Accessibility / Performance / Other
- Severity: Critical / High / Medium / Low
- Reproducible: Yes / No
- User impact: Blocks task / Slows task / Cosmetic
- Owner:
- Target fix date:
- Status: New / In Progress / Fixed / Needs Retest / Closed

## Decision Rules
- Critical: blocks core use for blind keyboard users or causes data risk.
  - Action: fix immediately.
- High: major confusion, repeated interruption, or severe lag.
  - Action: prioritize next.
- Medium: clear workaround exists, but UX is degraded.
  - Action: schedule after critical/high.
- Low: minor polish or wording issues.
  - Action: batch into cleanup pass.

## Retest Gate
For each fixed issue, record:
- Retest by tester needed: Yes / No
- Retest result: Pass / Fail
- If Fail, short notes:

## Release Readiness Snapshot
- Critical open issues: number
- High open issues: number
- Accessibility overall: Pass / Needs Work
- Performance overall: Pass / Needs Work
- Ship recommendation: Yes / No
- Final comments:
