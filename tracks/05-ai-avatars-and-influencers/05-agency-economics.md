# Agency Case Study: Small-Team Economics

> Don't build an audience for yourself; build and manage audiences for paying clients.

**Track:** AI Avatars & Influencers  
**Time:** ~30 minutes  
**Prerequisites:** Building a Consistent AI Character, Character to Content Pipeline, Voice Cloning & Dialogue, Monetization Tiers by Follower Count  

## The Problem

Launching your own virtual influencer from scratch is slow. You have to build an audience, optimize scripts, post daily, and wait for sponsorships to roll in. During this 6-month ramp-up phase, you have zero cash flow, but your monthly subscriptions and API bills keep arriving.

A faster, more predictable way to make a full-time income is running a **Virtual Influencer Agency (VIA)**.

Instead of building an audience for yourself, you **build, manage, and animate virtual spokespeople on behalf of existing corporate clients**. Companies (SaaS startups, law firms, accounting practices) need human faces to explain their products, but their founders are too busy or camera-shy to record videos themselves. They will gladly pay an agency an upfront monthly retainer to handle it for them.

## The Concept

The economics of a Virtual Influencer Agency (VIA) are built on a **Management Retainer Contract**:

```
Client Retainer ($2,000/mo)  ──►  Upfront Invoice settled  ──►  Agency delivers 15 Videos/mo
```

To run a profitable VIA:
* **The Spokesperson Retention Agreement:** You structure a contract using the [`templates/influencer-agency-agreement.md`](templates/influencer-agency-agreement.md) detailing the scope of work, monthly volume, and payment schedules.
* **IP Separation:** You clearly define who owns the underlying assets. The industry standard is that the **Agency owns the engine files** (prompt guides, model seeds, and voice clone credentials), while the **Client owns the distribution rights to the completed video exports**. This protects your intellectual property and ensures client lock-in.
* **Vocal & Visual Sync:** You charge a premium because you manage the entire pipeline (visual consistency, lip-sync rendering, and voice synthesis) under a unified service.

---

## Do It

### Step 1: Customize Your Service Contract
Open the [`templates/influencer-agency-agreement.md`](templates/influencer-agency-agreement.md). Define the monthly fee (**$1,500–$2,500/month** is standard for micro-agencies) and the volume (typically 15 vertical clips per month).

### Step 2: Pitch B2B Professional Services
Reach out to service-based firms that need content marketing:
* Bookkeeping/Accounting firms (explaining tax write-offs).
* Recruiting agencies (explaining job interview tips).
* Local real estate brokerages (explaining buying guides).
Highlight that they don't need to show their face on camera or spend hours recording audio.

### Step 3: Conduct the Character Briefing Session
Upon securing the contract, run a briefing session. Agree on the character's age, look, style, and voice profile (e.g. *"professional HR advisor in her 30s, warm and clear voice"*). Create the visual seed guidelines.

### Step 4: Run the Weekly Batch Station
Manage deliveries in weekly batches (4 videos every Friday).
* Write the scripts and get client approval via email.
* Batch-generate the cloned voice audio.
* Run the static avatar image and voice tracks through the `/sync-lipsync` API.
* Trim, subtitle, and color-grade the exports.

### Step 5: Deliver to Shared Folders
Upload the finished files to the client's shared folder. Send a notification: *"Batch 2 is ready in your folder. Let us know if you need any adjustments by Monday."*

---

## Worked Example

**Virtual Spokesperson Campaign for "HireFast" (Recruiting SaaS)**

* **The Client:** A recruiting software startup.
* **The Deal:** **$2,000/month** retainer.
* **The Deliverables:** 15 vertical video tips (e.g. *"how to write a resume"*).
* **The Character:** "Maya" (A virtual HR consultant, styled in business-casual clothing).
* **Monthly Agency P&L:**
  * **Retainer Income:** **$2,000.00**
  * **API Expenses:** 15 videos * $0.70/video = **$10.50**
  * **Software Subscriptions:** ElevenLabs + CapCut Pro = **$45.00**
  * **Net Agency Profit:** **$1,944.50 / month** (97% profit margin).
  * **Time Spent:** ~5 hours per month to script, generate, and edit the batch.

**The Result:** The client gets a high-performing brand spokesperson posting consistently. The agency runs a high-value service with almost zero overhead, allowing a single editor to manage up to 4 clients simultaneously ($8,000/month gross).

---

## Compare Tools

| Platform / Tool | Invoice & Payments | Deliverables Management | Client Onboarding |
|---|---|---|---|
| **Stripe Invoicing** | Safe, reliable, recurring card charges. | N/A | Sending professional corporate billing terms. |
| **Google Drive / Dropbox** | Simple, reliable, direct folder sharing. | Direct upload of large video files. | Staging raw client assets and visual templates. |
| **ClickUp / Slack** | Client task assignment and project milestones. | N/A | Complex agency operations with multiple clients. |

For small agencies, keep communication simple. Do not invite clients into complex Slack channels or project management spaces. Send monthly invoices via Stripe, manage script approvals via simple email, and deliver final files through a shared Google Drive folder.

---

## Launch It

**How to manage approval cycles:**
* **Establish a Lock-In Milestone:** In your agreement, state that once a script is approved, it cannot be modified. This prevents the client from requesting voiceover or lip-sync re-renders (which cost you API credits) after the video is compiled.
* **Re-render Fees:** If the client requests a visual revision due to a change in their script *after* approval, charge a flat **$50 re-render fee** per video to cover API credits and edit times.

---

## Exercises

1. **Easy:** Fill out the Influencer Agency Agreement template with a mock client and specify character ownership rules.
2. **Medium:** Research three local business niches. Write a 1-paragraph pitch email for a virtual spokesperson tailored specifically to one of them.
3. **Hard:** Project the monthly profit-and-loss sheet for an agency managing 3 distinct client avatars, factoring in all software subscriptions and API credits used for a 15-video/month delivery schedule.

---

## Templates

* [`templates/influencer-agency-agreement.md`](templates/influencer-agency-agreement.md) — agency service contract covering character ownership, retainers, and revisions.

---

[← Monetization Tiers by Follower Count](04-monetization-tiers.md) · [Track overview](README.md)
