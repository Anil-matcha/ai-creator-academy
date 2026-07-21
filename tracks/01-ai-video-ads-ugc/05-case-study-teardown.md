# Case Study Teardown

> Learn to reverse-engineer a winning ad instead of guessing what worked.

**Track:** AI Video Ads & UGC
**Time:** ~30 minutes
**Prerequisites:** How AI UGC Actually Works, Pricing & Selling UGC Ads

## The Problem

It's easy to produce ads. It's harder to know which elements of a successful ad actually drove its performance, versus which were incidental. Without a teardown method, you end up copying surface style (a trending sound, a specific creator look) without understanding the structural reasons an ad worked — which means you can't reliably reproduce success for a different product.

## The Concept

A teardown separates an ad into the same five layers from Module 1 — script, avatar/voice, video, captions, export — and asks, for each layer, "what choice was made here, and why might it matter?" This turns "that ad performed well" into a checklist of reusable decisions, rather than a vibe.

Documented, large-scale AI-UGC ad campaigns are useful teardown subjects precisely because their spend level implies the brand tested and kept what worked — the surviving ad reflects real performance data, not a guess.

## Do It

1. **Pick a real, currently-running ad** in your target product category (visible via a platform's public ad library) that's been running for a while — longevity is a signal it's performing, since brands cut losing ads quickly.
2. **Transcribe the script** and map it to the hook/pitch/proof/CTA structure from Module 1 — note what makes the hook work specifically (what question/claim/visual, and why it stops a scroll).
3. **Note the avatar/voice choice** — tone, apparent age/demographic match to the product's audience, energy level.
4. **Note the video structure** — how much is talking-head vs. b-roll, and where cuts happen relative to the script beats.
5. **Note captioning style** — timing, emphasis (bold/highlighted keywords), whether it's synced tightly to speech.
6. **Write down 2-3 structural takeaways** you could apply to a different product — not "copy this ad," but "this kind of hook works for this kind of problem."

## Worked Example

Say you're prospecting a skincare-serum brand and want a teardown to open the conversation. You pull up **Meta Ads Library** (free, no login needed) and search the brand's page.

**Step 1 — longevity signal:** One ad shows "started running 47 days ago" with 6 near-identical variants (same script, different creator). Running that long, with that many variants of itself, is the tell that the brand found a winning script and is now testing creators/hooks against it — not guessing.

**Step 2 — script mapped to structure:**
| Layer | What's actually in the ad |
|---|---|
| Hook (0-2s) | "I stopped using retinol after this happened to my skin." — a scare/curiosity hook, not a claim about the product yet |
| Pitch (2-12s) | Names a specific complaint (retinol irritation) before introducing the product as the alternative |
| Proof (12-22s) | Before/after skin close-up, timestamped "day 1 / day 14" |
| CTA (22-25s) | "Link in bio, 20% off first order" — discount-anchored, not just "shop now" |

**Step 3 — why it likely works:** the hook never mentions the product — it's a relatable complaint first, which is why it probably clears a decent hook-rate (viewers watch past 3 seconds to find out what happened) before the pitch even starts. The before/after proof with a day-count is a concrete, checkable claim, not "amazing results."

**Step 4 — the takeaway you'd reuse**, written generically (not naming the brand): *"A pain-first hook that withholds the product name for the first few seconds, paired with a dated before/after, works well for skincare-category ads — the curiosity gap is what earns the watch-through."*

**Using it in outreach:** "I noticed a running ad in the skincare-serum category using a pain-first hook + dated before/after proof — that structure is why it's still running after 47 days. Here's a sample ad using the same structure for [prospect's product]." This is a stronger opener than "I make AI ads" because it demonstrates you understood *why* something works before pitching anything.

## Compare Tools

Teardown is mostly a manual skill (Do It above), but a video-understanding model can do a first-pass breakdown for you — worth knowing about even though the manual version is what actually builds your judgment.

**Real test:** ran Module 1's GripMount clip through **`gemini-video-vision`** (muapi, $0.004/call — a video-in, text-out model) with the prompt "break this into hook/pitch/proof/CTA, and comment on lip-sync quality and video structure." Actual output:

> **Hook:** "...her immediate, palpable surprise and excitement are very engaging... 'Okay, I did not expect this...' creates immediate curiosity."
> **CTA: Missing.** "There is no explicit or implied call to action in this short clip. It ends abruptly... A full ad would typically follow up with 'Shop now'..."
> **Lip-sync:** "Excellent... flawless and perfectly aligned with the audio."
> **Structure:** "Talking-head. ...there is no b-roll footage."

That's a genuinely correct read — the clip really is just the hook with no CTA, and it caught that.

**Manual vs. AI-assisted, honestly:**

| | Manual teardown (Do It above) | AI-assisted (`gemini-video-vision`) |
|---|---|---|
| What it's good for | Building your own judgment — you have to notice *why* a hook works, not just that it exists | A fast first pass, or a check against your own read when you're not sure |
| Speed | Slower — you're watching and thinking | Seconds, and $0.004/call |
| Where it can mislead | Doesn't apply — it's your own read | Can miss context a human would catch (brand history, category norms, why *this* audience specifically) — treat it as a draft, not a verdict |

Use it as a learning aid (compare its read to your own to check your instincts) or as a time-saver when you're doing a batch of teardowns and can't manually watch every candidate ad — not as a replacement for actually doing the manual version enough times to build the skill yourself.

## Launch It

**How to use this in sales:** A short teardown of a real running ad in a prospect's category — "here's why this ad from [category, not naming competitors by name] is working, and here's how I'd apply the same structure to your product" — is a stronger pitch opener than a generic capabilities pitch, because it demonstrates judgment, not just production ability.

**How to position it:** Offer a "structural analysis + sample ad" as a low-cost or free first deliverable for prospects who are on the fence — it's fast to produce once you've practiced this skill, and it sells your judgment, not just your tool access.

**A note on naming:** When doing teardowns for client-facing material, describe competitor ads by category and structure ("a running ad in the skincare-serum category uses a before/after hook"), not by naming the specific brand or ad — this keeps the analysis about the technique, not competitive intelligence gathering.

## Exercises

1. **Easy:** Tear down one running ad in a product category you're interested in, using the five-layer structure.
2. **Medium:** Tear down 3 ads in the same category and identify what's common across all three (a shared structural pattern) versus what's unique to each.
3. **Hard:** Apply a teardown's structural takeaway to produce a new ad for a different product, and write down which specific choice you borrowed and why.

## Templates

Reusable template(s) this module produces — fill these in and reuse them on real work:

- [`templates/teardown-worksheet.md`](templates/teardown-worksheet.md) — the five-layer teardown structure as a fill-in worksheet.

---

[← Previous: Pricing & Selling UGC Ads](04-pricing-and-selling-ugc.md) · [Track overview](README.md) · You've completed Track 1 — see [ROADMAP.md](../../ROADMAP.md) for what's next.
