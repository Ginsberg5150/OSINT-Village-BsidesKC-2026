# Lab — Module 1 — 🟠 Ghost
## Identify Caterpillar's footprint — automated, audited, and complete

**Time budget:** 30 minutes (10:50–11:20)
**Pairs with:** `Class-Modules/Module-1-Identify.md`

---

## Pre-flight

- [ ] Pre-flight checklist green
- [ ] You've reviewed `Class-Modules/Module-1-Identify.md` and
      `Tools-and-Scripts/README.md`

---

## Open objective

Produce a complete Org Footprint section for Caterpillar Inc. with:

- The **complete** Exhibit 21 subsidiary list (not a sample), with
  jurisdictional clustering observed
- The **complete** Properties section data, structured for
  `plants_to_kml.py` consumption later
- A 4-state classification for **at least three** historical
  acquisitions, each verified via the redirect+EDGAR cross-check
- USASpending parent-recipient + sub-recipient hierarchy mapped to
  CAT operating segments

Plus: an audit comparing your manual results against
`domain_to_org.py`'s automated output, with at least one documented
finding the script missed (or that you missed).

---

## Suggested attack paths

You don't need to do all of these. Pick the ones that match your
strengths and the time you have.

### Path A — Automate Steps 1–3, audit the output

```bash
python3 Tools-and-Scripts/domain_to_org.py caterpillar.com \
    --output cat-org.json --verbose
```

Then independently verify a sample of the script's findings:
- Pick 5 subsidiaries from the script's output
- For each, verify the jurisdiction matches the Exhibit 21 source
- Check whether the script picked up the most recent 10-K or got
  cached on an older one
- Document any miss/extra in your dossier's Section 8

### Path B — Cross-jurisdiction sweep via OpenCorporates

EDGAR's Exhibit 21 captures U.S.-disclosed subsidiaries. For
international entities, OpenCorporates often holds richer data.

```
https://opencorporates.com/companies?q=caterpillar
```

For each foreign jurisdiction (Luxembourg, Ireland, UK, Singapore),
pull the local entity records. Cross-reference with Exhibit 21 — is
there an entity in OpenCorporates that *isn't* in Exhibit 21?
Either it's below the SEC's reporting threshold, or it's been
restructured. Either way it's a finding.

### Path C — Acquisition deep dive (3+ acquisitions, full history)

Pick three Caterpillar acquisitions across decades:
- One recent (last 5 years)
- One middle-aged (5–15 years)
- One old (15+ years)

For each, perform the full 4-state verification:
1. `curl -sI` redirect check on the acquired company's domain
2. EDGAR Exhibit 21 cross-check (current and at acquisition+1)
3. 8-K filings around acquisition / divestiture
4. Wayback Machine snapshot of acquired company's site at
   acquisition+1, +5 years (where available)

Output a table:
```
| Acquisition | Year | Domain | Redirect | Exhibit 21 status | State |
|-------------|------|--------|----------|-------------------|-------|
```

The **age dimension** is what makes this Ghost work — old absorbed
subsidiaries often left infrastructure that's still partially live
(Wayback-only sites, dormant DNS records, abandoned subdomains
that show up in CT logs). These are recon goldmines for Module 2.

### Path D — USASpending API automation

```bash
# The endpoint per the QA spec
curl -s -X POST 'https://api.usaspending.gov/api/v2/search/spending_by_category/awarding_agency/' \
  -H "Content-Type: application/json" \
  -d '{"filters":{"recipient_search_text":["Caterpillar"],"time_period":[{"start_date":"2024-01-01","end_date":"2026-04-25"}]}}' | jq
```

Walk the JSON. Build a table of agency → award amount → time period.
Identify which CAT operating subsidiaries the awards flow through —
Caterpillar Defense, Solar Turbines, Caterpillar Marine, etc. Each
contracting child is a potential Module 2 enumeration target you'd
otherwise miss.

---

## Automation prompt

If you script anything in this lab, the script should:

- Take `caterpillar.com` as input (target-agnostic, not hardcoded)
- Output structured data (JSON or CSV), not just stdout text
- Cite source URLs in the output
- Include retrieval timestamps
- Handle the EDGAR rate-limit politely (jittered sleeps, retry on 429)
- Save raw responses to a `raw/` subdirectory for audit

If you produce something useful and reusable, mention it in the
shout-out segment at 15:40.

---

## Deliverable

Add a richer Section 2 to your dossier than the Hunter version:

```markdown
## 2. Org Footprint

**Parent:** Caterpillar Inc. (Delaware) [A1, EDGAR CIK ####]

**Operating subsidiaries (complete from Exhibit 21):**
[Full table or list — could be 100+ entries]

**Jurisdictional clustering:**
- Delaware: N entities
- Luxembourg: N entities
- Ireland: N entities
- Singapore: N entities
- … (significance and notes)

**Manufacturing footprint (full Properties section):**
[Structured CSV-format list, ready for plants_to_kml.py]

**Acquisition history (3 verified):**
[Table with state classification, redirect evidence, citation]

**Federal contracting structure:**
[Mapped: agency → CAT operating subsidiary → contract value → period]

**Discrepancies between manual and automated (`domain_to_org.py`):**
[Specific findings, both directions]

**Sources & methodology:** [extensive]
```

---

## Bonus — RFC1918 / cloud-region preview

If you're done with all of the above and want to set up Module 2:
grep your subdomain enumeration sources (subfinder output, crt.sh
JSON, etc.) for hostnames containing:

- `10.`, `172.16-31.`, `192.168.` (RFC1918 leaks)
- `aws-`, `gcp-`, `azure-`, region codes (`us-east-1`, `eu-west-2`)
- Environment tells: `dev-`, `stg-`, `qa-`, `uat-`, `prod-`

Anything you spot becomes a high-value Module 2 deliverable. Note
them now; you'll formally document them in Module 2.

---

## Done?

Move to `Class-Modules/Module-2-Passive-Enumeration.md` whenever
you're ready. Module 2 starts at 11:20 — if you're early, start the
subfinder run; it takes a few minutes.
