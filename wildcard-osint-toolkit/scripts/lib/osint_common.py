"""
osint_common.py — Wildcard OSINT Toolkit shared helpers
========================================================

Centralizes the boring-but-critical parts that, when missing, cause every
script in this toolkit to fail with a cryptic error:

  - Loading API keys / contact emails from .env (with safe fallbacks)
  - Interactive prompting when a required value is missing, with the
    option to save it back to .env for next time
  - HTTP requests with retries, backoff, sane timeouts, and a User-Agent
    that identifies the toolkit (and contact email when SEC/Nominatim
    require it)
  - Validating user input (email, CIK, domain) before the API gets it
  - Friendly error printing — what failed, why, and what to do about it

Design rules:
  - Never crash on a missing API key. Degrade or prompt. Always.
  - Never make the user re-type something they've already given.
  - Never hide *why* a request failed. Tell them in plain English.

Import this from any script in scripts/:

    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent / "lib"))
    from osint_common import (
        get_config, prompt_for, http_get, http_get_json,
        info, warn, error, success, ConfigError,
    )
"""

from __future__ import annotations

import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Optional

try:
    import requests
except ImportError:
    print(
        "[!] The `requests` library is required.\n"
        "    Install it with:  pip install requests\n",
        file=sys.stderr,
    )
    sys.exit(1)


# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

# Repo root = parent of scripts/ dir = grandparent of this file
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_PATH = REPO_ROOT / ".env"

USER_AGENT_BASE = "wildcard-osint-toolkit/2.0"

# Every config key the toolkit might ask about. Each entry describes:
#   - the env var name
#   - human-friendly description (shown in prompts)
#   - whether it is REQUIRED (True) or OPTIONAL (False)
#   - free-form help text shown when the user is missing it (URL, what it does)
#   - optional validator that returns (ok, cleaned_value, error_msg)
CONFIG_REGISTRY: dict[str, dict] = {
    "CONTACT_EMAIL": {
        "description": "Your contact email",
        "required_for": ["SEC EDGAR", "OSM Nominatim geocoder"],
        "help": (
            "SEC EDGAR and OSM Nominatim REQUIRE a real contact email in the\n"
            "  User-Agent header. Without it, requests silently fail or 403.\n"
            "  Use a working email — they may contact you about abusive use.\n"
            "  A sock-puppet email is fine if it actually receives mail."
        ),
        "optional": False,
    },
    "SHODAN_API_KEY": {
        "description": "Shodan API key",
        "required_for": ["Deep Shodan host lookup", "Favicon pivot"],
        "help": (
            "Get one at https://account.shodan.io/\n"
            "  Free tier is limited; $5-lifetime sales run a few times a year.\n"
            "  WITHOUT this key, scripts fall back to InternetDB (free, no key)\n"
            "  which still gives you ports, CPEs, tags, and known CVEs."
        ),
        "optional": True,
    },
    "CENSYS_API_ID": {
        "description": "Censys API ID",
        "required_for": ["Censys Platform queries"],
        "help": (
            "Get credentials at https://platform.censys.io/\n"
            "  Community tier ≈ 250 queries/month."
        ),
        "optional": True,
    },
    "CENSYS_API_SECRET": {
        "description": "Censys API secret",
        "required_for": ["Censys Platform queries"],
        "help": "Pairs with CENSYS_API_ID. Same signup link.",
        "optional": True,
    },
    "OPENCORPORATES_API_KEY": {
        "description": "OpenCorporates API key",
        "required_for": ["Bulk corporate-registry lookups"],
        "help": (
            "Get one at https://opencorporates.com/api_accounts/new\n"
            "  Public access is heavily rate-limited; an API key raises the\n"
            "  ceiling. Free tier exists for personal/research use."
        ),
        "optional": True,
    },
    "NVD_API_KEY": {
        "description": "NIST NVD API key",
        "required_for": ["Faster CVE lookups"],
        "help": (
            "Free key at https://nvd.nist.gov/developers/request-an-api-key\n"
            "  Without a key the NVD throttles you to 1 req / 6 sec.\n"
            "  With one you get 1 req / 0.6 sec."
        ),
        "optional": True,
    },
    "HUNTER_API_KEY": {
        "description": "Hunter.io API key",
        "required_for": ["Email-pattern lookup for a domain"],
        "help": "Get one at https://hunter.io/api — free tier is 25 / month.",
        "optional": True,
    },
}


class ConfigError(RuntimeError):
    """Raised when a required config value is missing AND we can't prompt."""


# ---------------------------------------------------------------------------
# .ENV PARSING (no python-dotenv dependency — keep the toolkit lean)
# ---------------------------------------------------------------------------

def _parse_env_file(path: Path) -> dict[str, str]:
    """Tiny .env parser. Handles KEY=VALUE, ignores comments and blanks."""
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key:
            out[key] = val
    return out


def _write_env_value(path: Path, key: str, value: str) -> None:
    """Append or update KEY=VALUE in the .env file. Creates the file if needed."""
    existing = _parse_env_file(path) if path.exists() else {}
    existing[key] = value

    # Preserve comments by reading the original line by line and replacing
    # only the matching key. If file doesn't exist, write fresh.
    if path.exists():
        new_lines = []
        seen = set()
        for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
            stripped = raw.strip()
            if (
                stripped
                and not stripped.startswith("#")
                and "=" in stripped
                and stripped.split("=", 1)[0].strip() == key
            ):
                new_lines.append(f"{key}={value}")
                seen.add(key)
            else:
                new_lines.append(raw)
        if key not in seen:
            if new_lines and new_lines[-1].strip() != "":
                new_lines.append("")
            new_lines.append(f"{key}={value}")
        path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    else:
        # Brand-new .env — write a friendly header
        header = (
            "# Wildcard OSINT Toolkit — local config\n"
            "# This file is git-ignored. Do not commit it.\n"
            "# Edit values directly or let the scripts add them for you.\n\n"
        )
        path.write_text(header + f"{key}={value}\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# COLORED OUTPUT (degrades gracefully when stderr is not a tty)
# ---------------------------------------------------------------------------

def _supports_color() -> bool:
    return sys.stderr.isatty() and os.environ.get("NO_COLOR") is None


_C = {
    "reset": "\033[0m",
    "dim": "\033[2m",
    "bold": "\033[1m",
    "red": "\033[31m",
    "yellow": "\033[33m",
    "green": "\033[32m",
    "cyan": "\033[36m",
    "blue": "\033[34m",
}


def _c(text: str, color: str) -> str:
    if not _supports_color():
        return text
    return f"{_C.get(color, '')}{text}{_C['reset']}"


def info(msg: str) -> None:
    print(f"{_c('[*]', 'cyan')} {msg}", file=sys.stderr)


def warn(msg: str) -> None:
    print(f"{_c('[!]', 'yellow')} {msg}", file=sys.stderr)


def error(msg: str) -> None:
    print(f"{_c('[X]', 'red')} {msg}", file=sys.stderr)


def success(msg: str) -> None:
    print(f"{_c('[+]', 'green')} {msg}", file=sys.stderr)


def hint(msg: str) -> None:
    """Faint indented help text."""
    for line in msg.splitlines():
        print(f"    {_c(line, 'dim')}", file=sys.stderr)


# ---------------------------------------------------------------------------
# CONFIG LOADING + INTERACTIVE PROMPTING
# ---------------------------------------------------------------------------

# Cache loaded env so we don't re-read .env every call
_CACHED_ENV: Optional[dict[str, str]] = None


def _load_env() -> dict[str, str]:
    global _CACHED_ENV
    if _CACHED_ENV is None:
        _CACHED_ENV = _parse_env_file(ENV_PATH)
    return _CACHED_ENV


def get_config(
    key: str,
    *,
    required: Optional[bool] = None,
    prompt: bool = True,
    save: bool = True,
    fallback: Optional[str] = None,
) -> Optional[str]:
    """
    Resolve a config value in this order:
      1. process environment (highest priority — lets users one-shot override)
      2. .env file in the repo root
      3. interactive prompt (if `prompt` is True AND stdin is a tty)
      4. `fallback` value (if provided)

    Args:
      key: env var name (e.g. "SHODAN_API_KEY"). Should be in CONFIG_REGISTRY
           but unknown keys are accepted with a generic prompt.
      required: override the registry's "optional" flag. None = use registry.
      prompt: ask the user interactively if missing. Set False for non-tty
              automation; the function will then return None or `fallback`.
      save: if we prompted and got a value, write it back to .env. If False
            we hold the value in process memory only for this run.
      fallback: returned only if nothing else resolves AND key is optional.

    Returns:
      The resolved value (str), or None if optional and unresolved.

    Raises:
      ConfigError if required, missing, and we can't prompt (no tty / prompt=False).
    """
    spec = CONFIG_REGISTRY.get(key, {})
    is_required = (not spec.get("optional", True)) if required is None else required

    # 1) process env wins
    val = os.environ.get(key)
    if val:
        return val

    # 2) .env
    env_vals = _load_env()
    val = env_vals.get(key)
    if val:
        os.environ[key] = val  # surface for libs that read os.environ
        return val

    # 3) prompt
    if prompt and sys.stdin.isatty() and sys.stderr.isatty():
        val = _interactive_prompt(key, spec, is_required, save)
        if val:
            return val

    # 4) fallback or fail
    if is_required:
        raise ConfigError(
            f"Required config value '{key}' is missing and could not be obtained.\n"
            f"  Set it via env var, add it to {ENV_PATH}, or run interactively."
        )

    return fallback


def _interactive_prompt(
    key: str, spec: dict, required: bool, save: bool
) -> Optional[str]:
    """Prompt the user for a missing config value. Returns the value or None."""
    desc = spec.get("description", key)
    help_text = spec.get("help", "")
    needed_for = spec.get("required_for", [])

    print("", file=sys.stderr)
    if required:
        warn(f"Missing required config: {desc} ({key})")
    else:
        info(f"Optional config not set: {desc} ({key})")

    if needed_for:
        hint(f"Used for: {', '.join(needed_for)}")
    if help_text:
        hint(help_text)

    suffix = "" if required else " (press Enter to skip)"
    try:
        val = input(f"  {desc}{suffix}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("", file=sys.stderr)
        return None

    if not val:
        if required:
            warn("No value entered. Aborting this step.")
        return None

    # Validate (best-effort — only known keys have validators)
    validator = _VALIDATORS.get(key)
    if validator is not None:
        ok, cleaned, errmsg = validator(val)
        if not ok:
            error(f"Invalid value: {errmsg}")
            # Recurse once to give the user another shot
            return _interactive_prompt(key, spec, required, save)
        val = cleaned

    # Save?
    if save:
        try:
            ans = input(f"  Save to {ENV_PATH.name} for future runs? [Y/n]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            ans = "n"
        if ans in ("", "y", "yes"):
            try:
                _write_env_value(ENV_PATH, key, val)
                success(f"Saved {key} to {ENV_PATH}")
                # update cache
                if _CACHED_ENV is not None:
                    _CACHED_ENV[key] = val
            except OSError as e:
                warn(f"Could not write .env: {e}. Value will be used for this run only.")

    os.environ[key] = val
    return val


# ---------------------------------------------------------------------------
# VALIDATORS
# ---------------------------------------------------------------------------

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
DOMAIN_RE = re.compile(
    r"^(?=.{1,253}$)([a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+"
    r"[a-zA-Z]{2,63}$"
)
CIK_RE = re.compile(r"^\d{1,10}$")


def validate_email(val: str) -> tuple[bool, str, str]:
    val = val.strip()
    if EMAIL_RE.match(val):
        return True, val, ""
    return False, val, "Doesn't look like a valid email (need user@host.tld)."


def validate_domain(val: str) -> tuple[bool, str, str]:
    val = val.strip().lower().lstrip("*.").rstrip(".")
    # strip scheme + path if user pasted a URL
    val = re.sub(r"^https?://", "", val)
    val = val.split("/", 1)[0]
    val = val.split(":", 1)[0]  # strip port
    if DOMAIN_RE.match(val):
        return True, val, ""
    return False, val, "Doesn't look like a valid domain (need example.com)."


def validate_cik(val: str) -> tuple[bool, str, str]:
    val = val.strip().lstrip("0") or "0"  # SEC accepts un-padded but we'll pad later
    if CIK_RE.match(val):
        # SEC zero-pads CIK to 10 digits in URLs
        return True, val.zfill(10), ""
    return False, val, "CIK should be digits only, e.g. 0000320193 or 320193."


_VALIDATORS = {
    "CONTACT_EMAIL": validate_email,
}


# ---------------------------------------------------------------------------
# PROMPT-FOR-VALUE (used by scripts for non-config inputs like target domain)
# ---------------------------------------------------------------------------

def prompt_for(
    name: str,
    *,
    description: str = "",
    validator=None,
    required: bool = True,
    default: Optional[str] = None,
    examples: Optional[list[str]] = None,
) -> Optional[str]:
    """
    Prompt the user for a value (NOT a config secret — for things like
    "what domain are you scanning?" or "what CIK?").

    Returns the value, or None if optional and skipped.
    Raises ConfigError if required and no tty.
    """
    if not (sys.stdin.isatty() and sys.stderr.isatty()):
        if required:
            raise ConfigError(
                f"'{name}' is required but no terminal is available to prompt. "
                f"Pass it as a CLI argument."
            )
        return default

    print("", file=sys.stderr)
    if description:
        info(description)
    if examples:
        hint(f"Examples: {', '.join(examples)}")

    suffix = ""
    if default:
        suffix = f" [{default}]"
    elif not required:
        suffix = " (optional, press Enter to skip)"

    while True:
        try:
            val = input(f"  {name}{suffix}: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("", file=sys.stderr)
            if required:
                raise SystemExit(1)
            return default

        if not val:
            if default is not None:
                return default
            if not required:
                return None
            warn("Value is required.")
            continue

        if validator is not None:
            ok, cleaned, errmsg = validator(val)
            if not ok:
                error(errmsg)
                continue
            return cleaned

        return val


# ---------------------------------------------------------------------------
# HTTP HELPERS
# ---------------------------------------------------------------------------

DEFAULT_TIMEOUT = 30
DEFAULT_RETRIES = 3
RETRY_BACKOFF = 2.0  # seconds; exponential


def build_user_agent(contact_email: Optional[str] = None) -> str:
    """Build a User-Agent string. Includes contact email when available
    (required by SEC EDGAR and OSM Nominatim TOS)."""
    if contact_email:
        return f"{USER_AGENT_BASE} (contact: {contact_email})"
    return f"{USER_AGENT_BASE} (https://github.com/wildcard-llc/wildcard-osint-toolkit)"


def http_get(
    url: str,
    *,
    headers: Optional[dict] = None,
    params: Optional[dict] = None,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
    contact_email: Optional[str] = None,
    expect_json: bool = False,
    raise_for_status: bool = True,
) -> requests.Response:
    """
    GET a URL with retries, backoff, and a sensible User-Agent.

    Distinguishes:
      - Transient failures (5xx, 429, timeouts, ConnectionError) → retry
      - Permanent failures (4xx other than 429) → raise immediately with a
        readable explanation
      - Network down → friendly error
    """
    final_headers = {"User-Agent": build_user_agent(contact_email)}
    if expect_json:
        final_headers["Accept"] = "application/json"
    if headers:
        final_headers.update(headers)

    last_exc: Optional[Exception] = None
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, headers=final_headers, params=params, timeout=timeout)
        except requests.exceptions.ConnectionError as e:
            last_exc = e
            warn(
                f"Connection error talking to {_short_host(url)} "
                f"(attempt {attempt}/{retries}): {_short_exc(e)}"
            )
            if attempt < retries:
                time.sleep(RETRY_BACKOFF * attempt)
            continue
        except requests.exceptions.Timeout as e:
            last_exc = e
            warn(
                f"Timeout talking to {_short_host(url)} after {timeout}s "
                f"(attempt {attempt}/{retries})."
            )
            if attempt < retries:
                time.sleep(RETRY_BACKOFF * attempt)
            continue
        except requests.exceptions.RequestException as e:
            last_exc = e
            error(f"Request failed: {e}")
            break

        # Got a response — decide whether to retry
        if r.status_code in (429, 500, 502, 503, 504):
            warn(
                f"{r.status_code} from {_short_host(url)} "
                f"(attempt {attempt}/{retries}). Backing off..."
            )
            if attempt < retries:
                # Honor Retry-After if present
                ra = r.headers.get("Retry-After")
                wait = float(ra) if ra and ra.replace(".", "", 1).isdigit() else RETRY_BACKOFF * attempt
                time.sleep(wait)
                continue
        return _maybe_raise(r, url, raise_for_status)

    # Exhausted retries
    if last_exc:
        raise last_exc
    raise requests.exceptions.RequestException(
        f"Could not reach {url} after {retries} attempts."
    )


def http_get_json(url: str, **kwargs) -> Any:
    """GET and parse JSON. Raises a clear error if the body isn't JSON."""
    kwargs["expect_json"] = True
    r = http_get(url, **kwargs)
    try:
        return r.json()
    except ValueError as e:
        snippet = (r.text or "")[:200].replace("\n", " ")
        raise ValueError(
            f"Expected JSON from {url} but got non-JSON ({len(r.content)} bytes). "
            f"First 200 chars: {snippet!r}"
        ) from e


def _maybe_raise(r: requests.Response, url: str, raise_for_status: bool):
    if not raise_for_status or r.status_code < 400:
        return r

    host = _short_host(url)
    if r.status_code == 401:
        error(f"401 Unauthorized from {host}. Your API key is missing or wrong.")
    elif r.status_code == 403:
        error(
            f"403 Forbidden from {host}. Common causes:\n"
            f"      - Missing User-Agent contact email (required by SEC, Nominatim)\n"
            f"      - Datacenter/VPN IP blocked by the source\n"
            f"      - Resource requires a paid tier"
        )
    elif r.status_code == 404:
        error(f"404 Not Found at {url}. Check the spelling / target.")
    elif r.status_code == 429:
        error(f"429 Rate-limited by {host}. Slow down or use an API key for higher limits.")
    else:
        error(f"{r.status_code} {r.reason} from {host}.")
    r.raise_for_status()
    return r


def _short_host(url: str) -> str:
    try:
        return url.split("//", 1)[1].split("/", 1)[0]
    except IndexError:
        return url


def _short_exc(e: Exception) -> str:
    s = str(e)
    return (s[:120] + "...") if len(s) > 120 else s


# ---------------------------------------------------------------------------
# MISC HELPERS
# ---------------------------------------------------------------------------

def banner(title: str, subtitle: str = "") -> None:
    """Print a tidy header at the start of a script."""
    line = "─" * max(len(title), len(subtitle))
    print(_c(f"\n  {title}", "bold"), file=sys.stderr)
    if subtitle:
        print(_c(f"  {subtitle}", "dim"), file=sys.stderr)
    print(_c(f"  {line}\n", "dim"), file=sys.stderr)


def confirm(prompt: str, default: bool = True) -> bool:
    """Yes/no prompt. Returns the default if no tty."""
    if not (sys.stdin.isatty() and sys.stderr.isatty()):
        return default
    suffix = " [Y/n]" if default else " [y/N]"
    try:
        ans = input(f"  {prompt}{suffix}: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return default
    if not ans:
        return default
    return ans in ("y", "yes")
