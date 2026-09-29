# Plot Fetch Quality and Performance

**Version:** 3
**Proposed phase:** 31
**Status:** In progress — Batches A through E implemented; awaiting JAWS/NVDA review
**Scope:** `src/ui/web_metadata.py` and all modules in `src/web/`

## Objective

Make plot fetching faster, more reliable, and less likely to attach a description from the wrong work while preserving the current blocking progress dialog, Escape cancellation, source cooldowns, and Web Metadata review before saving.

## Findings

AbCS identifies a book by querying Open Library, Google Books, and Wikidata in sequence and returns the first acceptable metadata match. Plot enrichment is also sequential and accepts the first plot of at least `PLOT_MIN_LENGTH` that passes the stub, non-book, redundancy, and title/author relevance checks. A matched Open Library work description is preferred; Open Library search and Wikipedia are fallbacks. Successful results and short-lived misses are cached, and a cached match without a plot is enriched again later.

This is safe and understandable, but first-acceptable selection can miss a better description. Sequential fallbacks can spend most of the request budget before reaching the best source.

The local Calibre design under `C:\projects\calibre-master\src\calibre\ebooks\metadata\sources` provides useful patterns: independent source workers, source-owned candidates, normalization before ranking, deterministic comparison, cancellation/time limits, a short wait after the first result, and reuse of source identifiers and caches.

AbCS should not adopt Calibre's plugin framework, full metadata-merging system, or automatic longest-description choice. Description length is useful only after book identity is established.

## Source attribution and licensing gate

Complete a focused review of current API terms before Batch A implementation. The review must cover displaying, modifying, caching, and storing descriptions from Google Books, Open Library, Wikipedia/Wikimedia, and any later source.

Source compliance must be implemented without adding routine screen-reader clutter:

- Use one generic progress message such as **Searching online book sources…** rather than announcing each provider.
- Do not announce the provider when Plot receives focus and do not insert attribution into the plot text.
- Do not add a source control to the normal Tab order.
- Preserve the provider, exact source record or article URL, fetch date, and applicable license information with each candidate where available.
- Make source information available on demand through a context-menu command or another existing, non-disruptive details path.
- Add a user-facing **Data Sources and Attribution** help section listing each provider, data used, required attribution, and terms or license link.
- Provide an on-demand source link when required rather than placing it in the normal review sequence.
- Identify cleaned or shortened text as modified when the applicable license requires it.
- Do not imply that AbCS is affiliated with or endorsed by a provider.
- Confirm whether each provider permits full-description storage and modification. Otherwise use a compliant excerpt and source link, or exclude that provider's plot text.

Source names in progress messages are not the main copyright concern. The material risks are reuse, modification, caching, and storage of plot text. Removing attribution could create an additional compliance problem.

This is a product compliance checkpoint, not a legal conclusion. Any ambiguous provider terms must be resolved before that provider is enabled in a distributed v3 build.

## Proposed design

### 1. Candidate model with compatible facade

Add an internal plot candidate containing text, source, identifiers, match confidence, query type, elapsed time, cache state, and rejection reason. Move normalization, validation, and ranking into a small resolver module while retaining `WebBookAPI.get_book_metadata()` as the public facade.

Rejection reasons belong in opt-in logs and tests, not normal screen-reader announcements.

### 2. Separate identification from plot retrieval

Identify the work once, preserve ISBN/Open Library work key and other stable identifiers internally, and use them for description detail requests. Search by title and author only when identifiers are unavailable. Use Wikidata mainly for identity and identifier bridging. Keep Wikipedia as a strict final fallback.

### 3. Deterministic identity-first ranking

Rank candidates by:

1. Exact ISBN or stable work identifier.
2. Strong normalized title and author match.
3. Source reliability for the matched work.
4. Plot quality: useful prose, adequate length, paragraph quality, and no stub, review, or catalog language.
5. Stable source order as a final tie-breaker.

Low-confidence candidates must not automatically replace an existing saved plot.

### 4. Bounded source concurrency

After identification, request independent plot candidates with a small fixed worker limit and one shared deadline and cancel token. When the first high-confidence plot arrives, allow a short grace period for already-running sources, then rank completed candidates.

Do not start requests after deadline, cancellation, or source cooldown. Keep progress modal for v3 and keep all UI work on the GUI thread.

### 5. Source-aware caching

Cache normalized candidates with source, identifier, fetch time, and resolver schema version. Use different expiration rules for successful plots, confirmed no-description results, rejected matches, and transient timeout, cancellation, or rate-limit results. Transient conditions must not become durable misses.

Re-fetch bypasses the selected-result cache but still respects active source cooldowns. Resolver versioning invalidates obsolete ranking decisions without requiring users to delete the whole cache.

### 6. One resolver for single and batch fetch

`web_metadata.py`, `web_fetch_service.py`, and `batch_web_fetch.py` consume the same chosen plot, provenance, and confidence decision. Batch Apply all uses only high-confidence plots; lower-confidence results go to Review or report no usable plot.

Web Metadata keeps Plot as the initial review focus. Provider information is retained internally and available only on demand. It is not announced on Plot focus, inserted into plot text, or added to the normal Tab order. Internal scores and rejection details must not be exposed as routine announcements.

### 7. Optional follow-up

If real-library results often produce two close valid candidates, consider an accessible **Other plots** list or combo. It requires predictable arrow keys, labelled controls, intentional focus restoration, concise Alt+/ status, and JAWS/NVDA acceptance. It is not required for the core phase.

## Delivery batches

### Batch A — Baseline and candidate structure — Complete

- Complete and record the source attribution and API-terms review before implementation begins.
- Define the required provider, source URL, fetch date, modification notice, and license fields.
- Record fixture timing, request count, chosen source, and rejection reason.
- Add the candidate type and resolver behind the existing facade.
- Preserve current output and source order.

### Batch B — Identifier reuse and cache versioning — Complete

- Retain stable identifiers from identification.
- Prefer identifier detail calls over repeated title searches.
- Add source-aware positive, negative, and transient cache rules.

### Batch C — Deterministic ranking — Complete

- Normalize all candidates available within the shared request budget.
- Add identity-first ranking and automatic-apply confidence rules.
- Preserve source provenance through single and batch review.
- Choose by identity, source reliability, plot quality, then stable source order.
- Mark identifier and title-plus-author matches high confidence; batch Apply all skips lower-confidence plots while individual review retains them.
- Carry selected source, identifiers, URL, fetch time, license, modification state, and confidence with the reviewed plot.
- Prefer exact normalized Open Library title matches over loose-score ties, validate ISBN-returned plot metadata against the requested same work, and keep Google ISBN as an independent fallback even when an Open Library work key exists.
- Treat **The Murder Stone** and **A Rule Against Murder** as title aliases, strip the leading Gamache series label for strict ISBN identity checks, and invalidate prior resolver cache decisions with schema version 3.

### Batch D — Bounded concurrency — Complete

- Run only independent plot requests concurrently.
- Add shared cancellation, deadline, worker cap, deterministic tie-breaking, and cooldown enforcement.
- Compare time and request count with the Batch A baseline.
- Run Open Library, Google ISBN, and Wikipedia plot retrieval as provider-owned jobs with a maximum of three workers; dependent lookups remain sequential within their provider job.
- Reserve shared request capacity atomically, clamp HTTP timeouts to the shared deadline, poll for cancellation, and stop launching requests after cancellation, deadline, or cooldown.
- Rank returned candidates on the caller thread; after an auto-apply-confidence result, allow a 350 ms grace period for already-running providers. Workers do not write cache state or access UI objects.
- Use one generic online-source progress message; provider-specific progress is not announced.
- User smoke-tested several books with no issues; see the cache-isolated live comparison below.
- A cache-isolated live comparison against local `main` was run on 2026-09-29; both revisions used the same interpreter and benchmark harness. The current `main` and v3 working tree share base commit `8c4cf2d`; v3 measurements include its uncommitted changes.
- **A Rule Against Murder**: three runs per revision. `main` median 2.40 s / 9 requests; it selected the five-book Gamache collection and returned no usable plot. v3 median 0.83 s / 2 requests; it selected **The Murder stone** with a 1,187-character Open Library plot. The selected plot hash was identical across all three v3 runs.
- **Chief Inspector Armand Gamache 04 - The Murder Stone**: one run each. `main` found no metadata match (2.14 s / 7 requests); v3 selected **The Murder Stone** with a 995-character Open Library plot (1.83 s / 4 requests).
- **Glass Houses**: one run each. `main` returned a 7-character unusable plot (3.31 s / 12 requests); v3 rejected that short Open Library candidate but found no usable alternative (2.60 s / 12 requests).
- **A Better Man**: one run each. Neither revision found a usable plot; `main` took 5.92 s / 12 requests and v3 took 2.91 s / 12 requests.
- Timings for the latter three fixtures are single live-network samples and are directional only; the reproducible correctness/request-count changes are stronger evidence than those timings.

### Batch E — Other plots selector — Implemented; awaiting JAWS/NVDA review

- Preserve all accepted ranked candidates in the review payload with source provenance.
- Show a visibly labelled **Other plots** combo only when multiple accepted candidates are available; choices use neutral labels and do not announce a provider.
- Keep the selector out of the tab order when absent and include it in normal navigation only when available. Plot remains the initial focus and keeps its existing arrow-key reading behavior.
- Switching candidates updates reviewed text, save differences, and provenance; status announces only that another plot was selected.
- Complete JAWS and NVDA keyboard review before acceptance.

Do not combine the module split, concurrency, cache migration, and optional UI in one change.

## Benefits

- Faster hard misses and slow-source cases.
- Better plots because the first adequate string no longer automatically wins.
- Fewer wrong-work plots through identifier-first retrieval and identity-weighted ranking.
- Fewer repeated searches when a stable identifier is known.
- Consistent decisions in single and batch workflows.
- Better diagnostics without technical noise in normal status messages.
- Lower regression risk by preserving the existing facade.

## Risks and controls

- **Wrong plot:** identity-first scoring, preserved review, and no automatic low-confidence apply.
- **More requests or rate limits:** fixed worker cap, shared budget, cooldowns, identifier detail calls, and request-count gates.
- **Nondeterministic concurrency:** stable scores and source-order tie-breakers; vary completion order in tests.
- **Cancellation races:** one cancel token, bounded waits, worker cleanup, and no worker UI access.
- **Thread-unsafe cache/cooldown state:** centralize writes; source workers do not write shared disk state.
- **Stale cache:** version resolver decisions and retain provenance.
- **Refactor regression:** characterize behavior first and retain the `WebBookAPI` facade.
- **Wikipedia false positives:** keep it last and reject film, television, music, list, and disambiguation text.
- **Copyright, license, or API-terms violation:** retain provenance, provide required attribution and links through quiet help or on-demand details, document modifications, and exclude full-text storage when terms do not permit it.
- **Accessibility regression:** retain modal Escape cancellation, concise announcements, Plot focus, Alt+/, and focus restoration.
- **Scope growth:** plugins, non-modal jobs, covers, and broad metadata merging remain excluded.

## Verification gates

- Fixed fixtures for ISBNs, common titles, subtitles, series, co-authors, missing authors, author-prefixed titles, and same-title different works.
- Add these Louise Penny regression fixtures using author **Louise Penny** and the library title exactly as shown:
  - **Glass Houses** — verify that a common title is resolved using the author or identifier and that a source without a description does not stop cross-source plot retrieval.
  - **Chief Inspector Armand Gamache 04 - The Murder Stone** — verify removal of the leading series name and number for matching; recognize **The Murder Stone** and alternate regional title **A Rule Against Murder** as the same work; continue to another source when the first matched source has no usable plot.
  - **A Better Man** — verify common-title author matching and continued plot retrieval after an Open Library edition reports no description.
- For all three fixtures, record the normalized query, identifiers found, candidates returned and rejected, selected source, request count, and elapsed time.
- A plot failure is acceptable only when every permitted source returns no usable high-confidence description; it must not be caused by a series prefix, alternate title, common-title mismatch, or stopping after the first source lacks a description.
- Cover availability is recorded separately and does not determine the Phase 31 plot result; cover-fetch changes remain out of scope.
- Plot fixtures for HTML, paragraphs, short/stub text, reviews, boilerplate, non-book summaries, and each source.
- Deterministic ranking with different completion orders.
- Budget, timeout, cancel, cooldown, cache expiry, and transient-error checks.
- Identical plot decisions for single and batch fetch.
- Existing plots never overwritten by empty or low-confidence results.
- Representative local, network-drive, slow-network, and hard-miss manual comparisons.
- Escape cancellation and clean shutdown.
- JAWS and NVDA review of Plot, Save, Re-fetch, status, and Alt+/.
- Confirm that provider names are not announced during progress or Plot focus and that source information is outside the normal Tab order.
- Data Sources and Attribution documentation matches the providers and fields used by the application.
- Each enabled provider has a recorded decision for display, modification, caching, storage, linking, and license notices.

The test suite is not run during planning. Run tests only when the user requests implementation verification.

## Acceptance criteria

- Median and worst-case times improve on the agreed fixture set without more wrong-work selections.
- Requests stay within budget and cooled-down sources are not contacted.
- The same inputs choose the same plot regardless of response order.
- Single and batch fetch share resolver and cleaning rules.
- Cancellation leaves no worker or partial cache write.
- Existing callers continue through the `WebBookAPI` facade.
- JAWS and NVDA workflows add no announcement noise.
- Every displayed or saved plot retains the attribution and source link required by its provider or content license, available through help or on-demand details without changing the plot text.
- No provider with unresolved terms is used for plot text in a distributed build.
