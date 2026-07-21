# Track 2: AI Filmmaking

> Short films, music videos, trailers, and documentaries — made without a crew.

Five modules, in order. Each is one markdown file — click straight in, no subfolders. Every module follows the same structure: Problem → Concept → Do It → Compare Tools → Launch It → Exercises.

**"Templates" below** = the reusable template(s) each module produces (a screenplay template, shot list, terms sheet) — actual files you fill in and reuse, saved in [`templates/`](templates/).

| # | Module | Time | Requires |
|:---:|---|:---:|---|
| 1 | [Screenplay & Story Generation](01-screenplay-and-story.md) | ~40 min | — |
| 2 | [Storyboarding & Shot Planning](02-storyboarding-and-shots.md) | ~40 min | Module 1 |
| 3 | [Camera Movement & Cinematography Prompts](03-camera-movement.md) | ~50 min | Modules 1–2 |
| 4 | [Assembling a Short Film](04-assembling-short-film.md) | ~50 min | Modules 1–3 |
| 5 | [Selling Short-Form Films](05-selling-short-films.md) | ~30 min | Modules 1, 4 |

---

### 1. [Screenplay & Story Generation](01-screenplay-and-story.md)

> A good script is cheap; a good story that can actually be filmed by AI is rare.

- Learn the unique physical and character constraints of modern generative video models.
- Structure visual screenplay actions to double directly as text prompts.
- Utilize General LLMs (Claude/Gemini) to output structured prompts instead of generic actions.

**Templates:** [`screenplay-prompt-template.md`](templates/screenplay-prompt-template.md) · [`ai-film-brief.md`](templates/ai-film-brief.md)

### 2. [Storyboarding & Shot Planning](02-storyboarding-and-shots.md)

> A storyboard is the blueprint that stops you from burning credits on random video generations.

- Establish consistent characters (wardrobe, facial features, styling) using static image references.
- Utilize prompt prefixes and seeds to align the lighting and color palette before generating video.
- Design a complete camera shot list matching visual hierarchy (Wide, Medium, Close-up).

**Templates:** [`shot-list-template.md`](templates/shot-list-template.md) · [`style-guide-template.md`](templates/style-guide-template.md)

### 3. [Camera Movement & Cinematography Prompts](03-camera-movement.md)

> Camera movement is the difference between an AI slideshow and a movie.

- Apply dynamic cinematography verbs (dolly, track, tilt, crane) instead of generic motion terms.
- Condition video generators on storyboard first-frames to lock starting compositions.
- Control rendering artifacts using motion strength values and speed sliders.

**Templates:** [`motion-prompt-library.md`](templates/motion-prompt-library.md) · [`cinematography-cheat-sheet.md`](templates/cinematography-cheat-sheet.md)

### 4. [Assembling a Short Film](04-assembling-short-film.md)

> The film isn't made in the generator; it's made in the editor.

- Cut, trim, and stitch silent video clips to build scene rhythm.
- Set up a multi-layered sound design timeline: voiceover narration, continuous ambient room tone, Foley SFX, and score.
- Color grade separate clips using LUTs to achieve unified visual tone and cinematic atmosphere.

**Templates:** [`sound-design-checklist.md`](templates/sound-design-checklist.md)

### 5. [Selling Short-Form Films](05-selling-short-films.md)

> Festivals want the story; sponsors want the eyeballs; platforms want the assets.

- Direct film packaging structures (widescreen master, vertical cuts, clean voice-less audio tracks).
- Target and structure brand sponsorship pitch proposals for product placement.
- Negotiate upfront platform fees and revenue-sharing splits for episodic vertical dramas.

**Templates:** [`sponsorship-pitch-template.md`](templates/sponsorship-pitch-template.md) · [`licensing-agreement-sheet.md`](templates/licensing-agreement-sheet.md)

---

All templates live in [`templates/`](templates/). For status across the other 14 tracks, see [ROADMAP.md](../../ROADMAP.md).
