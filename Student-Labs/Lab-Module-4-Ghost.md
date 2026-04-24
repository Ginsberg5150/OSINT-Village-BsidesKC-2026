# Lab — Module 4 — 🟠 Ghost
## Profile, pivot, and correlate — the full physical surface

**Time budget:** 30 minutes (14:35–15:05)
**Pairs with:** `Class-Modules/Module-4-Profile-and-Pivot.md`

---

## Pre-flight

- [ ] Pre-flight green
- [ ] Module 2 subdomain + IP dataset in your notes
- [ ] Module 1 org graph and plant list in your notes

---

## Open objective

Produce a rich, correlated Section 6 (Physical & Regulatory) and a
complete Section 4 (Tech Stack & Exposed Services) that:

- Uses at least 4 different physical/regulatory sources (EPA, OSHA,
  FAA, FCC, USPTO/Google Patents, USITC/Panjiva, ADS-B Exchange)
- Correlates at least one finding across two independent sources
  (e.g., EPA facility address matches 10-K Properties listing)
- Produces a complete KML with *all* geocodable plants from your
  10-K list
- Notes which browser-only sources you used (OSHA/FAA/FCC) with
  screenshots cited

---

## Suggested attack paths

### Path A — Full physical/regulatory sweep

For every CAT facility in your Module 1 plant list, enrich with:

1. EPA Envirofacts FRS ID + ECHO compliance status
2. OSHA establishment search result (browser — screenshot)
3. Any state-level regulatory findings (state EPA equivalents,
   state labor departments)
4. Facility age / construction year (from 10-K or news archives)

Output: a table with one row per facility, one column per source,
joined on facility address. The correlation is the value — finding
address-mismatches or naming-inconsistencies surfaces either data
errors or legitimate operational details.

### Path B — Supply chain via customs / trade data

Panjiva and USITC DataWeb both expose bill-of-lading and customs
data. For a manufacturer like CAT, this reveals:

- Suppliers (who ships inputs TO CAT)
- Shipping routes
- Port-of-entry (which ports CAT uses most)
- Volume trends

Free tiers of Panjiva / ImportGenius are limited but usable for a
demonstration-quality finding. USITC DataWeb is fully free and
structured for research.

Document one non-obvious supplier relationship you can verify from
trade data.

### Path C — Corporate aviation trace

```
https://registry.faa.gov/aircraftinquiry/
# Search: Caterpillar
```

Record tail numbers. Then cross-reference to ADS-B Exchange:

```
https://globe.adsbexchange.com/?icao=<ICAO_code>
```

For each aircraft, ADS-B historical data shows where it has flown
in the past weeks/months. Patterns often reveal site visits, deal
activity, executive travel.

**Scope discipline:** This is publicly filed data that anyone with a
browser can retrieve. It is not surveillance. You're documenting
corporate aircraft movements, not individuals.

### Path D — Patent portfolio clustering

Instead of one patent, pull the last 50 CAT patent filings from
Google Patents or USPTO. Cluster by topic:

- Autonomous mining / haul trucks
- Battery electrification for heavy equipment
- Hydraulics / undercarriage
- Telematics / CAT Connect / digital services

The cluster distribution tells you CAT's R&D priorities by dollar
weight. A spike in any cluster is a strategy signal.

### Path E — Favicon-mining at scale

For every subdomain in your Module 2 list that looks like an
admin/portal/login page, run `favicon_pivot.py`. Build a
hash → vendor mapping. Several CAT subdomains sharing the same
favicon hash → same vendor platform → likely same app/vulnerability
class.

```bash
for sub in $(grep -iE '(admin|portal|login|dashboard)' cat-subs.txt); do
  echo "=== ${sub} ==="
  python3 Tools-and-Scripts/favicon_pivot.py "https://${sub}" 2>/dev/null | head -5
done
```

---

## Automation prompt

If you extend `plants_to_kml.py` to also pull EPA FRS data and
merge it into the KML, that would be **immediately useful** to
anyone doing corporate-recon work. Ghost work worth sharing at
shout-outs.

---

## Deliverable

```markdown
## 6. Physical & Regulatory

**Full facility enumeration:** N facilities across [states/countries],
sourced from [10-K + EPA FRS + OSHA + …]. See `cat-plants.kml`.

**Regulatory compliance snapshot (full table):**
[One row per facility: EPA status, OSHA inspection history, any
state-level findings]

**Corporate aviation (sample of N registered aircraft):**
| Tail # | Model | Pattern |
|--------|-------|---------|
| N###CAT | [model] | frequent trips to [cities] in past 90d |

**Patent portfolio direction (last 50 filings clustered):**
| Theme | Count | Trend |

**Supply chain signals (from trade data):**
- Notable port of entry: [city] (N% of observed imports)
- Notable supplier relationship: [vendor] (verified via [source])

**Sources used:** [extensive list with browser-only markers]

**Browser-only source screenshots:** [references to saved images]
```

---

## Done?

Module 5 at 15:05.
