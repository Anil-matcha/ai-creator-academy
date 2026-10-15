# Batch Catalog Processing Spec

Use this specification log to organize, track, and scale batch catalog generation for e-commerce catalogs.

## 1. Directory Structure Blueprint

Configure your project folders:
```
[project-root]/
├── 01_raw_assets/        # Raw product photo uploads
├── 02_isolated_masks/    # Output png files after background removal
├── 03_ai_backgrounds/    # Generated environment backdrop images
├── 04_composite_drafts/  # Draft composite renders
└── 05_final_deliver/     # Color-graded, scaled final WebP assets
```

## 2. Bounding Box & Aspect Ratio Mapping

For consistent layouts, define standard padding sizes inside the frame:
* **Amazon Hero standard:** Square format (1:1), product occupies exactly **85%** of frame height.
* **Shopify / WooCommerce gallery standard:** Vertical format (4:5), product centered with **10%** bottom padding.

## 3. Bulk Processing Log

Track generations across large catalogs:

| Product SKU | Raw File Path | Isolated Mask Status | Target Backdrop Prompt ID | Composite Render Status | QC Status | Export Path |
|---|---|:---:|:---:|:---:|:---:|---|
| SKU-BOT-01 | `01_raw/bot_01.jpg` | ✅ Done | BGD-TRAVERTINE-01 | ✅ Done | ✅ Pass | `05_final/sku_bot_01.webp` |
| SKU-BOT-02 | `01_raw/bot_02.jpg` | ✅ Done | BGD-TRAVERTINE-01 | ✅ Done | ✅ Pass | `05_final/sku_bot_02.webp` |
| SKU-JAR-01 | `01_raw/jar_01.jpg` | ❌ Pending | BGD-MARBLE-02 | ⬜ Out of sync | ⬜ Fail | |
| | | | | | | |
