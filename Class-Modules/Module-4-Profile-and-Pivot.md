# Module 4 — Profile and Pivot
## Tech stack, people, physical, regulatory

**Time budget:** 50 minutes (14:15–15:05)
**Prereqs:** Modules 1–3 complete; subdomain + IP list in your dossier
**Pairs with:** `Student-Labs/Lab-Module-4-Hunter.md`, `Student-Labs/Lab-Module-4-Ghost.md`

---

## Hook

> This is where most courses stop at recon and start at investigation.
> Both halves matter.
> Watch what happens when you ignore the physical world on a target
> that builds machines for a living.

---

## Learning objectives

By the end of Module 4 you can:

1. Fingerprint a tech stack from public-facing pages (passive)
2. Pivot via favicon hashes — find every server in the world running
   the same app
3. Query EPA Envirofacts for environmental compliance data on CAT
   facilities
4. Read patent filings as R&D direction signal
5. Query corporate aircraft activity via FAA + ADS-B Exchange
6. Distinguish scriptable sources from **browser-only** sources
   (OSHA, FAA forms, FCC ULS — all browser exercises)
7. Output a KML file for leadership-grade geographic visualization

---

## Talk topics

### 1. Tech fingerprinting — the digital half

Three tools, different angles:

- **Wappalyzer** (browser extension) — instant readout of CMS, CDN,
  analytics, JS frameworks, ad tech on whatever page you're viewing.
  Click the extension icon, read the panel.
- **BuiltWith** (`https://builtwith.com/`) — single-domain free
  report. Historical stack changes and trends are paid. Free tier
  is enough for today.
- **whatweb** (CLI) — passive HTTP fingerprinting from the command
  line, no JS execution.

```bash
whatweb -a 1 https://www.caterpillar.com
```

The `-a 1` keeps it passive (level 1 aggression, no probing).

**Akamai caveat:** Caterpillar fronts much of its public surface with
Akamai. Many of these tools will return generic Akamai responses for
the public-facing properties. The workaround is to fingerprint
**less prominent subdomains** that may not be CDN-fronted —
investor-relations sites, legacy properties, regional dealer pages.
Your subfinder output from Module 2 is the input here.

### 2. Favicon hashes — the recon multiplier

This is one of the highest-leverage pivots in OSINT.

**The technique:** Hash a favicon with the Shodan algorithm
(`mmh3.hash` of the base64-encoded bytes). Search Shodan for that
hash. Get a list of every public-internet server in the world serving
that favicon.

**Why it's useful:** admin panels hidden behind weird hostnames
(`internal-portal-thing.example.com`) usually share their favicon
with the vendor's public marketing page. Hash the vendor page's
favicon → search Shodan → find every customer's "hidden" admin panel.

**The script:** `Tools-and-Scripts/favicon_pivot.py` does this end-to-end.

```bash
python3 Tools-and-Scripts/favicon_pivot.py https://www.caterpillar.com
```

Output:
```
Favicon hash: -1234567890
Shodan pivot URL: https://www.shodan.io/search?query=http.favicon.hash%3A-1234567890
Censys pivot URL: https://search.censys.io/search?resource=hosts&q=services.http.response.favicons.md5_hash%3D...
```

**Per QA fix:** the script now falls back to parsing
`<link rel="icon">` from the homepage HTML if `/favicon.ico` returns
404. Many modern sites don't serve a default-path favicon.

### 3. People pivots — passive, scope-respecting

For Caterpillar today, **people pivots are the most ethically
sensitive part of the day.** Re-read the three rules in the target
brief before this segment.

Tools and what they do:

- **LinkedIn** — read company pages and "people" view in Private
  Mode. Document patterns ("software engineering teams concentrate
  in Peoria and Mossville facilities"), not individuals.
- **GitHub** — search for org-affiliated repos. `caterpillar` as
  an org slug, plus subsidiary names (`solar-turbines`, `progress-rail`).
- **hunter.io** — email pattern detection. Returns the inferred
  pattern (`{first}.{last}@caterpillar.com`) and, on a free tier
  account, ~25 sample emails.
- **phonebook.cz** — passive WHOIS-adjacent contact info aggregator.

**Hard scope reminder:** for today, you document the *pattern*
(`first.last@caterpillar.com`, observed N times across M sources,
Admiralty B2). You do **not** record individual employee names in
your dossier.

### 4. EPA Envirofacts — the physical regulatory layer

The EPA's Envirofacts portal aggregates environmental compliance
data for every regulated facility in the U.S. Caterpillar's
manufacturing facilities are in there.

```
https://enviro.epa.gov/envirofacts/
```

You can search by facility name, address, or EPA ID. Useful queries
for CAT:

- Facility Registry Service (FRS) — every regulated CAT site
- Toxic Release Inventory (TRI) — what they emit, in what quantities,
  trended over years
- Enforcement and Compliance History (ECHO) — compliance status,
  inspections, violations, settlements

**For the dossier:** EPA data is `A1` source material — primary
federal regulatory disclosure. Cite the Envirofacts URL and the
retrieval timestamp.

**Caveat per QA:** EPA FRS data has ~20% non-geocodable rows
("PORTABLE SOURCE", highway intersections without numbers, building
codes like "BLDG LL"). The `plants_to_kml.py` script pre-filters
these. If you're working from raw EPA data manually, expect the
same noise.

### 5. OSHA, FAA, FCC ULS — browser-only sources

This is a QA-flagged technique correction: **OSHA, FAA, and FCC ULS
public search forms are session+CSRF-gated** and don't work cleanly
from scripts or curl. Headless requests get empty HTML. They're
real, useful sources — but they're **browser exercises**, not
scriptable ones.

For today:

- **OSHA Establishment Search** —
  `https://www.osha.gov/ords/imis/establishment.html` — search by
  company name, get inspection history, violations, citations,
  establishment size.
- **FAA Registry** — `https://registry.faa.gov/aircraftinquiry/` —
  search by company name, get tail numbers of registered aircraft.
  Cross-reference with **ADS-B Exchange** historical data
  (`https://globe.adsbexchange.com/`) for actual flight tracks.
- **FCC ULS** — `https://wireless2.fcc.gov/UlsApp/UlsSearch/searchLicense.jsp` —
  licensed wireless transmitters at facilities. Reveals industrial
  wireless backbones, paging systems, security comms.

**Open these in browser tabs.** Take screenshots. Cite the URL +
timestamp + your search term. These three sources together can
produce dossier findings the digital workflow will never surface.

### 6. Patents — R&D direction

Two sources, one currently-best choice:

- **Google Patents** (`https://patents.google.com/`) — searchable
  by assignee. No API key required. **This is the recommended default
  per QA fix** — USPTO's PatentsView API now requires a key.
- **USPTO PatentsView** (`https://api.patentsview.org/`) — primary
  source. Requires a key as of recent updates. Use if you have one;
  otherwise Google Patents covers the same ground.

For Caterpillar:
```
https://patents.google.com/?assignee=caterpillar+inc
```

What patent filings tell you: what the company is investing in
*next*. Patents lag R&D by 12–24 months but lead public product
launches by years. A spike in autonomous-mining patents in 2022
predicts product announcements in 2024–2025. Read the recent ones
to see where the company thinks the puck is going.

### 7. Supply chain — Panjiva, USITC, ImportGenius

For a manufacturer, customs and bill-of-lading data is fully public
and reveals supplier dependencies in ways the company never
discloses voluntarily.

- **Panjiva** (Hong Kong / India / global trade data)
- **ImportGenius** (US import records)
- **USITC DataWeb** (`https://dataweb.usitc.gov/`) — official US
  trade statistics

These have varying free tiers. For today: most have a free preview
that's enough to demonstrate the method. The *technique* is the
lesson; the depth is what a paid account would unlock.

### 8. The KML deliverable — visual layer for leadership

The output that makes recon work *legible* to non-technical
audiences. Take the plant address list you captured from the 10-K
Properties section in Module 1. Run it through `plants_to_kml.py`.
Open the result in Google Earth Pro.

```bash
# Assume you have plants.csv with: name,address,segment columns
python3 Tools-and-Scripts/plants_to_kml.py plants.csv \
    --output cat-plants.kml \
    --title "Caterpillar Inc. — Discovered Facilities"
```

**Per QA fix:** the script uses Census TIGER as the primary
geocoder (works without keys, US-only) with Nominatim as
international fallback (works with VPNs that aren't blocked by
OSM). It also pre-filters rows whose address doesn't match a
street-number regex, skipping the EPA noise rows.

Open the KML in Google Earth Pro. Pan, zoom, screenshot. Show the
result of the workshop in one image: a global map of every
Caterpillar manufacturing facility, color-coded by segment, sourced
entirely from public filings and run through three Python scripts.

That's the slide that wins the room in any executive briefing.

---

## Live demo (instructor, ~15 minutes)

### Step 1 — whatweb fingerprint

```bash
whatweb -a 1 https://www.caterpillar.com
```

Note Akamai. Discuss what that means for fingerprinting strategy.
Pivot to a less-prominent subdomain from your subfinder output.

### Step 2 — favicon hash + Shodan pivot

```bash
python3 Tools-and-Scripts/favicon_pivot.py https://www.caterpillar.com
```

Click the resulting Shodan URL in a browser. Discuss the result
set — how many other hosts share this favicon, what that tells you.

### Step 3 — EPA Envirofacts walk

```
https://enviro.epa.gov/envirofacts/
```

Search a known CAT facility city (East Peoria, IL). Walk the FRS
results. Open one facility's TRI report. Show what dossier-grade
findings look like at `A1` source quality.

### Step 4 — Browser-source quick tour

Open OSHA, FAA Registry, and FCC ULS in three browser tabs. Search
"Caterpillar" in each. Show the kind of result each produces (one
finding per source, screenshotted, cited).

### Step 5 — Google Patents

```
https://patents.google.com/?assignee=caterpillar+inc
```

Sort by date. Read the most recent three patent titles. Discuss
what they suggest about CAT's R&D direction.

### Step 6 — KML production

Run `plants_to_kml.py` on a small sample CSV (3–5 plants from the
10-K). Open the resulting KML in Google Earth Pro. **This is the
visual that lands the dossier with non-technical audiences.**

---

## Mirror-fallback notes

Most Module 4 sources are not classroom-load-fragile (EPA, FAA, FCC,
USPTO/Google Patents, BuiltWith). Shodan favicon search may
rate-limit if many students hit it simultaneously — there's no
mirror for that; wait 30 seconds and retry.

---

## Lab assignments

- 🔵 Hunter: `Student-Labs/Lab-Module-4-Hunter.md`
- 🟠 Ghost: `Student-Labs/Lab-Module-4-Ghost.md`

30 minutes. Module 5 starts at 15:05.

---

## Transition to Module 5

> You have findings.
> Now: how do you assemble them into something a stakeholder can act
> on?

Module 5 is the dossier — assembly, structure, rating, and
self-audit. Short module, important module. The discipline you
learn in the next 35 minutes is what hiring managers actually want
to see in a portfolio.

Open `Class-Modules/Module-5-Report.md`.
