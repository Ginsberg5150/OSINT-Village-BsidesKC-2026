# Pre-Flight Checklist · Protect the investigator first

**Run this before every recon engagement. Today and forever.**

This is the line between a professional and a hobbyist. About 90 seconds.
Non-negotiable.

---

## The seven boxes

- [ ] **VPN active** — verified exit IP that is *not* your home ISP
- [ ] **Dedicated browser profile** open — *not* your personal browser
- [ ] **Personal accounts signed out** — Google, LinkedIn, GitHub, all of them
- [ ] **LinkedIn → Private Mode** before you view any profile
- [ ] **Sock puppet ready** *(only if today's work uses a logged-in source — see `Sock-Puppets.md`)*
- [ ] **Notes open** with the target name + the first timestamp
- [ ] **Sober, calm, focused** — if you're not, walk away and come back

---

## Why each box matters

**1. VPN active.**
Every query you run leaves a trail back to the source IP. Your home ISP's
IP is permanently associated with you (billing records, account history,
device fingerprint). A target's logs, the upstream service's logs, and
any intermediate CDN see something. That something should not be your
home identity.

What to verify: open `https://ifconfig.me/` or `https://ipleak.net/` in
the browser you're about to use. The IP returned should match your VPN's
exit, not your ISP. If it shows your ISP, your VPN isn't actually routing
you.

**2. Dedicated browser profile.**
Every browser keeps a fingerprint: installed extensions, screen resolution,
timezone, language, fonts, autofill data, login state. A personal profile
contaminates your recon work with personal-identity tells. Use a separate
profile (Firefox supports profiles directly; Chrome via "Add profile"; or
use Firefox Multi-Account Containers for finer separation).

What to verify: in the browser, you should see no personal bookmarks,
no autofill on common forms, no logged-in accounts in the corner of any
major site you visit.

**3. Personal accounts signed out.**
A logged-in Google account watching you load `caterpillar.com/careers`
builds a profile of you whether you want it to or not. Same for LinkedIn,
GitHub, Twitter/X, and every other site that drops a session cookie when
you're authenticated. The fix is to be authenticated to *nothing* in the
recon profile.

What to verify: visit `accounts.google.com`, `linkedin.com`, `github.com`
in the recon profile. Each should show a sign-in screen, not your account.

**4. LinkedIn → Private Mode.**
LinkedIn's "Who viewed your profile" feature is a counter-intelligence
feed. By default, when you view a target's profile, they see your name,
title, and company. Switching to Private Mode hides this — they see
"LinkedIn Member" instead. Settings → Visibility → Profile viewing options
→ Private mode.

Caveat: Private Mode disables your own "Who viewed me" data in return.
That's a fair trade for any kind of professional recon work.

**5. Sock puppet ready.**
Some sources require a logged-in account to view (Sales Navigator, certain
Facebook Graph queries, some Discord/Telegram channels). Logging in with
your real account during target recon is a hard burn. A sock puppet —
a separate persona with its own email, phone, and history — keeps your
real identity clean.

You don't always need one. For today's Caterpillar work, you can do
everything passive without a sock puppet. See `Sock-Puppets.md` for when
to invest in building one.

**6. Notes open with target name + timestamp.**
The dossier you produce today is only as good as the timestamps on its
sources. "I found X on the Caterpillar 10-K" is a weaker claim than "I
found X in Caterpillar's 2025 10-K, retrieved 2026-04-25 at 11:42 UTC,
URL pasted." Open your notes file before your first query and write the
first timestamp.

**7. Sober, calm, focused.**
Recon errors compound. A missed timestamp at 10:30 becomes an unprovable
claim at 15:00 becomes a removed line in your dossier at 15:30. Tired,
distracted, frustrated, hung-over, angry — any of these is a reason to
pause, not push through. The work will still be there in an hour.

---

## During the day — re-check at every break

Every time you come back from a break (water, bathroom, lunch, hallway
chat), spend 15 seconds checking that the seven boxes are still green.
VPNs drop. Browser profiles get accidentally swapped. Tabs get opened in
the wrong window. The discipline is the *re-check*, not the initial
check.

---

## Why this exists

The targets you investigate also investigate the people investigating
them. Mature organizations seed monitoring on their own surface. Threat
actors do the same — but in their case the monitoring is sometimes
adversarial honeypots designed to surface and identify investigators.

You are also a person, in a chair, with a real identity. The pre-flight
checklist is your professional-grade contribution to the boring,
unglamorous, infinitely-important work of *not getting hurt by your own
research*.

---

**Cross-references:**
- `Sock-Puppets.md` — when you need one and what makes one work
- `00-Students-Start-Here.md` — Section 2 has the same checklist in
  shorter form for at-the-door reading
