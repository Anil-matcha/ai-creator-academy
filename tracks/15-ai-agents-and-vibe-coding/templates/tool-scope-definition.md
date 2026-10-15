# Tool Scope Definition Template

Use this before building any micro-tool. Answering these 4 questions prevents scope creep and ensures the agent receives a clear, unambiguous instruction.

---

## 🔍 The 4 Scope Questions

### 1. What is the exact input?
> `[Describe the input file format, name, and example content]`

*Example: "A plain text file called `products.txt` containing one product name per line, e.g.:*
```
Cyberpunk Cat Tee
Botanical Wildflower Mug
Retro Mountain Hoodie
```
*"*

---

### 2. What is the exact output?
> `[Describe the output file format, name, column structure, and example row]`

*Example: "A CSV file called `seo_titles.csv` with 4 columns:*
```
ProductName, Title1, Title2, Keywords
```
*Example row: `"Cyberpunk Cat Tee","Cyberpunk Cat Shirt for Gamers","Futuristic Neon Cat Graphic Tee","cyberpunk,cat,neon,gamer,anime"`"*

---

### 3. What is the one transformation?
> `[Describe the single operation that converts input to output]`

*Example: "For each product name, send a GPT-4o-mini API request with a fixed SEO prompt. Parse the JSON response and write the titles and keywords to the output CSV."*

---

### 4. Who is the exact buyer?
> `[Describe the target buyer's job, platform, and specific pain point]`

*Example: "Etsy print-on-demand sellers who publish 15–50 new designs per month and currently spend 10–20 minutes manually writing SEO titles and keyword tags for each listing."*

---

## 📊 Tool Validation Checklist

Before you open the agent, confirm:

- [ ] The tool does **exactly one thing** (no secondary features in v1.0).
- [ ] The input format is concrete (I know the exact filename and structure).
- [ ] The output format is concrete (I know the exact filename, columns, and example row).
- [ ] The buyer and their pain point are specific (not "creators in general").
- [ ] I have a real sample input file ready to test with.

---

## 💰 Monetization Estimate

Fill in before building to confirm the tool is worth selling:

| Field | Your Estimate |
|---|---|
| **Hours saved per buyer per month** | `[e.g., 6 hours]` |
| **Buyer's estimated hourly rate** | `[e.g., $20/hr]` |
| **Monthly value saved** | `[Hours × Rate = e.g., $120/month]` |
| **Suggested price (10% of monthly value)** | `[e.g., $12 — round up to $19 for pricing psychology]` |
| **Break-even sales to recover build time** | `[e.g., 3 sales at $19 = $57 ≥ 1 hour of your time]` |

---

## 🗂️ High-Value Micro-Tool Ideas (Starter List)

Use these as inspiration if you're unsure what to build first:

| Tool Idea | Input | Output | Target Buyer |
|---|---|---|---|
| FLUX Batch Prompt Runner | `prompts.txt` (one prompt/line) | `results.csv` (prompt + image URL) | AI image creators |
| Etsy SEO Title Generator | `products.txt` (design names) | `titles.csv` (3 titles + keywords) | POD/Etsy sellers |
| Stock Metadata CSV Writer | Image filenames folder | `metadata.csv` (title + 30 keywords) | Stock contributors |
| YouTube Hook Generator | `topics.txt` (video topic per line) | `hooks.csv` (5 hook variations) | Faceless channel creators |
| Pricing Calculator Widget | HTML form (no input file) | Interactive web page | AI service freelancers |
| Podcast Show Notes Writer | `.txt` transcript | `shownotes.md` (summary + timestamps) | Podcast editors |
| AI Prompt Enhancer | `basic_prompts.txt` | `enhanced_prompts.txt` (expanded with style tokens) | Midjourney/FLUX users |
