# AI Storyboard Script & Shot Breakdown Template

Use this template to break down a screenplay scene into an AI-ready storyboard script before generating static images and video clips.

---

## 🎬 Project Overview

* **Film Title:** `[Film Name]`
* **Genre / Style:** `[e.g., Sci-Fi Noir, Cyberpunk, Cinematic Drama, Quiet Luxury]`
* **Scene Number & Title:** `Scene [X]: [Scene Title]`
* **Location & Setting:** `[INT/EXT. Location - Time of Day]`
* **Visual Anchor Character:** `[Character Name, Age, Outfit, Key Physical Attributes]`
* **Color Palette & Lighting:** `[e.g., Cool teal and cyan, neon orange rim lights, deep shadows]`

---

## 📌 Master Style Prefix & Negative Prompt

Lock consistency by prepending this exact style string to every AI image prompt in the scene:

* **Master Prompt Prefix:**
  > `"Cinematic 35mm film photograph, shot on Hasselblad 85mm lens, f/2.8 depth of field, [Color Palette/Mood], highly detailed 8k render."`

* **Master Negative Prompt:**
  > `"bad anatomy, cartoon, anime, 3d render, oversaturated, blurry, extra limbs, low resolution, watermark, deformed."`

---

## 📋 Multi-Shot Storyboard Script Breakdown

| Shot # | Shot Type | Subject & Action | Camera Framing & Lighting | AI Image Generation Prompt (`nano-banana-2`) | Image-to-Video Motion Prompt (`seedance-2`) | Asset Reference File |
|---|---|---|---|---|---|---|
| **Shot 1** | Wide Shot (WS) | Establishing shot of location | Wide angle, low position, volumetric mist | `[Master Prefix], wide establishing shot of [Location], [Lighting], widescreen 16:9` | `"Slow cinematic dolly forward into room, atmospheric smoke moving"` | `storyboard-shot1-wide.jpg` |
| **Shot 2** | Medium Shot (MS) | Character entrance / reaction | Eye-level, shallow depth of field | `[Master Prefix], medium shot of [Character Name] [Action], cool blue key light` | `"Character turns head toward camera, subtle facial muscle movement"` | `storyboard-shot2-medium.jpg` |
| **Shot 3** | Close-up (CU) | Prop / Detail interaction | Extreme close-up, macro focus | `[Master Prefix], close-up of [Prop/Object], macro focus, glowing status text` | `"Panning reflection across surface, digital screen flickering"` | `storyboard-shot3-closeup.jpg` |

---

## ⚙️ Drift Control Checklist

- [ ] Is the character reference image locked and passed as `images_list` for character shots?
- [ ] Are master style prefixes identical across all 3 prompts?
- [ ] Does the close-up shot isolate a prop to prevent character facial drift during scene transitions?
- [ ] Are aspect ratios aligned across all storyboard shots (`16:9` for landscape films, `9:16` for vertical shorts)?
