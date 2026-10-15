# AI Virtual Staging Brief & Style Guide Template

Use this brief to specify interior design aesthetics, room lighting parameters, and camera depth settings before generating virtual staging assets for real estate listings.

---

## 🏡 Property & Staging Brief

* **Property Address:** `[Property Street Address, City, State]`
* **Property Type:** `[e.g., Single Family Home, Modern Condo, Historic Craftsman, Luxury Penthouse]`
* **Target Buyer Profile:** `[e.g., Young Professionals, Growing Family, Executive Downsizer]`
* **Primary Architectural Features:** `[e.g., Hardwood floors, floor-to-ceiling windows, high vaulted ceiling, brick fireplace]`

---

## 🎨 Interior Design Style Packs

Select the interior style pack best suited to the property architecture:

### 1. Modern Scandinavian (Recommended Default)
* **Color Palette:** Warm white, natural oak, light beige, subtle sage green accents.
* **Furniture Selection:** Low-profile linen sectional sofa, light oak coffee table, neutral woven area rug, potted monstera or fiddle-leaf fig.
* **Lighting:** Diffused natural window sunlight, warm 3000K accent lamps.
* **Prompt Token:**
  > `"Modern Scandinavian living room virtual staging, light oak furniture, cream fabric sectional, plush beige rug, indoor potted plants, bright daylight, 8k photorealistic, architectural digest cover."`

### 2. Contemporary Luxury
* **Color Palette:** Deep navy, charcoal grey, brushed brass, white marble, emerald green.
* **Furniture Selection:** Velvet sofa with brass legs, marble-topped coffee table, dark hardwood accents, statement chandelier, abstract wall art.
* **Lighting:** Dramatic warm side lighting, recessed ceiling spot lights.
* **Prompt Token:**
  > `"Contemporary luxury living room staging, velvet sofa with gold brass accents, white marble coffee table, plush dark rug, sophisticated ambiance, photorealistic high end interior design."`

### 3. Coastal Modern
* **Color Palette:** Crisp white, seafoam blue, sandy beige, natural rattan, weathered wood.
* **Furniture Selection:** White slipcovered sofa, light wood coffee table, jute area rug, nautical decor accents, sheer curtains.
* **Lighting:** Bright airy sunshine, cool daylight shadows.
* **Prompt Token:**
  > `"Coastal modern staging, crisp white slipcover sofa, rattan coffee table, natural jute rug, airy beach house feel, bright natural window light, photorealistic."`

---

## 📋 Quality Control & Depth Checklist

- [ ] **Perspective Alignment:** Do furniture edges align with the room's vanishing point and wall angles?
- [ ] **Floor Contact:** Are tight, soft contact shadows (ambient occlusion) visible under sofa legs and coffee tables?
- [ ] **Scale Accuracy:** Is the furniture scaled realistically relative to doors, windows, and light switches?
- [ ] **Structural Preservation:** Are windows, doorways, flooring textures, and fireplaces left unaltered by the inpainting mask?
- [ ] **Resolution:** Is the exported JPEG at least 3000px wide and formatted in 16:9 or 4:3 for MLS uploads?
