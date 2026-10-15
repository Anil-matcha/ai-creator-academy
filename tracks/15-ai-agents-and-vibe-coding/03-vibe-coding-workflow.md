# The Vibe-Coding Workflow: Prompt → Build → Test → Ship

> A repeatable 4-phase development loop that lets you build and ship working creator tools without reading a single line of code.

**Track:** AI Agents & Vibe-Coding for Creators
**Time:** ~50 minutes
**Prerequisites:** [01: What Coding Agents Actually Do](01-what-coding-agents-actually-do.md), [02: Building Your First Sellable Micro-Tool](02-building-your-first-sellable-micro-tool.md)

## The Problem

Most creators who start vibe-coding hit the same wall after their second or third tool:

* The agent produces a file that crashes on the first run.
* The creator pastes the error message back, the agent fixes it, but now something else breaks.
* After 3 rounds of back-and-forth, the session devolves into confusion and the project is abandoned.

This happens because vibe-coding without a **structured workflow** is just random prompting. A disciplined 4-phase loop — **Prompt → Build → Test → Ship** — eliminates this failure pattern by giving both you and the agent a clear contract for what each phase produces.

---

## The Concept

The **Vibe-Coding Loop** is a repeatable session structure:

```
Phase 1: PROMPT (Define Scope) ──► Phase 2: BUILD (Agent Generates) ──► Phase 3: TEST (You Verify) ──► Phase 4: SHIP (Package & Publish)
```

### Phase Breakdown:

#### Phase 1 — PROMPT (10 minutes)
Write the **Tool Spec Brief** (see [`templates/vibe-coding-session-brief.md`](templates/vibe-coding-session-brief.md)) before opening the agent. Your brief must include:
* **One-sentence tool description** (what it does, for whom, using what input/output).
* **Error handling rules** (e.g., *"if a line in the input file is blank, skip it and continue"*).
* **Tech constraints** (e.g., *"use only Python standard library — no external packages except `openai`"*).

> **The Golden Rule of Prompting for Code:** Never open the agent without a written brief. Improvised prompting produces improvised code that breaks unpredictably.

#### Phase 2 — BUILD (15–30 minutes)
Paste your full brief into the agent in a single message. Let the agent generate the complete initial version without interrupting. Then:
* Read the agent's explanation of what it built (not the code — the explanation in plain English).
* If the explanation matches your brief, proceed to Phase 3.
* If it doesn't match, correct the agent with a **targeted single-sentence fix**, not a full re-description.

#### Phase 3 — TEST (10–15 minutes)
Run the tool on real data — not dummy placeholder data. Use the actual filenames, actual product names, or actual prompts your buyers will use. Check:
* ✅ Does it produce the correct output format?
* ✅ Does it handle edge cases gracefully (blank lines, special characters, long strings)?
* ✅ Does it complete in under 60 seconds for a typical input size?

When you find a bug, paste the **exact error message** (not a paraphrase) back to the agent:
> *"Running the script gives this error: `KeyError: 'title1'`. Fix it."*

#### Phase 4 — SHIP (10 minutes)
Ask the agent to generate the packaging assets:
> *"Write a plain-English README.md explaining installation and usage. Also create a `requirements.txt` listing all pip packages needed."*

Zip the folder: `[tool-name]-v1.0.zip`. Upload to Gumroad or LemonSqueezy. Done.

---

## Do It

### Step 1: Write Your Session Brief
Open [`templates/vibe-coding-session-brief.md`](templates/vibe-coding-session-brief.md). Complete each field:

```
Tool Name: FLUX Batch Prompt Runner
One-Line Description: Reads prompts from prompts.txt, sends each to muapi /nano-banana-2, 
                      saves all output image URLs to results.csv.
Input: prompts.txt — one prompt string per line
Output: results.csv — columns: PromptText, ImageURL, Timestamp
API: muapi (key from MUAPI_KEY environment variable)
Error Handling: If an API call fails, log the error to errors.log and continue.
Packages Allowed: requests, csv (standard library)
```

### Step 2: Run the BUILD Phase
Paste the completed brief to Claude Code or Cursor. Wait for the full first draft. Do not interrupt mid-generation.

### Step 3: Run the TEST Phase
Create a `prompts.txt` with 3 real prompts you would actually use. Run the script. Verify `results.csv` contains 3 rows with working image URLs.

### Step 4: Run the SHIP Phase
Ask the agent: *"Generate a README.md and requirements.txt for this project."* Then zip and upload.

---

## Worked Example

**Full Vibe-Coding Session: "FLUX Batch Prompt Runner"**

* **Phase 1 (Prompt):** 8-minute brief writing session in `vibe-coding-session-brief.md`.
* **Phase 2 (Build):** Agent generated `batch_runner.py` in 2 minutes. One issue caught immediately: the agent used `requests.get()` instead of `requests.post()` for the API call — fixed with 1 correction sentence.
* **Phase 3 (Test):** Tested with 10 real prompts. 9 succeeded, 1 failed due to a prompt containing a special apostrophe character. Agent fixed the encoding issue in 30 seconds.
* **Phase 4 (Ship):** Agent generated README and requirements.txt in 1 minute. Zip created and uploaded to Gumroad.
* **Total Session Time:** 52 minutes from blank folder to live product page.
* **Gumroad Price:** **$29 one-time**.
* **Week 1 Revenue:** 11 sales × $29 = **$319**.

---

## Compare Tools

| Vibe-Coding Setup | Phase 2 Speed | Phase 3 Error Recovery | Learning Curve |
|---|---|---|---|
| **Claude Code (terminal)** | Fast (single command sends full brief) | Excellent (paste error → instant fix) | Low — just type in terminal |
| **Cursor (visual editor)** | Fast (chat panel) | Excellent (click error in editor → agent sees context) | Very Low — familiar UI |
| **Windsurf (Codeium)** | Fast | Good | Low |
| **ChatGPT.com (no file access)** | Slow (manual copy-paste between phases) | Poor (loses context across messages) | Medium |

---

## Launch It

**Scaling beyond one tool:**
* **Version 2 Upgrades:** Release a `v2.0` update (e.g., add a GUI window so buyers don't need a terminal) and charge existing buyers an upgrade fee of **$9 – $15**. Gumroad supports this natively.
* **Tool Bundle Packs:** Bundle 3 related micro-tools (e.g., "The POD Creator Toolkit": Etsy Title Generator + Keyword Expander + Mockup Namer) at a 25% discount from buying separately. Bundles consistently outperform individual tools by **2.5–4x revenue**.

---

## Exercises

1. **Easy:** Write a full session brief for a "YouTube Script Section Formatter" tool using the template — without opening an agent.
2. **Medium:** Run a full 4-phase vibe-coding session to build a script that reads a list of Etsy store names and generates 5 niche-specific product idea keywords per store.
3. **Hard:** Complete a full Prompt → Build → Test → Ship cycle for a tool of your choosing, upload it to a Gumroad draft page, and write the product description copy.

---

## Templates

* [`templates/vibe-coding-session-brief.md`](templates/vibe-coding-session-brief.md) — Session planning templates, agent prompt frameworks, and tool spec sheets.

---

[← Building Your First Sellable Micro-Tool](02-building-your-first-sellable-micro-tool.md) · Next: [Pricing & Selling Tools You Build With Agents →](04-pricing-and-selling-tools.md)
