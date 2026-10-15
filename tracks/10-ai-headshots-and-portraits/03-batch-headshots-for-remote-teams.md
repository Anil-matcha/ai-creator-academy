# Batch Headshots & Bulk Automation for Remote Teams

> Scale from individual portraits to processing 50+ remote employee headshots in a single automated batch run.

**Track:** AI Headshots & Portraits  
**Time:** ~40 minutes  
**Prerequisites:** [01: Consistent Headshot Generation](01-consistent-headshot-generation.md), [02: Standing Out Against Fiverr Competition](02-standing-out-against-fiverr-competition.md)  

## The Problem

When scaling your headshot agency to handle enterprise clients, manual processing becomes a bottleneck. A company with **50 remote employees** across 6 countries sends you 150+ raw selfies.

If you open each selfie in an editor, manually type prompts, run inference one-by-one, and organize folders individually, processing 50 employees takes **over 12 hours of repetitive manual work**.

To service high-ticket corporate contracts efficiently, you need an automated **Bulk CSV Ingestion & Batch Rendering Pipeline**.

---

## The Concept

The **Batch Headshot Automation Pipeline** processes multi-employee rosters systematically:

```
CSV Roster + Selfie Directory ──► Automated Identity Vector Extraction ──► Batch Inpainting & Background Sync ──► Auto-Folder Zip Generation
```

### Core Automation Pillars:

1. **Batch CSV Roster Ingestion:** Reading a master CSV file (`employee_id, full_name, role, dress_code, selfie_path`).
2. **Automated Facial Alignment & Pre-Cropping:** Running face-detection scripts (OpenCV / MediaPipe) to auto-crop selfies to a standardized square aspect ratio before feeding them to identity models.
3. **Unified Brand Background Injections:** Pre-loading a fixed corporate background asset (e.g., modern glass office or studio grey gradient) across all 50 renders so every team member shares an identical background composition.

---

## Do It

### Step 1: Prepare the Master Employee Roster CSV
Open [`templates/b2b-headshot-proposal.md`](templates/b2b-headshot-proposal.md). Create a batch input CSV file `team_roster.csv`:

```csv
EmployeeID,FullName,Title,DressCode,SelfieFile
EMP001,John Doe,VP of Engineering,Executive Suit,selfies/john_doe.jpg
EMP002,Sarah Jenkins,Lead Designer,Creative Blazer,selfies/sarah_j.jpg
EMP003,Alex Rivera,Senior Developer,Tech Sweater,selfies/alex_r.jpg
```

### Step 2: Run Batch Face-Detection & Auto-Cropping
Run a Python pre-processing script to detect face bounding boxes in `selfies/`, auto-cropping each image with a 35% margin above the head and 1:1 aspect ratio.

### Step 3: Execute Batch Inference via API Loop
Run your batch script calling muapi `/nano-banana-2` (or InstantID endpoint) in a loop, passing each employee's identity vector and target dress code prompt while locking the corporate background seed.

### Step 4: Auto-Package into Client Zip Bundles
Generate employee subfolders containing `[FullName]_linkedin.jpg` (1080x1080px) and `[FullName]_website.jpg` (2400x3000px). Compress all folders into a master client deliverable `Apex_Financial_Team_Headshots.zip`.

---

## Worked Example

<p align="center">
<img src="templates/examples/corporate-executive-headshot.jpg" alt="Batch Processed Corporate Headshot" width="320">
</p>
<p align="center"><sub>Batch Processed Corporate Team Asset (Unified Brand Background & Studio Lighting)</sub></p>

**Batch Processing Performance for "Summit Cloud Systems" (42 Employees)**

* **Input:** 42 employee selfies uploaded via self-serve intake portal.
* **Batch Processing Time:** 18 minutes automated script execution.
* **Deliverable:** 42 organized employee folders with 3 high-res renders each (126 total image files).
* **Labor Time:** 12 minutes setup & quality review (vs. 10+ hours manual labor).
* **Contract Revenue:** **$840.00** ($20/person).
* **API Compute Cost:** **$2.52** total credit cost.

---

## Compare Tools

| Platform / Tool | Automation Capability | Identity Consistency | Best For |
|---|---|---|---|
| **muapi Batch API + Python** | Ultra-High (Folder-wide script execution, auto-zip output) | High (InstantID vector embedding per employee) | High-volume corporate team contracts (25–100+ employees) |
| **InstantID / FLUX PuLID (local)** | Medium (Manual batch queue via ComfyUI) | Maximum (Highest identity fidelity) | Premium executive packages where top-tier accuracy is critical |
| **Typeform + Zapier Automation** | High (Auto-routes intake form submissions to processing queue) | N/A | Client-facing intake portals for self-serve employee photo uploads |

---

## Launch It

**Pricing for batch corporate packages:**
* **Per-Seat Add-On Rate:** Charge **$20 – $25 per additional employee** beyond the base package tier (e.g., a 35-person team on the $799 Corporate Standard package: 25 included + 10 add-ons × $20 = **$999 total**).
* **Automate Quality Audits:** Write a quick script to check output resolution and file size automatically before zipping, ensuring no corrupt or under-sized renders are sent to the client.

---

## Exercises

1. **Easy:** Create a CSV roster file for 5 hypothetical employees with names, titles, and dress code tags.
2. **Medium:** Write a Python script to auto-crop 5 selfies to 1:1 aspect ratio centered on face landmarks.
3. **Hard:** Run a batch script generating 5 employee headshots with a unified studio background.

---

## Templates

* [`templates/b2b-headshot-proposal.md`](templates/b2b-headshot-proposal.md) — Batch CSV schemas, automated folder naming standards, and team packaging guides.

---

[← Standing Out Against Fiverr Competition](02-standing-out-against-fiverr-competition.md) · Next: [Creative Headshots & Stylized Portraits →](04-creative-headshots-and-stylized-portraits.md)
