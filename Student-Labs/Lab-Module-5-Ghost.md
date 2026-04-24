# Lab — Module 5 — 🟠 Ghost
## Produce a leadership-grade dossier

**Time budget:** 30 minutes (15:10–15:40)
**Pairs with:** `Class-Modules/Module-5-Report.md`

---

## Pre-flight

- [ ] Pre-flight green
- [ ] Rich findings from Modules 1–4 (deeper than Hunter tier)

---

## Open objective

Produce **three correlated deliverables**:

1. `cat-dossier.md` — markdown dossier, 8 sections, Admiralty-rated
2. `cat-plants.kml` — geographic visualization
3. `cat-dossier.json` — machine-readable structured data for
   downstream tooling

Plus: write the kind of Executive Summary a CISO would forward
unedited.

---

## Suggested attack paths

### Path A — Start with the executive summary, work backwards

Write Section 1 first. Three bullets. Each one a decision enabler.

Then build Sections 2–8 as **evidence-support structure** for the
summary. Any content that doesn't support a summary bullet goes in
Section 8 as "considered but not dispositive," or gets cut.

This is the most important skill of the day. It forces ruthless
prioritization and produces consistently better dossiers than the
"collect everything, summarize last" approach.

### Path B — Full correlation across modules

A mature dossier has cross-section references:

- Section 7 Finding: "Cross-match between Section 2 (Exhibit 21
  subsidiaries), Section 3 (subdomain enumeration), and Section 6
  (EPA FRS registered facilities) reveals that acquired subsidiary
  [X] still operates independent infrastructure, with [N] DNS
  subdomains and [N] EPA-registered sites — meaning the 'absorbed'
  classification in Section 2 may be incomplete."

These are the findings that require running the full 8-section
analysis to surface. They're what Ghost tier produces that Hunter
tier can't.

### Path C — Run `domain_to_dossier.py` and extend the output

```bash
python3 Tools-and-Scripts/domain_to_dossier.py caterpillar.com \
    --keyless --mirror-dir Mirrors/ \
    --output cat-dossier-base.md \
    --json cat-dossier-base.json
```

The script produces a structurally complete but narratively thin
dossier. Your job: add the narrative value.

- Copy the base into `cat-dossier.md`
- Add Section 1 (Executive Summary) — the script can't write this
- Add Section 7 (Notable Findings) — the script identifies data but
  doesn't interpret it
- Expand Section 8 (Footprint Self-Audit) — the script emits a
  default; enrich it with what you specifically did differently
- Cross-reference across sections (Path B)

### Path D — Produce the JSON + downstream pipeline

```bash
python3 Tools-and-Scripts/domain_to_dossier.py caterpillar.com \
    --keyless --mirror-dir Mirrors/ \
    --json cat-dossier.json
```

Then use `jq` to produce derivative artifacts:

```bash
# Top 10 most-exposed IPs by open-port count
jq '.sections["3_domains_ip"].ips | sort_by(.open_ports | length) | reverse | .[0:10]' \
   cat-dossier.json

# All Admiralty-A findings (the high-confidence core)
jq '.. | objects | select(has("admiralty")) | select(.admiralty | startswith("A"))' \
   cat-dossier.json
```

These derivative views are what downstream dashboards consume. Ship
one or two as extra deliverables.

### Path E — Build a slide from the dossier

Take the finished markdown + KML and produce a single slide a CISO
could show in a 10-minute executive briefing:

- One-bullet-per-section takeaway (8 lines)
- KML screenshot as the visual
- Admiralty-rated findings at the bottom right

This is the end state of corporate recon. The dossier feeds the
deck; the deck changes a decision.

---

## Deliverable

Your deliverable set for shout-outs:
- `cat-dossier.md` (the narrative)
- `cat-plants.kml` (the visual)
- `cat-dossier.json` (the data, if you generated it)
- Optionally: a derivative query result or a single-slide summary

If you produced anything the room would benefit from (automation,
a pattern you spotted, a tool gap), raise your hand at shout-outs.

---

## Done?

Shout-outs at 15:40. Bring your dossier on your laptop —
if you want to share a finding, raise your hand and read the
Notable Finding out loud.
