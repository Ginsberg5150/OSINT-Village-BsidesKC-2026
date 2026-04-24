#!/usr/bin/env python3
"""
favicon_pivot.py — OSINT Village BSides KC 2026 Toolkit (Wildcard Industries LLC)
From Domain to Dossier · BSides KC 2026 · OSINT Village

Compute the Shodan-style mmh3 hash of a website's favicon and emit a
ready-to-click Shodan search URL that finds every other host in the
world serving the same favicon.

This is one of the single best recon pivots there is: an admin panel
hidden behind a weird hostname usually has the same favicon as the
vendor's public page. The favicon hash finds all of them.

Usage:
    # Hash the favicon at example.com/favicon.ico
    python3 favicon_pivot.py https://example.com

    # Point at a specific favicon URL
    python3 favicon_pivot.py https://example.com/static/favicon.ico

    # Just print the hash, no URL
    python3 favicon_pivot.py https://example.com --hash-only

Admiralty rating of output: C2
    C — hash pivots produce plausible related infrastructure but
        shared favicons occur for mundane reasons (stock CMS, CDN)
    2 — pivoted host is probably related but confirm with DNS/WHOIS

Dependencies: pip install requests mmh3
"""

import argparse
import base64
import sys
from urllib.parse import urljoin, urlparse

try:
    import requests
except ImportError:
    print("[!] requests required: pip install requests", file=sys.stderr)
    sys.exit(1)

try:
    import mmh3
except ImportError:
    print("[!] mmh3 required: pip install mmh3", file=sys.stderr)
    sys.exit(1)

USER_AGENT = "osint-village-bsideskc-2026/1.0 (https://github.com/Ginsberg5150/OSINT-Village-BsidesKC-2026)"


def _try_link_rel_icon(page_url: str) -> bytes:
    """QA fix: fallback when /favicon.ico 404s. Fetch the page HTML and
    parse <link rel="icon" href="..."> to find the real favicon URL."""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        raise RuntimeError("beautifulsoup4 required for link-rel fallback: "
                           "pip install beautifulsoup4")

    parsed = urlparse(page_url)
    base = f"{parsed.scheme}://{parsed.netloc}"

    print(f"[*] favicon.ico not found — parsing <link rel=icon> in {base}",
          file=sys.stderr)
    r = requests.get(base, headers={"User-Agent": USER_AGENT}, timeout=15,
                     allow_redirects=True)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # Try in priority order: rel="icon", rel="shortcut icon", rel="apple-touch-icon"
    for rel in ("icon", "shortcut icon", "apple-touch-icon"):
        link = soup.find("link", rel=lambda v: v and rel in (v if isinstance(v, list) else [v]))
        if link and link.get("href"):
            icon_url = urljoin(base, link["href"])
            print(f"[*] found icon link: {icon_url}", file=sys.stderr)
            ri = requests.get(icon_url, headers={"User-Agent": USER_AGENT},
                              timeout=15, allow_redirects=True)
            ri.raise_for_status()
            return ri.content

    raise RuntimeError(f"no favicon and no <link rel=icon> in {base}")


def fetch_favicon(url: str) -> bytes:
    """Fetch favicon bytes. If URL is a page, try /favicon.ico, then
    fall back to parsing <link rel='icon'> from the page HTML."""
    parsed = urlparse(url)
    if not parsed.scheme:
        url = "https://" + url
        parsed = urlparse(url)

    # If the URL path doesn't look like a favicon, try /favicon.ico
    path_lower = parsed.path.lower()
    page_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path or '/'}"
    if not (path_lower.endswith(".ico") or path_lower.endswith(".png") or
            "favicon" in path_lower):
        url = urljoin(f"{parsed.scheme}://{parsed.netloc}", "/favicon.ico")

    print(f"[*] fetching favicon: {url}", file=sys.stderr)
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15,
                         allow_redirects=True)
        r.raise_for_status()
        if len(r.content) < 64:
            raise RuntimeError(f"favicon at {url} is suspiciously small "
                              f"({len(r.content)} bytes)")
        return r.content
    except (requests.HTTPError, RuntimeError) as e:
        # QA fix: fallback to <link rel="icon"> parsing
        print(f"[!] {e} — trying link-rel fallback", file=sys.stderr)
        return _try_link_rel_icon(page_url)


def shodan_favicon_hash(data: bytes) -> int:
    """Replicate Shodan's favicon hash: mmh3.hash of base64-encoded bytes."""
    encoded = base64.encodebytes(data)
    return mmh3.hash(encoded)


def main():
    p = argparse.ArgumentParser(
        description="Compute Shodan favicon hash and emit pivot URL"
    )
    p.add_argument("url", help="website URL or direct favicon URL")
    p.add_argument("--hash-only", action="store_true",
                   help="print just the hash, no Shodan URL")
    args = p.parse_args()

    try:
        data = fetch_favicon(args.url)
    except Exception as e:
        print(f"[!] fetch error: {e}", file=sys.stderr)
        sys.exit(2)

    h = shodan_favicon_hash(data)
    print(f"[+] favicon bytes: {len(data)}", file=sys.stderr)
    print(f"[+] mmh3 hash: {h}", file=sys.stderr)

    if args.hash_only:
        print(h)
        return

    shodan_url = f"https://www.shodan.io/search?query=http.favicon.hash%3A{h}"
    print()
    print(f"Hash:        {h}")
    print(f"Shodan URL:  {shodan_url}")
    print()
    print("Try in Censys too: services.http.response.favicons.md5_hash "
          "(different algorithm — MD5 of bytes, not mmh3 of base64).")


if __name__ == "__main__":
    main()
