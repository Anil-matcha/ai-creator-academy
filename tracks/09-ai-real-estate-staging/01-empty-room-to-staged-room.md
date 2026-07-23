# Empty Room → Staged Room Pipeline

> Transform vacant properties into high-converting luxury homes in minutes using depth-aware AI inpainting.

**Track:** AI Real Estate (Virtual Staging)  
**Time:** ~40 minutes  
**Prerequisites:** Basic understanding of image generation prompts  

## The Problem

Vacant real estate listings suffer from a major buyer perception gap: empty rooms feel smaller, colder, and harder to visualize than furnished spaces. According to the National Association of Realtors (NAR), **81% of buyers find it easier to visualize a property as a future home when it is staged**, and staged homes sell for **up to 20% more** than empty properties.

However, traditional physical staging is extremely expensive and slow:
* **Cost:** Renting physical furniture and hiring interior design crews costs **$2,500 to $5,000+ per month** per listing.
* **Turnaround:** Scheduling movers and assembling furniture takes **3 to 7 days**, delaying listing launches.
* **Risk:** Physical furniture risks scratching floors or damaging walls during transport.

If you attempt basic image editing or low-end 3D rendering, the furniture looks flat, out of scale, and unnaturally floating above the flooring, destroying buyer trust. You need a fast, photorealistic AI workflow that preserves room geometry while seamlessly populating spaces with trendy interior decor.

---

## The Concept

The AI virtual staging pipeline relies on **Perspective-Locked Inpainting** and **Depth-Aware Furniture Placement**:

```
Empty Room Photo ──► Depth Mask Generation ──► Perspective Alignment ──► Inpainting Furniture ──► Shadow & Reflection Matching
```

### Core Technical Pillars:

1. **Perspective & Vanishing Point Locking:** Real estate photography uses wide-angle lenses (16–24mm) with distinct architectural vanishing points. To prevent furniture from appearing distorted or skewed, the AI model must respect the existing horizon line and vertical wall angles.
2. **Floor & Wall Depth Preserving:** When populating an empty room, the AI model must detect floor planes, baseboards, and window light sources. Using ControlNet Depth or depth-masking ensures sofa legs resting on the floor align perfectly with wall bases without altering structural windows, doors, or flooring textures.
3. **Interior Style Presets:** High-performing virtual staging targets specific buyer demographics through curated aesthetic themes:
   * **Modern Scandinavian:** Light oak, neutral linen sofas, minimalist coffee tables, potted monstera plants.
   * **Contemporary Luxury:** Velvet sectionals, marble coffee tables, brass accent lighting, plush area rugs.
   * **Coastal Modern:** Light textiles, rattan accents, soft blues, woven jute rugs, warm natural sunlight.

---

## Do It

### Step 1: Capture & Select the Source Photograph
Obtain a high-resolution wide-angle photograph of the vacant room. Ensure the photo is straight (horizontally level and vertically plum) and well-lit with natural daylight. Save as `empty-room-source.jpg`.

### Step 2: Define the Staging Mask Area
Open your photo editor or inpainting interface. Select the floor area where furniture should sit while keeping structural features (windows, fireplaces, support columns, structural walls) untouched. Create an inpainting mask layer covering 60–70% of the open floor space.

### Step 3: Write the Depth-Aware Staging Prompt
Assemble a prompt using your interior style specifications from [`templates/virtual-staging-brief.md`](templates/virtual-staging-brief.md). Prepend architectural and lighting anchor tokens matching the original photo:

* **Prompt:**  
  > `"High-end modern luxury living room virtual staging. A sleek cream fabric L-shaped sectional sofa with plush pillows resting on a soft beige area rug, low-profile oval wood coffee table, potted fiddle-leaf fig in ceramic planter, natural sunlight casting soft shadows, interior design magazine style, 8k photorealistic resolution, perfectly aligned to floor plane."`
* **Negative Prompt:**  
  > `"warped floor, distorted furniture legs, floating objects, cartoon, low resolution, blurry, altered windows, altered walls, 3d render look, oversaturated."`

### Step 4: Execute Inpainting with ControlNet / Depth Reference
Pass `empty-room-source.jpg` and your mask into the model (e.g., FLUX Inpainting or muapi `/nano-banana-2` inpainting mode). Set ControlNet Depth weight to `0.75` to enforce structural floor geometry while allowing the model to generate 3D furniture volumes.

### Step 5: Composite & Verify Contact Shadows
Inspect the output at 100% zoom:
* **Floor Contact:** Verify sofa and table legs touch the floor naturally with dark, tight contact shadows (ambient occlusion).
* **Light Source Consistency:** Confirm furniture highlights match window sunlight direction.
* Save the final staged image as `staged-living-room.jpg`.

---

## Worked Example

<p align="center">
<img src="templates/examples/staged-living-room.jpg" alt="Staged Living Room AI Image" width="320">
<img src="templates/examples/living-room-staging-motion.gif" alt="Staged Living Room Motion Loop (I2V)" width="320">
</p>
<p align="center"><sub>AI Staged Living Room Image (Left) ──► Image-to-Video Walkthrough Loop (Right) · Video File: <a href="templates/examples/living-room-staging-motion.mp4">templates/examples/living-room-staging-motion.mp4</a></sub></p>

**Staging Execution Breakdown for "Oakridge Listing"**

* **Source Property:** Empty 450 sq ft living room with hardwood floors and large sunlit windows.
* **Target Buyer:** Young professional couple seeking modern luxury styling.
* **Selected Furniture Pack:** Scandinavian Luxury (Cream Sectional, Oak Coffee Table, Textured Rug, Indoor Botanicals).
* **Render Settings:** Denoising strength `0.65`, Depth weight `0.80`, 16:9 aspect ratio matching camera output.
* **Turnaround Time:** 4 minutes total processing time.
* **Cost:** **$0.06** AI generation cost vs. **$3,200** traditional physical staging quote.

---

## Compare Tools

| Platform / Method | Turnaround Time | Cost per Photo | Realism & Control | Best For |
|---|---|---|---|---|
| **FLUX / muapi Inpainting API** | < 1 minute | $0.05 - $0.15 | **Extremely High** — Custom depth control, exact furniture styling | High-volume real estate agencies and automated staging workflows |
| **Specialized Staging SaaS (BoxBrownie, VirtualStagingAI)** | 24 - 48 hours | $20 - $35 | **High** — Manual designer review or fixed 3D catalog | One-off residential listings with fixed budget |
| **Traditional Physical Staging** | 3 - 7 days | $2,500 - $5,000+ | **Physical Reality** — Actual furniture in house | Ultra-luxury mega-mansions ($5M+) with in-person open houses |

---

## Launch It

**How to price & package this service:**
* **Single Room Staging:** **$35 – $50** per photo.
* **Full House Listing Package (5 Rooms):** **$149 – $199** package price (includes Living Room, Master Bedroom, Kitchen/Dining, Guest Bedroom, Patio).
* **Delivery Specs:** Deliver high-resolution JPEGs (3000px+ wide) optimized for MLS (Multiple Listing Service) and Zillow/Redfin uploads within 24 hours.

---

## Exercises

1. **Easy:** Photograph an empty room in your home or download a vacant room stock photo. Identify the primary vanishing point and window light source.
2. **Medium:** Use an inpainting tool to place a modern sofa and coffee table into the empty room while preserving original flooring and wall textures.
3. **Hard:** Perform a multi-style staging test on the same empty room: render one version in **Modern Scandinavian** and a second version in **Industrial Loft**, ensuring lighting and perspective match in both renders.

---

## Templates

* [`templates/virtual-staging-brief.md`](templates/virtual-staging-brief.md) — Interior design style guides, prompt frameworks, and quality control checklists.

---

[Track Overview](README.md) · Next: [Pricing Against Traditional Staging →](02-pricing-against-traditional-staging.md)
