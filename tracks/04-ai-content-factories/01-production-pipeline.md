# The Multi-Step Production Pipeline

> A factory is built on stations, not tasks.

**Track:** AI Content Factories  
**Time:** ~40 minutes  
**Prerequisites:** None  

## The Problem

Most solopreneurs and content agencies handle video creation as an ad-hoc craft. They write a line, open an image generator to test it, write another line, record a voice clip, import it into an editor, and tweak it. This constant context-shifting causes extreme decision fatigue and wastes hours. A single 60-second video can take an entire afternoon to produce. 

If you are selling content production as a service, this speed is a business-killer. If you charge $50 per video and spend 4 hours creating it, you are working for $12.50 an hour. 

To turn a profit, you must run your production like an assembly line: separating the process into discrete, linear **stations** where assets flow unidirectionally from ideation to final scheduling without ever moving backward.

## The Concept

The core principle of a content factory is the **Linear Production Pipeline**:

```
Idea  ──►  Script  ──►  Voiceover  ──►  Visuals  ──►  Assembly  ──►  Polish  ──►  Schedule
```

By organizing your work into stations, you achieve:
* **Unidirectional Flow:** You never write or modify a script *after* voiceover generation is complete. You never generate new visual assets *after* editing is complete.
* **Station Specialization:** Each stage has strict input and output criteria, preventing unfinished work from clogging down-line editors.
* **Standardized Deliverables:** Export files are checked against strict technical parameters (resolution, codecs, audio thresholds) before delivery to avoid revisions.

---

## Do It

### Step 1: Set Up Your Factory Folders
On your hard drive, create a folder template that mirrors the pipeline station structure:
```
[Factory_Batch_01]/
├── 01_scripts/     # Locked script drafts
├── 02_audio/       # Voiceover narrations (.mp3/.wav)
├── 03_assets/      # Visual clips, overlays, and screens
├── 04_edit/        # Timeline project files (CapCut/Premiere)
└── 05_exports/     # Completed masters checked against specs
```

### Step 2: Station 1 & 2 (Script Lock)
Draft the batch scripts. Ensure they meet the strict word count restrictions (under 180 words for short-form) and follow the hook structures. Lock the scripts.

### Step 3: Station 3 & 4 (Audio Spine)
Batch-generate the voiceover audio files. Import them into your project folder. Cut out starting and trailing silences. Log their durations in your narration log template.

### Step 4: Station 5 (Visual Harvest)
Generate or download the background visuals matching the logged audio timeline. Do not open the video editor yet. Keep visuals organized in subfolders by video number.

### Step 5: Station 6 & 7 (Timeline Edit & Polish)
Import all assets. Cut the visual clips to the exact audio milestones. Apply text caption templates and LUT color profiles. 

### Step 6: Station 8 (Specs Check & Export)
Before exporting, run through the [`templates/asset-specs-checklist.md`](templates/asset-specs-checklist.md). Verify that:
* Aspect ratio is correct (`9:16` for vertical, `16:9` for widescreen).
* Peak audio volume sits at **-3dB** to **-1dB**.
* The file name contains the primary target keyword.

---

## Worked Example

**Pipeline Run: "AI in Retail" Explainer (Widescreen)**

* **Station 1 (Idea):** Angle chosen: *"How physical grocery stores use AI cameras to count inventory."* (Time spent: **2 mins**).
* **Station 2 (Script):** Drafted a 140-word narrative structure. (Time spent: **6 mins**).
* **Station 3 (Voice):** Fed script into ElevenLabs using a warm narration voice profile. (Time spent: **3 mins**).
* **Station 4 (Visuals):** Generated 4 widescreen background clips of high-tech grocery stores using `nano-banana-2` and `seedance-2`. (Time spent: **8 mins**).
* **Station 5 (Edit & Polish):** Synced visual cuts to the audio spine, added text captions, applied a cinematic color LUT. (Time spent: **10 mins**).
* **Station 6 (Export check):** Verified audio levels and H.264 export settings. (Time spent: **2 mins**).

**Total Production Time:** **31 minutes** from blank page to finished export.

---

## Compare Tools

| Production Method | Speed | Output Quality | Best for |
|---|---|---|---|
| **Manual CapCut Editing** | Medium (30 mins/video) | High (Highly custom captions, custom transitions) | Professional client deliverables and premium channels. |
| **Programmatic Rendering** (`AI-Youtube-Shorts-Generator`) | Fast (5 mins/video) | Medium (Generic template overlays and stock clips) | Mass-producing faceless channels and placeholder video networks. |
| **Traditional Editors** (Premiere/DaVinci) | Slow (60+ mins/video) | Ultra-High (Unrestricted color grading, advanced audio mixing) | Cinema-grade corporate videos and long-form explainers. |

For agency-scale output, CapCut is the standard tool because of its fast rendering times and auto-caption capabilities. When scaling beyond 3 channels, use programmatic generators like `AI-Youtube-Shorts-Generator` to handle bulk rendering.

---

## Launch It

**How to monetize this system:**
* **Pipeline Audit Service:** Pitch local businesses that are struggling to produce content. Audit their current workflow and design a custom production flowchart for them for **$500–$1,000**.
* **Content Sourcing Outsourcing:** Scale your factory by hiring cheap freelance virtual assistants to manage specific stations (e.g. Station 5: Visual Sourcing, or Station 3: Audio Generation) while you handle Station 2 (Scripting) and Station 6 (Editing).

---

## Exercises

1. **Easy:** Set up a clean factory folder structure on your local drive. Organize a mock set of audio and visual files inside.
2. **Medium:** Document your current content creation workflow step-by-step. Identify the points where you move backwards in the pipeline, and rewrite your process as a strict unidirectional flow.
3. **Hard:** Complete a full 60-second video build using a stopwatch. Track the exact time spent at each of the 6 stations. Highlight the slowest station and write a plan to optimize it.

---

## Templates

* [`templates/pipeline-flowchart-template.md`](templates/pipeline-flowchart-template.md) — a layout diagram and audit sheet for pipeline stations.
* [`templates/asset-specs-checklist.md`](templates/asset-specs-checklist.md) — export checklist for resolution, codecs, and safe zones.

---

[← Track overview](README.md) · Next: [Building a TikTok/Reels Factory →](02-tiktok-reels-factory.md)
