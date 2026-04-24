# Sock Puppets · The persona that isn't you

**A sock puppet is an account you own that isn't tied to your real
identity. Separate email, separate phone, separate photo, separate
payment method, separate history.**

You don't need one for today's Caterpillar work. Everything in the
class can be done from your real, signed-out, VPN-protected browser.
This reference exists because in your career you *will* need one,
and building one badly is worse than not having one at all.

---

## Why they work

Compartmentalization. If a target investigates who's looking at them,
they see the persona, not you. Your real identity stays clean. If the
persona is burned (locked out, banned, exposed), you retire it; you
don't retire yourself.

This is a defensive tool. It exists to protect investigators from
predictable retaliation, doxing, and counter-investigation by
sophisticated targets.

---

## When you actually need one

A sock puppet is appropriate when:

- The source you need to query **requires a logged-in account** and
  using your real account would create a permanent association
  between you and the target (LinkedIn Sales Navigator, certain
  Facebook Graph queries, gated Discord/Telegram channels, paid
  research platforms with public profiles).

- The target is **plausibly monitoring** for adversary recon and
  would actively investigate signed-in viewers (high-value commercial
  targets, defense contractors, political organizations,
  cyber-aware adversaries).

- You may need to **interact with adjacent accounts** to gather
  information (joining a community, asking a clarifying question in
  a group chat, observing posting patterns in a thread).

A sock puppet is **not** appropriate when:

- You can do the work with no login at all (most CT logs, public
  EDGAR, public WHOIS, public regulator databases).

- The plan is to **engage with the target directly** (DMs, comments,
  emails). That's not investigation; that's catfishing or social
  engineering, which has a different ethical and legal regime.

- You want to **bypass a platform's terms of service** for paid
  features. Sock puppets for evading paywalls is a separate problem
  with its own consequences.

---

## What makes one work

A working sock puppet has all of the following:

| Element | What it means |
|---------|---------------|
| **Backstory** | A consistent written biography you can recall under pressure. Where the persona grew up, went to school, currently works, what they're interested in. Write it down. Reread it before any interaction. |
| **Aged account** | New accounts are flagged as suspicious by every major platform. Sock puppets need to *exist* for months before they're useful. Build them long before you need them. |
| **Realistic photo** | A face that doesn't reverse-image-search to a stock-photo site, an existing person, or another sock puppet. Generated faces (e.g., from `thispersondoesnotexist.com`) work but check — these can be detected. Some operators commission custom AI portraits with specific traits. |
| **Separate email** | Not a Gmail forwarder of your real address. A genuinely separate provider, ideally one that doesn't require phone verification. ProtonMail, Tutanota, or self-hosted with a clean domain. |
| **Separate phone** | A real, working number that is not yours. MySudo, Hushed, Burner, or a physical pre-paid SIM in a separate device. Critical for any account requiring SMS verification. |
| **Separate payment** | Privacy.com virtual cards, prepaid Visa/Mastercard, or crypto where the platform allows. Never use a card with your real name. |
| **Network separation** | A different VPN exit, ideally a residential-IP service for any account that fingerprints datacenter IPs. Never log in from your home network or your work network. |
| **Device separation** | A separate browser profile at minimum; a separate browser entirely is better; a separate device is best. The persona's session must not contaminate your real identity's fingerprint. |
| **Behavior** | Realistic posting cadence, realistic typos, realistic interests outside the target's domain. A sock puppet that only ever logs in to view targets is itself a tell. |

---

## What breaks them

Common failure modes, in approximate order of frequency:

1. **Reused photos.** Reverse image search of the persona's profile pic
   returns ten other accounts with the same image, all flagged.
2. **Geographic tells.** Persona claims to live in Brooklyn but logs in
   from a German VPN exit and posts at 3am EST. Timezone mismatch is
   investigated by every fraud-detection system.
3. **Phone area code.** Persona claims Texas but the SMS verification
   number has a 415 area code.
4. **Personal device contamination.** You logged in once on your real
   phone "just to check." Cookies, IP, fingerprint, and biometric data
   now associate persona to you forever.
5. **Emotional reaction.** Target pokes the persona ("interesting that
   you only ever look at X"). You react. The reaction is the breach,
   not the original observation.
6. **Cross-contamination.** Same email recovery address across two
   sock puppets, same phone, same payment card. One persona burns;
   they all burn.
7. **Activity pattern.** Persona only ever logs in for 90 seconds at a
   time, only ever views targets, never posts, never reacts. A
   sufficiently bored fraud analyst notices.

---

## The ethical line

Sock puppets are a defensive and investigative tool. They exist to
protect investigators from retaliation by powerful targets — including
hostile state actors, organized crime, doxing networks, and stalking
ex-partners with resources.

Using sock puppets to:
- Engage actual victims of targets you're investigating
- Impersonate real people (real name, real photo, real claimed
  affiliation)
- Catfish individuals into emotional or romantic interaction
- Defraud platforms or merchants

…is **out of scope**, **legally risky in most jurisdictions**, and
**not what this reference is teaching**. If your work is heading in
that direction, stop and consult counsel.

---

## For today's class

For Caterpillar work today, you do not need a sock puppet. Every
source in the modules is either fully public or accessible signed-out.

If you find yourself wanting to use a logged-in source mid-lab, the
correct move is to **note it as a "with-puppet follow-up" item in
your dossier** and continue with what you can do passive. Real
investigations operate this way: you do everything you can without
crossing a line, then plan the riskier moves separately, deliberately.

---

**Cross-references:**
- `Pre-Flight-Checklist.md` — Box 5 ("Sock puppet ready") points here
- `00-Students-Start-Here.md` — Section 2 mentions sock puppets briefly
- For deeper practice: Michael Bazzell, *Open Source Intelligence
  Techniques* (current ed.) has a multi-chapter treatment of persona
  construction
