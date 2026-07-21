# Building a 10-Ad Batch

> Clients don't buy one ad — they buy variants to test. Batching is the actual product.

**Track:** AI Video Ads & UGC
**Time:** ~50 minutes
**Prerequisites:** How AI UGC Actually Works, Character & Face Consistency

## The Problem

A single ad, however good, is a gamble on one hook and one angle. Brands that run paid social know this — they test multiple variants against each other and keep whichever performs. This is why the real service isn't "make me an ad," it's "make me 10 ad variants I can test" — and producing a batch efficiently, rather than one at a time from scratch, is what makes this a viable business rather than a slow craft.

## The Concept

A batch isn't 10 unrelated ads — it's one product, varied along a small number of axes, so you can produce it efficiently while still giving the client meaningfully different things to test:

- **Hook variation** — same product, different opening 2 seconds (question, bold claim, before/after, problem-first)
- **Angle variation** — same product, different selling angle (price, convenience, social proof, novelty)
- **Format variation** — same script, different avatar/voice or b-roll style

Varying all three per ad would make every ad different in every way, making it impossible to know *why* one outperformed another. Vary one or two axes at a time and hold the rest constant — that's what makes the results the client gets back actually useful, not just "another ad."

## Do It

1. **Lock the constants.** Same product, same core proof point, same CTA — these stay fixed across the whole batch.
2. **Write 3-4 hook variants** using the script template from Module 1, each testing a different opening angle.
3. **Pair hooks with 2-3 angle variants** (price-focused, convenience-focused, social-proof-focused) to generate your combination matrix — e.g. 4 hooks × 3 angles doesn't mean 12 ads; pick the most promising 8-10 combinations rather than every permutation.
4. **Reuse your consistent character** (Module 2) across the whole batch unless the brief calls for multiple creator "types."
5. **Batch-produce voice and avatar generation** — since script/character are locked, this step is mostly repetition with different script text, which is where API-based generation earns its keep over one-by-one manual tools.
6. **Deliver with a simple test plan** — label each ad by which axis it varies, so the client (or you) can actually read the results afterward.

## Worked Example

Continuing the GripMount ad (Module 1) with the consistent "creator" from Module 2. Here's a real 5-ad test batch matrix:

| Ad # | Hook | Angle | Constant |
|---|---|---|---|
| 1 | "I did not expect this to hold through a pothole." | Durability/surprise | Same product demo, same CTA |
| 2 | "My old mount fell off literally every drive." | Problem-first (names the pain point) | Same product demo, same CTA |
| 3 | "POV: you're driving and your phone doesn't fall for once." | Relatable/POV format | Same product demo, same CTA |
| 4 | "This $28 thing fixed a problem I didn't know had a fix." | Price/value framing | Same product demo, same CTA |
| 5 | "Two weeks, every pothole, still holding." | Proof-first (leads with the result, not the hook question) | Same product demo, same CTA |

Only the hook and opening angle change — product demo, proof section, and CTA stay identical across all 5, so if one ad wins, you know it's the hook, not some other variable.

**Ad 1 (Module 1) vs. Ad 2 and Ad 3, actually generated** — same anchor character (Module 2), same product, only the opening line changes. This is what "batching" looks like in practice, not just a table of hooks:

<p align="center">
<img src="outputs/examples/gripmount-hook-clip.gif" alt="Ad 1: durability/surprise hook" width="180">
<img src="outputs/examples/gripmount-ad2-problem-first.gif" alt="Ad 2: problem-first hook" width="180">
<img src="outputs/examples/gripmount-ad3-pov.gif" alt="Ad 3: POV format hook" width="180">
</p>
<p align="center"><sub>Ad 1: <a href="outputs/examples/gripmount-hook-clip.mp4">mp4</a> · Ad 2: <a href="outputs/examples/gripmount-ad2-problem-first.mp4">mp4</a> · Ad 3: <a href="outputs/examples/gripmount-ad3-pov.mp4">mp4</a> (with audio; GIFs above are silent previews)</sub></p>

Producing these 3 took re-using the same uploaded anchor image across 3 separate `seedance-2-image-to-video-fast` calls, changing only the prompt's dialogue line each time (~$0.75/clip) — this is exactly what "batch-produce voice and avatar generation" in Do It, step 5 means: the character and product stay fixed, only the script text changes per call.

**How to actually read the test** once these are running as paid social ads: check **hook rate** first (the % of viewers who watch past the first 2-3 seconds) — an ad with a weak hook rate is dead regardless of anything downstream, so don't bother comparing CPA on it yet. Only compare cost-per-result (CPA/ROAS) across ads that already have a decent hook rate; a low CPA on very little spend is noise, not a signal. A common rule of thumb: run each variant long enough to clear a few thousand impressions (roughly 3-4 days at a modest daily budget per variant) before calling a winner — long enough to get past the platform's initial learning phase, short enough not to waste spend on an obvious loser.

**Labeling for the client:** deliver the batch with each ad tagged by which single thing it varies ("Ad 2 = problem-first hook") so whoever's running the media buy can read the result back to a specific creative decision, not just "ad 2 did better."

## Compare Tools

| Path | Throughput for a 10-ad batch | Best for |
|---|---|---|
| **muapi API** | Fast — script the batch as repeated calls varying only script text/params | Client work with deadlines; the default for batch production |
| **Other paid UGC tools (GUI-based)** | Slower — usually one-at-a-time through a UI, even if the UI is polished | Occasional single ads, not batch production |
| **Local/self-hosted** | Can be fast once a batch-generation workflow is set up (e.g. a ComfyUI workflow queue), but the setup investment only pays off at high recurring volume | Agencies producing many batches per month who've already paid the local setup cost in Module 1/2 |

## Launch It

**How to price it:** Price per batch, not per ad — e.g. "$150-$300 for a 5-8 ad test batch," scaling with revisions included. This matches how brands already think about UGC ad budgets and is easier to sell than a per-ad rate card.

**How to position it:** Sell the *testing capability*, not the ad count — "get 8 variants to find your winner" is a stronger pitch than "get 8 ads." Brands running paid social already understand why this matters.

**Where to find first clients:** Same as Module 1 — DTC brands visibly running paid social ads. For batch work specifically, mention in outreach that you can turn around a full test batch faster than sourcing multiple human creators, since speed-to-test is the actual value prop here.

**The real numbers:** Agency-level UGC ad retainers documented in the $1,500-$3,000/month range are typically buying ongoing batch production like this, not one-off ads — this module is what makes that retainer model deliverable.

## Exercises

1. **Easy:** Plan a 6-ad batch matrix (3 hooks × 2 angles) for a product of your choice, without producing it yet.
2. **Medium:** Produce a 5-ad batch end-to-end, holding character and CTA constant while varying hook and angle.
3. **Hard:** Produce a 10-ad batch and write a one-page "test plan" a client could use to track which variant performed best.

## Outputs

Reusable template(s) this module produces — fill these in and reuse them on real work:

- [`outputs/batch-matrix-template.md`](outputs/batch-matrix-template.md) — a fill-in template for planning hook × angle combinations before production.

---

[← Previous: Character & Face Consistency](02-character-consistency.md) · [Track overview](README.md) · Next: [Pricing & Selling UGC Ads →](04-pricing-and-selling-ugc.md)
