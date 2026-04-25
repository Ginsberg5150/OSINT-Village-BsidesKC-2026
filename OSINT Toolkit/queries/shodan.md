# Shodan Dorks — Corporate Recon

Curated Shodan search queries for passive external attack surface
mapping. Run these in the Shodan web UI or via the API.

> **Reminder:** these are *passive* — Shodan already scanned, you're
> querying its archive. You are not directly contacting any target.

## Org-scoped baseline

Replace `EXAMPLE` with the target. `org` is the most useful filter once
you know an ASN's parent org name.

```
org:"Example Inc"
hostname:"example.com"
ssl.cert.subject.cn:"example.com"
ssl.cert.subject.cn:".example.com"
hostname:".example.com" -hostname:"www.example.com"
```

## SharePoint (on-prem) discovery

```
product:"Microsoft SharePoint"
http.component:"SharePoint"
http.title:"SharePoint"
"X-SharePointHealthScore"
"MicrosoftSharePointTeamServices"
"SharePoint 2019"
"SharePoint 2016"
"SharePoint 2013"
http.html:"/_layouts/15/"
http.html:"/_layouts/16/"
"Server: Microsoft-IIS" "SharePoint"
```

Combine with country/org filters:

```
product:"Microsoft SharePoint" country:"US" org:"Example Inc"
```

## Exposed industrial / OT (read only — never touch)

```
port:502   "Schneider Electric"      # Modbus
port:102   "Siemens"                 # S7
port:44818 "Rockwell"                # EtherNet/IP
port:1911  "Tridium"                 # Niagara Fox
"Server: NetBiter"
```

## Common admin / management interfaces

```
http.title:"VMware vSphere"
http.title:"Citrix Gateway"
http.title:"FortiGate"
http.title:"PAN-OS"
http.title:"Pulse Connect Secure"
http.title:"GlobalProtect Portal"
http.title:"Cisco ASA"
http.title:"Outlook Web App"
http.title:"OWA" port:443
"Server: Apache Tomcat"  /manager/html
http.title:"phpMyAdmin"
http.title:"Jenkins"
http.title:"GitLab"
http.title:"Confluence"
http.title:"Jira"
```

## Databases and caches exposed to the internet (red flags)

```
port:27017 "MongoDB Server Information"
port:9200 product:"Elastic"
port:6379 "REDIS_VERSION"
port:5432 product:"PostgreSQL"
port:3306 product:"MySQL"
port:11211 "STAT pid"
port:2375  "Docker"
```

## SSL certificate pivots

```
ssl.cert.issuer.cn:"Example CA"
ssl.cert.serial:"1234567890"
ssl.jarm:"<JARM_HASH>"
```

JARM hashes are a particularly good pivot — once you have one for a
target's edge stack, you can find the rest of their fleet behind
otherwise unrelated IPs.

## Favicon pivot (use favicon_pivot.py to generate hash)

```
http.favicon.hash:-1234567890
```

## Cloud-bucket-style exposure

```
http.title:"Index of /"
"S3 Bucket"
http.html:"<ListBucketResult"
```

## Operator notes

- Use the `--limit` flag in API mode to keep credit usage bounded.
- Free Shodan tier doesn't allow most filters — keep a small paid
  account ($5 lifetime sales) for serious work.
- Combine search operators with `country:`, `org:`, `asn:`, and
  `before:` / `after:` for tight filtering.
- Anything you find here is months-old by definition; treat it as a
  lead, not as ground truth.
