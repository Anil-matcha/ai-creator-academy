# Garment Try-on for Fashion E-commerce

> A garment only comes alive when it moves with a human body.

**Track:** AI Fashion & Virtual Try-On  
**Time:** ~45 minutes  
**Prerequisites:** None  

## The Problem

For e-commerce fashion brands, booking models, hair/makeup artists, photographers, and renting studios is a massive recurring cost. A single product line shoot can cost over $5,000 and take weeks to edit.

To save money, brands often rely on flat-lays (clothing laid flat on a table) or "ghost mannequin" shots (clothing on a plastic dummy that is edited out). While cheap, these photos look flat and uninspiring. Customers want to see how the fabric drapes, folds, fits, and matches a real person's body. Without human model photos, fashion brands suffer from low click-through rates and high return rates because customers cannot judge the fit.

To launch new designs instantly without physical photo shoots, you need to implement a **Virtual Try-On (VTO)** pipeline.

## The Concept

The fashion synthesis workflow uses **Garment Segmentation**, **Virtual Try-On (VTO) Diffusion**, and **Draping Fitting**:

```
Flat Garment Photo ──► Garment Mask Extraction ──► VTO Model Alignment ──► Timbre-Draping Synthesis
```

* **Preserving Garment Integrity:** Unlike standard image generators that change clothing details, a VTO model uses a reference garment image. It isolates the garment, analyzes its texture, stitching, buttons, and patterns, and drapes it onto a target model's body while preserving **95%** of the original physical detail.
* **Mannequin-to-Model Transfer:** If you already have ghost mannequin shots, VTO engines can use the mannequin pose as a structural guide, replace the plastic limbs and head with a real model, and keep the exact fit.
* **Custom Model Demographics:** You can swap the model's ethnicity, age, height, and build while keeping the same garment. This allows brands to instantly personalize their landing pages for different regional target markets.

---

## Do It

### Step 1: Prep Your Garment Reference Photo
Photograph your physical garment flat-lay or on a mannequin. Make sure it is flat, in focus, and shot under clean daylight. Remove the background using an AI subject cutter to isolate the garment. Save it as `garment_ref.png`.

### Step 2: Define Model Demographics
Open your try-on specification sheet in [`templates/tryon-spec-sheet.md`](templates/tryon-spec-sheet.md). Document the target model's parameters:
* *Example:* East Asian male, 28 years old, athletic build, standing in a studio environment.

### Step 3: Choose a Target Model Model Pose
If your try-on pipeline supports reference models, upload a photo of a model in your desired pose (e.g. Pose A: standing straight, hands at sides). If using a text-to-image edit model (like `nano-banana-2-edit`), upload the original mannequin photo, mask the clothing area, and write your target model description.

### Step 4: Run the VTO Draping Engine
Submit your assets to the try-on engine (such as IDM-TryOn or Kolors VTO API):
* Pass the `garment_ref.png` as the clothing input.
* Pass the model pose image or text prompt as the target body input.
* Set the draping fitting rate to **0.75** (balancing cloth detail preservation with realistic body movement wrinkles).
Generate and download the output `.jpg`.

### Step 5: Perform Detail Quality Control
Zoom in on the final image and inspect these key areas:
* **Collar & Button borders:** Ensure the collar shapes are crisp and not blurry or merged with the skin.
* **Cuffs & Hemlines:** Verify that the hands pass naturally through the shirt cuffs, and that the bottom hem lies straight.
* **Prints & Textures:** Check that stripes, prints, or logos follow the natural curves and folds of the model's body.

---

## Worked Example

**Linen Shirt Mannequin-to-Model Swap**

* **Garment Input:** A flat ghost mannequin shot of an off-white linen button-down shirt.
* **Target Model:** A 30-year-old Caucasian male model with an athletic build.
* **VTO Pipeline:** IDM-TryOn API call.
  * `garment_image` = `linen_shirt.png`
  * `model_image` = `reference_male_model.jpg`
* **Synthesis Output:** The off-white linen shirt is draped over the model. Buttons are clear, stitching lines are sharp, and the linen fabric's cross-hatch texture is fully preserved. Soft shadows sit naturally under the shirt collar.

**The Result:** The brand upgraded their online catalog page from a plastic mannequin to a professional model shot, raising the perceived premium value of the shirt.

---

## Compare Tools

| Platform / Tool | Detail Preservation | Pose Customization | Best for |
|---|---|---|---|
| **IDM-TryOn** | Ultra-High (Preserves complex patterns, textures, and fabric stitching) | Medium | Creating high-fidelity e-commerce listing catalog photos. |
| **Kolors Virtual Try-On** | High | High (Excellent at adjusting cloth to complex poses) | Creative fashion editorial lookbooks and social graphics. |
| **Kling AI Image-to-Video** | Medium | High (Can animate models walking while wearing clothing) | Creating short video loops of models walking. |

For standard product detail pages (PDP) on Shopify or Amazon, IDM-TryOn is the preferred tool because it keeps the garment's logos, text, and fabric textures perfectly sharp. For social media banner ads where you need models in active poses (running, jumping), Kolors VTO provides better pose adjustments.

---

## Launch It

**How to organize catalog images:**
* **Maintain model consistency:** Use the exact same target model face and body across a single product category page. If a shopper clicks through shirts and the model's face changes on every item, the store layout will look amateur and inconsistent.
* **Store high-resolution templates:** Save your top model pose templates in a master folder. When you release a new garment line, reuse these exact poses to speed up batch rendering.

---

## Exercises

1. **Easy:** Photograph a t-shirt flat-lay. Use a background cutter to create a clean clothing PNG mask.
2. **Medium:** Submit your t-shirt PNG to a virtual try-on tool. Generate a male model and a female model wearing the same shirt.
3. **Hard:** Using a ghost mannequin shot of a buttoned jacket, run a VTO draping pipeline. Review the collar edges and cuff seams at 200% zoom. Correct any border bleeding using a photo editor.

---

## Templates

* [`templates/tryon-spec-sheet.md`](templates/tryon-spec-sheet.md) — garment specs, model demographic charts, mask targets, and QA checks.

---

[Track overview](README.md) · Next: [High-converting Studio Lookbooks →](02-studio-lookbooks.md)
