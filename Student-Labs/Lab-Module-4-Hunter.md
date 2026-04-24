# Lab — Module 4 — 🔵 Hunter
## Profile and pivot — tech, physical, regulatory

**Time budget:** 30 minutes (14:35–15:05)
**Pairs with:** `Class-Modules/Module-4-Profile-and-Pivot.md`

---

## Pre-flight

- [ ] Pre-flight green
- [ ] Subdomain list from Module 2 in your notes
- [ ] Plant location CSV from Module 1 in your notes

---

## Core objective

By end of lab you have:

1. Tech stack fingerprint for `www.caterpillar.com` AND one
   non-public-facing subdomain
2. Favicon hash + Shodan pivot URL for a CAT property
3. At least **2 EPA Envirofacts findings** on CAT facilities
4. One patent filing reading (title + year + inference)
5. A **KML file** with at least 3 CAT plant locations rendered

Every finding Admiralty-rated.

---

## Step-by-step

### Step 1 — Tech fingerprint the main site (4 min)

```bash
whatweb -a 1 https://www.caterpillar.com
```

Also browse there with Wappalyzer extension open. Record what both
tools report.

**Expected:** Akamai fronting. Most stack tells will be generic.
That's a finding in itself.

**In your notes:**
- Main site: Akamai-fronted [A1, direct observation]
- Stack hints through Akamai: ____________

### Step 2 — Fingerprint a less-public subdomain (4 min)

From your Module 2 output, pick a subdomain that looks like an
investor-relations site, dealer portal, or regional property —
somewhere *less likely* to be fully CDN-fronted.

```bash
whatweb -a 1 https://<chosen-subdomain>
```

**In your notes:**
- Subdomain: ____________
- Stack: [CMS, JS frameworks, analytics, ad tech] [B2]

### Step 3 — Favicon pivot (5 min)

```bash
python3 Tools-and-Scripts/favicon_pivot.py https://www.caterpillar.com
```

Or against a subdomain that looks like a vendor admin panel.

**In your notes:**
- Favicon hash: ____________
- Shodan pivot URL: ____________
- (Click the URL) How many other hosts serve this favicon?

If the hash matches to CAT-owned hosts only, you've confirmed a
vendor/platform cluster. If it matches to many non-CAT hosts, the
favicon is a common third-party vendor's (e.g., a SaaS platform).

### Step 4 — EPA Envirofacts on CAT facilities (8 min)

Open `https://enviro.epa.gov/envirofacts/`. Use the Facility Search.

Search for Caterpillar facility cities from your Module 1 plant list
(East Peoria IL, Mossville IL, etc.).

For each facility found:
- Note the EPA Facility Registry System (FRS) ID
- Open the ECHO (Enforcement & Compliance History) link
- Record: inspection history, any violations, compliance status

**In your notes, capture at least 2:**

```
Facility: Caterpillar East Peoria, IL
- FRS ID: __________
- EPA programs: __________
- Compliance status: __________
- Violations in past 5 years: __________
- Admiralty: A1 (primary federal regulatory)
```

### Step 5 — One patent filing read (3 min)

```
https://patents.google.com/?assignee=caterpillar+inc&sort=new
```

Click the top result (most recent filing).

**In your notes:**
- Patent title: ____________
- Filing year: ____________
- What the patent suggests about CAT's R&D direction: ____________
- Admiralty: A1 (primary USPTO filing)

### Step 6 — Build the KML (6 min)

Take the plant list from Module 1. If you haven't already, make it
a CSV:

```bash
# cat-plants.csv
name,address,segment,notes
Caterpillar East Peoria,500 SE Adams St East Peoria IL 61611,Construction Industries,
Caterpillar Mossville,14009 Old Galena Rd Mossville IL 61552,Large Power Systems,
...
```

Generate the KML:

```bash
python3 Tools-and-Scripts/plants_to_kml.py cat-plants.csv \
    --output cat-plants.kml \
    --title "Caterpillar — Discovered Facilities (Hunter)"
```

Open in Google Earth Pro. Screenshot for your dossier.

**In your notes:**
- KML file path: ____________
- Plants geocoded successfully: ____________
- Plants that failed geocoding: ____________

---

## Deliverable

Add Section 6 to your dossier:

```markdown
## 6. Physical & Regulatory

**Manufacturing footprint (visual):** see `cat-plants.kml` — N
facilities across [states/countries]. [A1]

**EPA regulatory (sample of 2):**
- East Peoria, IL facility: FRS ID [id], ECHO compliance status
  [status], N violations in past 5 years. [A1]
- Mossville, IL facility: [similar]

**Patent R&D direction (sample):**
- Most recent patent title: "[title]" (filed YYYY). Suggests
  investment in [domain]. [A1]
- Cross-reference to public product announcements: [URL]

**Sources:** [list]
```

Section 4 (tech stack) gets your whatweb + favicon findings.

---

## 🟠 Ghost preview challenge

Run the favicon pivot on a CAT subdomain that looks like an admin
panel or login page. Walk the Shodan search results looking for
hosts **outside CAT** that share the favicon. If you find them,
they're usually the same vendor's product deployed at other
orgs — which can hint at what software is running on the CAT host.

Document one external match (other org running the same product)
in your dossier.

---

## Common gotchas

- **whatweb `-a 3` or `-a 4` is ACTIVE scanning.** Stick to `-a 1`
  for passive on CAT.
- **Google Patents sometimes lags** — a filing might be on USPTO
  direct but not yet on Google Patents. If you need the absolute
  latest, USPTO PatentsView (with a key) has the newest data.
- **KML geocoding will fail on some addresses** — that's the QA-
  flagged issue. Script pre-filters street-numbers-missing rows but
  some still slip through. Note failures in Section 8.

---

## Done?

Module 5 starts at 15:05.
