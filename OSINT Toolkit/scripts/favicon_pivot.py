#!/usr/bin/env python3
"""
favicon_pivot.py — Wildcard OSINT Toolkit
Hash a favicon and pivot to other hosts that serve the same one.

Why this exists:
  Many orgs serve the same custom favicon across all their owned hosts —
  even ones that don't appear in CT logs or DNS. Hashing the favicon and
  searching Shodan / Censys for matching hosts is one of the cleanest
  pivots in passive OSINT.

What's new in v2:
  - Prompts for the favicon URL if you forget to pass one
  - Prompts for SHODAN_API_KEY if missing, with help text + offer to save
  - Builds clickable URLs for Shodan + Censys + ZoomEye even without keys
    (so you can search manually) — never silently produces nothing
  - Tells you exactly what failed and how to fix it

Usage:
    python3 favicon_pivot.py https://example.com/favicon.ico
    python3 favicon_pivot.py example.com           # auto-appends /favicon.ico
    python3 favicon_pivot.py                       # prompts for URL
    python3 favicon_pivot.py example.com --query   # only print search URLs
    python3 favicon_pivot.py example.com --json
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path
from urllib.parse import quote_plus

# Make the lib/ shared helpers importable
sys.path.insert(0, str(Path(__file__).parent / "lib"))
from osint_common import (  # noqa: E402
    banner, info, warn, error, success, hint,
    http_get, get_config, prompt_for, validate_domain,
    ConfigError,
)

try:
    import mmh3
except ImportError:
    print(
        "[!] The `mmh3` library is required.\n"
        "    Install with:  pip install mmh3\n",
        file=sys.stderr,
    )
    sys.exit(1)


def normalize_favicon_url(raw: str) -> str:
    """Accept a domain or a full URL; produce a fetchable favicon URL."""
    raw = raw.strip()
    if raw.startswith(("http://", "https://")):
        if raw.endswith("/"):
            return raw + "favicon.ico"
        if "/favicon" in raw or raw.endswith((".ico", ".png", ".svg")):
            return raw
        return raw.rstrip("/") + "/favicon.ico"
    # Bare domain — assume https + /favicon.ico
    ok, cleaned, _ = validate_domain(raw)
    if ok:
        return f"https://{cleaned}/favicon.ico"
    # Last resort
    return f"https://{raw}/favicon.ico"


def shodan_favicon_hash(content: bytes) -> int:
    """Compute the Shodan-compatible favicon hash.

    Shodan's hash is mmh3.hash() of the base64-encoded favicon content,
    where the b64 has a newline every 76 chars and a trailing newline
    (the python-stdlib `base64.encodebytes` default — NOT b64encode).
    """
    b64 = base64.encodebytes(content)
    return mmh3.hash(b64)


def main() -> int:
    p = argparse.ArgumentParser(
        description="Compute a favicon mmh3 hash and pivot to matching hosts.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "target",
        nargs="?",
        help="favicon URL OR a domain (will append /favicon.ico)",
    )
    p.add_argument(
        "--query", action="store_true",
        help="just print pivot search URLs, don't call any APIs",
    )
    p.add_argument("--json", action="store_true", help="emit JSON")
    p.add_argument(
        "--max-results", type=int, default=20,
        help="max Shodan results to fetch (default: 20)",
    )
    args = p.parse_args()

    banner("favicon_pivot.py", "Hash a favicon, pivot to matching hosts")

    # --- resolve target ---
    target = args.target
    if not target:
        try:
            target = prompt_for(
                "Favicon URL or domain",
                description="What favicon should I hash?",
                examples=[
                    "https://shopify.com/favicon.ico",
                    "yelp.com",
                    "https://example.com/static/icon.png",
                ],
            )
        except ConfigError as e:
            error(str(e))
            return 2

    favicon_url = normalize_favicon_url(target)
    info(f"Fetching favicon: {favicon_url}")

    # --- fetch favicon ---
    try:
        r = http_get(favicon_url, timeout=15, retries=3, raise_for_status=False)
    except Exception as e:
        error(f"Could not fetch favicon: {type(e).__name__}: {e}")
        hint("Tip: try the bare domain (yelp.com) and let the script append /favicon.ico,\n"
             "or open the page in a browser and right-click the tab icon → copy URL.")
        return 3

    if r.status_code >= 400:
        error(f"Got {r.status_code} fetching {favicon_url}")
        hint("The site may not have a favicon at /favicon.ico. Check page source for a <link rel='icon'> tag.")
        return 3

    if not r.content:
        error("Got an empty response — no favicon bytes to hash.")
        return 3

    fhash = shodan_favicon_hash(r.content)
    success(f"Favicon hash (Shodan-compatible mmh3): {fhash}")
    info(f"Bytes: {len(r.content)}, Content-Type: {r.headers.get('Content-Type', 'unknown')}")

    # --- always build manual pivot URLs ---
    pivots = {
        "shodan_web": f"https://www.shodan.io/search?query={quote_plus(f'http.favicon.hash:{fhash}')}",
        "censys_web": f"https://search.censys.io/search?resource=hosts&q={quote_plus(f'services.http.response.favicons.shodan_hash: {fhash}')}",
        "zoomeye_web": f"https://www.zoomeye.org/searchResult?q={quote_plus(f'iconhash:\"{fhash}\"')}",
        "fofa_web": f"https://fofa.info/result?qbase64={base64.b64encode(f'icon_hash=\"{fhash}\"'.encode()).decode()}",
    }

    print("", file=sys.stderr)
    info("Manual pivot URLs (open in a browser):")
    for name, url in pivots.items():
        print(f"  {name:13} {url}", file=sys.stderr)

    if args.query:
        if args.json:
            print(json.dumps({"favicon_url": favicon_url, "hash": fhash, "pivots": pivots}, indent=2))
        return 0

    # --- try Shodan API for live results ---
    matches: list[dict] = []
    shodan_key = None
    try:
        shodan_key = get_config("SHODAN_API_KEY", prompt=True, save=True)
    except ConfigError:
        pass

    if shodan_key:
        info("Querying Shodan API for live matches...")
        try:
            data = _shodan_search(fhash, shodan_key, args.max_results)
            for m in data.get("matches", []):
                matches.append({
                    "ip": m.get("ip_str"),
                    "port": m.get("port"),
                    "org": m.get("org"),
                    "hostnames": m.get("hostnames", []),
                    "title": (m.get("http") or {}).get("title"),
                    "asn": m.get("asn"),
                    "country": (m.get("location") or {}).get("country_name"),
                })
            success(f"Shodan returned {len(matches)} match(es) (showing up to {args.max_results})")
        except Exception as e:
            warn(f"Shodan API call failed: {type(e).__name__}: {e}")
            hint("You can still use the manual Shodan URL above to browse results.")
    else:
        warn("No SHODAN_API_KEY available — skipping live API query.")
        hint("Use the manual Shodan URL above, or set the key with the setup wizard.")

    # --- emit ---
    if args.json:
        payload = {
            "favicon_url": favicon_url,
            "favicon_hash": fhash,
            "favicon_bytes": len(r.content),
            "pivots": pivots,
            "shodan_matches": matches,
            "admiralty_rating": "B2",
        }
        print(json.dumps(payload, indent=2))
    else:
        if matches:
            print("\n=== Shodan matches ===")
            for m in matches:
                hosts = ", ".join(m["hostnames"]) if m["hostnames"] else "—"
                print(f"  {m['ip']}:{m['port']}  org={m['org'] or '—'}  hosts=[{hosts}]")
        else:
            print(f"\nNo live matches retrieved. Hash: {fhash}")
            print("Open the manual URLs above to search by hand.")

    return 0


def _shodan_search(fhash: int, api_key: str, limit: int) -> dict:
    url = (
        f"https://api.shodan.io/shodan/host/search"
        f"?key={api_key}&query={quote_plus(f'http.favicon.hash:{fhash}')}"
    )
    r = http_get(url, timeout=30, retries=3, raise_for_status=False)
    if r.status_code == 401:
        raise RuntimeError("Shodan rejected the API key (401). Check it at https://account.shodan.io/")
    if r.status_code == 403:
        raise RuntimeError("403 — your Shodan plan may not include search API access.")
    r.raise_for_status()
    data = r.json()
    if "matches" in data and len(data["matches"]) > limit:
        data["matches"] = data["matches"][:limit]
    return data


if __name__ == "__main__":
    sys.exit(main())
