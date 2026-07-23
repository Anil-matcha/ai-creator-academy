# Print-on-Demand Platform Basics

> Automate production, fulfillment, and store sync across Etsy, Shopify, and POD suppliers.

**Track:** AI Print-on-Demand & Merch Design  
**Time:** ~35 minutes  
**Prerequisites:** [01: Designing Sellable AI Art](01-designing-sellable-ai-art-for-merch.md)  

## The Problem

Creating great AI artwork is only half the battle. Setting up physical manufacturing, managing inventory, and handling shipping logistics manually can sink a merch business before it starts.

Traditional inventory models require purchasing 100+ shirts upfront in various sizes (S, M, L, XL), storing boxes in your home, and risking unsold stock if a design doesn't sell.

Print-on-Demand (POD) eliminates inventory risk by printing and shipping orders automatically when a customer buys—but setting up integration bridges between platforms (Etsy/Shopify) and suppliers (Printify/Printful) requires proper configuration.

---

## The Concept

The automated POD e-commerce workflow connects storefronts directly to fulfillment providers:

```
Customer Places Order (Etsy/Shopify) ──► Auto-Sync to Print Supplier (Printify) ──► DTG Printing & Shipping ──► Tracking Auto-Sent to Customer
```

### Core Components:

1. **Front-End Storefronts:** Etsy (built-in search traffic), Shopify (custom brand control), or Redbubble (marketplace catalog).
2. **Back-End Print Suppliers:** Printify, Printful, or Gelato. They handle **DTG (Direct-to-Garment — a process that inkjet-prints your design directly onto fabric, one item at a time, with no minimum order)** printing, quality control, packaging, and shipping.
3. **Mockup Generation:** Creating photorealistic lifestyle product photos so customers see the shirt/mug in a real-world setting.

---

## Do It

### Step 1: Connect Your POD Supplier to Your Store
Create a Printify/Printful account and link it to your Etsy or Shopify store using API OAuth.

### Step 2: Upload Your 300 DPI Transparent Graphic
Select a garment (e.g., Bella+Canvas 3001 Unisex Tee). Upload your `merch-graphic-transparent.png`. Center the graphic on the printable area.

### Step 3: Publish Lifestyle Mockups
Generate lifestyle product photos using your AI photography pipeline from [`templates/merch-prompt-brief.md`](templates/merch-prompt-brief.md) or Printify mockup tools.

### Step 4: Configure Automated Order Routing
Enable **Automatic Fulfillment** in your supplier settings so incoming store orders process without manual intervention.

---

## Worked Example

<p align="center">
<img src="templates/examples/vintage-botanical-mug-mockup.jpg" alt="Vintage Botanical Ceramic Mug Mockup" width="480">
</p>
<p align="center"><sub>AI Vintage Botanical Coffee Mug Mockup (Product Showcase)</sub></p>

**Product Listing Setup for "Botanical Wildflower Ceramic Mug"**

* **Print Supplier:** Monster Digital via Printify.
* **Product:** 11oz White Ceramic Mug.
* **Retail Price:** **$16.99**.
* **Base Production Cost:** **$4.50** + **$5.00** shipping.
* **Profit per Sale:** **$7.49** (44% Margin).
* **Fulfillment:** 100% automated upon order receipt.

---

## Compare Tools

| Platform / Supplier | Best Strengths | Fulfillment Speeds | Best For |
|---|---|---|---|
| **Printify** | Vendor network, lowest base prices | 2 - 5 business days | High-margin Etsy & Shopify stores |
| **Printful** | In-house print quality, custom branding inserts | 2 - 4 business days | Premium apparel brands |
| **Redbubble** | Built-in organic search traffic | 3 - 7 business days | Zero-setup passive catalog publishing |

---

## Launch It

* **Enable Automatic Order Backup:** Set up backup supplier routing in Printify so if one print shop runs out of stock on black L shirts, your orders automatically route to a secondary supplier.

---

## Exercises

1. **Easy:** Create a free Printify account and upload an isolated AI graphic onto a t-shirt mockup.
2. **Medium:** Connect your POD supplier to an Etsy or Shopify dev store.
3. **Hard:** Set up automated order fulfillment and test a sample order delivery.

---

## Templates

* [`templates/pod-pricing-calculator.md`](templates/pod-pricing-calculator.md) — COGS pricing models, profit margin calculators, and platform fee breakdowns.

---

[← Designing Sellable AI Art](01-designing-sellable-ai-art-for-merch.md) · Next: [Building a Catalog Without Repeating Yourself →](03-building-a-catalog-without-repeating.md)
