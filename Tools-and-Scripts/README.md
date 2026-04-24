# Tools-and-Scripts/

Helper scripts for the workshop labs. All are passive. All respect
rate limits. All are deliberately simple so you can read them end to
end in one sitting.

---

## Setup

```bash
pip install -r ../requirements.txt
```

Optional: copy `../.env.example` to `../.env` and fill in any API
keys you have. Everything works keyless by default.

**theHarvester is NOT in requirements.txt.** Install it separately
per `00-Students-Start-Here.md`:

```bash
pip install git+https://github.com/laramies/theHarvester.git
```

---

## The scripts, at a glance

| Script | When to use | Labs that call it |
|--------|-------------|-------------------|
| `cert_enum.py` | crt.sh CT-log enumeration for a single domain | Module 2 Hunter |
| `domain_to_org.py` | Module 1 automation (Ghost stub) | Module 1 Ghost |
| `domain_to_dossier.py` | Module 2+ automation — passive surface + ASN + InternetDB | Modules 2/5 Ghost preview |
| `favicon_pivot.py` | Shodan favicon-hash pivot | Module 4 Hunter & Ghost |
| `plants_to_kml.py` | CSV of plant addresses → KML map | Module 4 Hunter & Ghost |

---

## Script-by-script notes

### `cert_enum.py`

Minimal crt.sh wrapper. Returns deduplicated subdomains for a domain
via CT logs.

```bash
python3 cert_enum.py caterpillar.com
python3 cert_enum.py caterpillar.com --include-wildcards
```

Production-safe as-is. **Status: ✅ ready.**

If crt.sh 502s, fall back to the mirror:
```bash
jq -r '.[].name_value' ../Mirrors/crtsh/caterpillar.json | tr ',' '\n' | sort -u
```

### `favicon_pivot.py`

Hashes a favicon with Shodan's algorithm (mmh3 of base64 bytes) and
emits pivot URLs for Shodan and Censys.

```bash
python3 favicon_pivot.py https://www.caterpillar.com
```

**Status: ✅ ready** (includes QA-flagged `<link rel="icon">` fallback
for sites without `/favicon.ico`).

### `plants_to_kml.py`

Takes a CSV with `name,address` columns and produces a KML file.
Uses Census TIGER as primary geocoder, OSM Nominatim as fallback.

```bash
python3 plants_to_kml.py cat-plants.csv --output cat-plants.kml \
    --title "Caterpillar Facilities"
```

**Status: ✅ ready** (includes QA-flagged street-number pre-filter
that skips EPA-style "PORTABLE SOURCE" / no-street-number rows).

CSV format:
```
name,address,segment,notes
East Peoria,500 SE Adams St East Peoria IL 61611,Construction,
...
```

### `domain_to_dossier.py`

The flagship script. Takes a domain, produces a full passive
dossier. Best run during Module 5 after you have manual findings
to compare against.

```bash
python3 domain_to_dossier.py caterpillar.com \
    --output cat-dossier.md --json cat-dossier.json
```

**Status: ⚠️ carry-over, minor fixes pending.** See the QA-flagged
TODO block at the top of the script. The script runs and produces
useful output today; the deeper fixes (`--mirror-dir`, `--keyless`,
source ordering, jittered sleeps) are tracked as post-class
improvements. The **narrative additions Module 5 asks you to make**
(Executive Summary, Notable Findings, Footprint Self-Audit) are
what raise a script-generated base into a professional dossier
anyway.

### `domain_to_org.py`

Module 1 automation — EDGAR + USASpending.

```bash
python3 domain_to_org.py caterpillar.com --output cat-org.json
```

**Status: 🚧 STUB — Ghost-tier exercise.** The framework is in place
but `latest_10k_accession`, `pull_exhibit_21`, and
`usaspending_contracts` are deliberately unimplemented. Ghost-tier
students implement them as Lab-Module-1-Ghost Path A.

Hunter students: you don't need this script. Your lab does the
same work in a browser with no ambiguity about whether it worked.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `ModuleNotFoundError: mmh3` | missing dep | `pip install mmh3` |
| `ModuleNotFoundError: bs4` | missing bs4 | `pip install beautifulsoup4` |
| `ModuleNotFoundError: simplekml` | missing dep | `pip install simplekml` |
| `502` from crt.sh | classroom load | use `../Mirrors/crtsh/*.json` |
| `429` from Shodan InternetDB | rate limited | dedupe to distinct IPs, jittered sleep |
| Empty favicon / 404 | no `/favicon.ico` | script auto-falls-back to `<link rel=icon>` |
| Nominatim returning blank | VPN blocked by OSM | switch VPN exit or use Census TIGER primary |

---

## If you improve a script

If you write a fix or an extension that's genuinely useful (e.g.,
implementing the `domain_to_org.py` stubs), mention it in the
shout-outs at 15:40 or open a PR against the public repo after
class. Practical improvements to this toolkit become the template
for the next workshop's tools.
