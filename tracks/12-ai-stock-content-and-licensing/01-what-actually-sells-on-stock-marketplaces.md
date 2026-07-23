# What Actually Sells on Stock Marketplaces

> Identify high-demand commercial stock niches and generate licensable visual assets that buyers actually download.

**Track:** AI Stock Content & Licensing  
**Time:** ~40 minutes  
**Prerequisites:** None  

## The Problem

The stock photography market is overflowing with generic AI images: fantasy landscapes, futuristic cyber cities, and random aesthetic portraits. Beginners upload thousands of these generic images to Adobe Stock or Shutterstock, only to make **$0.00 in total royalties**.

Marketplace buyers (ad agencies, news editors, corporate design teams, and marketing agencies) are not looking for art—they are looking for **commercial concepts that illustrate specific business problems**:
* Business professionals shaking hands on a deal.
* Renewable energy solar farm installations.
* Diverse healthcare workers discussing patient charts.
* Cyber security data breach concepts.

If you generate pretty art without a commercial use-case, your images sit at the bottom of marketplace search results forever.

---

## The Concept

The AI stock licensing pipeline relies on **Commercial Trend Analysis**, **IPTC Metadata Tagging** (IPTC = International Press Telecommunications Council — the industry-standard schema for embedding titles, keywords, and copyright fields inside an image file), and **Property Release Compliance**:

```
Commercial Demand Search ──► Concept Prompting ──► Quality Audit & Upscale ──► IPTC Keywording ──► Marketplace Submission
```

### The 4 Commercial Stock Demand Pillars:

1. **High-Demand Commercial Categories:**
   * **Business & Corporate:** Team meetings, office handshakes, remote video calls, executive presentations.
   * **Technology & Cyber Security:** Server rooms, AI cloud computing, data security, biometric authentication.
   * **Healthcare & Wellness:** Medical research, doctor-patient trust, mental health therapy, biotechnology labs.
   * **Green Energy & Sustainability:** Wind turbines, electric vehicle charging, solar panels, sustainable architecture.
2. **Copy Space (Negative Space for Text Overlay):** Stock buyers need room to add headlines, logos, and promotional text. Images with clean, uncluttered backgrounds (e.g., negative space on the left or top 30% of the frame) sell 4x more frequently than busy, cluttered compositions.
3. **No Trademark / Brand Artifacts:** Stock agencies reject images containing recognizable brand logos (Apple, Nike, BMW), trademarked architecture, or copyrighted artwork.

---

## Do It

### Step 1: Research Trending Keywords on Adobe Stock Insights
Open Adobe Stock Contributor Portal. Check the monthly **"Demand Trends Brief"** for missing or high-conversion commercial search terms (e.g., *"diverse executive handshake modern office"*).

### Step 2: Assemble the Stock Prompt with Copy Space
Open [`templates/stock-metadata-template.md`](templates/stock-metadata-template.md). Draft a commercial stock prompt with copy space:
* **Prompt:**  
  > `"Photorealistic 8k commercial stock photo of two diverse business executives shaking hands across a glass conference table in a sunlit modern corporate office, copy space on left side for text overlay, shot on 35mm lens, neutral corporate color palette, high resolution."`
* **Negative Prompt:**  
  > `"brand logos, watermarks, text, cartoon, 3d render, extra fingers, distorted hands, blurry, oversaturated."`

### Step 3: Inspect for Artifacts at 100% Zoom
Before submitting to stock portals, inspect key details:
* **Hand & Finger Geometry:** Ensure handshakes contain exactly 5 fingers per hand without warping.
* **Eye Reflection & Catchlights:** Confirm pupils are round and clear.

### Step 4: Add IPTC Metadata (Title, Keywords, Categories)
Use an IPTC editor (ExifTool or stock tagger) to embed 30+ targeted commercial keywords (e.g., *agreement, partnership, deal, handshake, business, corporate, executive, meeting, office, teamwork, trust*).

---

## Worked Example

<p align="center">
<img src="templates/examples/corporate-handshake-stock.jpg" alt="Corporate Handshake Commercial Stock Photo" width="480">
<img src="templates/examples/stock-catalog-motion.gif" alt="Stock Catalog Video Motion (I2V)" width="480">
</p>
<p align="center"><sub>Commercial Stock Photograph (Left) ──► Image-to-Video Stock Motion Clip (Right) · Video File: <a href="templates/examples/stock-catalog-motion.mp4">templates/examples/stock-catalog-motion.mp4</a></sub></p>

**Stock Asset Performance Analysis for "Corporate Handshake Concept"**

* **Marketplace:** Adobe Stock & Freepik.
* **Category:** Business / Finance / Corporate Partnership.
* **Metadata Tags:** 38 commercial keywords + copy space tag.
* **Downloads:** 142 licensing downloads in 90 days.
* **Royalty Revenue:** **$142.00** passive recurring earnings from 1 single image render.

---

## Compare Tools

| Stock Marketplace | AI Image Acceptance | Royalty Structure | Best For |
|---|---|---|---|
| **Adobe Stock** | **Accepted** (requires AI tag) | 33% per download ($0.33 to $9.90+) | Highest revenue per download |
| **Freepik Premium** | **Accepted** | Pay-per-download pool (~$0.05 to $0.15) | High volume downloads |
| **Shutterstock** | Restricted (In-house AI only) | Varies | Non-AI stock submission |

---

## Launch It

* **Tag Your Uploads Correctly:** Always check the **"Created using Generative AI tools"** box when uploading to Adobe Stock. Hiding AI origin risks account suspension.

---

## Exercises

1. **Easy:** Research 3 trending commercial search terms on Adobe Stock.
2. **Medium:** Generate a commercial stock photo featuring copy space for headlines.
3. **Hard:** Tag your image with 30+ commercial IPTC keywords and submit it to a stock contributor portal.

---

## Templates

* [`templates/stock-metadata-template.md`](templates/stock-metadata-template.md) — Metadata tagging schemas, copy space guides, and agency submission checklists.

---

[Track Overview](README.md) · Next: [Batch-Generating a Licensable Catalog →](02-batch-generating-a-licensable-catalog.md)
