# Stock Agency Submission & FTP Upload Guide

Use this step-by-step submission guide to upload batch AI stock assets to Adobe Stock, Freepik, and Wirestock.

---

## 📤 Stock Agency Upload Specifications

### 1. Adobe Stock Contributor Portal
* **Min Resolution:** 4 Megapixels (e.g., 2400 × 1600 px). Recommended: **4000 × 2667 px (10.6 MP)**.
* **File Format:** JPEG (.jpg) with maximum quality settings (Quality 10-12).
* **AI Disclosure Mandate:** Select **"Created using Generative AI tools"** -> Check **"People and Property are fictional"** (eliminates model release requirement).

### 2. Freepik Premium Contributor
* **Min Resolution:** 2000 px on the shortest side.
* **Batch Size:** Minimum 10 assets per initial submission batch.
* **File Naming Standard:** Lowercase with underscores (`corporate_handshake_01.jpg`).

---

## 🌐 FTP Batch Upload Configuration (Adobe Stock)

Use an FTP client (FileZilla or Cyberduck) to upload 100+ files instantly without browser upload limits:

```yaml
FTP_Configuration:
  Host: "ftp.adobestock.com"
  Port: 21 (or 22 SFTP)
  Username: "[Your Adobe Stock Contributor ID]"
  Password: "[Generated FTP Password from Adobe Contributor Settings]"
  Upload_Directory: "/"
```

---

## ⚡ 5-Point Pre-Submission Rejection Audit

1. **100% Zoom Crop Inspection:** Inspect pupils, fingers, and text areas for bizarre AI distortions.
2. **Copy Space Verification:** Confirm image contains clean area for buyers to add text headlines.
3. **Trademark Scrub:** Verify zero brand logos (Apple, Nike, Samsung, car hood ornaments) are visible.
4. **Metadata Density:** Ensure at least 30 relevant IPTC keywords are embedded in each file's metadata.
5. **Color Space:** Exported in **sRGB** color space to prevent color shift on contributor portal previews.
