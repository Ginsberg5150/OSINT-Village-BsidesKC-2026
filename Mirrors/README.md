# Mirrors/ · Pre-cached upstream data

**Why this exists:** When 30 students hit crt.sh simultaneously,
crt.sh returns 502 for the rest of the hour. Same for Wayback CDX
under load, and for some subfinder upstream sources. Mirrors eliminate
the class-day rate-limit problem by caching the upstream data the
**night before**.

The mirror is **not a shortcut** — it's how professionals run recon at
scale against rate-limited sources. Learning the fallback pattern is
itself a workshop objective.

---

## What's cached here

| Path | Source | Notes |
|------|--------|-------|
| `crtsh/caterpillar.json` | crt.sh JSON export for `caterpillar.com` | overnight snapshot |
| `crtsh/cat.json` | crt.sh JSON export for `cat.com` | overnight snapshot |
| `subfinder/caterpillar.txt` | subfinder output for `caterpillar.com` | aggregated from ~30 passive sources |
| `subfinder/cat.txt` | subfinder output for `cat.com` | " |
| `wayback/caterpillar.json` | Wayback CDX export for `*.caterpillar.com` | historical hostnames |

Each file includes a small JSON header or top-line comment with the
capture timestamp — cite the snapshot date in your dossier when you
use mirror data.

---

## Using a mirror during labs

The labs reference the mirror paths where relevant. Quick lookups:

```bash
# Pull subdomains from the crt.sh mirror
jq -r '.[].name_value' Mirrors/crtsh/caterpillar.json | tr ',' '\n' | sort -u

# Pull subdomains from the subfinder mirror
cat Mirrors/subfinder/caterpillar.txt | sort -u

# Pull Wayback hostnames
jq -r '.[1:] | .[] | .[0]' Mirrors/wayback/caterpillar.json | awk -F/ '{print $3}' | sort -u
```

---

## Pre-cache recipe (instructor, night before class)

Run these commands the evening before. Total time: ~10–15 min.

### crt.sh

```bash
mkdir -p Mirrors/crtsh

# caterpillar.com
curl -s 'https://crt.sh/?q=%25.caterpillar.com&output=json' \
  -H "User-Agent: osint-village-bsideskc-2026/1.0 precache" \
  -o Mirrors/crtsh/caterpillar.json

# cat.com
curl -s 'https://crt.sh/?q=%25.cat.com&output=json' \
  -H "User-Agent: osint-village-bsideskc-2026/1.0 precache" \
  -o Mirrors/crtsh/cat.json

# Verify — should be large JSON arrays
wc -c Mirrors/crtsh/*.json
jq 'length' Mirrors/crtsh/caterpillar.json
```

If crt.sh 502s during precache, retry with a 30-second sleep between.
If it still fails, try tomorrow morning 3+ hours before class.

### subfinder

```bash
mkdir -p Mirrors/subfinder

subfinder -silent -d caterpillar.com -o Mirrors/subfinder/caterpillar.txt
subfinder -silent -d cat.com -o Mirrors/subfinder/cat.txt

wc -l Mirrors/subfinder/*.txt
```

### Wayback CDX

```bash
mkdir -p Mirrors/wayback

curl -s \
  'https://web.archive.org/cdx/search/cdx?url=*.caterpillar.com&output=json&fl=original,timestamp,statuscode&collapse=urlkey&limit=20000' \
  -H "User-Agent: osint-village-bsideskc-2026/1.0 precache" \
  -o Mirrors/wayback/caterpillar.json

jq 'length' Mirrors/wayback/caterpillar.json
```

Wayback CDX often 429s even on the night before — be prepared to
retry 2–3 times with 60-second sleeps between.

---

## What's NOT mirrored (on purpose)

- **EDGAR** — usually robust; no mirror needed. Fall back to retrying
  with a 60s sleep if you hit a temporary hiccup.
- **USASpending.gov** — robust API; no mirror needed.
- **DNS queries** — direct resolution works fine at classroom scale;
  no mirror needed.
- **Team Cymru ASN DNS** — free and high-capacity; no mirror needed.
- **Shodan InternetDB** — free, rate-limited per-IP but fine if
  students dedupe to distinct IPs first (this is a teachable point,
  not a mirror case).

---

## When students must explicitly cite the mirror

Any finding sourced from a mirror file should be cited with:

- The mirror path used (`Mirrors/crtsh/caterpillar.json`)
- The snapshot timestamp (from the file metadata or precache log)
- Admiralty rating **B3** instead of **B2** — the source is
  cached-and-potentially-stale, which slightly lowers credibility.

Example dossier line:
```
Subdomain enumeration sourced from `Mirrors/crtsh/caterpillar.json`
(snapshot 2026-04-24T22:15:00Z) due to crt.sh 502 during class
runtime; N subdomains identified. [B3]
```

The professional move isn't to hide the mirror — it's to be explicit
about it.
