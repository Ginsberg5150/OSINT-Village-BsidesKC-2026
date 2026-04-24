# CRAAP Test · Five questions per source

**Before you assign an Admiralty letter, ask the source these five
questions. The answers tell you what letter to give.**

Origin: Sarah Blakeslee, Meriam Library, CSU Chico, 2004. Adopted
widely in journalism and academic research. The OSINT use is identical.

---

## The five questions

### **C — Currency**
*When was this published, indexed, or last scanned?*

A 2018 vendor security advisory about Caterpillar's tech stack tells you
about 2018, not today. A `crt.sh` query shows you certificates issued
*ever*, not currently valid. A LinkedIn job description for "Senior
Cloud Engineer at CAT" might be six years old.

**The question to actually ask:** *Is this fresh enough to support the
claim I want to make?*

### **R — Relevance**
*Does this actually answer the question I'm asking, or just an adjacent
one?*

You search for "Caterpillar plant addresses." You find an article about
Caterpillar's Peoria headquarters. The article is real, the company is
real, the city is real — but it doesn't answer your question. It
answers an adjacent one.

**The question to actually ask:** *If I quote this source in support of
my claim, would a reviewer say "that's not what that source says"?*

### **A — Authority**
*Who published this? Are they qualified? Primary, secondary, or
tertiary?*

Primary: the source has direct knowledge (CAT's own SEC filing about
CAT's plants).
Secondary: the source is reporting on what someone else said (Reuters
reporting on CAT's SEC filing).
Tertiary: the source is summarizing other secondary sources (Wikipedia
article citing Reuters citing the SEC filing).

Each step away from primary loses fidelity and adds the possibility of
error. Always seek the primary if you can.

**The question to actually ask:** *Can I get one step closer to the
original source?*

### **A — Accuracy**
*Is this cross-referenceable? Does it cite its sources? Are there
obvious errors?*

A claim that is true and supported by linked primary sources is
defensible. A claim that is true but unsourced is *currently
defensible by accident* — you'll be unable to defend it when challenged.

A source full of obvious errors (misspelled company name, wrong year,
wrong ticker symbol) signals low editorial standards. Even if the
specific claim you care about happens to be correct, the source has
told you it shouldn't be trusted by default.

**The question to actually ask:** *If I had to defend this claim in
front of someone hostile, do I have enough?*

### **P — Purpose**
*Why does this piece of content exist?*

Sincere reporting. Marketing. SEO bait. AI-generated content farm.
Activism. Disinformation. Legal disclosure. Investor relations
spin. Each of these warps content in predictable ways.

A press release exists to make the company look good. A 10-K exists
because the SEC requires disclosure under threat of fraud charges.
Both can be informative; they're informative about *different things*.

**The question to actually ask:** *Whose interests does this content
serve, and how does that affect what it tells me?*

---

## How to use it in practice

You don't run all five questions out loud on every source. You do it
mentally, fast, every time. After a few hours, it becomes automatic.

When in doubt, the **two highest-leverage questions** are Authority and
Purpose. "Who said this, and why does it exist?" answers most of the
hard cases.

---

## Cognitive hazards the CRAAP test helps you avoid

- **AI slop.** Content farms producing plausible-sounding articles that
  cite nothing and synthesize everything. Currency may be high (just
  published). Authority is zero. Accuracy is unverifiable. Purpose is
  ad revenue. → CRAAP catches this.

- **Adversarial honeypots.** Mature targets seed misleading content for
  investigators. Currency: fresh. Relevance: appears high. Authority:
  appears legitimate. Accuracy: subtly wrong in ways that compound.
  Purpose: to mislead. → Hardest to catch; cross-reference to a primary
  source you trust before acting on anything important.

- **Confirmation bias.** You start with a hypothesis. You find sources
  that support it. You forget to look for sources that contradict it.
  → CRAAP doesn't catch this directly; the antidote is to actively seek
  one disconfirming source per finding before the finding goes in the
  dossier.

- **Sunk-cost rabbit holes.** Four hours into a thread is not a reason
  to stay in it. The CRAAP test on the *first* source in a thread
  often tells you the whole thread is a low-value dead end. Set a time
  budget per thread and respect it.

- **Pattern illusions.** Three weak correlations do not make one strong
  finding. If your dossier has a pattern claim, the underlying
  observations should each be `A` or `B` rated individually before
  you assert the pattern.

---

## The takeaway line

> Anyone can collect. An analyst evaluates. CRAAP is the evaluation step.

---

**Cross-references:**
- `Admiralty-Code.md` — the rating you assign after running CRAAP
- `Pre-Flight-Checklist.md` — the OPSEC step before CRAAP
