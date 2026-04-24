#!/usr/bin/env python3
"""
domain_to_dossier.py — OSINT Village BSides KC 2026 Toolkit (Wildcard Industries LLC)
From Domain to Dossier · BSides KC 2026 · OSINT Village

Takes a single domain and produces a structured passive-OSINT dossier
by chaining certificate transparency, subdomain enumeration, DNS
resolution, ASN/ownership lookup, passive port info (Shodan InternetDB),
and optional deep Shodan and CVE correlation.

All data sources are passive. No active scanning. No auth bypass.
No contact attempts.

=========================================================================
⚠️  CLASS-DAY STATUS — READ BEFORE SHIPPING TO STUDENTS
=========================================================================

This script was ported from the pre-2026 Wildcard OSINT Toolkit with
branding/URL updates only. The QA review of this workshop's test run
identified several production-grade fixes that should be applied before
the script fully matches the behavior described in the class modules:

TODO (QA-flagged, not yet in this code):
  1. SOURCE ORDER — chain should be:
       subfinder (if installed) → crt.sh raw → Wayback CDX →
       Shodan InternetDB (on distinct IPs only) →
       Cymru ASN DNS → bgp.he.net scrape → (optional) VT.
     Currently the script hits crt.sh first, then InternetDB per-host.
  2. --mirror-dir <path>
     If set, on 429/5xx from upstream, read the mirror at
     {mirror-dir}/{source}/{target}.json instead of failing.
     (`Mirrors/crtsh/caterpillar.json` etc. are shipped ready for this.)
  3. --keyless
     Skip any key-gated source (VT, etc.) with a single-line rationale
     per skip. Default behavior otherwise unchanged.
  4. --no-vt / --no-internetdb
     Per-source skip flags for classroom rate-limit management.
  5. InternetDB dedupe
     Build a set of distinct resolved IPs FIRST, hit InternetDB once
     per IP rather than once per hostname.
  6. Jittered 1.0–1.5s sleep
     Between polled calls. Avoids rate-limit clustering when 30 students
     run this simultaneously.
  7. PatentsView → Google Patents
     Default to Google Patents for patent pivots; PatentsView API now
     requires a key.

Students: for today, the script as-is will produce a useful base
dossier. You'll add narrative value on top (executive summary,
notable findings, footprint self-audit) by hand in Module 5.

Instructors: applying the fixes above is tracked as a post-class
improvement; the Instructor-Only/ materials (not shipped in this
public repo) have the detailed spec.
=========================================================================

Usage:
    python3 domain_to_dossier.py example.com
    python3 domain_to_dossier.py example.com --output mydossier.md --json mydossier.json

Optional environment variables:
    SHODAN_API_KEY     — enables deep Shodan host lookups (banners, HTTP, SSL)
    CENSYS_API_ID      — enables Censys host lookups (paired with secret)
    CENSYS_API_SECRET
    NVD_API_KEY        — speeds up NVD CVE lookups (not required)

Dependencies:
    pip install requests dnspython
"""

import argparse
import concurrent.futures
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    print("[!] requests required: pip install requests", file=sys.stderr)
    sys.exit(1)

try:
    import dns.resolver
    HAS_DNS = True
except ImportError:
    HAS_DNS = False
    print("[*] dnspython not installed — DNS features disabled "
          "(pip install dnspython)", file=sys.stderr)

# ============================================================
# Config
# ============================================================

USER_AGENT = "osint-village-bsideskc-2026/1.0 (https://github.com/Ginsberg5150/OSINT-Village-BsidesKC-2026)"
HTTP_TIMEOUT = 15
MAX_WORKERS = 10


@dataclass
class Dossier:
    domain: str
    generated_at: str
    subdomains: dict = field(default_factory=dict)   # sub → [IPs]
    asns: dict = field(default_factory=dict)         # ip  → {asn, org, country, prefix}
    services: dict = field(default_factory=dict)    # ip  → InternetDB data
    shodan_deep: dict = field(default_factory=dict) # ip  → full Shodan host data
    cves: list = field(default_factory=list)
    tools_available: list = field(default_factory=list)
    notes: list = field(default_factory=list)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(msg: str, level: str = "*") -> None:
    prefix = {"*": "[*]", "+": "[+]", "!": "[!]"}.get(level, "[ ]")
    print(f"{prefix} {msg}", file=sys.stderr)


def is_installed(cmd: str) -> bool:
    """Check if a command is in PATH."""
    try:
        subprocess.run(
            [cmd, "-h"], capture_output=True, timeout=5
        )
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        try:
            subprocess.run(
                [cmd, "--help"], capture_output=True, timeout=5
            )
            return True
        except Exception:
            return False


# ============================================================
# Phase 1: Subdomain Enumeration (passive only)
# ============================================================

def crtsh_enum(domain: str) -> set:
    """Pull subdomains from crt.sh certificate transparency logs."""
    log(f"crt.sh: querying certificate transparency for {domain}")
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    try:
        r = requests.get(
            url, headers={"User-Agent": USER_AGENT}, timeout=HTTP_TIMEOUT
        )
        r.raise_for_status()
        subs = set()
        for entry in r.json():
            for name in entry.get("name_value", "").split("\n"):
                name = name.strip().lower().lstrip("*.")
                if name and (name == domain or name.endswith("." + domain)):
                    subs.add(name)
        log(f"crt.sh: {len(subs)} unique subdomains", "+")
        return subs
    except Exception as e:
        log(f"crt.sh failed: {e}", "!")
        return set()


def subfinder_enum(domain: str) -> set:
    """Run subfinder passively if installed (ProjectDiscovery)."""
    if not is_installed("subfinder"):
        log("subfinder: not installed, skipping")
        return set()
    log("subfinder: running passive enumeration")
    try:
        r = subprocess.run(
            ["subfinder", "-silent", "-d", domain],
            capture_output=True, text=True, timeout=180
        )
        subs = {
            line.strip().lower()
            for line in r.stdout.splitlines()
            if line.strip() and line.strip().lower().endswith(domain)
        }
        log(f"subfinder: {len(subs)} subdomains", "+")
        return subs
    except Exception as e:
        log(f"subfinder: {e}", "!")
        return set()


def amass_enum(domain: str) -> set:
    """Run amass in passive mode if installed."""
    if not is_installed("amass"):
        log("amass: not installed, skipping")
        return set()
    log("amass: running passive enumeration")
    try:
        r = subprocess.run(
            ["amass", "enum", "-passive", "-d", domain],
            capture_output=True, text=True, timeout=240
        )
        subs = {
            line.strip().lower()
            for line in r.stdout.splitlines()
            if line.strip() and line.strip().lower().endswith(domain)
        }
        log(f"amass: {len(subs)} subdomains", "+")
        return subs
    except Exception as e:
        log(f"amass: {e}", "!")
        return set()


# ============================================================
# Phase 2: DNS Resolution
# ============================================================

def resolve_bulk(subdomains: set) -> dict:
    """Resolve each subdomain to IPs concurrently."""
    if not HAS_DNS or not subdomains:
        return {s: [] for s in subdomains}
    log(f"resolving {len(subdomains)} subdomains")
    resolver = dns.resolver.Resolver()
    resolver.timeout = 3
    resolver.lifetime = 5

    def resolve_one(sub):
        try:
            answers = resolver.resolve(sub, "A")
            return sub, sorted(a.to_text() for a in answers)
        except Exception:
            return sub, []

    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        for sub, ips in ex.map(resolve_one, subdomains):
            results[sub] = ips

    resolved = sum(1 for ips in results.values() if ips)
    log(f"resolved: {resolved}/{len(subdomains)}", "+")
    return results


# ============================================================
# Phase 3: ASN & Ownership (Team Cymru via DNS)
# ============================================================

def cymru_lookup(ip: str) -> dict:
    """Team Cymru ASN/org lookup via DNS TXT records. No API key needed."""
    if not HAS_DNS:
        return {}
    try:
        octets = ip.split(".")
        if len(octets) != 4:
            return {}
        rdns = f"{octets[3]}.{octets[2]}.{octets[1]}.{octets[0]}.origin.asn.cymru.com"
        resolver = dns.resolver.Resolver()
        resolver.timeout = 2
        resolver.lifetime = 4
        answers = resolver.resolve(rdns, "TXT")
        # Format: "ASN | BGP Prefix | CountryCode | Registry | Allocated"
        txt = str(answers[0]).strip('"')
        fields = [f.strip() for f in txt.split("|")]
        asn = fields[0].split()[0] if fields else ""
        org = ""
        if asn:
            try:
                as_ans = resolver.resolve(f"AS{asn}.asn.cymru.com", "TXT")
                as_txt = str(as_ans[0]).strip('"')
                as_fields = [f.strip() for f in as_txt.split("|")]
                if len(as_fields) >= 5:
                    org = as_fields[4]
            except Exception:
                pass
        return {
            "asn": asn,
            "prefix": fields[1] if len(fields) > 1 else "",
            "country": fields[2] if len(fields) > 2 else "",
            "org": org,
        }
    except Exception:
        return {}


def asn_lookup_bulk(ips: set) -> dict:
    """Look up ASN for each unique IP."""
    if not ips:
        return {}
    log(f"ASN lookup: {len(ips)} IPs via Team Cymru")
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        for ip, info in zip(ips, ex.map(cymru_lookup, ips)):
            if info:
                results[ip] = info
    log(f"ASN lookup: {len(results)}/{len(ips)} resolved", "+")
    return results


# ============================================================
# Phase 4: Passive port/service info — Shodan InternetDB (free)
# ============================================================

def internetdb(ip: str) -> dict:
    """Shodan InternetDB — free, no API key. Returns ports/CPEs/tags/vulns."""
    try:
        r = requests.get(
            f"https://internetdb.shodan.io/{ip}",
            headers={"User-Agent": USER_AGENT},
            timeout=HTTP_TIMEOUT,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}


def internetdb_bulk(ips: set) -> dict:
    """Query InternetDB for each IP. This is the free-tier workhorse."""
    if not ips:
        return {}
    log(f"Shodan InternetDB: querying {len(ips)} IPs (free tier)")
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        for ip, data in zip(ips, ex.map(internetdb, ips)):
            if data and (data.get("ports") or data.get("vulns")):
                results[ip] = data
    log(f"InternetDB: data on {len(results)}/{len(ips)} IPs", "+")
    return results


# ============================================================
# Phase 5: Deep Shodan (API key required — optional)
# ============================================================

def shodan_host(ip: str, api_key: str) -> dict:
    """Deep Shodan lookup — banners, HTTP, SSL. Burns a query credit."""
    try:
        r = requests.get(
            f"https://api.shodan.io/shodan/host/{ip}",
            params={"key": api_key},
            timeout=HTTP_TIMEOUT,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}


# ============================================================
# Output rendering
# ============================================================

ADMIRALTY_KEY = """
| Code | Source Reliability | Information Credibility |
|------|--------------------|-------------------------|
| A | Completely reliable | 1 Confirmed by other sources |
| B | Usually reliable | 2 Probably true |
| C | Fairly reliable | 3 Possibly true |
| D | Not usually reliable | 4 Doubtful |
| E | Unreliable | 5 Improbable |
| F | Cannot be judged | 6 Cannot be judged |
"""


def render_markdown(dossier: Dossier) -> str:
    md = []
    md.append(f"# Dossier: {dossier.domain}")
    md.append(f"\n*Generated by `osint-village-bsideskc-2026` / `domain_to_dossier.py`*")
    md.append(f"*Generated at: {dossier.generated_at}*")
    md.append("\n> **Passive OSINT only.** No active scanning was performed. "
              "All findings derive from public sources — certificate transparency, "
              "DNS, BGP/ASN data, and Shodan InternetDB (passive).")

    md.append("\n## Admiralty Code Key\n")
    md.append(ADMIRALTY_KEY.strip())

    md.append("\n## Summary")
    md.append(f"- Tools available at runtime: {', '.join(dossier.tools_available) or 'crt.sh only'}")
    md.append(f"- Subdomains discovered: **{len(dossier.subdomains)}**")
    md.append(f"- Subdomains resolved: **{sum(1 for ips in dossier.subdomains.values() if ips)}**")
    md.append(f"- Unique IPs: **{len(dossier.asns) or len({ip for ips in dossier.subdomains.values() for ip in ips})}**")
    md.append(f"- Hosts with passive port data: **{len(dossier.services)}**")
    md.append(f"- Known CVEs correlated: **{len(dossier.cves)}**")

    md.append("\n## Subdomains & Resolution")
    md.append("*Source: crt.sh + subfinder/amass (when available) · Admiralty: **B2***\n")
    md.append("| Subdomain | IP(s) |")
    md.append("|-----------|-------|")
    for sub in sorted(dossier.subdomains.keys()):
        ips = ", ".join(dossier.subdomains[sub]) if dossier.subdomains[sub] else "*(unresolved)*"
        md.append(f"| `{sub}` | {ips} |")

    if dossier.asns:
        md.append("\n## ASN & Ownership")
        md.append("*Source: Team Cymru via DNS · Admiralty: **B1***\n")
        md.append("| IP | ASN | Organization | Country | Prefix |")
        md.append("|----|-----|--------------|---------|--------|")
        for ip, info in sorted(dossier.asns.items()):
            md.append(f"| `{ip}` | AS{info.get('asn','?')} | "
                      f"{info.get('org','?')} | {info.get('country','?')} | "
                      f"{info.get('prefix','?')} |")

    if dossier.services:
        md.append("\n## Passive Port & Service Info")
        md.append("*Source: Shodan InternetDB · Admiralty: **B2** — last-scan timestamp varies*\n")
        for ip in sorted(dossier.services.keys()):
            data = dossier.services[ip]
            md.append(f"### `{ip}`")
            if data.get("ports"):
                md.append(f"- **Open ports:** {', '.join(str(p) for p in data['ports'])}")
            if data.get("hostnames"):
                md.append(f"- **Hostnames:** {', '.join(data['hostnames'])}")
            if data.get("cpes"):
                md.append(f"- **CPEs:** {', '.join(data['cpes'])}")
            if data.get("tags"):
                md.append(f"- **Tags:** {', '.join(data['tags'])}")
            if data.get("vulns"):
                md.append(f"- **Known vulns:** {', '.join(data['vulns'])}")
            md.append("")

    if dossier.cves:
        md.append("\n## CVE Correlation Summary")
        md.append(f"*Source: Shodan InternetDB vulns field · Admiralty: **C3** — "
                  f"flagged CVE != confirmed exploitability*\n")
        md.append(", ".join(f"`{c}`" for c in dossier.cves))

    if dossier.notes:
        md.append("\n## Notes")
        for n in dossier.notes:
            md.append(f"- {n}")

    md.append("\n## Next Steps for the Analyst")
    md.append("- Re-rate every claim above using the Admiralty Code before "
              "passing the dossier to a decision-maker.")
    md.append("- Cross-reference at least one finding per section with an "
              "independent source (CRAAP test).")
    md.append("- InternetDB data is a floor, not a ceiling — consider deep "
              "Shodan / Censys / urlscan.io pivots on anything unusual.")
    md.append("- Consider emitting a KML file (see `plants_to_kml.py`) if this "
              "dossier is for a physical/industrial target and leadership wants "
              "a map.")
    md.append("\n---\n*OSINT Village BSides KC 2026 · github.com/Ginsberg5150/OSINT-Village-BsidesKC-2026*")
    return "\n".join(md)


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Passive OSINT domain → dossier chain"
    )
    parser.add_argument("domain", help="target domain (e.g. example.com)")
    parser.add_argument("--output", "-o", default=None,
                        help="output markdown file (default: dossier-<domain>-<ts>.md)")
    parser.add_argument("--json", default=None, help="also write JSON")
    parser.add_argument("--no-internetdb", action="store_true",
                        help="skip Shodan InternetDB calls")
    parser.add_argument("--no-asn", action="store_true",
                        help="skip ASN lookups")
    args = parser.parse_args()

    start_time = time.time()
    domain = args.domain.strip().lower().lstrip("*.")

    print(f"\n=== From Domain to Dossier: {domain} ===\n", file=sys.stderr)

    dossier = Dossier(domain=domain, generated_at=now_iso())

    # Which tools do we have?
    available = ["crt.sh"]
    if is_installed("subfinder"):
        available.append("subfinder")
    if is_installed("amass"):
        available.append("amass")
    if HAS_DNS:
        available.append("dns-resolve")
        available.append("cymru-asn")
    if not args.no_internetdb:
        available.append("shodan-internetdb")
    if os.getenv("SHODAN_API_KEY"):
        available.append("shodan-api")
    dossier.tools_available = available

    # Phase 1: subdomain enumeration
    subs = {domain}
    subs |= crtsh_enum(domain)
    subs |= subfinder_enum(domain)
    subs |= amass_enum(domain)
    log(f"total unique subdomains: {len(subs)}", "+")

    # Phase 2: resolution
    resolved = resolve_bulk(subs)
    dossier.subdomains = resolved

    ips = {ip for ip_list in resolved.values() for ip in ip_list}
    log(f"unique IPs: {len(ips)}", "+")

    # Phase 3: ASN
    if not args.no_asn:
        dossier.asns = asn_lookup_bulk(ips)

    # Phase 4: InternetDB
    if not args.no_internetdb:
        dossier.services = internetdb_bulk(ips)
        all_vulns = set()
        for data in dossier.services.values():
            all_vulns.update(data.get("vulns", []))
        dossier.cves = sorted(all_vulns)

    # Flags / reminders
    if not os.getenv("SHODAN_API_KEY"):
        dossier.notes.append(
            "Set SHODAN_API_KEY env var for deep host banners (optional)"
        )
    elapsed = int(time.time() - start_time)
    dossier.notes.append(
        f"Dossier generated in {elapsed}s — re-run periodically; "
        "recon is a living artifact."
    )

    # Output
    md = render_markdown(dossier)
    ts = int(time.time())
    out = args.output or f"dossier-{domain}-{ts}.md"
    Path(out).write_text(md, encoding="utf-8")
    log(f"wrote markdown dossier: {out}", "+")

    if args.json:
        Path(args.json).write_text(
            json.dumps(asdict(dossier), indent=2, default=str),
            encoding="utf-8"
        )
        log(f"wrote JSON dossier: {args.json}", "+")


if __name__ == "__main__":
    main()
