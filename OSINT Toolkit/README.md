# Wildcard OSINT Toolkit

Passive OSINT scripts for corporate attack surface mapping. Built for the
"From Domain to Dossier" workshop at BSides KC 2026 (OSINT Village),
maintained by Wildcard LLC.

Everything in this repo is **passive**: no active scanning, no auth bypass,
no contact attempts. Use it on targets you have legitimate reason to
research — bug bounty scopes, your own infrastructure, due diligence
subjects.

## Quickstart

```bash
git clone https://github.com/Ginsberg5150/OSINT-Village-BsidesKC-2026.git
cd OSINT-Village-BsidesKC-2026
pip install -r requirements.txt

# One-shot interactive setup (optional — scripts also prompt as needed)
python3 setup.py

# Build a passive dossier for a domain
python3 scripts/domain_to_dossier.py shopify.com -o shopify.md

# Pull subsidiaries from SEC EDGAR Exhibit 21 (CIK or company name)
python3 scripts/edgar_subsidiaries.py "Apple"

# Other focused tools
python3 scripts/cert_enum.py example.com
python3 scripts/favicon_pivot.py example.com
python3 scripts/plants_to_kml.py plants.csv -o out.kml
```

## What's in here

```
.
├── README.md                  this file
├── LICENSE                    MIT + ethical-use statement
├── UPGRADE_NOTES.md           what changed in v2
├── requirements.txt           Python dependencies
├── .env.example               optional API keys — copy to .env
├── setup.py                   interactive first-time config wizard
│
├── scripts/
│   ├── lib/
│   │   └── osint_common.py    shared helpers (config, prompts, HTTP)
│   ├── domain_to_dossier.py   flagship — domain → markdown dossier
│   ├── edgar_subsidiaries.py  SEC EDGAR Exhibit 21 → subsidiary list
│   ├── cert_enum.py           crt.sh + certspotter subdomain enum
│   ├── favicon_pivot.py       favicon mmh3 hash → Shodan / Censys pivot
│   └── plants_to_kml.py       facility CSV → Google Earth KML
│
├── queries/
│   ├── shodan.md              curated Shodan search dorks
│   ├── google_dorks.md        corporate recon Google dorks
│   └── github_dorks.md        secret-hunting GitHub dorks
│
└── targets/
    └── practice_scopes.md     safe practice targets (bug bounty programs)
```

## The five scripts at a glance

| Script | Input | Output | Notes |
|---|---|---|---|
| `domain_to_dossier.py` | a domain | Markdown + JSON dossier | Chains crt.sh, certspotter, DNS, Team Cymru ASN, Shodan InternetDB, optional Shodan API. Per-source fault tolerance. Reports a 0-100 completeness score. |
| `edgar_subsidiaries.py` | CIK or company name | subsidiary list (Admiralty A1) | Resolves names via SEC tickers file. Pulls latest 10-K Exhibit 21. Requires CONTACT_EMAIL (SEC mandate). |
| `cert_enum.py` | a domain | sorted subdomain list | Tries crt.sh first, falls back to certspotter automatically. |
| `favicon_pivot.py` | URL or domain | favicon hash + manual pivot URLs | Always prints search URLs for Shodan / Censys / ZoomEye / FOFA so you get value even with no API key. |
| `plants_to_kml.py` | CSV (name, address, ...) | KML for Google Earth | Geocodes via OSM Nominatim. Caches results so re-runs are free. Failed rows go to `<output>_failures.csv`. |

## How the prompting works

When a script needs something it doesn't have, it asks you — and offers to
save the answer to `.env` so you only type it once:

```
[!] Missing required config: Your contact email (CONTACT_EMAIL)
    Used for: SEC EDGAR, OSM Nominatim geocoder

  Your contact email: you@example.com
  Save to .env for future runs? [Y/n]: y
[+] Saved CONTACT_EMAIL to /path/to/.env
```

The next run picks it up automatically. Same flow for optional API keys
(Shodan, Censys, etc.) — except those are skippable; the scripts degrade
gracefully when keys aren't available.

## Configuration

All values are in `.env` (copy `.env.example` and fill in what you have).
Run `python3 setup.py` to walk through them interactively.

| Key | Required? | Used by | Where to get |
|---|---|---|---|
| `CONTACT_EMAIL` | **YES** for SEC + Nominatim | edgar, plants_to_kml | use a real working email |
| `SHODAN_API_KEY` | optional | dossier, favicon | https://account.shodan.io |
| `CENSYS_API_ID` + `CENSYS_API_SECRET` | optional | future | https://platform.censys.io |
| `OPENCORPORATES_API_KEY` | optional | TPRM workflows | https://opencorporates.com/api_accounts/new |
| `NVD_API_KEY` | optional | future | https://nvd.nist.gov/developers/request-an-api-key |
| `HUNTER_API_KEY` | optional | future | https://hunter.io/api |

## Ethical use

This toolkit is for defensive security research, due diligence, bug
bounty work in scope, investigative journalism, and education. Use only
on targets you are authorized to research. Don't harass, dox, or stalk.

OSINT is a tool. Use it to protect, not to attack.
