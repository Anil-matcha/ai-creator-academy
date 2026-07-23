# Pricing & Selling Tools You Build With Agents

> Turn micro-tools into a recurring passive income stream using Gumroad, LemonSqueezy, and creator affiliate networks.

**Track:** AI Agents & Vibe-Coding for Creators
**Time:** ~40 minutes
**Prerequisites:** [02: Building Your First Sellable Micro-Tool](02-building-your-first-sellable-micro-tool.md), [03: The Vibe-Coding Workflow](03-vibe-coding-workflow.md)

## The Problem

Most creators who build a working micro-tool undercharge or don't charge at all. They post the tool for free on GitHub, get 200 stars, and make $0.

Others price based on gut feel — $5 because *"it's just a script"* — without understanding that buyers are paying for **time saved**, not code complexity. A script that saves 10 hours per week is worth far more than $5 regardless of how simple it looks.

Meanwhile, the minority who price correctly and list on the right platforms discover that a single well-scoped tool can generate **$500 to $3,000 in the first 30 days** from a creator audience of a few thousand.

---

## The Concept

The **Creator Tool Monetization Stack** sells through three channels simultaneously:

```
Micro-Tool ──► Direct Gumroad/LemonSqueezy Page ──► Creator Community Launch ──► Affiliate Partner Network ──► Passive Recurring Revenue
```

### The Tool Pricing Formula:

$$\text{Tool Price} = \text{Hours Saved Per Month} \times \text{Buyer's Hourly Rate} \times 0.10$$

> **Plain English:** Price your tool at roughly **10% of the monthly value it saves the buyer**. If your tool saves an Etsy seller 8 hours/month of keyword research, and their time is worth $25/hour, the tool is saving them $200/month — so charge **$20 one-time** (or $9/month if it requires ongoing API costs).

### Pricing Model Options:

1. **One-Time Lifetime License (Most Popular for Scripts):** Single payment, buyer owns the tool forever. Best for Python scripts with no ongoing server costs. Converts at 3–5x the rate of subscriptions for audiences under 10,000 followers.
2. **Monthly Subscription (Best for Tools with API Costs):** If your tool calls GPT-4 or muapi on every run, pass your API costs to the buyer via a $9–$29/month subscription. Use LemonSqueezy for subscription billing.
3. **Pay-What-You-Want with a Minimum:** Set a floor of $9 with a suggested price of $25. Gumroad supports this natively and frequently generates higher average revenue than a fixed price.

---

## Do It

### Step 1: Write Your Gumroad Product Page
Open [`templates/micro-tool-product-page.md`](templates/micro-tool-product-page.md). Fill in the product page copy following this structure:
* **Headline:** Lead with the outcome, not the tool name. Example: *"Generate 30 IPTC Keywords for Every Stock Photo in 4 Minutes"* — not *"Stock Metadata CSV Script v1.2"*.
* **The Pain:** One sentence describing the exact frustration it solves. *"Manually tagging 100 stock images takes 25+ hours. This tool does it in 4 minutes."*
* **What's Included:** List every file in the zip (script, README, sample input, requirements.txt).
* **Who It's For:** Name the exact buyer type (e.g., *"Adobe Stock and Freepik contributors who upload 50+ images per batch"*).
* **Price Anchor:** Show the time cost of the manual alternative: *"25 hours of manual tagging @ $15/hr = $375 in your time. This tool: $39 one-time."*

### Step 2: Set Up Gumroad or LemonSqueezy
* **Gumroad** (gumroad.com): Best for one-time purchases. 10% fee on free plan, 0% on $10/month paid plan. Handles global VAT automatically.
* **LemonSqueezy** (lemonsqueezy.com): Best for subscriptions or if you want a checkout embed on your own site. 5% + $0.50 per transaction.

Upload your zip, set your price, publish. The product page is live in under 10 minutes.

### Step 3: Launch to Your Existing Audience
Post in the creator communities where your target buyer already lives:
* **For POD / Etsy tools:** Post in Facebook groups ("Printify Sellers", "Etsy Print on Demand Success"), Reddit r/Etsy, and relevant Discord servers.
* **For AI image tools:** Post in Midjourney community Discord, r/StableDiffusion, and AI creator newsletters.
* **Announcement format:** Share a 60-second Loom video showing the tool running on real data — before → after. Text posts alone convert at 5–10%; video demos convert at 20–35%.

### Step 4: Set Up an Affiliate Program
Gumroad's built-in affiliate system and LemonSqueezy both support commission-based referrals. Offer **30–40% commission** to other creators who promote your tool to their audiences.
* **Target affiliates:** Creators in the same niche with 1,000–10,000 followers who don't sell their own tools yet.
* **Affiliate pitch:** *"You mention my tool once in a newsletter or video; you earn $12 every time a subscriber buys. No ongoing work."*

---

## Worked Example

**30-Day Launch Results for "Etsy SEO Title Generator"**

* **Product Price:** $29 one-time (lifetime license).
* **Launch Channel 1:** Post in 3 Etsy POD Facebook groups (8,500 combined members). Result: 23 sales in 48 hours = **$667**.
* **Launch Channel 2:** Mention in a mid-size Etsy newsletter (4,200 subscribers, affiliate @ 30%). Result: 41 referral sales × $29 × 70% = **$833 net**.
* **Ongoing organic (weeks 3–4):** Google searches for "Etsy SEO tool" and Gumroad discovery. Result: 18 more sales = **$522**.
* **Total 30-Day Revenue:** **$2,022**.
* **Total Build + Marketing Time:** 6.5 hours.
* **Effective Hourly Rate:** **$311/hour**.

---

## Compare Tools

| Platform | Best For | Fee Structure | Affiliate Support |
|---|---|---|---|
| **Gumroad** | One-time script sales, creator audiences | 10% (free) / 0% ($10/mo) | ✅ Built-in (custom %) |
| **LemonSqueezy** | Subscriptions, SaaS-style tools | 5% + $0.50 per transaction | ✅ Built-in |
| **Whop** | Discord-gated tool access, community tools | 3% per transaction | ✅ Built-in |
| **GitHub (free)** | Open-source tool lead magnets | $0 | ❌ None |

---

## Launch It

**Scaling a tool portfolio to $3,000+/month:**
* **Build 1 New Micro-Tool Per Month:** With the vibe-coding workflow from Lesson 3, a new tool takes 1–2 focused sessions. After 6 months, a portfolio of 6 tools generating an average of $300–$500/month each compounds to **$1,800–$3,000/month pure passive income**.
* **Update Existing Tools:** Release a v2.0 update every 90 days (1 new feature added by the agent in under an hour) to keep the Gumroad listing fresh and prompt existing buyers to share it again.

---

## Exercises

1. **Easy:** Fill in the Gumroad product page template for a tool you built or plan to build. Focus on the headline — write 5 variations and pick the strongest outcome-focused one.
2. **Medium:** Calculate the correct price for a tool that saves a stock photographer 6 hours per batch upload session, assuming their time is worth $20/hour.
3. **Hard:** Launch a tool (even a simple one built in the exercises from Lessons 2–3) on Gumroad at a real price, post about it in one creator community, and report your first-week results.

---

## Templates

* [`templates/micro-tool-product-page.md`](templates/micro-tool-product-page.md) — Gumroad/LemonSqueezy product page copy templates, pricing frameworks, and affiliate setup guides.

---

[← The Vibe-Coding Workflow](03-vibe-coding-workflow.md) · [Track Overview](README.md)
