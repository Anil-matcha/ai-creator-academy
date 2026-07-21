# Visual Style Guide Template

Create a locked style guide for your film project to ensure color grading, lighting, and textures match across all generated scenes.

---

## 1. Core Prompt Style Prefix
Every image and storyboard prompt should start with this exact string of aesthetic instructions:
> **Aesthetic Prefix:** "Cinematic 35mm film photograph, anamorphic lens, muted color grading with deep teal shadows and soft amber highlights, film grain, highly detailed realistic skin texture, directed by [Director Name]..."

## 2. Aspect Ratio Settings
* **Selected Ratio:** [e.g., `--ar 2.39:1` for widescreen, `--ar 16:9` for standard, `--ar 9:16` for vertical]

## 3. Approved Lighting Setups
Only use these lighting descriptors in your prompts:
* **Interior shots:** "Low-key moody lighting, soft side-lighting from a single window, dust motes visible in light beam."
* **Exterior night shots:** "Hard backlighting from street lamps, neon glow reflections on wet concrete surfaces, high contrast."
* **Exterior day shots:** "Overcast lighting, soft diffused shadows, cool daylight."

## 4. Color Grading Matrix
Define the hex colors or descriptive palette keywords:
* **Primary shadows:** [Teal / Slate Gray / Deep Indigo]
* **Primary highlights:** [Warm Amber / Pale Gold / Soft White]
* **Saturation Level:** [Muted / High Contrast / Neon Saturation]

## 5. Negative Prompts / Excluded Styles
Ensure your generations avoid these styles:
> **Negative Prompt / Exclude list:** "render, 3D, CGI, illustration, drawing, high-saturation, digital art, cartoon, perfect skin, smooth texture, anime"
