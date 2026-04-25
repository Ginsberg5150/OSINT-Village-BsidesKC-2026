#!/usr/bin/env python3
"""
plants_to_kml.py — Wildcard OSINT Toolkit
Turn a CSV of facility addresses into a Google Earth KML.

Why this exists:
  Industrial OSINT deliverables hit harder when leadership can rotate the
  globe. Take the plant list from a 10-K "Properties" section, geocode,
  hand them an interactive map.

What's new in v2:
  - Prompts for the CSV path if you forget to pass one
  - Prompts for CONTACT_EMAIL the first time (REQUIRED by Nominatim's TOS —
    without it you will silently get blocked)
  - Validates the CSV header and tells you which columns are missing
  - Per-row geocoding errors are reported but don't kill the whole run;
    they're collected and printed at the end
  - Caches geocoding results to .geocode_cache.json so re-runs are free
  - Writes a `failures.csv` next to the KML for any addresses that didn't
    geocode, so you can fix them and re-run

Input CSV header must include at least:
    name, address

Optional columns:
    segment   — folder grouping in KML (e.g. "Construction", "Mining")
    notes     — free text in the description bubble
    lat, lon  — if present, geocoding is skipped for that row

Usage:
    python3 plants_to_kml.py plants.csv -o caterpillar.kml
    python3 plants_to_kml.py plants.csv -o out.kml --no-geocode
    python3 plants_to_kml.py                # prompts for CSV path
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

# Make the lib/ shared helpers importable
sys.path.insert(0, str(Path(__file__).parent / "lib"))
from osint_common import (  # noqa: E402
    banner, info, warn, error, success, hint,
    http_get_json, get_config, prompt_for, confirm,
    ConfigError,
)

try:
    import simplekml
except ImportError:
    print(
        "[!] The `simplekml` library is required.\n"
        "    Install with:  pip install simplekml\n",
        file=sys.stderr,
    )
    sys.exit(1)


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
RATE_LIMIT_SECONDS = 1.1  # Nominatim TOS: max 1 req/sec
CACHE_FILE = Path(".geocode_cache.json")
REQUIRED_COLS = {"name", "address"}


def load_cache() -> dict:
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_cache(cache: dict) -> None:
    try:
        CACHE_FILE.write_text(json.dumps(cache, indent=2))
    except OSError as e:
        warn(f"Could not save geocode cache: {e}")


def geocode_one(address: str, contact_email: str, cache: dict) -> tuple[float, float] | None:
    """Geocode via OSM Nominatim. Returns (lat, lon) or None. Uses cache."""
    key = address.strip().lower()
    if key in cache:
        cached = cache[key]
        if cached is None:
            return None
        return cached["lat"], cached["lon"]

    try:
        data = http_get_json(
            NOMINATIM_URL,
            params={"q": address, "format": "json", "limit": 1},
            timeout=20,
            retries=3,
            contact_email=contact_email,
        )
    except Exception as e:
        warn(f"Geocode error for {address!r}: {type(e).__name__}: {e}")
        return None

    if not data:
        cache[key] = None
        return None

    lat = float(data[0]["lat"])
    lon = float(data[0]["lon"])
    cache[key] = {"lat": lat, "lon": lon, "display": data[0].get("display_name", "")}
    return lat, lon


def validate_csv_headers(reader_fields: list[str]) -> list[str]:
    """Return list of missing required column names (case-insensitive)."""
    have = {f.lower().strip() for f in (reader_fields or [])}
    return sorted(REQUIRED_COLS - have)


def main() -> int:
    p = argparse.ArgumentParser(
        description="Convert a CSV of facility addresses to a Google Earth KML.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("csv_path", nargs="?", help="input CSV file")
    p.add_argument("-o", "--output", default="plants.kml", help="output KML path")
    p.add_argument(
        "--no-geocode",
        action="store_true",
        help="skip geocoding (CSV must already have lat,lon columns)",
    )
    args = p.parse_args()

    banner("plants_to_kml.py", "Facility CSV → Google Earth KML")

    # --- resolve CSV path ---
    csv_path = args.csv_path
    if not csv_path:
        try:
            csv_path = prompt_for(
                "CSV file path",
                description="Which CSV has the facility list?",
                examples=["plants.csv", "./data/cat_properties.csv"],
            )
        except ConfigError as e:
            error(str(e))
            return 2

    csv_p = Path(csv_path).expanduser()
    if not csv_p.exists():
        error(f"CSV file not found: {csv_p}")
        hint("Make sure the path is correct relative to your current directory.")
        return 2

    # --- read + validate CSV ---
    try:
        with csv_p.open(encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            fields = reader.fieldnames or []
            missing = validate_csv_headers(fields)
            if missing:
                error(f"CSV is missing required column(s): {', '.join(missing)}")
                hint(f"Found columns: {', '.join(fields) if fields else '(none)'}")
                hint("Required: name, address.  Optional: segment, notes, lat, lon")
                return 2
            rows = list(reader)
    except OSError as e:
        error(f"Could not read CSV: {e}")
        return 2

    if not rows:
        error("CSV has no data rows.")
        return 2

    info(f"Loaded {len(rows)} row(s) from {csv_p.name}")

    # --- geocoding setup ---
    contact_email = None
    if not args.no_geocode:
        try:
            contact_email = get_config("CONTACT_EMAIL", required=True)
        except ConfigError as e:
            error(str(e))
            error("Geocoding via Nominatim REQUIRES a contact email in the User-Agent.")
            hint("Re-run interactively to set it, or use --no-geocode if your CSV already has lat,lon.")
            return 2

    cache = load_cache() if not args.no_geocode else {}

    # --- build KML ---
    kml = simplekml.Kml()
    folders: dict[str, simplekml.Folder] = {}

    failures: list[dict] = []
    geocoded = 0
    used_existing = 0
    skipped = 0

    for i, row in enumerate(rows, start=1):
        name = (row.get("name") or "").strip()
        address = (row.get("address") or "").strip()
        segment = (row.get("segment") or "Uncategorized").strip() or "Uncategorized"
        notes = (row.get("notes") or "").strip()
        existing_lat = (row.get("lat") or "").strip()
        existing_lon = (row.get("lon") or "").strip()

        if not name:
            warn(f"Row {i}: skipping — no name.")
            skipped += 1
            failures.append({**row, "_reason": "missing name"})
            continue

        # Determine coordinates
        lat = lon = None
        if existing_lat and existing_lon:
            try:
                lat = float(existing_lat)
                lon = float(existing_lon)
                used_existing += 1
            except ValueError:
                warn(f"Row {i} ({name}): bad lat/lon in CSV — re-geocoding.")
                lat = lon = None

        if (lat is None or lon is None) and not args.no_geocode:
            if not address:
                warn(f"Row {i} ({name}): no address and no coords — skipping.")
                skipped += 1
                failures.append({**row, "_reason": "no address, no coords"})
                continue

            time.sleep(RATE_LIMIT_SECONDS)  # respect Nominatim TOS
            result = geocode_one(address, contact_email, cache)
            if result is None:
                warn(f"Row {i} ({name}): could not geocode {address!r}")
                failures.append({**row, "_reason": "geocode failed"})
                continue
            lat, lon = result
            geocoded += 1

        if lat is None or lon is None:
            failures.append({**row, "_reason": "no coords resolved"})
            continue

        # Add to KML
        folder = folders.get(segment)
        if folder is None:
            folder = kml.newfolder(name=segment)
            folders[segment] = folder

        pnt = folder.newpoint(name=name, coords=[(lon, lat)])
        desc_lines = []
        if address:
            desc_lines.append(f"Address: {address}")
        if notes:
            desc_lines.append(notes)
        if desc_lines:
            pnt.description = "\n".join(desc_lines)

    # --- save outputs ---
    save_cache(cache)

    out_path = Path(args.output)
    kml.save(str(out_path))
    success(f"Wrote {out_path}")
    info(
        f"Stats: {geocoded} newly geocoded, {used_existing} from existing lat/lon, "
        f"{skipped} skipped, {len(failures)} failed"
    )

    if failures:
        fail_path = out_path.with_name(out_path.stem + "_failures.csv")
        with fail_path.open("w", encoding="utf-8", newline="") as fh:
            fieldnames = list(rows[0].keys()) + ["_reason"]
            w = csv.DictWriter(fh, fieldnames=fieldnames)
            w.writeheader()
            for f in failures:
                w.writerow({k: f.get(k, "") for k in fieldnames})
        warn(f"Wrote {fail_path} — fix and re-run; cache will skip ones already done.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
