# Lab — Module 2 — 🟠 Ghost
## Complete passive surface map, automated and audited

**Time budget:** 30 minutes (11:50–12:20)
**Pairs with:** `Class-Modules/Module-2-Passive-Enumeration.md`

---

## Pre-flight

- [ ] Pre-flight checklist green
- [ ] subfinder, dnsx, asnmap, dig in PATH

---

## Open objective

Produce the most complete passive surface map for Caterpillar that
30 minutes allows. The deliverable is a structured Section 3 of
the dossier with:

- Subdomains from **at least 3 independent enumeration methods** with
  set-overlap analysis
- Full ASN inventory across CAT-owned IP space (not CDN echo)
- TXT vendor map, complete
- RFC1918 / architecture-leak hunt with structured output
- Shodan InternetDB sweep across distinct CAT-owned IPs (rate-limit
  respecting)
- Coverage estimate for Section 8 of your dossier

---

## Suggested attack paths

### Path A — Three-source enumeration + Venn

```bash
# Source 1: subfinder (aggregator)
subfinder -silent -d caterpillar.com | sort -u > /tmp/cat-subfinder.txt

# Source 2: crt.sh raw
python3 Tools-and-Scripts/cert_enum.py caterpillar.com > /tmp/cat-crtsh.txt

# Source 3: amass passive
amass enum -passive -d caterpillar.com -silent | sort -u > /tmp/cat-amass.txt

# Set analysis
echo "subfinder: $(wc -l < /tmp/cat-subfinder.txt)"
echo "crt.sh:    $(wc -l < /tmp/cat-crtsh.txt)"
echo "amass:     $(wc -l < /tmp/cat-amass.txt)"
echo ""
echo "Only in subfinder:"
comm -23 <(sort /tmp/cat-subfinder.txt) <(cat /tmp/cat-crtsh.txt /tmp/cat-amass.txt | sort -u)
echo ""
echo "Only in crt.sh:"
comm -23 <(sort /tmp/cat-crtsh.txt) <(cat /tmp/cat-subfinder.txt /tmp/cat-amass.txt | sort -u)
```

The set-overlap analysis tells you which sources contribute unique
findings — **inform your future workflow priorities**, document in
Section 8.

### Path B — Resolve, then ASN-cluster

```bash
# Resolve everything
cat /tmp/cat-*.txt | sort -u | dnsx -silent -resp-only > /tmp/cat-resolved.txt

# Extract distinct IPs
awk '{print $NF}' /tmp/cat-resolved.txt | sort -u > /tmp/cat-ips.txt

# ASN attribute via asnmap
cat /tmp/cat-ips.txt | asnmap -silent > /tmp/cat-asn.txt

# Or via Cymru DNS in a loop (no quota)
while read ip; do
  reversed=$(echo "$ip" | awk -F. '{printf "%s.%s.%s.%s", $4, $3, $2, $1}')
  asn=$(dig +short TXT "${reversed}.origin.asn.cymru.com" | tr -d '"')
  echo "$ip | $asn"
done < /tmp/cat-ips.txt > /tmp/cat-asn-cymru.txt
```

Cluster the IPs by ASN. Which ASNs are CAT-owned vs. CDN vs. cloud?
The CAT-owned cluster is your real recon surface; the rest are
pass-through.

### Path C — Wayback-only hostname mining

```bash
# Pull historical hostnames from Wayback CDX
curl -s 'https://web.archive.org/cdx/search/cdx?url=*.caterpillar.com&output=text&fl=original&collapse=urlkey' \
  | awk -F/ '{print $3}' | sort -u > /tmp/cat-wayback-hosts.txt

# If 429s: fall back to mirror
# jq -r '.[1:] | .[] | .[0]' Mirrors/wayback/caterpillar.json | awk -F/ '{print $3}' | sort -u

# Subtract live-resolving hosts to get historical-only
comm -23 /tmp/cat-wayback-hosts.txt <(awk '{print $1}' /tmp/cat-resolved.txt | sort -u) \
  > /tmp/cat-historical-only.txt
```

Historical-only hostnames are abandoned/decommissioned services. Some
are dead. Some still respond and were forgotten. Worth a Wayback
Machine spot-check on the latter for "what was this app".

### Path D — Architecture-leak hunt at scale

```bash
# Combined hostname pool
cat /tmp/cat-*.txt /tmp/cat-wayback-hosts.txt | sort -u > /tmp/cat-all-hosts.txt

# RFC1918 in hostname
grep -E '(^|[^0-9])(10|172\.(1[6-9]|2[0-9]|3[01])|192\.168)\.' /tmp/cat-all-hosts.txt > /tmp/cat-rfc1918.txt

# Architecture/environment tells
grep -iE '(^|[.-])(lb|proxy|gw|fw|dev|stg|qa|uat|aws|gcp|azure|dc[0-9]|vpn|rdp|admin|internal|private|api)' \
  /tmp/cat-all-hosts.txt > /tmp/cat-arch-leaks.txt

# IP-in-hostname pattern (e.g., fw04-ha121528 → 12.15.28.x)
grep -oE '[a-z]+[0-9]{4,}' /tmp/cat-all-hosts.txt | sort -u > /tmp/cat-ip-hints.txt
```

Each match is a candidate finding. Rate them honestly — most won't
hold up. The few that do are dossier-worthy.

### Path E — InternetDB sweep with rate-limit discipline

```bash
# Distinct CAT-owned IPs only (filter out CDN-prefix IPs)
# Manually identify CAT ASNs from Path B output
CAT_IPS=$(grep -E 'AS(####|####)' /tmp/cat-asn-cymru.txt | awk '{print $1}')

# Polite sweep with jittered sleep
for ip in $CAT_IPS; do
  curl -s "https://internetdb.shodan.io/${ip}" >> /tmp/cat-internetdb.jsonl
  echo "" >> /tmp/cat-internetdb.jsonl
  sleep $(awk 'BEGIN{srand();print 1.0+rand()*0.5}')
done

# Surface CVEs across the sweep
jq -r 'select(.vulns != null) | "\(.ip) → \(.vulns[])"' /tmp/cat-internetdb.jsonl
```

---

## Automation prompt

If you script anything reusable:
- Make it target-agnostic (parameterize the domain)
- Output structured (JSON or JSONL), not stdout text
- Honor rate limits with jittered sleeps
- Handle 429/5xx gracefully with `--mirror-dir` fallback per the
  spec in `Tools-and-Scripts/README.md`
- Cite source + timestamp in every record

If your script is good, share it in the shout-outs at 15:40.

---

## Deliverable

Section 3 of your dossier should look something like:

```markdown
## 3. Domains & IP Space

**Enumeration methodology:** subfinder + crt.sh + amass passive,
deduplicated and resolved via dnsx, ASN-attributed via Team Cymru.
Coverage estimate: see Section 8.

**Total distinct hostnames:** [count]
**Resolving today:** [count]
**Historical-only (Wayback):** [count]

**Source contribution analysis:**
- subfinder unique: [count]
- crt.sh unique: [count]
- amass unique: [count]
- All three agree on: [count] ([%] of total)

**ASN clustering:**
| ASN | Owner | IPs in scope | Notes |
|-----|-------|--------------|-------|

**TXT-record vendor map:** [full table, not sample]

**Architecture / RFC1918 leaks:**
[Structured table of findings, each rated]

**Shodan InternetDB sweep:** [count] IPs swept, [count] with open ports
beyond 80/443, [count] with known CVEs. Notable findings:
[list with Admiralty ratings]

**Sources:** [extensive]
```

---

## Bonus

If you have time after the above:

**Favicon hash on a non-public CAT subdomain.** Pick something from
your Path D output that looks like an admin panel or login page.
Run `Tools-and-Scripts/favicon_pivot.py` against it. The Shodan
result might surface other CAT properties using the same vendor —
or other organizations sharing infrastructure.

This is also a Module 4 technique; doing it now sets up your
afternoon work.

---

## Done?

Lunch is at 12:20. Module 3 starts at 13:20.
