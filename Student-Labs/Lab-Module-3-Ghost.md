# Lab — Module 3 — 🟠 Ghost
## Active techniques, rigorously passive on Caterpillar

**Time budget:** 30 minutes (13:45–14:15)
**Pairs with:** `Class-Modules/Module-3-Active-Techniques-Passive-Demos.md`

---

## Pre-flight

- [ ] Pre-flight green
- [ ] Wildcard discipline internalized (always detect first)
- [ ] You understand the active/passive line per tool

---

## Open objective

For each tool in the Module 3 toolset, produce a dossier-quality
section that:

1. Shows you drove the tool competently in its passive-safe mode
2. Declares where the active boundary would have been crossed
3. Captures any failures (rate limits, bit-rot, empty returns) as
   findings for Section 8 of your dossier
4. Correlates findings across tools — what does theHarvester know
   that recon-ng doesn't, and vice versa?

---

## Suggested attack paths

### Path A — Run the full Module 3 toolset, record gaps

- `theHarvester` against `caterpillar.com` AND `cat.com` with the
  explicit-source list
- `recon-ng` workspace with every module you can find that returns
  data without erroring — document which worked, which bit-rotted
- `holehe` against ONE public press contact email (not individual
  employees)
- Complete TXT vendor enumeration against both `caterpillar.com`
  and every high-value subdomain from Module 2 output

Output: structured "Module 3 findings" section with source
contribution analysis.

### Path B — Wildcard map across CAT's subdomain tree

Wildcard detection on the root is only the beginning. Some orgs
wildcard *specific subdomains* (e.g., `*.dealer.caterpillar.com`
might wildcard while the root doesn't). Probe the pattern:

```bash
# For each suspected "parent" subdomain, check if it wildcards
for parent in dealer shop parts corp info; do
  probe="NOT-A-REAL-HOST-${RANDOM}.${parent}.caterpillar.com"
  result=$(dig +short "$probe")
  echo "${parent}.caterpillar.com → $([ -z "$result" ] && echo "no wildcard" || echo "WILDCARD $result")"
done
```

Any wildcarded subdomain is noteworthy. Document both positive and
negative findings; the map as a whole is dossier-worthy.

### Path C — TXT vendor map → dossier cross-check

You have a TXT-derived vendor list. Now cross-check: does the
company's **public job postings mention tools from vendors you found
in TXT?**

For each vendor in your TXT map, search:
```
site:caterpillar.com "Klaviyo"
site:caterpillar.com "Atlassian"
site:caterpillar.com "Snowflake"
```

Matches confirm production use. Non-matches suggest the vendor is
deployed somewhere non-public (internal tools, dev environments,
legacy). Either way, it strengthens your dossier.

### Path D — recon-ng bit-rot audit

Walk the recon-ng module catalog:

```
[recon-ng] > modules search recon/domains-hosts
```

For each module, try loading and running it against `caterpillar.com`.
Record which work, which fail, and why. This produces a
**current-as-of-class-day recon-ng status matrix** that's genuinely
useful beyond today — and not something published anywhere else.

Output format:
```
| Module | Status | Error / Notes |
|--------|--------|---------------|
| recon/domains-hosts/netcraft | ✅ works | returns N hosts |
| recon/domains-hosts/threatcrowd | ❌ dead | service offline since 2022 |
| recon/domains-hosts/bing_domain_api | ❌ key-gated | |
| ... |
```

Share this at shout-outs. Someone in the room will want a copy.

---

## Automation prompt

If you wrap any of this in a script, make it:
- Target-agnostic (`--domain` arg)
- Structured output (JSON)
- Respect rate limits
- Record every source that failed and why (goes into Section 8)

---

## Deliverable

Your Module 3 contribution to the dossier is:

```markdown
## 4. Tech Stack & Exposed Services (partial — completed in Module 4)

**Active-technique toolset coverage (passive mode only, CAT is
no-active scope):**

- theHarvester [passive sources: duckduckgo,crtsh,dnsdumpster,…]:
  N hosts surfaced, M unique to this source [B2]
- recon-ng: [status matrix, see attached]
- Wildcard property of caterpillar.com and [N] subdomains mapped:
  [result summary] [A1]
- TXT vendor map cross-checked against public job postings:
  N/M vendors confirmed in public hiring content [B2]

**Active line declaration:** DNS brute not run. theHarvester `-c`
flag not used. Port probing not performed. All findings derived
from passive aggregators or direct DNS queries only. [scope]

**Sources & failure log:**
[extensive, including rate-limits hit, modules that bit-rotted,
sources skipped]
```

---

## Done?

Module 4 starts at 14:15.
