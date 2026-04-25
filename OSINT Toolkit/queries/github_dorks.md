# GitHub Dorks — Secret & Code Exposure

GitHub's own search supports passive secret hunting against a target.
Plug your target's domain or org name in for `example.com`.

> **Important:** finding a leaked credential does NOT authorize you to
> use it. Report it to the org's security contact. Never attempt to
> validate live credentials.

## Domain-scoped sweeps

```
"example.com" password
"example.com" api_key
"example.com" apikey
"example.com" secret
"example.com" token
"example.com" credentials
"example.com" private_key
"example.com" BEGIN RSA PRIVATE KEY
```

## Common secret patterns

```
filename:.env "example.com"
filename:.npmrc _auth
filename:.dockercfg auth
filename:wp-config.php "example.com"
filename:configuration.php "example.com"
filename:credentials.xml
filename:database.yml "example.com"
filename:.git-credentials
filename:.htpasswd
filename:id_rsa
filename:id_dsa
```

## Cloud provider keys (no domain needed — but filter by org)

```
"AKIA" extension:env                         # AWS access key prefix
"aws_access_key_id" "aws_secret_access_key"
"AIza"  extension:js                         # Google API key prefix
"ghp_"  extension:env                        # GitHub PAT prefix
"sk-"   extension:env                        # OpenAI key prefix
"xoxb-" extension:js                         # Slack bot token
"xoxp-"                                      # Slack user token
```

## CI / pipeline secrets

```
filename:.gitlab-ci.yml "example.com"
filename:bitbucket-pipelines.yml "example.com"
filename:.github/workflows "example.com" SECRET
filename:Jenkinsfile "example.com"
```

## SSH / certificate exposure

```
"BEGIN OPENSSH PRIVATE KEY"
"BEGIN RSA PRIVATE KEY"
"BEGIN DSA PRIVATE KEY"
"BEGIN EC PRIVATE KEY"
"BEGIN PGP PRIVATE KEY"
filename:id_rsa "example.com"
```

## Database connection strings

```
"jdbc:mysql://"   "example.com"
"jdbc:postgresql://" "example.com"
"mongodb+srv://"  "example.com"
"DATABASE_URL"    "example.com"
```

## Internal docs / runbooks

```
"example.com" "internal use only"
"example.com" "do not distribute"
"example.com" "confidential"
"example.com" "runbook"
```

## Org-scoped discovery (find their public repos)

```
user:example-inc                # if they use this GitHub org
"@example.com" in:email         # commits authored from corp email
```

Cross-reference commit emails — engineers often push from corp emails
even on personal projects.

## Beyond GitHub search

The web UI's search has limits. For deeper sweeps use:

- **grep.app** — code search across many public repos, faster than GitHub
- **trufflehog** — clone target repos and run regex/entropy detection
- **gitleaks** — same, with config-driven rule sets
- **shhgit** — historical commits scanner
- **GitGuardian Public Search** — managed scanning (free tier)
- **Sourcegraph Cloud** — indexes public repos with strong filters

## Operator notes

- GitHub's search API is rate-limited — authenticated lookups raise the
  ceiling. Don't burn your account on bulk scans.
- A leaked secret in a *deleted* commit is still recoverable via the
  commit SHA if anyone has it. Old commits live forever.
- Always rotate before reporting if it's your own org.
- For external orgs, file a coordinated disclosure — never try the key.
