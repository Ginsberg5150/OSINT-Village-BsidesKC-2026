#!/usr/bin/env python3
"""
cert_enum.py — OSINT Village BSides KC 2026 Toolkit (Wildcard Industries LLC)
From Domain to Dossier · BSides KC 2026 · OSINT Village

Focused crt.sh certificate transparency subdomain enumerator.

Every TLS certificate issued anywhere on the internet is logged in
public Certificate Transparency logs. crt.sh is the searchable
frontend. This is the single most valuable passive subdomain source.

Usage:
    python3 cert_enum.py example.com
    python3 cert_enum.py example.com --output subs.txt
    python3 cert_enum.py example.com --include-wildcards
    python3 cert_enum.py example.com --json

Admiralty rating of output: B2
    B — crt.sh is a usually-reliable aggregator of CT logs
    2 — each subdomain probably existed at issuance time, but
        may be stale or never have resolved

Dependencies: pip install requests
"""

import argparse
import json
import sys
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    print("[!] requests required: pip install requests", file=sys.stderr)
    sys.exit(1)

USER_AGENT = "osint-village-bsideskc-2026/1.0 (https://github.com/Ginsberg5150/OSINT-Village-BsidesKC-2026)"


def enumerate_crtsh(domain: str, include_wildcards: bool = False) -> list:
    """Return a sorted list of unique subdomains seen in CT logs."""
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    r.raise_for_status()
    subs = set()
    for entry in r.json():
        for name in entry.get("name_value", "").split("\n"):
            name = name.strip().lower()
            if not name:
                continue
            if name.startswith("*."):
                if not include_wildcards:
                    continue
                name = name[2:]
            if name == domain or name.endswith("." + domain):
                subs.add(name)
    return sorted(subs)


def main():
    p = argparse.ArgumentParser(description="crt.sh CT-log subdomain enumerator")
    p.add_argument("domain", help="root domain, e.g. example.com")
    p.add_argument("--output", "-o", default=None, help="write list to file")
    p.add_argument("--include-wildcards", action="store_true",
                   help="include wildcard certs (*.example.com)")
    p.add_argument("--json", action="store_true",
                   help="emit JSON with metadata instead of bare list")
    args = p.parse_args()

    domain = args.domain.strip().lower().lstrip("*.")
    print(f"[*] querying crt.sh for %.{domain}", file=sys.stderr)

    try:
        subs = enumerate_crtsh(domain, args.include_wildcards)
    except requests.HTTPError as e:
        print(f"[!] crt.sh HTTP error: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"[!] error: {e}", file=sys.stderr)
        sys.exit(2)

    print(f"[+] {len(subs)} unique subdomains", file=sys.stderr)

    if args.json:
        payload = {
            "domain": domain,
            "source": "crt.sh",
            "admiralty": "B2",
            "queried_at": datetime.now(timezone.utc).isoformat(),
            "count": len(subs),
            "subdomains": subs,
        }
        output = json.dumps(payload, indent=2)
    else:
        output = "\n".join(subs)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output + "\n")
        print(f"[+] wrote {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
