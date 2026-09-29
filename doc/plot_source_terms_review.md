# Plot Source Terms Review

Status: Batch A record. Provider terms require confirmation before plot text is enabled in a distributed build.

This document records the fields required for each plot candidate. The application must retain the provider, exact source URL when available, fetch date, modification status, and applicable license or terms identifier. It must not present this record as legal advice.

| Provider | Data used | Display | Modify | Cache | Store | Required action |
| --- | --- | --- | --- | --- | --- | --- |
| Open Library | Metadata and work descriptions | Review terms | Review terms | Review terms | Review terms | Confirm current API and description terms; record attribution and URL requirements. |
| Google Books | Volume metadata and descriptions | Review terms | Review terms | Review terms | Review terms | Confirm current API terms and whether full description storage and modification are permitted. |
| Wikipedia/Wikimedia | Article summaries and extracts | Review terms | Review terms | Review terms | Review terms | Confirm applicable Wikimedia license, attribution, modification notice, and link requirements. |
| WikiData | Work identity and identifiers | Review terms | Review terms | Review terms | Review terms | Confirm API terms and identifier reuse requirements. |

Batch A records provenance and diagnostics but does not change provider order, selection rules, caching policy, or concurrency. No provider should be treated as approved for distributed plot-text storage until the unresolved terms above are confirmed.