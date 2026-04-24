# Module 1 — Identify
## Who is Caterpillar, really?

**Time budget:** 60 minutes (10:20–11:20)
**Prereqs:** Pre-flight checklist green; `Target-Briefs/Target-Caterpillar.md` read
**Pairs with:** `Student-Labs/Lab-Module-1-Hunter.md`, `Student-Labs/Lab-Module-1-Ghost.md`

---

## Hook

> LinkedIn says Caterpillar has about 109,000 employees.
> That's not the whole org. That's not even half.

By the end of this module you'll have mapped Caterpillar's actual
corporate footprint — the parent, the operating subsidiaries, the
brand portfolio, the M&A history, and the federal contracting layer
the LinkedIn page never mentions.

---

## Learning objectives

By the end of Module 1 you can:

1. Distinguish corporate, brand, and legal identity for a Fortune 100
2. Read a 10-K like an investigator (not an investor)
3. Pull Exhibit 21 — the SEC-mandated subsidiary disclosure
4. Read M&A history with the **4-state verification gate** applied
5. Use USASpending.gov to reveal federal contracting structure
6. Build an org graph with cited sources for every node

---

## Talk topics

### 1. Corporate ≠ brand ≠ legal entity

Three different things, three different search spaces.

- **Corporate:** the holding entity (e.g., "Caterpillar Inc.")
- **Brand:** what the public calls them ("CAT" — also `cat.com`)
- **Legal entity:** what shows up in court records, contracts, regulatory
  filings ("Caterpillar Inc. (Delaware)", "Solar Turbines Incorporated",
  "Progress Rail Services Corporation")

Recon hits different surfaces depending on which identity you're
chasing. SEC filings use legal names. Regulator databases use legal
names. News articles use brand names. Court records use legal names.
Your subdomain enumeration will mix all three plus DBAs (Doing-Business-As)
and historical names.

### 2. The 10-K is a confession

Read it like an investigator, not an investor. Three sections matter
most for Module 1:

- **Business** — what they do, by segment. Tells you their world.
- **Risk Factors** — what they're afraid of. Tells you their attack
  surface from their own perspective. Read it for the things they
  *don't* mention as much as the things they do.
- **Properties** — physical locations, owned vs. leased, square footage.
  This is your input to Module 4's KML deliverable.

For Caterpillar specifically, the 10-K also has a **Segment Reporting**
section that breaks revenue down by operating division — Construction
Industries, Resource Industries, Energy & Transportation, Financial
Products. Each segment maps to subsidiaries and brand domains you'll
enumerate in Module 2.

### 3. Exhibit 21 — the org chart the SEC demands

Every public company files Exhibit 21 alongside their 10-K. It lists
every subsidiary the company is required to disclose. Almost nobody
reads them.

For Caterpillar, Exhibit 21 contains organizations like:
- Solar Turbines Incorporated
- Progress Rail Services Corporation
- Caterpillar Financial Services Corporation
- Caterpillar Industrial Inc.
- (… and roughly 200 more entries across multiple jurisdictions)

You'll read it live in the demo. What jumps out is the *jurisdictional
diversity* — Delaware, Luxembourg, Ireland, Singapore. That's tax
structure speaking. From an OSINT perspective, each foreign entity has
its own corporate registry, its own court records, its own regulatory
exposure.

### 4. M&A as inherited attack surface — and the 4-state verification gate

When a company acquires another company, they inherit the acquired
company's infrastructure, employees, and *security posture*. M&A
history is core scoping material.

But — and this is the QA fix this module incorporates — **acquired
domains exist in four states, not two.** Before you spend any time
enumerating an acquired company's subdomains, verify which state it's in:

| State | What it means | Recon implication |
|-------|---------------|-------------------|
| **Absorbed** | Acquired company's infrastructure folded into parent | Enumerate against the *parent* domain; acquired domain may redirect |
| **Independent** | Still operating as a subsidiary with own infrastructure | Enumerate the acquired domain separately as a real surface |
| **Sunset / legacy** | Domain still exists but content is archive-only | Wayback Machine is your friend; live enumeration yields little |
| **Divested** | Sold off; no longer part of the parent | **Don't enumerate** — wasted effort, wrong target |

The verification gate, before you enumerate any acquired domain:

```bash
# Check redirect target
curl -sI https://acquired-domain.com | grep -i location

# If it redirects to the parent, it's likely Absorbed.
# If it resolves and serves its own content, likely Independent.
# If it 404s or serves only old content, likely Sunset.
# If it redirects to a different parent or returns NXDOMAIN, likely Divested.
```

Cross-check against EDGAR — if the acquired company still appears in
Exhibit 21, it's not Divested. If it's gone from Exhibit 21, check the
8-K filings around the disposition for the divestiture confirmation.

### 5. USASpending.gov — the contractor view

For any organization that sells to the U.S. federal government,
USASpending.gov reveals contract awards by agency, by amount, by
period. The view is structured differently than the 10-K and often
exposes operating divisions you wouldn't see otherwise.

The endpoint to learn:
```
https://api.usaspending.gov/api/v2/search/spending_by_category/awarding_agency/
```

For Caterpillar, this lights up. Federal contract awards across
multiple agencies, multiple operating subsidiaries, multiple years.
Each award maps to a real operating division doing real work for the
government — which is recon-relevant intelligence the 10-K summarizes
but doesn't itemize.

**Note on SAM.gov:** Older syllabi and many tutorials send you to
SAM.gov's public entity search. Per the QA review on this workshop,
SAM.gov's entity-search endpoint returns inconsistent cross-query
results and shouldn't be relied on. **Use USASpending.gov instead.**

### 6. Building the org graph

By the end of this module you should have, on paper or in a notes
file, a graph that looks roughly like:

```
Caterpillar Inc. (parent, Delaware)
├── Solar Turbines Incorporated (subsidiary, Delaware)
├── Progress Rail Services Corporation (subsidiary, Alabama)
├── Caterpillar Financial Services Corp. (subsidiary, Delaware)
├── Cat Reman (DBA, internal segment)
├── [acquired companies: Bucyrus 2011 (absorbed), …]
├── [foreign entities: Caterpillar (UK) Ltd, Caterpillar SARL Luxembourg, …]
└── [federal contracting view: agencies awarding contracts to CAT entities]
```

Every node has a citation. Every edge has a citation. This is the
input to Module 2's enumeration phase — you can't enumerate what you
haven't identified.

---

## Live demo (instructor, ~15 minutes)

These steps run live during the lecture. Students follow along on
their own machines.

### Step 1 — EDGAR Full-Text Search

```
https://efts.sec.gov/LATEST/search-index?q=%22Caterpillar+Inc%22&forms=10-K
```

Pull the most recent 10-K. Open the filing index. Note the path
structure (this is what `domain_to_org.py` will hit programmatically).

### Step 2 — Open Exhibit 21

Inside the most recent 10-K filing, find the exhibit named
`ex21*`, `exhibit21*`, or `subsidiar*` (variation per filing).
Open it. Read out a few entries. Note the jurisdictional diversity.

### Step 3 — Properties section

In the 10-K main document, find the Properties section (typically
Item 2). Note the structure: principal manufacturing facilities by
country and segment. **Save this list** — Module 4 turns it into a
KML file.

### Step 4 — USASpending search

```
https://www.usaspending.gov/recipient/
```

Search for "Caterpillar". Note the parent recipient view, the
sub-recipient awards, the agencies, the dollar amounts. Discuss
what the structure tells you about which CAT subsidiaries do
federal work.

### Step 5 — Acquisition verification (4-state demo)

Pick one historical Caterpillar acquisition — Bucyrus International
(2011) is a clean example. Verify what state the `bucyrus.com` domain
is in today using the `curl -sI` redirect check. Discuss what the
result tells you about whether to enumerate that domain in Module 2.

### Step 6 — Build the live whiteboard graph

Sketch the org graph live. Parent at the top. Operating subsidiaries
as branches. Federal-contracting view as a side panel. Foreign
entities as a separate cluster. **Cite the source for every edge.**

---

## Mirror-fallback notes

EDGAR is generally robust under classroom load — no mirror needed.
USASpending.gov is also robust. If either returns 5xx during your lab,
try again in 60 seconds; persistent failures should be reported to
the instructor.

---

## Lab assignments

Open the lab file matching your tier:

- 🔵 Hunter: `Student-Labs/Lab-Module-1-Hunter.md`
- 🟠 Ghost: `Student-Labs/Lab-Module-1-Ghost.md`

You have 30–35 minutes. Module 2 starts at 11:20.

---

## Transition to Module 2

> Now we know who Caterpillar is.
> Let's see what they have exposed.

Module 2 takes the org graph you just built and turns it into a list
of subdomains, IPs, ASNs, and exposed services — using only sources
that don't touch Caterpillar's infrastructure.

Open `Class-Modules/Module-2-Passive-Enumeration.md` when you're
ready.
