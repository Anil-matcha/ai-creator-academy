# Virtual Try-On Specification Sheet

Use this template to specify the garment and model parameters for running virtual try-on generations.

## 1. Garment Parameters
* **Garment Name:** e.g., Classic Linen Button-Down Shirt
* **Category:** [x] Tops / [ ] Bottoms / [ ] Outerwear / [ ] Full Dress
* **Material/Texture:** Light-woven organic flax linen.
* **Color Spec:** Off-white / Cream `#F5F2EB`.
* **Garment Source Photo:** `raw_garment_01.png` (isolated transparent flat-lay or ghost mannequin photo).

## 2. Target Model Demographics
* **Gender/Presentation:** e.g., Male / Masculine
* **Age Range:** e.g., 25 - 35
* **Ethnicity Profile:** e.g., East Asian
* **Body Type:** [ ] Slim / [x] Athletic / [ ] Curvy / [ ] Big & Tall

## 3. Mask & Composition Details
* **Inpaint Mask Strategy:** [x] Keep face and skin, replace clothing / [ ] Keep clothing, swap model face/body
* **Draping Fitting Rate:** `0.75` (high similarity to original garment folds).
* **Collar Detail Preservation:** [x] Keep open collar / [ ] Buttoned up

## 4. Operational Run Log

| Run # | Model Prompt | Fit Rating (1-10) | Fabric Texture Rating | Bounding Box Alignment | Notes |
|:---:|---|---|---|---|---|
| 1 | "East Asian male model, athletic build..." | 8/10 | 9/10 | Center | Natural fold lines |
| 2 | "Same model, standing in studio..." | 9/10 | 9/10 | Center | Shadow matches |
| 3 | | | | | |
