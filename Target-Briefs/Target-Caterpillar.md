# Target Brief — Caterpillar Inc.

**Read this before Module 1 starts. Five minutes.**

---

## Identity

| Field | Value |
|-------|-------|
| **Legal name** | Caterpillar Inc. |
| **Ticker** | NYSE: CAT |
| **HQ** | Irving, TX (relocated from Deerfield, IL in 2018) |
| **Sector** | Heavy industrial — construction, mining, energy, transportation |
| **Primary domain** | `caterpillar.com` |
| **Other known domains** | `cat.com` (worth checking — corporate uses it too) |

This is the only target for today's workshop. One target, five modules,
one finished dossier.

---

## Why this target

Caterpillar is the workshop's anchor for one reason: **it forces you to
practice both halves of corporate recon in a single day.**

- **Digital surface.** A real corporate web presence with the kind of
  certificate footprint, DNS hygiene, and infrastructure choices a
  Fortune 100 makes. Plenty of subdomains. Real ASN ownership. Real
  cloud/CDN architecture decisions you can fingerprint.
- **Physical surface.** Manufacturing plants on multiple continents.
  EPA-regulated facilities. OSHA inspection history. Patent filings.
  Corporate aircraft. A supply chain that's visible in import records.
  Dealer geography that maps to sales distribution. **This is the layer
  most "corporate recon" courses skip entirely** — it's where heavy
  industry leaks more than the digital surface ever will.
- **Federal contracting presence.** SAM.gov / USASpending.gov registers
  light up. There's a CAGE code and contract awards to discover.
  Operating divisions visible to the government that aren't always
  obvious in the 10-K.
- **Heavy SEC filings.** Subsidiary list, Properties section with
  plant addresses, segment reporting that maps revenue to operating
  divisions — all of it public, all of it discoverable today.

A digital-only target (Shopify, Stripe, etc.) lets you practice the
left half. A people-heavy target (Yelp, Reddit) lets you practice the
middle. Caterpillar is the only kind of target that exercises everything.

---

## In scope today

✅ Anything publicly available on the open internet about Caterpillar
   Inc., its subsidiaries, brands, dealers, and disclosed operations
✅ SEC filings (10-K, 10-Q, 8-K, proxy statements, exhibits)
✅ Other public regulatory disclosures — EPA, OSHA, EEO-1, federal
   contracts, patents, trademarks
✅ Court records, where public
✅ Certificate transparency logs (crt.sh and equivalents)
✅ Passive scan databases — Shodan, Censys, urlscan.io
✅ Public corporate registries — OpenCorporates, state Secretary of
   State sites, foreign equivalents
✅ News, trade publications, financial analyst reports
✅ Patent and trademark databases (USPTO, Google Patents, WIPO)
✅ Public social media profiles of the company itself and its
   public-facing official spokespeople
✅ Trade and import data (Panjiva, ImportGenius, USITC DataWeb)
✅ Aviation registries (FAA registry, ADS-B Exchange historical data)

## Out of scope today

❌ Active scanning of any Caterpillar-owned infrastructure (no nmap,
   no port scanners, no vulnerability scanners — Module 3 covers
   what "active" means in detail)
❌ Authentication attempts of any kind, on any CAT property
❌ Contact attempts with CAT employees, dealers, customers, or
   contractors — no emails, no DMs, no LinkedIn messages, no calls
❌ Engagement with any social media account belonging to CAT or its
   employees — no follows, likes, replies, comments. Pure passive
   observation.
❌ Aggregation of personally identifiable information about
   individual CAT employees beyond what's necessary to *demonstrate
   a technique*. The technique is the lesson; the person is not
   the target.
❌ Anything that would embarrass Caterpillar, the workshop, BSides
   KC, or you when read aloud in a conference room

---

## Three rules to commit to memory

These are the lines you don't cross, regardless of what a tool will
let you do.

**1. Plant addresses are public; building access details are not.**
Caterpillar's 10-K Properties section lists facility addresses by
city — that's a federal filing, fully public, fully fair game to map
on Google Earth. What is *not* fair game today: shift schedules,
employee parking patterns, gate procedures, security camera placements,
or anything else that reads like physical penetration scoping. Map
the locations. Don't case the buildings.

**2. No employee names in your dossier.**
You will find email patterns. You will find LinkedIn profiles. You
will find people in GitHub commit histories. Document the *pattern*
in your dossier ("`first.last` for engineering staff, observed
N times across M sources, Admiralty B2"), not the individual.
Aggregating named real people is what dossiers-against-people do —
that's a different ethical regime and it is not what we are doing
today.

**3. If a finding feels like it crosses a line, it does. Stop and ask.**
Recon at this scale will sometimes surface things — active labor
disputes, lawsuits, individual employee struggles, accidents — that
are public but sensitive. Document the source link and move on. Don't
amplify, don't speculate, and don't make it the centerpiece of your
dossier. If you're not sure whether something is okay to include, ask
the instructor. The answer is almost always "cite the source link
without elaborating."

---

## What to expect

**Some sources will block you.** Caterpillar fronts much of its
infrastructure with major CDNs (Akamai is common at this scale). Several
passive fingerprinting techniques that work cleanly on smaller targets
will return generic CDN answers here. **That is part of the lesson.**
The modules will show you how to read indirect signals (DNS TXT records,
nameserver patterns, mail routing, regulatory filings) when the front
door is opaque.

**Some sources will rate-limit you.** When 30 people in a classroom
hit `crt.sh` at the same time, `crt.sh` returns 502s. When 30 people
hit Wayback's CDX API, you get 429s for the rest of the day. The
`Mirrors/` folder in this repo is your fallback. Using it is not
cheating — mirroring upstream sources you have permission to query is
what professionals do at scale.

**A lot will work.** Hundreds of subdomains. Multiple operating
subsidiaries with their own legal identities. Plant addresses you can
map. Federal contract awards in the millions. Patents that telegraph
R&D direction. Import records that show supply-chain dependencies.
You will not be short on findings. The discipline you're learning
today is *which* findings to keep, *how* to rate them, and *how* to
present them — not how to find more.

---

## Pre-class verification

The instructor verifies the morning of the workshop:

- No active public security incident at Caterpillar that would make
  recon awkward or insensitive
- No major news cycle (labor dispute, scandal, tragedy) that recon
  could be perceived to be exploiting
- Scripts run end-to-end against `caterpillar.com` on conference Wi-Fi
- `Mirrors/` folder is current — captured the night before

If any of those raise flags, the instructor adjusts and notifies the
room before Module 1.

---

When you're ready, open **`Class-Modules/Module-1-Identify.md`**.
