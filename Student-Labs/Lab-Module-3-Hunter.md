# Lab — Module 3 — 🔵 Hunter
## Active techniques, passive demos on Caterpillar

**Time budget:** 30 minutes (13:45–14:15)
**Pairs with:** `Class-Modules/Module-3-Active-Techniques-Passive-Demos.md`

---

## Pre-flight

- [ ] Pre-flight checklist green
- [ ] theHarvester installed (from git, per Start-Here)
- [ ] You understand the active/passive line for each tool below

---

## Core objective

By the end of this lab you will have:

1. theHarvester output for `caterpillar.com` from explicit passive sources
2. A recon-ng workspace with at least one working module run
3. A documented **wildcard detection result** for `caterpillar.com`
4. A **complete TXT-record vendor map** with each entry classified
5. (Optional) holehe output for a public press contact email — read
   correctly

---

## Step-by-step

### Step 1 — theHarvester explicit-sources run (8 min)

```bash
theHarvester -d caterpillar.com \
  -b duckduckgo,crtsh,dnsdumpster,yahoo,rapiddns,hackertarget,otx,certspotter,urlscan \
  -l 200 \
  -f cat-harvester.html
```

What `-l 200` does: limit each source to 200 results — keeps the
run time reasonable.

What `-f cat-harvester.html` does: write an HTML report you can
open in a browser.

Open the resulting HTML report. Compare to your Module 2 subfinder
output:

**In your notes:**
- Hosts theHarvester surfaced that subfinder didn't: ____________
- Hosts subfinder surfaced that theHarvester didn't: ____________
- Email addresses theHarvester surfaced (if any): ____________
  (Note: many of these are *patterns*, not real addresses — see
  Step 5)

**Admiralty rating:** B2 for theHarvester findings (aggregator with
multiple sources, not independently confirmed)

### Step 2 — recon-ng with the working module (5 min)

```bash
recon-ng -w cat-demo
```

Inside the recon-ng prompt:

```
[recon-ng][cat-demo] > db insert domains caterpillar.com

[recon-ng][cat-demo] > modules load recon/domains-hosts/netcraft

[recon-ng][cat-demo][netcraft] > run

[recon-ng][cat-demo][netcraft] > show hosts

[recon-ng][cat-demo][netcraft] > exit
```

**In your notes:**
- Hosts returned by netcraft module: ____________
- Hosts that overlap with subfinder/theHarvester: ____________
- Hosts that are unique to netcraft: ____________

If the netcraft module errors or returns zero results, that's the
**bit-rot lesson** in real time. Document the failure: which module
broke, what error message, what was the upstream symptom (captcha?
404? changed API?). That's a finding for your dossier's Section 8.

### Step 3 — Wildcard detection on caterpillar.com (3 min)

```bash
# Resolve a definitely-non-existent random hostname
dig +short DEFINITELY-NOT-A-REAL-XYZQ123-${RANDOM}.caterpillar.com
```

**Expected result for caterpillar.com:** NXDOMAIN (no output, or
"NXDOMAIN" status in verbose mode). This means CAT does *not*
wildcard.

**In your notes, document the detection result:**

```
Wildcard detection on caterpillar.com:
- Probe hostname: DEFINITELY-NOT-A-REAL-XYZQ123-12345.caterpillar.com
- Result: NXDOMAIN
- Conclusion: caterpillar.com does NOT wildcard. DNS brute force
  results against this domain (on an active-permitted target) would
  be reliable signal, not wildcard echo.
- Admiralty rating: A1 (direct DNS observation)
```

**This is a finding even though brute force was not run.** The
wildcard property of a domain is dossier-relevant on its own.

### Step 4 — TXT vendor map (full enumeration) (8 min)

You started this in Module 2. Now complete it.

```bash
dig +short TXT caterpillar.com > /tmp/cat-txt.txt
cat /tmp/cat-txt.txt
```

For **every** TXT record, classify it. Reference table:

| Pattern | Vendor / Service |
|---------|------------------|
| `v=spf1 include:_spf.google.com` | Google Workspace mail |
| `v=spf1 include:spf.protection.outlook.com` | Microsoft 365 mail |
| `v=spf1 include:amazonses.com` | AWS SES |
| `v=spf1 include:mailgun.org` | Mailgun |
| `v=spf1 include:sendgrid.net` | SendGrid |
| `MS=ms########` | Microsoft 365 / Azure tenant |
| `google-site-verification=` | Google product (Search Console, etc.) |
| `_amazonses-` | AWS SES verification |
| `klaviyo-site-verification=` | Klaviyo email marketing |
| `stripe-verification=` | Stripe |
| `docusign=` | DocuSign |
| `atlassian-domain-verification=` | Atlassian (Jira/Confluence) |
| `zoom-domain-verification=` | Zoom |
| `apple-domain-verification=` | Apple business services |
| `facebook-domain-verification=` | Meta business |

Build the dossier-quality version of the table:

```markdown
**TXT-record-derived vendor map for caterpillar.com:**

| Vendor | Evidence (TXT prefix) | Admiralty |
|--------|----------------------|-----------|
| Google Workspace mail | v=spf1 include:_spf.google.com | A1 |
| Microsoft 365 tenant | MS=ms40012345 | A1 |
| AWS SES | _amazonses-01abcdef | A1 |
| … | … | A1 |
```

**Every TXT record is A1** — you observed it directly via DNS
resolution. The vendor *interpretation* is what carries the
inferential rating; the raw record is primary data.

### Step 5 — (Optional) holehe on a public press contact (6 min)

**Skip this if you're uncomfortable with people-pivots, even
public-press-contact ones.** It's optional, not required.

Find a public press contact email on Caterpillar's investor
relations or media page. These are publicly published email
addresses — the company *wants* media to email them.

```bash
holehe press-contact-public@caterpillar.com
```

Read the output **carefully**. Reference key:

| Symbol | Meaning |
|--------|---------|
| `[+]` | Email IS registered on this service |
| `[-]` | Email confirmed NOT registered |
| `[x]` | Inconclusive (rate-limit or service error) — *not a hit* |

**Common error:** reading `[x]` as a soft positive. It is not.
Treat `[x]` as "no signal."

**In your notes:**
- Email checked: [public-press-contact-only]
- Services with `[+]`: ____________
- Notable absences (`[-]` on services you'd expect): ____________

**Hard reminder:** today's scope is "no individual employees." A
public press contact email is fair game; an individual engineer's
inferred email is not.

---

## Deliverable

Add to your dossier:

```markdown
## 4. Tech Stack & Exposed Services

[Some of this fills in during Module 4. For now, capture:]

**Subdomain enumeration sources used (final):**
- subfinder
- crt.sh (or mirror)
- theHarvester (passive sources only): N additional unique hosts
- recon-ng netcraft module: N additional unique hosts
- Total unique resolving subdomains: [count]

**Wildcard property of caterpillar.com:** No wildcard. Brute force
results would be reliable signal. (Brute not executed; CAT is
no-active scope.) [A1]

**TXT-record vendor map:** [full table from Step 4]

**Sources:** [URLs and tool versions]
```

---

## 🟠 Ghost preview challenge

Run the explicit-sources theHarvester command against `cat.com`
in addition to `caterpillar.com`. Compare the two surfaces.

```bash
theHarvester -d cat.com \
  -b duckduckgo,crtsh,dnsdumpster,yahoo,rapiddns,hackertarget,otx,certspotter,urlscan \
  -l 200 -f cat-domain-harvester.html
```

Are the results different sets, overlapping sets, or near-identical?
What does that tell you about how Caterpillar uses the two domains
internally?

Document one finding from this comparison in your dossier.

---

## Common gotchas

- **theHarvester source dropouts** — if a source returns zero, it
  may be temporarily down or rate-limited. Try removing it from `-b`
  and re-running with the remaining sources.
- **recon-ng captcha errors** are normal in 2026. The bit-rot is
  the lesson; don't fight it.
- **Some TXT records are SPF includes that nest** (e.g.,
  `include:_spf.vendor.com` which itself includes others). For full
  signal, recursively resolve the includes — but for the deliverable,
  the top-level vendor name is enough.

---

## Done?

Module 4 starts at 14:15. Open
`Class-Modules/Module-4-Profile-and-Pivot.md` when you're ready.
