# Public Launch — Questions for Chris

These are the decisions I need from you before the launch plan can be finalized. My recommendation is listed under each question — if you agree, you can just say "go with your recommendations" instead of answering each one.

---

## 1. License wording: "open source" vs. what AbCS actually uses

`AbCS_License.txt` is a **Custom Non-Commercial License** (personal/non-commercial use only, no selling, no commercial redistribution). That is **not** an OSI-approved open source license (true "open source" requires allowing commercial use). Calling AbCS "open source" on the new site while the license forbids commercial use is a mismatch that a technical visitor (or a directory's editorial reviewer) may flag.

**Options:**
- **A.** Keep the custom non-commercial license, and describe the project on the site as **"free and source-available"** instead of "open source."
- **B.** Switch to a real OSI license (e.g. MIT, or GPL-3.0 if you want a copyleft that stops others from making a closed paid fork) so "open source" is accurate.

**My recommendation:** A, unless you specifically want to allow commercial reuse/forks. It is the smallest change and matches what you've already written.

Your recommendation this is fine for AbCS 
Does the same apply to Talk3270, or does it use a different license already?
no talk3270 is a application we sell to businesses that have as/400 or simular lagecy terminal systems. Talk3270 is a set of jaws scripts to provide access to these types of terminals. No ddownload for this just a form for requesting a demo / more information. 


## 2. Making the GitHub repos public

Both repos are private today. GitHub Releases (the standard place to host installer downloads) only works publicly if the repo itself is public. Also, "open source"/"source-available" claims require the source to actually be visible.

**Options:**
- **A.** Flip both repos to public at (or just before) launch, and use GitHub Releases to host the installers.
- **B.** Keep repos private for now, and self-host the installer download only on the Aurora Accessibility site (then drop "source-available" language until repos go public).

**My recommendation:** A, once Dominic's AbCS help docs are in and you've done a pass for anything sensitive (API keys, personal info, commit history) — a quick check before flipping to public is worth doing regardless.

Talk3270 will stay private 
---

## 3. Code signing for the Windows build

Right now the README already documents the unsigned-app SmartScreen warning workaround. Several download directories (FilePuma, Softpedia, etc.) run VirusTotal scans, and **unsigned installers from a brand-new publisher frequently get flagged by 1-3 antivirus engines**, which can delay or block approval on those sites.

**Options:**
- **A.** Buy a code-signing certificate (OV cert is roughly $150–400/year) before submitting to third-party directories.
- **B.** Ship unsigned for v1 and accept some rejections/warnings; revisit signing later if it becomes a real blocker.

**My recommendation:** B for now — get the site and GitHub release out first, revisit signing only if a specific directory rejects you for it or SmartScreen becomes a recurring support issue.
Yes option b 
---

## 4. macOS support at launch

There is no macOS installer yet (`doc/plan_macos_installer.md` is still "planned"). Windows and Linux both have working build scripts.

**Options:**
- **A.** Launch v1 with Windows + Linux installers only; macOS users run from source (already documented in INSTALL.md).
- **B.** Hold the public launch until a macOS `.app`/dmg exists.

**My recommendation:** A — don't block the whole launch on the macOS packaging backlog item.
The MAC IOS is off my list too complicated and expensive make a note to clean up any docs.
---

## 5. Talk3270 — current state

I don't have access to the Talk3270 repo/folder from this workspace, so I can't inspect it directly. Can you tell me:
- What kind of project is it (installable desktop app? scripts? web-based)?
- Is it as close to launch-ready as AbCS, or earlier stage?
- Is its GitHub repo also private, and does it have a similar license file?

---Talk3270 is a set of JAWS screen reader scripts that provides customized access to the standard IBM AS/400 327x/5150 terminal. I created these scripts back in 1998 and several large banks and other business have purchased licensed 

## 6. Your Carrd page

You mentioned I can review it if you publish it temporarily. When you're ready, send me the live URL and I'll fetch it and check the content structure and accessibility (heading order, link text, contrast, alt text) as best I can from the rendered page.

Still working on the site 
---

## 7. Donation platform preference

For the "optional donate" link, do you have a preference, or should I just recommend one in the plan?

Common options: GitHub Sponsors, Ko-fi, Buy Me a Coffee, Liberapay, Open Collective, PayPal.me.

**My recommendation:** Ko-fi — no fees on tips, works immediately without a lengthy approval process (GitHub Sponsors requires an application/approval), and has a simple embeddable button for Carrd.

yes agree 
---

Once you've answered (or told me to use my recommendations), I'll fold the decisions into the launch plan.
