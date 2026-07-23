# Pricing & Passive-Income Math for POD

> Master unit economics, marketplace listing fees, and conversion math to build a profitable POD catalog.

**Track:** AI Print-on-Demand & Merch Design  
**Time:** ~35 minutes  
**Prerequisites:** [01: Designing Sellable AI Art](01-designing-sellable-ai-art-for-merch.md), [02: POD Platform Basics](02-print-on-demand-platform-basics.md), [03: Building a Catalog](03-building-a-catalog-without-repeating.md)  

## The Problem

Many POD sellers generate sales but end up **losing money** at the end of the month. They price t-shirts at $19.99 without accounting for hidden platform fees:
* Etsy listing fees ($0.20 per listing).
* Etsy payment processing fees (6.5% transaction fee + 3% + $0.25 payment fee).
* Print supplier base garment costs ($9.50) + shipping ($4.75).
* Ad spend or marketing costs ($2 - $5 per sale).

After subtracting all costs, a $19.99 shirt nets a negative profit margin. You need an exact mathematical pricing model to ensure every sale yields a healthy **$7 to $12 net profit**.

> **Note on Etsy fees:** Etsy charges a $0.20 listing fee, a 6.5% transaction fee on the sale price, and a ~3% + $0.25 payment processing fee. Combined, this totals roughly **9.5–10% of your retail price** — which is what the model below uses.

---

## The Concept

The POD Profit Formula determines net profit per unit sold:

$$\text{Net Profit} = \text{Retail Price} - (\text{Print Supplier Cost} + \text{Shipping}) - \text{Marketplace Fees} - \text{Ad Spend}$$

### Unit Economics Breakdown (Example T-Shirt):

```
Retail Sale Price:           $24.99
-----------------------------------
Printify Base Garment Cost:  -$9.25
Shipping Cost:               -$4.75
Etsy Fees (~10% total):      -$2.50
-----------------------------------
NET PROFIT PER SALE:          $8.49 (34% Net Margin)
```

---

## Do It

### Step 1: Benchmark Base Supplier Costs
Open [`templates/pod-pricing-calculator.md`](templates/pod-pricing-calculator.md). Input base production and shipping costs for your core products:
* **T-Shirt (Bella+Canvas 3001):** $9.25 print + $4.75 shipping = **$14.00 Base**.
* **Ceramic Mug (11oz White):** $4.50 print + $5.00 shipping = **$9.50 Base**.
* **Heavyweight Hoodie (Gildan 18000):** $18.50 print + $7.50 shipping = **$26.00 Base**.

### Step 2: Set Target Retail Prices for 35%+ Net Margins
* Set T-Shirt Retail Price to **$24.99** (Net Profit: **$8.49**).
* Set Ceramic Mug Retail Price to **$17.99** (Net Profit: **$6.69**).
* Set Heavyweight Hoodie Retail Price to **$44.99** (Net Profit: **$14.49**).

### Step 3: Run the Catalog Revenue Projection
Calculate passive monthly income based on catalog size and average store conversion rates (1.5% - 2.5%):
* **Catalog Size:** 100 Active Listings.
* **Monthly Store Views:** 10,000 visitors.
* **Orders (2.0% Conversion Rate):** 200 sales/month.
* **Monthly Net Profit (200 sales × $8.50 avg profit):** **$1,700 / month passive income**.

---

## Worked Example

**30-Day Financial Performance of "Urban Vector Merch Studio"**

* **Active Catalog:** 120 POD listings across Etsy & Shopify.
* **Total Units Sold:** 340 t-shirts, mugs, and hoodies.
* **Gross Revenue:** **$8,650.00**.
* **Supplier Production & Shipping (Printify):** -$4,620.00.
* **Marketplace & Payment Fees:** -$865.00.
* **Etsy Ads Spend:** -$650.00.
* **Net Monthly Profit:** **$2,515.00** (29.1% Net Profit Margin).

---

## Compare Tools

| Financial Tool | Purpose | Key Metric Tracked |
|---|---|---|
| **Etsy / Shopify Analytics** | Conversion tracking & traffic sources | Conversion Rate & AOV |
| **Printify Profit Calculator** | Instant COGS and shipping estimation | Gross Margin % |
| **Google Sheets / Excel Matrix** | Net profit modeling after fees & ads | Monthly Net Income |

---

## Launch It

* **Offer Free Shipping by Bundling:** Include shipping in the retail price (e.g., price shirt at $28.99 with "FREE SHIPPING") to increase Etsy search rank and buyer conversion rates.

---

## Exercises

1. **Easy:** Calculate the net profit for a ceramic mug priced at $18.99 with a base cost of $4.50 and shipping of $5.00.
2. **Medium:** Use your pricing sheet to model a 50-product catalog generating 50 sales per month.
3. **Hard:** Set up a dynamic pricing matrix accounting for 10% Etsy ad spend while maintaining an $8.00 minimum profit per sale.

---

## Templates

* [`templates/pod-pricing-calculator.md`](templates/pod-pricing-calculator.md) — Dynamic profit spreadsheets, platform fee formulas, and COGS benchmarks.

---

[← Building a Catalog](03-building-a-catalog-without-repeating.md) · [Track Overview](README.md)
