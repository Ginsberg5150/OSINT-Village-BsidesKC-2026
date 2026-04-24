# Lab — Module 2 — 🔵 Hunter
## Passive enumeration of Caterpillar's external surface

**Time budget:** 30 minutes (11:50–12:20)
**Pairs with:** `Class-Modules/Module-2-Passive-Enumeration.md`

---

## Pre-flight

- [ ] Pre-flight checklist still green
- [ ] Org graph from Module 1 in your notes
- [ ] subfinder installed (or you'll fall back to crt.sh + mirror)

---

## Core objective

By the end of this lab you will have:

1. A deduplicated list of **at least 50 resolving subdomains** for
   `caterpillar.com` (or `cat.com`)
2. ASN / owner data for **at least 5 distinct IPs** in CAT's space
3. The complete **TXT record vendor map** for caterpillar.com
4. At least **one RFC1918 leak OR one architecture-leaking hostname**
   identified (or a documented "none found" with evidence)
5. Shodan InternetDB results for **at least 3 distinct IPs**

Every finding tagged with Admiralty Code.

---

## Step-by-step

### Step 1 — Subdomain enumeration (8 min)

**First try: subfinder unified chain**

```bash
subfinder -silent -d caterpillar.com | dnsx -silent -resp-only | sort -u > cat-subs.txt
wc -l cat-subs.txt
```

If this works, skip to Step 2.

**If subfinder returns nothing or fails:** fall back to the mirror

```bash
cat Mirrors/subfinder/caterpillar.txt | sort -u > cat-subs.txt
```

**If you don't have subfinder installed at all:** use crt.sh directly

```bash
python3 Tools-and-Scripts/cert_enum.py caterpillar.com > cat-subs.txt
```

**If crt.sh returns 502:** fall back to the mirror

```bash
jq -r '.[].name_value' Mirrors/crtsh/caterpillar.json | tr ',' '\n' | sort -u > cat-subs.txt
```

**In your notes:**
- Source used: ____________
- Total subdomains found: ____________
- Admiralty rating: B2 (subfinder/crt.sh raw) or B3 (mirror — note
  the snapshot date)

### Step 2 — DNS disclosure walk (5 min)

```bash
# SPF — email vendor
dig +short TXT caterpillar.com | grep -i spf

# MX — mail platform
dig +short MX caterpillar.com

# All TXT — SaaS vendor map
dig +short TXT caterpillar.com

# NS — DNS provider
dig +short NS caterpillar.com
```

**In your notes, list every vendor inferred from TXT records:**

```
- Microsoft 365 (MS=ms########)
- Google Workspace (google-site-verification=…)
- AWS SES (_amazonses-…)
- Klaviyo (klaviyo-site-verification=…)
- … (your full list)
```

The TXT vendor map is one of the highest-signal findings of the day.
Don't shortchange this step.

### Step 3 — ASN attribution (5 min)

Pick 5 distinct IPs from your Step 1 subdomain output. For each:

```bash
# Reverse the IP and look up via Team Cymru DNS
# Example IP 12.34.56.78:
dig +short TXT 78.56.34.12.origin.asn.cymru.com
```

Returns: `"ASN | PREFIX | COUNTRY | REGISTRY | DATE"`

**In your notes:**
```
12.34.56.78 → AS#### "Caterpillar Inc" / "Akamai" / "Cloudflare" / etc.
```

Note which IPs are CAT-owned vs. CDN-fronted (Akamai, Cloudflare,
Fastly). The CAT-owned ones are your most valuable enumeration
results — those are CAT's own infrastructure, not a CDN's.

### Step 4 — Shodan InternetDB on distinct IPs (5 min)

For 3 distinct **CAT-owned** IPs (not the CDN ones — those will all
look the same):

```bash
curl -s https://internetdb.shodan.io/12.34.56.78 | jq
```

**In your notes:**
- IP: ____________
- Open ports: ____________
- Hostnames: ____________
- Known CVEs (if any): ____________
- Admiralty rating: B2

**Discipline reminder:** dedupe to distinct IPs first. Don't fire
this against every hostname — many will resolve to the same IP and
you'll waste rate-limit budget.

### Step 5 — RFC1918 / architecture leak hunt (5 min)

```bash
# RFC1918 IPs in subdomain names (rare but high value)
grep -E '(^|[^0-9])(10|172\.(1[6-9]|2[0-9]|3[01])|192\.168)\.' cat-subs.txt

# Architecture-leaking hostnames
grep -iE '(^|-)(lb|proxy|gw|fw|dev|stg|qa|uat|aws|gcp|azure|dc[0-9]|vpn|rdp)' cat-subs.txt
```

**In your notes:**

If anything matched: list the hostname + what it leaks.

If nothing matched: write "**No RFC1918 or architecture-leaking
hostnames found in subdomain enumeration of caterpillar.com.
Sample N=[count]. [B2]**" — *the negative finding is itself a
finding.* It says something about CAT's cert hygiene.

---

## Deliverable

Add Section 3 to your dossier:

```markdown
## 3. Domains & IP Space

**Subdomains enumerated:** [count] resolving subdomains via [source]
[B2 or B3, retrieved YYYY-MM-DD]

**Notable subdomains:**
- [3-5 specific subdomains worth calling out, especially anything
  architecture-leaking or non-public-facing]

**ASN ownership (sample of 5):**
| IP | ASN | Owner | Country |
|----|-----|-------|---------|
| 12.34.56.78 | AS#### | Caterpillar Inc | US |
| … |

**TXT-record-derived vendor map:**
- Microsoft 365 [A1]
- Google Workspace [A1]
- … (full list)

**Shodan InternetDB sample (3 IPs):**
- 12.34.56.78: ports [80,443], no known CVEs [B2]
- … 

**RFC1918 / architecture leaks:** [list, or "none found, N=count"]

**Sources:** [URLs and tool versions]
```

---

## 🟠 Ghost preview challenge — try this if you finish early

**Run the dossier script with mirror fallback:**

```bash
python3 Tools-and-Scripts/domain_to_dossier.py caterpillar.com \
    --keyless \
    --mirror-dir Mirrors/ \
    --output cat-dossier-draft.md
```

Open the output. Compare:
- What did the script find that you didn't?
- What did you find that the script missed?
- Where did the script fall back to a mirror, and what does it tell
  you about which sources rate-limited during the class?

Document one finding in each direction in your dossier's Section 8
(Footprint Self-Audit).

---

## Common gotchas

- **CAT is heavily Akamai-fronted.** Most ASN lookups on
  resolved IPs will return "Akamai", not "Caterpillar Inc". That's
  the lesson from Module 4 about indirect fingerprinting — don't
  treat it as a problem.
- **`dig` returning nothing** usually means your local resolver is
  failing, not that the record doesn't exist. Try `dig @8.8.8.8` to
  bypass.
- **Shodan InternetDB returns `{}` (empty object)** for IPs Shodan
  hasn't scanned. Not an error; just no data.

---

## Done?

Lunch is at 12:20. Module 3 starts at 13:20 — open
`Class-Modules/Module-3-Active-Techniques-Passive-Demos.md` after
lunch.
