# Google Dorks — Corporate Recon

Search-engine queries for passive corporate reconnaissance. Plug your
target's domain in for `example.com`.

## Subdomain & infrastructure surface

```
site:example.com -site:www.example.com
site:*.example.com -site:www.example.com
inurl:example.com -site:example.com
"example.com" -site:example.com
```

## Document & file exposure

```
site:example.com filetype:pdf
site:example.com filetype:xlsx
site:example.com filetype:docx
site:example.com filetype:pptx
site:example.com filetype:csv
site:example.com filetype:txt
site:example.com filetype:log
site:example.com filetype:bak OR filetype:old OR filetype:swp
site:example.com (filetype:env OR filetype:cfg OR filetype:ini OR filetype:yaml)
```

Document metadata often leaks usernames, software versions, paths, and
internal hostnames. FOCA / exiftool the results.

## Internal-looking paths exposed externally

```
site:example.com inurl:admin
site:example.com inurl:login
site:example.com inurl:wp-admin
site:example.com inurl:phpmyadmin
site:example.com inurl:test OR inurl:staging OR inurl:dev OR inurl:uat
site:example.com inurl:config OR inurl:setup
site:example.com inurl:.git OR inurl:.svn
site:example.com inurl:backup OR inurl:.bak
site:example.com intitle:"index of"
site:example.com intitle:"directory listing"
```

## Error messages that leak info

```
site:example.com "fatal error" OR "warning:" OR "stack trace"
site:example.com "ORA-" OR "MySQL error" OR "PostgreSQL error"
site:example.com "Whitelabel Error Page"
```

## Personnel & contacts (corporate due diligence)

```
site:example.com "CISO" OR "Chief Information Security"
site:linkedin.com/in "Example Inc"
site:linkedin.com/in "@example.com"
site:example.com inurl:about OR inurl:team OR inurl:leadership
"@example.com" -site:example.com
```

## SEC / regulatory trail

```
site:sec.gov "Example Inc"
site:sec.gov "Example Inc" filetype:pdf
"Example Inc" 10-K
"Example Inc" "Exhibit 21"
"Example Inc" 8-K data breach
```

## M&A / corporate structure

```
"Example Inc" "wholly-owned subsidiary"
"acquired by" "Example Inc"
"Example Inc" "merger agreement"
"DBA" "doing business as" "Example Inc"
```

## Public code / paste exposure

```
site:github.com "example.com"
site:github.com "@example.com"
site:gitlab.com "example.com"
site:bitbucket.org "example.com"
site:pastebin.com "example.com"
site:trello.com "example.com"
```

## Cloud bucket exposure

```
site:s3.amazonaws.com "example"
site:storage.googleapis.com "example"
site:blob.core.windows.net "example"
inurl:s3.amazonaws.com "example.com"
```

## Vendor / supplier discovery (TPRM)

```
"Example Inc" "vendor" OR "supplier" OR "partner"
"Example Inc" customer OR "case study"
"Example Inc" "trusted by"
```

## Operator notes

- Different search engines yield different results — also try Bing,
  DuckDuckGo, Yandex, and Searx. Each indexes different parts of the
  web.
- `site:` is approximate — it's based on the index, not authoritative.
- Wayback Machine (`web.archive.org`) is a force multiplier; pages that
  have been removed from the live site often persist there.
- Combine with `before:YYYY-MM-DD` / `after:YYYY-MM-DD` to bound time.
