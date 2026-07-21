# Character & Face Consistency

> If your AI creator looks like a different person in every shot, nobody will pay for the ad.

**Track:** AI Video Ads & UGC
**Time:** ~40 minutes
**Prerequisites:** How AI UGC Actually Works

## The Problem

This is the single most common complaint from people trying AI-generated content: the same "character" comes out looking like a slightly different person in every generation — different face shape, different age, different outfit continuity. For a one-off image this doesn't matter. For a UGC ad campaign, a faceless channel host, or an AI influencer, it's disqualifying — viewers notice immediately, and clients will reject the work.

Most tutorials skip this because it's the hardest part to explain simply, and it's exactly why this is its own module rather than a footnote.

## The Concept

Consistency comes from giving the model an "anchor" it can't drift away from, instead of re-describing the character in text every time. Three anchor types, from weakest to strongest:

- **Prompt-only consistency** — describing the character in detail every time (hair, face, age, clothing). Weakest — text descriptions are ambiguous and the model fills gaps differently each generation.
- **Reference-image consistency** — feeding a reference photo of the character alongside the prompt, so the model conditions on the actual face, not just a text description. Much stronger, and the easiest to use with API-based models.
- **Fine-tuned/locked identity (LoRA or equivalent)** — training a small adapter on multiple photos of the same character so the model can reproduce that exact identity from any prompt. Strongest and most portable across scenes, but requires more setup (usually a local/self-hosted step, not a single API call).

A fixed **seed** (the random-number starting point for generation) also helps within a single session, but seed-locking alone doesn't survive across different prompts or sessions the way a reference image or trained identity does — treat seed-locking as a helper, not the main mechanism.

## Do It

1. **Pick or generate your anchor character** — either an AI-generated "founder" image or a stand-in reference photo, at high resolution, front-facing, neutral lighting.
2. **Use reference-image conditioning** for every subsequent generation of that character — pass the anchor image alongside each new prompt (different outfit, pose, background) rather than re-describing the person in text.
3. **Check for drift** — generate 3-5 variations and compare: same facial structure, same apparent age, consistent identifying features (freckles, specific hairstyle). If it's drifting, tighten the prompt to describe only what should change (outfit, background) and rely on the reference image for everything about the face.
4. **For heavy repeat use** (a recurring ad character, an influencer, a channel host), consider training a dedicated identity model (LoRA-style) — one-time setup cost, then near-perfect consistency across unlimited future generations.

## Compare Tools

| Path | Consistency strength | Setup effort | Best for |
|---|---|---|---|
| **muapi API, reference-image conditioning** | Good — strong resemblance across generations | Low — pass a reference image param | Most UGC/ad work; fastest path to "good enough" |
| **Other paid tools with built-in "character" features** | Varies — some wrap reference-image conditioning behind a simpler UI | Low | Teams wanting a GUI over the same underlying technique |
| **Local (ComfyUI + trained LoRA)** | Strongest — near-identical identity across any prompt/scene | High — needs a training pass on multiple reference photos, then a workflow to use it | A recurring character used across dozens/hundreds of generations (an influencer, a channel host) where the training cost pays for itself |

Be honest with yourself about how many times you'll reuse this character. Reference-image conditioning via API is the right default for a one-off client ad. A trained local identity is worth the extra setup only once you're generating the same character repeatedly.

## Launch It

**How to price it:** Consistency work isn't billed separately — it's what makes the deliverable usable at all, so it's baked into your ad or content pricing (see Module 4). What you *can* upsell is a **"branded AI character" package** — designing and locking a consistent identity a client can reuse across all future content, priced as a one-time setup fee ($200-$500) plus per-piece production after.

**How to position it:** Frame it as "your reusable AI spokesperson," not "an AI-generated photo." Clients pay more for something they can reuse across campaigns than for a single image.

**Where this shows up:** Every track in this curriculum depends on this module — an AI influencer, a faceless channel's "host," and a UGC ad character are all the same underlying consistency problem applied to a different business model.

## Exercises

1. **Easy:** Generate the same character in 3 different outfits using reference-image conditioning; check for facial drift across them.
2. **Medium:** Generate the same character in 5 different scenes/backgrounds and identify which details drift first (usually: age, specific facial proportions, hairstyle).
3. **Hard:** Set up a local ComfyUI workflow with a trained identity for one character and compare consistency against the API reference-image approach for the same 5 scenes.

## Outputs

- `outputs/character-consistency-checklist.md` — what to check for drift before delivering a batch to a client.
