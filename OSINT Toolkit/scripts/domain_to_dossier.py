#!/usr/bin/env python3
"""
domain_to_dossier.py — Wildcard OSINT Toolkit flagship script
From Domain to Dossier · BSides KC 2026 · OSINT Village

Takes a single domain and produces a structured passive-OSINT dossier
by chaining certificate transparency, DNS, ASN/ownership lookup, passive
port info (Shodan InternetDB), and optional deep Shodan and CVE data.

All data sources are passive. No active scanning. No auth bypass.
No contact attempts.

What's new in v2:
  - Prompts for a domain if you forget to pass one
  - Clearly lists which data sources are enabled / disabled / failed
  - Each source is independently fault-tolerant — one failure never kills
    the whole run
  - Skips Shodan API gracefully if no key, falls back to InternetDB
  - Reports a "completeness score" so you know how good the dossier is

Usage:
    python3 domain_to_dossier.py shopify.com
    python3 domain_to_dossier.py                       # prompts for domain
    python3 domain_to_dossier.py shopify.com -o out.md
    python3 domain_to_dossier.py shopify.com --json out.json
    python3 domain_to_dossier.py shopify.com --no-shodan
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

# Make the lib/ shared helpers importable
sys.path.insert(0, str(Path(__file__).parent / "lib"))
from osint_common import (  # noqa: E402
    banner, info, warn, error, success, hint,
    http_get, http_get_json, get_config, prompt_for, validate_domain,
    ConfigError,
)


# ---------------------------------------------------------------------------
# Data-source modules (each returns a (status, data) tuple)
# ---------------------------------------------------------------------------

def src_crtsh(domain: str) -> tuple[str, dict]:
    """Pull subdomains from crt.sh CT logs."""
    try:
        url = f"https://crt.sh/?q=%25.{domain}&output=json"
        data = http_get_json(url, timeout=45, retries=4)
        subs = set()
        for entry in data:
            for name in (entry.get("name_value") or "").split("\n"):
                name = name.strip().lower().lstrip("*.")
                if name and (name == domain or name.endswith("." + domain)):
                    subs.add(name)
        return "ok", {"count": len(subs), "subdomains": sorted(subs)}
    except Exception as e:
        return "fail", {"error": f"{type(e).__name__}: {e}"}


def src_certspotter(domain: str) -> tuple[str, dict]:
    """Fallback / additional CT source."""
    try:
        url = (
            f"https://api.certspotter.com/v1/issuances"
            f"?domain={domain}&include_subdomains=true&expand=dns_names"
        )
        data = http_get_json(url, timeout=30, retries=2)
        subs = set()
        for entry in data:
            for name in entry.get("dns_names", []) or []:
                name = name.strip().lower().lstrip("*.")
                if name and (name == domain or name.endswith("." + domain)):
                    subs.add(name)
        return "ok", {"count": len(subs), "subdomains": sorted(subs)}
    except Exception as e:
        return "fail", {"error": f"{type(e).__name__}: {e}"}


def src_dns(host: str) -> tuple[str, dict]:
    """Resolve A records for a single host."""
    try:
        ips = sorted({i[4][0] for i in socket.getaddrinfo(host, None)})
        return "ok", {"ips": ips}
    except (socket.gaierror, socket.herror) as e:
        return "fail", {"error": str(e)}


def src_team_cymru_asn(ip: str) -> tuple[str, dict]:
    """ASN/org lookup via Team Cymru's DNS-based service. No key needed."""
    try:
        # reverse the IP and query origin.asn.cymru.com
        rev = ".".join(reversed(ip.split(".")))
        query = f"{rev}.origin.asn.cymru.com"
        # Using socket TXT queries is ugly — use dnspython if available
        try:
            import dns.resolver
            answers = dns.resolver.resolve(query, "TXT")
            txt = str(answers[0]).strip('"')
        except ImportError:
            return "skip", {"reason": "dnspython not installed (pip install dnspython)"}
        # Format: "AS | CIDR | CC | RIR | YYYY-MM-DD"
        parts = [p.strip() for p in txt.split("|")]
        return "ok", {
            "asn": parts[0] if len(parts) > 0 else None,
            "cidr": parts[1] if len(parts) > 1 else None,
            "country": parts[2] if len(parts) > 2 else None,
            "rir": parts[3] if len(parts) > 3 else None,
            "allocated": parts[4] if len(parts) > 4 else None,
        }
    except Exception as e:
        return "fail", {"error": f"{type(e).__name__}: {e}"}


def src_internetdb(ip: str) -> tuple[str, dict]:
    """Shodan InternetDB — FREE, no API key. Ports + CPEs + tags + vulns."""
    try:
        url = f"https://internetdb.shodan.io/{ip}"
        r = http_get(url, timeout=15, retries=2, raise_for_status=False)
        if r.status_code == 404:
            return "ok", {"ports": [], "cpes": [], "tags": [], "vulns": [], "hostnames": []}
        if r.status_code >= 400:
            return "fail", {"error": f"HTTP {r.status_code}"}
        return "ok", r.json()
    except Exception as e:
        return "fail", {"error": f"{type(e).__name__}: {e}"}


def src_shodan_host(ip: str, api_key: str) -> tuple[str, dict]:
    """Deep Shodan host lookup — requires API key."""
    try:
        url = f"https://api.shodan.io/shodan/host/{ip}?key={api_key}"
        r = http_get(url, timeout=20, retries=2, raise_for_status=False)
        if r.status_code == 401:
            return "fail", {"error": "401 — Shodan rejected the API key"}
        if r.status_code == 403:
            return "fail", {"error": "403 — your Shodan plan may not include host API"}
        if r.status_code == 404:
            return "ok", {"ports": [], "vulns": [], "data": []}
        if r.status_code >= 400:
            return "fail", {"error": f"HTTP {r.status_code}"}
        d = r.json()
        return "ok", {
            "ports": d.get("ports", []),
            "hostnames": d.get("hostnames", []),
            "org": d.get("org"),
            "isp": d.get("isp"),
            "country": d.get("country_name"),
            "vulns": list((d.get("vulns") or {}).keys()) if isinstance(d.get("vulns"), dict) else d.get("vulns", []),
            "last_update": d.get("last_update"),
            "tags": d.get("tags", []),
        }
    except Exception as e:
        return "fail", {"error": f"{type(e).__name__}: {e}"}


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def build_dossier(domain: str, opts: argparse.Namespace) -> dict:
    """Run all enabled data sources and aggregate the results."""
    started = datetime.now(timezone.utc).isoformat()
    dossier = {
        "domain": domain,
        "started_utc": started,
        "toolkit": "wildcard-osint-toolkit/2.0",
        "sources": {},
        "subdomains": [],
        "hosts": {},
        "summary": {},
    }

    # --- Phase 1: subdomain enumeration (CT logs) ---
    print("", file=sys.stderr)
    info("Phase 1: Certificate transparency")
    all_subs: set[str] = set()
    if not opts.no_crtsh:
        status, payload = src_crtsh(domain)
        dossier["sources"]["crtsh"] = {"status": status, **payload}
        _report_source("crt.sh", status, payload, "count")
        if status == "ok":
            all_subs.update(payload["subdomains"])
    if not opts.no_certspotter:
        status, payload = src_certspotter(domain)
        dossier["sources"]["certspotter"] = {"status": status, **payload}
        _report_source("certspotter", status, payload, "count")
        if status == "ok":
            all_subs.update(payload["subdomains"])

    all_subs.add(domain)
    dossier["subdomains"] = sorted(all_subs)
    info(f"Total unique hosts after CT phase: {len(all_subs)}")

    if opts.max_hosts and len(all_subs) > opts.max_hosts:
        warn(
            f"Limiting to first {opts.max_hosts} hosts (have {len(all_subs)}). "
            f"Pass --max-hosts 0 to disable."
        )
        all_subs = set(sorted(all_subs)[: opts.max_hosts])

    # --- Phase 2: DNS resolution (parallel) ---
    print("", file=sys.stderr)
    info(f"Phase 2: DNS resolution ({len(all_subs)} hosts)")
    host_to_ips: dict[str, list[str]] = {}
    with ThreadPoolExecutor(max_workers=opts.workers) as ex:
        future_map = {ex.submit(src_dns, h): h for h in all_subs}
        for fut in as_completed(future_map):
            h = future_map[fut]
            status, payload = fut.result()
            if status == "ok":
                host_to_ips[h] = payload["ips"]
                dossier["hosts"][h] = {"ips": payload["ips"]}
            else:
                dossier["hosts"][h] = {"ips": [], "dns_error": payload.get("error")}
    resolved_count = sum(1 for v in host_to_ips.values() if v)
    info(f"Resolved {resolved_count}/{len(all_subs)} hosts")

    unique_ips = sorted({ip for ips in host_to_ips.values() for ip in ips})
    info(f"Unique IPs: {len(unique_ips)}")

    # --- Phase 3: ASN / org lookup ---
    if not opts.no_asn and unique_ips:
        print("", file=sys.stderr)
        info(f"Phase 3: ASN lookup (Team Cymru, {len(unique_ips)} IPs)")
        asn_data: dict[str, dict] = {}
        with ThreadPoolExecutor(max_workers=min(opts.workers, 8)) as ex:
            future_map = {ex.submit(src_team_cymru_asn, ip): ip for ip in unique_ips}
            for fut in as_completed(future_map):
                ip = future_map[fut]
                status, payload = fut.result()
                if status == "ok":
                    asn_data[ip] = payload
                elif status == "skip":
                    warn(payload.get("reason", "skipped"))
                    break
        dossier["asn_by_ip"] = asn_data
        success(f"ASN data for {len(asn_data)} IPs")

    # --- Phase 4: InternetDB (free passive port data) ---
    if not opts.no_internetdb and unique_ips:
        print("", file=sys.stderr)
        info(f"Phase 4: Shodan InternetDB ({len(unique_ips)} IPs, free, no key)")
        idb: dict[str, dict] = {}
        with ThreadPoolExecutor(max_workers=opts.workers) as ex:
            future_map = {ex.submit(src_internetdb, ip): ip for ip in unique_ips}
            for fut in as_completed(future_map):
                ip = future_map[fut]
                status, payload = fut.result()
                if status == "ok":
                    idb[ip] = payload
        dossier["internetdb"] = idb
        with_data = sum(1 for v in idb.values() if v.get("ports") or v.get("vulns"))
        success(f"InternetDB returned data for {with_data}/{len(unique_ips)} IPs")

        # CVE summary from InternetDB
        all_vulns = sorted({v for d in idb.values() for v in (d.get("vulns") or [])})
        if all_vulns:
            warn(f"Known CVEs across infrastructure: {len(all_vulns)}")
            dossier["summary"]["cves"] = all_vulns

    # --- Phase 5: Shodan deep API (optional) ---
    shodan_key = None
    if not opts.no_shodan:
        try:
            shodan_key = get_config("SHODAN_API_KEY", prompt=opts.interactive_keys, save=True)
        except ConfigError:
            shodan_key = None
        if shodan_key and unique_ips:
            print("", file=sys.stderr)
            info(f"Phase 5: Shodan deep host API ({len(unique_ips)} IPs)")
            shod: dict[str, dict] = {}
            with ThreadPoolExecutor(max_workers=min(opts.workers, 4)) as ex:
                future_map = {ex.submit(src_shodan_host, ip, shodan_key): ip for ip in unique_ips}
                for fut in as_completed(future_map):
                    ip = future_map[fut]
                    status, payload = fut.result()
                    if status == "ok":
                        shod[ip] = payload
                    else:
                        warn(f"Shodan {ip}: {payload.get('error')}")
            dossier["shodan"] = shod
            success(f"Shodan deep data for {len(shod)} IPs")
        else:
            if not shodan_key:
                hint("No SHODAN_API_KEY — skipping deep host API. InternetDB still ran.")

    # --- Summary / completeness score ---
    dossier["finished_utc"] = datetime.now(timezone.utc).isoformat()
    dossier["summary"]["host_count"] = len(all_subs)
    dossier["summary"]["resolved_host_count"] = resolved_count
    dossier["summary"]["unique_ip_count"] = len(unique_ips)
    dossier["summary"]["completeness_score"] = _completeness(dossier)

    return dossier


def _report_source(name: str, status: str, payload: dict, count_field: str | None = None):
    if status == "ok":
        if count_field and count_field in payload:
            success(f"{name}: {payload[count_field]} result(s)")
        else:
            success(f"{name}: ok")
    elif status == "skip":
        warn(f"{name}: skipped — {payload.get('reason', '')}")
    else:
        warn(f"{name}: failed — {payload.get('error', 'unknown')}")


def _completeness(d: dict) -> int:
    """Score 0-100 based on how many sources contributed data."""
    score = 0
    if any(d["sources"].get(s, {}).get("status") == "ok" for s in ("crtsh", "certspotter")):
        score += 30
    if d["summary"].get("resolved_host_count", 0) > 0:
        score += 20
    if d.get("asn_by_ip"):
        score += 15
    if any(v.get("ports") for v in d.get("internetdb", {}).values()):
        score += 20
    if d.get("shodan"):
        score += 15
    return score


# ---------------------------------------------------------------------------
# Markdown output
# ---------------------------------------------------------------------------

def render_markdown(d: dict) -> str:
    lines = []
    lines.append(f"# Dossier: {d['domain']}")
    lines.append("")
    lines.append(f"_Generated {d['finished_utc']} by {d['toolkit']}_")
    lines.append("")
    lines.append(f"**Completeness:** {d['summary']['completeness_score']}/100  ")
    lines.append(f"**Hosts found:** {d['summary']['host_count']}  ")
    lines.append(f"**Resolved:** {d['summary']['resolved_host_count']}  ")
    lines.append(f"**Unique IPs:** {d['summary']['unique_ip_count']}  ")
    lines.append("")

    # CT log subdomains
    lines.append("## Subdomains (Admiralty B2)")
    lines.append("")
    lines.append(f"_Source: Certificate Transparency logs (crt.sh, certspotter)_")
    lines.append("")
    if d["subdomains"]:
        for s in d["subdomains"]:
            lines.append(f"- `{s}`")
    else:
        lines.append("_(none discovered)_")
    lines.append("")

    # ASN
    if d.get("asn_by_ip"):
        lines.append("## ASN / Ownership (Admiralty A1)")
        lines.append("")
        lines.append("| IP | ASN | CIDR | Country | RIR |")
        lines.append("|----|-----|------|---------|-----|")
        for ip, asn in sorted(d["asn_by_ip"].items()):
            lines.append(
                f"| `{ip}` | AS{asn.get('asn', '?')} | "
                f"{asn.get('cidr', '?')} | {asn.get('country', '?')} | "
                f"{asn.get('rir', '?')} |"
            )
        lines.append("")

    # InternetDB summary
    if d.get("internetdb"):
        lines.append("## Exposed Services (Admiralty B2 — Shodan InternetDB)")
        lines.append("")
        for ip in sorted(d["internetdb"]):
            entry = d["internetdb"][ip]
            ports = entry.get("ports") or []
            vulns = entry.get("vulns") or []
            if not ports and not vulns:
                continue
            lines.append(f"### `{ip}`")
            if ports:
                lines.append(f"- **Open ports:** {', '.join(str(p) for p in ports)}")
            if vulns:
                lines.append(f"- **Known CVEs:** {', '.join(vulns)}")
            cpes = entry.get("cpes") or []
            if cpes:
                lines.append(f"- **CPEs:** {', '.join(cpes)}")
            tags = entry.get("tags") or []
            if tags:
                lines.append(f"- **Tags:** {', '.join(tags)}")
            lines.append("")

    # Shodan deep
    if d.get("shodan"):
        lines.append("## Shodan Deep Host Data (Admiralty B2)")
        lines.append("")
        for ip, entry in sorted(d["shodan"].items()):
            lines.append(f"- `{ip}` — org={entry.get('org', '?')}, "
                         f"isp={entry.get('isp', '?')}, "
                         f"country={entry.get('country', '?')}")
        lines.append("")

    # CVE summary
    if d["summary"].get("cves"):
        lines.append("## CVE Roll-up")
        lines.append("")
        for cve in d["summary"]["cves"]:
            lines.append(f"- [{cve}](https://nvd.nist.gov/vuln/detail/{cve})")
        lines.append("")

    # Failed sources
    failed = {k: v for k, v in d["sources"].items() if v.get("status") == "fail"}
    if failed:
        lines.append("## Source Failures")
        lines.append("")
        for name, info_d in failed.items():
            lines.append(f"- **{name}**: {info_d.get('error', 'unknown')}")
        lines.append("")

    lines.append("## Next Steps for the Analyst")
    lines.append("")
    lines.append("1. CRAAP-rate every finding before pasting into the deliverable")
    lines.append("2. Cross-reference SEC EDGAR Exhibit 21 for org ownership confirmation")
    lines.append("   (use `edgar_subsidiaries.py`)")
    lines.append("3. Pivot interesting favicons with `favicon_pivot.py`")
    lines.append("4. Ensure scope authorization before any active follow-up")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(
        description="Build a passive-OSINT dossier for a domain.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("domain", nargs="?", help="root domain, e.g. shopify.com")
    p.add_argument("-o", "--output", help="output Markdown file (default: stdout)")
    p.add_argument("--json", help="also write JSON to this path")
    p.add_argument("--no-crtsh", action="store_true", help="skip crt.sh")
    p.add_argument("--no-certspotter", action="store_true", help="skip certspotter")
    p.add_argument("--no-asn", action="store_true", help="skip ASN lookup")
    p.add_argument("--no-internetdb", action="store_true", help="skip Shodan InternetDB")
    p.add_argument("--no-shodan", action="store_true", help="skip Shodan API even if key is set")
    p.add_argument(
        "--interactive-keys",
        dest="interactive_keys",
        action="store_true",
        default=True,
        help="prompt for missing API keys (default)",
    )
    p.add_argument(
        "--no-prompt-keys",
        dest="interactive_keys",
        action="store_false",
        help="never prompt for keys; just skip what's missing",
    )
    p.add_argument(
        "--max-hosts", type=int, default=200,
        help="cap hosts processed downstream (default: 200, 0 = no cap)",
    )
    p.add_argument("--workers", type=int, default=10, help="parallel workers (default: 10)")
    args = p.parse_args()

    banner("domain_to_dossier.py", "Passive OSINT dossier builder")

    # --- resolve domain ---
    domain = args.domain
    if not domain:
        try:
            domain = prompt_for(
                "Target domain",
                description="Which domain do you want a dossier for?",
                examples=["shopify.com", "yelp.com", "caterpillar.com"],
                validator=validate_domain,
            )
        except ConfigError as e:
            error(str(e))
            return 2
    else:
        ok, cleaned, msg = validate_domain(domain)
        if not ok:
            error(msg)
            return 2
        domain = cleaned

    if args.max_hosts == 0:
        args.max_hosts = None

    # --- run ---
    try:
        dossier = build_dossier(domain, args)
    except KeyboardInterrupt:
        error("Aborted by user.")
        return 130

    # --- output ---
    md = render_markdown(dossier)
    if args.output:
        Path(args.output).write_text(md, encoding="utf-8")
        success(f"Wrote Markdown dossier to {args.output}")
    else:
        print(md)

    if args.json:
        Path(args.json).write_text(json.dumps(dossier, indent=2, default=str), encoding="utf-8")
        success(f"Wrote JSON to {args.json}")

    print("", file=sys.stderr)
    score = dossier["summary"]["completeness_score"]
    if score >= 80:
        success(f"Done. Completeness: {score}/100 (good)")
    elif score >= 50:
        info(f"Done. Completeness: {score}/100 (partial — see Source Failures section)")
    else:
        warn(f"Done. Completeness: {score}/100 (limited data — check connectivity, keys)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
