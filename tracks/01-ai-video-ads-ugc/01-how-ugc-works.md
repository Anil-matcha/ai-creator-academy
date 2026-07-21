# How AI UGC Actually Works

> A UGC ad is just five pieces stitched together — once you can see the seams, you can make any of them.

**Track:** AI Video Ads & UGC
**Time:** ~45 minutes
**Prerequisites:** None

## The Problem

Brands pay real creators $200-$1,500 per UGC (user-generated-content-style) ad because it converts better than polished studio ads — it looks like a real person talking to camera about a product, not a commercial. The problem: sourcing, briefing, filming, and revising human creators is slow, and it doesn't scale. A brand that wants 20 ad variants to test can't get 20 creators on short notice.

AI-generated UGC solves the scaling problem, but most people trying it get stuck on one thing: their AI "creator" doesn't look consistent from shot to shot, or the voice/lip-sync looks obviously fake, and the ad gets rejected. Understanding the actual pipeline — not just "type a prompt" — is what separates a usable ad from an uncanny one.

## The Concept

A UGC-style AI ad is five stages, each producible independently and swappable:

```
Script  →  Avatar / Voice  →  Video  →  Captions  →  Export
```

- **Script** — a short, conversational hook + pitch + call-to-action, written the way a real person talks, not ad copy.
- **Avatar/Voice** — either a generated talking-head avatar with a cloned/synthetic voice, or a still reference image animated with lip-sync driven by an audio track.
- **Video** — the avatar's performance, plus any b-roll (product shots, screen recordings) cut around it.
- **Captions** — auto-generated, burned-in captions, standard for the format because most viewers watch muted.
- **Export** — format/aspect ratio matched to the platform (9:16 for Reels/TikTok/Shorts, sometimes 1:1 or 16:9).

The reason this pipeline matters more than any single "best model" is that each stage can be produced by a different tool, and the weak link is whichever stage looks least real — usually the avatar's face/voice sync, not the script or captions.

## Do It

1. **Write the script.** Keep it under 30 seconds spoken (~75-90 words). Structure: hook (first 2 seconds — a question, a bold claim, or a visual surprise), problem/pitch (10-15 seconds), proof or demo (10-15 seconds), call-to-action (last 2-3 seconds).
2. **Generate the voice.** Use a text-to-speech or voice-cloning model to turn the script into natural-sounding narration. Match tone to the product (energetic for a gadget, calm for skincare).
3. **Generate or animate the avatar.** Either generate a talking-head video directly from the script/voice, or animate a reference image with lip-sync driven by the audio track.
4. **Add b-roll.** Cut in product shots or screen recordings during the pitch/proof section — this also hides any short imperfect stretches in the avatar footage.
5. **Caption and export.** Auto-generate captions, burn them in, and export at 9:16 for short-form platforms.

## Worked Example

Product: a $28 magnetic phone car mount ("GripMount").

**Script** (hook/pitch/proof/CTA, ~28 seconds spoken):

> "Okay, I did not expect this to actually hold my phone through a pothole. [holds up phone, taps mount] I used to have one of those suction ones that fell off literally every drive — this one's magnetic, snaps on in like two seconds. [demo: slaps phone onto mount] It's held through every drive for the last two weeks, potholes included. It's $28, link's below — honestly just get it before your next road trip."

Mapped to the structure:
- **Hook (0-2s):** "Okay, I did not expect this to actually hold my phone through a pothole." — a surprised, specific claim, not generic ("this product is great").
- **Problem/Pitch (2-15s):** names the actual competing product's failure (suction mount falling off) — this is what makes it sound like a real person, not ad copy.
- **Proof/Demo (15-25s):** a visual demo (slapping the phone on) plus a concrete duration ("two weeks, potholes included") — specific numbers read as more credible than "it works great."
- **CTA (25-28s):** price stated plainly, one action ("link's below"), urgency tied to a real use case (road trip) instead of a generic "buy now."

**Why this script would survive production:** it's short enough to keep energy up on one take, the demo moment (slapping the phone on) gives the avatar something to *do* with its hands instead of just talking — which also hides minor avatar imperfections — and it never says "AI" or sounds scripted.

**Common first-attempt mistake:** writing the pitch section like copy ("Introducing GripMount, the revolutionary new way to...") instead of like speech. Read your script out loud before producing anything — if you wouldn't say it to a friend, rewrite it.

**The clip below is real, not a mockup** — the anchor image from Module 2 animated into a short talking clip from the hook line above, so you can see what a first-pass output actually looks like before any editing/b-roll/captions are added:

<p align="center"><img src="outputs/examples/gripmount-hook-clip.gif" alt="Generated talking clip (silent GIF preview)" width="280"></p>

<p align="center"><a href="outputs/examples/gripmount-hook-clip.mp4">▶ Watch the original with audio (.mp4)</a> — GitHub can't play video inline in a README, so the GIF above is a silent preview; the linked file has the actual voice.</p>

<p align="center"><i>An unedited first pass — lip movement is decent but not perfect, which is normal at this stage. Cutting in b-roll during the pitch/proof section (Do It, step 4) is what usually hides this kind of imperfection in a finished ad.</i></p>

*How this was actually produced, end to end, via the muapi API:*
1. Generated the anchor portrait with **`nano-banana-2`** (text-to-image, $0.06/image) — the same image used in Module 2's example.
2. Uploaded that image via muapi's `upload_file` endpoint to get a URL the next model could reference.
3. Fed that image URL into **`seedance-2-image-to-video-fast`** (image-to-video, $0.75/clip) with a prompt describing the action and the exact line of dialogue — no separate TTS/lip-sync pass was needed, since this model generates speech and mouth movement together from the prompt.
4. Downloaded the resulting `.mp4` from muapi's CDN (generated outputs expire after 30 days, so anything you want to keep needs downloading promptly) and converted it to the silent GIF preview above with `ffmpeg` for inline display.

Total cost for this one clip: **$0.81** across the two model calls. This is exactly the "image → video model, prompt-driven" pipeline described in Do It, step 3 — the models named here are current examples, not a fixed recommendation; see Compare Tools below for how to pick a model when these become outdated.

## Compare Tools

Model names change constantly, but the *category* choice matters more than any specific model — here's what's actually reasonable for each stage right now:

| Stage | Good muapi models to reach for | Why |
|---|---|---|
| Voice/TTS | Gemini TTS, ElevenLabs text-to-dialogue | Natural multi-speaker delivery with emotion/pace control — not robotic TTS |
| Avatar/video (image → talking clip) | Seedance 2.x, Kling 3.0 | Current-generation video models that handle head/hand motion and speech convincingly in one pass, as in the clip above |
| Lip-sync (audio-driven, onto an existing video/image) | A dedicated lip-sync model (e.g. sync-style lip-sync) or a Kling avatar model | Better fit when you already have separately-recorded narration you need to match to a face, rather than generating speech+motion together |

| Path | Cost per ad | Setup effort | Consistency | Best for |
|---|---|---|---|---|
| **muapi API** (managed) | Per-generation credit cost, no infra | Low — call the endpoint, get a result | High — same model/voice reused via API params | Fast iteration, client work, testing many variants |
| **Other paid all-in-one UGC tools** | Often subscription-gated, per-seat pricing | Low, but locked to their UI/workflow | Varies by tool | Teams that want a GUI, not an API |
| **Local/self-hosted** (ComfyUI + local TTS/video models, e.g. LTX 2.3) | Free after hardware, but needs a capable GPU | High — workflow setup, model downloads, tuning | Can be very high once tuned, but slower to get there | Zero marginal cost at volume, full control, privacy-sensitive clients who don't want cloud processing |

LTX 2.3 is worth naming specifically for the local path: it's an open-weight video model runnable in ComfyUI, so it's the closest local equivalent to the Seedance/Kling-class models above — weaker out of the box, but the only one of this group you can actually run on your own GPU instead of an API call.

The honest tradeoff: local is genuinely free per-generation once set up, but the setup and iteration time cost is real — expect to spend a weekend tuning a ComfyUI workflow before it's reliable. API is the right default while you're still learning what "good" looks like; local becomes worth it once you're producing at real volume (dozens of ads/month) or a client specifically needs on-premise generation.

## Launch It

**How to price it:** Individual UGC-style ad gigs on freelance marketplaces run roughly $10-$55 per finished ad; agencies retainer this work at $1,500-$3,000/month for ongoing batches. Price by deliverable (e.g., "$150 for 5 ad variants") rather than by hour — clients understand ad packages, not your production time.

**How to position it:** Lead with the business outcome ("more ad variants to test, faster, without a film crew"), not the AI process. Brands buying UGC ads care about conversion and testing speed, not how the video was made.

**Where to find first clients:** DTC e-commerce brands running paid social ads are the best fit — they already buy UGC and already understand the format. Cold outreach to brands you can see running Meta/TikTok ads (visible in the platforms' public ad libraries) with a sample ad for their actual product is a stronger opener than a generic pitch.

**The real numbers:** Documented case studies show individual brands running AI-UGC-style creative at $600K+/month in ad spend for a single product — the point isn't that you'll match that, it's that the format is proven at scale, not a novelty.

## Exercises

1. **Easy:** Write three 30-second UGC scripts for a product you use, following the hook/pitch/proof/CTA structure.
2. **Medium:** Produce one full ad end-to-end (script → voice → avatar → captions → export) for a real or hypothetical product.
3. **Hard:** Produce 5 variants of the same ad (same product, different hooks or angles) and compare which hook you'd expect to perform best, and why.

## Outputs

Reusable template(s) this module produces — fill these in and reuse them on real work:

- [`outputs/ugc-script-template.md`](outputs/ugc-script-template.md) — the hook/pitch/proof/CTA script structure as a fill-in-the-blank template.
- [`outputs/ad-brief-checklist.md`](outputs/ad-brief-checklist.md) — a checklist for briefing yourself (or a client) before producing a batch.

---

[← Track overview](README.md) · Next: [Character & Face Consistency →](02-character-consistency.md)
