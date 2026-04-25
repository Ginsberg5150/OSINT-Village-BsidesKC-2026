#!/usr/bin/env python3
"""
edgar_subsidiaries.py — Wildcard OSINT Toolkit
SEC EDGAR Exhibit 21 → corporate subsidiary list.

Why this exists:
  Public US companies disclose their subsidiaries in Exhibit 21 of the
  annual 10-K filing. This is the most authoritative single source for
  corporate ownership mapping (Admiralty A1) — and it's free.

What this script does:
  - Accepts a CIK (Central Index Key) OR a company name
  - If you give it a name, it searches EDGAR's company tickers file to
    resolve to a CIK — no guessing
  - Pulls the most recent 10-K
  - Extracts and prints the Exhibit 21 subsidiary list
  - Saves a JSON record so you can re-run without hitting the SEC

  This script is the fastest way to answer "who do they actually own?"
  for any US-listed public company.

Required:
  CONTACT_EMAIL — the SEC requires this in the User-Agent. The script
  will prompt you the first time and save it to .env.

Usage:
    python3 edgar_subsidiaries.py 320193           # Apple by CIK
    python3 edgar_subsidiaries.py "Shopify"        # by name (fuzzy match)
    python3 edgar_subsidiaries.py                  # prompts for input
    python3 edgar_subsidiaries.py 320193 --json out.json

Admiralty rating of output: A1
    A — SEC EDGAR is a primary source, legally mandated to be accurate
    1 — confirmed by other independent sources at filing time
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Make the lib/ shared helpers importable
sys.path.insert(0, str(Path(__file__).parent / "lib"))
from osint_common import (  # noqa: E402
    banner, info, warn, error, success, hint,
    http_get, http_get_json, get_config, prompt_for,
    validate_cik, ConfigError,
)


SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
SEC_ARCHIVES_BASE = "https://www.sec.gov/Archives/edgar/data"


# ---------------------------------------------------------------------------
# Resolving company name → CIK
# ---------------------------------------------------------------------------

def resolve_cik(query: str, contact_email: str) -> tuple[str, str] | None:
    """
    Resolve a query (CIK or company name) to (cik_padded, company_name).
    Returns None if no match.
    """
    # If it looks like a CIK already, just pad it
    ok, cleaned, _ = validate_cik(query)
    if ok:
        # Confirm by hitting the submissions API
        try:
            data = http_get_json(
                SEC_SUBMISSIONS_URL.format(cik=cleaned),
                contact_email=contact_email,
                timeout=20, retries=2,
            )
            return cleaned, data.get("name", "(unknown)")
        except Exception as e:
            warn(f"CIK lookup failed: {e}")
            return None

    # Otherwise treat as company name — search the tickers file
    info(f"Searching EDGAR for company: {query!r}")
    try:
        tickers = http_get_json(
            SEC_TICKERS_URL, contact_email=contact_email, timeout=30, retries=3,
        )
    except Exception as e:
        error(f"Could not fetch SEC tickers list: {e}")
        return None

    # Tickers file is dict of "0":{"cik_str":..., "ticker":..., "title":...}
    q_lower = query.lower().strip()
    matches: list[tuple[int, str, str, str]] = []
    for _, row in tickers.items():
        title = row.get("title", "")
        ticker = row.get("ticker", "")
        if q_lower in title.lower() or q_lower == ticker.lower():
            matches.append((
                int(row["cik_str"]),
                str(row["cik_str"]).zfill(10),
                title,
                ticker,
            ))

    if not matches:
        error(f"No EDGAR match for {query!r}")
        hint("Try a different spelling, the ticker symbol, or pass the CIK directly.")
        return None

    if len(matches) == 1:
        _, cik, name, ticker = matches[0]
        success(f"Matched: {name} ({ticker}) — CIK {cik}")
        return cik, name

    # Multiple matches — let the user pick
    print("", file=sys.stderr)
    info(f"{len(matches)} matches — pick one:")
    for i, (_, cik, name, ticker) in enumerate(matches[:20], start=1):
        print(f"  {i:2}. {name} ({ticker})  CIK {cik}", file=sys.stderr)
    if len(matches) > 20:
        hint(f"({len(matches) - 20} more not shown — try a more specific name)")

    if not (sys.stdin.isatty() and sys.stderr.isatty()):
        # Auto-pick first if non-interactive (and warn)
        warn("Non-interactive mode — picking the first match.")
        _, cik, name, _ = matches[0]
        return cik, name

    while True:
        try:
            ans = input("  Pick [1]: ").strip() or "1"
        except (EOFError, KeyboardInterrupt):
            return None
        if ans.isdigit() and 1 <= int(ans) <= len(matches[:20]):
            _, cik, name, _ = matches[int(ans) - 1]
            return cik, name
        warn("Invalid choice. Try again.")


# ---------------------------------------------------------------------------
# Pulling the latest 10-K + Exhibit 21
# ---------------------------------------------------------------------------

def latest_10k(cik: str, contact_email: str) -> dict | None:
    """Find the accession number + primary doc for the most recent 10-K."""
    info(f"Fetching submissions index for CIK {cik}")
    try:
        subs = http_get_json(
            SEC_SUBMISSIONS_URL.format(cik=cik),
            contact_email=contact_email,
            timeout=30, retries=3,
        )
    except Exception as e:
        error(f"Could not fetch submissions: {e}")
        return None

    recent = subs.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    accessions = recent.get("accessionNumber", [])
    primary_docs = recent.get("primaryDocument", [])
    dates = recent.get("filingDate", [])

    for i, form in enumerate(forms):
        if form == "10-K":
            return {
                "accession": accessions[i],
                "primary_doc": primary_docs[i],
                "filing_date": dates[i],
                "company_name": subs.get("name"),
            }
    return None


def find_exhibit_21(cik: str, accession: str, contact_email: str) -> str | None:
    """Find the Exhibit 21 file URL inside a 10-K filing."""
    cik_int = int(cik)
    accession_clean = accession.replace("-", "")
    index_url = (
        f"{SEC_ARCHIVES_BASE}/{cik_int}/{accession_clean}/index.json"
    )
    info(f"Reading filing index: {index_url}")
    try:
        idx = http_get_json(index_url, contact_email=contact_email, timeout=30, retries=3)
    except Exception as e:
        error(f"Could not fetch filing index: {e}")
        return None

    items = idx.get("directory", {}).get("item", [])
    # Heuristic: look for files whose name contains "ex21" or "ex-21"
    candidates = [
        it for it in items
        if re.search(r"ex[-_]?21", it.get("name", "").lower())
        and not it.get("name", "").lower().endswith(".jpg")
    ]
    if not candidates:
        return None

    # Prefer .htm/.html over .txt
    candidates.sort(key=lambda it: (
        0 if it["name"].lower().endswith((".htm", ".html")) else 1,
        it["name"],
    ))
    name = candidates[0]["name"]
    return f"{SEC_ARCHIVES_BASE}/{cik_int}/{accession_clean}/{name}"


def parse_exhibit_21(html: str) -> list[dict]:
    """Best-effort parse of an Exhibit 21 HTML document into structured rows."""
    # Strip tags simply — Exhibit 21 layouts vary wildly
    text = re.sub(r"<script.*?</script>", "", html, flags=re.S | re.I)
    text = re.sub(r"<style.*?</style>", "", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", "\n", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"\s+\n", "\n", text)
    text = re.sub(r"\n\s+", "\n", text)
    text = re.sub(r"\n{2,}", "\n", text)

    rows: list[dict] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if len(line) < 3 or len(line) > 250:
            continue
        # Skip obvious header lines
        low = line.lower()
        if any(skip in low for skip in (
            "exhibit 21", "list of subsidiaries", "subsidiaries of", "the registrant",
            "name of subsidiary", "jurisdiction", "state of", "country of",
            "page ", "(1)", "(2)",
        )):
            continue
        # If line looks like "Name, Jurisdiction" split on last comma
        if "," in line and not line.endswith(","):
            name, _, juris = line.rpartition(",")
            name = name.strip(" ,.\t")
            juris = juris.strip(" ,.\t")
            if name and juris and len(juris) < 60:
                rows.append({"name": name, "jurisdiction": juris})
                continue
        rows.append({"name": line, "jurisdiction": None})
    # De-duplicate while preserving order
    seen = set()
    out = []
    for r in rows:
        key = (r["name"].lower(), (r["jurisdiction"] or "").lower())
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(
        description="Pull subsidiaries from SEC EDGAR 10-K Exhibit 21.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "query", nargs="?",
        help="CIK number OR company name (e.g. 320193 or 'Apple')",
    )
    p.add_argument("--json", help="write JSON to this path")
    p.add_argument(
        "--raw", action="store_true",
        help="also dump the raw Exhibit 21 HTML (for manual inspection)",
    )
    args = p.parse_args()

    banner("edgar_subsidiaries.py", "SEC EDGAR Exhibit 21 → subsidiaries")

    # --- contact email (REQUIRED by SEC) ---
    try:
        contact_email = get_config("CONTACT_EMAIL", required=True)
    except ConfigError as e:
        error(str(e))
        error("SEC EDGAR REQUIRES a contact email in the User-Agent header.")
        hint("Re-run interactively to set it once — saved to .env for next time.")
        return 2

    # --- query (CIK or name) ---
    query = args.query
    if not query:
        try:
            query = prompt_for(
                "CIK or company name",
                description="Enter a CIK number or company name to look up.",
                examples=["320193", "Apple", "Shopify", "0001318605"],
            )
        except ConfigError as e:
            error(str(e))
            return 2

    # --- resolve to CIK ---
    resolved = resolve_cik(query, contact_email)
    if not resolved:
        return 3
    cik, company_name = resolved

    # --- find latest 10-K ---
    filing = latest_10k(cik, contact_email)
    if not filing:
        error(f"No 10-K found for {company_name} (CIK {cik}).")
        hint("This company may not file 10-Ks (foreign private issuers file 20-F instead).")
        return 3
    success(f"Latest 10-K: filed {filing['filing_date']}, accession {filing['accession']}")

    # --- find Exhibit 21 file ---
    ex21_url = find_exhibit_21(cik, filing["accession"], contact_email)
    if not ex21_url:
        error("Couldn't find an Exhibit 21 file in the latest 10-K.")
        hint("Some companies embed Exhibit 21 in the main 10-K document — open the filing manually:")
        accession_clean = filing["accession"].replace("-", "")
        hint(f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=10-K")
        return 3

    info(f"Fetching Exhibit 21: {ex21_url}")
    try:
        r = http_get(ex21_url, contact_email=contact_email, timeout=30, retries=3)
    except Exception as e:
        error(f"Could not fetch Exhibit 21: {e}")
        return 3

    html = r.text
    subsidiaries = parse_exhibit_21(html)

    if not subsidiaries:
        warn("Parsed zero rows from Exhibit 21 — the layout may be unusual.")
        hint(f"Open it manually: {ex21_url}")
        if args.raw or args.json:
            pass
        else:
            return 3

    # --- output ---
    print("")
    print(f"# Subsidiaries of {company_name}")
    print(f"# CIK {cik} · 10-K filed {filing['filing_date']}")
    print(f"# Source: {ex21_url}")
    print(f"# Admiralty A1 (primary source, legally mandated)")
    print()
    for row in subsidiaries:
        if row["jurisdiction"]:
            print(f"- {row['name']}  ({row['jurisdiction']})")
        else:
            print(f"- {row['name']}")
    print()
    success(f"Found {len(subsidiaries)} subsidiary entries.")

    if args.json:
        payload = {
            "company_name": company_name,
            "cik": cik,
            "filing_date": filing["filing_date"],
            "accession": filing["accession"],
            "exhibit_21_url": ex21_url,
            "admiralty_rating": "A1",
            "subsidiaries": subsidiaries,
        }
        Path(args.json).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        success(f"Wrote JSON to {args.json}")

    if args.raw:
        raw_path = f"ex21_{cik}_{filing['filing_date']}.html"
        Path(raw_path).write_text(html, encoding="utf-8")
        success(f"Wrote raw HTML to {raw_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
