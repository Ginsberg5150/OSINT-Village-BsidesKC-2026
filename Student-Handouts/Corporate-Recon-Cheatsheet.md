# Corporate Recon Cheat Sheet · OSINT Village BSides KC 2026

**One-page field reference for passive corporate reconnaissance.**
Target today: **Caterpillar Inc.** (`caterpillar.com`, `cat.com`)
Scope: **passive only** · no active scans · no individual employees

---

## 0 · Pre-Flight (before every engagement)

- [ ] VPN active — verify exit IP ≠ home ISP at `ifconfig.me`
- [ ] Dedicated browser profile — not personal browser
- [ ] All personal accounts signed out (Google, LinkedIn, GitHub)
- [ ] LinkedIn → Settings → Visibility → Private Mode
- [ ] Notes open with target name + first timestamp
- [ ] Sober, calm, focused

---

## 1 · Identify (who is the target, really?)

| Source | URL | Use |
|--------|-----|-----|
| EDGAR full-text | `efts.sec.gov/LATEST/search-index` | `company` + `forms=10-K` |
| EDGAR filings | `sec.gov/cgi-bin/browse-edgar` | navigate filings by CIK |
| Exhibit 21 | inside any 10-K | complete subsidiary list |
| USASpending | `usaspending.gov/recipient` | federal contracts (NOT SAM.gov) |
| OpenCorporates | `opencorporates.com` | international entity records |
| Wayback CDX | `web.archive.org/cdx/search/cdx` | historical site snapshots |

**M&A 4-state verification** (always run before enumerating acquired domain):
```bash
curl -sI https://acquired.com | grep -i location
```
→ **Absorbed** (redirects to parent) · **Independent** (own content) ·
  **Sunset** (404 / archive only) · **Divested** (different parent / NXDOMAIN)

---

## 2 · Passive Enumeration (what's exposed?)

```bash
# Unified chain — this is the command to commit to muscle memory
subfinder -silent -d caterpillar.com | dnsx -silent -resp-only | sort -u

# Add ASN attribution
subfinder -silent -d caterpillar.com | dnsx -silent -resp-only | asnmap -silent
```

**Fallback order if subfinder/crt.sh down:**
1. `Mirrors/subfinder/caterpillar.txt` (pre-cached)
2. `Mirrors/crtsh/caterpillar.json` (pre-cached)
3. Certspotter · Censys CT search · Merklemap

**DNS disclosure — always walk these:**
```bash
dig +short TXT caterpillar.com       # SaaS vendor map
dig +short MX caterpillar.com        # mail platform
dig +short NS caterpillar.com        # DNS provider (watch for Foundation DNS)
dig +short SPF caterpillar.com       # email senders (in TXT)
```

**ASN lookup — no quota, no key:**
```bash
# Reverse 12.34.56.78 and look up via Cymru DNS
dig +short TXT 78.56.34.12.origin.asn.cymru.com
```

**Shodan InternetDB (keyless, fast):**
```bash
curl -s https://internetdb.shodan.io/<distinct-ip> | jq
```

**RFC1918-in-CT hunt:**
```bash
grep -E '(^|[^0-9])(10|172\.(1[6-9]|2[0-9]|3[01])|192\.168)\.' subs.txt
```

---

## 3 · Active Techniques, Passive Demos (today only)

**theHarvester — explicit sources (never `-b all`):**
```bash
pip install git+https://github.com/laramies/theHarvester.git
theHarvester -d caterpillar.com \
  -b duckduckgo,crtsh,dnsdumpster,yahoo,rapiddns,hackertarget,otx,certspotter,urlscan \
  -l 200 -f cat-harvester.html
```

**recon-ng — pruned to working modules:**
```
recon-ng -w cat
> db insert domains caterpillar.com
> modules load recon/domains-hosts/netcraft
> run
```

**Wildcard detection — ALWAYS FIRST before brute:**
```bash
dig +short DEFINITELY-NOT-REAL-XYZQ123.caterpillar.com
# NXDOMAIN = safe to brute (on authorized targets)
# Any IPs returned = wildcard; filter brute output against them
```

**holehe symbol reading:** `[+]` hit · `[-]` confirmed-not-registered · `[x]` inconclusive (NOT a hit)

**Foundation DNS fingerprint** (NS records): `gold.foundationdns.com/.net/.org` = Cloudflare enterprise

---

## 4 · Profile & Pivot

| Tool | What it does |
|------|--------------|
| `whatweb -a 1 <url>` | passive HTTP fingerprint |
| Wappalyzer (browser ext) | CMS/CDN/analytics/JS stack readout |
| BuiltWith | historical stack (free tier) |
| `favicon_pivot.py <url>` | mmh3 hash → Shodan/Censys pivot |
| EPA Envirofacts | `enviro.epa.gov/envirofacts` — facility registry + TRI + ECHO |
| OSHA establishment | `osha.gov/ords/imis/establishment.html` (browser-only) |
| FAA Registry | `registry.faa.gov/aircraftinquiry/` (browser-only) |
| FCC ULS | `wireless2.fcc.gov/UlsApp/UlsSearch/` (browser-only) |
| Google Patents | `patents.google.com/?assignee=caterpillar+inc` (default; no key needed) |
| ADS-B Exchange | `globe.adsbexchange.com/?icao=<code>` (historical flight) |

**KML generation:**
```bash
python3 Tools-and-Scripts/plants_to_kml.py cat-plants.csv \
    --output cat-plants.kml --title "Caterpillar Facilities"
```

---

## 5 · Report (assemble & rate)

**8-section dossier structure:**
1. Executive Summary (write FIRST, 3 bullets)
2. Org Footprint
3. Domains & IP Space
4. Tech Stack & Exposed Services
5. People & Roles (patterns only — no individuals)
6. Physical & Regulatory
7. Notable Findings (3–5 "so what" items)
8. **Footprint Self-Audit** (what searched, what skipped, coverage)

**Admiralty Code** — tag every claim `[Letter Number]`:

| Letter (source) | Number (info) |
|-----------------|---------------|
| A Completely reliable | 1 Confirmed by independents |
| B Usually reliable | 2 Probably true |
| C Fairly reliable | 3 Possibly true |
| D Not usually reliable | 4 Doubtful |
| E Unreliable | 5 Improbable |
| F Cannot judge | 6 Cannot judge |

**CRAAP** per source: **C**urrency · **R**elevance · **A**uthority · **A**ccuracy · **P**urpose

---

## Scope reminders

- **Passive only on CAT** — no active scans, no DNS brute, no `-c` flags
- **No individual employees** — patterns only, no names/emails
- **Respect rate limits** — jittered 1.0–1.5s between polled calls
- **Cite everything** — URL + timestamp + Admiralty rating

---

## Tier graduation

🔵 **Hunter** — follow the step-by-step lab, produce the checklist
deliverables. Try the "Ghost preview challenge" at the end of each
lab when you're ahead of time.

🟠 **Ghost** — open objectives, automate the repetitive parts, produce
leadership-grade deliverables (MD + KML + JSON), cross-correlate
findings across sections.

---

*OSINT Village BSides KC 2026 · Wildcard Industries LLC ·
github.com/Ginsberg5150/OSINT-Village-BsidesKC-2026*
