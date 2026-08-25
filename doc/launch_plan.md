# AbCS Public Launch Plan

**Status:** Main Aurora site ready for Dominic content review; AbCS product site is the next Carrd priority.
**Created:** Aug 2026
**Updated:** Aug 2026
**Source of decisions:** [launch_open_questions.md](launch_open_questions.md) (keep for the record; this document is the actionable plan built from those answers).

---

## 1. Decisions summary

| # | Topic | Decision |
|---|-------|----------|
| 1 | License wording | Keep the existing custom non-commercial license (`AbCS_License.txt`). Describe AbCS publicly as **"free and source-available"**, not "open source" (license forbids commercial use/resale, so "open source" would be inaccurate). |
| 2 | GitHub repo visibility | Flip the **AbCS** repo to public once the pre-flip security/content pass is done (see checklist). **Talk3270** is a separate, unrelated product/repo and stays private — not part of this launch. |
| 3 | Code signing | Ship the Windows build **unsigned** for v1. Keep the existing SmartScreen workaround note in the README/INSTALL docs. Revisit only if a specific download directory rejects the unsigned build or SmartScreen becomes a recurring support issue. |
| 4 | macOS support | **Dropped from the roadmap** — no packaged macOS installer. macOS users continue to run AbCS from source (already documented). Backlog/status docs updated to reflect this (see Doc cleanup below). |
| 5 | Talk3270 | Separate JAWS-scripting product for AS/400 terminal access (sold to businesses since 1998); demo-request form only, no public download. Carrd site supports lead gen; not on the critical path for the AbCS repo/release launch. |
| 6 | Web presence | **Three Carrd sites** under `auroraaccessibility.com`: main brand/home (`auroraaccessibility.com`), AbCS (`abcs.auroraaccessibility.com`), Talk3270 (`talk3270.auroraaccessibility.com`). DNS via Porkbun; Cloudflare not used. |
| 7 | Donation link | **Ko-fi** confirmed. Add a Ko-fi link/button to the README and the AbCS Carrd page (not required on the main Aurora page for v1). |
| 8 | Public contact | **`auroraaccessibility@gmail.com`** for README Support and product-specific use. **Main Aurora site:** no public email (routes visitors to product sites). **AbCS site:** add a contact/questions section when ready. **Talk3270 site:** demo request form (and email via form workflow). |
| 9 | AbCS help docs on the site | Link from the AbCS Carrd site via **one link** to a single GitHub entry point (`help_docs/01_overview.md`), not per-doc Carrd pages. Avoids GitHub file-tree navigation for screen reader users and avoids duplicating/maintaining 22 docs on Carrd. In-app help (Shift+F1 / bundled `help_docs`) remains primary. |
| 10 | AbCS video tutorials | **Deferred** — not part of v1 launch. Text and in-app help are enough for now; revisit later if users ask for video. |
| 11 | Talk3270 package delivery | After a demo-request / license, send the zipped install + user docs via a **Google Drive** shared link per client (manual, not a public download). |
| 12 | Talk3270 client support page | **Unlisted Carrd page** (not in site navigation), shared with licensed clients via direct link only. |
| 13 | Git commit identity | Before AbCS goes public, rewrite commit author/committer from the personal Hotmail address to **Aurora Accessibility** / GitHub noreply (`18517493+cfdrakeNS@users.noreply.github.com`). Same rewrite applied to the already-public `pyside6-accessible-ui-reference` repo. |

---

## 2. Site status (Aug 2026)

### Main Aurora site — ready for Dominic review

**Test URL:** https://auroratesting.carrd.co/  
**Live URL (when published):** https://auroraaccessibility.com/

Done:

- Hero with Products (AbCS, Talk3270) and About section
- About copy: mission, What we build, Our story, Our approach, The team (Francis and Dominic, first names only)
- Talk3270 blurb links to Talk3270 site
- No public email on main site
- Heading structure: one H1, H2 for Products and About, H3 subsections
- Meta description set
- Indexing off on test URL until launch

Pending (after Dominic meeting):

- Dominic content/sign-off on Our story, team blurbs, and bank/employer wording
- Expand accessibility wording to mention **braille display users** (tagline and/or About — deferred until meeting)
- Copyright footer (optional, low priority)
- Switch test URLs to custom domains and publish when approved
- Ko-fi on main site — optional; not required for v1

About-page draft reference: [aurora_about_page_draft.md](aurora_about_page_draft.md)

### AbCS site — next priority

**Test URL:** https://abcstest.carrd.co/  
**Live URL (when published):** https://abcs.auroraaccessibility.com/

Needs work: download buttons, **one** help-docs link to GitHub `help_docs/01_overview.md` (not per-doc pages), placeholder list items, typos, contact section, heading cleanup, Ko-fi link, braille/screen reader copy alignment with main site. Video tutorials deferred.

### Talk3270 site — after AbCS or in parallel with Dominic

**Test URL:** https://talk3270.carrd.co/  
**Live URL (when published):** https://talk3270.auroraaccessibility.com/

Needs work: sectioned layout cleanup, features/benefits as proper lists, demo form review with Dominic, duplicate headings, link labels. Client delivery via Google Drive; unlisted Carrd support page for licensed clients.

---

## 3. Doc cleanup already done (earlier pass)

- [plan_macos_installer.md](plan_macos_installer.md) — status changed from "Planned" to "Cancelled — out of scope", with a note pointing back to this plan.
- [plan_enhancements_fall2026.md](plan_enhancements_fall2026.md) — removed the macOS installer row from the backlog table.
- [plans_status.md](plans_status.md) — removed macOS installer from the active backlog table; added a new "Cancelled / dropped" section listing it with rationale.
- [abcs_proposed_enhancements.md](abcs_proposed_enhancements.md) — moved "Mac installer" out of the tester-facing backlog table and into "What we are not planning".
- [README.md](README.md) — changed the Windows SmartScreen note from "new open-source project" to "new, free and source-available project" to match the licensing decision.
- [linux_build.md](../linux_build.md) — removed a personal Gmail address that had been hardcoded into an example SSH key output; replaced with the same generic placeholder used elsewhere in that doc.
- [README.md](README.md) — Support section now points to `auroraaccessibility@gmail.com` instead of naming C.F. Drake directly, so no personal contact info is exposed once the repo is public.

---

## 4. Pre-launch checklist

### Main Aurora site
- [x] Carrd layout: hero, product links, About section
- [x] About copy drafted and published on test site
- [x] No public email on main site (product sites handle contact)
- [x] DNS/custom domains configured (Porkbun)
- [ ] Dominic content review and sign-off
- [ ] Braille display users mentioned in copy (after Dominic meeting)
- [ ] Publish to `auroraaccessibility.com` and confirm SSL

### AbCS Carrd site
- [ ] Finish product page content (features, accessibility, downloads)
- [ ] Replace tutorial placeholders with **one** help-docs link to GitHub `help_docs/01_overview.md` (not per-doc pages); fix link text
- [ ] Add contact/questions section with `auroraaccessibility@gmail.com`
- [ ] Add Ko-fi link
- [ ] Accessibility pass (headings, lists, contrast)
- [ ] Wire download buttons to GitHub Release assets when ready
- [ ] Publish to `abcs.auroraaccessibility.com`
- [ ] Video tutorials — out of scope for v1 (deferred)

### Talk3270 Carrd site
- [ ] Dominic review of demo form and business copy
- [ ] Clean up sectioned layout and duplicate headings
- [ ] Publish to `talk3270.auroraaccessibility.com`
- [ ] Client package delivery via Google Drive shared link (manual, per client)
- [ ] Unlisted Carrd support page for licensed clients (tutorials/docs; direct link only)

### Repo / code (AbCS)
- [ ] **Blocker:** Scrub personal email from AbCS git commit history (author/committer → Aurora Accessibility / GitHub noreply) before flipping public. Same rewrite for `pyside6-accessible-ui-reference` (already public).
- [ ] Security/content pass on the AbCS repo before flipping public: search commit history and current tree for API keys, tokens, personal paths, or personal info.
- [ ] Confirm `AbCS_License.txt` and the README License section both read "free and source-available" (or equivalent) consistently — no lingering "open source" wording.
- [ ] Confirm Dominic's AbCS help doc pass is merged before flipping the repo public.
- [ ] Flip the AbCS GitHub repo from private to public.
- [ ] Create a GitHub Release and attach the Windows installer (and Linux build, if ready) as release assets.
- [ ] Verify the unsigned-installer SmartScreen note in README/INSTALL still matches the actual install experience.

### Marketing / cross-cutting
- [ ] Add a Ko-fi link to the README (Support section) if desired.
- [ ] Make sure the AbCS site describes AbCS as "free and source-available", not "open source".
- [ ] Do not reference a macOS installer or "coming to Mac" anywhere on the sites — macOS is source-only.
- [x] Public contact email decided: `auroraaccessibility@gmail.com` (README; AbCS and Talk3270 sites as appropriate).

---

## 5. Suggested sequencing

1. **Git history privacy fix** — rewrite personal Hotmail out of AbCS and `pyside6-accessible-ui-reference` commit metadata; update local git config; enable GitHub "Keep my email private" / block-push settings (manual).
2. **Dominic meeting** — sign off main site About copy; agree braille-display wording; confirm Talk3270 form/copy expectations.
3. **AbCS Carrd site** — finish product page (downloads, one help-docs link, contact, Ko-fi). This is on the critical path for the AbCS launch.
4. Security/content pass on the AbCS repo (can overlap with step 3).
5. Merge Dominic's help docs.
6. Publish main + AbCS Carrd sites to custom domains.
7. Flip AbCS repo to public.
8. Cut a GitHub Release with installer(s) attached; wire AbCS site download buttons.
9. **Talk3270 Carrd site** — polish and publish (can follow AbCS; not blocking AbCS repo/release); set up Google Drive delivery and unlisted client support page.

---

## 6. Open items

- Dominic review of main site test URL: https://auroratesting.carrd.co/
- Braille display users — copy expansion deferred until Dominic meeting
- Confirm whether the Linux build should attach to the first GitHub Release, or Windows-only for v1
- Talk3270 site timing — after AbCS unless Dominic wants it prioritized at the meeting
- AbCS video tutorials — deferred; revisit after launch if needed
- Manual GitHub account settings: enable "Keep my email addresses private" and "Block command line pushes that expose my email"
