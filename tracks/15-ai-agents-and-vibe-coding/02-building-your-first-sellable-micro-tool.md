# Building Your First Sellable Micro-Tool

> Scope, build, and wrap a single-function creator tool in one vibe-coding session — then turn it into a product.

**Track:** AI Agents & Vibe-Coding for Creators
**Time:** ~50 minutes
**Prerequisites:** [01: What Coding Agents Actually Do](01-what-coding-agents-actually-do.md)

## The Problem

Most creators who discover coding agents immediately try to build something ambitious — a full SaaS platform, a multi-feature app, a custom AI model training dashboard. These projects stall within 48 hours because:

* The scope is too large to describe clearly in a single instruction.
* When the agent produces an error, the creator doesn't know if the error is in step 1 or step 27.
* Weeks pass with a half-finished project that can't be sold.

The correct approach is the **Micro-Tool Method**: build one tool that does **exactly one thing** extremely well. A micro-tool is small enough to be built in a single 60-minute session, specific enough to solve a painful creator problem, and simple enough that a non-developer can maintain it.

---

## The Concept

The **Micro-Tool Funnel** transforms a single creator pain point into a sellable digital product:

```
Identify 1 Painful Repetitive Creator Task ──► Define Exact Input & Output ──► Agent Builds the Tool ──► Wrap & Price It ──► Sell on Gumroad
```

### The Micro-Tool Scope Definition Framework:

A valid micro-tool must answer all 4 questions clearly before you open the agent:

1. **What is the exact input?** (e.g., a `.txt` file with 10 product names)
2. **What is the exact output?** (e.g., a `.csv` file with 3 SEO titles and 5 keywords per product)
3. **What is the one transformation?** (e.g., GPT-4o generates titles and keywords using a fixed commercial SEO prompt)
4. **Who is the buyer?** (e.g., Etsy print-on-demand sellers who hate writing SEO copy)

### 5 High-Value Micro-Tool Categories for Creators:

| Tool Category | What It Does | Target Buyer | Sell Price |
|---|---|---|---|
| **Batch Prompt Runner** | Sends 50+ prompts to FLUX/muapi in one click | AI image creators | $29 – $49 |
| **Etsy SEO Title Generator** | Generates 3 title + keyword sets per product from a name list | POD sellers | $19 – $39 |
| **Stock Metadata CSV Writer** | Reads image filenames and writes 30 IPTC keywords per image | Stock contributors | $29 – $59 |
| **Pricing Calculator Widget** | Interactive web form that calculates package pricing for a client | Agency freelancers | $19 – $29 |
| **YouTube Script Formatter** | Reformats a raw script into hook / body / CTA sections with timestamps | Faceless channel creators | $15 – $25 |

---

## Do It

### Step 1: Define Your Micro-Tool Scope
Open [`templates/tool-scope-definition.md`](templates/tool-scope-definition.md). Fill in the 4 questions above for your chosen tool. Example for the **Etsy SEO Title Generator**:

* **Input:** A `.txt` file named `products.txt` — one product name per line (e.g., `"Cyberpunk Cat Tee"`, `"Botanical Wildflower Mug"`).
* **Output:** A `seo_titles.csv` file with columns: `Product Name`, `Title 1`, `Title 2`, `Title 3`, `Keywords`.
* **Transformation:** Call the OpenAI API with a fixed SEO prompt for each product name.
* **Buyer:** Etsy POD sellers who publish 20+ new designs per month.

### Step 2: Write the Agent Instruction
Open Claude Code or Cursor in a new empty folder. Paste this exact instruction (adapting for your tool):

> *"Build a Python script called `etsy_seo_generator.py` that:*
> *1. Reads product names from `products.txt` (one per line).*
> *2. For each name, calls the OpenAI chat completions API using the model `gpt-4o-mini` with this system prompt: 'You are an expert Etsy SEO copywriter. Generate 3 optimized Etsy listing title variations and 5 relevant keywords for the given product name. Format your response as JSON: {title1, title2, title3, keywords}.'*
> *3. Writes all results to `seo_titles.csv` with columns: ProductName, Title1, Title2, Title3, Keywords.*
> *4. Reads the OpenAI API key from an environment variable called OPENAI_API_KEY."*

### Step 3: Test with Real Data
Create a `products.txt` file with 5 of your actual product names. Run the script:
```bash
python etsy_seo_generator.py
```
Open `seo_titles.csv` and verify the output quality. If a title looks weak, tell the agent: *"Improve the system prompt to produce more buyer-intent focused titles with emotional hooks."*

### Step 4: Package for Non-Technical Buyers
Ask the agent:
> *"Add a simple README.md explaining how to install and run this tool in plain English for someone who has never used Python. Include the exact terminal commands."*

Now your tool is buyer-ready. A non-technical Etsy seller can follow the README and run it.

---

## Worked Example

**Micro-Tool Build: "Stock Metadata CSV Writer"**

* **Problem:** Stock photographers spend 8–15 minutes manually tagging each image with IPTC keywords before uploading to Adobe Stock.
* **Tool Built:** Python script that reads a folder of image filenames, sends each filename to GPT-4o-mini asking for 30 commercial stock keywords, and writes a `metadata.csv` ready for FTP upload.
* **Build Time:** 45 minutes (including testing with 10 sample filenames).
* **Agent Errors Encountered:** 2 (a missing `csv` import and a JSON parsing edge case) — both fixed by pasting the error message back to the agent.
* **Result:** Tool processes 100 images in 4 minutes. Manual equivalent: 25 hours.
* **Listed on Gumroad at:** $39 one-time purchase.
* **First Month Revenue:** 14 sales × $39 = **$546 passive income**.

---

## Compare Tools

| Agent / Environment | Recommended for This Lesson | Why |
|---|---|---|
| **Claude Code (terminal)** | ✅ Best for this lesson | Handles multi-file project creation cleanly. `claude "build me a script that..."` works directly. |
| **Cursor (visual editor)** | ✅ Good alternative | Easier for creators who find the terminal intimidating. Chat panel on the right, file tree on the left. |
| **ChatGPT + manual copy-paste** | ❌ Avoid | Too slow — you'll spend more time copying code than building. |

---

## Launch It

**How to wrap and price your micro-tool:**
* **Free README + Paid Script Bundle:** Zip the script + README + sample input file. Price at **$19 – $59** depending on time saved per use.
* **Lifetime License (Recommended):** One-time payment is the easiest sell for small creator tools — buyers don't want subscriptions for a script they'll run weekly.
* **Upload to Gumroad:** Create a product page in 10 minutes. Set the file as a downloadable product. Gumroad handles payment, delivery, and VAT automatically.

---

## Exercises

1. **Easy:** Complete the tool scope definition for a "YouTube Script Formatter" tool in `templates/tool-scope-definition.md`.
2. **Medium:** Use an agent to build a Python script that reads `designs.txt` and outputs `titles.csv` with 3 Etsy title variations per design using GPT-4o-mini.
3. **Hard:** Package your tool with a README, sample input file, and a `requirements.txt` dependencies list. Share the zip with a fellow creator and ask them to run it from scratch.

---

## Templates

* [`templates/tool-scope-definition.md`](templates/tool-scope-definition.md) — Single-function tool scope definitions, input/output specs, and monetization checklists.

---

[← What Coding Agents Actually Do](01-what-coding-agents-actually-do.md) · Next: [The Vibe-Coding Workflow →](03-vibe-coding-workflow.md)
