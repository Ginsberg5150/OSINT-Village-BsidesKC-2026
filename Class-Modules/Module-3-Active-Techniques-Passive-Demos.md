# Module 3 — Active Techniques, Passive Demos
## The toolset, the fences

**Time budget:** 55 minutes (13:20–14:15)
**Prereqs:** Modules 1 & 2 complete
**Pairs with:** `Student-Labs/Lab-Module-3-Hunter.md`, `Student-Labs/Lab-Module-3-Ghost.md`

---

## Hook

> The tools we cover this hour can do active recon.
> We are not going to do active recon today.
> We are going to learn to drive them — and to know exactly where
> the line is, so when you have authorization tomorrow, you don't
> have to think about it.

Caterpillar is **no-active scope** for this workshop. The techniques
in this module are real, the tools work, and the demos run — but only
in their passive aggregator modes. For each technique, we'll cover
"what changes when you cross into active" so you know the boundary.

---

## Learning objectives

By the end of Module 3 you can:

1. Run **theHarvester** with explicit sources (the safe configuration)
2. Run a **pruned recon-ng** (only the modules that still work)
3. Detect a **DNS wildcard** before any brute force happens — always
4. Read **TXT records as a SaaS vendor map** (promoted technique)
5. Read **holehe semantic output** without misinterpreting `[x]`
6. Distinguish "passive aggregator mode" from "active mode" for each
   tool, and know which one you're in

---

## Talk topics

### 1. The active/passive line — operational definition

For Module 3, we use this working definition:

- **Passive:** you read what other systems collected. No packets sent
  to the target's infrastructure. Every query you make is to a
  third party that already knows about the target.
- **Active:** you send packets to the target's infrastructure. The
  target's logs see *your* IP. Active is appropriate **only** with
  written authorization (bug bounty scope, signed engagement letter,
  internal pentest charter).

Many tools blur this line. theHarvester can pull from passive sources
*or* it can do its own DNS brute. recon-ng has passive modules and
active modules. DNS brute is active by definition — you're sending
queries to the target's authoritative nameservers.

The discipline: **know which mode you're in, every time.**

### 2. theHarvester — explicit sources only

**Install (per QA fix):**
```bash
# The PyPI package "theHarvester" is a placeholder — wrong code.
# Install from git:
pip install git+https://github.com/laramies/theHarvester.git

# Verify:
which theHarvester && theHarvester -h | head -1
```

**Don't use `-b all`.** As of theHarvester v4.10.x, several sources
listed under `all` are dropped or broken (`bing`, `anubis`), and
running `-b all` crashes the tool partway through.

**Use an explicit source list** known to work as of class day:

```bash
theHarvester -d caterpillar.com -b duckduckgo,crtsh,dnsdumpster,yahoo,rapiddns,hackertarget,otx,certspotter,urlscan -l 500 -f cat-harvester.html
```

Every source in that list is a **passive aggregator** — none of them
touch caterpillar.com directly. theHarvester is in passive mode here
by virtue of source selection, not by a flag.

What active mode would look like (we don't do this today):
```bash
# DNS brute against the target — DON'T RUN THIS ON CAT
theHarvester -d caterpillar.com -c -b duckduckgo
# The -c flag triggers DNS brute via the target's nameservers
```

### 3. recon-ng — pruned

recon-ng is a recon framework with a workspace concept and pluggable
modules. It's been around long enough that significant portions of
its module ecosystem are bit-rotted: dead upstream APIs, captcha
walls, services that no longer exist (threatcrowd.org is gone, etc.).

For today, we use **only the modules confirmed working as of the QA
review.** The working set centers on:

- `recon/domains-hosts/netcraft` — passive, returns subdomains via
  Netcraft's site report
- (a few others depending on classroom day; check
  `Tools-and-Scripts/README.md` for the current working list)

The bit-rot itself is **a teachable point**, not just an inconvenience.
You're going to inherit toolkits in your career. You will be the
person who finds out that 7/8 modules don't work anymore. Practice
that workflow now.

```bash
# Start recon-ng with a workspace
recon-ng -w caterpillar

# Add target domain
[recon-ng][caterpillar] > db insert domains caterpillar.com

# Load and run a working module
[recon-ng][caterpillar] > modules load recon/domains-hosts/netcraft
[recon-ng][caterpillar][netcraft] > run
```

### 4. DNS brute force — wildcard detection FIRST

DNS brute force is the active technique most likely to give a
beginner false confidence. Run it without checking for wildcards
first, and you'll get **228 hits out of 228 attempts**, all pointing
at the same wildcard IP, and you'll think you found a goldmine.

You found nothing. The wildcard is the goldmine — for the target's
opsec, not yours.

**Mandatory step zero of any DNS brute:**

```bash
# Resolve a definitely-non-existent random hostname
dig +short DEFINITELY-NOT-A-REAL-SUBDOMAIN-XYZQ123.caterpillar.com

# If anything resolves, the domain has wildcards.
# Record the wildcard IP set.
```

If the random query returns IPs, the domain wildcards. Any brute
force result that resolves to those same IPs is a **wildcard echo,
not a real subdomain**. You filter your brute output against the
wildcard set, then HTTP-probe the survivors to see which actually
serve content.

**For Caterpillar:** based on the QA review, CAT does *not* wildcard
its public DNS. So a wildcard-detection step against caterpillar.com
returns NXDOMAIN for the random string — the **negative result is
itself a useful confirmation** of how to read this signal. Demo
exactly that.

> ⚠️ We are not running the actual brute force on Caterpillar today.
> CAT is no-active scope. The wildcard detection step *itself* is
> passive — it's a single DNS query. The brute that would follow is
> what crosses the line. On an active-permitted target, you'd
> continue with `dnsx -d caterpillar.com -w wordlist.txt` and filter
> the results against your recorded wildcard set. We'll show the
> command on a slide and stop.

### 5. TXT records as a SaaS vendor map (promoted technique)

This is technique #2 from the QA-flagged "promote to first-class"
list, and it deserves its own segment.

A single `dig TXT caterpillar.com` query commonly returns more
high-signal vendor intelligence than any passive aggregator. Each
TXT record is typically there because some SaaS vendor told the
target to add it for ownership verification or service routing.

Reading TXT records:

| TXT prefix / pattern | What it means |
|----------------------|---------------|
| `v=spf1 include:...` | SPF record — every `include:` is an authorized email sender |
| `google-site-verification=...` | Google product ownership (Search Console, Analytics, Workspace) |
| `MS=ms########` | Microsoft 365 / Azure tenant verification |
| `_amazonses-...` | AWS SES email sending |
| `klaviyo-site-verification=` | Klaviyo (email marketing) |
| `stripe-verification=` | Stripe |
| `docusign=` | DocuSign |
| `atlassian-domain-verification=` | Atlassian (Jira, Confluence) |
| `zoom-domain-verification=` | Zoom |
| `openai-domain-verification=` | OpenAI usage |
| `facebook-domain-verification=` | Meta business |
| `apple-domain-verification=` | Apple business services |

Walk a Fortune 100's TXT records and you've often built **the most
accurate vendor list that exists for that company** in under 30
seconds. SaaS sprawl is real, and TXT records are the most honest
source for what's actually in use.

### 6. holehe — semantic output reading

holehe checks whether an email address is registered on a list of
common services. Its output uses three symbols and **students
routinely misread them**:

| Symbol | Meaning |
|--------|---------|
| `[+]` | **Hit** — email IS registered on this service |
| `[-]` | **Confirmed not registered** — useful negative result |
| `[x]` | **Inconclusive** — usually rate-limited or service-side error, *not* a hit |

The most common mistake: reading `[x]` as a hit. It is not. Treat
`[x]` as "no signal, ignore" rather than "soft positive." Wait a
few minutes and re-run if you need a real answer for that service.

For today's Caterpillar work, we use holehe (if at all) only on
**non-employee emails** — for example, public press contact emails
listed on the company's investor relations page. Never on individual
employee addresses; that would cross into the people-aggregation
line we drew in Module 0.

### 7. Foundation DNS — a fingerprint to know

When you walk the NS records of a target during the DNS disclosure
step (Module 2), watch for:

```
gold.foundationdns.com
gold.foundationdns.net
gold.foundationdns.org
```

This is **Cloudflare Foundation DNS**, launched 2024. Most
fingerprint cheatsheets don't list it yet. Foundation DNS NS records
on a target tell you the target is a Cloudflare enterprise customer,
which has implications for further fingerprinting (a lot of traffic
will be Cloudflare-CDN-fronted, generic responses, etc.).

---

## Live demo (instructor, ~15 minutes)

### Step 1 — theHarvester explicit-sources run

```bash
theHarvester -d caterpillar.com -b duckduckgo,crtsh,dnsdumpster,yahoo,rapiddns,hackertarget,otx,certspotter,urlscan -l 200 -f cat-harvester.html
```

Watch the output. Open the resulting HTML report. Discuss the unique
hosts theHarvester surfaced that subfinder missed (and vice versa).

### Step 2 — recon-ng workspace + netcraft

```bash
recon-ng -w cat-demo
[cat-demo] > db insert domains caterpillar.com
[cat-demo] > modules load recon/domains-hosts/netcraft
[cat-demo][netcraft] > run
[cat-demo][netcraft] > show hosts
```

Discuss the bit-rot meta-lesson while it runs.

### Step 3 — Wildcard detection demo

```bash
dig +short DEFINITELY-NOT-A-REAL-XYZQ123.caterpillar.com
# Expect NXDOMAIN — CAT does not wildcard.
# Compare to a known-wildcarding target (instructor will supply
# a screenshot from the mirrors folder).
```

Discuss the difference between NXDOMAIN, NOERROR-with-no-data, and
a wildcard echo. Slide showing what the brute command would look
like on an active-permitted target.

### Step 4 — TXT vendor walk

```bash
dig +short TXT caterpillar.com
```

Read the output line by line. Translate each TXT record into a
vendor relationship live. Discuss how complete this list is
relative to anything CAT publishes.

### Step 5 — Foundation DNS check

```bash
dig +short NS caterpillar.com
```

Note the result. Discuss what it tells you about CAT's DNS
infrastructure choice.

---

## Where the active line falls (one slide)

For each tool covered today, here's what would push it into active
scope:

| Tool | Passive mode (what we did) | Active mode (we didn't do this on CAT) |
|------|----------------------------|-----------------------------------------|
| theHarvester | `-b` with passive sources only | `-c` flag (DNS brute via target's NS) |
| recon-ng | passive `recon/*` modules | discovery and brute modules (DNS brute, port scan) |
| DNS brute | wildcard-detect query (1 query, NXDOMAIN check) | wordlist iteration against target NS |
| dnsx | resolving subfinder output | brute mode (`-w wordlist.txt`) |
| holehe | non-employee email check | individual employee email check (also crosses ethics) |

Memorize this table. It's the difference between a clean engagement
and a complaint to your VP of Security.

---

## Mirror-fallback notes

theHarvester upstream sources rate-limit individually. If you see
zero hits on a normally-productive source, comment it out of your
`-b` list and rerun.

recon-ng modules will sometimes hard-fail mid-run with an HTTP error
or captcha — that's the bit-rot. Move to the next module rather than
debugging.

For comparison data (what subfinder vs. theHarvester surfaced last
night), see `Mirrors/subfinder/caterpillar.txt` and (if captured)
`Mirrors/harvester/caterpillar.json`.

---

## Lab assignments

- 🔵 Hunter: `Student-Labs/Lab-Module-3-Hunter.md`
- 🟠 Ghost: `Student-Labs/Lab-Module-3-Ghost.md`

30 minutes. Module 4 starts at 14:15.

---

## Transition to Module 4

> Now we know what's there.
> Let's profile what's running on it — and connect it to people,
> places, and the supply chain CAT depends on.

Module 4 is where the digital surface meets the physical surface.
Tech fingerprinting, favicon pivots, EPA / OSHA / patent / aviation
data. The differentiator that "corporate recon" courses skip.

Open `Class-Modules/Module-4-Profile-and-Pivot.md`.
