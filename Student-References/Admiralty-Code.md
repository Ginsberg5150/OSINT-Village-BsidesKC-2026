# Admiralty Code · Rate every finding

**Every claim that goes in your dossier gets a two-character tag:
a letter for source reliability + a number for information credibility.**

Origin: NATO STANAG 2511. Adopted by intelligence services worldwide.
Used here because it forces you to evaluate, not just collect.

---

## The matrix

| Source reliability | Information credibility |
|---|---|
| **A** Completely reliable | **1** Confirmed by other independent sources |
| **B** Usually reliable | **2** Probably true |
| **C** Fairly reliable | **3** Possibly true |
| **D** Not usually reliable | **4** Doubtful |
| **E** Unreliable | **5** Improbable |
| **F** Reliability cannot be judged | **6** Truth cannot be judged |

Tag every finding `[Letter][Number]`. Examples: `A1`, `B2`, `D3`, `F6`.

---

## How to assign the letter (source reliability)

The letter is about the *source itself*, independent of the specific
claim being made.

**A — Completely reliable.** Primary documentary source. Legally compelled
disclosure. Direct sensor data. Examples: SEC EDGAR filings, court
records, government regulator databases (EPA, OSHA, FAA), the
target's own published audited financial statements.

**B — Usually reliable.** Established outlet with editorial oversight or
established vendor with reputational stake in accuracy. Examples:
Reuters, AP, Wall Street Journal, vendor security advisories, peer-reviewed
academic publications, established industry trade publications.

**C — Fairly reliable.** Industry press, sector-focused trade outlets,
major aggregators with curation. Examples: Heavy Equipment Guide,
Construction Equipment magazine, BuiltWith, Crunchbase, OpenCorporates.

**D — Not usually reliable.** Forums, social media posts, anonymous blogs,
content with low editorial bar. Examples: Reddit, Quora, individual blog
posts without attribution, anonymous Pastebin drops with stated context.

**E — Unreliable.** Known bad-faith sources. Disinformation outlets.
Sources with documented history of fabrication.

**F — Reliability cannot be judged.** New source, no track record,
anonymous and uncorroborated. Examples: a new Telegram channel, a
first-time poster on an obscure forum, an AI-generated article with
no clear publisher.

---

## How to assign the number (information credibility)

The number is about *this specific claim*, independent of the source.

**1 — Confirmed by other independent sources.** Two or more sources of
different origin agree. Independent here means *different lineage*, not
just different URLs — five news articles all citing the same press
release count as one source, not five.

**2 — Probably true.** Single source you trust, internally consistent
with everything else you know about the target.

**3 — Possibly true.** Single source, plausible, no contradiction.

**4 — Doubtful.** Single source, contradicts other things you've found,
no clear explanation for the conflict.

**5 — Improbable.** Multiple lines of evidence point the other way.

**6 — Truth cannot be judged.** Not enough information to evaluate.

---

## Worked examples on Caterpillar findings

| Finding | Source | Tag | Why |
|---------|--------|-----|-----|
| "CAT operates a plant in East Peoria, IL" | CAT 10-K Properties section | **A1** | Primary federal filing; confirmed by satellite imagery and Google Maps |
| "CAT acquired Solar Turbines in 1981" | CAT corporate history page | **B2** | Vendor's own history — usually reliable, no contradiction found |
| "CAT has 109,100 full-time employees" | CAT 10-K cover page | **A2** | Federal filing (A); single source for this number, no independent confirmation (2) |
| "CAT is moving production to Mexico" | LinkedIn post by industry blogger | **D3** | Forum-grade source, plausible but unconfirmed |
| "CAT's Building 12 has badge readers from XYZ vendor" | Anonymous Pastebin drop | **F6** | No way to evaluate the source; no way to verify the claim |
| "Subdomain `it.caterpillar.com` resolves to 12.34.56.78" | Direct DNS resolution today | **A1** | First-hand observation; confirmed by repeat lookup |

---

## What an Admiralty-rated dossier line looks like

```
Caterpillar maintains manufacturing operations in East Peoria, Illinois.
The facility is approximately 1,500 acres per the 2025 10-K Properties
section [A1]. Satellite imagery (Google Earth, retrieved 2026-04-25)
shows active rail spurs entering the southwest quadrant [A2].
```

Every claim cited. Every claim rated. The reader can scan the dossier
and instantly know which findings to act on (`A1`, `A2`) and which to
flag for follow-up (`C3`, `D4`).

---

## What an unrated dossier line looks like (don't do this)

```
Caterpillar has a big plant in Peoria with rail access.
```

This is a hobbyist line. No source, no rating, no timestamp. Useless to
anyone who wasn't with you when you found it. *Useless to you in two
weeks when you can't remember where you got it.*

---

## The rating discipline IS the lesson

Most OSINT failures happen at evaluation, not collection. People find
something and put it in the dossier without asking *whether they should
trust it*. Tagging every finding with `[Letter][Number]` forces you to
ask the question before the claim ships.

If you find yourself wanting to write `D4` on something, that's usually a
sign the finding shouldn't be in the dossier at all. Either upgrade it
(find a corroborating `A` or `B` source and re-tag) or cut it.

The dossier you finish at 15:40 today should have **mostly `A`s and `B`s**,
with a small "Flagged for follow-up" section at the bottom holding the
weaker findings you couldn't yet upgrade. That's a professional product.

---

**Cross-references:**
- `CRAAP-Test.md` — five questions to ask before assigning a letter
- All `Class-Modules/` files reference Admiralty ratings on demo findings
- `Tools-and-Scripts/domain_to_dossier.py` emits ratings automatically on
  every section it produces
