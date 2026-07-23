# Batch-Generating a Licensable Catalog

> Build a 500+ asset stock catalog using automated prompt batching, AI upscaling, and CSV metadata tagging.

**Track:** AI Stock Content & Licensing  
**Time:** ~40 minutes  
**Prerequisites:** [01: What Sells on Stock Marketplaces](01-what-actually-sells-on-stock-marketplaces.md)  

## The Problem

Stock licensing is a **volume numbers game**. Earning $500 to $2,000+ per month in passive royalties requires a portfolio of **500 to 2,000+ high-quality commercial assets**.

Generating, upscaling, keywording, and uploading images one by one takes 15 minutes per image. Manually publishing 500 images at that rate would take over 125 hours of tedious manual labor.

Without a batch automation workflow, creators quit before reaching the catalog size necessary to unlock compounding passive income.

---

## The Concept

The **Automated Stock Factory Pipeline** processes images in bulk:

```
Batch Prompt Matrix ──► Automated Generation ──► 4x Upscale Pipeline ──► Auto-CSV Metadata Tagging ──► FTP Batch Upload
```

### Automation Pillars:

1. **Batch API Generation:** Calling `/nano-banana-2` via Python scripts to generate 50 images in a single run.
2. **Bulk AI Upscaling:** Processing raw 1024px images through batch upscalers to reach **4000px+ (12+ Megapixels)** required by stock agencies.
3. **CSV Metadata Ingestion:** Stock portals (like Adobe Stock and Freepik) accept CSV files containing `filename, title, keywords, category`, eliminating manual text entry.

---

## Do It

### Step 1: Create a Batch Prompt Array
Open [`templates/stock-metadata-template.md`](templates/stock-metadata-template.md). Define a prompt matrix targeting commercial technology concepts:
* `"Photorealistic 8k commercial stock photo of [TECH_CONCEPT], blue fiber optic illumination, clean high-tech server room background, widescreen 16:9, copy space."`
* Substitute `[TECH_CONCEPT]` with: `AI cloud data server`, `biometric facial scanner`, `cyber security firewall node`, `quantum computer processor`.

### Step 2: Run Batch API Script
Run your generation script to output 20 high-res stock images into an `output_raw/` directory.

### Step 3: Batch Upscale & Inspect
Pass all images through an AI upscaler to reach 4000px+ resolution. Filter out any renders with visual glitches or hand distortions.

### Step 4: Auto-Generate CSV Metadata & Upload via FTP
Generate a `metadata.csv` file mapping titles and 30 keywords to each file. Upload the batch via FTP directly to Adobe Stock Contributor Portal.

---

## Worked Example

<p align="center">
<img src="templates/examples/future-technology-stock.jpg" alt="Future Technology Commercial Stock Photo" width="480">
</p>
<p align="center"><sub>Commercial High-Tech Stock Photograph (Batch Catalog Asset)</sub></p>

**Batch Campaign Results for "Cyber Security & Tech Collection"**

* **Assets Generated:** 100 high-tech commercial stock images.
* **Batch Processing Time:** 45 minutes automated execution.
* **Uploaded Catalog:** 88 approved images (88% acceptance rate on Adobe Stock).
* **Monthly Performance:** 215 downloads generating **$236.50/month** in recurring royalties.

---

## Launch It

* **Maintain High Acceptance Rates:** Keep your approval rate above 80% on Adobe Stock by thoroughly checking 100% zoom crop for noise artifacts before uploading.

---

## Exercises

1. **Easy:** Create a CSV metadata template mapping titles and keywords for 5 stock photos.
2. **Medium:** Batch generate 10 commercial stock photos targeting the renewable energy niche.
3. **Hard:** Set up FTP auto-upload for batch submitting 25 stock assets to a contributor portal.

---

## Templates

* [`templates/stock-metadata-template.md`](templates/stock-metadata-template.md) — Batch CSV schemas, keyword tagging libraries, and FTP upload guides.

---

[← What Actually Sells](01-what-actually-sells-on-stock-marketplaces.md) · Next: [Licensing Models & Passive-Income Expectations →](03-licensing-models-and-passive-income.md)
