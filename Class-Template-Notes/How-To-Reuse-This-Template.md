# How to reuse this template for a future class

This repo was built as **a class template**, not a Caterpillar-
specific deliverable. The structure, references, tools, and
pedagogy all carry forward. Only the target-specific content needs
to change.

---

## What to swap

### 1. `Target-Briefs/` — the target dossier

This folder defines the target and its scope. Replace the single
file `Target-Caterpillar.md` with a new brief for your next target:
`Target-[CompanyName].md`.

Update inside the file:
- Company name, tickers, legal entity
- Scope boundaries (passive only? active permitted? individuals
  in/out?)
- The three memorize rules (target-specific or same three)
- What sources will likely block the class, used as a teaching
  moment

---

### 2. Find-and-replace across all student files

Every module, lab, cheatsheet, and reference contains target-specific
strings. Use a find-and-replace pass:

| Find | Replace with |
|------|--------------|
| `Caterpillar Inc.` | `[New Target Inc.]` |
| `Caterpillar` | `[New Target]` |
| `caterpillar.com` | `[newtarget.com]` |
| `cat.com` | `[secondary-domain.com]` (or delete if N/A) |
| `CAT` (when used as ticker / shorthand) | `[new ticker]` |
| Plant-specific names (`East Peoria`, `Mossville`) | `[new target's key facilities]` |
| Industry-specific framing ("builds machines", "manufacturer", "Fortune 100") | update per new target |
| Example Admiralty-rated findings | rewrite for new target |

**Files heavily affected:**
- `README.md` (landing page)
- `00-Students-Start-Here.md`
- All `Class-Modules/Module-*.md`
- All `Student-Labs/Lab-Module-*.md`
- `Student-Handouts/Corporate-Recon-Cheatsheet.md`
- `Student-References/Admiralty-Code.md` (worked examples use CAT)
- `Mirrors/README.md` (mirror paths reference CAT)

**Files you can leave alone:**
- `LICENSE`
- `.env.example`
- `.gitignore`
- `requirements.txt`
- `Student-References/Pre-Flight-Checklist.md` (target-agnostic)
- `Student-References/CRAAP-Test.md` (target-agnostic)
- `Student-References/Sock-Puppets.md` (target-agnostic)
- `Student-References/Jobs-Pipeline.md` (target-agnostic)
- `Tools-and-Scripts/*.py` (target-agnostic; accept target as arg)

---

### 3. Date, venue, time

Every class-day reference to "BSides KC 2026 · April 25 2026 ·
KCKCC" needs updating. Grep first:

```bash
grep -rn "BSides KC 2026\|April 25, 2026\|2026-04-25\|KCKCC" .
```

Update in README, Start-Here, Target brief, and the closing remarks
in `Final-Activity/Wrap-and-Shout-Outs.md`.

---

### 4. Pre-cached mirrors

The mirror files in `Mirrors/crtsh/`, `Mirrors/subfinder/`,
`Mirrors/wayback/` are target-specific. **Run the precache recipe
in `Mirrors/README.md` against your new target the night before
class.**

Old mirror files for the previous target can be deleted or moved to
`Mirrors/archive/` for future reference.

---

### 5. Module 3 / 4 validation

Some technique-specific details in modules 3 and 4 depend on the
target:

- **Wildcard detection result** — CAT doesn't wildcard. Your new
  target might. Confirm during dry-run and update the Module 3
  framing if needed.
- **Akamai fronting** — most F500s are CDN-fronted in 2026 but the
  specific CDN varies. Adjust Module 4's tech-fingerprint framing if
  the new target uses Cloudflare, Fastly, etc.
- **Foundation DNS fingerprint** — mention if target uses it; drop
  if irrelevant.
- **EPA / OSHA / FAA / FCC coverage** — depends on whether the new
  target has environmental regulation, industrial workforce,
  corporate aircraft, wireless licenses. A tech company has far
  less surface in these sources than a manufacturer. Adjust Module
  4 weight accordingly.
- **USASpending relevance** — only matters if the target is a
  federal contractor. Cut the USASpending segment entirely if not
  (and flag the alternative: for non-contractor targets, USPTO
  trademark filings often surface similar structural information).

---

### 6. Example cheatsheet rewrites

Any code block in `Student-Handouts/Corporate-Recon-Cheatsheet.md`
that shows a specific subdomain, IP, or hostname from CAT needs
updating. Do a dry run of each command against your new target and
paste in current results.

---

## Pre-class checklist (use this every time)

- [ ] Target brief written and reviewed for scope
- [ ] Find-and-replace pass completed across all student files
- [ ] Date and venue updated everywhere
- [ ] Mirrors pre-cached the night before (test that the files
      parse with `jq`)
- [ ] Modules re-read after the swap, looking for orphaned CAT
      references you missed
- [ ] Dry-run Module 3 wildcard detection on the new target
- [ ] Dry-run Module 4 favicon pivot on the new target
- [ ] `domain_to_dossier.py` test run against the new target (look
      for surprises)
- [ ] `.gitignore` confirms `Instructor-Only/` is excluded
- [ ] New repo URL updated in scripts' User-Agent strings and in
      references across the codebase

---

## Keeping the instructor materials separate

The `Instructor-Only/` folder is **never pushed to the public repo**.
It lives on your local machine and holds:

- Master cheatsheet (instructor's copy, with answers)
- Answer keys for each lab
- `findings-import.md` (your test-run findings, used to pre-load
  dossier examples for the live demos)
- Teachable-moments log (what went wrong in past runs, what to
  prepare for)
- Timing and pacing notes (where you tend to run long)
- Post-event write-up template

Use `.gitignore` (already configured) to enforce this boundary. Every
time you finish a class, update `Instructor-Only/` with what you
learned. Next instructor — future you, or someone you hand this to —
benefits.

---

## Workshop pedagogy — what's load-bearing

If you're tempted to rip out or restructure big chunks, preserve
these load-bearing elements:

1. **Two tiers, one class.** Hunter → Ghost graduation via preview
   challenges. This keeps everyone in the same room pacing and
   avoids the "advanced track / beginner track" split that fragments
   small classes.
2. **Passive-only scope discipline.** Every module has the active
   line clearly drawn. Don't blur it to save time.
3. **Admiralty rating on every finding.** The rating discipline IS
   the lesson. Don't ship a class that doesn't require ratings.
4. **Section 8 (Footprint Self-Audit) is non-negotiable.** This is
   the thing that separates a class output from a hobbyist dossier.
5. **Mirrors as professional technique, not training wheels.** Frame
   them as how real ops work, not as "the API is broken today."
6. **Shout-outs, no prizes.** The room is sharing learnings, not
   competing for trinkets.

---

Good luck with your next class.
