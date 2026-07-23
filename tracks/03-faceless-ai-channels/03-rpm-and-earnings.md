# Honest RPM & Earnings Math

> Views are vanity; profit margins are sanity.

**Track:** Faceless AI Channels  
**Time:** ~35 minutes  
**Prerequisites:** Niche Selection & Script Pipeline, Duration-Matched Narration & Pacing  

## The Problem

Social media is full of "gurus" sharing screenshots of YouTube dashboards showing $10,000/month in earnings from faceless channels. What they rarely show are the operational costs behind those earnings: the money spent on AI API credits, video editing subscriptions, thumbnail design, and the fact that most of their views are on Shorts, which pay pennies.

If you jump in blindly, you might build a channel that generates 1 million views a month but only earns $50 in AdSense because it is in a low-value niche (like meme compilations). If your monthly subscription costs for ElevenLabs, Canva, and video generators total $120, **you are running a business at a loss** despite having millions of views.

To run a channel like a real business, you need to understand the exact math behind RPM (Revenue Per Mille), factor in generation expenses, and target monetization funnels that don't rely solely on AdSense payouts.

## The Concept

The financial health of your channel is determined by two main factors: **RPM** and **COGS (Cost of Goods Sold)**.

### 1. The RPM Discrepancy:
* **CPM (Cost Per Mille):** The amount advertisers pay to show ads on your videos per 1,000 views.
* **RPM (Revenue Per Mille):** The net amount *you* receive per 1,000 views after the platform takes its cut. YouTube takes **45%** of long-form ad revenue and **55%** of Shorts ad revenue.
* **Format Impact:** Long-form videos (videos over 8 minutes) allow mid-roll ads, pushing RPMs to $5–$25. Short-form videos (Shorts/Reels) draw from a shared creator pool, resulting in a microscopic RPM of **$0.02 to $0.06** per 1,000 views.

### 2. The COGS of AI Video:
Every video you generate carries a marginal cost:
```
Cost per Video = LLM Script Cost + TTS Audio Cost + Video Generator Credit Cost
```
If you spend $0.50 in API credits to produce a Short, and it gets 5,000 views on YouTube Shorts earning $0.04 RPM, the video earns $0.20. You have lost $0.30 on that upload. To turn a profit on low-RPM short-form video, you must convert those views into **direct sales** (affiliate link clicks, newsletter signups, or digital product sales).

---

## Do It

### Step 1: Research Real CPM Ranges
Go to Google Keyword Planner. Type in keywords related to your niche. Look at the "Top of Page Bid" range.
* High bids (e.g. $5.00+ CPC for "Business Liability Insurance") mean high CPM.
* Low bids (e.g. $0.10 CPC for "Funny cats") mean low CPM.

### Step 2: Establish Your Monthly Operational Budget
List all your monthly recurring subscriptions and API credit packages. Log them in the [`templates/channel-profitability-calculator.md`](templates/channel-profitability-calculator.md). Keep your software stack lean during the startup phase.

### Step 3: Calculate Your Production Cost per Video
Track your actual API consumption. For a 60-second video:
* **Script (LLM):** ~0.05 credits
* **Narration (TTS):** ElevenLabs text generation (~1,000 characters) = ~$0.15
* **Video Generation:** muapi video generation credits (e.g. Seedance 2) = ~$0.50
* **Total Cost per Video:** **$0.70**

### Step 4: Map Your Monetization Ladder
Calculate how many views you need to secure a digital product conversion. If you convert **0.1%** of viewers into email subscribers (1 in 1,000 views), and you convert **2%** of subscribers into a $27 product sale (1 in 50 subscribers), then every 50,000 views yields one digital sale ($27) plus some AdSense. This is the math that makes channels profitable.

---

## Worked Example

<p align="center">
<img src="templates/examples/faceless-finance-niche.jpg" alt="Finance Niche Studio" width="280">
<img src="templates/examples/faceless-finance-clip.gif" alt="Finance Channel Video Motion (I2V)" width="280">
</p>
<p align="center"><sub>High-RPM Finance Studio Image (Left) ──► Image-to-Video Motion (Right) · Video File: <a href="templates/examples/faceless-finance-clip.mp4">templates/examples/faceless-finance-clip.mp4</a></sub></p>

**Profitability Comparison: Niche & Format Optimization**



### Scenario A: General Gaming Channel (Shorts-Only)
* **Monthly Views:** 1,000,000 views (Shorts)
* **Niche RPM:** $0.04
* **AdSense Earnings:** `(1,000,000 / 1000) * 0.04` = **$40**
* **Expenses:** ElevenLabs + CapCut + Video credits = **$75**
* **Net Monthly Profit:** **-$35** (Loss)

### Scenario B: SaaS Automation Channel (Shorts + Digital Funnel)
* **Monthly Views:** 100,000 views (Shorts)
* **Niche RPM:** $0.05
* **AdSense Earnings:** `(100,000 / 1000) * 0.05` = **$5**
* **Direct Sales (Lead Magnet funnel):** 100 signups -> 5 sales of a $27 automation template = **$135**
* **Expenses:** LLM script + ElevenLabs + muapi Video credits = **$45**
* **Net Monthly Profit:** **$95** (Profit)

**The Lesson:** Even with 10 times fewer views, Scenario B is profitable because the niche demographic converts into high-margin digital product sales, overriding low short-form AdSense payouts.

---

## Compare Tools

| Platform / Tool | Cost Reporting Capabilities | Best for |
|---|---|---|
| **Google AdSense Analytics** | Real-time AdSense RPM reporting, country breakdowns, and ad type performance. | Tracking long-form ad earnings. |
| **Whop / Gumroad Dashboard** | Conversion rate tracking, email capture, gross sales, and net payouts after transaction fees (approx. 5-10%). | Tracking digital product and community sales. |
| **Muapi Wallet Log** | Precise credit-by-credit usage logging per generation task. | Tracking exact production costs. |

AdSense analytics show only ad revenue. To run a profitable business, you must combine AdSense data, merchant account payouts (Stripe/PayPal), and API expense logs into a single master spreadsheet like the profitability calculator template.

---

## Launch It

**How to set up your accounting:**
* **Separate Wallet:** Open a separate bank or PayPal account specifically for your channel. Route all affiliate and digital product income there, and pay for all API credits from the same account. This makes tracking your net monthly margins simple.
* **Affiliate Disclosures:** Platforms require clear disclosures. In your video description, add: *"Disclosure: Some links in this description are affiliate links, meaning I earn a commission at no extra cost to you."*

---

## Exercises

1. **Easy:** Research the CPC bids for three keywords in the Finance niche and three keywords in the Humour/Meme niche. Write down the difference.
2. **Medium:** Fill out the Channel Profitability Calculator for a hypothetical channel getting 50,000 views, producing 15 videos a month, and selling one $47 digital product.
3. **Hard:** Project the financial layout for a channel transition from Shorts-only to a hybrid layout (2 long-form videos per month, 15 Shorts). Calculate how the change in RPM affects net profit margins.

---

## Templates

* [`templates/channel-profitability-calculator.md`](templates/channel-profitability-calculator.md) — a monthly audit sheet for views, direct sales, software costs, and net margins.

---

[← Duration-Matched Narration & Pacing](02-narration-and-pacing.md) · Next: [Scaling to Multiple Channels →](04-scaling-channels.md)
