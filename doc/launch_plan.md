# AbCS Public Launch Plan

**Status:** All three Carrd sites ready on test URLs; awaiting Dominic content review before custom domains and repo flip.
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
| 7 | Donation link | **Ko-fi** confirmed. Add a Ko-fi link/button to the README and the AbCS Carrd page (optional for v1). |
| 8 | Public contact | **`auroraaccessibility@gmail.com`** in README Support. **Main Aurora site:** no public email. **AbCS site:** no public email (free product; in-app help only — no support inbox). **Talk3270 site:** demo form → `auroraaccessibility@gmail.com` as form recipient. |
| 9 | AbCS help docs on the site | Optional: one link from the AbCS Carrd site to GitHub `help_docs/01_overview.md`. In-app help (Shift+F1 / bundled `help_docs`) remains primary. Dominic owns help doc copy — do not edit `help_docs/` in repo until his pass is merged. |
| 10 | AbCS video tutorials | **Deferred** — not part of v1 launch. Text and in-app help are enough for now; revisit later if users ask for video. |
| 11 | Talk3270 package delivery | After a demo-request / license, send the zipped install + user docs via a **Google Drive** shared link per client (manual, not a public download). |
| 12 | Talk3270 client support page | **Unlisted Carrd page** (not in site navigation), shared with licensed clients via direct link only. |
| 13 | Git commit identity | Rewrite commit author/committer from personal Hotmail to **Aurora Accessibility** / GitHub noreply. **Done Aug 2026** via `fresh_public_repo.ps1`. |
| 14 | Product naming | Use **Audiobook** (one word) for the expanded product name: **Audiobook Collector Scanner**. Body text: **audiobook** / **audiobooks**. Default collection: **Audiobooks**. Align code and docs; `help_docs/` updated by Dominic separately. |

---

## 2. Site status (Aug 2026)

### Main Aurora site — ready for Dominic review

**Test URL:** https://auroratesting.carrd.co/  
**Live URL (when published):** https://auroraaccessibility.com/

Done:

- Hero with Products (AbCS, Talk3270) and About section
- About copy: mission, What we build, Our story, Our approach (incl. PySide6 GitHub link), The team
- Talk3270 blurb links to Talk3270 site
- **Audiobook Collector Scanner** naming on Products and About
- No public email on main site
- Heading structure, meta description, footer
- Indexing off on test URL until launch

Pending (after Dominic meeting):

- Dominic content/sign-off on Our story, team blurbs, and bank/employer wording
- Expand accessibility wording to mention **braille display users** (deferred until meeting)
- Switch test URLs to custom domains, turn indexing on, publish when approved

About-page draft reference: [aurora_about_page_draft.md](aurora_about_page_draft.md)

### AbCS site — ready for Dominic review

**Test URL:** https://abcstest.carrd.co/  
**Live URL (when published):** https://abcs.auroraaccessibility.com/

Done:

- Product page: features, accessibility bullets, **AbCS — Audiobook Collector Scanner** title
- Download buttons wired to GitHub Release v2.06 (Windows + Linux zips)
- Footer link to Aurora main site
- No public contact email (by design)

Pending (optional / post-Dominic):

- Ko-fi link (optional)
- One help-docs link to GitHub `help_docs/01_overview.md` (optional)
- Publish to custom domain; turn indexing on

### Talk3270 site — ready for Dominic review

**Test URL:** https://talk3270.carrd.co/  
**Live URL (when published):** https://talk3270.auroraaccessibility.com/

Done:

- Features and Benefits as proper lists; intro as paragraph (single H1)
- Demo request form: Contact Name, Organization, Email, terminal emulator (message field), Require consent
- Form recipient: `auroraaccessibility@gmail.com`
- **Filter messages** off (required for delivery — short field values were blocked when on)
- Footer link to Aurora main site

Pending (after Dominic meeting):

- Dominic review of demo form copy and business wording
- Publish to custom domain; turn indexing on
- Google Drive delivery workflow for licensed clients
- Unlisted client support Carrd page (direct link only)

---

## 3. Doc cleanup already done (earlier pass)

- [plan_macos_installer.md](plan_macos_installer.md) — status changed from "Planned" to "Cancelled — out of scope", with a note pointing back to this plan.
- [plan_enhancements_fall2026.md](plan_enhancements_fall2026.md) — removed the macOS installer row from the backlog table.
- [plans_status.md](plans_status.md) — removed macOS installer from the active backlog table; added a new "Cancelled / dropped" section listing it with rationale.
- [abcs_proposed_enhancements.md](abcs_proposed_enhancements.md) — moved "Mac installer" out of the tester-facing backlog table and into "What we are not planning".
- [README.md](../README.md) — SmartScreen note uses "free and source-available project"; Support uses `auroraaccessibility@gmail.com`.
- [linux_build.md](linux_build.md) — removed personal email from SSH key example.
- Git history scrub and remote cleanup — **done Aug 2026** (`fresh_public_repo.ps1`, [github_cleanup.ps1](github_cleanup.ps1)).
- GitHub Release **v2.06** with Windows and Linux zip installers — **done Aug 2026** (manual upload).
- Carrd publish script — [publish_github_release.ps1](publish_github_release.ps1).

---

## 4. Pre-launch checklist

### Main Aurora site
- [x] Carrd layout: hero, product links, About section
- [x] About copy on test site
- [x] No public email on main site
- [x] DNS/custom domains configured (Porkbun)
- [ ] Dominic content review and sign-off
- [ ] Braille display users mentioned in copy (after Dominic meeting)
- [ ] Publish to `auroraaccessibility.com`, indexing on, confirm SSL

### AbCS Carrd site
- [x] Product page content (features, accessibility, downloads)
- [x] Download buttons → GitHub Release v2.06
- [x] No public contact email (by design)
- [ ] Ko-fi link (optional)
- [ ] Help-docs link to GitHub entry point (optional)
- [ ] Publish to `abcs.auroraaccessibility.com`, indexing on

### Talk3270 Carrd site
- [x] Features/benefits lists and demo form working
- [x] Form recipient and Filter messages off
- [ ] Dominic review of form and business copy
- [ ] Publish to `talk3270.auroraaccessibility.com`, indexing on
- [ ] Google Drive delivery for licensed clients
- [ ] Unlisted client support page

### Repo / code (AbCS)
- [x] Scrub personal email from git history
- [x] GitHub remote branch/tag cleanup
- [x] GitHub Release v2.06 with installers
- [x] Align **Audiobook Collector Scanner** naming in code/docs (excluding `help_docs/` — Dominic)
- [x] Help → Website… opens AbCS product page
- [x] Aurora Accessibility in About, License, and installer publisher
- [x] Root doc tidy (`linux_build.md`, `abcs_linux_fixes.md`, `CLEANUP_VULTURE_FINDINGS.md` → `doc/`)
- [ ] Security/content pass before public flip
- [ ] Confirm license/README wording ("free and source-available")
- [ ] Merge Dominic's help doc pass before or soon after public flip
- [ ] Flip repo to public (if not already)
- [ ] Verify SmartScreen note in README/INSTALL

### Marketing / cross-cutting
- [ ] Ko-fi on README and/or AbCS site (optional)
- [ ] Sites describe AbCS as "free and source-available", not "open source"
- [x] Public contact email: `auroraaccessibility@gmail.com` (README; Talk3270 form)

---

## 5. Suggested sequencing

1. **Dominic meeting** — sign off all three Carrd sites; braille-display wording; Talk3270 form/copy; help docs timeline.
2. ~~**Naming pass in repo**~~ — **done Aug 2026** (code/docs; `help_docs/` for Dominic).
3. Security/content pass on AbCS repo.
4. Publish all three Carrd sites to custom domains; indexing on.
5. Flip AbCS repo public (if not done); confirm Release assets and download links.
6. Talk3270 client delivery (Google Drive) and unlisted support page when needed.

---

## 6. Open items

- Dominic review: https://auroratesting.carrd.co/ , https://abcstest.carrd.co/ , https://talk3270.carrd.co/
- Braille display users — copy expansion deferred until Dominic meeting
- Talk3270 fixed email subject (`Request Talk3270 Demo`) — requires Pro Plus or Gmail filter; Pro Standard uses default Carrd subject
- Dominic help docs merge — do not edit `help_docs/` locally until merged
- Manual GitHub settings: "Keep my email addresses private", "Block command line pushes that expose my email"
