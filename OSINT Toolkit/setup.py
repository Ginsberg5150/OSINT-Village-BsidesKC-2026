#!/usr/bin/env python3
"""
setup.py — Wildcard OSINT Toolkit interactive setup wizard

Run this once to configure the toolkit. It will:
  - Walk you through each config value
  - Tell you what each one is for, where to get it, and whether it's required
  - Save your answers to .env (creating the file if it doesn't exist)
  - Skip values that are already set unless you pass --reconfigure

You don't have to run this — every script will prompt you for missing values
on its own. This is just the convenient way to do it all at once.

Usage:
    python3 setup.py
    python3 setup.py --reconfigure        # ask about everything, even already-set values
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "scripts" / "lib"))
from osint_common import (  # noqa: E402
    banner, info, warn, success, hint,
    CONFIG_REGISTRY, ENV_PATH, _load_env, _write_env_value, _CACHED_ENV,
    _interactive_prompt, validate_email, _VALIDATORS,
)


def main() -> int:
    p = argparse.ArgumentParser(description="Configure the toolkit interactively.")
    p.add_argument(
        "--reconfigure",
        action="store_true",
        help="ask about every value, even ones already set",
    )
    args = p.parse_args()

    banner("Wildcard OSINT Toolkit — Setup", f"Editing {ENV_PATH}")

    print("This wizard will walk through each setting. Required ones have a [REQ] tag.", file=sys.stderr)
    print("You can press Enter to skip optional values; you'll be re-prompted by", file=sys.stderr)
    print("the scripts that need them later.\n", file=sys.stderr)

    existing = _load_env()

    for key, spec in CONFIG_REGISTRY.items():
        already_set = key in existing and existing[key]
        if already_set and not args.reconfigure:
            success(f"{key}: already set (skipping — use --reconfigure to change)")
            continue

        required = not spec.get("optional", True)
        # Use the same prompt the scripts use
        val = _interactive_prompt(key, spec, required, save=True)
        if not val and required:
            warn(f"{key} was required but not set. Some scripts will fail until you set it.")

    print("", file=sys.stderr)
    success("Setup complete.")
    info(f"Your config is in {ENV_PATH}. Edit it directly any time.")
    info("To run a script:")
    hint("  python3 scripts/domain_to_dossier.py shopify.com")
    hint("  python3 scripts/edgar_subsidiaries.py 'Apple'")
    hint("  python3 scripts/cert_enum.py example.com")
    hint("  python3 scripts/favicon_pivot.py example.com")
    hint("  python3 scripts/plants_to_kml.py plants.csv -o out.kml")

    return 0


if __name__ == "__main__":
    sys.exit(main())
