# AI Image Model Selection Guide & Benchmark Matrix

Use this reference guide to match client project requirements to the right AI image generation model.

---

## 📊 Image Model Performance Matrix

| Model | Photorealism (Skin & Lighting) | Typography & Text Accuracy | Spatial Prompt Adherence | Style Versatility | Render Speed | API Cost / Image |
|---|---|---|---|---|---|---|
| **FLUX 1.1 Pro** | **9.5 / 10** | **9.5 / 10** | **9.5 / 10** | 8.5 / 10 | ~5 sec | **$0.04** |
| **FLUX Schnell** | 8.5 / 10 | 9.0 / 10 | 9.0 / 10 | 8.0 / 10 | **~2 sec** | **$0.003** |
| **Midjourney v6** | 9.0 / 10 | 6.5 / 10 | 8.0 / 10 | **10.0 / 10** | ~15 sec | Sub ($10-$60/mo) |
| **Ideogram v2** | 7.5 / 10 | **10.0 / 10** | 9.0 / 10 | 8.5 / 10 | ~8 sec | **$0.08** |
| **DALL-E 3** | 6.5 / 10 | 8.5 / 10 | 9.0 / 10 | 7.5 / 10 | ~10 sec | **$0.08** |

---

## 🎯 Use Case Decision Tree

```
Project Requirement?
├── Corporate Headshots / Product Photos ──► FLUX 1.1 Pro / muapi (/nano-banana-2)
├── Apparel Merch / Logo Typography      ──► Ideogram v2 or FLUX 1.1 Pro
├── Film Storyboards / Artistic Fantasy ──► Midjourney v6 (--stylize 250+)
└── Fast Conceptual Brainstorming        ──► FLUX Schnell / DALL-E 3
```
