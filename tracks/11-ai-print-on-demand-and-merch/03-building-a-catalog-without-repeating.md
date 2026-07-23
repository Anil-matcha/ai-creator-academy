# Building a Catalog Without Repeating Yourself

> Scale from 1 to 100+ unique merch listings using prompt matrix variations and niche sub-segmentation.

**Track:** AI Print-on-Demand & Merch Design  
**Time:** ~40 minutes  
**Prerequisites:** [01: Designing Sellable AI Art](01-designing-sellable-ai-art-for-merch.md), [02: POD Platform Basics](02-print-on-demand-platform-basics.md)  

## The Problem

To generate meaningful revenue on Etsy or POD marketplaces, you need a diverse catalog of **50 to 200+ listings**. However, creators often make two fatal mistakes:
1. **Spamming Identical Designs:** Uploading the exact same image with minor color tweaks, getting flagged for listing spam by marketplace algorithms.
2. **Burnout from One-Off Prompting:** Spending hours crafting custom prompts for one single shirt, making catalog expansion impossible to sustain.

You need a structured **Prompt Matrix Expansion System** to generate distinct, niche-targeted designs efficiently without creative repetition.

---

## The Concept

The **Niche Prompt Matrix** expands 1 core design theme across multiple sub-niches:

```
Core Theme (Retro Vintage Animals) ──► Niche Matrix (Cat / Dog / Owl / Bear) ──► Style Variations (80s Synthwave / Japanese Ink / Minimal Line) ──► 12 Distinct Listings
```

### The 3x3 Expansion Framework:

| Subject (Axis A) | Aesthetic Style (Axis B) | Target Customer Niche (Axis C) |
|---|---|---|
| Cyberpunk Cat | Japanese Sumi-e Ink | Tech Developers & Programmers |
| Vintage Botanical Sunflower | Cottagecore Watercolor | Gardening & Plant Enthusiasts |
| Retro Synthwave Mountain | 80s Neon Vector | Hikers & Outdoor Campers |

---

## Do It

### Step 1: Select a Passion Niche Matrix
Identify a passionate buyer niche (e.g., *Outdoor Camping & Coffee*).

### Step 2: Build a Variable Prompt Template
Open [`templates/merch-prompt-brief.md`](templates/merch-prompt-brief.md). Create a prompt template with replaceable variables:
* `"Clean vector graphic of [SUBJECT] drinking coffee by a campfire, [STYLE] style, bold outlines, isolated on solid background, 300 DPI"`
* Substitute `[SUBJECT]` with: `Bear`, `Fox`, `Raccoon`, `Owl`.
* Substitute `[STYLE]` with: `Retro 70s Badge`, `Minimalist Linework`, `Synthwave Neon`.

### Step 3: Batch Generate 12 Distinct Graphics
Run the prompt combinations through muapi `/nano-banana-2`. Isolate backgrounds and upscale all 12 graphics in batch.

### Step 4: Cross-Publish Across Product Types
Apply each graphic to 3 high-margin product types (T-Shirt, Coffee Mug, Canvas Tote Bag) to turn 12 graphics into **36 unique store listings**.

---

## Worked Example

<p align="center">
<img src="templates/examples/merch-design-vector-art.jpg" alt="Isolated Vector Merch Art Design" width="480">
</p>
<p align="center"><sub>Isolated Vector Art Graphic (Ready for Multi-Product Catalog Placement)</sub></p>

**Catalog Scaling Case Study: "The Retro Outdoor Collection"**

* **Core Concept:** Retro National Park Badge Illustrations.
* **Subjects Generated:** 5 Animals (Bear, Wolf, Bison, Eagle, Moose).
* **Styles Applied:** 70s Vintage Sunburst & Linework.
* **Total Products Published:** 5 Animals × 3 Products (Shirt, Mug, Hoodie) = **45 Active Listings**.
* **Time Taken:** 2.5 hours total setup.

---

## Launch It

* **Avoid Copyright & Trademark Infringement:** Never use trademarked names (e.g., Disney, Marvel, Nike) or celebrity likenesses in your prompts or store tags. Search USPTO TESS database before publishing.

---

## Exercises

1. **Easy:** Build a 3x3 prompt matrix for a niche of your choice (e.g., Coffee, Gaming, Cats).
2. **Medium:** Batch generate 6 distinct graphics from your matrix and isolate their backgrounds.
3. **Hard:** Publish a 15-item product collection across 3 product types (Tee, Mug, Tote) in your dev store.

---

## Templates

* [`templates/merch-prompt-brief.md`](templates/merch-prompt-brief.md) — Matrix prompt templates, niche variable tables, and trademark compliance checklists.

---

[← POD Platform Basics](02-print-on-demand-platform-basics.md) · Next: [Pricing & Passive-Income Math for POD →](04-pricing-and-passive-income-math.md)
