# Practice Scopes — Safe Targets

Before pointing this toolkit at anything else, practice on targets
where you have explicit permission. The cleanest sources are public
bug bounty programs that publish their scope.

> **Always re-read the scope before each session.** Programs change
> scope, pause, or close without warning. What was in scope last
> month may be out of scope today.

## Recommended bug bounty programs

These were chosen because they have **broad public scopes**, mature
security teams, and publish good disclosure guidance.

### Shopify
- HackerOne: https://hackerone.com/shopify
- Why it's good for practice: massive subdomain estate, lots of
  acquisitions to map (great for `domain_to_dossier.py` and
  `edgar_subsidiaries.py` — Shopify is publicly traded under SHOP).
- Public CIK: 0001594805

### Yelp
- HackerOne: https://hackerone.com/yelp
- Why it's good for practice: clear scope, mature program, US-listed
  (CIK 0001345016) so EDGAR scripts work, well-documented infra.

### GitHub
- HackerOne: https://hackerone.com/github
- Why: massive scale, deep documentation, generous scope.

### GitLab
- HackerOne: https://hackerone.com/gitlab
- Why: open-source company with extensive public infrastructure.

### Mozilla
- Bugcrowd: https://bugcrowd.com/mozilla
- Why: nonprofit, broad scope, very welcoming to new researchers.

### HackerOne (the company itself)
- HackerOne: https://hackerone.com/security
- Why: meta — they run programs, they get tested. Excellent docs.

## Industrial / non-public-company practice

For practicing `plants_to_kml.py` on facility data without touching a
specific company:

- **Caterpillar 10-K Properties section** — publicly disclosed plant
  list. Excellent for the KML workflow. (CIK 0000018230)
- **Deere & Co. 10-K** — same, agricultural. (CIK 0000315189)
- **Boeing 10-K** — manufacturing footprint. (CIK 0000012927)

These are public regulatory disclosures. Mapping a company's own
disclosed properties is fully passive.

## What's NOT a practice scope

- Anything not listed in a public bug bounty program scope
- Government infrastructure (don't, even passively)
- Critical infrastructure (utilities, hospitals, water, ICS)
- Active attack scenarios (this toolkit is passive — keep it that way)
- Personal targets, ex-employers, or anyone you have a grievance with

## Pre-flight checklist before touching any target

- [ ] Re-read the program scope today
- [ ] Confirm the asset is in scope (not just the parent company)
- [ ] Verify your activity is allowed (passive vs. active rules differ
      sharply between programs)
- [ ] Confirm no excluded categories (PII enumeration, social
      engineering, employee testing)
- [ ] Note the disclosure timeline you're committing to

If anything is unclear — ask the program. Bug bounty platforms have
direct messaging to triagers for exactly this.
