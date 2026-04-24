#!/usr/bin/env python3
"""
domain_to_org.py — OSINT Village BSides KC 2026 Toolkit (Wildcard Industries LLC)
Module 1 companion script · From Domain to Org Graph

Takes a domain and produces a structured org graph by:
  1. Resolving the company on EDGAR (full-text filing search)
  2. Locating the most recent 10-K filing
  3. Pulling Exhibit 21 (subsidiaries disclosure)
  4. Cross-referencing USASpending.gov for federal contracting

All passive. All primary-source.

=========================================================================
⚠️  CLASS-DAY STATUS — EARLY-STAGE STUB
=========================================================================

This script is a starter stub. It demonstrates the approach and API
endpoints from the QA-specified spec, but is intentionally left as
an exercise for Ghost-tier students to extend.

Ghost challenge (Lab-Module-1-Ghost.md, Path A): run this against
caterpillar.com, audit its output against your manual Exhibit 21
read, document where it succeeds and where it misses.

The QA-specified behavior this stub targets:
  - Use the EDGAR /Archives/edgar/data/{cik}/{acc}/index.json endpoint
    (NOT the HTML filing-index page) for structured filing data.
  - Widened Exhibit 21 filename regex:
      ex[-_x]*21 | exhibit[-_]?21 | subsidiar(y|ies)
  - USASpending (not SAM.gov) for federal contracting cross-reference.
  - Jittered 1.0–1.5s sleeps between polled calls.
  - Honor EDGAR's User-Agent requirement (real contact info).

Hunter students: you don't need to run this. Your Module 1 lab walks
you through the same steps manually in a browser.
=========================================================================

Usage:
    python3 domain_to_org.py caterpillar.com
    python3 domain_to_org.py caterpillar.com --output cat-org.json --verbose
"""
import argparse
import json
import re
import sys
import time
import random

try:
    import requests
except ImportError:
    print("[!] requests required: pip install requests", file=sys.stderr)
    sys.exit(1)

USER_AGENT = "osint-village-bsideskc-2026/1.0 research-contact github.com/Ginsberg5150"
EDGAR_SEARCH = "https://efts.sec.gov/LATEST/search-index"
EDGAR_ARCHIVE = "https://www.sec.gov/Archives/edgar/data"
USASPENDING_SEARCH = "https://api.usaspending.gov/api/v2/recipient/duns/"

# QA-specified widened regex for Exhibit 21 filenames
EX21_PATTERN = re.compile(
    r'ex[-_x]*21|exhibit[-_]?21|subsidiar(y|ies)',
    re.IGNORECASE
)


def _sleep():
    """QA-specified jittered 1.0-1.5s sleep between polled calls."""
    time.sleep(1.0 + random.random() * 0.5)


def find_cik(company_search: str) -> str:
    """Search EDGAR for a company name, return the CIK of the top match."""
    r = requests.get(
        EDGAR_SEARCH,
        params={"q": company_search, "forms": "10-K"},
        headers={"User-Agent": USER_AGENT},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    hits = data.get("hits", {}).get("hits", [])
    if not hits:
        return None
    # Each hit has _source.ciks (list)
    top = hits[0]
    ciks = top.get("_source", {}).get("ciks", [])
    return ciks[0] if ciks else None


def latest_10k_accession(cik: str) -> str:
    """
    STUB: retrieve the most recent 10-K accession number for a CIK.
    Should hit EDGAR's submissions API at:
        https://data.sec.gov/submissions/CIK{cik:010d}.json
    Parse recent.filings entries where form == "10-K", return first.
    """
    # TODO: implement per QA spec using EDGAR submissions endpoint
    raise NotImplementedError(
        "Ghost challenge: implement using data.sec.gov/submissions/CIK{cik:010d}.json"
    )


def pull_exhibit_21(cik: str, accession: str) -> list:
    """
    STUB: given CIK + accession, fetch the filing index.json and
    locate Exhibit 21 by filename matching EX21_PATTERN.

    QA-specified endpoint:
        {EDGAR_ARCHIVE}/{cik}/{accession_no_dashes}/index.json

    Then the exhibit URL is:
        {EDGAR_ARCHIVE}/{cik}/{accession_no_dashes}/{filename}

    Parse the exhibit HTML/text for subsidiary entries.
    Returns: list of {"name": str, "jurisdiction": str}
    """
    # TODO: implement per QA spec
    raise NotImplementedError(
        "Ghost challenge: parse Exhibit 21 from EDGAR filing index.json"
    )


def usaspending_contracts(company_name: str) -> dict:
    """
    STUB: query USASpending.gov for federal contract awards to the
    named recipient. Return structured summary.

    QA-specified: use USASpending.gov, NOT SAM.gov
    (SAM entity search returns cross-query garbage).
    """
    # TODO: implement per QA spec
    raise NotImplementedError(
        "Ghost challenge: implement USASpending recipient search"
    )


def main():
    parser = argparse.ArgumentParser(
        description="EDGAR + USASpending org graph builder (early stub)"
    )
    parser.add_argument("domain", help="target domain (used to guess company name)")
    parser.add_argument("--company", help="override company name to search")
    parser.add_argument("--output", help="write JSON output to file")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    company = args.company or args.domain.split(".")[0]
    print(f"[*] searching EDGAR for: {company}", file=sys.stderr)

    _sleep()
    cik = find_cik(company)
    if not cik:
        print(f"[!] no EDGAR match for '{company}'", file=sys.stderr)
        sys.exit(2)
    print(f"[+] CIK: {cik}", file=sys.stderr)

    result = {
        "domain": args.domain,
        "company_search": company,
        "edgar_cik": cik,
        "subsidiaries": [],
        "usaspending_summary": None,
        "notes": [
            "STUB — this script is a Ghost-tier extension exercise.",
            "See docstring for QA-specified implementation targets.",
        ],
    }

    # The Ghost-tier work: implement the stubs above and remove these notes.
    try:
        _sleep()
        accession = latest_10k_accession(cik)
        _sleep()
        result["subsidiaries"] = pull_exhibit_21(cik, accession)
        _sleep()
        result["usaspending_summary"] = usaspending_contracts(company)
    except NotImplementedError as e:
        result["notes"].append(f"NotImplemented: {e}")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"[+] wrote {args.output}", file=sys.stderr)
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
