# Niche Selection & Script Pipeline

> If your niche has low CPM, your view count doesn't matter; if your script has low retention, YouTube won't show it to anyone.

**Track:** Faceless AI Channels  
**Time:** ~45 minutes  
**Prerequisites:** None  

## The Problem

Most people starting a faceless AI channel pick the same generic niches: "scary campfire stories," "motivational quote compilations," or "gaming funny moments." They choose these because they are easy to generate, but the economics are brutal. These niches suffer from low advertiser demand, resulting in an RPM (Revenue Per Mille) of under $0.50 per 1,000 views. To make $1,000, you need 2 million views. 

Furthermore, they write scripts that read like dry Wikipedia articles, causing viewers to click away in the first 3 seconds. Since platform recommendation algorithms (YouTube, TikTok, Reels) prioritize **Average Percentage Viewed (Retention)**, these low-retention videos are never recommended to new viewers.

To make a faceless channel profitable, you must choose a high-value, advertiser-rich niche and run your scriptwriting through a pipeline engineered to lock in viewer attention.

## The Concept

The economics of a channel are defined by a simple formula:

```
Earnings = (Views / 1000) * RPM + Direct Conversions
```

To maximize this, we focus on:
* **High-CPM Niches:** Industries that sell high-priced products (e.g. business software, SaaS, banking, real estate, luxury travel). Advertisers in these fields bid heavily to show ads, driving your RPM up to $10–$30. At $20 RPM, you only need 50,000 views to make $1,000.
* **The Retention Curve:** Most viewers hit the exit button within the first 5–10 seconds — that's the sharpest drop in how long people keep watching. We fight this by leading the script with a powerful hook (fear or desire), followed by a core problem, a step-by-step solve, and **pattern interrupts** (visual changes or audio SFX) every 3–5 seconds to restart attention.

---

## Do It

### Step 1: Grade Your Niche Options
Use the [`templates/niche-evaluation-matrix.md`](templates/niche-evaluation-matrix.md) to audit three prospective niches. Look up advertiser density by checking the **Meta Ad Library** or **Google Keyword Planner** for the niche's key terms. If advertisers are paying high Cost-Per-Click (CPC) rates to bid on keywords, the niche has a high CPM. Select the niche with the highest score.

### Step 2: Plan Your Video Concept
Map your script out using the [`templates/retention-script-template.md`](templates/retention-script-template.md). Focus on a single target problem (e.g. *"how to automate your business bookkeeping"* rather than a broad *"introduction to accounting"*).

### Step 3: Write the Script in Conversational Format
Draft the script text. Keep it under 180 words for a 60-second video to allow a comfortable speaking pace.
* **0–10s Hook:** State the immediate value or shock factor. Avoid generic greetings (e.g. *"Welcome back to my channel"*).
* **10–25s Problem:** Establish why the standard method is failing.
* **25–45s Solve:** Deliver the step-by-step blueprint.
* **45–50s Pattern Interrupt:** Insert a surprising statistic or change in pacing.
* **55–60s CTA:** Guide them to the link in your description.

### Step 4: System Prompting for Script Generation
If you use a text LLM (like Claude or Gemini) to write scripts, feed it a system prompt that structures the narrative flow:
> *System Prompt:* "You are a professional YouTube Shorts scriptwriter. Write a 60-second script about [Topic]. Keep the tone conversational, informal, and visual. Avoid high-level marketing words. Write short sentences. Every 5 seconds, insert a [Visual transition] instruction. Ensure the total word count is exactly 150-160 words."

### Step 5: Read-Aloud Retention Audit
Read your finished draft script out loud. If you stumble on a sentence, or if it reads too formally, rewrite it. Conversational scripting uses active verbs, contractions (e.g. *"you'll"* instead of *"you will"*), and direct address (*"you"*).

---

## Worked Example

<p align="center">
<img src="templates/examples/faceless-anchor.jpg" alt="Faceless Channel Visual Anchor" width="240">
<img src="templates/examples/faceless-niche-intro.gif" alt="Faceless Niche Video Loop (I2V)" width="240">
</p>
<p align="center"><sub>Faceless Channel Image (Left) ──► Image-to-Video Motion Loop (Right) · Video File: <a href="templates/examples/faceless-niche-intro.mp4">templates/examples/faceless-niche-intro.mp4</a></sub></p>

**Niche Evaluation & Script for "Automate Smarter" (SaaS Automation Niche)**



* **Niche Score:** 22/25 (High CPM, software affiliate programs, high-value demographic).
* **Topic:** Automated Invoice Processing.
* **Word Count:** 158 words.

**Script Excerpt:**

```markdown
[0-5s Hook]
"If you're still manually copying invoices into your accounting software, you are throwing away five hours a week. [Visual: Screen recording of a user typing fast on a spreadsheet, overlay red X]"

[5-15s Problem]
"Most freelancers think they have to pay a virtual assistant to do this. But assistant costs scale up, and copy-paste errors eventually lead to tax discrepancies. [Visual: close-up of calculator showing error screen]"

[15-40s Solve]
"Here is the automated fix. You connect your billing email to Zapier, run it through muapi's document parser, and auto-populate your invoices. Setup takes 10 minutes. [Visual: Clean flowchart animation showing email icon moving to folder]"
```

**Why this script keeps retention high:**
1. **Immediate Hook:** Calls out a specific pain point ("manually copying invoices") and a time penalty ("throwing away five hours a week") in the first sentence.
2. **Visual Pacing:** The visual directions instruct transitions every 5–10 seconds, forcing the editor to change the screen visual to keep the viewer's eyes engaged.
3. **Short Sentences:** Every line is short and easy for a TTS model to read naturally.

**The clip below is real, not a mockup** — the anchor image generated via `nano-banana-2` (9:16 vertical aspect ratio) and animated into a short vertical video clip using `seedance-2-image-to-video-fast` from the script excerpt above, so you can see what a first-pass output actually looks like:



<p align="center"><i>An unedited first pass — the image represents a high-concept visual of the invoice processing error, dynamically animated by the video engine for high-retention engagement.</i></p>

*How this was actually produced, end to end, via the muapi API:*
1. Generated the anchor vertical portrait with **`nano-banana-2`** (text-to-image, $0.06/image) with a `9:16` aspect ratio.
2. Uploaded that image via muapi's `upload_file` endpoint to get a URL.
3. Fed that image URL into **`seedance-2-image-to-video-fast`** (image-to-video, $0.50/clip) on the `images_list` param with a vertical aspect ratio and a prompt describing the camera zoom.
4. Downloaded the resulting `.mp4` and converted it to the silent GIF preview above using `ffmpeg`.

---

## Compare Tools

| LLM / Tool | Scriptwriting Capabilities | Best For |
|---|---|---|
| **Claude 3.5 Sonnet / Gemini 1.5 Pro** | Excellent at formatting scripts, maintaining a natural conversational tone, and keeping strictly to word counts. | Automated script drafting and visual pacing layouts. |
| **Traditional Script Editors** | Standard formatting for television, not optimized for short-form visual hooks. | Long-form linear narratives. |
| **ChatGPT Plus (GPT-4o)** | Creative brainstorming, but tends to write cheesy hooks (e.g. *"Are you tired of..."*) that drop retention. | Initial topic brainstorming. |

Frontier LLMs (Claude/Gemini) are the best pipeline option. By configuring custom system instructions, you can automate script layouts that output both the voiceover text and the video prompt keys in a single run.

---

## Launch It

**How to monetize this step:**
* **Select Your Niche:** Greenlight a high-CPM niche using your graded matrix.
* **Check Advertiser Density:** Before creating the channel, search your niche keywords on the Meta Ad Library. If you see dozens of brands running paid social ads for that keyword, it means they are bidding heavily. Your AdSense RPM will be high.
* **Sourcing Affiliates:** Research SaaS tools in your niche that offer affiliate programs (typically paying **20–30%** recurring monthly commissions). These will be your primary monetization source while you wait to qualify for the YouTube Partner Program.

---

## Exercises

1. **Easy:** Audit three potential niches using the Niche Evaluation Matrix. Select the one with the highest score.
2. **Medium:** Take a dry blog post about a technical topic and adapt it into a high-retention 60-second script using the 5-part script structure. Keep it under 160 words.
3. **Hard:** Write a script outline that incorporates three distinct "pattern interrupts" (e.g. a transition sound effect, a rapid zoom-in, a text card overlay) and explain where you would place them on the timeline to save dropping retention.

---

## Templates

* [`templates/niche-evaluation-matrix.md`](templates/niche-evaluation-matrix.md) — a score sheet to grade potential niches.
* [`templates/retention-script-template.md`](templates/retention-script-template.md) — a structured template to write high-retention scripts.

---

[← Track overview](README.md) · Next: [Duration-Matched Narration & Pacing →](02-narration-and-pacing.md)
