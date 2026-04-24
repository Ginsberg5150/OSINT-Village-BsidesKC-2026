# Module 5 — Report
## Assemble the dossier, rate every finding

**Time budget:** 35 minutes (15:05–15:40)
**Prereqs:** Modules 1–4 complete; raw findings captured in your notes
**Pairs with:** `Student-Labs/Lab-Module-5-Hunter.md`, `Student-Labs/Lab-Module-5-Ghost.md`

---

## Hook

> A 200-finding dossier with no ratings is a liability.
> A 20-finding dossier, rated and cited, is a professional product.

This is the module that separates a hobbyist from a hire.

---

## Learning objectives

By the end of Module 5 you can:

1. Structure a dossier into the standard 8 sections
2. Apply Admiralty Code ratings to every claim
3. Write the executive summary *first*, then assemble evidence to
   support it
4. Add a **footprint self-audit** — what you searched, what you
   chose not to search, why
5. Recognize when to flag a finding for follow-up vs. drop it

---

## Talk topics

### 1. The standard 8-section structure

Every dossier you produce follows the same skeleton. Stakeholders
learn to read it; you learn to write it the same way every time.

```
1. Executive Summary           3 bullets, plain English, no jargon
2. Org Footprint               parent · subs · brands · M&A
3. Domains & IP Space          subdomains · ASNs · IP ranges (cited)
4. Tech Stack & Exposed Services
5. People & Roles              titles, locations, public handles —
                               PATTERNS, not individuals (today)
6. Physical & Regulatory       plants, EPA, OSHA, federal contracts
7. Notable Findings            the "so what" — high-value things
                               you'd brief a stakeholder on
8. Footprint Self-Audit        what you searched, what you didn't,
                               and why (today's QA-flagged addition)
```

Every section ends with a "Sources" subsection listing the citations
referenced. Every claim in the section body has an inline `[Letter
Number]` Admiralty tag.

### 2. Write the executive summary FIRST

This is counterintuitive. Most people write the summary last. They
shouldn't.

When you write the summary first, you're forced to commit to:
- What is the most important thing the reader needs to know?
- What action does this enable?
- Which 3 findings (out of 50+) earn space in the elevator pitch?

Then you assemble the rest of the dossier as **evidence supporting
the summary**. This produces sharper dossiers because every section
has a job: support the executive summary, or you cut it.

For Caterpillar today, your three executive bullets might look like:

```
1. Caterpillar Inc. operates 31 manufacturing facilities across 18
   states and 12 countries [A1, 10-K], with a federal contracting
   footprint of $X.XX over the trailing 12 months across N agencies
   [A1, USASpending].

2. The public-facing digital surface is heavily Akamai-fronted; key
   recon-leverage subdomains identified include [list] [A1, CT logs].

3. Notable supply-chain dependency on [supplier], visible via import
   bills of lading [B2, Panjiva, sample], representing [estimated
   significance].
```

Three bullets. Each cites primary sources. Each gives a stakeholder
something to act on.

### 3. Apply Admiralty ratings — discipline check

Re-read `Student-References/Admiralty-Code.md` if needed. The rule
for the dossier:

- **Sections 2–6 (the body):** every claim tagged `[Letter Number]`
- **Section 7 (Notable Findings):** ratings shown more visibly,
  often in their own column of a table
- **Section 8 (Footprint Self-Audit):** uses ratings to declare
  what wasn't found and how confidently you can claim absence

If a finding wants to be rated `D4` or worse, **it does not belong
in the main body**. Move it to Section 8 ("Flagged for follow-up:
this rumor / forum claim / unverified pattern needs a primary source
before it ships").

### 4. The footprint self-audit (Section 8) — what it covers

This is the QA-flagged addition that elevates a Hunter dossier into
a Ghost-quality one. Section 8 declares the *shape* of your
investigation, not the findings.

A complete Section 8 includes:

- **Sources searched:** every aggregator, every regulator, every
  passive scan database you queried
- **Sources skipped:** what you intentionally didn't query and why
  (e.g., "Sock-puppet-required sources skipped per scope")
- **Failure modes encountered:** which sources rate-limited, returned
  empty, or required keys you didn't have, and which mirrors you fell
  back to
- **Coverage estimate:** how confident you are this is a complete
  picture (e.g., "subdomain enumeration via subfinder + crt.sh
  agreed at 87% — the 13% delta is mostly Wayback-only historical
  hostnames that no longer resolve")
- **What you'd do next with more time:** the explicit handoff to
  whoever might continue this work

A reader who only reads Section 1 and Section 8 of a good dossier
should be able to make a confident decision about what to do next.

### 5. When to flag for follow-up vs. drop

Flag for follow-up when:
- The finding is plausibly important AND you have a concrete plan
  for how to upgrade its rating
- The finding contradicts something else in your dossier and the
  conflict matters
- You ran out of time on a thread that was producing real signal

Drop when:
- The finding is interesting but you have no path to evaluate it
- The finding is a single weak source (`D4` or worse) with no obvious
  way to corroborate
- The finding is gossip dressed up as research

The best dossiers are short. Cuts are virtues.

### 6. The deliverable formats

For today, your primary deliverable is a **markdown dossier** —
text, portable, diff-able, version-control-friendly.

Optional deliverables that level it up:

- **PDF export** of the markdown — for distribution to people who
  don't read markdown
- **KML file** (Module 4 output) — geographic visualization of
  physical findings, opens in Google Earth Pro
- **JSON output** from `domain_to_dossier.py` — machine-readable
  copy for downstream tooling

For Hunter tier today: just the markdown is plenty. For Ghost tier:
markdown + KML + JSON is the full leadership-grade deliverable set.

---

## Live demo (instructor, ~10 minutes)

### Step 1 — Open a sample assembled dossier

Instructor displays a pre-assembled CAT dossier (from the test run,
sanitized). Walk the 8 sections, top to bottom. Pause on Section 1
to demonstrate "summary first" discipline. Pause on Section 7 to
show how the headline findings are presented.

### Step 2 — Walk Section 8 (the new part)

Spend extra time on the footprint self-audit. This is the part most
attendees won't have seen before. Show how it transforms a "here's
what I found" into "here's what I found AND here's what I know about
what I might have missed."

### Step 3 — Run the dossier generator

```bash
python3 Tools-and-Scripts/domain_to_dossier.py caterpillar.com \
    --keyless \
    --mirror-dir Mirrors/ \
    --output cat-dossier.md \
    --json cat-dossier.json
```

Let it run. ~2 minutes. Open the markdown. Show the Admiralty
ratings on every section. Discuss what the script gave you for free
and what you'll add by hand (executive summary, notable findings
prose, footprint self-audit).

### Step 4 — Demo the KML overlay

Open the KML file in Google Earth Pro. Show what a leadership-grade
visual deliverable looks like.

---

## Lab assignments

- 🔵 Hunter: `Student-Labs/Lab-Module-5-Hunter.md`
- 🟠 Ghost: `Student-Labs/Lab-Module-5-Ghost.md`

30 minutes. Shout-outs and wrap at 15:40.

---

## Transition to Final Activity

> You have a dossier.
> Let's hear what surprised you.

Open `Final-Activity/Wrap-and-Shout-Outs.md`.
