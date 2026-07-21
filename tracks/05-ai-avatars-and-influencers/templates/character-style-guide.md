# Character Style Guide Template

Use this style guide to document and lock down your AI character's visual identity. Keep these tokens and values identical across all generation sessions to prevent face drift.

---

## 1. Core Character Profile
* **Character Name:** ________________________  
* **Age & Gender:** ________________________  
* **Ethnicity / Facial Structure:** [e.g., Caucasian, high cheekbones, green eyes, oval face]  
* **Hair Details:** [e.g., short brown hair, textured crop, messy side part]  

---

## 2. Text-to-Image Generation Prompt Anchors
*Use these exact prompts as the baseline prefix for every scene generation.*

* **Physical Face Description (The Identity Token):**  
  > `"A close-up portrait of [Name], a [Age]-year-old [Gender] with [Hair Details], [Facial Details]..."`
* **Clothing / Wardrobe Anchor:**  
  > `"wearing a [Color] [Garment type, e.g. wearing a dark blue crewneck sweater]..."`
* **Aesthetic / Lighting Anchor:**  
  > `"cinematic office background, out of focus warm ambient lighting, 35mm film photography, photorealistic, 8k..."`
* **Locked Seed (if applicable):** Seed value: `__________________`

---

## 3. Scene Setting Matrix
Track your character's appearances across different backgrounds to maintain visual cohesion:

| Scene # | Location / Background | Wardrobe | Camera Angle | Reference Image URL / File |
|---|---|---|---|---|
| **01** | Modern corporate office | Dark blue sweater | Medium close-up | `examples/avatar-anchor.jpg` |
| **02** | Moody home office | Dark blue sweater | Close-up profile | |
| **03** | Minimalist cafe | Dark blue sweater | Wide shot | |
