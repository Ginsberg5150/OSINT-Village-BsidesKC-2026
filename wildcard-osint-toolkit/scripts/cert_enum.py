#!/usr/bin/env python3
"""
cert_enum.py — Wildcard OSINT Toolkit
crt.sh certificate-transparency subdomain enumerator (with fallback)

What's new in v2:
  - Prompts for a domain if you forget to pass one (instead of usage error)
  - Retries crt.sh automatically on 403 / 5xx / timeout (Cloudflare bug)
  - Falls back to certspotter (https://certspotter.com) if crt.sh is dead
  - Validates the domain you give it (strips https://, paths, ports, etc.)
  - Reports what failed in plain language

Usage:
    python3 cert_enum.py example.com
    python3 cert_enum.py                       # prompts for domain
    python3 cert_enum.py example.com -o subs.txt
    python3 cert_enum.py example.com --include-wildcards
    python3 cert_enum.py example.com --json
    python3 cert_enum.py example.com --source crtsh|certspotter|both

Admiralty rating of output: B2
    B — CT log aggregators are usually-reliable secondary sources
    2 — each subdomain probably existed at issuance time, but
        may be stale or never have resolved
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Make the lib/ shared helpers importable
sys.path.insert(0, str(Path(__file__).parent / "lib"))
from osint_common import (  # noqa: E402
    banner, info, warn, error, success,
    http_get_json, prompt_for, validate_domain,
    ConfigError,
)


def _query_crtsh(domain: str, include_wildcards: bool) -> set[str]:
    """Pull subdomains from crt.sh's JSON endpoint. Raises on hard failure."""
    info(f"Querying crt.sh for %.{domain}")
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    data = http_get_json(url, timeout=45, retries=4)
    return _extract_names(data, domain, include_wildcards, name_field="name_value")


def _query_certspotter(domain: str, include_wildcards: bool) -> set[str]:
    """Pull subdomains from certspotter's free issuances API. Raises on failure."""
    info(f"Querying certspotter for {domain}")
    url = (
        f"https://api.certspotter.com/v1/issuances"
        f"?domain={domain}&include_subdomains=true&expand=dns_names"
    )
    data = http_get_json(url, timeout=45, retries=3)
    subs: set[str] = set()
    for entry in data:
        for name in entry.get("dns_names", []) or []:
            cleaned = _clean_name(name, domain, include_wildcards)
            if cleaned:
                subs.add(cleaned)
    return subs


def _extract_names(
    data, domain: str, include_wildcards: bool, name_field: str
) -> set[str]:
    subs: set[str] = set()
    for entry in data:
        raw = entry.get(name_field, "")
        for name in raw.split("\n") if isinstance(raw, str) else raw:
            cleaned = _clean_name(name, domain, include_wildcards)
            if cleaned:
                subs.add(cleaned)
    return subs


def _clean_name(name: str, domain: str, include_wildcards: bool) -> str | None:
    name = (name or "").strip().lower()
    if not name:
        return None
    if name.startswith("*."):
        if not include_wildcards:
            return None
        name = name[2:]
    if name == domain or name.endswith("." + domain):
        return name
    return None


def main() -> int:
    p = argparse.ArgumentParser(
        description="Enumerate subdomains from Certificate Transparency logs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="If you don't pass a domain, the script will prompt for one.",
    )
    p.add_argument("domain", nargs="?", help="root domain, e.g. example.com")
    p.add_argument("-o", "--output", help="write results to file")
    p.add_argument(
        "--include-wildcards",
        action="store_true",
        help="include wildcard certs (*.example.com)",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="emit JSON with metadata instead of bare list",
    )
    p.add_argument(
        "--source",
        choices=["crtsh", "certspotter", "both"],
        default="both",
        help="CT log source (default: both — tries crt.sh first, falls back)",
    )
    args = p.parse_args()

    banner("cert_enum.py", "Certificate Transparency subdomain enumerator")

    # --- resolve domain (CLI arg → prompt) ---
    domain_raw = args.domain
    if not domain_raw:
        try:
            domain_raw = prompt_for(
                "Target domain",
                description="Which domain do you want subdomains for?",
                examples=["shopify.com", "yelp.com", "caterpillar.com"],
                validator=validate_domain,
            )
        except ConfigError as e:
            error(str(e))
            return 2
    else:
        ok, cleaned, msg = validate_domain(domain_raw)
        if not ok:
            error(msg)
            return 2
        domain_raw = cleaned

    domain = domain_raw

    # --- run sources with graceful fallback ---
    all_subs: set[str] = set()
    tried = []

    # crtsh first (more comprehensive)
    if args.source in ("crtsh", "both"):
        try:
            all_subs.update(_query_crtsh(domain, args.include_wildcards))
            tried.append("crt.sh")
        except Exception as e:
            warn(f"crt.sh failed: {type(e).__name__}: {e}")
            if args.source == "crtsh":
                error("crt.sh was the only source requested. Try --source both or certspotter.")
                return 3

    # certspotter (fallback or both)
    if args.source in ("certspotter", "both"):
        # Skip certspotter if crtsh already gave us results AND user said both
        # (saves their certspotter quota). Override: --source certspotter forces it.
        if args.source == "certspotter" or not all_subs:
            try:
                all_subs.update(_query_certspotter(domain, args.include_wildcards))
                tried.append("certspotter")
            except Exception as e:
                warn(f"certspotter failed: {type(e).__name__}: {e}")
                if not all_subs:
                    error("Both CT sources failed. Check connectivity and try again.")
                    return 3

    if not all_subs:
        warn("No subdomains found. The domain may be very new, or may not have any "
             "publicly-logged certificates.")
        return 0

    sorted_subs = sorted(all_subs)
    success(f"Found {len(sorted_subs)} unique subdomain(s) via {', '.join(tried)}")

    # --- emit ---
    if args.json:
        payload = {
            "domain": domain,
            "queried_utc": datetime.now(timezone.utc).isoformat(),
            "sources": tried,
            "include_wildcards": args.include_wildcards,
            "count": len(sorted_subs),
            "subdomains": sorted_subs,
            "admiralty_rating": "B2",
        }
        text = json.dumps(payload, indent=2)
    else:
        text = "\n".join(sorted_subs)

    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
        success(f"Wrote {args.output}")
    else:
        print(text)

    return 0


if __name__ == "__main__":
    sys.exit(main())
