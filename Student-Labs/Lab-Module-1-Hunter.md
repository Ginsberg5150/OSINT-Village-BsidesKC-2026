# Lab — Module 1 — 🔵 Hunter
## Identify Caterpillar's footprint

**Time budget:** 30 minutes (10:50–11:20)
**Pairs with:** `Class-Modules/Module-1-Identify.md`

---

## Pre-flight

- [ ] Pre-flight checklist still green (`Student-References/Pre-Flight-Checklist.md`)
- [ ] Notes file open with target name + first timestamp
- [ ] Module 1 lecture concepts reviewed (you'll cite them by name)

---

## Core objective

By the end of this lab you will have, in your notes file:

1. The CIK number for Caterpillar Inc. on EDGAR
2. A list of at least **5 Caterpillar subsidiaries** from the most
   recent Exhibit 21
3. A list of at least **3 plant locations** with addresses from the
   10-K Properties section
4. The 4-state classification for at least **one historical Caterpillar
   acquisition** (your choice — Bucyrus, ERA Mining, Trimble's
   construction unit, etc.)
5. Confirmation of CAT's federal contracting presence via USASpending

Every finding gets an Admiralty Code tag.

---

## Step-by-step

### Step 1 — Find Caterpillar on EDGAR (3 min)

Open the EDGAR full-text search:
```
https://efts.sec.gov/LATEST/search-index?q=%22Caterpillar+Inc%22&forms=10-K
```

Or the regular search UI:
```
https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company=caterpillar&type=10-K
```

**In your notes:**
- CIK number for Caterpillar Inc.: ____________
- URL of the most recent 10-K filing index: ____________
- Date of most recent 10-K: ____________
- Admiralty rating for everything from EDGAR: **A1** (primary federal filing)

### Step 2 — Pull Exhibit 21 (5 min)

In the most recent 10-K filing index, find the exhibit named like
`ex21*`, `exhibit21*`, or `subsidiar*`. Click it open.

**In your notes, list at least 5 subsidiaries** with:
- Subsidiary name
- Jurisdiction (Delaware, Luxembourg, etc.)
- Admiralty rating (will be A1 for all of these)

Example format:
```
Solar Turbines Incorporated — Delaware [A1, Exhibit 21, 2025 10-K]
Progress Rail Services Corporation — Alabama [A1, Exhibit 21, 2025 10-K]
…
```

### Step 3 — Properties section (5 min)

In the main 10-K document (not Exhibit 21), find Item 2 — Properties.

**In your notes, capture at least 3 plant locations** with:
- Facility name (or city if name not given)
- Full address (or city + state if address not given)
- Segment (Construction Industries, Resource Industries, Energy &
  Transportation, Financial Products)
- Owned vs. leased status
- Square footage if listed
- Admiralty rating

**Save this list separately too** — Module 4 will turn it into a KML
file. Copy it into `cat-plants.csv` with columns:
`name,address,segment,notes`.

### Step 4 — One acquisition, fully verified (8 min)

Pick one historical Caterpillar acquisition. Suggested candidates
(easiest first):

- **Bucyrus International** (acquired 2011) — large, well-documented
- **ERA Mining Machinery** (acquired 2012) — has a story you'll find
- **Solar Turbines** (acquired 1981) — very old, mostly absorbed

For your chosen acquisition, perform the **4-state verification**:

```bash
# Check redirect target on the acquired company's domain
curl -sI https://bucyrus.com 2>&1 | grep -i location
```

Cross-check on EDGAR — does the acquired company still appear in
Exhibit 21 you pulled in Step 2?

**In your notes:**
- Acquired company: ____________
- Year acquired: ____________
- Domain checked: ____________
- Redirect target (if any): ____________
- Appears in current Exhibit 21? Yes / No
- **State classification:** Absorbed / Independent / Sunset / Divested
- Reasoning for classification (1 sentence)
- Admiralty rating: B2 or A1 depending on how confident you are in
  the redirect+EDGAR cross-check

### Step 5 — USASpending federal contracts (5 min)

Open USASpending recipient search:
```
https://www.usaspending.gov/recipient/
```

Search for "Caterpillar". Look at the parent recipient, sub-recipient
awards, awarding agencies, and dollar amounts.

**In your notes:**
- Total federal contracts to Caterpillar entities (TTM or all-time):
  $____________
- Top 3 awarding agencies: ____________
- Notable subsidiary names appearing in award data that don't appear
  in your Exhibit 21 list: ____________
- Admiralty rating: **A1** (primary federal data)

### Step 6 — Sketch the org graph (4 min)

On a piece of paper or in your notes, sketch:

```
Caterpillar Inc. (parent, Delaware)
├── [subsidiary 1 from Step 2]
├── [subsidiary 2]
├── [subsidiary 3]
├── [subsidiary 4]
├── [subsidiary 5]
├── [acquisition from Step 4 — note its 4-state classification]
└── [federal contracting view: top agencies from Step 5]
```

**Cite every node.** Every edge gets a source URL or filing
reference.

---

## Deliverable

Add a new section to your dossier file:

```markdown
## 2. Org Footprint

**Parent:** Caterpillar Inc. (Delaware) [A1, EDGAR CIK ####]

**Operating subsidiaries (sample of N from Exhibit 21):**
- Solar Turbines Incorporated (Delaware) [A1, Exhibit 21, 2025 10-K]
- Progress Rail Services Corporation (Alabama) [A1, Exhibit 21]
- … (your list)

**Manufacturing footprint (sample from 10-K Properties):**
- East Peoria, IL — Construction Industries — owned [A1, 10-K Item 2]
- … (your list)

**Notable acquisition (verified):**
- Bucyrus International (2011): **Absorbed** — bucyrus.com redirects
  to caterpillar.com/.../mining; entity does not appear in current
  Exhibit 21 [A1, EDGAR + redirect check]

**Federal contracting:** $X.XX in awards across N agencies (USASpending,
TTM as of YYYY-MM-DD) [A1]

**Sources:**
- EDGAR filing index: [URL]
- Exhibit 21: [URL]
- 10-K Properties section: [URL]
- USASpending recipient view: [URL]
```

---

## 🟠 Ghost preview challenge — try this if you finish early

**Run `Tools-and-Scripts/domain_to_org.py` against caterpillar.com**
and compare its output to what you produced manually.

```bash
python3 Tools-and-Scripts/domain_to_org.py caterpillar.com
```

The script automates Steps 1–2. Compare:
- Did the script find subsidiaries you missed?
- Did you find subsidiaries the script missed?
- Where the lists differ, *which one is right*?

**In your notes, document one finding in either column.** That's the
Ghost-tier work — knowing not just how to run a tool but how to audit
its output against ground truth.

---

## Common gotchas

- **EDGAR rate-limits eventually.** If your queries start failing,
  wait 30 seconds. Don't retry in a tight loop.
- **Exhibit 21 filename varies.** Look for `ex21`, `exhibit-21`,
  `subsidiaries`, etc. The QA-fixed regex in `domain_to_org.py`
  handles the variation.
- **An acquisition you "remember from the news" might not be in
  Exhibit 21 anymore** — that's a Divestiture or absorption signal,
  not an error.

---

## Done?

Move to `Class-Modules/Module-2-Passive-Enumeration.md` when the
instructor calls Module 2. You can also keep working — there's no
"waiting for the bell" rule today.
