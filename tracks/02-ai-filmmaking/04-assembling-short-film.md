# Assembling a Short Film

> The film isn't made in the generator; it's made in the editor.

**Track:** AI Filmmaking  
**Time:** ~50 minutes  
**Prerequisites:** Screenplay & Story Generation, Storyboarding & Shot Planning, Camera Movement & Cinematography Prompts  

## The Problem

If you take raw, silent clips directly from a video generator and play them back-to-back, the result is jarring. One clip might have a slight green tint, the next is warm yellow. The camera motion speeds don't match. And most of all, the complete silence makes the video feel dead, revealing the artificial nature of the footage immediately.

Most tutorials focus purely on the generation phase, leaving you with a folder of silent, disconnected files. 

An AI film only becomes a real movie when it enters the editor. You must stitch the clips together, establish narrative pacing, match the color palette across different generation runs, and build a rich, multi-layered audio track.

## The Concept

Post-production assembly bridges the gap between silent AI clips and a finished cinematic piece. This workflow consists of two main pillars: **Audio Layering** and **Color Grading**.

### The Sound Design Hierarchy:
Because AI video clips are generated silent, you must build the audio track from scratch. We layer audio in a precise hierarchy:
1. **Dialogue / Narration:** The vocal performance (voiceover or synced speech).
2. **Ambience / Room Tone:** Continuous background noise that sets the space (e.g., spaceship engine hum, rain).
3. **Foley / Sound Effects (SFX):** Discrete sounds synchronized with visual events (e.g., switches clicking, heavy footsteps).
4. **Music / Soundtrack:** The emotional underscore of the scene.

```
Silent Visual Cuts  →  Narration  →  Ambience Track  →  Foley Sync  →  Music Score
```

### Visual Unification:
To fix slight shifts in color grading between different generations, you apply a **LUT (Look-Up Table)** to the entire editing timeline. This overlays a uniform color grade across all clips, blending them into a single visual style.

---

## Do It

### Step 1: Organize Your Project Timeline
Import your generated clips into an NLE editing program (e.g., DaVinci Resolve, Premiere Pro, or CapCut). Lay them out in order on your main video track (V1). Trim any visual glitches that occur at the very beginning or end of a clip (video models often dissolve or warp in the final half-second).

### Step 2: Generate the Voiceover Narration
Use a high-quality TTS or voice-cloning API (like ElevenLabs).
* Paste your script from Module 1.
* Add artificial line breaks or punctuation (commas, ellipses) to force the voice model to pause naturally.
* Import the audio file into the editor on audio track A1. Sync the start of dialogue lines with your character's visual entrance.

### Step 3: Layer the Ambient Soundscape
Find or generate a continuous background noise track matching your film brief (e.g. static room tone or city rain). Place this on track A2. Fade it in at the opening frame and let it run continuously under all edits to unify the cuts.

### Step 4: Synchronize Foley SFX
Scroll through the video frame by frame. Wherever a physical action occurs (a screen flickers, a head turns, boots hit pavement), place a matching sound effect on track A3. Align the audio peak exactly with the visual moment of impact.

### Step 5: Score the Scene
Place your background music on track A4. Set the general music volume low (around -18dB to -24dB). Enable **Audio Ducking** so that the music automatically drops by an additional 6dB whenever the voice track (A1) is active.

### Step 6: Apply a Unified Color Grade
Select all video clips on V1. Add an adjustment layer over the entire timeline and apply a film emulation LUT (e.g. Kodak 2383 style). This unifies the highlights and shadow colors across all separate generations, hiding minor color discrepancies. Export the finished project at 24fps.

---

## Worked Example

**Timeline Assembly for "The Last Signal" Scene 1**

Here is the track layout inside the editing timeline for the first 12 seconds:

* **V1 (Video Track):**
  * 0:00 - 0:04: Shot 1.1 (Establishing Wide Shot of cockpit)
  * 0:04 - 0:08: Shot 1.2 (Astronaut portrait, slow dolly-in)
  * 0:08 - 0:12: Shot 1.3 (Close-up of static screen)
  * *Effect:* Adjustment layer over V1 with a "Teal & Orange" LUT at 70% opacity.

* **A1 (Dialogue Track):**
  * 0:05 - 0:08: JOHN (V.O.): *"No one has answered in six months."*
  * *Settings:* Centered mono channel, volume set to -3dB.

* **A2 (Ambience Track):**
  * 0:00 - 0:12: Continuous loop of `"Low spaceship drone hum with computer static"`
  * *Settings:* Volume set to -18dB.

* **A3 (SFX/Foley Track):**
  * 0:08 - 0:09: Synchronized `"Electric spark & CRT monitor flicker hum"` as Shot 1.3 cuts in.
  * *Settings:* Volume set to -6dB.

* **A4 (Music Track):**
  * 0:00 - 0:12: Slow, tense ambient synthesizer pad.
  * *Settings:* Volume set to -20dB, ducking to -26dB during John's voice line.

**The Result:** The sequence feels like a unified piece. The screen flicker sound hides the hard visual cut to the static screen, and the continuous spaceship hum holds the atmosphere together across the cuts.

*Existing Automation Reference:* If you want to automate this timeline assembly and audio synchronization, you can reference the [`Open-AI-Micro-Drama-Generator`](https://github.com/Anil-matcha/awesome-generative-ai-apps/tree/main/video_generation/Open-AI-Micro-Drama-Generator) app, which maps dialogue transcripts directly to video durations and builds the combined assets programmatically.

---

## Compare Tools

| Editing / Sound Tool | Capabilities | Setup Effort | Best for |
|---|---|---|---|
| **DaVinci Resolve / Premiere Pro** | Professional NLE. Multi-track editing, advanced audio ducking, professional LUT color grading. | High (Needs local installation and learning curve) | Widescreen films, commercial ads, and high-end festival entries. |
| **CapCut Desktop** | Lightweight editor. Auto-captions, built-in sound effects library, and easy timeline cutting. | Low | Vertical micro-dramas, TikToks, and fast social media formats. |
| **ElevenLabs (Audio-Native)** | Best voice cloning, natural emotional inflection, and built-in Foley SFX generation from text prompts. | Low (API/Web interface) | High-fidelity narration, character voiceovers, and custom sound effects. |

For fast, high-volume production (like vertical drama series), CapCut is the most efficient choice because of its built-in assets and captions engine. For narrative short films, DaVinci Resolve is preferred for its superior color grading engine.

---

## Launch It

**How to monetize this skill:**
* **AI Film Editor & Sound Designer:** Many AI creators can generate pretty pictures but do not know how to edit or design sound. Offer "Assembly and Sound Design Packages" for AI filmmakers, charging **$100–$300** per finished minute of film.
* **Vertical Drama Production:** Produce and edit 1-minute drama episodes for creators building mobile mini-series. Agencies and platforms pay **$150–$350** per edited vertical episode.

**Where to find clients:**
Cold pitch AI influencers on YouTube/Instagram who post silent loops or slideshows. Show them a 10-second sample of their own footage edit with voiceover and sound effects to prove the value.

---

## Exercises

1. **Easy:** Import 3 random silent video clips into your editor. Synchronize a continuous ambient background sound and a simple background music track.
2. **Medium:** Take a silent 4-second clip of a character speaking. Generate a dialogue line in ElevenLabs, import it, and edit the clip's visual duration to match the audio line length exactly.
3. **Hard:** Perform a color-matching challenge: import 3 video clips generated from different video models (with different lighting). Color grade them using color match wheels or a shared LUT to make them look like they were filmed in the same room on the same camera.

---

## Templates

Reusable template(s) this module produces:

* [`templates/sound-design-checklist.md`](templates/sound-design-checklist.md) — a master list for dialogue, ambience, SFX, and music leveling.

---

[← Camera Movement & Cinematography Prompts](03-camera-movement.md) · Next: [Selling Short-Form Films →](05-selling-short-films.md)
