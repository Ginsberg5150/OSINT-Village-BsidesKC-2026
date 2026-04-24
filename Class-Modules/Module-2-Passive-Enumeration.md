# Module 2 — Passive Enumeration
## What's exposed?

**Time budget:** 60 minutes (11:20–12:20)
**Prereqs:** Module 1 complete; org graph in your notes
**Pairs with:** `Student-Labs/Lab-Module-2-Hunter.md`, `Student-Labs/Lab-Module-2-Ghost.md`

---

## Hook

> Caterpillar does not want you to know how many subdomains they have.
> They do not have a choice.
> Their own SSL certificates tell on them.

---

## Learning objectives

By the end of Module 2 you can:

1. Enumerate subdomains via Certificate Transparency without touching the target
2. Run the **subfinder → dnsx → ASN** unified passive chain
3. Read DNS records as disclosure (SPF, MX, TXT, NS)
4. Map an org's IP space via **Team Cymru's ASN-over-DNS** lookup
5. Pull passive port and service info from Shodan InternetDB (keyless)
6. Fall back to `Mirrors/` when upstream sources rate-limit
7. Spot RFC1918 leaks in CT logs (the most underused enumeration finding)

---

## Talk topics

### 1. Passive vs. active — today's rule

Today is **passive only on Caterpillar**. We're going to read what
other systems already collected about CAT — certificate authorities,
DNS providers, public scanners — without ever sending a packet to a
CAT-owned IP.

This is legal. It's ethical. It's also the only OSINT mode that scales
— a passive workflow you can run on 1,000 targets in a day is more
valuable than an active one that requires written authorization for
each.

### 2. Certificate Transparency: the great unmasker

Every TLS certificate issued by a publicly trusted CA since ~2018 ends
up in a public Certificate Transparency log. There is no opt-out for
public-internet-facing services that need browser-trusted certs.

This means: **every public-facing subdomain CAT has issued a cert for
is publicly enumerable**, regardless of whether it's listed anywhere
else, indexed by Google, or even resolves today.

The aggregator we use most:
```
https://crt.sh/?q=%25.caterpillar.com&output=json
```

Also worth knowing for `cat.com`:
```
https://crt.sh/?q=%25.cat.com&output=json
```

### 3. crt.sh under classroom load — and the fallbacks

crt.sh runs on a single PostgreSQL instance and **routinely returns
502 under modest load**. When 30 students hit it simultaneously, it
dies for the rest of the hour.

Fallback order, in priority:

1. **subfinder** (aggregates ~30 sources including CT — *use this
   first*, not crt.sh raw)
2. **`Mirrors/crtsh/caterpillar.json`** (pre-cached the night before)
3. **Certspotter:** `https://api.certspotter.com/v1/issuances?domain=caterpillar.com&include_subdomains=true&expand=dns_names`
4. **Censys CT search:** `https://search.censys.io/certificates?q=parsed.names%3A%25.caterpillar.com` (browser, no key needed for browse)
5. **Merklemap:** `https://merklemap.com/search?query=%25.caterpillar.com`

The lesson here is real: when one source is at capacity, you route
around it. The mirror is what professionals do at scale, not training
wheels.

### 4. The ProjectDiscovery unified chain

This is the command to commit to muscle memory:

```bash
subfinder -silent -d caterpillar.com | \
  dnsx -silent -resp-only | \
  sort -u
```

What's happening:
- `subfinder` aggregates passive subdomain sources (~30 of them) and
  emits a deduplicated list
- `dnsx` resolves each subdomain to verify it actually resolves today
  (cuts the historical/stale entries CT logs surface)
- The output is the set of **resolvable subdomains** with their IPs

For ASN attribution, add:

```bash
subfinder -silent -d caterpillar.com | \
  dnsx -silent -resp-only | \
  asnmap -silent
```

Output now includes ASN ownership for each resolved IP.

### 5. DNS as disclosure

The target's DNS configuration is *informed consent* — they published
it for resolution to work. Read it like a menu of vendor relationships.

```bash
# Email vendor — SPF record reveals who handles outbound mail
dig +short TXT caterpillar.com | grep -i spf

# Mail routing — MX reveals spam filter / mail platform
dig +short MX caterpillar.com

# SaaS integrations — TXT records reveal vendor verifications
dig +short TXT caterpillar.com

# DNS provider — NS reveals who runs their authoritative zones
dig +short NS caterpillar.com
```

**TXT records deserve their own callout** (this is a QA-flagged fix —
TXT enumeration is genuinely under-used). Many companies leave 30–50
SaaS vendor verification strings in TXT records: `_amazonses-*` for
SES, `google-site-verification` for various Google products, vendor
strings for Klaviyo, OpenAI usage, Stripe, DocuSign, Zoom, Atlassian,
and more.

When you walk the TXT records of a Fortune 100, you're often reading
**the most accurate vendor list that exists for that company** — more
accurate than their own published procurement page.

### 6. ASN / IP space — Team Cymru via DNS

You don't need to register for an account or call an HTTPS API to
look up ASN ownership. Team Cymru runs a free DNS-based lookup service:

```bash
# Reverse the IP and prepend it to origin.asn.cymru.com
# Example: 12.34.56.78 → 78.56.34.12.origin.asn.cymru.com
dig +short TXT 78.56.34.12.origin.asn.cymru.com
```

Returns: `"AS_NUMBER | PREFIX | COUNTRY | REGISTRY | DATE"`.

This is the fastest, most quota-free way to attribute an IP to an
organization. Build it into your default workflow.

For more interactive exploration: `https://bgp.he.net/` (Hurricane
Electric BGP toolkit, web UI) lets you walk an ASN's prefixes, see
peering relationships, and find adjacent IP space.

### 7. Shodan InternetDB — keyless passive port info

Shodan InternetDB is a free, keyless API that returns Shodan's known
port and vulnerability data for an IP, without the rate limits of the
full Shodan API:

```bash
curl -s https://internetdb.shodan.io/12.34.56.78
```

Returns JSON with open ports, hostnames, and known CVEs.

**Discipline:** dedupe to *distinct IPs* before you call this. If your
subdomain enumeration produced 200 hostnames pointing at 12 unique
IPs, hit InternetDB 12 times, not 200. The QA review on this workshop
specifically flagged a script that fired 146 unnecessary calls and
got rate-limited to zero results.

### 8. RFC1918-leak hunting in CT logs

This is one of the highest-value enumeration findings and almost
nobody looks for it:

When a company issues TLS certificates for **internal-only hostnames**
that include RFC1918 IPs (`10.x.x.x`, `172.16-31.x.x`, `192.168.x.x`),
those certificates show up in public CT logs. Internal hostnames like
`internal-app-10.90.0.11.corp.example.com` leak the internal IP
addressing scheme to anyone who searches for it.

Search pattern:

```bash
# In your subfinder output, look for hostnames containing RFC1918 patterns
grep -E '(^|[^0-9])(10|172\.(1[6-9]|2[0-9]|3[01])|192\.168)\.' subdomains.txt
```

Even a single `10.x.x.x`-bearing subdomain in CT for your target is a
high-value finding: it tells you the internal addressing scheme, often
hints at firewall conventions (e.g., `fw04-ha121528` → firewall
cluster 04 with HA pair at 12.15.28.x), and signals lax cert hygiene
that may exist elsewhere in their infrastructure.

### 9. The hostname-embeds-infra pattern

Related to #8: many companies embed infrastructure hints in hostnames
themselves. Patterns to watch for:

- `lb-`, `proxy-`, `gw-`, `fw-` → load balancers, proxies, gateways,
  firewalls
- `dc1-`, `dc2-`, `aws-`, `gcp-`, `azure-` → datacenter or cloud
  region tells
- `dev-`, `stg-`, `qa-`, `uat-` → environment tells
- `-int-`, `-internal-`, `-private-` → not-meant-for-public hosts
  that ended up in CT anyway
- `vpn-`, `rdp-`, `cit-` → remote access infrastructure

A subdomain named `dev-cit-aws-us-east-1.caterpillar.com` is reading
its own architecture out loud. Your dossier benefits.

---

## Live demo (instructor, ~15 minutes)

### Step 1 — crt.sh raw query

```
https://crt.sh/?q=%25.caterpillar.com
```

Show the volume. Discuss what would happen if 30 people hit this
simultaneously (502s).

### Step 2 — subfinder unified chain

```bash
subfinder -silent -d caterpillar.com | dnsx -silent -resp-only | sort -u
```

Watch the output stream in. Discuss why this is the production
default, not crt.sh raw.

### Step 3 — Mirror fallback demo

Open `Mirrors/crtsh/caterpillar.json` directly. Show that the data is
there, it's static, it works under any load. **This is what
professionals do.**

### Step 4 — DNS disclosure walk

```bash
dig TXT caterpillar.com
```

Walk the output line by line. Every TXT line is a vendor relationship
or a verification token. Translate three of them live.

### Step 5 — Team Cymru ASN lookup

Pick a resolved IP from Step 2. Run the Cymru DNS lookup. Read the
ASN, owner, country, prefix.

### Step 6 — Shodan InternetDB

```bash
curl -s https://internetdb.shodan.io/<resolved-ip> | jq
```

Show the open ports and any CVE data. Note: keyless. Note: rate-limit
discipline.

### Step 7 — RFC1918-in-CT hunt

Grep the resolved subdomain list for the RFC1918 pattern. If
Caterpillar happens to have one (they might), surface it. If not,
demonstrate against the pattern using a well-known leaker.

---

## Mirror-fallback notes

| Source | When to fall back | Mirror path |
|--------|-------------------|-------------|
| crt.sh | 502 or slow >10s | `Mirrors/crtsh/caterpillar.json`, `Mirrors/crtsh/cat.json` |
| subfinder upstream sources | Any 429 from any source | `Mirrors/subfinder/caterpillar.txt`, `Mirrors/subfinder/cat.txt` |
| Wayback CDX | First 429, persists for the day | `Mirrors/wayback/caterpillar.json` |

The mirror data was captured the night before class. It's a snapshot,
not real-time — if a finding is time-sensitive, note that in your
dossier with an Admiralty rating reflecting the snapshot date.

---

## Lab assignments

- 🔵 Hunter: `Student-Labs/Lab-Module-2-Hunter.md`
- 🟠 Ghost: `Student-Labs/Lab-Module-2-Ghost.md`

30 minutes. Lunch is at 12:20.

---

## Transition to Module 3

> We know the org. We know the assets.
> Now: what techniques cross the active line, and how do we
> demonstrate them without crossing it on Caterpillar?

Module 3 covers the **active enumeration toolset** — theHarvester,
recon-ng, DNS brute forcing — but runs the demos in their *passive
aggregator* modes only, since CAT is a no-active target. The active
techniques are the lesson; the demonstration respects scope.

Open `Class-Modules/Module-3-Active-Techniques-Passive-Demos.md`
after lunch.
