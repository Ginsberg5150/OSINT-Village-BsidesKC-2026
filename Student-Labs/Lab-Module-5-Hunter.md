# Lab — Module 5 — 🔵 Hunter
## Assemble the dossier

**Time budget:** 30 minutes (15:10–15:40)
**Pairs with:** `Class-Modules/Module-5-Report.md`

---

## Pre-flight

- [ ] Pre-flight green
- [ ] Findings from Modules 1–4 in your notes
- [ ] `Student-References/Admiralty-Code.md` reviewed one more time

---

## Core objective

Produce a single markdown dossier file (`cat-dossier.md`) with the
standard 8 sections, every claim Admiralty-rated, and a
footprint self-audit that honestly declares what you covered.

This is the portfolio artifact. **The dossier, not the findings, is
what a hiring manager would ask to see.**

---

## Step-by-step

### Step 1 — Create the skeleton (2 min)

Create `cat-dossier.md` with these 8 section headers:

```markdown
# Caterpillar Inc. — Corporate Recon Dossier

**Investigator:** [your name or handle]
**Date:** 2026-04-25
**Class:** BSides KC 2026 — OSINT Village
**Scope:** Passive-only; no active scanning of CAT-owned infrastructure;
          no individual-employee aggregation.

---

## 1. Executive Summary
[3 bullets — fill in LAST, but the structure is here now]

## 2. Org Footprint
[from Module 1]

## 3. Domains & IP Space
[from Module 2]

## 4. Tech Stack & Exposed Services
[from Modules 2, 3, 4]

## 5. People & Roles
[patterns only — no individual names]

## 6. Physical & Regulatory
[from Module 4]

## 7. Notable Findings
[3–5 "so what" findings, highest-leverage discoveries]

## 8. Footprint Self-Audit
[what you searched, what you didn't, why]
```

### Step 2 — Fill sections 2–6 from your notes (10 min)

Copy your findings from Modules 1–4 into the corresponding sections.
For each claim, check:

- [ ] Is there a source URL or filing reference?
- [ ] Is there an Admiralty rating in `[Letter Number]` format?
- [ ] Is there a retrieval timestamp somewhere (at least in the
      section or the Sources subsection)?

If any finding fails this check, either fix it or move it to
Section 8 as "flagged for follow-up."

### Step 3 — Write Section 5 (People & Roles) carefully (3 min)

Scope reminder: **patterns only.**

Good Section 5 line:
```
CAT engineering teams concentrate in Peoria, IL area based on
~N LinkedIn profiles observed by searching "Caterpillar" with
location filter "Peoria-Area" (LinkedIn Private Mode session,
YYYY-MM-DD) [B2]. No individual names or emails recorded per
workshop scope.
```

Bad Section 5 line (don't write this):
```
Jane Doe is a Senior DevOps Engineer at CAT. Her email is
jane.doe@caterpillar.com.
```

### Step 4 — Write Section 7 (Notable Findings) (5 min)

3–5 findings. Each one a "so what" — something a reader can act on.

Pattern:
```markdown
### Finding 1: [short title]
**Finding:** [one-sentence claim]
**Evidence:** [citation, source URL, Admiralty rating]
**Implication:** [what this means for a stakeholder]
**Recommended follow-up:** [what to do next]
```

Examples of what a notable finding looks like:
- "CAT's TXT record vendor map reveals SaaS spend concentrated in
  [N vendors]; two of those vendors have had public breaches in
  past 12 months — TPRM follow-up warranted."
- "N% of CAT subdomains resolve to Akamai, but M critical ones
  ([list]) resolve to CAT-owned IPs — the non-Akamai surface is
  disproportionately concentrated in [pattern]."
- "CAT's Exhibit 21 lists [N] Luxembourg entities, suggesting
  [tax/structural reason]; this is relevant to [anyone doing M&A
  diligence on CAT]."

### Step 5 — Write Section 8 (Footprint Self-Audit) (5 min)

This is the new part (QA-flagged). Cover:

- **Sources searched** (list with bullet points):
  - EDGAR: full-text + filing index
  - USASpending: recipient search
  - crt.sh / subfinder / amass (or mirrors as fallback)
  - DNS: TXT/MX/NS/SPF enumeration
  - Shodan InternetDB (keyless)
  - EPA Envirofacts
  - Google Patents
  - (the rest of what you used)

- **Sources you skipped and why:**
  - Sock-puppet-required sources skipped per scope
  - VirusTotal skipped — no API key available, keyless mode
  - Individual-employee LinkedIn lookups skipped per scope
  - Active scanning skipped per scope

- **Failures encountered:**
  - crt.sh returned 502 at [timestamp], fell back to
    `Mirrors/crtsh/caterpillar.json` (snapshot 2026-04-24)
  - recon-ng module X hit captcha, module Y returned 0 results
  - …

- **Coverage estimate:**
  - "Subdomain enumeration via N sources agreed at [X]%, suggesting
    approximately [Y] complete."
  - "Physical footprint covers N of [M estimated] facilities;
    international facilities likely undercounted due to US-only
    regulator focus."

- **What I'd do next with more time:**
  - "Run additional aggregators (Censys certificate search, Certspotter)"
  - "Explore subsidiary `solar-turbines.com` as independent target"
  - "Deeper Wayback mining on historical-only hostnames"

### Step 6 — Write Section 1 (Executive Summary) (5 min)

**Now** write the summary. Three bullets. Plain English. No jargon.

Each bullet:
- States a finding or a conclusion
- Cites the primary source with Admiralty rating
- Enables a decision

Draft, read aloud, shorten. Read aloud again. The best executive
summaries fit in 3 sentences the reader can remember.

---

## Deliverable

Save `cat-dossier.md` somewhere you'll keep it. This is your
portfolio artifact. Email it to yourself or push it to a private
GitHub repo.

Also produce the KML file (Module 4 output) as a supporting
deliverable.

---

## 🟠 Ghost preview challenge

Run `domain_to_dossier.py` and compare its output to what you wrote
by hand:

```bash
python3 Tools-and-Scripts/domain_to_dossier.py caterpillar.com \
    --keyless --mirror-dir Mirrors/ \
    --output cat-dossier-auto.md
```

- Where does the automated output agree with yours?
- Where does it disagree, and who is right?
- Does your Executive Summary add value the automated output can't?
  (It should.)

Document one insight from this comparison in your final dossier
Section 8.

---

## Done?

Shout-outs start at 15:40. Bring your dossier open on your laptop —
you may be asked to share a finding.
