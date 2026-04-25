# Wildcard OSINT Toolkit — v2 Upgrade Notes

## What changed

The core problem in v1 was that scripts crashed when a config value was
missing — wrong API key, no contact email, no domain on the command line —
instead of asking the user what to do. v2 fixes that across the board.

### New shared library: `scripts/lib/osint_common.py`

One module that handles:

- **Config loading** with priority order: process env → `.env` → interactive prompt → fallback
- **Interactive prompts** for missing required values, with offer to save the answer to `.env`
- **HTTP requests** with retries, exponential backoff, sane timeouts, and a User-Agent that includes the contact email (required by SEC + Nominatim)
- **Friendly errors** that explain what failed in plain English (401 = wrong key, 403 = missing UA email, 429 = rate limited, etc.)
- **Validators** for email, domain, CIK before they hit external APIs

Every script imports from this. No more copy-pasted retry loops.

### New script: `setup.py`

Run it once to walk through every config value interactively:

```bash
python3 setup.py
```

You don't have to use it — every script will prompt you for what it needs as you go. It's just the convenient way to do it all at once.

### New script: `scripts/edgar_subsidiaries.py`

Pulls the Exhibit 21 (subsidiaries list) from a public company's most recent 10-K. Accepts either a CIK number OR a company name (resolves the name via the SEC tickers file — no guessing).

```bash
python3 scripts/edgar_subsidiaries.py 320193          # by CIK
python3 scripts/edgar_subsidiaries.py "Shopify"       # by name
python3 scripts/edgar_subsidiaries.py                 # prompts you
```

This is the **A1** source for corporate ownership mapping (primary source, legally mandated). If you're doing TPRM or attack surface work on a US-listed public company, this is the first script to run.

### Refactored scripts

All four existing scripts now share the same UX patterns:

| Script | What's new |
|---|---|
| `domain_to_dossier.py` | Prompts for domain. Per-source fault tolerance (one source dying doesn't kill the run). Reports a 0-100 completeness score. Lists which sources contributed and which failed. |
| `cert_enum.py` | Prompts for domain. Falls back to certspotter automatically if crt.sh 403s (which it does intermittently from datacenter IPs). |
| `favicon_pivot.py` | Prompts for URL/domain. Always prints manual pivot URLs (Shodan, Censys, ZoomEye, FOFA) so you get value even without an API key. Auto-appends `/favicon.ico` if you give a bare domain. |
| `plants_to_kml.py` | Prompts for CSV path. Validates CSV headers and tells you which columns are missing. Prompts for `CONTACT_EMAIL` (required by Nominatim TOS). Geocoding is cached to `.geocode_cache.json` — re-runs are free. Failed rows go to `<output>_failures.csv` so you can fix and re-run. |

## Config — what you can set

All optional unless marked **REQ**.

| Key | Used by | Where to get |
|---|---|---|
| `CONTACT_EMAIL` **REQ** for SEC + Nominatim | `edgar_subsidiaries.py`, `plants_to_kml.py` | Use a real working email |
| `SHODAN_API_KEY` | `domain_to_dossier.py`, `favicon_pivot.py` | https://account.shodan.io/ |
| `CENSYS_API_ID` + `CENSYS_API_SECRET` | (future) | https://platform.censys.io/ |
| `OPENCORPORATES_API_KEY` | TPRM workflows | https://opencorporates.com/api_accounts/new |
| `NVD_API_KEY` | (future CVE enrichment) | https://nvd.nist.gov/developers/request-an-api-key |
| `HUNTER_API_KEY` | (future email enrichment) | https://hunter.io/api |

## Migrating from v1

Drop the new files into your existing repo. The new `scripts/` files are
drop-in replacements (same names, same arguments, same outputs — they
just don't crash anymore). The new `lib/` directory and `setup.py` are
additive.

If you had a `.env` already, it still works — the new code reads the same
keys plus the new `CONTACT_EMAIL`.

## How the prompting works

When a script needs something it doesn't have, it does this:

```
[!] Missing required config: Your contact email (CONTACT_EMAIL)
    Used for: SEC EDGAR, OSM Nominatim geocoder
    SEC EDGAR and OSM Nominatim REQUIRE a real contact email in the
    User-Agent header. Without it, requests silently fail or 403.

  Your contact email: you@example.com
  Save to .env for future runs? [Y/n]: y
[+] Saved CONTACT_EMAIL to /path/to/.env
```

The next time any script needs `CONTACT_EMAIL` it just uses the saved
value. No more re-typing, no more crashes.

## Quick reference

```bash
# First-time setup (optional — scripts will also prompt as you go)
python3 setup.py

# The five scripts
python3 scripts/domain_to_dossier.py shopify.com
python3 scripts/edgar_subsidiaries.py "Apple"
python3 scripts/cert_enum.py example.com
python3 scripts/favicon_pivot.py example.com
python3 scripts/plants_to_kml.py plants.csv -o out.kml

# All scripts respond to --help
python3 scripts/domain_to_dossier.py --help
```
