# Consistent Headshot Generation

> Transform casual smartphone selfies into studio-grade corporate portraits without facial distortion or artificial plastic skin.

**Track:** AI Headshots & Portraits  
**Time:** ~40 minutes  
**Prerequisites:** None  

## The Problem

Professional headshots are essential for LinkedIn profiles, corporate website team pages, speaker keynotes, and press releases. However, traditional studio headshot sessions are painful and expensive:
* **High Cost:** Booking a professional photographer, studio space, and hair/makeup artists costs **$250 to $600 per person**.
* **Time Consumption:** Travel time, wardrobe changes, and waiting 5 to 7 days for edited proofs wastes valuable working hours.
* **Inconsistency for Teams:** When companies hire remote employees globally, getting a consistent background, lighting style, and dress code across 30 team members is nearly impossible.

If you attempt basic AI face swaps or over-filtered app presets, the output looks fake: skin textures become waxy plastic, eye colors drift, teeth align into unnatural artificial rows, and background lighting doesn't match the subject's face.

---

## The Concept

The professional AI headshot generation pipeline relies on **Facial Identity Locking**, **Lighting Rig Alignment**, and **Skin Texture Preservation**:

```
Casual Smartphone Selfie ──► Face Embed & Identity Lock ──► Studio Lighting & Outfit Prompt ──► Detail Upscale & Skin Frequency Match
```

### Technical Pillars:

1. **Facial Identity Vector Locking (InstantID / FLUX PuLID):** Rather than generating a random person, identity-locking models extract facial landmarks (eye spacing, jawline shape, nose bridge structure, skin tone) from 1 to 3 casual reference selfies. Passing this embedding into the diffusion model ensures the output looks unmistakably like the subject.
2. **Studio Lighting Rigs (3-Point Lighting in Prompts):** Professional portrait photography relies on controlled lighting setups:
   * **Key Light:** Primary illumination softbox set at a 45-degree angle to create natural dimension (Rembrandt or Butterfly lighting pattern).
   * **Fill Light:** Diffused soft light on the shadow side to maintain detail without harsh dark patches.
   * **Rim / Hair Light:** Backlight behind the subject to separate their hair and shoulders from the background.
3. **High-Frequency Skin Texture Preservation:** Low-end AI filters destroy natural pores, fine wrinkles, and freckles. Setting img2img denoising strength to **0.40–0.55** and applying frequency separation in post-processing preserves authentic skin micro-texture while cleaning up messy backgrounds and informal clothing.

---

## Do It

### Step 1: Collect Quality Source Selfies
Instruct your client or subject to upload 3 to 5 casual photos:
* High resolution (well-lit by window daylight, no heavy filters, no sunglasses, neutral or smiling expression).
* Direct eye contact with the camera.
* Varying angles (front-facing, 3/4 turn).

### Step 2: Assemble the Corporate Studio Prompt
Open your lighting guide in [`templates/headshot-style-guide.md`](templates/headshot-style-guide.md). Prepend photography anchors matching the target professional tier:

* **Executive Corporate Prompt:**  
  > `"Photorealistic 8k corporate studio portrait photograph of [Identity Anchor], confident friendly expression, wearing a tailored charcoal navy blazer and crisp white shirt, soft Rembrandt key light, subtle rim light separating shoulders from background, blurred modern glass office background with soft bokeh, shot on 85mm f/1.8 lens, natural skin pores, studio quality."`
* **Creative Tech Founder Prompt:**  
  > `"Photorealistic 8k editorial portrait photograph of [Identity Anchor], warm approachable smile, wearing a stylish dark grey turtleneck, soft warm studio lighting, neutral grey gradient background, crisp focus on eyes, 85mm lens, highly detailed."`
* **Negative Prompt:**  
  > `"plastic skin, smooth mannequin face, extra teeth, asymmetric eyes, cartoon, oversaturated, harsh direct flash, warped neck, low resolution, blurry."`

### Step 3: Run Identity-Locked Inference
Pass the source selfie and prompt into your generator (e.g., muapi `/nano-banana-2` with face-reference parameter or InstantID pipeline). Set aspect ratio to **1:1** for LinkedIn/Slack avatars or **4:5** for executive team pages.

### Step 4: Refine Clothing & Background Swaps
If the client wants multiple wardrobe variations (e.g., formal suit vs. business casual sweater), run targeted inpainting over the torso area while keeping the facial identity seed locked.

### Step 5: Frequency Separation & Skin Restoration
Inspect the render at 100% zoom:
* Confirm skin contains visible natural pores and authentic eye catchlights.
* Apply subtle sharpening to iris reflections.
* Save the final high-resolution file as `corporate-executive-headshot.jpg`.

---

## Worked Example

<p align="center">
<img src="templates/examples/corporate-executive-headshot.jpg" alt="Corporate Executive AI Headshot" width="320">
<img src="templates/examples/headshot-lighting-motion.gif" alt="Headshot Lighting & Motion Loop (I2V)" width="320">
</p>
<p align="center"><sub>AI Corporate Executive Portrait (Left) ──► Image-to-Video Motion Loop (Right) · Video File: <a href="templates/examples/headshot-lighting-motion.mp4">templates/examples/headshot-lighting-motion.mp4</a></sub></p>

**Corporate Rebrand Breakdown for "Apex Financial Group"**

* **Source File:** A casual phone selfie taken in a living room with harsh ceiling light.
* **Target Style:** Executive Corporate Navy Blazer & Office Bokeh.
* **Model Pipeline:** Identity vector extraction via InstantID + FLUX 1.1 render.
* **Generation Settings:** Denoising strength `0.45`, Identity weight `0.85`, 85mm lens prompt anchor.
* **Turnaround:** 3 minutes total processing time.
* **Cost:** **$0.06** AI generation cost vs. **$350** local studio quote.

---

## Compare Tools

| Platform / Pipeline | Face Consistency | Skin Realism | Best For |
|---|---|---|---|
| **FLUX PuLID / InstantID (muapi API)** | **Extremely High** | **Photorealistic** — Preserves natural pores & expression | Professional client delivery, corporate team packages |
| **Consumer Headshot Apps (Remini, HeadshotPro)** | Medium | Low — Over-smoothed "plastic" skin effect | Low-budget personal social avatars |
| **Custom LoRA Fine-Tuning (ComfyUI / Kohya)** | Maximum | High — Requires 15+ training images | Celebrity, executive, or recurring influencer models |

---

## Launch It

**Packaging options:**
* **Individual Professional Package:** **$49 – $79** (Includes 5 styled variations: Formal, Business Casual, Creative, Studio Dark, Office Bokeh).
* **Corporate Team Pass (10 Employees):** **$399 – $599** (Includes consistent corporate background and dress code matching company brand guidelines).

---

## Exercises

1. **Easy:** Take a casual selfie in window daylight. Write a prompt to generate a studio portrait with a blurred office background.
2. **Medium:** Perform a clothing swap on the generated portrait, converting a casual t-shirt into a navy suit blazer.
3. **Hard:** Generate 3 consistent team headshots for 3 different individuals using the same studio lighting prompt and background bokeh, ensuring company brand consistency across all 3.

---

## Templates

* [`templates/headshot-style-guide.md`](templates/headshot-style-guide.md) — Lighting setup prompts, wardrobe descriptors, and negative prompt libraries.

---

[Track Overview](README.md) · Next: [Standing Out Against Fiverr Competition →](02-standing-out-against-fiverr-competition.md)
