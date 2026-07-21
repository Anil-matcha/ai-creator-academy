# Character to Content Pipeline

> The character is the face, but the motion makes them real.

**Track:** AI Avatars & Influencers  
**Time:** ~45 minutes  
**Prerequisites:** Building a Consistent AI Character  

## The Problem

A static image of an AI avatar is only useful for photo-based feeds (like Instagram grid posts). But the highest reach, attention, and advertiser payments are on **video feeds** (TikTok, YouTube Shorts, Reels). If your character cannot talk, move, and present information in video format, you cannot build a scalable virtual influencer brand.

However, video animation presents severe challenges. If you run your consistent character through a standard image-to-video model, the face will warp as soon as the head moves. The hair structure will change, or the clothing textures will slide around, creating an unnatural "uncanny valley" effect that drives viewers away.

To animate your character successfully, you need to establish a dedicated lip-sync and compositing pipeline that animates only the mouth and facial expressions while locking down the rest of the head and body.

## The Concept

The professional virtual influencer video pipeline is based on **Lip-Sync Video Rendering**:

```
Static Avatar Portrait + Clean Voice Audio  ──►  Lip-Sync Engine  ──►  Talking Head Video
```

1. **The Static Anchor:** Instead of generating a full video from scratch, you use your consistent Master Portrait as the visual anchor.
2. **Audio-Driven Lip Sync:** You feed the Master Portrait and your generated voice track into a lip-sync API (like `sync-lipsync` or `volcengine-video-to-video-lip-sync` via muapi). The engine morphs *only* the mouth, jaw, and eyes to match the audio waveforms, keeping the head structure, hair, and clothing 100% consistent.
3. **Compositing & Overlay:** To make the video look dynamic, you cut away from the talking head every 4–5 seconds, overlaying b-roll screenshots, charts, or slides while the voice track continues playing.

---

## Do It

### Step 1: Prep Your Assets
Ensure your files meet the guidelines in the [`templates/lipsync-spec-sheet.md`](templates/lipsync-spec-sheet.md). Lock down your static Master Portrait (`emma-master.jpg`) and your clean voiceover narration (`01_intro.mp3`).

### Step 2: Call the Lip-Sync API
Submit your assets to the `/sync-lipsync` (or volcengine lip-sync) endpoint:
* **Audio URL:** The public URL of your narration file.
* **Image URL:** The public URL of your consistent avatar portrait.
* Set the aspect ratio to `9:16` or `1:1` to match your target feed.

### Step 3: Download & Audit the Render
Download the generated `.mp4` file. Run a quality audit:
* **Mouth warping:** Check if the mouth coordinates stretch unnaturally during fast words.
* **Drift:** Ensure the lips match the voice track syllables. If there is a slight lag, adjust the audio track by -50ms to -100ms in your timeline to align the sync.

### Step 4: Add B-Roll Overlays in Editing
Import the talking-head video into CapCut. Do not leave the talking head on screen for the entire 60 seconds.
* **0.0 - 3.0s:** Keep the avatar on screen to establish the human hook.
* **3.0 - 15.0s:** Cut away to high-contrast b-roll (screen recordings, product shots) while the voiceover continues on A1.
* **15.0 - 18.0s:** Cut back to the avatar's face to re-establish connection.

---

## Worked Example

**Animating "Emma" for a 60-Second Short**

* **Assets Prepped:** `emma-master.jpg` (centered face) and `01_hook.mp3` (*"Hey, it's Emma here. Today we are..."*, duration: 4.5 seconds).
* **Lip-Sync Processing:** Assets fed into `/sync-lipsync`. The output video file is 4.5 seconds long, showing Emma speaking the intro text naturally with blink animations.
* **Timeline Assembly:**
  * **0.0 - 4.5s:** Emma is on screen speaking directly to the audience. Text captions overlay on Y-axis.
  * **4.5 - 20.0s:** Video track cuts to screen recording of a Zapier automation workspace. Emma's voiceover continues.
  * **20.0 - 24.0s:** Video track cuts back to Emma speaking.

**The Result:** The video is highly dynamic. The viewer is hooked by a realistic, talking face, but the body of the video is filled with informative screenshots, keeping engagement high while minimizing rendering costs.

**The clip below is real, not a mockup** — the consistent cafe image animated into a short vertical video loop using `seedance-2-image-to-video-fast` from the scenario above, so you can see what a first-pass output actually looks like:

<p align="center"><img src="templates/examples/emma-clip.gif" alt="Emma consistent cafe video (silent GIF preview)" width="158"></p>

<p align="center"><a href="templates/examples/emma-clip.mp4">▶ Watch the original (.mp4)</a> — GitHub can't play video inline in a README, so the GIF above is a silent preview; the linked file has the high-quality render.</p>

<p align="center"><i>An unedited first pass — Emma blinks naturally, shifts her head slightly, holding the coffee cup, dynamically animated by the video engine for high-retention content.</i></p>

*How this was actually produced, end to end, via the muapi API:*
1. Took the consistent face-swapped image `emma-cafe-consistent.jpg`.
2. Uploaded it via muapi's `upload_file` endpoint to get a public URL.
3. Fed that URL into **`seedance-2-image-to-video-fast`** (image-to-video, $0.50/clip) on the `images_list` param with a vertical aspect ratio and a prompt describing Emma's facial movement.
4. Downloaded the resulting `.mp4` and converted it to the silent GIF preview above using `ffmpeg`.

---

## Compare Tools

| Platform / Tool | Rendering Quality | Payout / Credit Cost | Setup Effort |
|---|---|---|---|
| **muapi `/sync-lipsync`** | High (Maintains background details, provides natural blinking) | ~$0.50 per clip | Low (Direct API call) |
| **HeyGen / Synthesia** | Very High (Pre-built bodies and hand gestures, but subscription is expensive) | High ($30–$200/mo) | Low |
| **Local ComfyUI (LivePortrait)** | Ultra-High (Tracks exact movements from a webcam actor) | Free | Very High (Requires heavy GPU setup and node mapping) |

For content factories delivering client projects, using muapi's `/sync-lipsync` is the most scalable option. It charges only per API call with no monthly subscription lock-in, and outputs high-fidelity head movement that matches custom voiceover files.

---

## Launch It

**How to optimize your video files:**
* **Use Green-Screen Backgrounds:** If you want your avatar to sit in front of changing backgrounds, generate your Master Portrait with a solid green background. Use the editor's Chroma Key tool to remove the green and composite the talking head over any video clip.
* **Add Subtle Ambient Light:** Apply an adjustment layer in editing with a soft amber or teal color overlay at 5% opacity to blend the avatar face into the background lighting, making it look integrated.

---

## Exercises

1. **Easy:** Gather one clean front-facing face image and a 5-second audio clip. Verify that they meet the checklist specs.
2. **Medium:** Submit your prepped assets to a lip-sync engine. Download the video and align the audio track to the timeline, correcting any minor lip sync delays.
3. **Hard:** Produce a 30-second vertical video where the AI avatar speaks for the first 3 seconds, cuts to green-screen background b-roll for 20 seconds, and cuts back to the avatar for a 7-second call-to-action.

---

## Templates

* [`templates/lipsync-spec-sheet.md`](templates/lipsync-spec-sheet.md) — visual and audio prep checklists and sync logs.

---

[← Building a Consistent AI Character](01-consistent-character.md) · Next: [Voice Cloning & Dialogue →](03-voice-cloning-dialogue.md)
